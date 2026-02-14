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
from ship_assembler import assemble_ship
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
    time_engine = TimeEngine(logger=logger)
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
    assembled = assemble_ship("civ_t1_midge", [], {"weapon": 0, "defense": 0, "engine": 0})
    active_ship = ShipEntity(
        ship_id="PLAYER-SHIP-001",
        model_id="civ_t1_midge",
        owner_id=player.player_id,
        activity_state="active",
        location_id=player.current_system_id,
        current_location_id=player.current_system_id,
        fuel_capacity=int(assembled["fuel_capacity"]),
        current_fuel=int(assembled["fuel_capacity"]),
    )
    active_ship.persistent_state["module_instances"] = []
    active_ship.persistent_state["degradation_state"] = {"weapon": 0, "defense": 0, "engine": 0}
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

