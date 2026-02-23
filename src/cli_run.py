from __future__ import annotations

import argparse
import json
from pathlib import Path

from data_catalog import load_data_catalog
from economy_engine import EconomyEngine
from government_law_engine import GovernmentLawEngine
from government_registry import GovernmentRegistry
from logger import Logger
from player_state import PlayerState
from ship_assembler import assemble_ship, compute_hull_max_from_ship_state
from ship_entity import ShipEntity
from simulation_controller import SimulationController
from time_engine import TimeEngine, _reset_time_state_for_test
from turn_loop import TurnLoop
from world_generator import WorldGenerator


def _read_version() -> str:
    content = (Path(__file__).resolve().parents[1] / "VERSION").read_text(
        encoding="utf-8", errors="replace"
    )
    for line in content.splitlines():
        if line.startswith("Version:"):
            return line.split("Version:", 1)[1].strip()
    return "0.0.0"


def build_simulation(seed: int) -> tuple[SimulationController, dict]:
    _reset_time_state_for_test()
    catalog = load_data_catalog()
    registry = GovernmentRegistry.from_file(
        Path(__file__).resolve().parents[1] / "data" / "governments.json"
    )
    logger = Logger(version=_read_version())
    sector = WorldGenerator(
        seed=seed,
        system_count=5,
        government_ids=registry.government_ids(),
        catalog=catalog,
        logger=logger,
    ).generate()
    player = PlayerState(current_system_id=sector.systems[0].system_id, credits=5000)
    time_engine = TimeEngine(
        logger=logger,
        world_seed=seed,
        sector=sector,
        player_state=player,
        event_frequency_percent=8,
    )
    economy_engine = EconomyEngine(sector=sector, logger=logger)
    law_engine = GovernmentLawEngine(registry=registry, logger=logger, seed=seed)
    turn_loop = TurnLoop(
        time_engine=time_engine,
        sector=sector,
        player_state=player,
        logger=logger,
        economy_engine=economy_engine,
        law_engine=law_engine,
        catalog=catalog,
        government_registry=registry,
        world_seed=seed,
    )
    # Enforce starting ship: Midge (civ_t1_midge) with no modules
    # All ship stats derive from assemble_ship() output
    hull_id = "civ_t1_midge"
    module_instances = []
    degradation_state = {"weapon": 0, "defense": 0, "engine": 0}
    assembled = assemble_ship(hull_id, module_instances, degradation_state)
    
    # Extract hull data for crew_capacity and cargo base
    from data_loader import load_hulls
    hulls_data = load_hulls()
    hull_data = None
    for hull in hulls_data.get("hulls", []):
        if hull.get("hull_id") == hull_id:
            hull_data = hull
            break
    
    if hull_data is None:
        raise ValueError(f"Hull data not found for {hull_id}")
    
    # Extract cargo capacities: base from hull + module bonuses from assembler
    cargo_base = hull_data.get("cargo", {})
    physical_cargo_base = int(cargo_base.get("physical_base", 0))
    data_cargo_base = int(cargo_base.get("data_base", 0))
    utility_effects = assembled.get("ship_utility_effects", {})
    physical_cargo_capacity = physical_cargo_base + int(utility_effects.get("physical_cargo_bonus", 0))
    data_cargo_capacity = data_cargo_base + int(utility_effects.get("data_cargo_bonus", 0))
    
    # Extract crew capacity from hull data
    crew_capacity = int(hull_data.get("crew_capacity", 0))
    
    # Extract subsystem bands from assembler
    bands = assembled.get("bands", {})
    effective_bands = bands.get("effective", {})
    
    active_ship = ShipEntity(
        ship_id="PLAYER-SHIP-001",
        model_id=hull_id,
        owner_id=player.player_id,
        owner_type="player",
        activity_state="active",
        destination_id=player.current_destination_id,
        current_system_id=player.current_system_id,
        current_destination_id=player.current_destination_id,
        fuel_capacity=int(assembled["fuel_capacity"]),
        current_fuel=int(assembled["fuel_capacity"]),
        crew_capacity=crew_capacity,
        physical_cargo_capacity=physical_cargo_capacity,
        data_cargo_capacity=data_cargo_capacity,
    )
    active_ship.persistent_state["module_instances"] = list(module_instances)
    active_ship.persistent_state["degradation_state"] = dict(degradation_state)
    active_ship.persistent_state["max_hull_integrity"] = int(assembled.get("hull_max", 0))
    active_ship.persistent_state["current_hull_integrity"] = int(assembled.get("hull_max", 0))
    active_ship.persistent_state["assembled"] = assembled
    active_ship.persistent_state["subsystem_bands"] = {
        "weapon": int(effective_bands.get("weapon", 0)),
        "defense": int(effective_bands.get("defense", 0)),
        "engine": int(effective_bands.get("engine", 0)),
    }
    fleet_by_id = {active_ship.ship_id: active_ship}
    player.active_ship_id = active_ship.ship_id
    player.owned_ship_ids = [active_ship.ship_id]
    world_state = {
        "sector": sector,
        "fleet_by_id": fleet_by_id,
        "active_situations": [],
        "time_engine": time_engine,
        "economy_engine": economy_engine,
        "law_engine": law_engine,
        "catalog": catalog,
        "government_registry": registry,
        "logger": logger,
        "turn_loop": turn_loop,
    }
    controller = SimulationController(world_seed=seed, world_state=world_state, player=player)
    return controller, world_state


def main() -> None:
    parser = argparse.ArgumentParser(description="EmojiSpace simulation runner.")
    parser.add_argument("--seed", type=int, default=12345)
    args = parser.parse_args()

    controller, state = build_simulation(args.seed)
    player = state["turn_loop"]._player_state  # noqa: SLF001
    print(json.dumps({"event": "init", "seed": args.seed, "system_id": player.current_system_id}))
    print("Commands: travel <SYSTEM_ID> | location <ACTION_ID> [KEY=VALUE...] | encounter <ACTION> | quit")
    while True:
        raw = input("sim> ").strip()
        if not raw:
            continue
        if raw in {"quit", "exit"}:
            break
        parts = raw.split()
        try:
            if parts[0] == "travel" and len(parts) >= 2:
                command = {"action_type": "travel_to_destination", "payload": {"target_system_id": parts[1]}}
            elif parts[0] == "location" and len(parts) >= 2:
                payload = {"action_id": parts[1]}
                for token in parts[2:]:
                    if "=" in token:
                        key, value = token.split("=", 1)
                        payload[key] = value
                command = {"action_type": "location_action", "payload": payload}
            elif parts[0] == "encounter" and len(parts) >= 2:
                command = {"action_type": "encounter_action", "payload": {"action": parts[1]}}
            else:
                print(json.dumps({"ok": False, "error": "invalid_command"}))
                continue
            result = controller.execute(command)
            print(json.dumps(result, sort_keys=True))
            if result.get("hard_stop"):
                break
        except Exception as exc:  # noqa: BLE001
            print(json.dumps({"ok": False, "error": str(exc)}))


if __name__ == "__main__":
    main()

