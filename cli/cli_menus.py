"""
Menu flow only. No rendering logic; menus only call renderer functions.
"""

from __future__ import annotations

import math
from typing import Any

from cli_renderer import (
    destination_display_entity,
    location_display_entity,
    menu_back,
    menu_exit,
    render_entity,
    render_encounter,
    render_good,
    ship_display_entity,
    title_current_location,
)
from cli_input import get_choice, get_choice_required


# ----- Engine result extraction (no display logic) -----

def _extract_detail_from_stage(step_result: dict, stage: str) -> dict | None:
    events = step_result.get("events") or []
    for event in events:
        if isinstance(event, dict) and event.get("stage") == stage:
            detail = event.get("detail")
            if isinstance(detail, dict):
                return detail
    return None


def _extract_actions_from_stage(step_result: dict, stage: str) -> list[dict]:
    events = step_result.get("events") or []
    for event in events:
        if isinstance(event, dict) and event.get("stage") == stage:
            detail = event.get("detail")
            if isinstance(detail, dict):
                actions = detail.get("actions") or []
                return [a for a in actions if isinstance(a, dict)]
    return []


def _extract_rows_from_stage(step_result: dict, stage: str) -> list[dict]:
    events = step_result.get("events") or []
    for event in events:
        if isinstance(event, dict) and event.get("stage") == stage:
            detail = event.get("detail")
            if isinstance(detail, dict):
                rows = detail.get("rows") or []
                return [r for r in rows if isinstance(r, dict)]
    return []


# ----- Helpers: visibility and names from engine -----

def _visited_system_ids(engine: Any) -> set[str]:
    ids = getattr(engine.player_state, "visited_system_ids", None)
    return set(ids) if isinstance(ids, (set, list)) else set()


def _visited_destination_ids(engine: Any) -> set[str]:
    ids = getattr(engine.player_state, "visited_destination_ids", None)
    return set(ids) if isinstance(ids, (set, list)) else set()


def _current_destination(engine: Any) -> Any:
    ctx = engine.get_current_destination_context()
    dest_id = ctx.get("destination_id") or ""
    if not dest_id:
        return None
    sector = getattr(engine, "sector", None)
    if not sector:
        return None
    system = sector.get_system(engine.player_state.current_system_id) if engine.player_state.current_system_id else None
    if not system:
        return None
    for d in getattr(system, "destinations", []) or []:
        if getattr(d, "destination_id", None) == dest_id:
            return d
    return None


def _current_location_type(engine: Any) -> str:
    dest = _current_destination(engine)
    if not dest:
        return ""
    loc_id = str(engine.player_state.current_location_id or "")
    for loc in list(getattr(dest, "locations", []) or []):
        if getattr(loc, "location_id", None) == loc_id:
            return str(getattr(loc, "location_type", "") or "")
    return ""


def _current_location_name(engine: Any) -> str:
    loc_type = _current_location_type(engine)
    if loc_type:
        return loc_type.replace("_", " ").title()
    return _current_destination_name(engine)


def _current_destination_name(engine: Any) -> str:
    ctx = engine.get_current_destination_context()
    return str(ctx.get("destination_name") or "Unknown")


def _good_name_and_entity(engine: Any, sku_id: str) -> tuple[str, Any]:
    try:
        catalog = getattr(engine, "catalog", None)
        if catalog and hasattr(catalog, "good_by_sku"):
            good = catalog.good_by_sku(sku_id)
            return (getattr(good, "name", sku_id), good)
    except Exception:
        pass
    return (sku_id, {"category": None, "tags": [], "name": sku_id})


def _hull_name(engine: Any, hull_id: str) -> str:
    try:
        from hull_utils import get_hull_display_name
        return get_hull_display_name(hull_id) or hull_id
    except Exception:
        return hull_id or "Unknown"


# ----- Main menu -----

def run_main_loop(engine: Any) -> None:
    while True:
        if engine.has_pending_encounter():
            _resolve_pending_encounter(engine)
            continue
        if engine.has_pending_combat():
            _resolve_pending_combat(engine)
            continue
        pending_loot = engine.get_pending_loot()
        if pending_loot:
            _resolve_pending_loot(engine, pending_loot)
            continue

        dest_name = _current_destination_name(engine)
        loc_type = _current_location_type(engine)
        if loc_type:
            current_label = _current_location_name(engine)
        else:
            current_label = dest_name

        print()
        print(title_current_location(current_label))
        print()
        dest_profile = _extract_detail_from_stage(
            engine.execute({"type": "get_destination_profile"}),
            "destination_profile",
        )
        market_attached = bool(dest_profile and dest_profile.get("market_attached"))

        print("1 Travel")
        print("2 Locations")
        print("3 Missions")
        print("4 Ship")
        if market_attached:
            print("5 Market")
        print("6 Status")
        print(menu_exit())

        max_opt = 6
        choice = get_choice(max_opt)
        if choice is None:
            print("Invalid choice.")
            continue
        if choice == 0:
            _do_quit(engine)
            return
        if choice == 1:
            _travel_menu(engine)
        elif choice == 2:
            _locations_menu(engine)
        elif choice == 3:
            _missions_menu(engine)
        elif choice == 4:
            _ship_menu(engine)
        elif choice == 5 and market_attached:
            _market_menu(engine)
        elif choice == 6:
            _status_menu(engine)
        else:
            print("Invalid choice.")


def _do_quit(engine: Any) -> None:
    engine.execute({"type": "quit"})


# ----- Travel -----

def _travel_menu(engine: Any) -> None:
    system_result = engine.execute({"type": "get_system_profile"})
    detail = _extract_detail_from_stage(system_result, "system_profile")
    if not detail:
        print("Unable to load system.")
        return
    reachable = detail.get("reachable_systems") or []
    current_system_id = engine.player_state.current_system_id
    sector = engine.sector
    current_system = sector.get_system(current_system_id) if current_system_id else None
    visited = _visited_system_ids(engine)

    print()
    print("0 Back")
    print("1 Inter-system travel")
    print("2 Travel to destination in this system")
    c = get_choice(2)
    if c is None:
        print("Invalid choice.")
        return
    if c == 0:
        return

    if c == 1:
        if not reachable:
            print("No systems in range.")
            return
        options = sorted(reachable, key=lambda r: (r.get("name") or r.get("system_id") or ""))
        for idx, row in enumerate(options, start=1):
            sys_id = row.get("system_id") or ""
            name = row.get("name") or sys_id
            system_obj = sector.get_system(sys_id) if sys_id else None
            visible = sys_id in visited
            display = render_entity(system_obj if system_obj else row, name, visible)
            in_range = row.get("in_range", False)
            dist = row.get("distance_ly", 0)
            print(f"{idx} {display} ({dist:.1f} ly, {'in range' if in_range else 'out of range'})")
        print("0 Back")
        sel = get_choice(len(options))
        if sel is None or sel == 0:
            return
        if sel < 1 or sel > len(options):
            print("Invalid choice.")
            return
        target = options[sel - 1]
        target_system_id = target.get("system_id")
        target_system = sector.get_system(target_system_id) if target_system_id else None
        dests = list(getattr(target_system, "destinations", []) or []) if target_system else []
        target_destination_id = dests[0].destination_id if dests else None
        result = engine.execute({
            "type": "travel_to_destination",
            "target_system_id": target_system_id,
            "target_destination_id": target_destination_id,
        })
        _handle_travel_result(engine, result, target_system, target_system_id)
        return

    if c == 2:
        if not current_system:
            print("No current system.")
            return
        dests = sorted(
            list(getattr(current_system, "destinations", []) or []),
            key=lambda d: getattr(d, "display_name", "") or getattr(d, "destination_id", ""),
        )
        if not dests:
            print("No destinations here.")
            return
        for idx, dest in enumerate(dests, start=1):
            visible = getattr(dest, "destination_id", "") in _visited_destination_ids(engine)
            name = getattr(dest, "display_name", "") or getattr(dest, "destination_id", "")
            display = render_entity(destination_display_entity(dest), name, visible)
            print(f"{idx} {display}")
        print("0 Back")
        sel = get_choice(len(dests))
        if sel is None or sel == 0:
            return
        if sel < 1 or sel > len(dests):
            print("Invalid choice.")
            return
        dest = dests[sel - 1]
        result = engine.execute({
            "type": "travel_to_destination",
            "target_system_id": current_system_id,
            "target_destination_id": getattr(dest, "destination_id", None),
        })
        _handle_travel_result(engine, result, current_system, current_system_id)


def _handle_travel_result(engine: Any, result: dict, system: Any, system_id: str) -> None:
    if result.get("game_over"):
        print("Game over.")
        return
    while result.get("hard_stop"):
        reason = result.get("hard_stop_reason")
        if reason == "pending_encounter_decision":
            result = _resolve_pending_encounter(engine)
        elif reason == "pending_combat_action":
            _resolve_pending_combat(engine)
            result = {}
        else:
            break
    if not result.get("hard_stop") and system_id and system:
        visible = system_id in _visited_system_ids(engine)
        name = getattr(system, "name", None) or system_id
        print(f"You have arrived in {render_entity(system, name, visible)}.")


# ----- Pending encounter / combat / loot -----

def _resolve_pending_encounter(engine: Any) -> dict:
    info = engine.get_pending_encounter_info()
    if not info:
        return {}
    options = info.get("options") or []
    encounter_description = info.get("encounter_description") or "Unknown"
    display = render_encounter(encounter_description, None, visible=True)
    print()
    print(display)
    for idx, opt in enumerate(options, start=1):
        label = opt.get("label", "Unknown")
        print(f"{idx} {label}")
    print("0 Back")
    if not options:
        return {}
    c = get_choice(len(options))
    if c is None or c == 0:
        return {}
    if c < 1 or c > len(options):
        print("Invalid choice.")
        return {}
    decision_id = options[c - 1].get("id")
    if not decision_id:
        return {}
    result = engine.execute({
        "type": "encounter_decision",
        "encounter_id": info.get("encounter_id"),
        "decision_id": decision_id,
    })
    if engine.has_pending_combat():
        _resolve_pending_combat(engine)
    return result


def _resolve_pending_combat(engine: Any) -> None:
    info = engine.get_pending_combat_info()
    if not info:
        return
    allowed = info.get("allowed_actions") or []
    labels = [a.get("label", "") for a in allowed]
    ids = [a.get("id", "") for a in allowed]
    while engine.has_pending_combat():
        info = engine.get_pending_combat_info()
        if not info:
            break
        allowed = info.get("allowed_actions") or []
        labels = [a.get("label", "") for a in allowed]
        ids = [a.get("id", "") for a in allowed]
        round_num = info.get("round_number", 1)
        player_pct = info.get("player_hull_pct", 0)
        enemy_pct = info.get("enemy_hull_pct", 0)
        print(f"\n--- Combat Round {round_num} ---")
        enemy_info = info.get("enemy_ship_info") or {}
        enemy_name = enemy_info.get("hull_name", "Unknown")
        print(f"Enemy: {render_entity(enemy_info, enemy_name, True)}")
        print(f"Your hull: {player_pct}% | Enemy hull: {enemy_pct}%")
        for idx, label in enumerate(labels, start=1):
            print(f"{idx} {label}")
        c = get_choice(len(labels))
        if c is None or c == 0:
            continue
        if c < 1 or c > len(labels):
            print("Invalid choice.")
            continue
        action_id = ids[c - 1] if c <= len(ids) else None
        if not action_id:
            continue
        result = engine.execute({
            "type": "combat_action",
            "action": action_id,
            "encounter_id": info.get("encounter_id"),
        })
        if result.get("combat_ended"):
            if result.get("combat_result", {}).get("winner") == "player":
                print("You win!")
            else:
                print("Combat ended.")
            break


def _resolve_pending_loot(engine: Any, pending_loot: dict) -> None:
    print("\nLoot recovered.")
    print("1 Take all")
    print("2 Decline")
    c = get_choice(2)
    if c is None or c == 0:
        return
    if c == 1:
        engine.resolve_pending_loot(take_all=True)
    else:
        engine.resolve_pending_loot(take_all=False)


# ----- Locations -----

def _locations_menu(engine: Any) -> None:
    dest = _current_destination(engine)
    if not dest:
        print("No destination.")
        return
    locations = sorted(
        list(getattr(dest, "locations", []) or []),
        key=lambda loc: str(getattr(loc, "location_type", "") or getattr(loc, "location_id", "")),
    )
    if not locations:
        print("No locations here.")
        return
    print()
    for idx, loc in enumerate(locations, start=1):
        loc_type = str(getattr(loc, "location_type", "") or "")
        name = loc_type.replace("_", " ").title() if loc_type else "Unknown"
        entity = location_display_entity(loc)
        print(render_entity(entity, name, True))
    print(menu_back())
    sel = get_choice(len(locations))
    if sel is None or sel == 0:
        return
    if sel < 1 or sel > len(locations):
        print("Invalid choice.")
        return
    loc = locations[sel - 1]
    loc_id = getattr(loc, "location_id", None)
    result = engine.execute({"type": "enter_location", "location_index": sel})
    if not result.get("ok"):
        print("Unable to enter location.")
        return
    loc_type = str(getattr(loc, "location_type", "") or "")
    if loc_type == "market":
        _market_location_menu(engine)
    elif loc_type == "shipdock":
        _shipdock_menu(engine)
    else:
        _location_actions_menu(engine)


def _location_actions_menu(engine: Any) -> None:
    list_result = engine.execute({"type": "list_location_actions"})
    actions = _extract_actions_from_stage(list_result, "location_actions")
    if not actions:
        print("No actions here.")
        _return_to_destination(engine)
        return
    actions_sorted = sorted(actions, key=lambda a: str(a.get("display_name", "") or a.get("action_id", "")))
    print()
    for idx, action in enumerate(actions_sorted, start=1):
        display_name = str(action.get("display_name") or action.get("action_id") or "")
        print(f"{idx} {render_entity(action, display_name, True)}")
    print(menu_back())
    sel = get_choice(len(actions_sorted))
    if sel is None or sel == 0:
        _return_to_destination(engine)
        return
    if sel < 1 or sel > len(actions_sorted):
        print("Invalid choice.")
        return
    action = actions_sorted[sel - 1]
    result = engine.execute({
        "type": "location_action",
        "action_id": action.get("action_id"),
        "kwargs": _prompt_action_kwargs(action),
        "confirm": True,
    })
    if not result.get("ok") and result.get("error"):
        print(result.get("error", "Error"))
    _return_to_destination(engine)


def _destination_actions_menu(engine: Any) -> None:
    list_result = engine.execute({"type": "list_destination_actions"})
    actions = _extract_actions_from_stage(list_result, "destination_actions")
    if not actions:
        print("No actions here.")
        _return_to_destination(engine)
        return
    actions_sorted = sorted(actions, key=lambda a: str(a.get("display_name", "") or a.get("action_id", "")))
    print()
    for idx, action in enumerate(actions_sorted, start=1):
        display_name = str(action.get("display_name") or action.get("action_id") or "")
        print(f"{idx} {render_entity(action, display_name, True)}")
    print(menu_back())
    sel = get_choice(len(actions_sorted))
    if sel is None or sel == 0:
        _return_to_destination(engine)
        return
    if sel < 1 or sel > len(actions_sorted):
        print("Invalid choice.")
        return
    action = actions_sorted[sel - 1]
    result = engine.execute({
        "type": "destination_action",
        "action_id": action.get("action_id"),
        "action_kwargs": _prompt_action_kwargs(action),
    })
    if not result.get("ok") and result.get("error"):
        print(result.get("error", "Error"))
    _return_to_destination(engine)


def _return_to_destination(engine: Any) -> None:
    engine.execute({"type": "return_to_destination"})
    name = _current_destination_name(engine)
    dest = _current_destination(engine)
    visible = getattr(dest, "destination_id", "") in _visited_destination_ids(engine) if dest else True
    print(f"Back at {render_entity(destination_display_entity(dest), name, visible)}.")


def _prompt_action_kwargs(action: dict) -> dict:
    params = action.get("parameters") or []
    if not params:
        return {}
    kwargs = {}
    for p in params:
        if isinstance(p, dict):
            name = p.get("name")
            prompt = p.get("prompt", name)
            if not name:
                continue
            raw = input(f"{prompt}: ").strip()
            if p.get("type") == "int":
                try:
                    kwargs[name] = int(raw)
                except ValueError:
                    kwargs[name] = raw
            else:
                kwargs[name] = raw
        elif isinstance(p, str):
            raw = input(f"{p}: ").strip()
            if p in ("quantity", "requested_units", "location_index"):
                try:
                    kwargs[p] = int(raw)
                except ValueError:
                    kwargs[p] = raw
            else:
                kwargs[p] = raw
    return kwargs


# ----- Market (at destination level: list goods) -----

def _market_menu(engine: Any) -> None:
    buy_result = engine.execute({"type": "market_buy_list"})
    buy_rows = _extract_rows_from_stage(buy_result, "market_buy_list")
    sell_result = engine.execute({"type": "market_sell_list"})
    sell_rows = _extract_rows_from_stage(sell_result, "market_sell_list")
    all_skus = set()
    for row in buy_rows or []:
        sku = row.get("sku_id")
        if sku:
            all_skus.add(sku)
    for row in sell_rows or []:
        sku = row.get("sku_id")
        if sku:
            all_skus.add(sku)
    if not all_skus:
        print("No market goods here.")
        return
    sku_list = sorted(all_skus)
    print()
    for idx, sku_id in enumerate(sku_list, start=1):
        name, entity = _good_name_and_entity(engine, sku_id)
        print(f"{idx} {render_good(entity, name, True)}")
    print(menu_back())
    sel = get_choice(len(sku_list))
    if sel is None or sel == 0:
        return
    if sel < 1 or sel > len(sku_list):
        print("Invalid choice.")
        return
    sku_id = sku_list[sel - 1]
    print("1 Buy  2 Sell  0 Back")
    c = get_choice(2)
    if c is None or c == 0:
        return
    if c == 1:
        qty_str = input("Quantity: ").strip()
        try:
            qty = int(qty_str)
        except ValueError:
            qty = 0
        engine.execute({"type": "market_buy", "sku_id": sku_id, "quantity": qty})
    elif c == 2:
        qty_str = input("Quantity: ").strip()
        try:
            qty = int(qty_str)
        except ValueError:
            qty = 0
        engine.execute({"type": "market_sell", "sku_id": sku_id, "quantity": qty})


def _market_location_menu(engine: Any) -> None:
    _market_menu(engine)
    _return_to_destination(engine)


# ----- Shipdock -----

def _shipdock_menu(engine: Any) -> None:
    list_result = engine.execute({"type": "list_location_actions"})
    actions = _extract_actions_from_stage(list_result, "location_actions")
    action_ids = [a.get("action_id") for a in actions if a.get("action_id")]
    print()
    print("1 Buy Hull")
    print("2 Buy Module")
    print("3 Sell Hull")
    print("4 Sell Module")
    print("5 Repair Ship")
    print(menu_back())
    c = get_choice(5)
    if c is None or c == 0:
        _return_to_destination(engine)
        return
    if c == 1:
        _shipdock_buy_hull(engine)
    elif c == 2:
        _shipdock_buy_module(engine)
    elif c == 3:
        _shipdock_sell_hull(engine)
    elif c == 4:
        _shipdock_sell_module(engine)
    elif c == 5:
        engine.execute({"type": "location_action", "action_id": "repair_ship", "kwargs": {}, "confirm": True})
    _shipdock_menu(engine)


def _shipdock_buy_hull(engine: Any) -> None:
    result = engine.execute({"type": "shipdock_hull_list"})
    rows = _extract_rows_from_stage(result, "shipdock_hull_list")
    if not rows:
        print("No hulls for sale.")
        return
    for idx, row in enumerate(rows, start=1):
        hull_id = row.get("hull_id", "")
        name = _hull_name(engine, hull_id)
        entity = ship_display_entity(row)
        print(f"{idx} {render_entity(entity, name, True)}")
    print("0 Back")
    sel = get_choice(len(rows))
    if sel is None or sel == 0:
        return
    if sel < 1 or sel > len(rows):
        return
    hull_id = rows[sel - 1].get("hull_id")
    active = engine.get_active_ship()
    ship_id = active.get("ship_id") if active else None
    if not ship_id:
        print("No active ship.")
        return
    engine.execute({"type": "location_action", "action_id": "buy_hull", "kwargs": {"ship_id": ship_id, "hull_id": hull_id}, "confirm": True})


def _shipdock_buy_module(engine: Any) -> None:
    result = engine.execute({"type": "shipdock_module_list"})
    rows = _extract_rows_from_stage(result, "shipdock_module_list")
    if not rows:
        print("No modules for sale.")
        return
    for idx, row in enumerate(rows, start=1):
        mod_id = row.get("module_id", "")
        name = row.get("display_name") or mod_id
        print(f"{idx} {render_entity(row, name, True)}")
    print("0 Back")
    sel = get_choice(len(rows))
    if sel is None or sel == 0:
        return
    if sel < 1 or sel > len(rows):
        return
    module_id = rows[sel - 1].get("module_id")
    active = engine.get_active_ship()
    ship_id = active.get("ship_id") if active else None
    if not ship_id:
        return
    engine.execute({"type": "location_action", "action_id": "buy_module", "kwargs": {"ship_id": ship_id, "module_id": module_id}, "confirm": True})


def _shipdock_sell_hull(engine: Any) -> None:
    ships = engine.get_owned_ships()
    if not ships:
        print("No ships to sell.")
        return
    for idx, ship in enumerate(ships, start=1):
        hull_id = ship.get("hull_id", "")
        name = _hull_name(engine, hull_id)
        print(f"{idx} {render_entity(ship_display_entity(ship), name, True)}")
    print("0 Back")
    sel = get_choice(len(ships))
    if sel is None or sel == 0:
        return
    if sel < 1 or sel > len(ships):
        return
    ship_id = ships[sel - 1].get("ship_id")
    engine.execute({"type": "location_action", "action_id": "sell_hull", "kwargs": {"ship_id": ship_id}, "confirm": True})


def _shipdock_sell_module(engine: Any) -> None:
    active = engine.get_active_ship()
    if not active:
        print("No active ship.")
        return
    ship_id = active.get("ship_id")
    result = engine.execute({"type": "shipdock_installed_modules_list", "ship_id": ship_id})
    rows = _extract_rows_from_stage(result, "shipdock_installed_modules_list")
    if not rows:
        print("No modules to sell.")
        return
    for idx, row in enumerate(rows, start=1):
        name = row.get("display_name") or row.get("module_id", "")
        print(f"{idx} {render_entity(row, name, True)}")
    print("0 Back")
    sel = get_choice(len(rows))
    if sel is None or sel == 0:
        return
    if sel < 1 or sel > len(rows):
        return
    module_id = rows[sel - 1].get("module_id")
    engine.execute({"type": "location_action", "action_id": "sell_module", "kwargs": {"ship_id": ship_id, "module_id": module_id}, "confirm": True})


# ----- Ship menu (status) -----

def _ship_menu(engine: Any) -> None:
    active = engine.get_active_ship()
    if not active:
        print("No active ship.")
        return
    hull_id = active.get("hull_id", "")
    name = _hull_name(engine, hull_id)
    print()
    print(render_entity(ship_display_entity(active), name, True))
    hull_int = active.get("hull_integrity") or {}
    cur = hull_int.get("current", 0)
    mx = hull_int.get("max", 1)
    if mx:
        print(f"Hull: {cur}/{mx}")
    fuel = active.get("fuel") or {}
    print(f"Fuel: {fuel.get('current', 0)}/{fuel.get('capacity', 0)}")
    print(menu_back())
    get_choice_required(0)


# ----- Missions -----

def _missions_menu(engine: Any) -> None:
    result = engine.execute({"type": "get_destination_profile"})
    detail = _extract_detail_from_stage(result, "destination_profile")
    missions = (detail or {}).get("active_missions") or []
    if not missions:
        print("No active missions.")
        print(menu_back())
        get_choice(0)
        return
    for idx, m in enumerate(missions, start=1):
        mission_type = m.get("mission_type") or "Mission"
        target_id = (m.get("target_destination_id") or m.get("target_system_id") or "")
        name = f"{mission_type} -> {target_id}" if target_id else mission_type
        print(f"{idx} {render_entity(m, name, True)}")
    print(menu_back())
    get_choice(len(missions))


# ----- Status -----

def _status_menu(engine: Any) -> None:
    result = engine.execute({"type": "get_player_profile"})
    detail = _extract_detail_from_stage(result, "player_profile")
    if not detail:
        print("Unable to load status.")
        print(menu_back())
        get_choice(0)
        return
    credits = detail.get("credits", 0)
    ship = detail.get("ship") or {}
    hull_id = ship.get("hull_id", "")
    name = _hull_name(engine, hull_id)
    print()
    print(f"Credits: {credits}")
    print(f"Ship: {render_entity(ship_display_entity(ship), name, True)}")
    print(menu_back())
    get_choice_required(0)
