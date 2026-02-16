from __future__ import annotations

import json

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
    rows: list[dict[str, object]] = []
    for system in engine.sector.systems:
        rows.append(
            {
                "system_id": system.system_id,
                "name": system.name,
                "population": int(system.population),
                "government_id": system.government_id,
                "x": float(system.x),
                "y": float(system.y),
                "destinations": [
                    {
                        "destination_id": destination.destination_id,
                        "display_name": destination.display_name,
                        "population": int(destination.population),
                    }
                    for destination in system.destinations
                ],
            }
        )
    print(json.dumps(rows, sort_keys=True))


def _travel_menu(engine: GameEngine) -> None:
    current_system_id = engine.player_state.current_system_id
    current_system = engine.sector.get_system(current_system_id)
    if current_system is None:
        print(json.dumps({"ok": False, "error": "current_system_not_found"}, sort_keys=True))
        return

    print(f"Current system: {current_system.system_id} ({current_system.name})")
    print("1) Inter-system warp")
    print("2) Intra-system destination travel")
    mode = input("Travel mode: ").strip()

    if mode == "1":
        options = [system for system in engine.sector.systems if system.system_id != current_system.system_id]
        options.sort(key=lambda system: system.system_id)
        if not options:
            print(json.dumps({"ok": False, "error": "no_inter_system_targets"}, sort_keys=True))
            return
        for index, system in enumerate(options, start=1):
            dx = float(system.x) - float(current_system.x)
            dy = float(system.y) - float(current_system.y)
            distance = (dx * dx + dy * dy) ** 0.5
            print(f"{index}) {system.system_id} {system.name} distance_ly={distance:.3f}")
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
        if destinations:
            print("Destination options:")
            for index, destination in enumerate(destinations, start=1):
                print(f"{index}) {destination.destination_id} {destination.display_name}")
            raw_destination = input("Select destination index [1]: ").strip()
            if raw_destination:
                try:
                    destination_index = int(raw_destination)
                    if 1 <= destination_index <= len(destinations):
                        target_destination_id = destinations[destination_index - 1].destination_id
                except ValueError:
                    pass
        payload: dict[str, object] = {
            "type": "travel_to_destination",
            "target_system_id": target_system.system_id,
        }
        if target_destination_id is not None:
            payload["target_destination_id"] = target_destination_id
        print(json.dumps(engine.execute(payload), sort_keys=True))
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
    print(json.dumps({"event": "engine_init", "seed": seed}, sort_keys=True))
    while True:
        print("1) list systems and destinations")
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


if __name__ == "__main__":
    main()
