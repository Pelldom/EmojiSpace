import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"
sys.path.insert(0, str(SRC_ROOT))

from cli_run import build_simulation  # noqa: E402


def test_simulation_controller_e2e_deterministic_sequence() -> None:
    first = _run_once(seed=4001)
    second = _run_once(seed=4001)
    assert first == second
    assert first["ok"] is True
    event_types = [event.get("event_type") for event in first["events"]]
    assert event_types[:5] == [
        "travel_resolution",
        "enforcement_checkpoint_processed",
        "travel_applied",
        "encounter_generated",
        "encounter_dispatch",
    ]
    assert ("pursuit_resolved" in event_types) or ("combat_resolved" in event_types)
    assert "reward_applied" in event_types
    assert first["events"][-1]["event_type"] == "reward_applied"


def _run_once(seed: int) -> dict:
    controller, world_state = build_simulation(seed)
    sector = world_state["sector"]
    player = world_state["turn_loop"]._player_state  # noqa: SLF001
    target_system = sector.systems[1]
    player.reputation_by_system[target_system.system_id] = 1
    player.heat_by_system[target_system.system_id] = 100
    result = controller.execute(
        {
            "action_type": "travel_to_destination",
            "payload": {
                "target_system_id": target_system.system_id,
                "distance_ly": 1,
                "encounter_action": "attack",
            },
        }
    )
    return result

