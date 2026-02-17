from __future__ import annotations

import json
import math

from game_engine import GameEngine


def _prompt_seed() -> int:
    raw = input("Seed [12345]: ").strip()
    if not raw:
        return 12345
    try:
        return int(raw)
    except ValueError:
        return 12345


def _print_systems(engine: GameEngine) -> None:
    current_system = engine.sector.get_system(engine.player_state.current_system_id)
    if current_system is None:
        print("Current system: unavailable")
        return

    active_ship = engine.fleet_by_id.get(engine.player_state.active_ship_id)
    current_fuel = int(getattr(active_ship, "current_fuel", 0) or 0)
    fuel_capacity = int(getattr(active_ship, "fuel_capacity", 0) or 0)

    print(f"Current system: {current_system.name} ({current_system.system_id})")
    print(f"Current destination: {engine.player_state.current_destination_id}")
    print(f"Fuel: {current_fuel}/{fuel_capacity}")
    print("Intra-system destinations:")
    destinations = sorted(current_system.destinations, key=lambda destination: destination.destination_id)
    for index, destination in enumerate(destinations, start=1):
        print(f"  {index}) {destination.destination_id} {destination.display_name}")

    print("Reachable inter-system systems:")
    reachable = _reachable_systems(engine=engine, current_system=current_system, fuel_limit=current_fuel)
    if not reachable:
        print("  none")
        return
    for index, item in enumerate(reachable, start=1):
        print(
            f"  {index}) {item['system_id']} {item['name']} "
            f"distance_ly={item['distance_ly']:.3f}"
        )


def _travel_menu(engine: GameEngine) -> None:
    current_system_id = engine.player_state.current_system_id
    current_system = engine.sector.get_system(current_system_id)
    if current_system is None:
        print(json.dumps({"ok": False, "error": "current_system_not_found"}, sort_keys=True))
        return
    active_ship = engine.fleet_by_id.get(engine.player_state.active_ship_id)
    current_fuel = int(getattr(active_ship, "current_fuel", 0) or 0)

    print(f"Current system: {current_system.system_id} ({current_system.name})")
    print("1) Inter-system warp")
    print("2) Intra-system destination travel")
    mode = input("Travel mode: ").strip()

    if mode == "1":
        reachable = _reachable_systems(engine=engine, current_system=current_system, fuel_limit=current_fuel)
        options = [row["system"] for row in reachable]
        if not options:
            print(json.dumps({"ok": False, "error": "no_inter_system_targets"}, sort_keys=True))
            return
        for index, row in enumerate(reachable, start=1):
            print(f"{index}) {row['system_id']} {row['name']} distance_ly={row['distance_ly']:.3f}")
        raw_index = input("Select target system index: ").strip()
        try:
            selected = int(raw_index)
        except ValueError:
            print(json.dumps({"ok": False, "error": "invalid_system_index"}, sort_keys=True))
            return
        if selected < 1 or selected > len(options):
            print(json.dumps({"ok": False, "error": "system_index_out_of_range"}, sort_keys=True))
            return
        target_system = options[selected - 1]
        destinations = sorted(target_system.destinations, key=lambda entry: entry.destination_id)
        target_destination_id = destinations[0].destination_id if destinations else None
        payload: dict[str, object] = {
            "type": "travel_to_destination",
            "target_system_id": target_system.system_id,
        }
        if target_destination_id is not None:
            payload["target_destination_id"] = target_destination_id
        result = engine.execute(payload)
        print(json.dumps(result, sort_keys=True))
        if result.get("ok") is True and result.get("player", {}).get("system_id") == target_system.system_id:
            print(f"You have arrived in {target_system.name}.")
            _print_current_system_destinations(engine)
        return

    if mode == "2":
        destinations = sorted(current_system.destinations, key=lambda entry: entry.destination_id)
        if not destinations:
            print(json.dumps({"ok": False, "error": "no_intra_system_destinations"}, sort_keys=True))
            return
        for index, destination in enumerate(destinations, start=1):
            print(f"{index}) {destination.destination_id} {destination.display_name}")
        raw_index = input("Select destination index: ").strip()
        try:
            selected = int(raw_index)
        except ValueError:
            print(json.dumps({"ok": False, "error": "invalid_destination_index"}, sort_keys=True))
            return
        if selected < 1 or selected > len(destinations):
            print(json.dumps({"ok": False, "error": "destination_index_out_of_range"}, sort_keys=True))
            return
        payload = {
            "type": "travel_to_destination",
            "target_system_id": current_system.system_id,
            "target_destination_id": destinations[selected - 1].destination_id,
        }
        print(json.dumps(engine.execute(payload), sort_keys=True))
        return

    print(json.dumps({"ok": False, "error": "invalid_travel_mode"}, sort_keys=True))


def _wait_menu(engine: GameEngine) -> None:
    raw = input("Days to wait (1..10): ").strip()
    try:
        days = int(raw)
    except ValueError:
        days = 1
    print(json.dumps(engine.execute({"type": "wait", "days": days}), sort_keys=True))


def main() -> None:
    seed = _prompt_seed()
    engine = GameEngine(world_seed=seed)
    _configure_cli_test_fuel(engine)
    print(json.dumps({"event": "engine_init", "seed": seed}, sort_keys=True))
    while True:
        print("1) show current travel overview")
        print("2) travel to destination")
        print("3) wait N days")
        print("4) quit")
        choice = input("Select: ").strip()
        if choice == "1":
            _print_systems(engine)
        elif choice == "2":
            _travel_menu(engine)
        elif choice == "3":
            _wait_menu(engine)
        elif choice == "4":
            print(json.dumps(engine.execute({"type": "quit"}), sort_keys=True))
            break
        else:
            print(json.dumps({"ok": False, "error": "invalid_menu_choice"}, sort_keys=True))


def _reachable_systems(*, engine: GameEngine, current_system, fuel_limit: int) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for system in sorted(engine.sector.systems, key=lambda entry: entry.system_id):
        if system.system_id == current_system.system_id:
            continue
        dx = float(system.x) - float(current_system.x)
        dy = float(system.y) - float(current_system.y)
        distance = math.sqrt((dx * dx) + (dy * dy))
        if distance <= float(fuel_limit):
            rows.append(
                {
                    "system": system,
                    "system_id": system.system_id,
                    "name": system.name,
                    "distance_ly": float(distance),
                }
            )
    return rows


def _print_current_system_destinations(engine: GameEngine) -> None:
    system = engine.sector.get_system(engine.player_state.current_system_id)
    if system is None:
        return
    destinations = sorted(system.destinations, key=lambda destination: destination.destination_id)
    print("Intra-system destinations:")
    for index, destination in enumerate(destinations, start=1):
        print(f"  {index}) {destination.destination_id} {destination.display_name}")


def _configure_cli_test_fuel(engine: GameEngine) -> None:
    active_ship = engine.fleet_by_id.get(engine.player_state.active_ship_id)
    if active_ship is None:
        return
    active_ship.fuel_capacity = 55
    active_ship.current_fuel = 55


if __name__ == "__main__":
    main()
