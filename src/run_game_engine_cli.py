from __future__ import annotations

import json
import math
from pathlib import Path

from game_engine import GameEngine


def _is_game_over_result(result: dict) -> bool:
    """Check if a result indicates game over."""
    if not isinstance(result, dict):
        return False
    if result.get("error") == "game_over":
        return True
    if result.get("game_over_reason"):
        return True
    # also support engine returning detail.reason if needed
    detail = result.get("detail")
    if isinstance(detail, dict) and detail.get("reason") in ("ship_destroyed", "tier2_arrest"):
        return True
    return False


def _print_game_over(result: dict) -> None:
    """Print game over message with reason."""
    reason = result.get("game_over_reason")
    if not reason:
        detail = result.get("detail")
        if isinstance(detail, dict):
            reason = detail.get("reason")
    if not reason:
        reason = "unknown"
    print("")
    print("=== GAME OVER ===")
    print(f"Reason: {reason}")
    print("Only option is Quit.")
    print("")


def _game_over_loop(engine: GameEngine, last_result: dict) -> None:
    """Enter quit-only loop after game over."""
    while True:
        print("1) Quit")
        choice = input("Select: ").strip()
        if choice == "1":
            engine.execute({"type": "quit"})
            raise SystemExit(0)
        else:
            print("Game over. Please quit.")


def _prompt_seed() -> int:
    raw = input("Seed [12345]: ").strip()
    if not raw:
        return 12345
    try:
        return int(raw)
    except ValueError:
        return 12345


def _prompt_admin_override() -> dict | None:
    """
    Prompt for admin starting ship override.
    Returns override dict or None if user declines.
    """
    response = input("Use admin custom starting ship? (y/n): ").strip().lower()
    if response != "y":
        return None
    
    # Load hull catalog
    from data_loader import load_hulls, load_modules
    from ship_assembler import get_slot_distribution
    
    hulls_data = load_hulls()
    hulls_list = hulls_data.get("hulls", [])
    
    if not hulls_list:
        raise ValueError("No hulls found in hulls.json")
    
    # Print indexed hull list
    print("\nAvailable Hulls:")
    for idx, hull in enumerate(hulls_list, start=1):
        name = hull.get("name", "Unknown")
        hull_id = hull.get("hull_id", "unknown")
        tier = hull.get("tier", "?")
        frame = hull.get("frame", "?")
        print(f"  [{idx}] {name} | {hull_id} | tier {tier} | {frame}")
    
    # Prompt for hull selection
    while True:
        raw = input("\nSelect hull index: ").strip()
        try:
            hull_idx = int(raw)
            if 1 <= hull_idx <= len(hulls_list):
                selected_hull = hulls_list[hull_idx - 1]
                hull_id = selected_hull.get("hull_id")
                frame = selected_hull.get("frame")
                tier = selected_hull.get("tier")
                break
            else:
                print(f"Invalid index. Please choose 1-{len(hulls_list)}")
        except ValueError:
            print("Invalid input. Please enter a number.")
    
    # Determine slot distribution
    slots = get_slot_distribution(frame, tier)
    weapon_slots = slots["weapon_slots"]
    defense_slots = slots["defense_slots"]
    utility_slots = slots["utility_slots"]
    untyped_slots = slots["untyped_slots"]
    total_slots = slots["total_slots"]
    
    print(f"\nSlot distribution: weapon={weapon_slots}, defense={defense_slots}, utility={utility_slots}, untyped={untyped_slots}, total={total_slots}")
    
    # Load module catalog
    modules_data = load_modules()
    modules_list = modules_data.get("modules", [])
    
    if not modules_list:
        raise ValueError("No modules found in modules.json")
    
    # Build modules by slot type
    modules_by_slot = {
        "weapon": [m for m in modules_list if m.get("slot_type") == "weapon"],
        "defense": [m for m in modules_list if m.get("slot_type") == "defense"],
        "utility": [m for m in modules_list if m.get("slot_type") == "utility"],
    }
    
    # Build slot list with types
    slot_list = []
    for _ in range(weapon_slots):
        slot_list.append("weapon")
    for _ in range(defense_slots):
        slot_list.append("defense")
    for _ in range(utility_slots):
        slot_list.append("utility")
    for _ in range(untyped_slots):
        slot_list.append("untyped")
    
    # Prompt for each slot
    selected_modules = []
    for slot_idx, slot_type in enumerate(slot_list, start=1):
        print(f"\nSlot {slot_idx} ({slot_type.upper()})")
        print("  0) Leave empty")
        
        # Show modules matching slot type (or all if untyped)
        if slot_type == "untyped":
            available_modules = modules_list
        else:
            available_modules = modules_by_slot[slot_type]
        
        if not available_modules:
            print("  (No modules available for this slot type)")
        else:
            for mod_idx, module in enumerate(available_modules, start=1):
                module_name = module.get("name", "Unknown")
                module_id = module.get("module_id", "unknown")
                print(f"  [{mod_idx}] {module_name} ({module_id})")
        
        # Prompt for module selection
        while True:
            raw = input("Select module index for this slot: ").strip()
            try:
                mod_idx = int(raw)
                if mod_idx == 0:
                    # Leave empty
                    break
                elif 1 <= mod_idx <= len(available_modules):
                    selected_module = available_modules[mod_idx - 1]
                    module_id = selected_module.get("module_id")
                    selected_modules.append({"module_id": module_id})
                    break
                else:
                    print(f"Invalid index. Please choose 0-{len(available_modules)}")
            except ValueError:
                print("Invalid input. Please enter a number.")
    
    # Build override dict
    override = {
        "hull_id": hull_id,
        "modules": selected_modules,
    }
    
    return override


def _show_player_info(engine: GameEngine) -> None:
    """Main Player / Ship Info submenu entry point."""
    # Get player profile for summary display
    result = engine.execute({"type": "get_player_profile"})
    detail = _extract_detail_from_stage(step_result=result, stage="player_profile")
    if not isinstance(detail, dict):
        print("Error: Could not retrieve player profile.")
        return
    
    destination_result = engine.execute({"type": "get_destination_profile"})
    if _is_game_over_result(destination_result):
        _print_game_over(destination_result)
        _game_over_loop(engine, destination_result)
        return
    
    destination_profile = _extract_detail_from_stage(
        step_result=destination_result,
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
    
    # Display comprehensive player information summary
    print("\n=== PLAYER / SHIP INFO ===")
    print(f"Credits: {detail.get('credits', 0)}")
    fuel_current = int(detail.get('fuel_current', 0) or 0)
    fuel_capacity = int(detail.get('fuel_capacity', 0) or 0)
    print(f"Fuel: {fuel_current}/{fuel_capacity}")
    if fuel_current > 0:
        print(f"Max reachable distance: {fuel_current} LY")
    print(f"Cargo manifest: {cargo_manifest}")
    print(f"Reputation: {detail.get('reputation_score', 0)} band={detail.get('reputation_band', 0)}")
    print(f"Heat: {detail.get('heat', 0)}")
    print(f"Notoriety: {detail.get('notoriety_score', 0)} band={detail.get('notoriety_band', 0)}")
    print(f"Arrest state: {detail.get('arrest_state', 'free')}")
    print(f"Warrants: {detail.get('warrants', [])}")
    print(f"Location: {detail.get('system_id', 'N/A')} / {detail.get('destination_id', 'N/A')} / {detail.get('location_id', 'N/A')}")
    print(f"Turn: {detail.get('turn', 0)}")
    
    # Display ship information from engine-provided profile
    ship_info = detail.get("ship")
    if ship_info:
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
    
    # Display short summary of active missions (detailed info in Missions submenu)
    active_missions = engine.get_active_missions()
    if active_missions:
        print(f"\nACTIVE MISSIONS: {len(active_missions)}")
        for mission in active_missions:
            mission_type = mission.get("mission_type", "N/A")
            mission_tier = mission.get("mission_tier", 0)
            target_dest = mission.get("target_destination_id") or mission.get("target_system_id", "N/A")
            if target_dest is None:
                target_dest = "N/A"
            print(f"  {mission_type} (T{mission_tier}) → {target_dest}")
    else:
        print("\nACTIVE MISSIONS: None")
    
    print("\nONGOING COSTS")
    print(f"  Insurance: {insurance_cost}")
    print(f"  Warehouse rental: {warehouse_cost}")
    print(f"  Crew wages: {crew_wages}")
    print(f"  Total recurring cost: {recurring_total}")
    
    print("\nWAREHOUSE RENTALS")
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
    
    # Submenu for detailed management
    while True:
        print("\nOptions:")
        print("0) Back")
        print("1) Ships And Modules")
        print("2) Financial")
        print("3) Missions")
        choice = input("Select: ").strip()
        
        if choice == "0":
            return
        elif choice == "1":
            _show_ships_and_modules(engine)
        elif choice == "2":
            _show_financial(engine)
        elif choice == "3":
            _show_missions(engine)
        else:
            print("Invalid selection.")


def _show_ships_and_modules(engine: GameEngine) -> None:
    """Ships And Modules submenu."""
    # Get owned ships from engine
    owned_ships = engine.get_owned_ships()
    active_ship = engine.get_active_ship()
    
    print("\n=== SHIPS AND MODULES ===")
    
    # Display active ship
    if active_ship:
        print("\nACTIVE SHIP:")
        print(f"  Ship ID: {active_ship.get('ship_id', 'N/A')}")
        print(f"  Hull ID: {active_ship.get('hull_id', 'N/A')}")
        hull_integrity = active_ship.get('hull_integrity', {})
        if isinstance(hull_integrity, dict):
            current = hull_integrity.get('current', 0)
            max_hull = hull_integrity.get('max', 0)
            pct = int((current / max_hull * 100)) if max_hull > 0 else 0
            print(f"  Hull Integrity: {current}/{max_hull} ({pct}%)")
        fuel_info = active_ship.get('fuel', {})
        if isinstance(fuel_info, dict):
            current = fuel_info.get('current', 0)
            capacity = fuel_info.get('capacity', 0)
            print(f"  Fuel: {current}/{capacity}")
        
        # Installed modules
        modules = engine.get_ship_modules(active_ship.get('ship_id', ''))
        if modules:
            print("  Installed Modules:")
            for slot_idx, module in enumerate(modules, start=0):
                module_id = module.get('module_id', 'N/A')
                slot_type = module.get('slot_type', 'N/A')
                print(f"    Slot {slot_idx} ({slot_type}): {module_id}")
        else:
            print("  Installed Modules: None")
        
        # Cargo summary
        cargo = engine.get_ship_cargo(active_ship.get('ship_id', ''))
        if cargo:
            cargo_summary = _compact_manifest(cargo)
            print(f"  Cargo: {cargo_summary}")
        else:
            print("  Cargo: None")
    else:
        print("\nACTIVE SHIP: None")
    
    # Display inactive ships
    active_ship_id = active_ship.get('ship_id') if active_ship else None
    inactive_ships = [s for s in owned_ships if s.get('ship_id') != active_ship_id]
    if inactive_ships:
        print("\nINACTIVE SHIPS:")
        for ship in inactive_ships:
            print(f"  Ship ID: {ship.get('ship_id', 'N/A')}")
            print(f"    Hull ID: {ship.get('hull_id', 'N/A')}")
            print(f"    Destination: {ship.get('destination_id', 'N/A')}")
            hull_integrity = ship.get('hull_integrity', {})
            if isinstance(hull_integrity, dict):
                current = hull_integrity.get('current', 0)
                max_hull = hull_integrity.get('max', 0)
                pct = int((current / max_hull * 100)) if max_hull > 0 else 0
                print(f"    Hull Integrity: {current}/{max_hull} ({pct}%)")
            cargo = engine.get_ship_cargo(ship.get('ship_id', ''))
            if cargo:
                cargo_summary = _compact_manifest(cargo)
                print(f"    Cargo: {cargo_summary}")
            else:
                print(f"    Cargo: None")
    
    # Submenu options
    while True:
        print("\nOptions:")
        print("0) Back")
        print("1) Change Active Ship")
        print("2) Install Module")
        print("3) Uninstall Module")
        print("4) Transfer Cargo")
        choice = input("Select: ").strip()
        
        if choice == "0":
            return
        elif choice == "1":
            _change_active_ship(engine)
            break
        elif choice == "2":
            _install_module(engine)
            break
        elif choice == "3":
            _uninstall_module(engine)
            break
        elif choice == "4":
            _transfer_cargo(engine)
            break
        else:
            print("Invalid selection.")


def _change_active_ship(engine: GameEngine) -> None:
    """Change active ship submenu."""
    owned_ships = engine.get_owned_ships()
    active_ship = engine.get_active_ship()
    
    if len(owned_ships) <= 1:
        print("Only one ship owned. Cannot change active ship.")
        return
    
    active_ship_id = active_ship.get('ship_id') if active_ship else None
    inactive_ships = [s for s in owned_ships if s.get('ship_id') != active_ship_id]
    if not inactive_ships:
        print("No inactive ships available.")
        return
    
    print("\nInactive Ships:")
    for idx, ship in enumerate(inactive_ships, start=1):
        print(f"  {idx}) {ship.get('ship_id', 'N/A')} - {ship.get('hull_id', 'N/A')} at {ship.get('destination_id', 'N/A')}")
    
    try:
        raw = input("\nSelect ship index [0 cancel]: ").strip()
        if raw == "0":
            return
        selected_idx = int(raw)
        if selected_idx < 1 or selected_idx > len(inactive_ships):
            print("Invalid selection.")
            return
        target_ship = inactive_ships[selected_idx - 1]
        ship_id = target_ship.get('ship_id')
        if not ship_id:
            print("Invalid ship ID.")
            return
        
        result = engine.execute({"type": "set_active_ship", "ship_id": ship_id})
        if _is_game_over_result(result):
            _print_game_over(result)
            _game_over_loop(engine, result)
            return
        if result.get("ok"):
            print(f"Active ship changed to {ship_id}.")
        else:
            error = result.get("error", "unknown_error")
            print(f"Failed to change active ship: {error}")
    except ValueError:
        print("Invalid input.")


def _install_module(engine: GameEngine) -> None:
    """Install module submenu (stub - requires shipdock integration)."""
    print("\nInstall Module:")
    print("This feature requires shipdock location access.")
    print("Please visit a shipdock to install modules.")
    input("Press Enter to continue...")


def _uninstall_module(engine: GameEngine) -> None:
    """Uninstall module submenu (stub - requires shipdock integration)."""
    print("\nUninstall Module:")
    print("This feature requires shipdock location access.")
    print("Please visit a shipdock to uninstall modules.")
    input("Press Enter to continue...")


def _transfer_cargo(engine: GameEngine) -> None:
    """Transfer cargo between ships submenu."""
    owned_ships = engine.get_owned_ships()
    active_ship = engine.get_active_ship()
    current_destination = engine.player_state.current_destination_id
    
    if not active_ship:
        print("No active ship.")
        return
    
    # Find ships at same destination
    same_dest_ships = [s for s in owned_ships if s.get('destination_id') == current_destination and s.get('ship_id') != active_ship.get('ship_id')]
    if not same_dest_ships:
        print("No other ships at current destination.")
        return
    
    print("\nShips at current destination:")
    for idx, ship in enumerate(same_dest_ships, start=1):
        print(f"  {idx}) {ship.get('ship_id', 'N/A')} - {ship.get('hull_id', 'N/A')}")
    
    try:
        raw = input("\nSelect target ship index [0 cancel]: ").strip()
        if raw == "0":
            return
        target_idx = int(raw)
        if target_idx < 1 or target_idx > len(same_dest_ships):
            print("Invalid selection.")
            return
        target_ship = same_dest_ships[target_idx - 1]
        target_ship_id = target_ship.get('ship_id')
        if not target_ship_id:
            print("Invalid ship ID.")
            return
        
        # List cargo on active ship
        source_cargo = engine.get_ship_cargo(active_ship.get('ship_id', ''))
        if not source_cargo:
            print("No cargo to transfer.")
            return
        
        cargo_list = sorted(source_cargo.items())
        print("\nAvailable cargo:")
        for idx, (sku, qty) in enumerate(cargo_list, start=1):
            print(f"  {idx}) {sku}: {qty}")
        
        raw_sku = input("\nSelect cargo SKU [0 cancel]: ").strip()
        if raw_sku == "0":
            return
        try:
            sku_idx = int(raw_sku)
            if sku_idx < 1 or sku_idx > len(cargo_list):
                print("Invalid selection.")
                return
            sku_id, available_qty = cargo_list[sku_idx - 1]
        except ValueError:
            sku_id = raw_sku
            available_qty = source_cargo.get(sku_id, 0)
            if available_qty == 0:
                print("Cargo not found.")
                return
        
        raw_qty = input(f"Quantity to transfer (max {available_qty}) [0 cancel]: ").strip()
        if raw_qty == "0":
            return
        try:
            qty = int(raw_qty)
            if qty < 1 or qty > available_qty:
                print("Invalid quantity.")
                return
        except ValueError:
            print("Invalid quantity.")
            return
        
        result = engine.execute({
            "type": "transfer_cargo",
            "source_ship_id": active_ship.get('ship_id'),
            "target_ship_id": target_ship_id,
            "sku": sku_id,
            "quantity": qty,
        })
        if _is_game_over_result(result):
            _print_game_over(result)
            _game_over_loop(engine, result)
            return
        if result.get("ok"):
            print(f"Transferred {qty} units of {sku_id}.")
        else:
            error = result.get("error", "unknown_error")
            print(f"Failed to transfer cargo: {error}")
    except ValueError:
        print("Invalid input.")


def _show_financial(engine: GameEngine) -> None:
    """Financial submenu."""
    result = engine.execute({"type": "get_player_profile"})
    detail = _extract_detail_from_stage(step_result=result, stage="player_profile")
    if not isinstance(detail, dict):
        print("Error: Could not retrieve player profile.")
        return
    
    print("\n=== FINANCIAL ===")
    print(f"\nCREDITS: {detail.get('credits', 0)}")
    
    # Warehouse rentals
    warehouses = engine.get_warehouse_rentals()
    print("\nWAREHOUSE RENTALS:")
    if not warehouses:
        print("  None")
    else:
        for idx, rental in enumerate(warehouses, start=1):
            destination_id = rental.get("destination_id", "N/A")
            capacity = rental.get("capacity", 0)
            cost = rental.get("cost_per_turn", 0)
            expiration = rental.get("expiration_day", "N/A")
            print(f"  {idx}) Location: {destination_id}, Capacity: {capacity}, Cost/turn: {cost}, Expiration: {expiration}")
    
    # Insurance stub
    print("\nINSURANCE:")
    insurance_policies = detail.get("insurance_policies", [])
    if not insurance_policies:
        print("  None")
    else:
        for idx, policy in enumerate(insurance_policies, start=1):
            print(f"  {idx}) {policy}")
    
    # Submenu options
    while True:
        print("\nOptions:")
        print("0) Back")
        print("1) Cancel Warehouse Rental")
        print("2) Cancel Insurance")
        choice = input("Select: ").strip()
        
        if choice == "0":
            return
        elif choice == "1":
            _cancel_warehouse_rental(engine)
            break
        elif choice == "2":
            print("\nCancel Insurance: Not yet implemented.")
            input("Press Enter to continue...")
            break
        else:
            print("Invalid selection.")


def _cancel_warehouse_rental(engine: GameEngine) -> None:
    """Cancel warehouse rental submenu."""
    warehouses = engine.get_warehouse_rentals()
    if not warehouses:
        print("No warehouse rentals to cancel.")
        return
    
    print("\nWarehouse Rentals:")
    for idx, rental in enumerate(warehouses, start=1):
        destination_id = rental.get("destination_id", "N/A")
        capacity = rental.get("capacity", 0)
        cost = rental.get("cost_per_turn", 0)
        print(f"  {idx}) {destination_id} - Capacity: {capacity}, Cost/turn: {cost}")
    
    try:
        raw = input("\nSelect rental index to cancel [0 cancel]: ").strip()
        if raw == "0":
            return
        selected = int(raw)
        if selected < 1 or selected > len(warehouses):
            print("Invalid selection.")
            return
        rental = warehouses[selected - 1]
        destination_id = rental.get("destination_id")
        if not destination_id:
            print("Invalid destination ID.")
            return
        
        result = engine.execute({"type": "warehouse_cancel", "destination_id": destination_id})
        if _is_game_over_result(result):
            _print_game_over(result)
            _game_over_loop(engine, result)
            return
        if result.get("ok"):
            print(f"Warehouse rental at {destination_id} cancelled.")
        else:
            error = result.get("error", "unknown_error")
            print(f"Failed to cancel warehouse rental: {error}")
    except ValueError:
        print("Invalid input.")


def _show_missions(engine: GameEngine) -> None:
    """Missions submenu with detailed mission information."""
    active_missions = engine.get_active_missions()
    claimable_missions = engine.get_claimable_missions()
    
    print("\n=== MISSIONS ===")
    
    print("\nACTIVE MISSIONS:")
    if not active_missions:
        print("  None")
    else:
        for idx, mission in enumerate(active_missions, start=1):
            mission_id = mission.get("mission_id", "N/A")
            mission_type = mission.get("mission_type", "N/A")
            mission_tier = mission.get("mission_tier", 0)
            
            # Source information
            source_type = mission.get("source_type", "N/A")
            source_id = mission.get("source_id", "N/A")
            if source_type and source_type != "N/A":
                source_display = f"{source_type}"
                if source_id and source_id != "N/A":
                    source_display += f" ({source_id})"
            else:
                source_display = "N/A"
            
            # Target information
            target_destination_id = mission.get("target_destination_id")
            target_system_id = mission.get("target_system_id", "N/A")
            if target_destination_id:
                target_display = f"{target_destination_id}"
                if target_system_id and target_system_id != "N/A":
                    target_display += f" in {target_system_id}"
            elif target_system_id and target_system_id != "N/A":
                target_display = target_system_id
            else:
                target_display = "N/A"
            
            # Rewards
            reward_summary = mission.get("reward_summary", [])
            reward_text = "None"
            if reward_summary:
                reward_parts = []
                for reward in reward_summary:
                    field = reward.get("field", "")
                    delta = reward.get("delta", 0)
                    if field == "credits":
                        reward_parts.append(f"{delta:+d} credits")
                if reward_parts:
                    reward_text = ", ".join(reward_parts)
            
            # Collection format
            collection_format = mission.get("collection_format", "Auto")
            
            print(f"\n  Mission {idx}: {mission_id}")
            print(f"    Type: {mission_type} (Tier {mission_tier})")
            print(f"    Source: {source_display}")
            print(f"    Target: {target_display}")
            print(f"    Rewards: {reward_text}")
            print(f"    Collection: {collection_format}")
    
    # Submenu options
    while True:
        print("\nOptions:")
        print("0) Back")
        print("1) Abandon Mission")
        # Phase 7.11.2b - Only show claim option if there are claimable missions
        if claimable_missions:
            print("2) Claim Mission Reward")
        choice = input("Select: ").strip()
        
        if choice == "0":
            return
        elif choice == "1":
            _abandon_mission(engine)
            break
        elif choice == "2" and claimable_missions:
            _claim_mission_reward(engine)
            break
        else:
            print("Invalid selection.")


def _abandon_mission(engine: GameEngine) -> None:
    """Abandon mission submenu."""
    active_missions = engine.get_active_missions()
    if not active_missions:
        print("No active missions to abandon.")
        return
    
    print("\nActive Missions:")
    for idx, mission in enumerate(active_missions, start=1):
        mission_id = mission.get("mission_id", "N/A")
        title = mission.get("title", mission.get("mission_type", "N/A"))
        print(f"  {idx}) {mission_id}: {title}")
    
    try:
        raw = input("\nSelect mission index to abandon [0 cancel]: ").strip()
        if raw == "0":
            return
        selected = int(raw)
        if selected < 1 or selected > len(active_missions):
            print("Invalid selection.")
            return
        mission = active_missions[selected - 1]
        mission_id = mission.get("mission_id")
        if not mission_id:
            print("Invalid mission ID.")
            return
        
        result = engine.execute({"type": "abandon_mission", "mission_id": mission_id})
        if _is_game_over_result(result):
            _print_game_over(result)
            _game_over_loop(engine, result)
            return
        if result.get("ok"):
            print(f"Mission {mission_id} abandoned.")
        else:
            error = result.get("error", "unknown_error")
            print(f"Failed to abandon mission: {error}")
    except ValueError:
        print("Invalid input.")


def _format_reward_summary(reward_summary: object) -> str:
    """Format reward_summary consistently for all mission displays (Phase 7.x).

    Expected input:
      reward_summary: list[dict] with entries like {"field": "credits", "delta": int}

    Output:
      "+4800 credits" / "+1000 credits" / "No rewards"
    """
    if not isinstance(reward_summary, list) or not reward_summary:
        return "No rewards"

    parts: list[str] = []
    for reward in reward_summary:
        if not isinstance(reward, dict):
            continue
        field = reward.get("field", "")
        delta = reward.get("delta", 0)
        if field == "credits":
            parts.append(f"{delta:+d} credits")
        else:
            parts.append(f"{field}: {delta}")

    return ", ".join(parts) if parts else "No rewards"


def _claim_mission_reward(engine: GameEngine) -> None:
    """Claim mission reward submenu."""
    claimable_missions = engine.get_claimable_missions()
    if not claimable_missions:
        print("No claimable mission rewards.")
        return
    
    print("\nClaimable Missions:")
    for idx, mission in enumerate(claimable_missions, start=1):
        mission_id = mission.get("mission_id", "N/A")
        title = mission.get("title", mission.get("mission_type", "N/A"))
        print(f"  {idx}) {mission_id}: {title}")
    
    try:
        raw = input("\nSelect mission index to claim [0 cancel]: ").strip()
        if raw == "0":
            return
        selected = int(raw)
        if selected < 1 or selected > len(claimable_missions):
            print("Invalid selection.")
            return
        mission = claimable_missions[selected - 1]
        mission_id = mission.get("mission_id")
        if not mission_id:
            print("Invalid mission ID.")
            return
        
        result = engine.execute({"type": "claim_mission", "mission_id": mission_id})
        if _is_game_over_result(result):
            _print_game_over(result)
            _game_over_loop(engine, result)
            return
        if result.get("ok"):
            print(f"Mission {mission_id} reward claimed.")
        else:
            error = result.get("error", "unknown_error")
            print(f"Failed to claim mission reward: {error}")
    except ValueError:
        print("Invalid input.")


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
    if raw_selection == "0":
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
    if _is_game_over_result(result):
        _print_game_over(result)
        _game_over_loop(engine, result)
        return
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
    if _is_game_over_result(result):
        _print_game_over(result)
        _game_over_loop(engine, result)
        return
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
    if _is_game_over_result(result):
        _print_game_over(result)
        _game_over_loop(engine, result)
        return
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


def _resolve_pending_encounter(engine: GameEngine) -> None:
    """
    Handle a pending encounter decision. Forces player to resolve the encounter
    before returning. This function loops until the encounter is resolved.
    """
    while engine.has_pending_encounter():
        pending_info = engine.get_pending_encounter_info()
        if not pending_info:
            break
        
        print("\n--- ENCOUNTER ---")
        
        # Display encounter description
        encounter_description = pending_info.get("encounter_description")
        if encounter_description:
            print(f"Encounter: {encounter_description}")
        
        # Display NPC ship info if available (hull name only for encounters)
        npc_ship_info = pending_info.get("npc_ship_info")
        if npc_ship_info:
            hull_name = npc_ship_info.get("hull_name", "Unknown")
            # Display: Ship Hull Name only - e.g., "Mosquito", "Wasp"
            print(f"NPC Ship: {hull_name}")
        
        print()  # Blank line before options
        
        options = pending_info.get("options", [])
        if not options:
            print("No encounter options available.")
            break
        
        # Display numbered options
        for idx, opt in enumerate(options, start=1):
            label = opt.get("label", "Unknown")
            print(f"{idx}) {label}")
        
        choice = input("Select option: ").strip()
        decision_id = None
        
        # Try to match by number first
        try:
            choice_num = int(choice)
            if 1 <= choice_num <= len(options):
                decision_id = options[choice_num - 1].get("id")
        except ValueError:
            # Try to match by id or label
            for opt in options:
                if str(opt.get("id", "")) == choice or str(opt.get("label", "")).lower() == choice.lower():
                    decision_id = opt.get("id")
                    break
        
        if decision_id:
            result = engine.execute({
                "type": "encounter_decision",
                "encounter_id": pending_info.get("encounter_id"),
                "decision_id": decision_id,
            })
            
            # Check for game over
            if _is_game_over_result(result):
                _print_game_over(result)
                _game_over_loop(engine, result)
                return
            
            # Immediate loot handling: if loot is pending, handle it before continuing
            if result.get("hard_stop") is True and result.get("hard_stop_reason") == "pending_loot_decision":
                pending_loot = engine.get_pending_loot()
                if pending_loot:
                    _handle_pending_loot(engine, pending_loot)
                    # After loot is resolved, check if we should continue to next encounter
                    # The engine will have set up the next encounter if any remain
                    continue
            
            # Check if result has another hard_stop (e.g., combat initiated)
            if result.get("hard_stop") is True:
                hard_stop_reason = result.get("hard_stop_reason")
                if hard_stop_reason == "pending_combat_action":
                    # Combat was initiated, resolve it
                    _resolve_pending_combat(engine)
                # Continue loop to check for next encounter
                continue
        else:
            print("Invalid selection. Please try again.")
            # Continue loop to force player to resolve encounter
            continue


def _resolve_pending_combat(engine: GameEngine) -> None:
    """
    Handle a pending combat action. Forces player to resolve combat
    before returning. This function loops until combat is resolved.
    """
    current_combat_seed_printed = False
    last_combat_seed = None
    
    while engine.has_pending_combat():
        pending_info = engine.get_pending_combat_info()
        if not pending_info:
            break
        
        # Safety check: detect invalid combat state
        invalid_state = pending_info.get("invalid_state", False)
        if invalid_state:
            error_msg = pending_info.get("error", "Unknown error")
            player_hull_max = pending_info.get("player_hull_max", 0)
            enemy_hull_max = pending_info.get("enemy_hull_max", 0)
            print("\n=== FATAL: INVALID COMBAT STATE ===")
            print(f"Error: {error_msg}")
            print(f"Player hull_max: {player_hull_max}")
            print(f"Enemy hull_max: {enemy_hull_max}")
            print("Combat cannot proceed. Breaking out of combat loop.")
            break
        
        # Safety check: detect 0% hull at round 1 (indicates initialization failure)
        round_number = pending_info.get("round_number", 1)
        if round_number < 1:
            round_number = 1
        player_hull_pct = pending_info.get("player_hull_pct", 0)
        enemy_hull_pct = pending_info.get("enemy_hull_pct", 0)
        if round_number == 1 and player_hull_pct == 0 and enemy_hull_pct == 0:
            player_hull_max = pending_info.get("player_hull_max", 0)
            enemy_hull_max = pending_info.get("enemy_hull_max", 0)
            print("\n=== FATAL: COMBAT INITIALIZATION FAILURE ===")
            print("Both player and enemy hull are at 0% at round 1.")
            print(f"Player hull_max: {player_hull_max}")
            print(f"Enemy hull_max: {enemy_hull_max}")
            print("This indicates invalid hull_id or assembly failure.")
            print("Combat cannot proceed. Breaking out of combat loop.")
            break
        
        allowed_actions = pending_info.get("allowed_actions", [])
        if not allowed_actions:
            print("No combat actions available.")
            break
        
        # Check for combat_rng_seed in pending_info or result (combat start detection)
        combat_seed = pending_info.get("combat_rng_seed")
        if combat_seed is not None and not current_combat_seed_printed:
            print("\n=== COMBAT START ===")
            print(f"combat_rng_seed: {combat_seed}")
            current_combat_seed_printed = True
            last_combat_seed = combat_seed
        
        # Extract labels from engine-provided allowed_actions (contract-correct)
        action_labels = [opt.get("label", "") for opt in allowed_actions]
        action_ids = [opt.get("id", "") for opt in allowed_actions]
        
        # Display menu using engine-provided labels (no hardcoding)
        action_label = _combat_action_menu(
            round_number=round_number,
            player_hull_pct=pending_info.get("player_hull_pct", 0),
            enemy_hull_pct=pending_info.get("enemy_hull_pct", 0),
            allowed_actions=action_labels,
            encounter_description=pending_info.get("encounter_description"),
            enemy_ship_info=pending_info.get("enemy_ship_info"),
        )
        
        # Map selected label back to action_id from engine payload
        action_id = None
        for idx, label in enumerate(action_labels):
            if label == action_label:
                action_id = action_ids[idx] if idx < len(action_ids) else None
                break
        
        if action_id:
            result = engine.execute({
                "type": "combat_action",
                "action": action_id,
                "encounter_id": pending_info.get("encounter_id"),
            })
            
            # Check for game over
            if _is_game_over_result(result):
                _print_game_over(result)
                _game_over_loop(engine, result)
                return
            
            # Check for engine errors and surface them
            if result.get("ok") is False:
                error_msg = result.get("error", "Unknown error")
                print(f"\n=== ERROR: Combat action failed ===")
                print(f"Error: {error_msg}")
                print("Breaking out of combat loop.")
                break
            
            # Immediate loot handling: if loot is pending, handle it before continuing
            if result.get("hard_stop") is True and result.get("hard_stop_reason") == "pending_loot_decision":
                pending_loot = engine.get_pending_loot()
                if pending_loot:
                    _handle_pending_loot(engine, pending_loot)
                    # After loot is resolved, check if combat continues or if we should break
                    # The engine will have set up the next encounter if any remain
                    if not engine.has_pending_combat():
                        # Combat ended and loot resolved - break out of combat loop
                        current_combat_seed_printed = False
                        break
                    # Combat may continue (shouldn't happen after loot, but handle gracefully)
                    continue
            
            # Safety check: detect if round_number did not advance (infinite loop prevention)
            if result.get("hard_stop") is True:
                next_pending = result.get("pending_combat")
                if next_pending:
                    next_round = next_pending.get("round_number", 0)
                    if next_round == round_number:
                        print("\n=== WARNING: COMBAT ROUND NOT ADVANCING ===")
                        print(f"Round number did not advance after action. Current: {round_number}, Next: {next_round}")
                        print("This may indicate an infinite loop. Breaking out of combat loop.")
                        print(f"Pending combat payload: {json.dumps(next_pending, sort_keys=True)}")
                        break
            
            # Check for combat_rng_seed in result (alternative detection path)
            result_seed = result.get("combat_rng_seed")
            if result_seed is not None and not current_combat_seed_printed:
                print("\n=== COMBAT START ===")
                print(f"combat_rng_seed: {result_seed}")
                current_combat_seed_printed = True
                last_combat_seed = result_seed
            
            # Check if combat ended
            if result.get("combat_ended") is True:
                # Combat ended - reset flags and break
                current_combat_seed_printed = False
                
                # Display combat result summary if available
                combat_result = result.get("combat_result")
                if combat_result:
                    outcome = combat_result.get("outcome", "unknown")
                    winner = combat_result.get("winner", "none")
                    rounds = combat_result.get("rounds", 0)
                    combat_rng_seed_final = combat_result.get("combat_rng_seed")
                    
                    print(f"\n--- COMBAT ENDED ---")
                    print(f"Outcome: {outcome}")
                    if winner != "none":
                        print(f"Winner: {winner}")
                    print(f"Rounds: {rounds}")
                    if combat_rng_seed_final is not None:
                        print(f"combat_rng_seed: {combat_rng_seed_final}")
                    
                    # Update last_combat_seed if available
                    if combat_rng_seed_final is not None:
                        last_combat_seed = combat_rng_seed_final
                
                # Offer replay
                if last_combat_seed is not None:
                    replay_choice = input("\nType R to replay last combat, or press Enter to continue: ").strip()
                    if replay_choice.upper() == "R":
                        # Replay: Note that full replay requires engine support for combat_rng_seed injection
                        # Since we cannot modify engine, we inform user of the seed for manual replay
                        print(f"Replay seed: {last_combat_seed}")
                        print("Note: Full replay requires engine support for combat_rng_seed injection.")
                        print("Combat inputs were not stored (engine-managed).")
                
                # Check if encounter decision needed
                if result.get("hard_stop") is True:
                    hard_stop_reason = result.get("hard_stop_reason")
                    if hard_stop_reason == "pending_encounter_decision":
                        _resolve_pending_encounter(engine)
                break
            
            # Check if result has another hard_stop (combat continues)
            if result.get("hard_stop") is True:
                hard_stop_reason = result.get("hard_stop_reason")
                if hard_stop_reason == "pending_encounter_decision":
                    # Combat ended, but encounter decision needed
                    _resolve_pending_encounter(engine)
                # Continue loop to check for next combat round
                continue
        else:
            print("Invalid action selection. Please try again.")
            # Continue loop to force player to resolve combat
            continue


def _handle_pending_loot(engine: GameEngine, loot_bundle: dict) -> None:
    """
    Handle pending loot prompt and application.
    
    Prompts player to accept or decline loot, then calls resolve_pending_loot.
    """
    # Get ship info for capacity display
    ship_info_result = engine.execute({"type": "get_player_profile"})
    if _is_game_over_result(ship_info_result):
        return
    ship_detail = _extract_detail_from_stage(step_result=ship_info_result, stage="player_profile")
    if not isinstance(ship_detail, dict):
        return
    
    physical_capacity = ship_detail.get("effective_physical_cargo_capacity", 0)
    data_capacity = ship_detail.get("effective_data_cargo_capacity", 0)
    current_cargo = ship_detail.get("cargo_manifest", {})
    
    # Calculate current cargo usage
    current_physical = 0
    current_data = 0
    for sku, qty in current_cargo.items():
        # Simple heuristic: check if SKU name suggests data (minimal, can be improved)
        # For now, assume all cargo is physical unless we have catalog access
        current_physical += int(qty)
    
    # Extract loot details
    credits = loot_bundle.get("credits", 0)
    cargo_sku = loot_bundle.get("cargo_sku")
    cargo_quantity = loot_bundle.get("cargo_quantity", 0)
    salvage_modules = loot_bundle.get("salvage_modules", [])
    salvage_count = len(salvage_modules)
    
    # Check if there's actually loot to offer
    has_loot = credits > 0 or (cargo_sku and cargo_quantity > 0) or salvage_count > 0
    
    if not has_loot:
        # No loot, clear and return
        engine.clear_pending_loot()
        return
    
    print("\n=== LOOT RECOVERED ===")
    if credits > 0:
        print(f"Credits: {credits}")
    if cargo_sku and cargo_quantity > 0:
        print(f"Cargo: {cargo_sku} x{cargo_quantity}")
    if salvage_count > 0:
        print(f"Salvage modules: {salvage_count}")
    print("----------------------")
    print("1) Take All")
    print("2) Leave Everything")
    
    choice = input("Select: ").strip()
    
    if choice == "1":
        # Accept all loot
        result = engine.resolve_pending_loot(take_all=True)
        if result.get("ok"):
            print("\nLoot applied successfully.")
            # Check if encounters should resume
            if result.get("resume_encounters"):
                # Engine will have pending encounter, CLI loop will handle it
                return
        else:
            error = result.get("error", "unknown")
            print(f"\nWARNING: Could not apply loot: {error}")
    else:
        # Decline all loot
        result = engine.resolve_pending_loot(take_all=False)
        if result.get("ok"):
            print("\nLoot declined.")
            # Check if encounters should resume
            if result.get("resume_encounters"):
                # Engine will have pending encounter, CLI loop will handle it
                return
        else:
            error = result.get("error", "unknown")
            print(f"\nWARNING: Could not clear loot: {error}")


def _travel_menu(engine: GameEngine) -> None:
    current_system_id = engine.player_state.current_system_id
    current_system = engine.sector.get_system(current_system_id)
    if current_system is None:
        print(json.dumps({"ok": False, "error": "current_system_not_found"}, sort_keys=True))
        return
    active_ship = engine.fleet_by_id.get(engine.player_state.active_ship_id)
    current_fuel = int(getattr(active_ship, "current_fuel", 0) or 0)

    while True:
        # Get current destination info
        current_destination = engine._current_destination()
        current_destination_id = engine.player_state.current_destination_id
        current_destination_name = current_destination.display_name if current_destination else "Unknown"
        
        print(f"Current system: {current_system.system_id} ({current_system.name})")
        print(f"Current destination: {current_destination_id or 'None'} ({current_destination_name})")
        print("0) Back")
        print("1) Inter-system warp")
        print("2) Intra-system destination travel")
        mode = input("Travel mode: ").strip()

        if mode == "0":
            return
        elif mode == "1":
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
            
            # Check for game over
            if _is_game_over_result(result):
                _print_game_over(result)
                _game_over_loop(engine, result)
                return
            
            # Handle hard_stop responses (pending encounters or combat)
            # Per interaction_layer_contract.md: all encounters must be resolved before travel continues
            hard_stop_iterations = 0
            while result.get("hard_stop") is True:
                hard_stop_iterations += 1
                if hard_stop_iterations > 100:
                    print("ERROR: Hard stop loop exceeded safe iteration limit.")
                    break
                
                # Check if combat ended - break immediately
                if result.get("combat_ended") is True:
                    break
                
                hard_stop_reason = result.get("hard_stop_reason")
                
                # Handle pending encounter decision - MUST resolve before continuing
                if hard_stop_reason == "pending_encounter_decision":
                    pending_encounter = result.get("pending_encounter")
                    if pending_encounter:
                        print("\n--- ENCOUNTER ---")
                        options = pending_encounter.get("options", [])
                        if not options:
                            print("No encounter options available.")
                            break
                        # Display numbered options
                        for idx, opt in enumerate(options, start=1):
                            label = opt.get("label", "Unknown")
                            print(f"{idx}) {label}")
                        choice = input("Select option: ").strip()
                        decision_id = None
                        # Try to match by number first
                        try:
                            choice_num = int(choice)
                            if 1 <= choice_num <= len(options):
                                decision_id = options[choice_num - 1].get("id")
                        except ValueError:
                            # Try to match by id or label
                            for opt in options:
                                if str(opt.get("id", "")) == choice or str(opt.get("label", "")).lower() == choice.lower():
                                    decision_id = opt.get("id")
                                    break
                        if decision_id:
                            result = engine.execute({
                                "type": "encounter_decision",
                                "encounter_id": pending_encounter.get("encounter_id"),
                                "decision_id": decision_id,
                            })
                            # Continue loop to check for next hard_stop (may be another encounter or combat)
                            continue
                        else:
                            print("Invalid selection. Please try again.")
                            # Don't return - force player to resolve encounter
                            continue
                    else:
                        # No pending_encounter payload - break to avoid infinite loop
                        break
                
                # Handle pending combat action - MUST resolve before continuing
                elif hard_stop_reason == "pending_combat_action":
                    # Defensive guard: do not prompt if combat already ended
                    if result.get("combat_ended") is True:
                        break
                    
                    pending_combat = result.get("pending_combat")
                    if pending_combat:
                        allowed_actions = pending_combat.get("allowed_actions", [])
                        if not allowed_actions:
                            print("No combat actions available.")
                            break
                        
                        # Get round number (enforce 1-indexed, no round 0)
                        round_number = pending_combat.get("round_number", 1)
                        if round_number < 1:
                            round_number = 1
                        
                        # Extract labels from engine-provided allowed_actions (contract-correct)
                        action_labels = [opt.get("label", "") for opt in allowed_actions]
                        action_ids = [opt.get("id", "") for opt in allowed_actions]
                        
                        # Display menu using engine-provided labels (no hardcoding)
                        action_label = _combat_action_menu(
                            round_number=round_number,
                            player_hull_pct=pending_combat.get("player_hull_pct", 0),
                            enemy_hull_pct=pending_combat.get("enemy_hull_pct", 0),
                            allowed_actions=action_labels,
                        )
                        
                        # Map selected label back to action_id from engine payload
                        action_id = None
                        for idx, label in enumerate(action_labels):
                            if label == action_label:
                                action_id = action_ids[idx] if idx < len(action_ids) else None
                                break
                        
                        if action_id:
                            result = engine.execute({
                                "type": "combat_action",
                                "action": action_id,
                                "encounter_id": pending_combat.get("encounter_id"),
                            })
                            
                            # Check for game over
                            if _is_game_over_result(result):
                                _print_game_over(result)
                                _game_over_loop(engine, result)
                                return
                            
                            # Check for engine errors and surface them
                            if result.get("ok") is False:
                                error_msg = result.get("error", "Unknown error")
                                print(f"\n=== ERROR: Combat action failed ===")
                                print(f"Error: {error_msg}")
                                print("Breaking out of combat loop.")
                                break
                            
                            # Check if combat ended - break immediately
                            if result.get("combat_ended") is True:
                                break
                            
                            # Continue loop to check for next hard_stop (combat may continue or end)
                            continue
                        else:
                            print("Invalid action selection. Please try again.")
                            # Don't return - force player to resolve combat
                            continue
                    else:
                        # No pending_combat payload - break to avoid infinite loop
                        break
                else:
                    # Unknown hard_stop_reason - break to avoid infinite loop
                    break
            
            print(json.dumps(result, sort_keys=True))
            if result.get("ok") is True and result.get("player", {}).get("system_id") == target_system.system_id:
                print(f"You have arrived in {target_system.name}.")
                _print_current_system_destinations(engine)
            return
        elif mode == "2":
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
            result = engine.execute(payload)
            
            # Check for game over
            if _is_game_over_result(result):
                _print_game_over(result)
                _game_over_loop(engine, result)
                return
            
            # Handle hard_stop responses (pending encounters or combat)
            # Per interaction_layer_contract.md: all encounters must be resolved before travel continues
            hard_stop_iterations = 0
            while result.get("hard_stop") is True:
                hard_stop_iterations += 1
                if hard_stop_iterations > 100:
                    print("ERROR: Hard stop loop exceeded safe iteration limit.")
                    break
                
                # Check if combat ended - break immediately
                if result.get("combat_ended") is True:
                    break
                
                hard_stop_reason = result.get("hard_stop_reason")
                
                # Handle pending encounter decision - MUST resolve before continuing
                if hard_stop_reason == "pending_encounter_decision":
                    pending_encounter = result.get("pending_encounter")
                    if pending_encounter:
                        print("\n--- ENCOUNTER ---")
                        options = pending_encounter.get("options", [])
                        if not options:
                            print("No encounter options available.")
                            break
                        # Display numbered options
                        for idx, opt in enumerate(options, start=1):
                            label = opt.get("label", "Unknown")
                            print(f"{idx}) {label}")
                        choice = input("Select option: ").strip()
                        decision_id = None
                        # Try to match by number first
                        try:
                            choice_num = int(choice)
                            if 1 <= choice_num <= len(options):
                                decision_id = options[choice_num - 1].get("id")
                        except ValueError:
                            # Try to match by id or label
                            for opt in options:
                                if str(opt.get("id", "")) == choice or str(opt.get("label", "")).lower() == choice.lower():
                                    decision_id = opt.get("id")
                                    break
                        if decision_id:
                            result = engine.execute({
                                "type": "encounter_decision",
                                "encounter_id": pending_encounter.get("encounter_id"),
                                "decision_id": decision_id,
                            })
                            # Check for game over
                            if _is_game_over_result(result):
                                _print_game_over(result)
                                _game_over_loop(engine, result)
                                return
                            # Continue loop to check for next hard_stop (may be another encounter or combat)
                            continue
                        else:
                            print("Invalid selection. Please try again.")
                            # Don't return - force player to resolve encounter
                            continue
                    else:
                        # No pending_encounter payload - break to avoid infinite loop
                        break
                
                # Handle pending combat action - MUST resolve before continuing
                elif hard_stop_reason == "pending_combat_action":
                    # Defensive guard: do not prompt if combat already ended
                    if result.get("combat_ended") is True:
                        break
                    
                    pending_combat = result.get("pending_combat")
                    if pending_combat:
                        allowed_actions = pending_combat.get("allowed_actions", [])
                        if not allowed_actions:
                            print("No combat actions available.")
                            break
                        
                        # Get round number (enforce 1-indexed, no round 0)
                        round_number = pending_combat.get("round_number", 1)
                        if round_number < 1:
                            round_number = 1
                        
                        # Extract labels from engine-provided allowed_actions (contract-correct)
                        action_labels = [opt.get("label", "") for opt in allowed_actions]
                        action_ids = [opt.get("id", "") for opt in allowed_actions]
                        
                        # Display menu using engine-provided labels (no hardcoding)
                        action_label = _combat_action_menu(
                            round_number=round_number,
                            player_hull_pct=pending_combat.get("player_hull_pct", 0),
                            enemy_hull_pct=pending_combat.get("enemy_hull_pct", 0),
                            allowed_actions=action_labels,
                        )
                        
                        # Map selected label back to action_id from engine payload
                        action_id = None
                        for idx, label in enumerate(action_labels):
                            if label == action_label:
                                action_id = action_ids[idx] if idx < len(action_ids) else None
                                break
                        
                        if action_id:
                            result = engine.execute({
                                "type": "combat_action",
                                "action": action_id,
                                "encounter_id": pending_combat.get("encounter_id"),
                            })
                            
                            # Check for game over
                            if _is_game_over_result(result):
                                _print_game_over(result)
                                _game_over_loop(engine, result)
                                return
                            
                            # Check for engine errors and surface them
                            if result.get("ok") is False:
                                error_msg = result.get("error", "Unknown error")
                                print(f"\n=== ERROR: Combat action failed ===")
                                print(f"Error: {error_msg}")
                                print("Breaking out of combat loop.")
                                break
                            
                            # Check if combat ended - break immediately
                            if result.get("combat_ended") is True:
                                break
                            
                            # Continue loop to check for next hard_stop (combat may continue or end)
                            continue
                        else:
                            print("Invalid action selection. Please try again.")
                            # Don't return - force player to resolve combat
                            continue
                    else:
                        # No pending_combat payload - break to avoid infinite loop
                        break
                else:
                    # Unknown hard_stop_reason - break to avoid infinite loop
                    break
            
            print(json.dumps(result, sort_keys=True))
            return
        else:
            print("Invalid selection.")
            continue


def _wait_menu(engine: GameEngine) -> None:
    raw = input("Days to wait (1..10): ").strip()
    try:
        days = int(raw)
    except ValueError:
        days = 1
    result = engine.execute({"type": "wait", "days": days})
    if _is_game_over_result(result):
        _print_game_over(result)
        _game_over_loop(engine, result)
        return
    print(json.dumps(result, sort_keys=True))


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
        if _is_game_over_result(result):
            _print_game_over(result)
            _game_over_loop(engine, result)
            return
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
                        reward_text = _format_reward_summary(mission.get("reward_summary", []))
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
                            reward_summary = result_data.get("reward_summary", [])
                            status = result_data.get("status")
                            text = result_data.get("text")
                            offer_only = result_data.get("offer_only", False)
                            
                            print(f"\nMISSION DETAILS")
                            print(f"  Type: {mission_type}")
                            print(f"  Tier: {mission_tier}")
                            reward_text = _format_reward_summary(reward_summary)
                            print(f"  Rewards: {reward_text}")
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
                reward_summary = interaction_result.get("reward_summary", [])
                reward_text = _format_reward_summary(reward_summary)
                print("MISSION OFFER")
                print(f"  Mission ID: {mission_id}")
                print(f"  Type: {mission_type}")
                print(f"  Tier: {mission_tier}")
                print(f"  Rewards: {reward_text}")
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
                        reward_text = _format_reward_summary(mission.get("reward_summary", []))
                        print(f"  Rewards: {reward_text}")
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
            # Refresh: clear DataNet offers for this location only
            current_location_id = engine.player_state.current_location_id
            if isinstance(current_location_id, str) and current_location_id:
                engine._mission_manager.clear_datanet_offers(location_id=current_location_id)
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
    starting_ship_override = _prompt_admin_override()
    engine = GameEngine(world_seed=seed, config={"system_count": 50}, starting_ship_override=starting_ship_override)
    log_path = str((Path(__file__).resolve().parents[1] / "logs" / f"gameplay_seed_{seed}.log"))
    _ = engine.execute({"type": "set_logging", "enabled": True, "log_path": log_path, "truncate": True})
    print(f"Logging to {log_path}")
    _configure_cli_test_fuel(engine)
    print(json.dumps({"event": "engine_init", "seed": seed}, sort_keys=True))
    # Display galaxy map at game start
    _render_galaxy_map(engine.sector)
    while True:
        # CRITICAL: Enforce hard-stop contract - check for pending encounters/combat BEFORE rendering menu
        # Per interaction_layer_contract.md and combat_resolution_contract.md, all encounters and combat
        # must be resolved before allowing menu navigation or travel.
        if engine.has_pending_encounter():
            _resolve_pending_encounter(engine)
            # After resolving encounter, continue loop (don't render menu yet in case combat was initiated)
            continue
        
        if engine.has_pending_combat():
            _resolve_pending_combat(engine)
            # After resolving combat, continue loop (don't render menu yet in case another encounter is pending)
            continue
        
        # Check for pending loot decision (after combat ends)
        pending_loot = engine.get_pending_loot()
        if pending_loot:
            _handle_pending_loot(engine, pending_loot)
            # After resolving loot, continue loop (don't render menu yet in case another encounter is pending)
            continue
        
        # Only render main menu if no pending encounters or combat
        # Display destination context block
        _print_destination_context(engine)
        print("1) Player / Ship Info")
        print("2) System Info")
        print("3) Travel")
        print("4) Destination Actions")
        print("5) Locations")
        print("6) Galaxy Summary")
        print("7) Quit")
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
            _galaxy_summary(engine)
        elif choice == "7":
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
    ctx = engine.get_current_destination_context()
    
    system_visited = ctx.get('system_government', '') != '' or ctx.get('primary_economy') is not None
    
    print("-" * 40)
    print(f"Destination: {ctx.get('destination_name', 'Unknown')} ({ctx.get('destination_type', 'unknown')})")
    print(f"System: {ctx.get('system_name', 'Unknown')}", end="")
    
    system_government = ctx.get('system_government', '')
    if system_government:
        print(f" ({system_government})")
    else:
        print()
    
    # Only show sensitive data if system is visited
    if system_visited:
        population = ctx.get('population', 0)
        if population > 0:
            print(f"Population: {population}")
        
        primary_economy = ctx.get('primary_economy')
        secondary_economies = ctx.get('secondary_economies', [])
        
        if primary_economy:
            economy_str = primary_economy
            if secondary_economies:
                economy_str += f" ({', '.join(secondary_economies)})"
            print(f"Economy: {economy_str}")
        
        # Separate system and destination situations
        system_id = ctx.get('system_id', '')
        destination_id = engine.player_state.current_destination_id
        
        # Get situation rows and separate by scope
        situation_rows = engine._active_situation_rows_for_system(system_id=system_id) if system_id else []
        system_situations = []
        destination_situations = []
        
        for row in situation_rows:
            situation_id = row.get('situation_id')
            scope = row.get('scope')
            target_id = row.get('target_id')
            
            if isinstance(situation_id, str) and situation_id:
                if scope == 'system':
                    system_situations.append(situation_id)
                elif scope == 'destination' and target_id == destination_id:
                    destination_situations.append(situation_id)
        
        system_situations = sorted(set(system_situations))
        destination_situations = sorted(set(destination_situations))
        
        if system_situations:
            print(f"System situations: {', '.join(system_situations)}")
        else:
            print("System situations: None")
        
        if destination_situations:
            print(f"Destination situations: {', '.join(destination_situations)}")
        else:
            print("Destination situations: None")
    
    print("-" * 40)


def _galaxy_summary(engine: GameEngine) -> None:
    """Print galaxy summary for debug visibility."""
    sector = engine.sector
    systems = sorted(sector.systems, key=lambda s: s.system_id)
    
    print("\n" + "=" * 60)
    print("GALAXY SUMMARY")
    print("=" * 60)
    print(f"Total systems: {len(systems)}\n")
    
    for system in systems:
        government = engine.government_registry.get_government(system.government_id)
        government_name = government.name if government else system.government_id
        
        print(f"System: {system.system_id} - {system.name}")
        print(f"  Government: {government_name}")
        print(f"  Population: {system.population}")
        print(f"  Destinations:")
        
        destinations = sorted(system.destinations, key=lambda d: d.destination_id)
        for dest in destinations:
            secondary_str = ", ".join(dest.secondary_economy_ids) if dest.secondary_economy_ids else "-"
            primary_str = dest.primary_economy_id if dest.primary_economy_id else "None"
            
            print(f"    {dest.destination_id} - {dest.display_name}")
            print(f"      Type: {dest.destination_type}")
            print(f"      Population: {dest.population}")
            print(f"      Primary Economy: {primary_str}")
            print(f"      Secondary Economies: {secondary_str}")
        print()
    
    print("=" * 60 + "\n")


def _destination_actions_menu(engine: GameEngine) -> None:
    # Display destination context before menu
    _print_destination_context(engine)
    
    while True:
        list_result = engine.execute({"type": "list_destination_actions"})
        actions = _extract_actions_from_stage(step_result=list_result, stage="destination_actions")
        if not actions:
            print("No destination actions available.")
            return
        print("0) Back")
        for index, action in enumerate(actions, start=1):
            print(f"{index}) {action['action_id']} {action.get('display_name')}")

        raw_index = input("Select destination action index: ").strip()
        try:
            selected = int(raw_index)
        except ValueError:
            print("Invalid destination action index.")
            continue
        if selected == 0:
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
    # Build base profile from system/destination for context only
    system_detail = _extract_detail_from_stage(
        step_result=engine.execute({"type": "get_system_profile"}),
        stage="system_profile",
    )
    destination_detail = _extract_detail_from_stage(
        step_result=engine.execute({"type": "get_destination_profile"}),
        stage="destination_profile",
    )
    # DataNet missions must be isolated from bar/admin missions.
    # Use a dedicated DataNet mission pool maintained by the engine/mission_manager.
    current_location_id = engine.player_state.current_location_id
    datanet_missions = []
    if isinstance(current_location_id, str) and current_location_id:
        datanet_missions = engine._datanet_mission_rows_for_location(location_id=current_location_id)
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
        "available_missions": datanet_missions,
        "system_notices": system_notices,
        "mission_actions": [],  # DataNet uses its own accept flow
        "has_mission_accept_action": bool(datanet_missions),
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


def _combat_action_menu(
    round_number: int,
    player_hull_pct: int,
    enemy_hull_pct: int,
    allowed_actions: list[str],
    encounter_description: str | None = None,
    enemy_ship_info: dict[str, Any] | None = None,
) -> str:
    """
    Prompt player for combat action selection.
    
    Per combat_resolution_contract.md Section 3: "CORE ACTIONS"
    Always available: Focus Fire, Reinforce Shields, Evasive Maneuvers, Attempt Escape, Surrender
    
    Args:
        round_number: Current combat round (1-indexed, no round 0)
        player_hull_pct: Player hull percentage (0-100)
        enemy_hull_pct: Enemy hull percentage (0-100)
        allowed_actions: List of allowed combat action labels (from engine's pending_combat.allowed_actions)
        encounter_description: Optional encounter description (e.g., "Pirate Raider", "Border Patrol")
        enemy_ship_info: Optional enemy ship information dict
        
    Returns:
        Selected action label (must be in allowed_actions)
    """
    # Enforce round numbering: no round 0
    if round_number < 1:
        round_number = 1
    
    # Display encounter description and enemy ship info
    print(f"\n--- COMBAT - Round {round_number} ---")
    
    if encounter_description:
        print(f"Encounter: {encounter_description}")
    
    if enemy_ship_info:
        hull_name = enemy_ship_info.get("hull_name", "Unknown")
        hull_id = enemy_ship_info.get("hull_id", "unknown")
        module_count = enemy_ship_info.get("module_count", 0)
        weapon_modules = enemy_ship_info.get("weapon_modules", 0)
        defense_modules = enemy_ship_info.get("defense_modules", 0)
        utility_modules = enemy_ship_info.get("utility_modules", 0)
        print(f"Enemy Ship: {hull_name} ({hull_id})")
        if module_count > 0:
            module_parts = []
            if weapon_modules > 0:
                module_parts.append(f"{weapon_modules} weapon")
            if defense_modules > 0:
                module_parts.append(f"{defense_modules} defense")
            if utility_modules > 0:
                module_parts.append(f"{utility_modules} utility")
            if module_parts:
                print(f"  Modules: {', '.join(module_parts)}")
    
    # Concise round summary
    print(f"\nPlayer hull: {player_hull_pct}%")
    print(f"Enemy hull: {enemy_hull_pct}%")
    print("\nAvailable Actions:")
    
    # Build numbered menu using labels directly from engine (contract-correct)
    # Do NOT hardcode action names - use what the engine provides
    options = {}
    for idx, action_label in enumerate(allowed_actions, start=1):
        print(f"{idx}) {action_label}")
        options[idx] = action_label
    
    # Get player selection
    while True:
        raw_choice = input("Select action: ").strip()
        try:
            selected = int(raw_choice)
            if selected in options:
                return options[selected]
            else:
                print(f"Invalid selection. Please choose 1-{len(options)}")
        except ValueError:
            print("Invalid input. Please enter a number.")


if __name__ == "__main__":
    main()
