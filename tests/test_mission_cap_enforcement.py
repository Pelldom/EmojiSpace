"""Test mission cap enforcement (tier-based and global)."""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"
sys.path.insert(0, str(SRC_ROOT))

from mission_entity import MissionEntity, MissionState  # noqa: E402
from mission_manager import MissionManager  # noqa: E402
from player_state import PlayerState  # noqa: E402


def test_accept_5_tier1_missions_succeeds() -> None:
    """Player can accept 5 Tier 1 missions (tier cap allows 5)."""
    manager = MissionManager()
    player = PlayerState()
    
    # Create and offer 5 Tier 1 missions
    missions = []
    for i in range(5):
        mission = MissionEntity(mission_id=f"M{i+1}", mission_tier=1)
        manager.offer(mission)
        missions.append(mission.mission_id)
    
    # Accept all 5
    for mission_id in missions:
        accepted, error = manager.accept(mission_id, player)
        assert accepted is True, f"Mission {mission_id} should be accepted"
        assert error is None
    
    # Verify all 5 are active
    active_count = sum(1 for m in manager.missions.values() if m.mission_state == MissionState.ACTIVE)
    assert active_count == 5


def test_accept_6th_tier1_mission_blocked_by_global_cap() -> None:
    """6th Tier 1 mission should be blocked by global cap (5 total)."""
    manager = MissionManager()
    player = PlayerState()
    
    # Create and offer 6 Tier 1 missions
    missions = []
    for i in range(6):
        mission = MissionEntity(mission_id=f"M{i+1}", mission_tier=1)
        manager.offer(mission)
        missions.append(mission.mission_id)
    
    # Accept first 5
    for mission_id in missions[:5]:
        accepted, error = manager.accept(mission_id, player)
        assert accepted is True
        assert error is None
    
    # 6th should be blocked by global cap
    accepted, error = manager.accept(missions[5], player)
    assert accepted is False
    assert error == "mission_accept_failed_total_cap"


def test_accept_3_tier3_missions_succeeds() -> None:
    """Player can accept 3 Tier 3 missions (tier cap allows 3)."""
    manager = MissionManager()
    player = PlayerState()
    
    # Create and offer 3 Tier 3 missions
    missions = []
    for i in range(3):
        mission = MissionEntity(mission_id=f"M{i+1}", mission_tier=3)
        manager.offer(mission)
        missions.append(mission.mission_id)
    
    # Accept all 3
    for mission_id in missions:
        accepted, error = manager.accept(mission_id, player)
        assert accepted is True
        assert error is None
    
    # Verify all 3 are active
    active_count = sum(1 for m in manager.missions.values() if m.mission_state == MissionState.ACTIVE)
    assert active_count == 3


def test_accept_4th_tier3_mission_blocked_by_tier_cap() -> None:
    """4th Tier 3 mission should be blocked by tier cap (3 max for tier 3)."""
    manager = MissionManager()
    player = PlayerState()
    
    # Create and offer 4 Tier 3 missions
    missions = []
    for i in range(4):
        mission = MissionEntity(mission_id=f"M{i+1}", mission_tier=3)
        manager.offer(mission)
        missions.append(mission.mission_id)
    
    # Accept first 3
    for mission_id in missions[:3]:
        accepted, error = manager.accept(mission_id, player)
        assert accepted is True
        assert error is None
    
    # 4th should be blocked by tier cap
    accepted, error = manager.accept(missions[3], player)
    assert accepted is False
    assert error == "mission_accept_failed_tier_cap"


def test_mixed_tiers_until_global_cap() -> None:
    """Mix tiers until total reaches 5, then further accepts blocked."""
    manager = MissionManager()
    player = PlayerState()
    
    # Create mix: 2 Tier 1, 2 Tier 2, 1 Tier 3 = 5 total
    missions = [
        MissionEntity(mission_id="M1-T1", mission_tier=1),
        MissionEntity(mission_id="M2-T1", mission_tier=1),
        MissionEntity(mission_id="M3-T2", mission_tier=2),
        MissionEntity(mission_id="M4-T2", mission_tier=2),
        MissionEntity(mission_id="M5-T3", mission_tier=3),
        MissionEntity(mission_id="M6-T1", mission_tier=1),  # This should be blocked
    ]
    
    for mission in missions:
        manager.offer(mission)
    
    # Accept first 5 (should succeed)
    for mission_id in ["M1-T1", "M2-T1", "M3-T2", "M4-T2", "M5-T3"]:
        accepted, error = manager.accept(mission_id, player)
        assert accepted is True, f"Mission {mission_id} should be accepted"
        assert error is None
    
    # 6th should be blocked by global cap
    accepted, error = manager.accept("M6-T1", player)
    assert accepted is False
    assert error == "mission_accept_failed_total_cap"


def test_tier5_only_one_allowed() -> None:
    """Tier 5 missions have cap of 1."""
    manager = MissionManager()
    player = PlayerState()
    
    # Create 2 Tier 5 missions
    m1 = MissionEntity(mission_id="M1-T5", mission_tier=5)
    m2 = MissionEntity(mission_id="M2-T5", mission_tier=5)
    manager.offer(m1)
    manager.offer(m2)
    
    # Accept first Tier 5
    accepted, error = manager.accept("M1-T5", player)
    assert accepted is True
    assert error is None
    
    # Second Tier 5 should be blocked by tier cap
    accepted, error = manager.accept("M2-T5", player)
    assert accepted is False
    assert error == "mission_accept_failed_tier_cap"
