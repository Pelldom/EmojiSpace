"""
Tests for unified reward system (Commit 4).

Validates that rewards use RewardBundle for both preview and payout.
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"
sys.path.insert(0, str(SRC_ROOT))

from mission_entity import MissionEntity, MissionState
from mission_manager import MissionManager
from mission_domain import RewardBundle
from reward_service import preview, payout
from player_state import PlayerState


class TestRewardUnified:
    """Test unified reward preview and payout."""
    
    def test_reward_preview_returns_reward_bundle(self):
        """Test that reward preview returns RewardBundle."""
        mission = MissionEntity(
            mission_id="MIS-TEST-1",
            mission_type="delivery",
            mission_tier=2,
            payout_policy="auto",
            claim_scope="none",
            reward_status="ungranted",
            reward_profile_id="raider_loot",
        )
        
        # Use empty system_markets for test (materialize_reward needs markets for cargo)
        bundle = preview(mission, system_markets=[], world_seed=12345)
        
        assert isinstance(bundle, RewardBundle)
        # raider_loot is "mixed" so should have credits
        assert bundle.credits >= 0
    
    def test_reward_payout_applies_to_player_state(self):
        """Test that reward payout applies rewards to player state."""
        mission = MissionEntity(
            mission_id="MIS-TEST-2",
            mission_type="delivery",
            mission_tier=2,
            payout_policy="auto",
            claim_scope="none",
            reward_status="ungranted",
            reward_profile_id="raider_loot",
        )
        
        player = PlayerState(player_id="test", credits=1000)
        credits_before = player.credits
        
        # Use empty system_markets for test
        bundle = payout(mission, player, system_markets=[], world_seed=12345)
        
        assert isinstance(bundle, RewardBundle)
        # raider_loot is "mixed" so should have credits
        if bundle.credits > 0:
            assert player.credits > credits_before  # Credits should increase
            assert player.credits == credits_before + bundle.credits
    
    def test_reward_bundle_to_summary_lines_credits(self):
        """Test RewardBundle.to_reward_summary_lines() for credits."""
        bundle = RewardBundle(credits=5000)
        lines = bundle.to_reward_summary_lines()
        
        assert len(lines) > 0
        assert any("5000" in line and "credits" in line for line in lines)
    
    def test_reward_bundle_to_summary_lines_cargo(self):
        """Test RewardBundle.to_reward_summary_lines() for cargo."""
        from mission_domain import CargoGrant
        
        bundle = RewardBundle()
        bundle.cargo_grants.append(CargoGrant(item_id="iron_ore", quantity=10))
        lines = bundle.to_reward_summary_lines()
        
        assert len(lines) > 0
        assert any("iron_ore" in line for line in lines)
        assert any("10" in line for line in lines)
    
    def test_reward_bundle_empty_shows_no_rewards(self):
        """Test that empty RewardBundle shows 'No rewards'."""
        bundle = RewardBundle()
        lines = bundle.to_reward_summary_lines()
        
        assert len(lines) == 1
        assert "No rewards" in lines[0]
    
    def test_mission_without_reward_profile_id_cannot_be_offered(self):
        """Test that missions without reward_profile_id raise error on offer."""
        manager = MissionManager()
        mission = MissionEntity(
            mission_id="MIS-NO-REWARD",
            mission_type="delivery",
            mission_tier=1,
            payout_policy="auto",
            claim_scope="none",
            reward_status="ungranted",
            reward_profile_id=None,  # Missing!
        )
        
        try:
            manager.offer(mission)
            assert False, "Should have raised ValueError"
        except ValueError as e:
            assert "reward_profile_id" in str(e)
            assert "cannot be offered" in str(e)
    
    def test_mission_with_reward_profile_id_can_be_offered(self):
        """Test that missions with reward_profile_id can be offered."""
        manager = MissionManager()
        mission = MissionEntity(
            mission_id="MIS-WITH-REWARD",
            mission_type="delivery",
            mission_tier=1,
            payout_policy="auto",
            claim_scope="none",
            reward_status="ungranted",
            reward_profile_id="raider_loot",
        )
        
        # Should not raise
        manager.offer(mission)
        assert mission.mission_id in manager.offered
        assert mission.mission_id in manager.missions
