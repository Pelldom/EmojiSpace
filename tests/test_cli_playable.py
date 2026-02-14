import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"
sys.path.insert(0, str(SRC_ROOT))

from cli_run import build_simulation  # noqa: E402
from simulation_controller import SimulationController  # noqa: E402


def _run_scripted(seed: int, turns: int) -> list[dict]:
    controller, world_state = build_simulation(seed)
    assert isinstance(controller, SimulationController)
    sector = world_state["sector"]
    system_ids = [system.system_id for system in sector.systems]
    events: list[dict] = []
    for index in range(turns):
        target = system_ids[(index + 1) % len(system_ids)]
        result = controller.execute(
            {
                "action_type": "travel_to_destination",
                "payload": {"target_system_id": target, "encounter_action": "ignore"},
            }
        )
        events.append(result)
    return events


def test_simulation_controller_five_turn_scripted_is_deterministic() -> None:
    first = _run_scripted(seed=2026, turns=5)
    second = _run_scripted(seed=2026, turns=5)
    assert first == second
    for result in first:
        assert result["ok"] is True
        event_types = [entry.get("event_type") for entry in result["events"]]
        assert "travel_resolution" in event_types
        assert "encounter_generated" in event_types
        assert "reward_applied" in event_types
