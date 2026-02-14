import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"
sys.path.insert(0, str(SRC_ROOT))

from cli_run import build_simulation  # noqa: E402


def test_phase4_legacy_flow_via_simulation_controller_is_deterministic() -> None:
    first = _run_once(seed=4012)
    second = _run_once(seed=4012)
    assert first == second
    assert first["ok"] is True
    event_types = [event.get("event_type") for event in first["events"]]
    assert event_types[:4] == [
        "travel_resolution",
        "enforcement_checkpoint_processed",
        "travel_applied",
        "encounter_generated",
    ]
    assert "encounter_dispatch" in event_types
    assert "reward_applied" in event_types


def _run_once(seed: int) -> dict:
    controller, world_state = build_simulation(seed)
    sector = world_state["sector"]
    target = sector.systems[1].system_id
    return controller.execute(
        {
            "action_type": "travel_to_destination",
            "payload": {
                "target_system_id": target,
                "distance_ly": 1,
                "encounter_action": "attack",
            },
        }
    )

