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
    print("SYSTEM PROFILE")
    print(f"  Name: {getattr(current_system, 'name', None)}")
    print(f"  ID: {getattr(current_system, 'system_id', None)}")
    print(f"  Government: {getattr(current_system, 'government_id', None)}")
    print(f"  Population: {getattr(current_system, 'population', None)}")
    print(f"  Coordinates: ({getattr(current_system, 'x', None)}, {getattr(current_system, 'y', None)})")

    destination = _current_destination_object(engine)
    print("DESTINATION PROFILE")
    if destination is None:
        print("  Destination: unavailable")
    else:
        print(f"  Name: {getattr(destination, 'display_name', None)}")
        print(f"  ID: {getattr(destination, 'destination_id', None)}")
        print(f"  Population: {getattr(destination, 'population', None)}")
        print(f"  Primary economy: {getattr(destination, 'primary_economy_id', None)}")
        market_attached = getattr(destination, "market", None) is not None
        print(f"  Market attached: {market_attached}")
        locations = list(getattr(destination, "locations", []) or [])
        if not locations:
            print("  Locations: none")
        else:
            print("  Locations:")
            for index, location in enumerate(locations, start=1):
                print(
                    f"    {index}) {getattr(location, 'location_id', None)} "
                    f"type={getattr(location, 'location_type', None)}"
                )
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


def _location_entry_menu(engine: GameEngine) -> None:
    destination = _current_destination_object(engine)
    if destination is None:
        print(json.dumps({"ok": False, "error": "no_locations_available"}, sort_keys=True))
        return
    locations = list(getattr(destination, "locations", []) or [])
    if not locations:
        print(json.dumps({"ok": False, "error": "no_locations_available"}, sort_keys=True))
        return

    for index, location in enumerate(locations, start=1):
        print(
            f"{index}) {getattr(location, 'location_id', None)} "
            f"type={getattr(location, 'location_type', None)}"
        )
    raw_index = input("Select location index: ").strip()
    result = _enter_location_by_index(engine=engine, selection_text=raw_index)
    if result.get("ok") is False:
        print(json.dumps(result, sort_keys=True))
        return

    print(f"Entered location: {engine.player_state.current_location_id}")
    _location_actions_menu(engine, selected_location=result.get("location"))


def _location_actions_menu(engine: GameEngine, selected_location: object | None) -> None:
    _ = selected_location
    while True:
        print("Location Menu:")
        print("1) list actions")
        print("2) execute action")
        print("3) return to destination")
        choice = input("Location select: ").strip()
        if choice == "1":
            list_result = engine.execute({"type": "list_location_actions"})
            print(json.dumps(list_result, sort_keys=True))
            actions = _extract_actions_from_step_result(list_result)
            if not actions:
                print("No actions available at this location.")
            else:
                for index, action in enumerate(actions, start=1):
                    print(f"{index}) {action['action_id']} {action.get('display_name')}")
        elif choice == "2":
            list_result = engine.execute({"type": "list_location_actions"})
            actions = _extract_actions_from_step_result(list_result)
            if not actions:
                print("No actions available at this location.")
                continue
            raw_action = input("Select action index: ").strip()
            try:
                selected = int(raw_action)
            except ValueError:
                print(json.dumps({"ok": False, "error": "invalid_action_index"}, sort_keys=True))
                continue
            if selected < 1 or selected > len(actions):
                print(json.dumps({"ok": False, "error": "action_index_out_of_range"}, sort_keys=True))
                continue
            action = actions[selected - 1]
            action_id = action["action_id"]
            action_kwargs = _prompt_action_kwargs(action)
            result = engine.execute(
                {
                    "type": "location_action",
                    "action_id": action_id,
                    "action_kwargs": action_kwargs,
                }
            )
            print(json.dumps(result, sort_keys=True))
        elif choice == "3":
            _return_to_destination(engine)
            print(f"Returned to destination: {engine.player_state.current_location_id}")
            return
        else:
            print(json.dumps({"ok": False, "error": "invalid_location_menu_choice"}, sort_keys=True))


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
        print("5) enter location")
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
        elif choice == "5":
            _location_entry_menu(engine)
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


def _current_destination_object(engine: GameEngine) -> object | None:
    current_system = engine.sector.get_system(engine.player_state.current_system_id)
    if current_system is None:
        return None
    destination_id = engine.player_state.current_destination_id
    for destination in list(getattr(current_system, "destinations", []) or []):
        if getattr(destination, "destination_id", None) == destination_id:
            return destination
    return None


def _enter_location_by_index(engine: GameEngine, selection_text: str) -> dict[str, object]:
    destination = _current_destination_object(engine)
    if destination is None:
        return {"ok": False, "error": "no_locations_available"}
    locations = list(getattr(destination, "locations", []) or [])
    if not locations:
        return {"ok": False, "error": "no_locations_available"}
    try:
        selected = int(selection_text)
    except ValueError:
        return {"ok": False, "error": "invalid_location_index"}
    if selected < 1 or selected > len(locations):
        return {"ok": False, "error": "location_index_out_of_range"}
    location = locations[selected - 1]
    location_id = getattr(location, "location_id", None)
    engine.player_state.current_location_id = location_id
    return {"ok": True, "location": location}


def _return_to_destination(engine: GameEngine) -> None:
    engine.player_state.current_location_id = engine.player_state.current_destination_id


def _extract_actions_from_step_result(step_result: dict[str, object]) -> list[dict[str, object]]:
    events = step_result.get("events", [])
    if not isinstance(events, list):
        return []
    for event in events:
        if not isinstance(event, dict):
            continue
        if event.get("stage") != "location_actions":
            continue
        detail = event.get("detail", {})
        if not isinstance(detail, dict):
            continue
        actions = detail.get("actions", [])
        if isinstance(actions, list):
            return [entry for entry in actions if isinstance(entry, dict)]
    return []


def _prompt_action_kwargs(action: dict[str, object]) -> dict[str, object]:
    params = action.get("parameters", [])
    if not isinstance(params, list) or not params:
        return {}
    kwargs: dict[str, object] = {}
    for param in params:
        if not isinstance(param, str):
            continue
        raw = input(f"{param}: ").strip()
        kwargs[param] = raw
    return kwargs


if __name__ == "__main__":
    main()
