import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"
sys.path.insert(0, str(SRC_ROOT))

from game_engine import GameEngine, EngineContext  # noqa: E402
from ship_assembler import ship_get_utility_count  # noqa: F401,E402 (imported for monkeypatch target)


class DummySpec:
    def __init__(self, encounter_id: str, subtype_id: str):
        self.encounter_id = encounter_id
        self.subtype_id = subtype_id
        self.reward_profile_id = None


def _make_engine():
    # Use small system_count for faster world generation
    return GameEngine(world_seed=12345, config={"system_count": 5})


def _make_context():
    return EngineContext(
        command={},
        command_type="encounter_action",
        turn_before=0,
        turn_after=0,
        events=[],
        hard_stop=False,
        hard_stop_reason=None,
        active_encounters=[],
    )


def test_probe_math_scaling(monkeypatch) -> None:
    engine = _make_engine()

    def _run_with_probe_count(count: int) -> float:
        monkeypatch.setattr(
            "ship_assembler.ship_get_utility_count",
            lambda ship, key: count,
        )
        context = _make_context()
        spec = DummySpec(encounter_id="ENC-PROBE", subtype_id="spatial_rift")
        engine._resolve_exploration_encounter(context=context, spec=spec, player_action="investigate")
        # Find last exploration_investigate event
        ev = next(
            e for e in reversed(context.events) if e.get("stage") == "exploration_investigate"
        )
        return float(ev["detail"]["chance"])

    assert _run_with_probe_count(0) == 0.25
    assert _run_with_probe_count(1) == 0.40
    assert _run_with_probe_count(2) == 0.55
    assert _run_with_probe_count(6) == 1.0


def test_probe_determinism(monkeypatch) -> None:
    engine = _make_engine()
    monkeypatch.setattr(
        "ship_assembler.ship_get_utility_count",
        lambda ship, key: 2,
    )
    spec = DummySpec(encounter_id="ENC-DET", subtype_id="spatial_rift")

    def _run_once():
        context = _make_context()
        outcome = engine._resolve_exploration_encounter(
            context=context,
            spec=spec,
            player_action="investigate",
        )
        ev = next(
            e for e in reversed(context.events) if e.get("stage") == "exploration_investigate"
        )
        detail = ev["detail"]
        return (
            float(detail["chance"]),
            float(detail["roll"]),
            bool(detail["success"]),
            outcome["resolver"],
            outcome["outcome"],
        )

    assert _run_once() == _run_once()


def test_wormhole_success_and_failure(monkeypatch) -> None:
    engine = _make_engine()
    spec = DummySpec(encounter_id="ENC-WH", subtype_id="wormhole_anomaly")

    # Force probe_count to 0 so base chance is 0.25
    monkeypatch.setattr(
        "ship_assembler.ship_get_utility_count",
        lambda ship, key: 0,
    )

    # Force success: roll < chance
    monkeypatch.setattr(
        "game_engine.deterministic_float",
        lambda seed_string: 0.0,
    )
    context_success = _make_context()
    outcome_success = engine._resolve_exploration_encounter(
        context=context_success,
        spec=spec,
        player_action="investigate",
    )
    assert outcome_success["resolver"] == "exploration"
    assert outcome_success["outcome"] == "wormhole_reveal"
    wh_event = next(
        e for e in reversed(context_success.events) if e.get("stage") == "wormhole_reveal"
    )
    detail = wh_event["detail"]
    assert "target_system_name" in detail
    assert detail["distance_band"] in {"Near", "Mid", "Far"}
    # Ensure target is not the current system
    current_system = engine.sector.get_system(engine.player_state.current_system_id)
    assert detail["target_system_name"] != current_system.name

    # Force failure: roll >= chance
    monkeypatch.setattr(
        "game_engine.deterministic_float",
        lambda seed_string: 0.999,
    )
    context_fail = _make_context()
    outcome_fail = engine._resolve_exploration_encounter(
        context=context_fail,
        spec=spec,
        player_action="investigate",
    )
    assert outcome_fail["resolver"] == "exploration"
    assert outcome_fail["outcome"] == "wormhole_fail"
    wh_event_fail = next(
        e for e in reversed(context_fail.events) if e.get("stage") == "wormhole_reveal"
    )
    detail_fail = wh_event_fail["detail"]
    assert detail_fail["message"] == "Destination unknown."

