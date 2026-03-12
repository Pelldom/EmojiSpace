"""
Tests for event-driven mission evaluation (Commit 3).

Validates that mission evaluation is triggered by game events.
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"
sys.path.insert(0, str(SRC_ROOT))

from mission_entity import MissionEntity, MissionState, MissionOutcome
from mission_manager import MissionManager
from mission_service import on_arrival, on_cargo_change, on_combat_resolved
from player_state import PlayerState


class TestEventDrivenEvaluation:
    """Test event-driven mission evaluation."""
    
    def test_arrival_triggers_exploration_completion(self):
        """Test that travel arrival automatically completes exploration missions."""
        # Create exploration mission
        mission = MissionEntity(
            mission_id="MIS-EXPLORE-ARRIVAL",
            mission_type="exploration",
            mission_tier=2,
            payout_policy="auto",
            claim_scope="none",
            reward_status="ungranted",
            mission_state=MissionState.ACTIVE,
        )
        mission.target = {
            "target_type": "destination",
            "target_id": "SYS-019-DST-05",
            "system_id": "SYS-019",
        }
        mission.reward_profile_id = "mission_credits_500"
        
        # Create player state
        player = PlayerState(
            player_id="test_player",
            credits=1000,
            active_missions=["MIS-EXPLORE-ARRIVAL"],
        )
        player.current_system_id = "SYS-019"
        player.current_destination_id = "SYS-019-DST-05"
        
        # Create mission manager
        manager = MissionManager()
        manager.missions[mission.mission_id] = mission
        
        # Simulate arrival event
        result = on_arrival(
            mission_manager=manager,
            player_state=player,
            new_system_id="SYS-019",
            new_destination_id="SYS-019-DST-05",
            world_seed=12345,
            turn=1,
        )
        
        # Assert mission completed automatically
        assert mission.mission_state == MissionState.RESOLVED
        assert mission.outcome == MissionOutcome.COMPLETED
        assert mission.mission_id in result["completed_mission_ids"]
        assert mission.mission_id not in player.active_missions
        assert mission.mission_id in player.completed_missions
    
    def test_cargo_change_triggers_cargo_acquired_evaluation(self):
        """Test that cargo changes trigger evaluation for cargo_acquired objectives."""
        # Create retrieval mission with cargo_acquired objective
        mission = MissionEntity(
            mission_id="MIS-RETRIEVE-1",
            mission_type="retrieval",
            mission_tier=2,
            payout_policy="auto",
            claim_scope="none",
            reward_status="ungranted",
            mission_state=MissionState.ACTIVE,
        )
        mission.objectives = [
            {
                "objective_id": "OBJ-1",
                "objective_type": "cargo_acquired",
                "status": "pending",
                "parameters": {
                    "goods": [
                        {"good_id": "iron_ore", "quantity": 5}
                    ]
                }
            }
        ]
        
        # Create player state without cargo initially
        player = PlayerState(
            player_id="test_player",
            credits=1000,
            active_missions=["MIS-RETRIEVE-1"],
        )
        player.current_system_id = "SYS-001"
        player.cargo_by_ship["active"] = {}
        
        # Create mission manager
        manager = MissionManager()
        manager.missions[mission.mission_id] = mission
        
        # Simulate cargo change (buy 3 iron_ore)
        player.cargo_by_ship["active"]["iron_ore"] = 3
        result = on_cargo_change(
            mission_manager=manager,
            player_state=player,
            cargo_delta={"iron_ore": 3},
            world_seed=12345,
            turn=1,
        )
        
        # Mission should not complete yet (need 5, have 3)
        assert mission.mission_state == MissionState.ACTIVE
        assert mission.mission_id not in result["completed_mission_ids"]
        
        # Add more cargo (now have 5)
        player.cargo_by_ship["active"]["iron_ore"] = 5
        result = on_cargo_change(
            mission_manager=manager,
            player_state=player,
            cargo_delta={"iron_ore": 2},
            world_seed=12345,
            turn=2,
        )
        
        # Mission should complete now
        assert mission.mission_state == MissionState.RESOLVED
        assert mission.outcome == MissionOutcome.COMPLETED
        assert mission.mission_id in result["completed_mission_ids"]
    
    def test_combat_resolved_triggers_combat_objectives(self):
        """Test that combat resolution triggers evaluation for combat-based objectives."""
        # Create bounty mission (would have combat_victory objective in full implementation)
        mission = MissionEntity(
            mission_id="MIS-BOUNTY-1",
            mission_type="bounty",
            mission_tier=2,
            payout_policy="auto",
            claim_scope="none",
            reward_status="ungranted",
            mission_state=MissionState.ACTIVE,
        )
        mission.objectives = [
            {
                "objective_id": "OBJ-1",
                "objective_type": "combat_victory",
                "status": "pending",
                "parameters": {}
            }
        ]
        
        # Create player state
        player = PlayerState(
            player_id="test_player",
            credits=1000,
            active_missions=["MIS-BOUNTY-1"],
        )
        player.current_system_id = "SYS-001"
        
        # Create mission manager
        manager = MissionManager()
        manager.missions[mission.mission_id] = mission
        
        # Simulate combat victory
        combat_result = {
            "outcome": "victory",
            "destroyed_npcs": [],
        }
        result = on_combat_resolved(
            mission_manager=manager,
            player_state=player,
            combat_result=combat_result,
            world_seed=12345,
            turn=1,
        )
        
        # Mission should complete (combat_victory objective satisfied)
        assert mission.mission_state == MissionState.RESOLVED
        assert mission.outcome == MissionOutcome.COMPLETED
        assert mission.mission_id in result["completed_mission_ids"]
    
    def test_arrival_auto_payout_for_exploration(self):
        """Test that exploration mission auto-pays on arrival completion."""
        # Create exploration mission with credit reward
        mission = MissionEntity(
            mission_id="MIS-EXPLORE-PAYOUT",
            mission_type="exploration",
            mission_tier=2,
            payout_policy="auto",
            claim_scope="none",
            reward_status="ungranted",
            mission_state=MissionState.ACTIVE,
        )
        mission.target = {
            "target_type": "destination",
            "target_id": "SYS-019-DST-05",
            "system_id": "SYS-019",
        }
        mission.reward_profile_id = "mission_credits_500"
        mission.distance_ly = 5
        
        # Create player state
        player = PlayerState(
            player_id="test_player",
            credits=1000,
            active_missions=["MIS-EXPLORE-PAYOUT"],
        )
        player.current_system_id = "SYS-019"
        player.current_destination_id = "SYS-019-DST-05"
        
        # Create mission manager
        manager = MissionManager()
        manager.missions[mission.mission_id] = mission
        
        credits_before = player.credits
        
        # Simulate arrival (should complete and auto-pay)
        result = on_arrival(
            mission_manager=manager,
            player_state=player,
            new_system_id="SYS-019",
            new_destination_id="SYS-019-DST-05",
            world_seed=12345,
            turn=1,
        )
        
        # Mission should be completed
        assert mission.mission_state == MissionState.RESOLVED
        assert mission.outcome == MissionOutcome.COMPLETED
        
        # Reward should be granted (auto payout)
        # Note: actual credit amount depends on reward profile calculation
        # We just verify reward_status changed
        assert mission.reward_status == "granted"
        assert mission.reward_granted_turn == 1
