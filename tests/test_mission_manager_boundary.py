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
        mission_type="delivery",
        mission_tier=1,
        payout_policy="auto",
        claim_scope="none",
        reward_status="ungranted",
        reward_profile_id="mission_credits_500",
    )


def test_mission_complete_delegates_reward_application(monkeypatch) -> None:
    """Test that mission.complete() transitions state correctly.
    
    Note: Rewards are now applied via evaluate_active_missions auto-payout,
    not through manager.complete(). This test verifies state transition only.
    """
    from mission_entity import MissionState, MissionOutcome
    
    manager = MissionManager()
    mission = _mission_with_rewards()
    manager.offer(mission)
    player = PlayerState(player_id="player", credits=1000, active_missions=["MIS-1"])
    manager.missions["MIS-1"].mission_state = MissionState.ACTIVE

    # Complete mission (state transition only, no reward application)
    manager.complete("MIS-1", player, logger=None, turn=7)
    
    # Verify state transition
    assert manager.missions["MIS-1"].mission_state == MissionState.RESOLVED
    assert manager.missions["MIS-1"].outcome == MissionOutcome.COMPLETED
    assert "MIS-1" not in player.active_missions
    assert "MIS-1" in player.completed_missions
    
    # Credits unchanged (rewards applied separately via evaluate_active_missions)
    assert player.credits == 1000


def test_mission_reward_outcome_remains_deterministic() -> None:
    """Test that mission completion state transitions are deterministic.
    
    Note: This test verifies state transitions, not reward application.
    Rewards are applied separately via evaluate_active_missions.
    """
    from mission_entity import MissionState, MissionOutcome
    
    manager = MissionManager()
    manager.offer(_mission_with_rewards())
    player_a = PlayerState(player_id="player", credits=1000, active_missions=["MIS-1"])
    player_b = PlayerState(player_id="player", credits=1000, active_missions=["MIS-1"])
    manager.missions["MIS-1"].mission_state = MissionState.ACTIVE

    manager.complete("MIS-1", player_a, logger=None, turn=1)
    
    # Reset for second completion
    manager.missions["MIS-1"].mission_state = MissionState.ACTIVE
    manager.missions["MIS-1"].outcome = None
    player_b.active_missions = ["MIS-1"]
    player_b.completed_missions = []
    
    manager.complete("MIS-1", player_b, logger=None, turn=1)
    
    # Both should have same state
    assert manager.missions["MIS-1"].mission_state == MissionState.RESOLVED
    assert manager.missions["MIS-1"].outcome == MissionOutcome.COMPLETED
    assert "MIS-1" not in player_a.active_missions
    assert "MIS-1" not in player_b.active_missions
    assert "MIS-1" in player_a.completed_missions
    assert "MIS-1" in player_b.completed_missions
