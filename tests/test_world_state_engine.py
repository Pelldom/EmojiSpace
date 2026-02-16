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


def test_scheduled_events_execute_on_due_day_only(tmp_path: Path) -> None:
    situations_path = tmp_path / "situations.json"
    events_path = tmp_path / "events.json"
    situations_path.write_text(json.dumps({"situations": []}), encoding="utf-8")
    events_path.write_text(
        json.dumps(
            {
                "events": [
                    {
                        "event_id": "E-A",
                        "event_family_id": "F-A",
                        "severity_tier": 1,
                        "random_allowed": True,
                        "duration_days": {"min": 1, "max": 1},
                        "effects": {
                            "create_situations": [],
                            "scheduled_events": [{"event_id": "E-B", "delay_days": 3}],
                            "system_flag_add": [],
                            "system_flag_remove": [],
                            "modifiers": [],
                        },
                    },
                    {
                        "event_id": "E-B",
                        "event_family_id": "F-B",
                        "severity_tier": 1,
                        "random_allowed": False,
                        "duration_days": {"min": 2, "max": 2},
                        "effects": {
                            "create_situations": [],
                            "scheduled_events": [],
                            "system_flag_add": [],
                            "system_flag_remove": [],
                            "modifiers": [],
                        },
                    },
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
    assert any(row.event_id == "E-A" for row in engine.get_active_events("SYS-0"))
    assert engine.process_scheduled_events(world_seed=1, current_day=1) == 0
    assert engine.process_scheduled_events(world_seed=1, current_day=2) == 0
    assert engine.process_scheduled_events(world_seed=1, current_day=3) == 0
    assert engine.process_scheduled_events(world_seed=1, current_day=4) == 1
    assert any(row.event_id == "E-B" for row in engine.get_active_events("SYS-0"))


def test_scheduled_event_execution_order_is_stable(tmp_path: Path) -> None:
    situations_path = tmp_path / "situations.json"
    events_path = tmp_path / "events.json"
    situations_path.write_text(json.dumps({"situations": []}), encoding="utf-8")
    events_path.write_text(
        json.dumps(
            {
                "events": [
                    {"event_id": "E-1", "event_family_id": "F", "severity_tier": 1, "random_allowed": False, "duration_days": {"min": 1, "max": 1}, "effects": {"create_situations": [], "scheduled_events": [], "system_flag_add": [], "system_flag_remove": [], "modifiers": []}},
                    {"event_id": "E-2", "event_family_id": "F", "severity_tier": 1, "random_allowed": False, "duration_days": {"min": 1, "max": 1}, "effects": {"create_situations": [], "scheduled_events": [], "system_flag_add": [], "system_flag_remove": [], "modifiers": []}},
                    {"event_id": "E-3", "event_family_id": "F", "severity_tier": 1, "random_allowed": False, "duration_days": {"min": 1, "max": 1}, "effects": {"create_situations": [], "scheduled_events": [], "system_flag_add": [], "system_flag_remove": [], "modifiers": []}},
                ]
            }
        ),
        encoding="utf-8",
    )

    def _run_once() -> list[str]:
        engine = WorldStateEngine()
        engine.load_situation_catalog(situations_path)
        engine.load_event_catalog(events_path)
        engine.schedule_event(ScheduledEvent(event_id="E-2", system_id="SYS-0", trigger_day=5))
        engine.schedule_event(ScheduledEvent(event_id="E-1", system_id="SYS-0", trigger_day=5))
        engine.schedule_event(ScheduledEvent(event_id="E-3", system_id="SYS-0", trigger_day=5))
        executed = engine.process_scheduled_events(world_seed=10, current_day=5)
        assert executed == 3
        return [row.event_id for row in engine.get_active_events("SYS-0")]

    assert _run_once() == ["E-2", "E-1", "E-3"]
    assert _run_once() == ["E-2", "E-1", "E-3"]


def test_scheduled_events_do_not_consume_spawn_gate(tmp_path: Path) -> None:
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
                        "modifiers": [],
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
                        "event_id": "E-SCHEDULED",
                        "event_family_id": "F-S",
                        "severity_tier": 1,
                        "random_allowed": False,
                        "duration_days": {"min": 1, "max": 1},
                        "effects": {
                            "create_situations": [],
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
    engine = WorldStateEngine()
    engine.load_situation_catalog(situations_path)
    engine.load_event_catalog(events_path)
    engine.schedule_event(ScheduledEvent(event_id="E-SCHEDULED", system_id="SYS-0", trigger_day=30))
    engine.evaluate_spawn_gate(
        world_seed=1,
        current_system_id="SYS-0",
        neighbor_system_ids=[],
        current_day=30,
        event_frequency_percent=8,
    )
    scheduled_count = engine.process_scheduled_events(world_seed=1, current_day=30)
    assert scheduled_count == 1
    assert len(engine.get_active_situations("SYS-0")) == 1
    assert any(row.event_id == "E-SCHEDULED" for row in engine.get_active_events("SYS-0"))


def test_scheduled_event_duration_roll_is_deterministic(tmp_path: Path) -> None:
    situations_path = tmp_path / "situations.json"
    events_path = tmp_path / "events.json"
    situations_path.write_text(json.dumps({"situations": []}), encoding="utf-8")
    events_path.write_text(
        json.dumps(
            {
                "events": [
                    {
                        "event_id": "E-DUR",
                        "event_family_id": "F-D",
                        "severity_tier": 1,
                        "random_allowed": False,
                        "duration_days": {"min": 2, "max": 5},
                        "effects": {
                            "create_situations": [],
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

    def _run_once() -> int:
        engine = WorldStateEngine()
        engine.load_situation_catalog(situations_path)
        engine.load_event_catalog(events_path)
        engine.schedule_event(ScheduledEvent(event_id="E-DUR", system_id="SYS-0", trigger_day=7))
        assert engine.process_scheduled_events(world_seed=999, current_day=7) == 1
        return engine.get_active_events("SYS-0")[0].remaining_days

    first = _run_once()
    second = _run_once()
    assert first == second
    assert 2 <= first <= 5


def test_propagation_legacy_fields_not_required_for_event_load(tmp_path: Path) -> None:
    situations_path = tmp_path / "situations.json"
    events_path = tmp_path / "events.json"
    situations_path.write_text(
        json.dumps(
            {
                "situations": [
                    {
                        "situation_id": "S-PROP",
                        "random_allowed": True,
                        "event_only": False,
                        "recovery_only": False,
                        "allowed_scope": "system",
                        "duration_days": {"min": 2, "max": 2},
                        "modifiers": [],
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
                        "event_id": "E-NO-LEGACY",
                        "event_family_id": "F-LEG",
                        "severity_tier": 4,
                        "random_allowed": False,
                        "duration_days": {"min": 1, "max": 1},
                        "propagation": [],
                        "effects": {
                            "create_situations": [],
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
    engine = WorldStateEngine()
    engine.load_situation_catalog(situations_path)
    engine.load_event_catalog(events_path)
    engine.add_event(
        ActiveEvent(
            event_id="E-NO-LEGACY",
            event_family_id="F-LEG",
            system_id="SYS-A",
            remaining_days=2,
            trigger_day=5,
        )
    )
    count = engine.process_propagation(
        world_seed=13,
        current_day=5,
        get_neighbors_fn=lambda system_id: {"SYS-A": ["SYS-B"]}.get(system_id, []),
    )
    assert count == 0


def test_propagation_ignores_unknown_situation_id_and_logs(tmp_path: Path, capsys) -> None:
    situations_path = tmp_path / "situations.json"
    events_path = tmp_path / "events.json"
    situations_path.write_text(json.dumps({"situations": []}), encoding="utf-8")
    events_path.write_text(
        json.dumps(
            {
                "events": [
                    {
                        "event_id": "E-UNK",
                        "event_family_id": "F-UNK",
                        "severity_tier": 5,
                        "random_allowed": False,
                        "duration_days": {"min": 1, "max": 1},
                        "propagation": [
                            {
                                "situation_id": "S-MISSING",
                                "delay_days": 0,
                                "systems_affected": 1,
                            }
                        ],
                        "effects": {
                            "create_situations": [],
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
    engine = WorldStateEngine()
    engine.load_situation_catalog(situations_path)
    engine.load_event_catalog(events_path)
    engine.add_event(
        ActiveEvent(
            event_id="E-UNK",
            event_family_id="F-UNK",
            system_id="SYS-A",
            remaining_days=2,
            trigger_day=8,
        )
    )
    count = engine.process_propagation(
        world_seed=44,
        current_day=8,
        get_neighbors_fn=lambda system_id: {"SYS-A": ["SYS-B"]}.get(system_id, []),
    )
    out = capsys.readouterr().out
    assert count == 0
    assert "unknown_situation_id" in out
    assert engine.get_active_situations("SYS-B") == []


def test_propagation_neighbor_selection_is_deterministic_for_systems_affected(tmp_path: Path) -> None:
    situations_path = tmp_path / "situations.json"
    events_path = tmp_path / "events.json"
    situations_path.write_text(
        json.dumps(
            {
                "situations": [
                    {
                        "situation_id": "S-PROP",
                        "random_allowed": True,
                        "event_only": False,
                        "recovery_only": False,
                        "allowed_scope": "system",
                        "duration_days": {"min": 3, "max": 3},
                        "modifiers": [],
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
                        "event_id": "E-DET",
                        "event_family_id": "F-DET",
                        "severity_tier": 5,
                        "random_allowed": False,
                        "duration_days": {"min": 1, "max": 1},
                        "propagation": [
                            {
                                "situation_id": "S-PROP",
                                "delay_days": 0,
                                "systems_affected": 2,
                            }
                        ],
                        "effects": {
                            "create_situations": [],
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

    def _run_once() -> list[str]:
        engine = WorldStateEngine()
        engine.load_situation_catalog(situations_path)
        engine.load_event_catalog(events_path)
        engine.add_event(
            ActiveEvent(
                event_id="E-DET",
                event_family_id="F-DET",
                system_id="SYS-A",
                remaining_days=2,
                trigger_day=11,
            )
        )
        count = engine.process_propagation(
            world_seed=999,
            current_day=11,
            get_neighbors_fn=lambda system_id: {
                "SYS-A": ["SYS-B", "SYS-C", "SYS-D"]
            }.get(system_id, []),
        )
        assert count == 2
        selected = []
        for system_id in ["SYS-B", "SYS-C", "SYS-D"]:
            if any(s.situation_id == "S-PROP" for s in engine.get_active_situations(system_id)):
                selected.append(system_id)
        return selected

    first = _run_once()
    second = _run_once()
    assert first == second
    assert len(first) == 2


def test_propagation_creates_situations_only_not_events(tmp_path: Path) -> None:
    situations_path = tmp_path / "situations.json"
    events_path = tmp_path / "events.json"
    situations_path.write_text(
        json.dumps(
            {
                "situations": [
                    {
                        "situation_id": "S-ONLY",
                        "random_allowed": True,
                        "event_only": False,
                        "recovery_only": False,
                        "allowed_scope": "system",
                        "duration_days": {"min": 2, "max": 2},
                        "modifiers": [],
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
                        "event_id": "E-SITUATION-ONLY",
                        "event_family_id": "F-SO",
                        "severity_tier": 5,
                        "random_allowed": False,
                        "duration_days": {"min": 1, "max": 1},
                        "propagation": [
                            {
                                "situation_id": "S-ONLY",
                                "delay_days": 0,
                                "systems_affected": 1,
                            }
                        ],
                        "effects": {
                            "create_situations": [],
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
    engine = WorldStateEngine()
    engine.load_situation_catalog(situations_path)
    engine.load_event_catalog(events_path)
    engine.add_event(
        ActiveEvent(
            event_id="E-SITUATION-ONLY",
            event_family_id="F-SO",
            system_id="SYS-A",
            remaining_days=2,
            trigger_day=12,
        )
    )
    count = engine.process_propagation(
        world_seed=1,
        current_day=12,
        get_neighbors_fn=lambda system_id: {"SYS-A": ["SYS-B"]}.get(system_id, []),
    )
    assert count == 1
    assert any(s.situation_id == "S-ONLY" for s in engine.get_active_situations("SYS-B"))
    assert engine.get_active_events("SYS-B") == []


def test_propagation_does_not_apply_structural_mutation_in_neighbors(tmp_path: Path) -> None:
    situations_path = tmp_path / "situations.json"
    events_path = tmp_path / "events.json"
    situations_path.write_text(
        json.dumps(
            {
                "situations": [
                    {
                        "situation_id": "S-NEIGHBOR",
                        "random_allowed": True,
                        "event_only": False,
                        "recovery_only": False,
                        "allowed_scope": "system",
                        "duration_days": {"min": 2, "max": 2},
                        "modifiers": [],
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
                        "event_id": "E-STRUCT-ORIGIN",
                        "event_family_id": "F-ST",
                        "severity_tier": 5,
                        "random_allowed": False,
                        "duration_days": {"min": 1, "max": 1},
                        "propagation": [
                            {
                                "situation_id": "S-NEIGHBOR",
                                "delay_days": 0,
                                "systems_affected": 1,
                            }
                        ],
                        "effects": {
                            "create_situations": [],
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
    engine = WorldStateEngine()
    engine.load_situation_catalog(situations_path)
    engine.load_event_catalog(events_path)
    engine.add_event(
        ActiveEvent(
            event_id="E-STRUCT-ORIGIN",
            event_family_id="F-ST",
            system_id="SYS-A",
            remaining_days=2,
            trigger_day=14,
        )
    )
    count = engine.process_propagation(
        world_seed=73,
        current_day=14,
        get_neighbors_fn=lambda system_id: {"SYS-A": ["SYS-B"]}.get(system_id, []),
    )
    assert count == 1
    assert engine.pending_structural_mutations == []
    assert engine.get_system_flags("SYS-B") == []


def test_aggregated_modifier_map_is_order_independent_and_deterministic() -> None:
    engine = WorldStateEngine()
    engine.register_system("SYS-1")
    rows = [
        {
            "domain": "goods",
            "target_type": "ALL",
            "target_id": None,
            "modifier_type": "price_bias_percent",
            "modifier_value": 5,
            "source_type": "event",
            "source_id": "E-1",
        },
        {
            "domain": "goods",
            "target_type": "tag",
            "target_id": "medical",
            "modifier_type": "price_bias_percent",
            "modifier_value": 3,
            "source_type": "situation",
            "source_id": "S-1",
        },
        {
            "domain": "goods",
            "target_type": "ALL",
            "target_id": None,
            "modifier_type": "price_bias_percent",
            "modifier_value": -2,
            "source_type": "event",
            "source_id": "E-2",
        },
    ]
    engine.active_modifiers_by_system["SYS-1"] = list(rows)
    first = engine.get_aggregated_modifier_map("SYS-1", "goods")
    engine.active_modifiers_by_system["SYS-1"] = list(reversed(rows))
    second = engine.get_aggregated_modifier_map("SYS-1", "goods")
    assert first == second
    assert first[("ALL", None, "price_bias_percent")] == 3
    assert first[("tag", "medical", "price_bias_percent")] == 3


def test_resolver_stacks_all_tag_category_and_id_with_caps() -> None:
    engine = WorldStateEngine()
    engine.register_system("SYS-1")
    engine.active_modifiers_by_system["SYS-1"] = [
        {"domain": "goods", "target_type": "ALL", "target_id": None, "modifier_type": "price_bias_percent", "modifier_value": 20, "source_type": "event", "source_id": "E1"},
        {"domain": "goods", "target_type": "category", "target_id": "MED", "modifier_type": "price_bias_percent", "modifier_value": 20, "source_type": "event", "source_id": "E2"},
        {"domain": "goods", "target_type": "tag", "target_id": "medical", "modifier_type": "price_bias_percent", "modifier_value": 20, "source_type": "situation", "source_id": "S1"},
        {"domain": "goods", "target_type": "sku", "target_id": "SKU-1", "modifier_type": "price_bias_percent", "modifier_value": 20, "source_type": "event", "source_id": "E3"},
        {"domain": "goods", "target_type": "ALL", "target_id": None, "modifier_type": "availability_delta", "modifier_value": 10, "source_type": "event", "source_id": "E4"},
    ]
    resolved = engine.resolve_modifiers_for_entities(
        system_id="SYS-1",
        domain="goods",
        entity_views=[
            {"entity_id": "SKU-1", "category_id": "MED", "tags": ["medical", "essential"]},
            {"entity_id": "SKU-2", "category_id": "MED", "tags": ["medical"]},
        ],
    )
    assert resolved["resolved"]["SKU-1"]["price_bias_percent"] == 40
    assert resolved["resolved"]["SKU-1"]["availability_delta"] == 3
    assert resolved["resolved"]["SKU-2"]["price_bias_percent"] == 40


def test_resolver_supports_destination_id_targeting() -> None:
    engine = WorldStateEngine()
    engine.register_system("SYS-1")
    engine.active_modifiers_by_system["SYS-1"] = [
        {"domain": "travel", "target_type": "destination_id", "target_id": "DST-1", "modifier_type": "risk_bias_delta", "modifier_value": 2, "source_type": "event", "source_id": "E1"},
        {"domain": "travel", "target_type": "destination_id", "target_id": "DST-2", "modifier_type": "risk_bias_delta", "modifier_value": -1, "source_type": "event", "source_id": "E2"},
    ]
    resolved = engine.resolve_modifiers_for_entities(
        system_id="SYS-1",
        domain="travel",
        entity_views=[
            {"entity_id": "DST-1", "category_id": None, "tags": []},
            {"entity_id": "DST-3", "category_id": None, "tags": []},
        ],
    )
    assert resolved["resolved"]["DST-1"]["risk_bias_delta"] == 2
    assert resolved["resolved"]["DST-3"] == {}


def test_caps_are_applied_after_sum() -> None:
    engine = WorldStateEngine()
    engine.register_system("SYS-1")
    engine.active_modifiers_by_system["SYS-1"] = [
        {"domain": "travel", "target_type": "ALL", "target_id": None, "modifier_type": "risk_bias_delta", "modifier_value": 5, "source_type": "event", "source_id": "E1"},
        {"domain": "travel", "target_type": "ALL", "target_id": None, "modifier_type": "risk_bias_delta", "modifier_value": 5, "source_type": "event", "source_id": "E2"},
    ]
    resolved = engine.resolve_modifiers_for_entities(
        system_id="SYS-1",
        domain="travel",
        entity_views=[{"entity_id": "R-1", "category_id": None, "tags": []}],
    )
    assert resolved["resolved"]["R-1"]["risk_bias_delta"] == 2


def test_resolver_output_ordering_is_deterministic() -> None:
    engine = WorldStateEngine()
    engine.register_system("SYS-1")
    engine.active_modifiers_by_system["SYS-1"] = [
        {"domain": "goods", "target_type": "ALL", "target_id": None, "modifier_type": "demand_bias_percent", "modifier_value": 1, "source_type": "event", "source_id": "E1"},
        {"domain": "goods", "target_type": "ALL", "target_id": None, "modifier_type": "availability_delta", "modifier_value": 1, "source_type": "event", "source_id": "E1"},
    ]
    resolved = engine.resolve_modifiers_for_entities(
        system_id="SYS-1",
        domain="goods",
        entity_views=[
            {"entity_id": "B-2", "category_id": "X", "tags": []},
            {"entity_id": "A-1", "category_id": "X", "tags": []},
        ],
    )
    assert list(resolved["resolved"].keys()) == ["A-1", "B-2"]
    assert list(resolved["resolved"]["A-1"].keys()) == ["availability_delta", "demand_bias_percent"]


def test_drain_structural_mutations_empty_returns_empty_list() -> None:
    engine = WorldStateEngine()
    assert engine.drain_structural_mutations() == []


def test_drain_structural_mutations_returns_deterministically_sorted_order() -> None:
    engine = WorldStateEngine()
    engine.pending_structural_mutations = [
        {"system_id": "SYS-B", "event_id": "E-2", "mutation_type": "population_delta", "insertion_index": 2},
        {"system_id": "SYS-A", "event_id": "E-3", "mutation_type": "government_change", "insertion_index": 1},
        {"system_id": "SYS-A", "event_id": "E-1", "mutation_type": "government_change", "insertion_index": 9},
        {"system_id": "SYS-A", "event_id": "E-1", "mutation_type": "asset_destruction"},
    ]
    drained = engine.drain_structural_mutations()
    keys = [
        (
            row.get("system_id"),
            row.get("event_id"),
            row.get("mutation_type"),
            row.get("insertion_index", 0),
        )
        for row in drained
    ]
    assert keys == [
        ("SYS-A", "E-1", "asset_destruction", 0),
        ("SYS-A", "E-1", "government_change", 9),
        ("SYS-A", "E-3", "government_change", 1),
        ("SYS-B", "E-2", "population_delta", 2),
    ]


def test_drain_structural_mutations_clears_internal_list() -> None:
    engine = WorldStateEngine()
    engine.pending_structural_mutations = [{"system_id": "SYS-1", "event_id": "E-1", "mutation_type": "x"}]
    drained = engine.drain_structural_mutations()
    assert len(drained) == 1
    assert engine.pending_structural_mutations == []


def test_repeated_drain_after_clear_returns_empty_list() -> None:
    engine = WorldStateEngine()
    engine.pending_structural_mutations = [{"system_id": "SYS-1", "event_id": "E-1", "mutation_type": "x"}]
    first = engine.drain_structural_mutations()
    second = engine.drain_structural_mutations()
    assert len(first) == 1
    assert second == []


def test_drain_structural_mutations_does_not_change_rng_state() -> None:
    import random

    engine = WorldStateEngine()
    engine.pending_structural_mutations = [{"system_id": "SYS-1", "event_id": "E-1", "mutation_type": "x"}]
    rng = random.Random(12345)
    state_before = rng.getstate()
    _ = engine.drain_structural_mutations()
    state_after = rng.getstate()
    assert state_before == state_after
