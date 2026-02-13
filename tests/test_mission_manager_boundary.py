import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"
sys.path.insert(0, str(SRC_ROOT))

from mission_entity import MissionEntity  # noqa: E402
from mission_manager import MissionManager  # noqa: E402
from player_state import PlayerState  # noqa: E402


def _mission_with_rewards() -> MissionEntity:
    return MissionEntity(
        mission_id="MIS-1",
        rewards=[{"field": "credits", "delta": 120}],
    )


def test_mission_complete_delegates_reward_application(monkeypatch) -> None:
    manager = MissionManager()
    mission = _mission_with_rewards()
    manager.offer(mission)
    player = PlayerState(player_id="player", credits=1000, active_missions=["MIS-1"])
    manager.missions["MIS-1"].mission_state = "active"

    called = {"count": 0, "mission_id": None}

    def _fake_apply(*, mission_id, rewards, player, logger, turn):
        called["count"] += 1
        called["mission_id"] = mission_id
        player.credits += 120

    monkeypatch.setattr("mission_manager.apply_mission_rewards", _fake_apply)
    manager.complete("MIS-1", player, logger=None, turn=7)
    assert called["count"] == 1
    assert called["mission_id"] == "MIS-1"
    assert player.credits == 1120


def test_mission_reward_outcome_remains_deterministic() -> None:
    manager = MissionManager()
    manager.offer(_mission_with_rewards())
    player_a = PlayerState(player_id="player", credits=1000, active_missions=["MIS-1"])
    player_b = PlayerState(player_id="player", credits=1000, active_missions=["MIS-1"])
    manager.missions["MIS-1"].mission_state = "active"

    manager.complete("MIS-1", player_a, logger=None, turn=1)
    manager.missions["MIS-1"].mission_state = "active"
    manager.missions["MIS-1"].outcome = None
    manager.complete("MIS-1", player_b, logger=None, turn=1)
    assert player_a.credits == player_b.credits == 1120
