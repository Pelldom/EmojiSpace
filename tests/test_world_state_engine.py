import sys
import json
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"
sys.path.insert(0, str(SRC_ROOT))

from world_state_engine import (  # noqa: E402
    ActiveEvent,
    ActiveSituation,
    ScheduledEvent,
    WorldStateEngine,
)


def test_register_system_initializes_containers() -> None:
    engine = WorldStateEngine()
    engine.register_system("SYS-1")
    assert engine.get_active_situations("SYS-1") == []
    assert engine.get_active_events("SYS-1") == []


def test_add_up_to_three_situations_and_fourth_raises() -> None:
    engine = WorldStateEngine()
    engine.register_system("SYS-1")
    engine.add_situation(
        ActiveSituation(
            situation_id="S1",
            system_id="SYS-1",
            scope="system",
            target_id=None,
            remaining_days=3,
        )
    )
    engine.add_situation(
        ActiveSituation(
            situation_id="S2",
            system_id="SYS-1",
            scope="destination",
            target_id="DST-1",
            remaining_days=3,
        )
    )
    engine.add_situation(
        ActiveSituation(
            situation_id="S3",
            system_id="SYS-1",
            scope="destination",
            target_id="DST-2",
            remaining_days=3,
        )
    )
    with pytest.raises(ValueError):
        engine.add_situation(
            ActiveSituation(
                situation_id="S4",
                system_id="SYS-1",
                scope="system",
                target_id=None,
                remaining_days=3,
            )
        )


def test_decrement_durations_clamps_at_zero() -> None:
    engine = WorldStateEngine()
    engine.add_situation(
        ActiveSituation(
            situation_id="S1",
            system_id="SYS-1",
            scope="system",
            target_id=None,
            remaining_days=1,
        )
    )
    engine.add_event(
        ActiveEvent(
            event_id="E1",
            event_family_id=None,
            system_id="SYS-1",
            remaining_days=2,
        )
    )
    engine.decrement_durations()
    engine.decrement_durations()
    assert engine.get_active_situations("SYS-1")[0].remaining_days == 0
    assert engine.get_active_events("SYS-1")[0].remaining_days == 0


def test_resolve_expired_removes_zero_or_less_remaining_days() -> None:
    engine = WorldStateEngine()
    engine.add_situation(
        ActiveSituation(
            situation_id="S-EXPIRE",
            system_id="SYS-1",
            scope="system",
            target_id=None,
            remaining_days=0,
        )
    )
    engine.add_situation(
        ActiveSituation(
            situation_id="S-ACTIVE",
            system_id="SYS-1",
            scope="system",
            target_id=None,
            remaining_days=2,
        )
    )
    engine.add_event(
        ActiveEvent(
            event_id="E-EXPIRE",
            event_family_id="F1",
            system_id="SYS-1",
            remaining_days=0,
        )
    )
    engine.add_event(
        ActiveEvent(
            event_id="E-ACTIVE",
            event_family_id="F1",
            system_id="SYS-1",
            remaining_days=2,
        )
    )

    engine.resolve_expired()

    remaining_situations = engine.get_active_situations("SYS-1")
    remaining_events = engine.get_active_events("SYS-1")
    assert [entry.situation_id for entry in remaining_situations] == ["S-ACTIVE"]
    assert [entry.event_id for entry in remaining_events] == ["E-ACTIVE"]


def test_events_and_situations_tracked_separately_and_schedule_list_kept() -> None:
    engine = WorldStateEngine()
    engine.add_situation(
        ActiveSituation(
            situation_id="S1",
            system_id="SYS-1",
            scope="system",
            target_id=None,
            remaining_days=3,
        )
    )
    engine.add_event(
        ActiveEvent(
            event_id="E1",
            event_family_id="FAMILY-1",
            system_id="SYS-1",
            remaining_days=5,
        )
    )
    engine.schedule_event(ScheduledEvent(event_id="E2", system_id="SYS-1", trigger_day=8))

    assert len(engine.get_active_situations("SYS-1")) == 1
    assert len(engine.get_active_events("SYS-1")) == 1
    assert len(engine.scheduled_events) == 1
    assert engine.scheduled_events[0].event_id == "E2"


def test_deterministic_spawn_behavior_is_identical_across_two_runs(tmp_path: Path) -> None:
    catalog_path = tmp_path / "situations.json"
    catalog_path.write_text(
        json.dumps(
            [
                {
                    "situation_id": "S-RANDOM",
                    "random_allowed": True,
                    "event_only": False,
                    "recovery_only": False,
                    "allowed_scope": "system",
                    "duration_days": 4,
                }
            ]
        ),
        encoding="utf-8",
    )

    def _run() -> dict[str, list[str]]:
        engine = WorldStateEngine()
        engine.load_situation_catalog(catalog_path)
        engine.evaluate_situation_spawn(
            current_system_id="SYS-0",
            neighbor_system_ids=["SYS-1", "SYS-2"],
            current_day=10,
            world_seed=1234,
        )
        return {
            "SYS-0": [s.situation_id for s in engine.get_active_situations("SYS-0")],
            "SYS-1": [s.situation_id for s in engine.get_active_situations("SYS-1")],
            "SYS-2": [s.situation_id for s in engine.get_active_situations("SYS-2")],
        }

    assert _run() == _run()


def test_no_spawn_when_random_allowed_empty(tmp_path: Path) -> None:
    catalog_path = tmp_path / "situations.json"
    catalog_path.write_text(
        json.dumps(
            [
                {
                    "situation_id": "S-NONRANDOM",
                    "random_allowed": False,
                    "event_only": False,
                    "recovery_only": False,
                    "allowed_scope": "system",
                    "duration_days": 4,
                }
            ]
        ),
        encoding="utf-8",
    )
    engine = WorldStateEngine()
    engine.load_situation_catalog(catalog_path)
    engine.evaluate_situation_spawn(
        current_system_id="SYS-0",
        neighbor_system_ids=["SYS-1"],
        current_day=10,
        world_seed=1234,
    )
    assert engine.get_active_situations("SYS-0") == []
    assert engine.get_active_situations("SYS-1") == []


def test_no_spawn_when_system_is_at_cap(tmp_path: Path) -> None:
    catalog_path = tmp_path / "situations.json"
    catalog_path.write_text(
        json.dumps(
            [
                {
                    "situation_id": "S-RANDOM",
                    "random_allowed": True,
                    "event_only": False,
                    "recovery_only": False,
                    "allowed_scope": "system",
                    "duration_days": 4,
                }
            ]
        ),
        encoding="utf-8",
    )
    engine = WorldStateEngine()
    engine.load_situation_catalog(catalog_path)
    engine.add_situation(ActiveSituation("A", "SYS-0", "system", None, 5))
    engine.add_situation(ActiveSituation("B", "SYS-0", "system", None, 5))
    engine.add_situation(ActiveSituation("C", "SYS-0", "destination", "DST-1", 5))

    engine.evaluate_situation_spawn(
        current_system_id="SYS-0",
        neighbor_system_ids=[],
        current_day=10,
        world_seed=1234,
    )
    assert len(engine.get_active_situations("SYS-0")) == 3


def test_only_current_and_neighbors_are_evaluated(tmp_path: Path) -> None:
    catalog_path = tmp_path / "situations.json"
    catalog_path.write_text(
        json.dumps(
            [
                {
                    "situation_id": "S-RANDOM",
                    "random_allowed": True,
                    "event_only": False,
                    "recovery_only": False,
                    "allowed_scope": "system",
                    "duration_days": 4,
                }
            ]
        ),
        encoding="utf-8",
    )
    engine = WorldStateEngine()
    engine.load_situation_catalog(catalog_path)
    engine.evaluate_situation_spawn(
        current_system_id="SYS-0",
        neighbor_system_ids=["SYS-1"],
        current_day=10,
        world_seed=1234,
    )
    assert "SYS-0" in engine.active_situations
    assert "SYS-1" in engine.active_situations
    assert "SYS-2" not in engine.active_situations


def test_event_only_situations_never_spawn_randomly(tmp_path: Path) -> None:
    catalog_path = tmp_path / "situations.json"
    catalog_path.write_text(
        json.dumps(
            [
                {
                    "situation_id": "S-EVENT-ONLY",
                    "random_allowed": True,
                    "event_only": True,
                    "recovery_only": False,
                    "allowed_scope": "system",
                    "duration_days": 4,
                }
            ]
        ),
        encoding="utf-8",
    )
    engine = WorldStateEngine()
    engine.load_situation_catalog(catalog_path)
    engine.evaluate_situation_spawn(
        current_system_id="SYS-0",
        neighbor_system_ids=["SYS-1"],
        current_day=10,
        world_seed=1234,
    )
    assert engine.get_active_situations("SYS-0") == []
    assert engine.get_active_situations("SYS-1") == []
