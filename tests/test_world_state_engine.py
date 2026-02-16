import sys
import json
import random
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
    situations_path = tmp_path / "situations.json"
    events_path = tmp_path / "events.json"
    situations_path.write_text(
        json.dumps(
            {
                "situations": [
                    {
                        "situation_id": "S-RANDOM",
                        "random_allowed": True,
                        "event_only": False,
                        "recovery_only": False,
                        "allowed_scope": "system",
                        "duration_days": {"min": 3, "max": 3},
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    events_path.write_text(
        json.dumps(
            {
                "events": [
                    {
                        "event_id": "E-T1",
                        "event_family_id": "FAMILY-1",
                        "severity_tier": 1,
                        "random_allowed": True,
                        "duration_days": {"min": 1, "max": 1},
                    }
                ]
            }
        ),
        encoding="utf-8",
    )

    def _run_once() -> tuple[list[str], list[str]]:
        engine = WorldStateEngine()
        engine.load_situation_catalog(situations_path)
        engine.load_event_catalog(events_path)
        engine.evaluate_spawn_gate(
            world_seed=1,
            current_system_id="SYS-0",
            neighbor_system_ids=["SYS-1", "SYS-2"],
            current_day=30,
            event_frequency_percent=8,
        )
        return (
            [s.situation_id for s in engine.get_active_situations("SYS-0")],
            [e.event_id for e in engine.get_active_events("SYS-0")],
        )

    assert _run_once() == _run_once()


def test_no_spawn_when_probability_roll_fails(tmp_path: Path) -> None:
    situations_path = tmp_path / "situations.json"
    events_path = tmp_path / "events.json"
    situations_path.write_text(
        json.dumps(
            {
                "situations": [
                    {
                        "situation_id": "S-RANDOM",
                        "random_allowed": True,
                        "event_only": False,
                        "recovery_only": False,
                        "allowed_scope": "system",
                        "duration_days": {"min": 3, "max": 3},
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    events_path.write_text(
        json.dumps(
            {
                "events": [
                    {
                        "event_id": "E-T1",
                        "event_family_id": "FAMILY-1",
                        "severity_tier": 1,
                        "random_allowed": True,
                        "duration_days": {"min": 1, "max": 1},
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    engine = WorldStateEngine()
    engine.load_situation_catalog(situations_path)
    engine.load_event_catalog(events_path)
    engine.evaluate_spawn_gate(
        world_seed=1,
        current_system_id="SYS-0",
        neighbor_system_ids=["SYS-1"],
        current_day=2,
        event_frequency_percent=8,
    )
    assert engine.get_active_situations("SYS-0") == []
    assert engine.get_active_events("SYS-0") == []


def test_only_one_spawn_per_day_globally(tmp_path: Path) -> None:
    situations_path = tmp_path / "situations.json"
    events_path = tmp_path / "events.json"
    situations_path.write_text(
        json.dumps(
            {
                "situations": [
                    {
                        "situation_id": "S-RANDOM",
                        "random_allowed": True,
                        "event_only": False,
                        "recovery_only": False,
                        "allowed_scope": "system",
                        "duration_days": {"min": 3, "max": 3},
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    events_path.write_text(
        json.dumps(
            {
                "events": [
                    {
                        "event_id": "E-T1",
                        "event_family_id": "FAMILY-1",
                        "severity_tier": 1,
                        "random_allowed": True,
                        "duration_days": {"min": 1, "max": 1},
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    engine = WorldStateEngine()
    engine.load_situation_catalog(situations_path)
    engine.load_event_catalog(events_path)
    engine.evaluate_spawn_gate(
        world_seed=1,
        current_system_id="SYS-0",
        neighbor_system_ids=["SYS-1", "SYS-2"],
        current_day=30,
        event_frequency_percent=8,
    )
    total = sum(len(v) for v in engine.active_situations.values()) + sum(len(v) for v in engine.active_events.values())
    assert total == 1


def test_70_30_split_is_deterministically_respected(tmp_path: Path) -> None:
    situations_path = tmp_path / "situations.json"
    events_path = tmp_path / "events.json"
    situations_path.write_text(
        json.dumps(
            {
                "situations": [
                    {
                        "situation_id": "S-RANDOM",
                        "random_allowed": True,
                        "event_only": False,
                        "recovery_only": False,
                        "allowed_scope": "system",
                        "duration_days": {"min": 3, "max": 3},
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    events_path.write_text(
        json.dumps(
            {
                "events": [
                    {
                        "event_id": "E-T1",
                        "event_family_id": "FAMILY-1",
                        "severity_tier": 1,
                        "random_allowed": True,
                        "duration_days": {"min": 1, "max": 1},
                    }
                ]
            }
        ),
        encoding="utf-8",
    )

    situation_engine = WorldStateEngine()
    situation_engine.load_situation_catalog(situations_path)
    situation_engine.load_event_catalog(events_path)
    situation_engine.evaluate_spawn_gate(
        world_seed=1,
        current_system_id="SYS-0",
        neighbor_system_ids=[],
        current_day=30,
        event_frequency_percent=8,
    )
    assert [s.situation_id for s in situation_engine.get_active_situations("SYS-0")] == ["S-RANDOM"]
    assert situation_engine.get_active_events("SYS-0") == []

    event_engine = WorldStateEngine()
    event_engine.load_situation_catalog(situations_path)
    event_engine.load_event_catalog(events_path)
    event_engine.evaluate_spawn_gate(
        world_seed=1,
        current_system_id="SYS-0",
        neighbor_system_ids=[],
        current_day=1,
        event_frequency_percent=8,
    )
    assert [e.event_id for e in event_engine.get_active_events("SYS-0")] == ["E-T1"]
    assert event_engine.get_active_situations("SYS-0") == []


def test_situation_cap_respected(tmp_path: Path) -> None:
    situations_path = tmp_path / "situations.json"
    events_path = tmp_path / "events.json"
    situations_path.write_text(
        json.dumps(
            {
                "situations": [
                    {
                        "situation_id": "S-RANDOM",
                        "random_allowed": True,
                        "event_only": False,
                        "recovery_only": False,
                        "allowed_scope": "system",
                        "duration_days": {"min": 3, "max": 3},
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    events_path.write_text(json.dumps({"events": []}), encoding="utf-8")
    engine = WorldStateEngine()
    engine.load_situation_catalog(situations_path)
    engine.load_event_catalog(events_path)
    engine.add_situation(ActiveSituation("A", "SYS-0", "system", None, 5))
    engine.add_situation(ActiveSituation("B", "SYS-0", "system", None, 5))
    engine.add_situation(ActiveSituation("C", "SYS-0", "destination", "DST-1", 5))
    engine.evaluate_spawn_gate(
        world_seed=1,
        current_system_id="SYS-0",
        neighbor_system_ids=[],
        current_day=30,
        event_frequency_percent=8,
    )
    assert len(engine.get_active_situations("SYS-0")) == 3


def test_tier_weighted_event_selection_is_deterministic(tmp_path: Path) -> None:
    situations_path = tmp_path / "situations.json"
    events_path = tmp_path / "events.json"
    situations_path.write_text(json.dumps({"situations": []}), encoding="utf-8")
    events_path.write_text(
        json.dumps(
            {
                "events": [
                    {
                        "event_id": "E-T1-A",
                        "event_family_id": "F1",
                        "severity_tier": 1,
                        "random_allowed": True,
                        "duration_days": {"min": 1, "max": 1},
                    },
                    {
                        "event_id": "E-T1-B",
                        "event_family_id": "F1",
                        "severity_tier": 1,
                        "random_allowed": True,
                        "duration_days": {"min": 1, "max": 1},
                    },
                    {
                        "event_id": "E-T5",
                        "event_family_id": "F5",
                        "severity_tier": 5,
                        "random_allowed": True,
                        "duration_days": {"min": 1, "max": 1},
                    },
                ]
            }
        ),
        encoding="utf-8",
    )

    def _run_once() -> list[str]:
        engine = WorldStateEngine()
        engine.load_situation_catalog(situations_path)
        engine.load_event_catalog(events_path)
        engine.evaluate_spawn_gate(
            world_seed=1,
            current_system_id="SYS-0",
            neighbor_system_ids=[],
            current_day=1,
            event_frequency_percent=8,
        )
        return [e.event_id for e in engine.get_active_events("SYS-0")]

    assert _run_once() == _run_once()


def test_spawn_only_evaluates_current_and_neighbors(tmp_path: Path) -> None:
    situations_path = tmp_path / "situations.json"
    events_path = tmp_path / "events.json"
    situations_path.write_text(json.dumps({"situations": []}), encoding="utf-8")
    events_path.write_text(json.dumps({"events": []}), encoding="utf-8")
    engine = WorldStateEngine()
    engine.load_situation_catalog(situations_path)
    engine.load_event_catalog(events_path)
    engine.evaluate_spawn_gate(
        world_seed=1,
        current_system_id="SYS-0",
        neighbor_system_ids=["SYS-1"],
        current_day=2,
        event_frequency_percent=8,
    )
    assert "SYS-0" in engine.active_situations
    assert "SYS-1" in engine.active_situations
    assert "SYS-2" not in engine.active_situations


def test_no_random_spawning_if_catalogs_empty(tmp_path: Path) -> None:
    situations_path = tmp_path / "situations.json"
    events_path = tmp_path / "events.json"
    situations_path.write_text(json.dumps({"situations": []}), encoding="utf-8")
    events_path.write_text(json.dumps({"events": []}), encoding="utf-8")
    engine = WorldStateEngine()
    engine.load_situation_catalog(situations_path)
    engine.load_event_catalog(events_path)
    engine.evaluate_spawn_gate(
        world_seed=1,
        current_system_id="SYS-0",
        neighbor_system_ids=["SYS-1"],
        current_day=1,
        event_frequency_percent=8,
    )
    assert engine.get_active_situations("SYS-0") == []
    assert engine.get_active_events("SYS-0") == []


def test_event_spawn_triggers_situations_up_to_cap_with_deterministic_durations(tmp_path: Path) -> None:
    situations_path = tmp_path / "situations.json"
    events_path = tmp_path / "events.json"
    situations_path.write_text(
        json.dumps(
            {
                "situations": [
                    {
                        "situation_id": "S-A",
                        "random_allowed": True,
                        "event_only": False,
                        "recovery_only": False,
                        "allowed_scope": "system",
                        "duration_days": {"min": 2, "max": 4},
                        "modifiers": [{"domain": "goods", "target_type": "ALL", "target_id": None, "modifier_type": "price_bias_percent", "modifier_value": 5}],
                    },
                    {
                        "situation_id": "S-B",
                        "random_allowed": True,
                        "event_only": False,
                        "recovery_only": False,
                        "allowed_scope": "destination",
                        "duration_days": {"min": 3, "max": 6},
                        "modifiers": [{"domain": "travel", "target_type": "ALL", "target_id": None, "modifier_type": "risk_bias_delta", "modifier_value": 1}],
                    },
                ]
            }
        ),
        encoding="utf-8",
    )
    events_path.write_text(
        json.dumps(
            {
                "events": [
                    {
                        "event_id": "E-TRIGGER",
                        "event_family_id": "F-1",
                        "severity_tier": 1,
                        "random_allowed": True,
                        "duration_days": {"min": 1, "max": 1},
                        "effects": {
                            "create_situations": [
                                {"situation_id": "S-A"},
                                {"situation_id": "S-B", "scope_type": "destination"},
                            ],
                            "scheduled_events": [],
                            "system_flag_add": [],
                            "system_flag_remove": [],
                            "modifiers": [],
                        },
                    }
                ]
            }
        ),
        encoding="utf-8",
    )

    def _run_once() -> list[tuple[str, int]]:
        engine = WorldStateEngine()
        engine.load_situation_catalog(situations_path)
        engine.load_event_catalog(events_path)
        engine.add_situation(ActiveSituation("EXISTING-1", "SYS-0", "system", None, 5))
        engine.add_situation(ActiveSituation("EXISTING-2", "SYS-0", "system", None, 5))
        engine.evaluate_spawn_gate(
            world_seed=1,
            current_system_id="SYS-0",
            neighbor_system_ids=["SYS-1"],
            current_day=1,
            event_frequency_percent=100,
        )
        rows = engine.get_active_situations("SYS-0")
        return [(row.situation_id, row.remaining_days) for row in rows]

    first = _run_once()
    second = _run_once()
    assert first == second
    engine = WorldStateEngine()
    engine.load_situation_catalog(situations_path)
    engine.load_event_catalog(events_path)
    engine.add_situation(ActiveSituation("EXISTING-1", "SYS-0", "system", None, 5))
    engine.add_situation(ActiveSituation("EXISTING-2", "SYS-0", "system", None, 5))
    engine.evaluate_spawn_gate(
        world_seed=1,
        current_system_id="SYS-0",
        neighbor_system_ids=["SYS-1"],
        current_day=1,
        event_frequency_percent=100,
    )
    assert [e.event_id for e in engine.get_active_events("SYS-0")] == ["E-TRIGGER"]
    assert len(first) == 3
    assert first[2][0] == "S-A"
    assert 2 <= first[2][1] <= 4


def test_event_schedules_follow_up_events_in_stable_order(tmp_path: Path) -> None:
    situations_path = tmp_path / "situations.json"
    events_path = tmp_path / "events.json"
    situations_path.write_text(json.dumps({"situations": []}), encoding="utf-8")
    events_path.write_text(
        json.dumps(
            {
                "events": [
                    {
                        "event_id": "E-SCHEDULE",
                        "event_family_id": "F-2",
                        "severity_tier": 1,
                        "random_allowed": True,
                        "duration_days": {"min": 1, "max": 1},
                        "effects": {
                            "create_situations": [],
                            "scheduled_events": [
                                {"event_id": "FOLLOW-1", "delay_days": 2},
                                {"event_id": "FOLLOW-2", "delay_days": 5},
                            ],
                            "system_flag_add": [],
                            "system_flag_remove": [],
                            "modifiers": [],
                        },
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    engine = WorldStateEngine()
    engine.load_situation_catalog(situations_path)
    engine.load_event_catalog(events_path)
    engine.evaluate_spawn_gate(
        world_seed=1,
        current_system_id="SYS-0",
        neighbor_system_ids=[],
        current_day=1,
        event_frequency_percent=100,
    )
    assert [(row.event_id, row.system_id, row.trigger_day) for row in engine.scheduled_events] == [
        ("FOLLOW-1", "SYS-0", 3),
        ("FOLLOW-2", "SYS-0", 6),
    ]


def test_system_flags_apply_add_then_remove_deterministically(tmp_path: Path) -> None:
    situations_path = tmp_path / "situations.json"
    events_path = tmp_path / "events.json"
    situations_path.write_text(json.dumps({"situations": []}), encoding="utf-8")
    events_path.write_text(
        json.dumps(
            {
                "events": [
                    {
                        "event_id": "E-FLAGS",
                        "event_family_id": "F-3",
                        "severity_tier": 1,
                        "random_allowed": True,
                        "duration_days": {"min": 1, "max": 1},
                        "effects": {
                            "create_situations": [],
                            "scheduled_events": [],
                            "system_flag_add": ["alpha", "beta"],
                            "system_flag_remove": ["alpha"],
                            "modifiers": [],
                        },
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    engine = WorldStateEngine()
    engine.load_situation_catalog(situations_path)
    engine.load_event_catalog(events_path)
    engine.evaluate_spawn_gate(
        world_seed=1,
        current_system_id="SYS-0",
        neighbor_system_ids=[],
        current_day=1,
        event_frequency_percent=100,
    )
    assert engine.get_system_flags("SYS-0") == ["beta"]


def test_modifiers_registry_tracks_active_and_removes_on_expiry(tmp_path: Path) -> None:
    situations_path = tmp_path / "situations.json"
    events_path = tmp_path / "events.json"
    situations_path.write_text(
        json.dumps(
            {
                "situations": [
                    {
                        "situation_id": "S-MOD",
                        "random_allowed": True,
                        "event_only": False,
                        "recovery_only": False,
                        "allowed_scope": "system",
                        "duration_days": {"min": 1, "max": 1},
                        "modifiers": [
                            {"domain": "goods", "target_type": "ALL", "target_id": None, "modifier_type": "price_bias_percent", "modifier_value": 3}
                        ],
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    events_path.write_text(
        json.dumps(
            {
                "events": [
                    {
                        "event_id": "E-MOD",
                        "event_family_id": "F-4",
                        "severity_tier": 1,
                        "random_allowed": True,
                        "duration_days": {"min": 1, "max": 1},
                        "effects": {
                            "create_situations": [{"situation_id": "S-MOD"}],
                            "scheduled_events": [],
                            "system_flag_add": [],
                            "system_flag_remove": [],
                            "modifiers": [
                                {"domain": "travel", "target_type": "ALL", "target_id": None, "modifier_type": "risk_bias_delta", "modifier_value": 1}
                            ],
                        },
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    engine = WorldStateEngine()
    engine.load_situation_catalog(situations_path)
    engine.load_event_catalog(events_path)
    engine.evaluate_spawn_gate(
        world_seed=1,
        current_system_id="SYS-0",
        neighbor_system_ids=[],
        current_day=1,
        event_frequency_percent=100,
    )

    all_mods = engine.get_active_modifiers("SYS-0")
    goods_mods = engine.get_active_modifiers("SYS-0", domain="goods")
    travel_mods = engine.get_active_modifiers("SYS-0", domain="travel")
    assert len(all_mods) == 2
    assert len(goods_mods) == 1
    assert len(travel_mods) == 1
    assert goods_mods[0]["source_type"] == "situation"
    assert travel_mods[0]["source_type"] == "event"

    engine.decrement_durations()
    engine.resolve_expired()
    assert engine.get_active_modifiers("SYS-0") == []


def test_pending_structural_mutations_are_recorded_not_applied(tmp_path: Path) -> None:
    situations_path = tmp_path / "situations.json"
    events_path = tmp_path / "events.json"
    situations_path.write_text(json.dumps({"situations": []}), encoding="utf-8")
    events_path.write_text(
        json.dumps(
            {
                "events": [
                    {
                        "event_id": "E-STRUCT",
                        "event_family_id": "F-5",
                        "severity_tier": 4,
                        "random_allowed": True,
                        "duration_days": {"min": 1, "max": 1},
                        "effects": {
                            "create_situations": [],
                            "scheduled_events": [],
                            "system_flag_add": [],
                            "system_flag_remove": [],
                            "modifiers": [],
                            "population_delta": 1,
                            "government_change": "gov_new",
                            "destroy_destination_ids": ["DST-9"],
                            "asset_destruction": {"goods_ids": ["sku_x"]},
                        },
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    engine = WorldStateEngine()
    engine.load_situation_catalog(situations_path)
    engine.load_event_catalog(events_path)
    engine.evaluate_spawn_gate(
        world_seed=1,
        current_system_id="SYS-0",
        neighbor_system_ids=[],
        current_day=1,
        event_frequency_percent=100,
    )
    assert len(engine.pending_structural_mutations) == 1
    record = engine.pending_structural_mutations[0]
    assert record["system_id"] == "SYS-0"
    assert record["source_event_id"] == "E-STRUCT"
    assert record["mutation_payload"]["population_delta"] == 1
    assert record["mutation_payload"]["government_change"] == "gov_new"


def test_apply_event_effects_raises_when_event_missing() -> None:
    engine = WorldStateEngine()
    engine.load_situation_catalog(catalog_path=Path(__file__).resolve().parents[1] / "data" / "situations.json")
    with pytest.raises(ValueError):
        engine.apply_event_effects(
            world_seed=1,
            current_day=1,
            target_system_id="SYS-0",
            event_id="MISSING-EVENT",
            rng=random.Random(1),
        )
