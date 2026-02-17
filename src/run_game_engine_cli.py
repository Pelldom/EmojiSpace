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


def _show_player_info(engine: GameEngine) -> None:
    result = engine.execute({"type": "get_player_profile"})
    detail = _extract_detail_from_stage(step_result=result, stage="player_profile")
    if not isinstance(detail, dict):
        print(json.dumps(result, sort_keys=True))
        return
    print("PLAYER / SHIP INFO")
    print(f"  Credits: {detail.get('credits')}")
    print(f"  Fuel: {detail.get('fuel_current')}/{detail.get('fuel_capacity')}")
    print(f"  Cargo manifest: {detail.get('cargo_manifest')}")
    print(f"  Reputation: {detail.get('reputation_score')} band={detail.get('reputation_band')}")
    print(f"  Heat: {detail.get('heat')}")
    print(f"  Notoriety: {detail.get('notoriety_score')} band={detail.get('notoriety_band')}")
    print(f"  Arrest state: {detail.get('arrest_state')}")
    print(f"  Warrants: {detail.get('warrants')}")
    print(f"  Location: {detail.get('system_id')} / {detail.get('destination_id')} / {detail.get('location_id')}")
    print(f"  Turn: {detail.get('turn')}")


def _show_system_info(engine: GameEngine) -> None:
    result = engine.execute({"type": "get_system_profile"})
    detail = _extract_detail_from_stage(step_result=result, stage="system_profile")
    if not isinstance(detail, dict):
        print(json.dumps(result, sort_keys=True))
        return
    coords = detail.get("coordinates", {})
    print("SYSTEM INFO")
    print(f"  Name: {detail.get('name')}")
    print(f"  ID: {detail.get('system_id')}")
    print(f"  Government: {detail.get('government_id')}")
    print(f"  Population: {detail.get('population')}")
    print(f"  Coordinates: ({coords.get('x')}, {coords.get('y')})")
    print(f"  Active situations: {detail.get('active_system_situations')}")
    print(f"  Active flags: {detail.get('active_system_flags')}")
    print("  Reachable systems:")
    for row in detail.get("reachable_systems", []):
        print(
            f"    {row.get('system_id')} {row.get('name')} "
            f"distance_ly={row.get('distance_ly'):.3f} in_range={row.get('in_range')}"
        )


def _show_destination_info(engine: GameEngine) -> None:
    result = engine.execute({"type": "get_destination_profile"})
    detail = _extract_detail_from_stage(step_result=result, stage="destination_profile")
    if not isinstance(detail, dict):
        print(json.dumps(result, sort_keys=True))
        return
    print("DESTINATION INFO")
    print(f"  Name: {detail.get('name')}")
    print(f"  ID: {detail.get('destination_id')}")
    print(f"  Population: {detail.get('population')}")
    print(f"  Primary economy: {detail.get('primary_economy')}")
    print(f"  Market attached: {detail.get('market_attached')}")
    print(f"  Active destination situations: {detail.get('active_destination_situations')}")
    print("  Locations:")
    locations = detail.get("locations", [])
    if not locations:
        print("    none")
    for row in locations:
        print(f"    {row.get('location_id')} type={row.get('location_type')}")
    print(f"  Active crew: {detail.get('active_crew')}")
    print(f"  Active missions: {detail.get('active_missions')}")


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

    location_by_index: dict[int, object] = {}
    for index, location in enumerate(locations, start=1):
        location_by_index[index] = location
        print(
            f"{index}) {getattr(location, 'location_id', None)} "
            f"type={getattr(location, 'location_type', None)}"
        )
    raw_index = input("Select location index: ").strip()
    try:
        selected = int(raw_index)
    except ValueError:
        print(json.dumps({"ok": False, "error": "invalid_location_index"}, sort_keys=True))
        return
    if selected < 1 or selected > len(locations):
        print(json.dumps({"ok": False, "error": "location_index_out_of_range"}, sort_keys=True))
        return
    selected_location = location_by_index[selected]
    result = engine.execute({"type": "enter_location", "location_index": selected})
    if result.get("ok") is False:
        print(json.dumps(result, sort_keys=True))
        return

    print(f"Entered location: {engine.player_state.current_location_id}")
    if str(getattr(selected_location, "location_type", "")) == "market":
        _print_market_profile(engine)
    _location_actions_menu(engine, selected_location=selected_location)


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
            if action_id == "buy":
                _market_buy_menu(engine)
                continue
            if action_id == "sell":
                _market_sell_menu(engine)
                continue
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
            result = engine.execute({"type": "return_to_destination"})
            print(json.dumps(result, sort_keys=True))
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
        print("1) player / ship info")
        print("2) system info")
        print("3) destination info")
        print("4) travel")
        print("5) enter location")
        print("6) destination actions")
        print("7) quit")
        choice = input("Select: ").strip()
        if choice == "1":
            _show_player_info(engine)
        elif choice == "2":
            _show_system_info(engine)
        elif choice == "3":
            _show_destination_info(engine)
        elif choice == "4":
            _travel_menu(engine)
        elif choice == "5":
            _location_entry_menu(engine)
        elif choice == "6":
            _destination_actions_menu(engine)
        elif choice == "7":
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
    try:
        selected = int(selection_text)
    except ValueError:
        return {"ok": False, "error": "invalid_location_index"}
    return engine.execute({"type": "enter_location", "location_index": selected})


def _return_to_destination(engine: GameEngine) -> None:
    _ = engine.execute({"type": "return_to_destination"})


def _destination_actions_menu(engine: GameEngine) -> None:
    list_result = engine.execute({"type": "list_destination_actions"})
    actions = _extract_actions_from_stage(step_result=list_result, stage="destination_actions")
    if not actions:
        print("No destination actions available.")
        return
    for index, action in enumerate(actions, start=1):
        print(f"{index}) {action['action_id']} {action.get('display_name')}")
    raw_index = input("Select destination action index: ").strip()
    try:
        selected = int(raw_index)
    except ValueError:
        print(json.dumps({"ok": False, "error": "invalid_destination_action_index"}, sort_keys=True))
        return
    if selected < 1 or selected > len(actions):
        print(json.dumps({"ok": False, "error": "destination_action_index_out_of_range"}, sort_keys=True))
        return
    action = actions[selected - 1]
    kwargs = _prompt_action_kwargs(action)
    result = engine.execute(
        {
            "type": "destination_action",
            "action_id": action["action_id"],
            "action_kwargs": kwargs,
        }
    )
    print(json.dumps(result, sort_keys=True))


def _print_market_profile(engine: GameEngine) -> None:
    result = engine.execute({"type": "get_market_profile"})
    if result.get("ok") is False:
        print(json.dumps(result, sort_keys=True))
        return
    events = result.get("events", [])
    detail = {}
    for event in events:
        if isinstance(event, dict) and event.get("stage") == "market_profile":
            detail = event.get("detail", {})
            break
    if not isinstance(detail, dict):
        print("Market profile unavailable.")
        return
    print("MARKET PROFILE")
    print(f"  System: {detail.get('system_id')}")
    print(f"  Destination: {detail.get('destination_id')}")
    print(f"  Primary economy: {detail.get('primary_economy_id')}")
    situations = detail.get("active_situations", [])
    print(f"  Active situations: {situations if situations else 'none'}")
    categories = detail.get("categories", {})
    if not isinstance(categories, dict):
        return
    for category_id in sorted(categories):
        row = categories[category_id]
        print(
            f"  {category_id}: produced={row.get('produced', [])} "
            f"consumed={row.get('consumed', [])} neutral={row.get('neutral', [])}"
        )


def _market_buy_menu(engine: GameEngine) -> None:
    result = engine.execute({"type": "market_buy_list"})
    rows = _extract_rows_from_stage(step_result=result, stage="market_buy_list")
    if not rows:
        print("No market buy offers.")
        return
    for index, row in enumerate(rows, start=1):
        print(
            f"{index}) {row['sku_id']} {row.get('display_name')} "
            f"price={row.get('unit_price')} legality={row.get('legality')} risk={row.get('risk_tier')}"
        )
    raw_index = input("Select buy sku index: ").strip()
    raw_qty = input("Quantity: ").strip()
    try:
        selected = int(raw_index)
        quantity = int(raw_qty)
    except ValueError:
        print(json.dumps({"ok": False, "error": "invalid_buy_input"}, sort_keys=True))
        return
    if selected < 1 or selected > len(rows):
        print(json.dumps({"ok": False, "error": "buy_index_out_of_range"}, sort_keys=True))
        return
    sku_id = rows[selected - 1]["sku_id"]
    print(json.dumps(engine.execute({"type": "market_buy", "sku_id": sku_id, "quantity": quantity}), sort_keys=True))


def _market_sell_menu(engine: GameEngine) -> None:
    result = engine.execute({"type": "market_sell_list"})
    rows = _extract_rows_from_stage(step_result=result, stage="market_sell_list")
    if not rows:
        print("No market sell offers.")
        return
    for index, row in enumerate(rows, start=1):
        print(
            f"{index}) {row['sku_id']} {row.get('display_name')} units={row.get('player_has_units')} "
            f"price={row.get('unit_price')} legality={row.get('legality')} risk={row.get('risk_tier')}"
        )
    raw_index = input("Select sell sku index: ").strip()
    raw_qty = input("Quantity: ").strip()
    try:
        selected = int(raw_index)
        quantity = int(raw_qty)
    except ValueError:
        print(json.dumps({"ok": False, "error": "invalid_sell_input"}, sort_keys=True))
        return
    if selected < 1 or selected > len(rows):
        print(json.dumps({"ok": False, "error": "sell_index_out_of_range"}, sort_keys=True))
        return
    sku_id = rows[selected - 1]["sku_id"]
    print(json.dumps(engine.execute({"type": "market_sell", "sku_id": sku_id, "quantity": quantity}), sort_keys=True))


def _extract_actions_from_step_result(step_result: dict[str, object]) -> list[dict[str, object]]:
    return _extract_actions_from_stage(step_result=step_result, stage="location_actions")


def _extract_actions_from_stage(*, step_result: dict[str, object], stage: str) -> list[dict[str, object]]:
    events = step_result.get("events", [])
    if not isinstance(events, list):
        return []
    for event in events:
        if not isinstance(event, dict):
            continue
        if event.get("stage") != stage:
            continue
        detail = event.get("detail", {})
        if not isinstance(detail, dict):
            continue
        actions = detail.get("actions", [])
        if isinstance(actions, list):
            return [entry for entry in actions if isinstance(entry, dict)]
    return []


def _extract_rows_from_stage(*, step_result: dict[str, object], stage: str) -> list[dict[str, object]]:
    events = step_result.get("events", [])
    if not isinstance(events, list):
        return []
    for event in events:
        if not isinstance(event, dict):
            continue
        if event.get("stage") != stage:
            continue
        detail = event.get("detail", {})
        if not isinstance(detail, dict):
            continue
        rows = detail.get("rows", [])
        if isinstance(rows, list):
            return [row for row in rows if isinstance(row, dict)]
    return []


def _extract_detail_from_stage(*, step_result: dict[str, object], stage: str) -> dict[str, object] | None:
    events = step_result.get("events", [])
    if not isinstance(events, list):
        return None
    for event in events:
        if not isinstance(event, dict):
            continue
        if event.get("stage") != stage:
            continue
        detail = event.get("detail", {})
        if isinstance(detail, dict):
            return detail
    return None


def _prompt_action_kwargs(action: dict[str, object]) -> dict[str, object]:
    params = action.get("parameters", [])
    if not isinstance(params, list) or not params:
        return {}
    kwargs: dict[str, object] = {}
    for param in params:
        if not isinstance(param, str):
            continue
        raw = input(f"{param}: ").strip()
        if param in {"quantity", "requested_units", "location_index"}:
            try:
                kwargs[param] = int(raw)
            except ValueError:
                kwargs[param] = raw
        elif param == "allow_repeat":
            kwargs[param] = raw.lower() in {"1", "true", "yes", "y"}
        else:
            kwargs[param] = raw
    return kwargs


if __name__ == "__main__":
    main()
