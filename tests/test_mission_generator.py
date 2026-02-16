import random
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"
sys.path.insert(0, str(SRC_ROOT))

from mission_generator import select_weighted_mission_type  # noqa: E402
from world_state_engine import WorldStateEngine  # noqa: E402


def _eligible() -> list[dict]:
    return [
        {
            "mission_type_id": "delivery",
            "base_weight": 100,
            "mission_tags": ["lawful", "cargo"],
        },
        {
            "mission_type_id": "escort",
            "base_weight": 100,
            "mission_tags": ["combat"],
        },
    ]


def test_baseline_without_world_state_unchanged() -> None:
    rng_a = random.Random(12345)
    selected_a, weights_a = select_weighted_mission_type(
        eligible_missions=_eligible(),
        rng=rng_a,
    )
    rng_b = random.Random(12345)
    selected_b, weights_b = select_weighted_mission_type(
        eligible_missions=_eligible(),
        rng=rng_b,
        world_state_engine=None,
        system_id=None,
    )
    assert selected_a == selected_b
    assert weights_a == weights_b == {"delivery": 100.0, "escort": 100.0}


def test_positive_modifier_increases_weight() -> None:
    ws = WorldStateEngine()
    ws.register_system("SYS-1")
    ws.active_modifiers_by_system["SYS-1"] = [
        {
            "domain": "missions",
            "target_type": "id",
            "target_id": "delivery",
            "modifier_type": "mission_weight_percent",
            "modifier_value": 50,
            "source_type": "event",
            "source_id": "E-1",
        }
    ]
    selected, weights = select_weighted_mission_type(
        eligible_missions=_eligible(),
        rng=random.Random(7),
        world_state_engine=ws,
        system_id="SYS-1",
    )
    assert selected in {"delivery", "escort"}
    assert weights["delivery"] == 150.0
    assert weights["escort"] == 100.0


def test_negative_modifier_of_minus_100_sets_weight_to_zero() -> None:
    ws = WorldStateEngine()
    ws.register_system("SYS-1")
    ws.active_modifiers_by_system["SYS-1"] = [
        {
            "domain": "missions",
            "target_type": "id",
            "target_id": "delivery",
            "modifier_type": "mission_weight_percent",
            "modifier_value": -100,
            "source_type": "event",
            "source_id": "E-2",
        }
    ]
    selected, weights = select_weighted_mission_type(
        eligible_missions=_eligible(),
        rng=random.Random(7),
        world_state_engine=ws,
        system_id="SYS-1",
    )
    assert weights["delivery"] == 0.0
    assert selected == "escort"


def test_determinism_with_world_state_modifier() -> None:
    ws = WorldStateEngine()
    ws.register_system("SYS-1")
    ws.active_modifiers_by_system["SYS-1"] = [
        {
            "domain": "missions",
            "target_type": "id",
            "target_id": "escort",
            "modifier_type": "mission_weight_percent",
            "modifier_value": 75,
            "source_type": "situation",
            "source_id": "S-1",
        }
    ]

    def _run_once() -> tuple[str | None, dict[str, float]]:
        return select_weighted_mission_type(
            eligible_missions=_eligible(),
            rng=random.Random(555),
            world_state_engine=ws,
            system_id="SYS-1",
        )

    first = _run_once()
    second = _run_once()
    assert first == second
