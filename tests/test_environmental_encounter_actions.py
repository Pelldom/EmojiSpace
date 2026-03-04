import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"
sys.path.insert(0, str(SRC_ROOT))

from interaction_layer import (  # noqa: E402
    ACTION_ATTACK,
    ACTION_IGNORE,
    ACTION_INVESTIGATE,
    ACTION_RESPOND,
    allowed_actions_initial,
)
from game_engine import GameEngine  # noqa: E402


class _EnvSpec:
    initiative = "npc"
    posture = "opportunity"
    encounter_category = "environmental_hazard"


class _NpcSpec:
    initiative = "npc"
    posture = "neutral"
    encounter_category = "space_npc_encounter"


def _make_engine() -> GameEngine:
    # Use small system_count for faster world generation
    return GameEngine(world_seed=12345, config={"system_count": 5})


def test_allowed_actions_initial_environmental_uses_investigate_and_ignore_only() -> None:
    spec = _EnvSpec()
    actions = set(allowed_actions_initial(spec))
    assert actions == {ACTION_INVESTIGATE, ACTION_IGNORE}


def test_allowed_actions_initial_npc_non_environmental_unchanged() -> None:
    spec = _NpcSpec()
    actions = set(allowed_actions_initial(spec))
    assert actions == {ACTION_IGNORE, ACTION_RESPOND, ACTION_ATTACK}


def test_pending_encounter_info_suppresses_npc_preview_for_environmental(monkeypatch) -> None:
    engine = _make_engine()

    class EnvEncounter:
        def __init__(self) -> None:
            self.encounter_id = "ENC-ENV-001"
            self.subtype_id = "debris_storm"
            self.encounter_category = "environmental_hazard"

    # If NPC preview is accidentally invoked for environmental encounters, fail the test.
    def _generate_npc_ship(*args, **kwargs):
        raise AssertionError("generate_npc_ship should not be called for environmental encounters")

    monkeypatch.setattr("npc_ship_generator.generate_npc_ship", _generate_npc_ship)

    env_spec = EnvEncounter()
    engine._pending_travel = {
        "encounter_context": {"encounter_id": env_spec.encounter_id, "options": []},
        "current_encounter": env_spec,
    }

    info = engine.get_pending_encounter_info()
    assert info is not None
    assert info["npc_ship_info"] is None


def test_pending_encounter_info_shows_npc_preview_for_non_environmental(monkeypatch) -> None:
    engine = _make_engine()

    class NpcEncounter:
        def __init__(self) -> None:
            self.encounter_id = "ENC-NPC-001"
            self.subtype_id = "civilian_trader_ship"
            self.encounter_category = "space_npc_encounter"

    def _generate_npc_ship(*args, **kwargs):
        return {"frame_id": "test_frame"}

    monkeypatch.setattr("npc_ship_generator.generate_npc_ship", _generate_npc_ship)

    npc_spec = NpcEncounter()
    engine._pending_travel = {
        "encounter_context": {"encounter_id": npc_spec.encounter_id, "options": []},
        "current_encounter": npc_spec,
    }

    info = engine.get_pending_encounter_info()
    assert info is not None
    assert info["npc_ship_info"] is not None

