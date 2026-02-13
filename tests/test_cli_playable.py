import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"
sys.path.insert(0, str(SRC_ROOT))

import cli_playable  # noqa: E402
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


def test_cli_playable_applies_rewards_via_reward_applicator(monkeypatch) -> None:
    calls = {"count": 0}
    original = cli_playable.apply_materialized_reward

    def _spy_apply_materialized_reward(*, player, reward_payload, context=None):
        calls["count"] += 1
        return original(player=player, reward_payload=reward_payload, context=context)

    monkeypatch.setattr(cli_playable, "apply_materialized_reward", _spy_apply_materialized_reward)
    run_playable(seed=2026, turns=5, scripted_actions=["travel"] * 5, interactive=False)
    assert calls["count"] >= 1

    source = (SRC_ROOT / "cli_playable.py").read_text(encoding="utf-8", errors="replace")
    assert "_apply_reward(" not in source
