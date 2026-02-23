from __future__ import annotations

import json
import math
from pathlib import Path

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
    insurance_cost = int(detail.get("insurance_cost_per_turn", 0) or 0)
    warehouse_cost = int(detail.get("warehouse_cost_per_turn", 0) or 0)
    crew_wages = int(detail.get("crew_wages_per_turn", 0) or 0)
    recurring_total = int(detail.get("total_recurring_cost_per_turn", 0) or 0)
    warehouses = detail.get("warehouses", [])
    if not isinstance(warehouses, list):
        warehouses = []
    print("PLAYER / SHIP INFO")
    print(f"  Credits: {detail.get('credits')}")
    fuel_current = int(detail.get('fuel_current', 0) or 0)
    fuel_capacity = int(detail.get('fuel_capacity', 0) or 0)
    print(f"  Fuel: {fuel_current}/{fuel_capacity}")
    if fuel_current > 0:
        print(f"  Max reachable distance: {fuel_current} LY")
    print(f"  Cargo manifest: {cargo_manifest}")
    print(f"  Reputation: {detail.get('reputation_score')} band={detail.get('reputation_band')}")
    print(f"  Heat: {detail.get('heat')}")
    print(f"  Notoriety: {detail.get('notoriety_score')} band={detail.get('notoriety_band')}")
    print(f"  Arrest state: {detail.get('arrest_state')}")
    print(f"  Warrants: {detail.get('warrants')}")
    print(f"  Location: {detail.get('system_id')} / {detail.get('destination_id')} / {detail.get('location_id')}")
    print(f"  Turn: {detail.get('turn')}")
    
    # Display ship information from engine-provided profile
    ship_info = detail.get("ship")
    if ship_info:
        # Get display name for hull
        try:
            from hull_utils import get_hull_display_name
        except ModuleNotFoundError:
            from src.hull_utils import get_hull_display_name
        
        hull_id = ship_info.get('hull_id', 'N/A')
        hull_display_name = get_hull_display_name(hull_id) if isinstance(hull_id, str) else 'N/A'
        
        print("\nSHIP:")
        print(f"  Hull: {hull_display_name} ({hull_id})" if hull_id != 'N/A' else f"  Hull: {hull_display_name}")
        print(f"  Tier: {ship_info.get('tier', 'N/A')}")
        print(f"  Crew: {ship_info.get('crew_current', 0)}/{ship_info.get('crew_capacity', 0)}")
        print(f"  Cargo capacity: Physical {ship_info.get('effective_physical_cargo_capacity', 0)}, Data {ship_info.get('effective_data_cargo_capacity', 0)}")
        print(f"  Fuel capacity: {ship_info.get('fuel_capacity', 0)}")
        subsystem_bands = ship_info.get("subsystem_bands", {})
        if subsystem_bands:
            print(f"  Subsystem bands: Weapon {subsystem_bands.get('weapon', 0)}, Defense {subsystem_bands.get('defense', 0)}, Engine {subsystem_bands.get('engine', 0)}")
        installed_modules = ship_info.get("installed_modules", [])
        if installed_modules:
            print(f"  Installed modules: {', '.join(installed_modules)}")
        else:
            print("  Installed modules: None")
        crew_list = ship_info.get("crew", [])
        if crew_list:
            print("  Crew members:")
            for index, crew_member in enumerate(crew_list, start=1):
                npc_id = crew_member.get('npc_id', 'N/A')
                daily_wage = crew_member.get('daily_wage', 0)
                print(f"    {index}) {npc_id} (wage: {daily_wage})")
        else:
            print("  Crew: None")
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
    print("WAREHOUSE RENTALS")
    if not warehouses:
        print("  none")
    else:
        for index, row in enumerate(warehouses, start=1):
            destination_id = row.get("destination_id")
            capacity = int(row.get("capacity", 0) or 0)
            used = int(row.get("used", 0) or 0)
            available = int(row.get("available", 0) or 0)
            cost = int(row.get("cost_per_turn", 0) or 0)
            goods = row.get("goods", {})
            print(
                f"  {index}) destination={destination_id} capacity={capacity} "
                f"used={used} available={available} cost/turn={cost} goods={goods}"
            )
    
    # Crew dismissal option (same menu grouping as warehouse rental management)
    crew_list = ship_info.get("crew", []) if ship_info else []
    if crew_list:
        print("\nCREW MANAGEMENT")
        print("  [d] Dismiss crew member")
        raw_action = input("Action [Enter skip]: ").strip().lower()
        if raw_action == "d":
            _dismiss_crew_menu(engine)
            return
    
    # Warehouse cancellation
    if warehouses:
        raw_cancel = input("Cancel warehouse rental index [0 skip]: ").strip()
        if raw_cancel in {"", "0"}:
            return
        try:
            selected = int(raw_cancel)
        except ValueError:
            print("Invalid warehouse cancel index.")
            return
        if selected < 1 or selected > len(warehouses):
            print("Invalid warehouse cancel index.")
            return
        destination_id = warehouses[selected - 1].get("destination_id")
        if not isinstance(destination_id, str) or not destination_id:
            print("Invalid warehouse destination.")
            return
        result = engine.execute({"type": "warehouse_cancel", "destination_id": destination_id})
        print(json.dumps(result, sort_keys=True))


def _dismiss_crew_menu(engine: GameEngine) -> None:
    """Handle crew dismissal from Player / Ship Info menu."""
    # Get player profile to access crew list
    result = engine.execute({"type": "get_player_profile"})
    detail = _extract_detail_from_stage(step_result=result, stage="player_profile")
    if not isinstance(detail, dict):
        print("Error: Could not retrieve player profile.")
        return
    
    ship_info = detail.get("ship")
    if not ship_info:
        print("Error: No active ship.")
        return
    
    crew_list = ship_info.get("crew", [])
    if not crew_list:
        print("No crew members to dismiss.")
        return
    
    print("CREW DISMISSAL")
    for index, crew_member in enumerate(crew_list, start=1):
        npc_id = crew_member.get('npc_id', 'N/A')
        daily_wage = crew_member.get('daily_wage', 0)
        print(f"  {index}) {npc_id} (wage: {daily_wage})")
    
    raw_selection = input("Dismiss crew member index [0 cancel]: ").strip()
    if raw_selection in {"", "0"}:
        return
    
    try:
        selected = int(raw_selection)
    except ValueError:
        print("Invalid crew member index.")
        return
    
    if selected < 1 or selected > len(crew_list):
        print("Invalid crew member index.")
        return
    
    npc_id = crew_list[selected - 1].get("npc_id")
    if not isinstance(npc_id, str) or not npc_id:
        print("Invalid crew member ID.")
        return
    
    result = engine.execute({"type": "dismiss_crew", "npc_id": npc_id})
    detail = _extract_detail_from_stage(step_result=result, stage="crew_dismissal")
    if isinstance(detail, dict):
        result_detail = detail.get("result", {})
        if result_detail.get("ok"):
            relocated = result_detail.get("relocated_to", {})
            print(f"Crew member {npc_id} dismissed and relocated to:")
            print(f"  System: {relocated.get('system_id')}")
            print(f"  Destination: {relocated.get('destination_id')}")
            print(f"  Location: {relocated.get('location_id')}")
        else:
            reason = result_detail.get("reason", "unknown_error")
            print(f"Dismissal failed: {reason}")
    else:
        print(json.dumps(result, sort_keys=True))


def _show_system_info(engine: GameEngine) -> None:
    result = engine.execute({"type": "get_system_profile"})
    detail = _extract_detail_from_stage(step_result=result, stage="system_profile")
    if not isinstance(detail, dict):
        print(json.dumps(result, sort_keys=True))
        return
    coords = detail.get("coordinates", {})
    system_id = str(detail.get("system_id", "") or "")
    system_visited = system_id in _visited_system_ids(engine)
    print("SYSTEM INFO")
    print(f"  Name: {detail.get('name')}")
    print(f"  ID: {system_id}")
    if system_visited:
        print(f"  Government: {detail.get('government_id')}")
        print(f"  Population: {detail.get('population')}")
    else:
        print("  Government: Unknown")
        print("  Population: Unknown")
    print(f"  Coordinates: ({coords.get('x')}, {coords.get('y')})")
    if system_visited:
        print(f"  Active situations: {detail.get('active_system_situations')}")
        system = engine.sector.get_system(system_id)
        if system is None:
            print("  Destinations: none")
        else:
            destination_names = [destination.display_name for destination in sorted(system.destinations, key=lambda d: d.destination_id)]
            print(f"  Destinations: {destination_names if destination_names else 'none'}")
    else:
        print("  Active situations: Unknown")
        print("  Destinations: Unknown")
    print(f"  Active flags: {detail.get('active_system_flags')}")
    print("  Reachable systems:")
    for row in detail.get("reachable_systems", []):
        print(
            f"    {row.get('system_id')} {row.get('name')} "
            f"distance_ly={row.get('distance_ly'):.3f} in_range={row.get('in_range')}"
        )
    # Display galaxy map
    print()
    _render_galaxy_map(engine.sector)


def _show_destination_info(engine: GameEngine) -> None:
    result = engine.execute({"type": "get_destination_profile"})
    detail = _extract_detail_from_stage(step_result=result, stage="destination_profile")
    if not isinstance(detail, dict):
        print(json.dumps(result, sort_keys=True))
        return
    destination_id = str(detail.get("destination_id", "") or "")
    destination_visited = destination_id in _visited_destination_ids(engine)
    print("DESTINATION INFO")
    print(f"  Name: {detail.get('name')}")
    print(f"  ID: {destination_id}")
    print(f"  Population: {detail.get('population')}")
    if destination_visited:
        print(f"  Primary economy: {detail.get('primary_economy')}")
    else:
        print("  Primary economy: Unknown")
    print(f"  Market attached: {detail.get('market_attached')}")
    if destination_visited:
        print(f"  Active destination situations: {detail.get('active_destination_situations')}")
    else:
        print("  Active destination situations: Unknown")
    print("  Locations:")
    if not destination_visited:
        print("    Unknown")
    else:
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
                system_id = str(row["system_id"])
                visited = system_id in _visited_system_ids(engine)
                distance = row['distance_ly']
                in_range = distance <= float(current_fuel)
                base = f"{index}) {row['system_id']} {row['name']} distance_ly={distance:.3f} in_range={in_range}"
                if not visited:
                    print(base)
                    continue
                system = row["system"]
                destination_count = len(getattr(system, "destinations", []) or [])
                live_situations = _active_system_situations(engine=engine, system_id=system_id)
                print(
                    f"{base} government={getattr(system, 'government_id', None)} "
                    f"population={getattr(system, 'population', None)} destinations={destination_count} "
                    f"active_situations={live_situations}"
                )
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
                print(f"{index}) {destination.destination_id} {destination.display_name} type={destination.destination_type}")
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
            return
        if location_type == "datanet":
            _datanet_location_menu(engine)
            return
        if location_type == "warehouse":
            _warehouse_location_menu(engine)
            return
        if location_type in {"bar", "administration"}:
            _npc_first_location_menu(engine)
            return
        _location_actions_menu(engine)
        return


def _location_actions_menu(engine: GameEngine) -> None:
    # Check if this is a shipdock location
    list_result = engine.execute({"type": "list_location_actions"})
    actions = _extract_actions_from_step_result(list_result)
    is_shipdock = any(
        action.get("action_id") in {"buy_hull", "buy_module", "sell_hull", "sell_module", "repair_ship"}
        for action in actions
    )
    
    if is_shipdock:
        _shipdock_menu(engine)
        return
    
    # Non-shipdock location actions (original flow)
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
        selected_action = actions[selected - 1]
        
        # Collect parameters if action has them
        action_kwargs = {}
        if selected_action.get("parameters"):
            action_kwargs = _prompt_action_kwargs(selected_action)
        
        # Handle confirmation if required
        confirmed = True
        if selected_action.get("requires_confirm"):
            confirmed = input("Confirm action? (y/n): ").strip().lower() == "y"
            if not confirmed:
                print("Action cancelled.")
                continue
        
        payload = {
            "type": "location_action",
            "action_id": selected_action["action_id"],
            "kwargs": action_kwargs,
            "confirm": confirmed,
        }
        result = engine.execute(payload)
        print(json.dumps(result, sort_keys=True))


def _current_location_type(engine: GameEngine) -> str | None:
    """Get the location_type of the current location."""
    destination = _current_destination_object(engine)
    if destination is None:
        return None
    location_id = engine.player_state.current_location_id
    if not location_id:
        return None
    locations = list(getattr(destination, "locations", []) or [])
    for location in locations:
        if getattr(location, "location_id", None) == location_id:
            return str(getattr(location, "location_type", "") or "")
    return None


def _npc_first_location_menu(engine: GameEngine) -> None:
    while True:
        list_result = engine.execute({"type": "list_location_npcs"})
        detail = _extract_detail_from_stage(step_result=list_result, stage="location_npcs") or {}
        npcs = detail.get("npcs", [])
        if not isinstance(npcs, list):
            npcs = []
        
        location_type = _current_location_type(engine)
        is_administration = location_type == "administration"
        
        print(f"LOCATION: {engine.player_state.current_location_id}")
        
        # Get location actions for administration (filtered to admin_mission_board only)
        location_actions: list[dict[str, object]] = []
        if is_administration:
            list_actions_result = engine.execute({"type": "list_location_actions"})
            all_actions = _extract_actions_from_step_result(list_actions_result)
            location_actions = [a for a in all_actions if isinstance(a, dict) and str(a.get("action_id", "")) == "admin_mission_board"]
        
        if not npcs and not location_actions:
            print("No NPCs or actions present.")
            print("0) Return to destination")
            if input("Select option: ").strip() == "0":
                _return_to_destination(engine)
                print(f"Returned to destination: {engine.player_state.current_location_id}")
                return
            print("Invalid selection.")
            continue
        
        # Display NPCs
        npc_count = 0
        if npcs:
            print("NPCs:")
            for index, row in enumerate(npcs, start=1):
                if not isinstance(row, dict):
                    continue
                name = str(row.get("display_name", "Unknown"))
                role = str(row.get("role", "unknown"))
                print(f"  {index}) {name} ({role})")
                npc_count = index
        
        # Display Location Actions (administration only, filtered to admin_mission_board)
        action_start_index = npc_count + 1
        if location_actions:
            print("Location Actions:")
            for action in location_actions:
                if not isinstance(action, dict):
                    continue
                action_id = str(action.get("action_id", ""))
                display_name = str(action.get("display_name", action_id))
                print(f"  {action_start_index}) {display_name}")
                action_start_index += 1
        
        print("0) Return to destination")
        raw_choice = input("Select option: ").strip()
        if raw_choice == "0":
            _return_to_destination(engine)
            print(f"Returned to destination: {engine.player_state.current_location_id}")
            return
        try:
            selected = int(raw_choice)
        except ValueError:
            print("Invalid selection.")
            continue
        
        # Handle NPC selection
        if 1 <= selected <= npc_count:
            row = npcs[selected - 1]
            if not isinstance(row, dict):
                print("Invalid NPC selection.")
                continue
            npc_id = row.get("npc_id")
            if not isinstance(npc_id, str) or not npc_id:
                print("Invalid NPC selection.")
                continue
            _npc_interactions_menu(engine, npc_id=npc_id)
            continue
        
        # Handle Location Action selection (administration only)
        action_index = selected - npc_count - 1
        if 0 <= action_index < len(location_actions):
            action = location_actions[action_index]
            if not isinstance(action, dict):
                print("Invalid action selection.")
                continue
            action_id = str(action.get("action_id", ""))
            if not action_id:
                print("Invalid action selection.")
                continue
            # Execute location action
            if action_id == "admin_mission_board":
                # Special handling for mission board: allow direct mission acceptance
                action_kwargs = {}
                if action.get("parameters"):
                    action_kwargs = _prompt_action_kwargs(action)
                confirmed = True
                if action.get("requires_confirm"):
                    confirmed = input("Confirm action? (y/n): ").strip().lower() == "y"
                    if not confirmed:
                        print("Action cancelled.")
                        continue
                payload = {"type": "location_action", "action_id": action_id, "kwargs": action_kwargs, "confirm": confirmed}
                result = engine.execute(payload)
                if result.get("ok"):
                    # Extract missions from result["detail"]["missions"] or from events
                    missions = []
                    # First try result["detail"]["missions"]
                    detail = result.get("detail", {})
                    if isinstance(detail, dict):
                        missions_raw = detail.get("missions")
                        if isinstance(missions_raw, list):
                            missions = missions_raw
                    # If not found, try extracting from events
                    if not missions:
                        event_detail = _extract_detail_from_stage(step_result=result, stage="location_action")
                        if event_detail and isinstance(event_detail, dict):
                            missions_raw = event_detail.get("missions")
                            if isinstance(missions_raw, list):
                                missions = missions_raw
                    # Only print "No missions available" if missions list is empty
                    if len(missions) == 0:
                        print("No missions available on the board.")
                        continue
                    # Display numbered list
                    print("MISSION BOARD")
                    for index, mission in enumerate(missions, start=1):
                        mission_type = mission.get("mission_type", "Unknown")
                        mission_tier = mission.get("mission_tier", 0)
                        rewards = mission.get("rewards", [])
                        # Format reward summary
                        reward_summary = []
                        for reward in rewards:
                            if isinstance(reward, dict):
                                reward_type = reward.get("type", "")
                                reward_amount = reward.get("amount", 0)
                                if reward_type == "credits":
                                    reward_summary.append(f"{reward_amount} credits")
                                else:
                                    reward_summary.append(f"{reward_type}: {reward_amount}")
                        reward_text = ", ".join(reward_summary) if reward_summary else "No rewards"
                        print(f"  {index}) {mission_type} (Tier {mission_tier}) – {reward_text}")
                    print()
                    # Prompt for selection
                    raw_choice = input("Select mission index to discuss (0 to cancel): ").strip()
                    if raw_choice == "0":
                        continue
                    try:
                        selected = int(raw_choice)
                    except ValueError:
                        print("Invalid selection.")
                        continue
                    if selected < 1 or selected > len(missions):
                        print("Invalid selection.")
                        continue
                    # Get mission_id from selected mission
                    selected_mission = missions[selected - 1]
                    mission_id = selected_mission.get("mission_id")
                    if not isinstance(mission_id, str) or not mission_id:
                        print("Invalid mission selection.")
                        continue
                    # Call MissionCore.get_details via engine command
                    discuss_result = engine.execute({"type": "mission_discuss", "mission_id": mission_id})
                    if not discuss_result.get("ok"):
                        print(f"Failed to discuss mission: {discuss_result.get('error', 'unknown error')}")
                        continue
                    # Extract mission details from discuss result
                    discuss_detail = _extract_detail_from_stage(step_result=discuss_result, stage="mission")
                    if discuss_detail and isinstance(discuss_detail, dict):
                        result_data = discuss_detail.get("result", {})
                        if isinstance(result_data, dict):
                            # Display mission details
                            mission_type = result_data.get("mission_type", "Unknown")
                            mission_tier = result_data.get("mission_tier", 0)
                            rewards = result_data.get("rewards", [])
                            status = result_data.get("status")
                            text = result_data.get("text")
                            offer_only = result_data.get("offer_only", False)
                            
                            print(f"\nMISSION DETAILS")
                            print(f"  Type: {mission_type}")
                            print(f"  Tier: {mission_tier}")
                            if rewards:
                                reward_summary = []
                                for reward in rewards:
                                    if isinstance(reward, dict):
                                        reward_type = reward.get("type", "")
                                        reward_amount = reward.get("amount", 0)
                                        if reward_type == "credits":
                                            reward_summary.append(f"{reward_amount} credits")
                                        else:
                                            reward_summary.append(f"{reward_type}: {reward_amount}")
                                if reward_summary:
                                    print(f"  Rewards: {', '.join(reward_summary)}")
                            if status:
                                print(f"  Status: {status}")
                            if text:
                                print(f"  {text}")
                            print()
                            
                            # Only prompt for acceptance if offer_only is True
                            if offer_only:
                                confirm = input("Accept this mission? (y/n): ").strip().lower()
                                if confirm == "y":
                                    # Call MissionCore.accept via engine command
                                    accept_result = engine.execute({"type": "mission_accept", "mission_id": mission_id})
                                    if accept_result.get("ok"):
                                        accept_detail = _extract_detail_from_stage(step_result=accept_result, stage="mission")
                                        if accept_detail and isinstance(accept_detail, dict):
                                            if accept_detail.get("accepted"):
                                                print(f"Mission accepted: {mission_id}")
                                            else:
                                                print(f"Mission accept result: {json.dumps(accept_detail, sort_keys=True)}")
                                        else:
                                            print(f"Mission accepted: {mission_id}")
                                    else:
                                        error = accept_result.get('error', 'unknown error')
                                        if error == "mission_accept_failed_total_cap":
                                            print("Cannot accept: total mission limit reached.")
                                        elif error == "mission_accept_failed_tier_cap":
                                            print("Cannot accept: tier limit reached.")
                                        else:
                                            print(f"Failed to accept mission: {error}")
                                else:
                                    print("Mission discussion cancelled.")
                            else:
                                # Mission is not in OFFERED state, cannot accept
                                print("This mission cannot be accepted at this time.")
                    else:
                        print("Failed to retrieve mission details.")
                else:
                    print(f"Action failed: {result.get('error', 'unknown error')}")
            else:
                action_kwargs = {}
                if action.get("parameters"):
                    action_kwargs = _prompt_action_kwargs(action)
                confirmed = True
                if action.get("requires_confirm"):
                    confirmed = input("Confirm action? (y/n): ").strip().lower() == "y"
                    if not confirmed:
                        print("Action cancelled.")
                        continue
                payload = {"type": "location_action", "action_id": action_id, "kwargs": action_kwargs, "confirm": confirmed}
                result = engine.execute(payload)
                if result.get("ok"):
                    detail = _extract_detail_from_stage(step_result=result, stage="location_action")
                    if detail and detail.get("missions"):
                        missions = detail.get("missions", [])
                        print("Available Missions:")
                        for mission in missions:
                            if isinstance(mission, dict):
                                print(f"  Mission ID: {mission.get('mission_id')}")
                                print(f"  Type: {mission.get('mission_type')}")
                                print(f"  Tier: {mission.get('mission_tier')}")
                                print(f"  Rewards: {mission.get('rewards')}")
                                print()
                else:
                    print(f"Action failed: {result.get('error', 'unknown error')}")
            continue
        
        print("Invalid selection.")


def _npc_interactions_menu(engine: GameEngine, *, npc_id: str) -> None:
    while True:
        list_result = engine.execute({"type": "list_npc_interactions", "npc_id": npc_id})
        detail = _extract_detail_from_stage(step_result=list_result, stage="npc_interactions") or {}
        interactions = detail.get("interactions", [])
        if not isinstance(interactions, list):
            interactions = []
        print(f"NPC: {npc_id}")
        for index, row in enumerate(interactions, start=1):
            if not isinstance(row, dict):
                continue
            print(f"{index}) {row.get('display_name')}")
        print("0) Back")
        raw_choice = input("Select interaction index: ").strip()
        if raw_choice == "0":
            return
        try:
            selected = int(raw_choice)
        except ValueError:
            print("Invalid interaction index.")
            continue
        if selected < 1 or selected > len(interactions):
            print("Invalid interaction index.")
            continue
        action = interactions[selected - 1]
        if not isinstance(action, dict):
            print("Invalid interaction index.")
            continue
        interaction_id = action.get("action_id")
        if not isinstance(interaction_id, str) or not interaction_id:
            print("Invalid interaction selection.")
            continue
        result = engine.execute({"type": "npc_interact", "npc_id": npc_id, "interaction_id": interaction_id})
        detail_out = _extract_detail_from_stage(step_result=result, stage="npc_interaction") or {}
        interaction_result = detail_out.get("result")
        if isinstance(interaction_result, dict):
            if isinstance(interaction_result.get("rumor_type"), str):
                print(f"Rumor type: {interaction_result.get('rumor_type')}")
                print(f"Rumor: {interaction_result.get('rumor_text')}")
                hint = interaction_result.get("hint")
                if isinstance(hint, dict):
                    system_id = hint.get("system_id")
                    destination_id = hint.get("destination_id")
                    if isinstance(system_id, str) and system_id:
                        if isinstance(destination_id, str) and destination_id:
                            print(f"Hint: system={system_id} destination={destination_id}")
                        else:
                            print(f"Hint: system={system_id}")
            elif interaction_result.get("offer_only") is True:
                # Mission offer - show details and prompt for confirmation
                mission_id = interaction_result.get("mission_id")
                mission_type = interaction_result.get("mission_type")
                mission_tier = interaction_result.get("mission_tier")
                rewards = interaction_result.get("rewards")
                print("MISSION OFFER")
                print(f"  Mission ID: {mission_id}")
                print(f"  Type: {mission_type}")
                print(f"  Tier: {mission_tier}")
                print(f"  Rewards: {rewards}")
                print()
                confirm = input("Accept this mission? (y/n): ").strip().lower()
                if confirm == "y":
                    # Call MissionCore.accept via engine command
                    accept_result = engine.execute({"type": "mission_accept", "mission_id": mission_id})
                    if accept_result.get("ok"):
                        accept_detail = _extract_detail_from_stage(step_result=accept_result, stage="mission")
                        if accept_detail and isinstance(accept_detail, dict):
                            if accept_detail.get("accepted"):
                                print(f"Mission accepted: {mission_id}")
                            else:
                                print(f"Mission accept result: {json.dumps(accept_detail, sort_keys=True)}")
                        else:
                            print(f"Mission accepted: {mission_id}")
                    else:
                        error = accept_result.get('error', 'unknown error')
                        if error == "mission_accept_failed_total_cap":
                            print("Cannot accept: total mission limit reached.")
                        elif error == "mission_accept_failed_tier_cap":
                            print("Cannot accept: tier limit reached.")
                        else:
                            print(f"Failed to accept mission: {error}")
                else:
                    print("Mission offer declined.")
            elif isinstance(interaction_result.get("missions"), list):
                missions = interaction_result.get("missions", [])
                print("Available Missions:")
                for mission in missions:
                    if isinstance(mission, dict):
                        print(f"  Mission ID: {mission.get('mission_id')}")
                        print(f"  Type: {mission.get('mission_type')}")
                        print(f"  Tier: {mission.get('mission_tier')}")
                        print(f"  Rewards: {mission.get('rewards')}")
                        print()
            elif interaction_result.get("status") == "active" and isinstance(interaction_result.get("text"), str):
                # Active mission status message
                print(str(interaction_result.get("text")))
            elif isinstance(interaction_result.get("text"), str):
                # Generic text response (e.g., resolved mission placeholder)
                print(str(interaction_result.get("text")))
            elif interaction_result.get("paid") is not None:
                print(f"Fines paid: {interaction_result.get('paid')}")
            elif interaction_result.get("cleared_warrants") is not None:
                print(f"Warrants cleared: {interaction_result.get('cleared_warrants')}")
            elif interaction_result.get("accepted"):
                print(f"Mission accepted: {interaction_result.get('mission_id')}")
            else:
                print(json.dumps(interaction_result, sort_keys=True))
        else:
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
        print("1) Rent space")
        print("2) Deposit cargo")
        print("3) Withdraw cargo")
        print("4) Return to Destination")
        raw_action = input("Select action index: ").strip()
        if raw_action == "1":
            raw_units = input("Units to rent: ").strip()
            try:
                units = int(raw_units)
            except ValueError:
                print("Invalid units.")
                continue
            payload = {
                "type": "location_action",
                "action_id": "warehouse_rent",
                "kwargs": {"units": units},
                "confirm": True,
            }
            result = engine.execute(payload)
            print(json.dumps(result, sort_keys=True))
            continue
        if raw_action == "2":
            player_profile = _extract_detail_from_stage(
                step_result=engine.execute({"type": "get_player_profile"}),
                stage="player_profile",
            )
            cargo_manifest = {}
            if isinstance(player_profile, dict):
                cargo_manifest = _compact_manifest(player_profile.get("cargo_manifest", {}))
            if not cargo_manifest:
                print("No cargo available to deposit.")
                continue
            cargo_skus = sorted(cargo_manifest.keys())
            for index, sku_id in enumerate(cargo_skus, start=1):
                print(f"{index}) {sku_id} units={cargo_manifest.get(sku_id)}")
            raw_index = input("Select cargo SKU index: ").strip()
            try:
                selected_index = int(raw_index)
            except ValueError:
                print("Invalid cargo SKU index.")
                continue
            if selected_index < 1 or selected_index > len(cargo_skus):
                print("Invalid cargo SKU index.")
                continue
            selected_sku_id = cargo_skus[selected_index - 1]
            raw_qty = input("Quantity: ").strip()
            try:
                quantity = int(raw_qty)
            except ValueError:
                print("Invalid quantity.")
                continue
            payload = {
                "type": "location_action",
                "action_id": "warehouse_deposit",
                "kwargs": {"sku_id": selected_sku_id, "quantity": quantity},
                "confirm": True,
            }
            result = engine.execute(payload)
            print(json.dumps(result, sort_keys=True))
            continue
        if raw_action == "3":
            raw_sku_id = input("SKU ID: ").strip()
            raw_qty = input("Quantity: ").strip()
            try:
                quantity = int(raw_qty)
            except ValueError:
                print("Invalid quantity.")
                continue
            payload = {
                "type": "location_action",
                "action_id": "warehouse_withdraw",
                "kwargs": {"sku_id": raw_sku_id, "quantity": quantity},
                "confirm": True,
            }
            result = engine.execute(payload)
            print(json.dumps(result, sort_keys=True))
            continue
        if raw_action == "4":
            _return_to_destination(engine)
            print(f"Returned to destination: {engine.player_state.current_location_id}")
            return
        print("Invalid action index.")


def main() -> None:
    seed = _prompt_seed()
    engine = GameEngine(world_seed=seed)
    log_path = str((Path(__file__).resolve().parents[1] / "logs" / f"gameplay_seed_{seed}.log"))
    _ = engine.execute({"type": "set_logging", "enabled": True, "log_path": log_path, "truncate": True})
    print(f"Logging to {log_path}")
    _configure_cli_test_fuel(engine)
    print(json.dumps({"event": "engine_init", "seed": seed}, sort_keys=True))
    # Display galaxy map at game start
    _render_galaxy_map(engine.sector)
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


def _render_galaxy_map(sector, width: int = 80, height: int = 30) -> None:
    """Render ASCII grid map of galaxy systems."""
    if not sector.systems:
        print("No systems to display.")
        return
    
    # Sort systems by system_id to assign stable indices
    sorted_systems = sorted(sector.systems, key=lambda s: s.system_id)
    
    # Find coordinate bounds
    min_x = min(s.x for s in sorted_systems)
    max_x = max(s.x for s in sorted_systems)
    min_y = min(s.y for s in sorted_systems)
    max_y = max(s.y for s in sorted_systems)
    
    # Add small padding to avoid edge issues
    x_range = max_x - min_x
    y_range = max_y - min_y
    if x_range < 1e-6:
        x_range = 1.0
        min_x -= 0.5
        max_x += 0.5
    if y_range < 1e-6:
        y_range = 1.0
        min_y -= 0.5
        max_y += 0.5
    
    # Create grid
    grid: List[List[str | None]] = [[None for _ in range(width)] for _ in range(height)]
    collisions: List[tuple[int, int, List[tuple[int, str, str]]]] = []  # (row, col, [(index, system_id, name)])
    
    # Map systems to grid cells
    for index, system in enumerate(sorted_systems, start=1):
        # Normalize coordinates to [0, 1]
        norm_x = (system.x - min_x) / x_range
        norm_y = (system.y - min_y) / y_range
        
        # Map to grid coordinates (flip y for display: top is max_y)
        col = int(norm_x * (width - 1))
        row = int((1.0 - norm_y) * (height - 1))
        
        # Clamp to grid bounds
        col = max(0, min(width - 1, col))
        row = max(0, min(height - 1, row))
        
        # Format label (2-3 digits)
        if index <= 99:
            label = f"{index:02d}"
        else:
            label = f"{index:03d}"
        
        # Handle collisions
        if grid[row][col] is not None:
            # Find or create collision entry
            collision_entry = None
            for i, (r, c, systems_list) in enumerate(collisions):
                if r == row and c == col:
                    collision_entry = i
                    break
            if collision_entry is None:
                # First collision at this cell - mark existing system
                existing_label = grid[row][col]
                existing_index = int(existing_label) if existing_label and existing_label.isdigit() else 0
                if existing_index > 0:
                    existing_sys = sorted_systems[existing_index - 1]
                    collisions.append((row, col, [(existing_index, existing_sys.system_id, existing_sys.name)]))
                    collision_entry = len(collisions) - 1
                else:
                    collisions.append((row, col, []))
                    collision_entry = len(collisions) - 1
            collisions[collision_entry][2].append((index, system.system_id, system.name))
            grid[row][col] = "*"
        else:
            grid[row][col] = label
    
    # Print grid
    print("\nGALAXY MAP")
    print("=" * width)
    for row in grid:
        line = ""
        for cell in row:
            if cell is None:
                line += " "
            else:
                line += str(cell)
        print(line)
    print("=" * width)
    
    # Print legend
    print("\nLEGEND:")
    for index, system in enumerate(sorted_systems, start=1):
        label = f"{index:02d}" if index <= 99 else f"{index:03d}"
        print(f"  {label} {system.system_id} {system.name} (x={system.x:.3f}, y={system.y:.3f})")
    
    # Print collisions if any
    if collisions:
        print("\nCOLLISIONS (multiple systems in same cell):")
        for row, col, systems_list in collisions:
            print(f"  Cell ({row}, {col}):")
            for idx, sys_id, sys_name in systems_list:
                label = f"{idx:02d}" if idx <= 99 else f"{idx:03d}"
                print(f"    {label} {sys_id} {sys_name}")
    print()


def _print_current_system_destinations(engine: GameEngine) -> None:
    system = engine.sector.get_system(engine.player_state.current_system_id)
    if system is None:
        return
    destinations = sorted(system.destinations, key=lambda destination: destination.destination_id)
    print("Intra-system destinations:")
    for index, destination in enumerate(destinations, start=1):
        print(f"  {index}) {destination.destination_id} {destination.display_name} type={destination.destination_type}")


def _configure_cli_test_fuel(engine: GameEngine) -> None:
    active_ship = engine.fleet_by_id.get(engine.player_state.active_ship_id)
    if active_ship is None:
        return
    # Set fuel to capacity for testing (no hardcoded value)
    if active_ship.fuel_capacity > 0:
        active_ship.current_fuel = active_ship.fuel_capacity


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


def _print_destination_context(engine: GameEngine) -> None:
    """Print standardized destination context block."""
    context = engine.get_current_destination_context()
    
    print("-" * 40)
    print(f"Destination: {context.get('destination_name', 'Unknown')} ({context.get('destination_type', 'unknown')})")
    print(f"System: {context.get('system_name', 'Unknown')}", end="")
    
    system_government = context.get('system_government', '')
    if system_government:
        print(f" ({system_government})")
    else:
        print()
    
    population = context.get('population', 0)
    if population > 0:
        print(f"Population: {population}")
    
    primary_economy = context.get('primary_economy')
    secondary_economies = context.get('secondary_economies', [])
    
    if primary_economy:
        economy_str = primary_economy
        if secondary_economies:
            economy_str += f" ({', '.join(secondary_economies)})"
        print(f"Economy: {economy_str}")
    
    situations = context.get('active_situations', [])
    if situations:
        print(f"Situations: {', '.join(situations)}")
    else:
        print("Situations: None")
    
    print("-" * 40)


def _destination_actions_menu(engine: GameEngine) -> None:
    # Display destination context before menu
    _print_destination_context(engine)
    
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


def _shipdock_menu(engine: GameEngine) -> None:
    """Shipdock location menu with numbered lists for all actions."""
    while True:
        print(f"SHIPDOCK: {engine.player_state.current_location_id}")
        print("1) Buy Hull")
        print("2) Buy Module")
        print("3) Sell Hull")
        print("4) Sell Module")
        print("5) Repair Ship")
        print("6) Return to Destination")
        
        raw_choice = input("Select action: ").strip()
        if raw_choice == "6":
            _return_to_destination(engine)
            print(f"Returned to destination: {engine.player_state.current_location_id}")
            return
        elif raw_choice == "1":
            _shipdock_buy_hull(engine)
        elif raw_choice == "2":
            _shipdock_buy_module(engine)
        elif raw_choice == "3":
            _shipdock_sell_hull(engine)
        elif raw_choice == "4":
            _shipdock_sell_module(engine)
        elif raw_choice == "5":
            _shipdock_repair_ship(engine)
        else:
            print("Invalid selection.")


def _shipdock_buy_hull(engine: GameEngine) -> None:
    """Buy hull from shipdock - shows numbered list."""
    result = engine.execute({"type": "shipdock_hull_list"})
    rows = _extract_rows_from_stage(step_result=result, stage="shipdock_hull_list")
    if not rows:
        print("No hulls available at this shipdock.")
        return
    
    print("AVAILABLE HULLS:")
    for index, row in enumerate(rows, start=1):
        print(
            f"{index}) {row.get('display_name', row.get('hull_id', 'Unknown'))} "
            f"(Tier {row.get('tier', 0)}) - {row.get('price', 0)} credits"
        )
    
    raw_index = input("Select hull index (0 to cancel): ").strip()
    if raw_index == "0":
        return
    try:
        selected = int(raw_index)
    except ValueError:
        print("Invalid index.")
        return
    if selected < 1 or selected > len(rows):
        print("Invalid index.")
        return
    
    hull_id = rows[selected - 1]["hull_id"]
    # Auto-select active ship
    ship_id = engine.player_state.active_ship_id
    if not ship_id:
        print("No active ship available.")
        return
    
    # Handle confirmation
    confirmed = True
    print(f"Purchase {rows[selected - 1].get('display_name', hull_id)} for {rows[selected - 1].get('price', 0)} credits?")
    confirmed = input("Confirm? (y/n): ").strip().lower() == "y"
    if not confirmed:
        print("Purchase cancelled.")
        return
    
    payload = {
        "type": "location_action",
        "action_id": "buy_hull",
        "kwargs": {"hull_id": hull_id, "ship_id": ship_id},
        "confirm": confirmed,
    }
    result = engine.execute(payload)
    print(json.dumps(result, sort_keys=True))


def _shipdock_buy_module(engine: GameEngine) -> None:
    """Buy module from shipdock - shows numbered list."""
    result = engine.execute({"type": "shipdock_module_list"})
    rows = _extract_rows_from_stage(step_result=result, stage="shipdock_module_list")
    if not rows:
        print("No modules available at this shipdock.")
        return
    
    print("AVAILABLE MODULES:")
    for index, row in enumerate(rows, start=1):
        print(
            f"{index}) {row.get('display_name', row.get('module_id', 'Unknown'))} "
            f"({row.get('slot_type', 'unknown')}) - {row.get('price', 0)} credits"
        )
    
    raw_index = input("Select module index (0 to cancel): ").strip()
    if raw_index == "0":
        return
    try:
        selected = int(raw_index)
    except ValueError:
        print("Invalid index.")
        return
    if selected < 1 or selected > len(rows):
        print("Invalid index.")
        return
    
    module_id = rows[selected - 1]["module_id"]
    # Auto-select active ship
    ship_id = engine.player_state.active_ship_id
    if not ship_id:
        print("No active ship available.")
        return
    
    payload = {
        "type": "location_action",
        "action_id": "buy_module",
        "kwargs": {"module_id": module_id, "ship_id": ship_id},
        "confirm": True,
    }
    result = engine.execute(payload)
    print(json.dumps(result, sort_keys=True))


def _shipdock_sell_hull(engine: GameEngine) -> None:
    """Sell hull at shipdock - shows numbered list of owned ships."""
    result = engine.execute({"type": "shipdock_ship_list"})
    rows = _extract_rows_from_stage(step_result=result, stage="shipdock_ship_list")
    if not rows:
        print("No ships available to sell at this destination.")
        return
    
    print("OWNED SHIPS (eligible to sell):")
    for index, row in enumerate(rows, start=1):
        print(
            f"{index}) {row.get('display_name', row.get('ship_id', 'Unknown'))} "
            f"(Tier {row.get('tier', 0)}) - {row.get('price', 0)} credits"
        )
    
    raw_index = input("Select ship index to sell (0 to cancel): ").strip()
    if raw_index == "0":
        return
    try:
        selected = int(raw_index)
    except ValueError:
        print("Invalid index.")
        return
    if selected < 1 or selected > len(rows):
        print("Invalid index.")
        return
    
    ship_id = rows[selected - 1]["ship_id"]
    
    # Handle confirmation
    print(f"Sell {rows[selected - 1].get('display_name', ship_id)} for {rows[selected - 1].get('price', 0)} credits?")
    confirmed = input("Confirm? (y/n): ").strip().lower() == "y"
    if not confirmed:
        print("Sale cancelled.")
        return
    
    payload = {
        "type": "location_action",
        "action_id": "sell_hull",
        "kwargs": {"ship_id": ship_id},
        "confirm": confirmed,
    }
    result = engine.execute(payload)
    print(json.dumps(result, sort_keys=True))


def _shipdock_sell_module(engine: GameEngine) -> None:
    """Sell module at shipdock - shows numbered list of installed modules."""
    # Default to active ship
    ship_id = engine.player_state.active_ship_id
    if not ship_id:
        print("No active ship available.")
        return
    
    result = engine.execute({"type": "shipdock_installed_modules_list", "ship_id": ship_id})
    rows = _extract_rows_from_stage(step_result=result, stage="shipdock_installed_modules_list")
    if not rows:
        print("No modules installed on active ship.")
        return
    
    print("INSTALLED MODULES:")
    for index, row in enumerate(rows, start=1):
        print(
            f"{index}) {row.get('display_name', row.get('module_id', 'Unknown'))} "
            f"({row.get('slot_type', 'unknown')}) - {row.get('price', 0)} credits"
        )
    
    raw_index = input("Select module index to sell (0 to cancel): ").strip()
    if raw_index == "0":
        return
    try:
        selected = int(raw_index)
    except ValueError:
        print("Invalid index.")
        return
    if selected < 1 or selected > len(rows):
        print("Invalid index.")
        return
    
    module_id = rows[selected - 1]["module_id"]
    
    payload = {
        "type": "location_action",
        "action_id": "sell_module",
        "kwargs": {"module_id": module_id, "ship_id": ship_id},
        "confirm": True,
    }
    result = engine.execute(payload)
    print(json.dumps(result, sort_keys=True))


def _shipdock_repair_ship(engine: GameEngine) -> None:
    """Repair ship - single step action."""
    # Default to active ship
    ship_id = engine.player_state.active_ship_id
    if not ship_id:
        print("No active ship available.")
        return
    
    payload = {
        "type": "location_action",
        "action_id": "repair_ship",
        "kwargs": {"ship_id": ship_id},
        "confirm": True,
    }
    result = engine.execute(payload)
    print(json.dumps(result, sort_keys=True))


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
    warehouse = getattr(engine.player_state, "warehouses", {}).get(destination_id, {})
    player_profile = _extract_detail_from_stage(
        step_result=engine.execute({"type": "get_player_profile"}),
        stage="player_profile",
    )
    profile_row: dict[str, object] = {}
    if isinstance(player_profile, dict):
        for row in player_profile.get("warehouses", []):
            if isinstance(row, dict) and row.get("destination_id") == destination_id:
                profile_row = row
                break
    stored_goods: dict[str, int] = {}
    if isinstance(warehouse, dict):
        goods_raw = warehouse.get("goods", {})
        if isinstance(goods_raw, dict):
            stored_goods = {
                str(sku_id): int(quantity)
                for sku_id, quantity in goods_raw.items()
                if isinstance(quantity, int) and int(quantity) > 0
            }
    rented_capacity = int((warehouse or {}).get("capacity", 0) or 0)
    used_storage = int(sum(int(value) for value in stored_goods.values()))
    available_storage = max(0, int(rented_capacity - used_storage))
    rental_cost = int(profile_row.get("cost_per_turn", 0) or 0)
    return {
        "rented_capacity": rented_capacity,
        "used_storage": used_storage,
        "available_storage": available_storage,
        "rental_cost_per_turn": rental_cost,
        "stored_goods": stored_goods,
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


def _visited_system_ids(engine: GameEngine) -> set[str]:
    raw = getattr(engine.player_state, "visited_system_ids", set())
    if isinstance(raw, set):
        return {entry for entry in raw if isinstance(entry, str)}
    if isinstance(raw, list):
        return {entry for entry in raw if isinstance(entry, str)}
    return set()


def _visited_destination_ids(engine: GameEngine) -> set[str]:
    raw = getattr(engine.player_state, "visited_destination_ids", set())
    if isinstance(raw, set):
        return {entry for entry in raw if isinstance(entry, str)}
    if isinstance(raw, list):
        return {entry for entry in raw if isinstance(entry, str)}
    return set()


def _active_system_situations(*, engine: GameEngine, system_id: str) -> list[str]:
    helper = getattr(engine, "_active_situation_rows_for_system", None)
    if not callable(helper):
        return []
    rows = helper(system_id=system_id)
    if not isinstance(rows, list):
        return []
    return sorted(
        [
            str(row.get("situation_id"))
            for row in rows
            if isinstance(row, dict) and isinstance(row.get("situation_id"), str)
        ]
    )


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
        # Handle dict parameters (new format: {"name": "...", "type": "...", "prompt": "..."})
        if isinstance(param, dict):
            param_name = param.get("name", "")
            param_prompt = param.get("prompt", param_name)
            param_type = param.get("type", "str")
            if not param_name:
                continue
            raw = input(f"{param_prompt}: ").strip()
            if param_type == "int":
                try:
                    kwargs[param_name] = int(raw)
                except ValueError:
                    kwargs[param_name] = raw
            elif param_type == "bool":
                kwargs[param_name] = raw.lower() in {"1", "true", "yes", "y"}
            else:
                kwargs[param_name] = raw
        # Handle string parameters (legacy format for backward compatibility)
        elif isinstance(param, str):
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
