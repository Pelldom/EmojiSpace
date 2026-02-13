import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"
sys.path.insert(0, str(SRC_ROOT))

from pursuit_resolver import resolve_pursuit  # noqa: E402
from reaction_engine import get_npc_outcome  # noqa: E402


class _Spec:
    def __init__(self):
        self.encounter_id = "ENC-REACTION-1"
        self.posture = "hostile"
        self.subtype_id = "raider"
        self.threat_rating_tr = 3
        self.allows_betrayal = True
        self.npc_response_profile = {
            "on_intimidate": {
                "attack": 10,
                "accept": 0,
            }
        }


def test_reaction_outcome_vocabulary_aligns_to_contract_for_reaction_actions() -> None:
    outcome, _ = get_npc_outcome(
        spec=_Spec(),
        player_action="intimidate",
        world_seed="WORLD",
        ignore_count=0,
        reputation_score=50,
        notoriety_score=50,
    )
    assert outcome in {
        "accept",
        "accept_and_attack",
        "refuse_stand",
        "refuse_flee",
        "refuse_attack",
    }
    assert outcome == "refuse_attack"


def test_pursuit_uses_contract_factors_and_is_deterministic() -> None:
    pursuer = {
        "speed": 4,
        "pilot_skill": 3,
        "engine_band": 2,
        "tr_band": 2,
        "interdiction_device": True,
    }
    pursued = {
        "speed": 6,
        "pilot_skill": 4,
        "engine_band": 4,
        "tr_band": 4,
        "cloaking_device": True,
    }
    first = resolve_pursuit("ENC-PUR-1", "WORLD-123", pursuer, pursued)
    second = resolve_pursuit("ENC-PUR-1", "WORLD-123", pursuer, pursued)

    assert first.outcome in {"escape_success", "escape_fail"}
    assert first.outcome == second.outcome
    assert first.threshold == second.threshold
    assert first.roll == second.roll
    assert first.log["engine_delta"] == 2
    assert first.log["tr_delta"] == 2
    assert "probability_distribution" in first.log
