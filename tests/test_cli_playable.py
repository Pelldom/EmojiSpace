import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"
sys.path.insert(0, str(SRC_ROOT))

from cli_playable import run_playable  # noqa: E402


def test_cli_playable_five_turn_scripted_is_deterministic() -> None:
    first = run_playable(seed=2026, turns=5, scripted_actions=["travel"] * 5, interactive=False)
    second = run_playable(seed=2026, turns=5, scripted_actions=["travel"] * 5, interactive=False)

    assert first == second
    events = [entry.get("event") for entry in first]
    assert events.count("turn_start") == 5
    assert "travel" in events
    assert "encounter" in events
    assert "interaction_dispatch" in events
    assert "reward" in events
