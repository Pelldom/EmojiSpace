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
    destination_profile = _extract_detail_from_stage(
        step_result=engine.execute({"type": "get_destination_profile"}),
        stage="destination_profile",
    )
    cargo_manifest = _compact_manifest(detail.get("cargo_manifest", {}))
    insurance_cost = _sum_numeric_fields(
        rows=getattr(engine.player_state, "insurance_policies", []) or [],
        candidate_keys=("premium_per_turn", "cost_per_turn", "recurring_cost", "premium"),
    )
    warehouse_cost = _sum_numeric_fields(
        rows=getattr(engine.player_state, "warehouse_leases", []) or [],
        candidate_keys=("rental_cost_per_turn", "cost_per_turn", "recurring_cost", "rental"),
    )
    active_ship = engine.fleet_by_id.get(engine.player_state.active_ship_id)
    crew_wages = int(getattr(active_ship, "get_total_daily_wages", lambda: 0)() or 0)
    recurring_total = int(insurance_cost + warehouse_cost + crew_wages)
    print("PLAYER / SHIP INFO")
    print(f"  Credits: {detail.get('credits')}")
    print(f"  Fuel: {detail.get('fuel_current')}/{detail.get('fuel_capacity')}")
    print(f"  Cargo manifest: {cargo_manifest}")
    print(f"  Reputation: {detail.get('reputation_score')} band={detail.get('reputation_band')}")
    print(f"  Heat: {detail.get('heat')}")
    print(f"  Notoriety: {detail.get('notoriety_score')} band={detail.get('notoriety_band')}")
    print(f"  Arrest state: {detail.get('arrest_state')}")
    print(f"  Warrants: {detail.get('warrants')}")
    print(f"  Location: {detail.get('system_id')} / {detail.get('destination_id')} / {detail.get('location_id')}")
    print(f"  Turn: {detail.get('turn')}")
    if isinstance(destination_profile, dict):
        print(f"  Active crew: {destination_profile.get('active_crew')}")
        print(f"  Active missions: {destination_profile.get('active_missions')}")
    else:
        print("  Active crew: []")
        print("  Active missions: []")
    print("ONGOING COSTS")
    print(f"  Insurance: {insurance_cost}")
    print(f"  Warehouse rental: {warehouse_cost}")
    print(f"  Crew wages: {crew_wages}")
    print(f"  Total recurring cost: {recurring_total}")


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


def _travel_menu(engine: GameEngine) -> None:
    current_system_id = engine.player_state.current_system_id
    current_system = engine.sector.get_system(current_system_id)
    if current_system is None:
        print(json.dumps({"ok": False, "error": "current_system_not_found"}, sort_keys=True))
        return
    active_ship = engine.fleet_by_id.get(engine.player_state.active_ship_id)
    current_fuel = int(getattr(active_ship, "current_fuel", 0) or 0)

    while True:
        print(f"Current system: {current_system.system_id} ({current_system.name})")
        print("1) Inter-system warp")
        print("2) Intra-system destination travel")
        print("3) Back")
        mode = input("Travel mode: ").strip()

        if mode == "1":
            reachable = _reachable_systems(engine=engine, current_system=current_system, fuel_limit=current_fuel)
            options = [row["system"] for row in reachable]
            if not options:
                print("No inter-system targets in range.")
                continue
            for index, row in enumerate(reachable, start=1):
                print(f"{index}) {row['system_id']} {row['name']} distance_ly={row['distance_ly']:.3f}")
            raw_index = input("Select target system index: ").strip()
            try:
                selected = int(raw_index)
            except ValueError:
                print("Invalid system index.")
                continue
            if selected < 1 or selected > len(options):
                print("Invalid system index.")
                continue
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
                print("No intra-system destinations available.")
                continue
            for index, destination in enumerate(destinations, start=1):
                print(f"{index}) {destination.destination_id} {destination.display_name}")
            raw_index = input("Select destination index: ").strip()
            try:
                selected = int(raw_index)
            except ValueError:
                print("Invalid destination index.")
                continue
            if selected < 1 or selected > len(destinations):
                print("Invalid destination index.")
                continue
            payload = {
                "type": "travel_to_destination",
                "target_system_id": current_system.system_id,
                "target_destination_id": destinations[selected - 1].destination_id,
            }
            print(json.dumps(engine.execute(payload), sort_keys=True))
            return

        if mode == "3":
            return
        print("Invalid travel mode.")


def _wait_menu(engine: GameEngine) -> None:
    raw = input("Days to wait (1..10): ").strip()
    try:
        days = int(raw)
    except ValueError:
        days = 1
    print(json.dumps(engine.execute({"type": "wait", "days": days}), sort_keys=True))


def _location_entry_menu(engine: GameEngine) -> None:
    while True:
        destination = _current_destination_object(engine)
        if destination is None:
            print("No locations available.")
            return
        locations = list(getattr(destination, "locations", []) or [])
        if not locations:
            print("No locations available.")
            return

        print("0) Back")
        location_by_index: dict[int, object] = {}
        for index, location in enumerate(locations, start=1):
            location_by_index[index] = location
            print(
                f"{index}) {getattr(location, 'location_id', None)} "
                f"type={getattr(location, 'location_type', None)}"
            )
        raw_index = input("Select location index: ").strip()
        if raw_index == "0":
            return
        try:
            selected = int(raw_index)
        except ValueError:
            print("Invalid location index.")
            continue
        if selected < 1 or selected > len(locations):
            print("Invalid location index.")
            continue
        selected_location = location_by_index[selected]
        result = engine.execute({"type": "enter_location", "location_index": selected})
        if result.get("ok") is False:
            print("Unable to enter location.")
            continue
        print(f"Entered location: {engine.player_state.current_location_id}")

        location_type = str(getattr(selected_location, "location_type", "") or "")
        if location_type == "market":
            _market_location_menu(engine)
            continue
        if location_type == "datanet":
            _datanet_location_menu(engine)
            continue
        if location_type == "warehouse":
            _warehouse_location_menu(engine)
            continue
        _location_actions_menu(engine)


def _location_actions_menu(engine: GameEngine) -> None:
    while True:
        list_result = engine.execute({"type": "list_location_actions"})
        actions = _extract_actions_from_step_result(list_result)
        print(f"LOCATION: {engine.player_state.current_location_id}")
        if not actions:
            print("No actions available at this location.")
            print("1) Return to Destination")
            if input("Select action index: ").strip() == "1":
                _return_to_destination(engine)
                print(f"Returned to destination: {engine.player_state.current_location_id}")
                return
            print("Invalid action index.")
            continue
        for index, action in enumerate(actions, start=1):
            print(f"{index}) {action.get('display_name')}")
        return_index = len(actions) + 1
        print(f"{return_index}) Return to Destination")

        raw_action = input("Select action index: ").strip()
        try:
            selected = int(raw_action)
        except ValueError:
            print("Invalid action index.")
            continue
        if selected == return_index:
            _return_to_destination(engine)
            print(f"Returned to destination: {engine.player_state.current_location_id}")
            return
        if selected < 1 or selected > len(actions):
            print("Invalid action index.")
            continue
        action = actions[selected - 1]
        action_kwargs = _prompt_action_kwargs(action)
        result = engine.execute(
            {
                "type": "location_action",
                "action_id": action["action_id"],
                "action_kwargs": action_kwargs,
            }
        )
        print(json.dumps(result, sort_keys=True))


def _market_location_menu(engine: GameEngine) -> None:
    while True:
        _print_market_profile(engine)
        _print_market_sku_overlay(engine)
        print("LOCATION: market")
        print("1) Buy")
        print("2) Sell")
        print("3) Return to Destination")
        raw_action = input("Select action index: ").strip()
        if raw_action == "1":
            _market_buy_menu(engine)
            continue
        if raw_action == "2":
            _market_sell_menu(engine)
            continue
        if raw_action == "3":
            _return_to_destination(engine)
            print(f"Returned to destination: {engine.player_state.current_location_id}")
            return
        print("Invalid action index.")


def _datanet_location_menu(engine: GameEngine) -> None:
    while True:
        profile = _build_datanet_profile(engine)
        _print_datanet_profile(profile)
        print("LOCATION: datanet")
        print("1) Refresh")
        if profile.get("has_mission_accept_action"):
            print("2) Accept mission")
        else:
            print("2) Accept mission (unavailable)")
        print("3) Return to Destination")
        raw_action = input("Select action index: ").strip()
        if raw_action == "1":
            continue
        if raw_action == "2":
            if not profile.get("has_mission_accept_action"):
                print("No missions available.")
                continue
            _accept_mission_from_datanet(engine, profile)
            continue
        if raw_action == "3":
            _return_to_destination(engine)
            print(f"Returned to destination: {engine.player_state.current_location_id}")
            return
        print("Invalid action index.")


def _warehouse_location_menu(engine: GameEngine) -> None:
    while True:
        profile = _build_warehouse_profile(engine)
        _print_warehouse_profile(profile)
        print("LOCATION: warehouse")
        print("1) Deposit cargo")
        print("2) Withdraw cargo")
        if profile.get("supports_rent"):
            print("3) Rent additional space")
        else:
            print("3) Rent additional space (unavailable)")
        print("4) Return to Destination")
        raw_action = input("Select action index: ").strip()
        if raw_action == "1":
            _execute_location_action_if_available(engine, action_id="deposit_cargo")
            continue
        if raw_action == "2":
            _execute_location_action_if_available(engine, action_id="withdraw_cargo")
            continue
        if raw_action == "3":
            if profile.get("supports_rent"):
                _execute_location_action_if_available(engine, action_id="rent_additional_space")
            else:
                print("Rent additional space is not available.")
            continue
        if raw_action == "4":
            _return_to_destination(engine)
            print(f"Returned to destination: {engine.player_state.current_location_id}")
            return
        print("Invalid action index.")


def main() -> None:
    seed = _prompt_seed()
    engine = GameEngine(world_seed=seed)
    _configure_cli_test_fuel(engine)
    print(json.dumps({"event": "engine_init", "seed": seed}, sort_keys=True))
    while True:
        destination = _current_destination_object(engine)
        destination_name = str(getattr(destination, "display_name", "Unknown Destination"))
        print(f"DESTINATION: {destination_name} ({engine.player_state.current_system_id})")
        print("1) Player / Ship Info")
        print("2) System Info")
        print("3) Travel")
        print("4) Destination Actions")
        print("5) Locations")
        print("6) Quit")
        choice = input("Select: ").strip()
        if choice == "1":
            _show_player_info(engine)
        elif choice == "2":
            _show_system_info(engine)
        elif choice == "3":
            _travel_menu(engine)
        elif choice == "4":
            _destination_actions_menu(engine)
        elif choice == "5":
            _location_entry_menu(engine)
        elif choice == "6":
            print(json.dumps(engine.execute({"type": "quit"}), sort_keys=True))
            break
        else:
            print("Invalid menu choice.")


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
    while True:
        list_result = engine.execute({"type": "list_destination_actions"})
        actions = _extract_actions_from_stage(step_result=list_result, stage="destination_actions")
        if not actions:
            print("No destination actions available.")
            return
        for index, action in enumerate(actions, start=1):
            print(f"{index}) {action['action_id']} {action.get('display_name')}")
        print(f"{len(actions) + 1}) Back")

        raw_index = input("Select destination action index: ").strip()
        try:
            selected = int(raw_index)
        except ValueError:
            print("Invalid destination action index.")
            continue
        if selected == len(actions) + 1:
            return
        if selected < 1 or selected > len(actions):
            print("Invalid destination action index.")
            continue
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
        print("Invalid buy input.")
        return
    if selected < 1 or selected > len(rows):
        print("Invalid buy index.")
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
        print("Invalid sell input.")
        return
    if selected < 1 or selected > len(rows):
        print("Invalid sell index.")
        return
    sku_id = rows[selected - 1]["sku_id"]
    print(json.dumps(engine.execute({"type": "market_sell", "sku_id": sku_id, "quantity": quantity}), sort_keys=True))


def _print_market_sku_overlay(engine: GameEngine) -> None:
    buy_rows = _extract_rows_from_stage(step_result=engine.execute({"type": "market_buy_list"}), stage="market_buy_list")
    sell_rows = _extract_rows_from_stage(step_result=engine.execute({"type": "market_sell_list"}), stage="market_sell_list")
    player_profile = _extract_detail_from_stage(
        step_result=engine.execute({"type": "get_player_profile"}),
        stage="player_profile",
    )
    cargo_manifest = _compact_manifest((player_profile or {}).get("cargo_manifest", {}))
    sell_price_by_sku: dict[str, object] = {}
    sell_display_by_sku: dict[str, object] = {}
    sell_legality_by_sku: dict[str, object] = {}
    sell_risk_by_sku: dict[str, object] = {}
    for row in sell_rows:
        sku_id = str(row.get("sku_id", "") or "")
        if not sku_id:
            continue
        sell_price_by_sku[sku_id] = row.get("unit_price")
        sell_display_by_sku[sku_id] = row.get("display_name")
        sell_legality_by_sku[sku_id] = row.get("legality")
        sell_risk_by_sku[sku_id] = row.get("risk_tier")

    buy_by_sku: dict[str, dict[str, object]] = {}
    for row in buy_rows:
        sku_id = str(row.get("sku_id", "") or "")
        if sku_id:
            buy_by_sku[sku_id] = row

    all_skus = sorted(set(buy_by_sku.keys()) | set(cargo_manifest.keys()) | set(sell_price_by_sku.keys()))
    if not all_skus:
        print("No market SKUs available.")
        return

    print("MARKET SKUS")
    for sku_id in all_skus:
        buy_row = buy_by_sku.get(sku_id, {})
        display_name = (
            buy_row.get("display_name")
            or sell_display_by_sku.get(sku_id)
            or sku_id
        )
        buy_price = buy_row.get("unit_price", "--")
        cargo_units = int(cargo_manifest.get(sku_id, 0) or 0)
        if cargo_units > 0:
            sell_price = sell_price_by_sku.get(sku_id, "--")
        else:
            sell_price = "--"
        legality = buy_row.get("legality", sell_legality_by_sku.get(sku_id, "--"))
        risk = buy_row.get("risk_tier", sell_risk_by_sku.get(sku_id, "--"))
        print(
            f"  {sku_id} | {display_name} | buy={buy_price} | sell={sell_price} "
            f"| cargo={cargo_units} | legality={legality} | risk={risk}"
        )


def _build_datanet_profile(engine: GameEngine) -> dict[str, object]:
    system_detail = _extract_detail_from_stage(
        step_result=engine.execute({"type": "get_system_profile"}),
        stage="system_profile",
    )
    destination_detail = _extract_detail_from_stage(
        step_result=engine.execute({"type": "get_destination_profile"}),
        stage="destination_profile",
    )
    destination_actions = _extract_actions_from_stage(
        step_result=engine.execute({"type": "list_destination_actions"}),
        stage="destination_actions",
    )
    mission_actions = [
        action
        for action in destination_actions
        if isinstance(action, dict) and "mission" in str(action.get("action_id", "")).lower()
    ]
    available_missions = []
    if isinstance(destination_detail, dict):
        rows = destination_detail.get("active_missions", [])
        if isinstance(rows, list):
            available_missions = rows
    system_situations = []
    system_notices = []
    destination_situations = []
    if isinstance(system_detail, dict):
        system_situations = list(system_detail.get("active_system_situations", []))
        system_notices = list(system_detail.get("active_system_flags", []))
    if isinstance(destination_detail, dict):
        destination_situations = list(destination_detail.get("active_destination_situations", []))
    return {
        "system_situations": system_situations,
        "destination_situations": destination_situations,
        "available_missions": available_missions,
        "system_notices": system_notices,
        "mission_actions": mission_actions,
        "has_mission_accept_action": bool(mission_actions and available_missions),
    }


def _print_datanet_profile(profile: dict[str, object]) -> None:
    print("DATANET PROFILE")
    print(f"  System situations: {profile.get('system_situations')}")
    print(f"  Destination situations: {profile.get('destination_situations')}")
    missions = profile.get("available_missions", [])
    if missions:
        print(f"  Available missions: {missions}")
    else:
        print("  Available missions: []")
        print("No missions available.")
    notices = profile.get("system_notices", [])
    if notices:
        print(f"  System notices: {notices}")
    else:
        print("  System notices: none")


def _accept_mission_from_datanet(engine: GameEngine, profile: dict[str, object]) -> None:
    actions = [row for row in profile.get("mission_actions", []) if isinstance(row, dict)]
    if not actions:
        print("No missions available.")
        return
    action = actions[0]
    kwargs = _prompt_action_kwargs(action)
    result = engine.execute(
        {
            "type": "destination_action",
            "action_id": action.get("action_id"),
            "action_kwargs": kwargs,
        }
    )
    print(json.dumps(result, sort_keys=True))


def _build_warehouse_profile(engine: GameEngine) -> dict[str, object]:
    destination_id = str(engine.player_state.current_destination_id or "")
    leases = list(getattr(engine.player_state, "warehouse_leases", []) or [])
    stored_goods_raw = getattr(engine.player_state, "stored_goods", {}) or {}

    stored_goods: dict[str, int] = {}
    if isinstance(stored_goods_raw, dict):
        target_bucket = stored_goods_raw.get(destination_id)
        if isinstance(target_bucket, dict):
            stored_goods = {
                str(sku_id): int(quantity)
                for sku_id, quantity in target_bucket.items()
                if isinstance(quantity, int) and int(quantity) > 0
            }
        else:
            stored_goods = {
                str(sku_id): int(quantity)
                for sku_id, quantity in stored_goods_raw.items()
                if isinstance(quantity, int) and int(quantity) > 0
            }

    rented_capacity = _sum_numeric_fields(
        rows=leases,
        candidate_keys=("rented_capacity", "capacity", "total_capacity", "max_storage"),
    )
    used_storage = int(sum(int(value) for value in stored_goods.values()))
    available_storage = max(0, int(rented_capacity - used_storage))
    rental_cost = _sum_numeric_fields(
        rows=leases,
        candidate_keys=("rental_cost_per_turn", "cost_per_turn", "recurring_cost", "rental"),
    )

    available_actions = _extract_actions_from_step_result(engine.execute({"type": "list_location_actions"}))
    action_ids = {str(row.get("action_id")) for row in available_actions if isinstance(row, dict)}
    supports_rent = any(
        action_id in action_ids
        for action_id in {"rent_additional_space", "rent_warehouse_space", "rent_space"}
    )
    return {
        "rented_capacity": rented_capacity,
        "used_storage": used_storage,
        "available_storage": available_storage,
        "rental_cost_per_turn": rental_cost,
        "stored_goods": stored_goods,
        "supports_rent": supports_rent,
    }


def _print_warehouse_profile(profile: dict[str, object]) -> None:
    print("WAREHOUSE PROFILE")
    print(f"  Rented capacity: {profile.get('rented_capacity')}")
    print(f"  Used storage: {profile.get('used_storage')}")
    print(f"  Available storage: {profile.get('available_storage')}")
    print(f"  Rental cost per turn: {profile.get('rental_cost_per_turn')}")
    stored_goods = profile.get("stored_goods", {})
    print("  Stored goods list:")
    if isinstance(stored_goods, dict) and stored_goods:
        for sku_id in sorted(stored_goods):
            print(f"    {sku_id}: {stored_goods[sku_id]}")
    else:
        print("    none")


def _execute_location_action_if_available(engine: GameEngine, action_id: str) -> None:
    candidate_map = {
        "deposit_cargo": ["deposit_cargo", "deposit", "store_goods"],
        "withdraw_cargo": ["withdraw_cargo", "withdraw", "retrieve_goods"],
        "rent_additional_space": ["rent_additional_space", "rent_warehouse_space", "rent_space"],
    }
    candidates = candidate_map.get(action_id, [action_id])
    actions = _extract_actions_from_step_result(engine.execute({"type": "list_location_actions"}))
    selected_action = next(
        (
            action
            for action in actions
            if isinstance(action, dict) and str(action.get("action_id")) in set(candidates)
        ),
        None,
    )
    if not isinstance(selected_action, dict):
        print("Action is not available at this location.")
        return
    kwargs = _prompt_action_kwargs(selected_action)
    result = engine.execute(
        {
            "type": "location_action",
            "action_id": selected_action["action_id"],
            "action_kwargs": kwargs,
        }
    )
    print(json.dumps(result, sort_keys=True))


def _compact_manifest(manifest: object) -> dict[str, int]:
    if not isinstance(manifest, dict):
        return {}
    compact: dict[str, int] = {}
    for sku_id, quantity in manifest.items():
        if not isinstance(quantity, int):
            continue
        if int(quantity) <= 0:
            continue
        compact[str(sku_id)] = int(quantity)
    return compact


def _sum_numeric_fields(*, rows: object, candidate_keys: tuple[str, ...]) -> int:
    if not isinstance(rows, list):
        return 0
    total = 0
    for row in rows:
        if not isinstance(row, dict):
            continue
        value = None
        for key in candidate_keys:
            if key in row:
                value = row.get(key)
                break
        if isinstance(value, int):
            total += int(value)
        elif isinstance(value, float):
            total += int(value)
    return int(total)


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
