from __future__ import annotations

import argparse
import json
from pathlib import Path

from combat_resolver import resolve_combat
from data_catalog import load_data_catalog
from economy_engine import EconomyEngine
from encounter_generator import generate_encounter
from government_law_engine import GovernmentLawEngine
from government_registry import GovernmentRegistry
from interaction_layer import (
    ACTION_IGNORE,
    HANDLER_COMBAT_STUB,
    HANDLER_PURSUIT_STUB,
    dispatch_destination_action,
    dispatch_player_action,
)
from logger import Logger
from market import Market
from npc_ship_generator import generate_npc_ship
from player_state import PlayerState
from pursuit_resolver import resolve_pursuit
from reward_applicator import apply_materialized_reward
from reward_materializer import materialize_reward
from ship_assembler import assemble_ship
from ship_entity import ShipEntity
from shipdock_inventory import generate_shipdock_inventory
from time_engine import TimeEngine
from travel_resolution import resolve_travel
from turn_loop import MoveAction, TurnLoop
from world_generator import WorldGenerator


def _read_version() -> str:
    version_path = Path(__file__).resolve().parents[1] / "VERSION"
    content = version_path.read_text(encoding="utf-8", errors="replace")
    for line in content.splitlines():
        if line.startswith("Version:"):
            return line.split("Version:", 1)[1].strip()
    return "0.0.0"


def _market_payload(market: Market | None) -> dict:
    if market is None:
        return {"categories": {}}
    categories = {}
    for category_id, category in market.categories.items():
        categories[category_id] = {
            "produced": [good.sku for good in category.produced],
            "consumed": [good.sku for good in category.consumed],
            "neutral": [good.sku for good in category.neutral],
        }
    return {"categories": categories}


def _find_shipdock_destination(system):
    for destination in system.destinations:
        for location in destination.locations:
            if location.location_type == "shipdock" and location.enabled:
                return destination
    return system.destinations[0] if system.destinations else None


def _choose_next_system_id(system_ids: list[str], current_id: str) -> str:
    if current_id not in system_ids:
        return system_ids[0]
    index = system_ids.index(current_id)
    return system_ids[(index + 1) % len(system_ids)]


def _emit(events: list[dict], payload: dict) -> None:
    events.append(payload)
    print(json.dumps(payload, sort_keys=True))


def run_playable(seed: int = 12345, turns: int = 5, scripted_actions: list[str] | None = None, interactive: bool = False) -> list[dict]:
    catalog = load_data_catalog()
    registry = GovernmentRegistry.from_file(Path(__file__).resolve().parents[1] / "data" / "governments.json")
    logger = Logger(version=_read_version())
    world = WorldGenerator(
        seed=seed,
        system_count=5,
        government_ids=registry.government_ids(),
        catalog=catalog,
        logger=logger,
    ).generate()
    start_system = world.systems[0]
    start_destination = _find_shipdock_destination(start_system)

    player = PlayerState(current_system_id=start_system.system_id, credits=5000)
    player.current_destination_id = getattr(start_destination, "destination_id", None)
    assembled = assemble_ship("civ_t1_midge", [], {"weapon": 0, "defense": 0, "engine": 0})
    ship = ShipEntity(
        ship_id="PLAYER-SHIP-001",
        model_id="civ_t1_midge",
        owner_id=player.player_id,
        activity_state="active",
        location_id=player.current_destination_id or start_system.system_id,
        current_location_id=player.current_destination_id or start_system.system_id,
        fuel_capacity=int(assembled["fuel_capacity"]),
        current_fuel=int(assembled["fuel_capacity"]),
    )
    ship.persistent_state["module_instances"] = []
    ship.persistent_state["degradation_state"] = {"weapon": 0, "defense": 0, "engine": 0}
    fleet_by_id = {ship.ship_id: ship}
    player.active_ship_id = ship.ship_id
    player.owned_ship_ids = [ship.ship_id]

    turn_loop = TurnLoop(
        time_engine=TimeEngine(),
        sector=world,
        player_state=player,
        logger=logger,
        economy_engine=EconomyEngine(sector=world, logger=logger),
        law_engine=GovernmentLawEngine(registry=registry, logger=logger, seed=seed),
        catalog=catalog,
        government_registry=registry,
        world_seed=seed,
    )

    events: list[dict] = []
    _emit(events, {"event": "init", "seed": seed, "system_id": player.current_system_id, "destination_id": player.current_destination_id})

    for index in range(turns):
        action = scripted_actions[index] if scripted_actions and index < len(scripted_actions) else "travel"
        if interactive:
            action = input("Action [travel/status/refuel/buy_hull/sell_hull/buy_module/sell_module/repair_ship/quit]: ").strip() or "travel"
        _emit(events, {"event": "turn_start", "turn": index + 1, "action": action, "system_id": player.current_system_id, "fuel": ship.current_fuel})

        if action == "quit":
            break
        if action == "status":
            _emit(events, {"event": "status", "credits": player.credits, "cargo": dict(player.cargo_by_ship.get("active", {}))})
            print(f"Turn {index + 1}: status credits={player.credits} fuel={ship.current_fuel}")
            continue

        current_system = world.get_system(player.current_system_id)
        destination = _find_shipdock_destination(current_system) if current_system is not None else None
        if action in {"refuel", "buy_hull", "sell_hull", "buy_module", "sell_module", "repair_ship"} and destination is not None:
            inventory = generate_shipdock_inventory(seed, current_system.system_id, current_system.population)
            payload = {"destination": destination, "player": player, "fleet_by_id": fleet_by_id}
            if action == "refuel":
                result = dispatch_destination_action("refuel", ship=ship, player_credits=player.credits, requested_units=None)
                if result.get("ok"):
                    player.credits = int(result["credits"])
            elif action == "buy_hull":
                hull_id = inventory.get("hulls", [{}])[0].get("hull_id")
                result = dispatch_destination_action(action, **payload, inventory=inventory, hull_id=hull_id, ship_id=f"SHIP-{index + 1:03d}")
            elif action == "sell_hull":
                target_id = next((sid for sid in player.owned_ship_ids if sid != player.active_ship_id), player.active_ship_id)
                result = dispatch_destination_action(action, **payload, ship_id=target_id)
            elif action == "buy_module":
                module_id = inventory.get("modules", [{}])[0].get("module_id")
                result = dispatch_destination_action(
                    action,
                    **payload,
                    inventory=inventory,
                    ship_id=player.active_ship_id,
                    module_id=module_id,
                )
            elif action == "sell_module":
                modules = fleet_by_id[player.active_ship_id].persistent_state.get("module_instances", [])
                module_id = modules[0]["module_id"] if modules else None
                result = dispatch_destination_action(action, **payload, ship_id=player.active_ship_id, module_id=module_id)
            else:
                result = dispatch_destination_action(
                    action,
                    **payload,
                    ship_id=player.active_ship_id,
                    system_population=current_system.population,
                )
            _emit(events, {"event": "shipdock_action", "turn": index + 1, "action": action, "result": result})
            print(f"Turn {index + 1}: shipdock action={action} ok={bool(result.get('ok'))}")
            continue

        system_ids = world.system_ids()
        target_system_id = _choose_next_system_id(system_ids, player.current_system_id)
        travel = resolve_travel(ship=ship, inter_system=True, distance_ly=1)
        if not travel.success:
            _emit(events, {"event": "travel_blocked", "turn": index + 1, "reason": travel.reason, "fuel": ship.current_fuel})
            print(f"Turn {index + 1}: travel blocked reason={travel.reason}")
            continue

        turn_loop.execute_move(MoveAction(target_system_id=target_system_id))
        new_system = world.get_system(player.current_system_id)
        new_destination = _find_shipdock_destination(new_system) if new_system is not None else None
        player.current_destination_id = getattr(new_destination, "destination_id", None)
        ship.location_id = player.current_destination_id or player.current_system_id
        ship.current_location_id = ship.location_id
        _emit(events, {"event": "travel", "turn": index + 1, "to_system_id": player.current_system_id, "fuel": ship.current_fuel})

        encounter = generate_encounter(
            encounter_id=f"PLAY-{seed}-T{index + 1}",
            world_seed=str(seed),
            system_government_id=new_system.government_id,
            active_situations=[],
        )
        _emit(
            events,
            {
                "event": "encounter",
                "turn": index + 1,
                "encounter_id": encounter.encounter_id,
                "subtype_id": encounter.subtype_id,
                "posture": encounter.posture,
                "initiative": encounter.initiative,
            },
        )
        dispatch = dispatch_player_action(
            spec=encounter,
            player_action=ACTION_IGNORE,
            world_seed=str(seed),
            ignore_count=0,
            reputation_band=player.reputation_by_system.get(player.current_system_id, 50),
            notoriety_band=player.progression_tracks.get("notoriety", 0),
        )
        _emit(events, {"event": "interaction_dispatch", "turn": index + 1, "next_handler": dispatch.next_handler, "payload": dispatch.handler_payload})

        if dispatch.next_handler == HANDLER_COMBAT_STUB:
            enemy_ship = generate_npc_ship(
                world_seed=seed,
                system_id=player.current_system_id,
                system_population=new_system.population,
                encounter_id=encounter.encounter_id,
                encounter_subtype=encounter.subtype_id,
            )
            player_ship_state = {
                "hull_id": ship.model_id,
                "module_instances": list(ship.persistent_state.get("module_instances", [])),
                "degradation_state": dict(ship.persistent_state.get("degradation_state", {"weapon": 0, "defense": 0, "engine": 0})),
                "current_hull_integrity": int(ship.persistent_state.get("current_hull_integrity", 0) or 0),
            }
            combat = resolve_combat(
                world_seed=str(seed),
                combat_id=f"CMB-{encounter.encounter_id}",
                system_id=player.current_system_id,
                player_ship_state=player_ship_state,
                enemy_ship_state=enemy_ship,
                max_rounds=3,
            )
            _emit(events, {"event": "combat", "turn": index + 1, "outcome": combat.outcome, "winner": combat.winner, "salvage_count": len(combat.salvage_modules)})
        elif dispatch.next_handler == HANDLER_PURSUIT_STUB:
            pursuit = resolve_pursuit(
                encounter_id=f"PUR-{encounter.encounter_id}",
                world_seed=str(seed),
                pursuer_ship={"speed": 3, "pilot_skill": 3, "engine_band": 3, "tr_band": 3},
                pursued_ship={"speed": 3, "pilot_skill": 3, "engine_band": 3, "tr_band": 3},
            )
            _emit(events, {"event": "pursuit", "turn": index + 1, "outcome": pursuit.outcome, "escaped": pursuit.escaped})

        reward = materialize_reward(encounter, [_market_payload(new_system.attributes.get("market"))], str(seed))
        applied = apply_materialized_reward(player=player, reward_payload=reward, context="cli_playable")
        _emit(events, {"event": "reward", "turn": index + 1, "reward_profile_id": encounter.reward_profile_id, "applied": applied})
        print(f"Turn {index + 1}: system={player.current_system_id} action=travel fuel={ship.current_fuel} credits={player.credits}")

    _emit(events, {"event": "done", "turns_completed": len([e for e in events if e.get('event') == 'turn_start'])})
    return events


def main() -> None:
    parser = argparse.ArgumentParser(description="Minimal playable simulation CLI harness for EmojiSpace.")
    parser.add_argument("--seed", type=int, default=12345)
    parser.add_argument("--turns", type=int, default=5)
    parser.add_argument("--scripted", action="store_true", help="Run non-interactive deterministic turn loop.")
    args = parser.parse_args()
    scripted_actions = ["travel"] * args.turns if args.scripted else None
    run_playable(seed=args.seed, turns=args.turns, scripted_actions=scripted_actions, interactive=not args.scripted)


if __name__ == "__main__":
    main()

