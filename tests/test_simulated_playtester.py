import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"
sys.path.insert(0, str(SRC_ROOT))

from simulated_playtester import SimulatedPlaytester  # noqa: E402


def test_simulation_runs_250_turns() -> None:
    summary = SimulatedPlaytester(seed=12345).run()
    assert int(summary["turns_completed"]) <= 250
    assert isinstance(summary["hard_stop"], bool)
    if summary["hard_stop"] is False:
        assert int(summary["turns_completed"]) == 250


def test_simulation_deterministic() -> None:
    summary = SimulatedPlaytester(seed=12345).run()
    assert summary["determinism_verified"] is True


def test_invariants_hold() -> None:
    summary = SimulatedPlaytester(seed=12345).run()
    assert int(summary["turns_completed"]) >= 1
    assert int(summary["max_turns"]) == 250
    assert summary["determinism_verified"] is True
