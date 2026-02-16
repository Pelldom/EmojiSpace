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
    system_id = input("Target system_id: ").strip()
    destination_id = input("Target destination_id (optional): ").strip()
    inter_raw = input("Inter-system travel? [y/N]: ").strip().lower()
    inter_system = inter_raw in {"y", "yes", "1", "true"}
    payload: dict[str, object] = {
        "type": "travel_to_destination",
        "target_system_id": system_id,
        "inter_system": inter_system,
    }
    if destination_id:
        payload["target_destination_id"] = destination_id
    if inter_system:
        distance_raw = input("distance_ly [1]: ").strip()
        try:
            distance_ly = float(distance_raw) if distance_raw else 1.0
        except ValueError:
            distance_ly = 1.0
        payload["distance_ly"] = distance_ly
    print(json.dumps(engine.execute(payload), sort_keys=True))


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
