import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"
sys.path.insert(0, str(SRC_ROOT))

import encounter_generator as eg  # noqa: E402
from world_state_engine import WorldStateEngine  # noqa: E402


def _patched_encounter_types():
    return [
        {
            "subtype_id": "pirate_raider",
            "emoji": "pirate_placeholder",
            "posture": "hostile",
            "initiative": "npc",
            "allows_betrayal": True,
            "base_weight": 10,
            "allowed_TR_range": {"min": 1, "max": 1},
            "participant_templates": [],
            "default_flags": ["piracy_context", "criminal_actor", "salvage_possible"],
            "reward_profiles": [],
            "npc_response_profile": {},
        },
        {
            "subtype_id": "customs_patrol",
            "emoji": "authority_placeholder",
            "posture": "authority",
            "initiative": "npc",
            "allows_betrayal": False,
            "base_weight": 10,
            "allowed_TR_range": {"min": 1, "max": 1},
            "participant_templates": [],
            "default_flags": ["authority_actor"],
            "reward_profiles": [],
            "npc_response_profile": {},
        },
    ]


def _patched_governments():
    return {"gov": {"id": "gov", "enforcement_strength": 0}}


def test_baseline_unchanged_when_world_state_none(monkeypatch) -> None:
    monkeypatch.setattr(eg, "load_encounter_types", _patched_encounter_types)
    monkeypatch.setattr(eg, "load_governments", _patched_governments)
    subtype_a, _ = eg.select_subtype(
        encounter_id="ENC-A",
        world_seed="SEED-1",
        system_government_id="gov",
        active_situations=[],
        travel_context=None,
    )
    subtype_b, _ = eg.select_subtype(
        encounter_id="ENC-A",
        world_seed="SEED-1",
        system_government_id="gov",
        active_situations=[],
        travel_context=None,
        world_state_engine=None,
        current_system_id=None,
    )
    assert subtype_a["subtype_id"] == subtype_b["subtype_id"]


def test_pirate_percent_bias_increases_pirate_weight(monkeypatch) -> None:
    monkeypatch.setattr(eg, "load_encounter_types", _patched_encounter_types)
    monkeypatch.setattr(eg, "load_governments", _patched_governments)
    ws = WorldStateEngine()
    ws.register_system("SYS-1")
    ws.active_modifiers_by_system["SYS-1"] = [
        {
            "domain": "encounters",
            "target_type": "tag",
            "target_id": "pirate",
            "modifier_type": "pirate_encounter_percent",
            "modifier_value": 50,
            "source_type": "event",
            "source_id": "E-1",
        }
    ]
    _, log = eg.select_subtype(
        encounter_id="ENC-B",
        world_seed="SEED-2",
        system_government_id="gov",
        active_situations=[],
        world_state_engine=ws,
        current_system_id="SYS-1",
    )
    by_id = {entry["subtype_id"]: entry for entry in log["candidate_weights"]}
    assert by_id["pirate_raider"]["final_weight"] == 15
    assert by_id["customs_patrol"]["final_weight"] == 10


def test_minus_100_pirate_bias_excludes_pirates(monkeypatch) -> None:
    monkeypatch.setattr(eg, "load_encounter_types", _patched_encounter_types)
    monkeypatch.setattr(eg, "load_governments", _patched_governments)
    ws = WorldStateEngine()
    ws.register_system("SYS-1")
    ws.active_modifiers_by_system["SYS-1"] = [
        {
            "domain": "encounters",
            "target_type": "tag",
            "target_id": "pirate",
            "modifier_type": "pirate_encounter_percent",
            "modifier_value": -100,
            "source_type": "event",
            "source_id": "E-2",
        }
    ]
    subtype, log = eg.select_subtype(
        encounter_id="ENC-C",
        world_seed="SEED-3",
        system_government_id="gov",
        active_situations=[],
        world_state_engine=ws,
        current_system_id="SYS-1",
    )
    by_id = {entry["subtype_id"]: entry for entry in log["candidate_weights"]}
    assert by_id["pirate_raider"]["final_weight"] == 0
    assert subtype["subtype_id"] != "pirate_raider"


def test_determinism_with_modifiers(monkeypatch) -> None:
    monkeypatch.setattr(eg, "load_encounter_types", _patched_encounter_types)
    monkeypatch.setattr(eg, "load_governments", _patched_governments)
    ws = WorldStateEngine()
    ws.register_system("SYS-1")
    ws.active_modifiers_by_system["SYS-1"] = [
        {
            "domain": "encounters",
            "target_type": "tag",
            "target_id": "hostile",
            "modifier_type": "hostile_bias_percent",
            "modifier_value": 40,
            "source_type": "event",
            "source_id": "E-3",
        }
    ]

    def _run_once():
        subtype, log = eg.select_subtype(
            encounter_id="ENC-D",
            world_seed="SEED-4",
            system_government_id="gov",
            active_situations=[],
            world_state_engine=ws,
            current_system_id="SYS-1",
        )
        return subtype["subtype_id"], log["eligible_weights"], log["selected_subtype_id"]

    assert _run_once() == _run_once()


def _patched_encounter_types_with_subtype_weight():
    # Same as _patched_encounter_types but with explicit weight=1 to verify no behavior change.
    return [
        {
            "subtype_id": "pirate_raider",
            "emoji": "pirate_placeholder",
            "posture": "hostile",
            "initiative": "npc",
            "allows_betrayal": True,
            "base_weight": 10,
            "allowed_TR_range": {"min": 1, "max": 1},
            "participant_templates": [],
            "default_flags": ["piracy_context", "criminal_actor", "salvage_possible"],
            "reward_profiles": [],
            "npc_response_profile": {},
            "weight": 1,
        },
        {
            "subtype_id": "customs_patrol",
            "emoji": "authority_placeholder",
            "posture": "authority",
            "initiative": "npc",
            "allows_betrayal": False,
            "base_weight": 10,
            "allowed_TR_range": {"min": 1, "max": 1},
            "participant_templates": [],
            "default_flags": ["authority_actor"],
            "reward_profiles": [],
            "npc_response_profile": {},
            "weight": 1,
        },
    ]


def test_explicit_weight_one_matches_baseline(monkeypatch) -> None:
    # Ensure adding weight=1 does not change deterministic selection or eligible weights.
    monkeypatch.setattr(eg, "load_governments", _patched_governments)
    # Baseline without explicit weight
    monkeypatch.setattr(eg, "load_encounter_types", _patched_encounter_types)
    subtype_base, log_base = eg.select_subtype(
        encounter_id="ENC-W",
        world_seed="SEED-W",
        system_government_id="gov",
        active_situations=[],
    )
    weights_base = log_base["eligible_weights"]

    # With explicit weight = 1
    monkeypatch.setattr(eg, "load_encounter_types", _patched_encounter_types_with_subtype_weight)
    subtype_weighted, log_weighted = eg.select_subtype(
        encounter_id="ENC-W",
        world_seed="SEED-W",
        system_government_id="gov",
        active_situations=[],
    )
    weights_weighted = log_weighted["eligible_weights"]

    assert subtype_base["subtype_id"] == subtype_weighted["subtype_id"]
    assert weights_base == weights_weighted


def _patched_weighted_subtypes():
    # Two subtypes with equal base_weight but different subtype weight factors.
    return [
        {
            "subtype_id": "A",
            "emoji": "a",
            "posture": "neutral",
            "initiative": "npc",
            "allows_betrayal": False,
            "base_weight": 1,
            "allowed_TR_range": {"min": 1, "max": 1},
            "participant_templates": [],
            "default_flags": [],
            "reward_profiles": [],
            "npc_response_profile": {},
            "weight": 1,
        },
        {
            "subtype_id": "B",
            "emoji": "b",
            "posture": "neutral",
            "initiative": "npc",
            "allows_betrayal": False,
            "base_weight": 1,
            "allowed_TR_range": {"min": 1, "max": 1},
            "participant_templates": [],
            "default_flags": [],
            "reward_profiles": [],
            "npc_response_profile": {},
            "weight": 3,
        },
    ]


def test_subtype_weight_affects_selection_and_is_deterministic(monkeypatch) -> None:
    monkeypatch.setattr(eg, "load_encounter_types", _patched_weighted_subtypes)
    monkeypatch.setattr(eg, "load_governments", _patched_governments)

    seeds = [f"SEED-{i}" for i in range(10)]

    def _run_all():
        results = []
        for s in seeds:
            subtype, log = eg.select_subtype(
                encounter_id="ENC-WEIGHT",
                world_seed=s,
                system_government_id="gov",
                active_situations=[],
            )
            results.append((s, subtype["subtype_id"], tuple(log["eligible_weights"])))
        return results

    run1 = _run_all()
    run2 = _run_all()
    assert run1 == run2  # determinism

    counts = {"A": 0, "B": 0}
    for _, sid, _ in run1:
        counts[sid] += 1
    # With weight 1 vs 3 and identical base_weight, B should be chosen more frequently
    assert counts["B"] > counts["A"]


def test_all_weights_zero_fallbacks_to_baseline(monkeypatch) -> None:
    monkeypatch.setattr(eg, "load_encounter_types", _patched_encounter_types)
    monkeypatch.setattr(eg, "load_governments", _patched_governments)
    ws = WorldStateEngine()
    ws.register_system("SYS-1")
    ws.active_modifiers_by_system["SYS-1"] = [
        {
            "domain": "encounters",
            "target_type": "ALL",
            "target_id": None,
            "modifier_type": "encounter_weight_percent",
            "modifier_value": -100,
            "source_type": "event",
            "source_id": "E-4",
        }
    ]
    baseline_subtype, _ = eg.select_subtype(
        encounter_id="ENC-E",
        world_seed="SEED-5",
        system_government_id="gov",
        active_situations=[],
    )
    subtype, log = eg.select_subtype(
        encounter_id="ENC-E",
        world_seed="SEED-5",
        system_government_id="gov",
        active_situations=[],
        world_state_engine=ws,
        current_system_id="SYS-1",
    )
    assert log["zero_adjusted_fallback_to_baseline"] is True
    assert subtype["subtype_id"] == baseline_subtype["subtype_id"]
