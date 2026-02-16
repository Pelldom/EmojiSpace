import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"
sys.path.insert(0, str(SRC_ROOT))

import time_engine as te  # noqa: E402
from government_registry import GovernmentRegistry  # noqa: E402
from world_generator import WorldGenerator  # noqa: E402


@dataclass
class _PlayerStub:
    current_system_id: str
    npc_registry: Any = None


def _run_world_state_horizon(seed: int, days: int) -> tuple[list[dict[str, Any]], dict[str, list[int]]]:
    te._reset_time_state_for_test()
    registry = GovernmentRegistry.from_file(PROJECT_ROOT / "data" / "governments.json")
    sector = WorldGenerator(seed=seed, system_count=4, government_ids=registry.government_ids()).generate()
    player = _PlayerStub(current_system_id=sector.systems[0].system_id)
    time_engine = te.TimeEngine(
        logger=None,
        world_seed=seed,
        sector=sector,
        player_state=player,
        event_frequency_percent=8,
    )
    engine = te._world_state_engine
    assert engine is not None

    initial_destination_ids = {
        system.system_id: sorted(destination.destination_id for destination in system.destinations)
        for system in sector.systems
    }
    destroyed_seen_by_system: dict[str, set[str]] = {system_id: set() for system_id in initial_destination_ids}
    snapshots: list[dict[str, Any]] = []

    for day in range(1, days + 1):
        turn = time_engine.advance()
        assert turn == day
        snapshot_systems: list[dict[str, Any]] = []
        for system in sorted(sector.systems, key=lambda row: row.system_id):
            destination_ids_now = sorted(destination.destination_id for destination in system.destinations)
            assert destination_ids_now == initial_destination_ids[system.system_id]
            assert int(system.population) >= 0

            destination_tags = {
                destination.destination_id: sorted(str(tag) for tag in getattr(destination, "tags", []))
                for destination in system.destinations
            }
            destroyed_now = {
                destination_id
                for destination_id, tags in destination_tags.items()
                if "destroyed" in tags
            }
            assert destroyed_seen_by_system[system.system_id].issubset(destroyed_now)
            destroyed_seen_by_system[system.system_id] = destroyed_now

            active_events = [
                (row.event_id, int(getattr(row, "trigger_day", 0)))
                for row in engine.get_active_events(system.system_id)
            ]
            assert len(active_events) == len(set(active_events))
            active_event_ids = sorted(event_id for event_id, _ in active_events)
            active_situation_ids = sorted(
                row.situation_id for row in engine.get_active_situations(system.system_id)
            )

            snapshot_systems.append(
                {
                    "system_id": system.system_id,
                    "population": int(system.population),
                    "government_id": str(system.government_id),
                    "destination_tags": destination_tags,
                    "active_event_ids": active_event_ids,
                    "active_situation_ids": active_situation_ids,
                    "last_structural_mutation_day": engine.last_structural_mutation_day_by_system.get(
                        system.system_id
                    ),
                    "cooldown_until_day": engine.cooldown_until_day_by_system.get(system.system_id),
                }
            )

        assert all(int(row.trigger_day) > day for row in engine.scheduled_events)
        snapshots.append(
            {
                "day": day,
                "systems": snapshot_systems,
                "scheduled_events": sorted(
                    (
                        row.event_id,
                        row.system_id,
                        int(row.trigger_day),
                        int(row.insertion_index),
                    )
                    for row in engine.scheduled_events
                ),
                "scheduled_situations": sorted(
                    (
                        row.situation_id,
                        row.system_id,
                        int(row.trigger_day),
                        int(row.insertion_index),
                    )
                    for row in engine.scheduled_situations
                ),
            }
        )

    structural_days_by_system: dict[str, list[int]] = {}
    for row in engine.pending_structural_mutations:
        day_applied = row.get("day_applied")
        if not isinstance(day_applied, int):
            continue
        system_id = str(row.get("system_id"))
        structural_days_by_system.setdefault(system_id, []).append(day_applied)
    for system_id in structural_days_by_system:
        structural_days_by_system[system_id].sort()

    return snapshots, structural_days_by_system


def test_long_horizon_deterministic_world_state() -> None:
    days = 300
    seed = 12345

    snapshots_a, structural_days_a = _run_world_state_horizon(seed=seed, days=days)
    snapshots_b, structural_days_b = _run_world_state_horizon(seed=seed, days=days)

    assert snapshots_a == snapshots_b
    assert structural_days_a == structural_days_b

    for system_id, days_list in structural_days_a.items():
        for index in range(1, len(days_list)):
            assert (days_list[index] - days_list[index - 1]) >= 10, (
                f"Structural limiter violation system_id={system_id} "
                f"days={days_list[index - 1]}->{days_list[index]}"
            )
