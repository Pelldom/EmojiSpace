"""
Admin tools. Hidden from players; launch with python cli/run_game_cli.py --admin.
"""

from __future__ import annotations

from typing import Any

from cli_input import get_choice
from cli_renderer import destination_display_entity, render_entity


def run_admin_loop(engine: Any) -> None:
    while True:
        print()
        print("Admin")
        print("1 Galaxy Summary")
        print("2 Ship Configurator")
        print("3 Player State Inspector")
        print("4 Force Encounter")
        print("5 Seed Inspector")
        print("0 Exit")
        c = get_choice(5)
        if c is None:
            print("Invalid choice.")
            continue
        if c == 0:
            return
        if c == 1:
            _galaxy_summary(engine)
        elif c == 2:
            _ship_configurator(engine)
        elif c == 3:
            _player_state_inspector(engine)
        elif c == 4:
            _force_encounter(engine)
        elif c == 5:
            _seed_inspector(engine)


def _visited_system_ids(engine: Any) -> set[str]:
    ids = getattr(engine.player_state, "visited_system_ids", None)
    return set(ids) if isinstance(ids, (set, list)) else set()


def _visited_destination_ids(engine: Any) -> set[str]:
    ids = getattr(engine.player_state, "visited_destination_ids", None)
    return set(ids) if isinstance(ids, (set, list)) else set()


def _galaxy_summary(engine: Any) -> None:
    sector = getattr(engine, "sector", None)
    if not sector or not getattr(sector, "systems", None):
        print("No sector data.")
        return
    systems = sorted(sector.systems, key=lambda s: getattr(s, "system_id", ""))
    visited_sys = _visited_system_ids(engine)
    visited_dest = _visited_destination_ids(engine)
    print()
    print("Galaxy Summary")
    print(f"Total systems: {len(systems)}")
    for system in systems:
        sys_id = getattr(system, "system_id", "")
        name = getattr(system, "name", sys_id)
        visible = sys_id in visited_sys
        display = render_entity(system, name, visible)
        gov_id = getattr(system, "government_id", "")
        try:
            government = engine.government_registry.get_government(gov_id)
            gov_name = government.name if government else gov_id
        except Exception:
            gov_name = gov_id
        print(f"  {display} (gov: {gov_name})")
        for dest in sorted(getattr(system, "destinations", []) or [], key=lambda d: getattr(d, "destination_id", "")):
            dest_id = getattr(dest, "destination_id", "")
            dname = getattr(dest, "display_name", dest_id)
            vis = dest_id in visited_dest
            print(f"    {render_entity(destination_display_entity(dest), dname, vis)}")
    print()


def _ship_configurator(engine: Any) -> None:
    ships = engine.get_owned_ships()
    active = engine.get_active_ship()
    active_id = active.get("ship_id") if active else None
    print()
    print("Owned ships:")
    for ship in ships or []:
        sid = ship.get("ship_id", "")
        hull_id = ship.get("hull_id", "")
        marker = " (active)" if sid == active_id else ""
        print(f"  {render_entity(ship, hull_id or sid, True)}{marker}")
    if not ships:
        print("  (none)")
    print("0 Back")
    get_choice(0)


def _player_state_inspector(engine: Any) -> None:
    ps = engine.player_state
    print()
    print("Player State")
    print(f"  credits: {getattr(ps, 'credits', 'N/A')}")
    print(f"  current_system_id: {getattr(ps, 'current_system_id', 'N/A')}")
    print(f"  current_destination_id: {getattr(ps, 'current_destination_id', 'N/A')}")
    print(f"  current_location_id: {getattr(ps, 'current_location_id', 'N/A')}")
    print(f"  active_ship_id: {getattr(ps, 'active_ship_id', 'N/A')}")
    print(f"  visited_system_ids: {len(getattr(ps, 'visited_system_ids', []) or [])} systems")
    print("0 Back")
    get_choice(0)


def _force_encounter(engine: Any) -> None:
    print()
    print("Force encounter: not implemented. Use engine harness for encounter testing.")
    print("0 Back")
    get_choice(0)


def _seed_inspector(engine: Any) -> None:
    seed = getattr(engine, "world_seed", None)
    print()
    print(f"World seed: {seed}")
    print("0 Back")
    get_choice(0)
