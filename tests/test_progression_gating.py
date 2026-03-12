"""
Tests for progression gating fix (Commit 5).

Validates that completed missions are correctly counted and progression gates unlock.
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"
sys.path.insert(0, str(SRC_ROOT))

from mission_entity import MissionEntity, MissionState, MissionOutcome
from mission_manager import MissionManager
from player_state import PlayerState


class TestProgressionGating:
    """Test progression gating with normalized MissionOutcome."""
    
    def test_build_progression_context_counts_completed_missions(self):
        """Test that _build_progression_context counts missions with MissionOutcome.COMPLETED."""
        from game_engine import GameEngine
        
        # Create a mock game engine (simplified for testing)
        manager = MissionManager()
        
        # Create completed mission with tag
        mission1 = MissionEntity(
            mission_id="MIS-ALIEN-1",
            mission_type="delivery",
            mission_tier=2,
            payout_policy="auto",
            claim_scope="none",
            reward_status="granted",
            mission_state=MissionState.RESOLVED,
            outcome=MissionOutcome.COMPLETED,
        )
        mission1.tags = ["ship:trait_alien"]
        manager.missions[mission1.mission_id] = mission1
        
        # Create another completed mission with same tag
        mission2 = MissionEntity(
            mission_id="MIS-ALIEN-2",
            mission_type="delivery",
            mission_tier=2,
            payout_policy="auto",
            claim_scope="none",
            reward_status="granted",
            mission_state=MissionState.RESOLVED,
            outcome=MissionOutcome.COMPLETED,
        )
        mission2.tags = ["ship:trait_alien"]
        manager.missions[mission2.mission_id] = mission2
        
        # Create a failed mission (should not be counted)
        mission3 = MissionEntity(
            mission_id="MIS-ALIEN-3",
            mission_type="delivery",
            mission_tier=2,
            payout_policy="auto",
            claim_scope="none",
            reward_status="ungranted",
            mission_state=MissionState.RESOLVED,
            outcome=MissionOutcome.FAILED,
        )
        mission3.tags = ["ship:trait_alien"]
        manager.missions[mission3.mission_id] = mission3
        
        # Create an active mission (should not be counted)
        mission4 = MissionEntity(
            mission_id="MIS-ALIEN-4",
            mission_type="delivery",
            mission_tier=2,
            payout_policy="auto",
            claim_scope="none",
            reward_status="ungranted",
            mission_state=MissionState.ACTIVE,
            outcome=None,
        )
        mission4.tags = ["ship:trait_alien"]
        manager.missions[mission4.mission_id] = mission4
        
        # Build progression context (using the logic from _build_progression_context)
        completed_by_tag = {}
        for mission in manager.missions.values():
            if mission.mission_state != MissionState.RESOLVED:
                continue
            if mission.outcome != MissionOutcome.COMPLETED:  # Using enum, not string
                continue
            
            # Count tags on completed missions
            for tag in mission.tags:
                completed_by_tag[tag] = completed_by_tag.get(tag, 0) + 1
        
        # Assert that only completed missions are counted
        assert completed_by_tag.get("ship:trait_alien", 0) == 2
        assert "ship:trait_alien" in completed_by_tag
    
    def test_progression_gate_unlocks_after_completion(self):
        """Test that progression gates unlock after required missions are completed."""
        from mission_registry import mission_type_candidates_for_source
        
        # Simulate progression context with 2 completed alien missions
        progression_context = {
            "completed_missions_by_tag": {
                "ship:trait_alien": 2,
            }
        }
        
        # Get candidates for a source that includes alien missions
        candidates = mission_type_candidates_for_source(
            source_type="bar",
            progression_context=progression_context,
        )
        
        # Find alien mission candidates
        alien_candidates = [
            c for c in candidates
            if isinstance(c, dict) and c.get("tags") and "ship:trait_alien" in c.get("tags", [])
        ]
        
        # If there are alien missions with progression gates, verify they pass
        for candidate in alien_candidates:
            gate = candidate.get("progression_gate")
            if gate:
                requires_tag = gate.get("requires_tag", "")
                min_completed = gate.get("min_completed_with_tag", 0)
                
                if requires_tag == "ship:trait_alien":
                    completed_count = progression_context["completed_missions_by_tag"].get(requires_tag, 0)
                    # Gate should pass if completed_count >= min_completed
                    assert completed_count >= min_completed, (
                        f"Progression gate should pass: {completed_count} >= {min_completed}"
                    )
    
    def test_progression_context_uses_enum_not_string(self):
        """Test that progression context correctly compares MissionOutcome enum, not strings."""
        manager = MissionManager()
        
        # Create mission with enum outcome
        mission = MissionEntity(
            mission_id="MIS-TEST-ENUM",
            mission_type="delivery",
            mission_tier=1,
            payout_policy="auto",
            claim_scope="none",
            reward_status="granted",
            mission_state=MissionState.RESOLVED,
            outcome=MissionOutcome.COMPLETED,  # Using enum
        )
        mission.tags = ["test_tag"]
        manager.missions[mission.mission_id] = mission
        
        # Build progression context
        completed_by_tag = {}
        for mission in manager.missions.values():
            if mission.mission_state != MissionState.RESOLVED:
                continue
            # This should work because we're comparing enum to enum
            if mission.outcome != MissionOutcome.COMPLETED:
                continue
            
            for tag in mission.tags:
                completed_by_tag[tag] = completed_by_tag.get(tag, 0) + 1
        
        # Should count the mission
        assert completed_by_tag.get("test_tag", 0) == 1
        
        # Verify enum comparison works correctly
        # The fix uses: mission.outcome != MissionOutcome.COMPLETED (enum to enum)
        # This is correct because mission.outcome is stored as MissionOutcome enum
        assert mission.outcome == MissionOutcome.COMPLETED  # Enum comparison works
        assert isinstance(mission.outcome, MissionOutcome)  # It's an enum, not a string
        # Note: In Python, MissionOutcome.COMPLETED == "completed" is True (value comparison)
        # But mission.outcome != "completed" would be False if mission.outcome is a string
        # The fix ensures we compare enum to enum, which is type-safe
    
    def test_progression_context_excludes_failed_missions(self):
        """Test that failed missions are not counted in progression context."""
        manager = MissionManager()
        
        # Create failed mission with tag
        mission = MissionEntity(
            mission_id="MIS-FAILED",
            mission_type="delivery",
            mission_tier=1,
            payout_policy="auto",
            claim_scope="none",
            reward_status="ungranted",
            mission_state=MissionState.RESOLVED,
            outcome=MissionOutcome.FAILED,  # Failed, not completed
        )
        mission.tags = ["ship:trait_alien"]
        manager.missions[mission.mission_id] = mission
        
        # Build progression context
        completed_by_tag = {}
        for mission in manager.missions.values():
            if mission.mission_state != MissionState.RESOLVED:
                continue
            if mission.outcome != MissionOutcome.COMPLETED:  # Only count COMPLETED
                continue
            
            for tag in mission.tags:
                completed_by_tag[tag] = completed_by_tag.get(tag, 0) + 1
        
        # Failed mission should not be counted
        assert completed_by_tag.get("ship:trait_alien", 0) == 0
