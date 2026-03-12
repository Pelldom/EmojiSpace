"""
Tests for objective-driven mission evaluation (Commit 2).

Validates that missions complete based on objectives, not mission_type.
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"
sys.path.insert(0, str(SRC_ROOT))

from mission_entity import MissionEntity, MissionState, MissionOutcome
from mission_manager import MissionManager, evaluate_active_missions
from mission_objective_evaluator import (
    convert_mission_objectives_to_canonical,
    evaluate_objective,
    MissionEventContext,
)
from player_state import PlayerState


class TestObjectiveEvaluation:
    """Test objective evaluation for mission completion."""
    
    def test_exploration_mission_completes_on_destination_arrival(self):
        """Test that exploration missions complete when arriving at target destination."""
        # Create exploration mission
        mission = MissionEntity(
            mission_id="MIS-EXPLORE-1",
            mission_type="exploration",
            mission_tier=2,
            payout_policy="auto",
            claim_scope="none",
            reward_status="ungranted",
            mission_state=MissionState.ACTIVE,
        )
        mission.target = {
            "target_type": "destination",
            "target_id": "SYS-001-DST-05",
            "system_id": "SYS-001",
        }
        mission.reward_profile_id = "mission_credits_500"
        
        # Create player state
        player = PlayerState(
            player_id="test_player",
            credits=1000,
            active_missions=["MIS-EXPLORE-1"],
        )
        player.current_system_id = "SYS-001"
        player.current_destination_id = "SYS-001-DST-05"
        
        # Create mission manager
        manager = MissionManager()
        manager.missions[mission.mission_id] = mission
        
        # Evaluate on arrival
        result = evaluate_active_missions(
            mission_manager=manager,
            player_state=player,
            current_system_id="SYS-001",
            current_destination_id="SYS-001-DST-05",
            event_context={"event": "travel_arrival", "target_destination_id": "SYS-001-DST-05"},
            world_seed=12345,
            turn=1,
        )
        
        # Assert mission completed
        assert mission.mission_state == MissionState.RESOLVED
        assert mission.outcome == MissionOutcome.COMPLETED
        assert mission.mission_id in result["completed_mission_ids"]
        assert mission.mission_id not in player.active_missions
        assert mission.mission_id in player.completed_missions
    
    def test_delivery_mission_completes_with_cargo_at_destination(self):
        """Test that delivery missions complete when cargo is present at destination."""
        # Create delivery mission with cargo objective
        mission = MissionEntity(
            mission_id="MIS-DELIVERY-1",
            mission_type="delivery",
            mission_tier=2,
            payout_policy="auto",
            claim_scope="none",
            reward_status="ungranted",
            mission_state=MissionState.ACTIVE,
        )
        mission.target = {
            "target_type": "destination",
            "target_id": "SYS-002-DST-03",
            "system_id": "SYS-002",
        }
        mission.objectives = [
            {
                "objective_id": "OBJ-1",
                "objective_type": "deliver_cargo",
                "status": "pending",
                "parameters": {
                    "goods": [
                        {"good_id": "iron_ore", "quantity": 5}
                    ]
                }
            }
        ]
        mission.reward_profile_id = "mission_credits_500"
        
        # Create player state with cargo
        player = PlayerState(
            player_id="test_player",
            credits=1000,
            active_missions=["MIS-DELIVERY-1"],
        )
        player.current_system_id = "SYS-002"
        player.current_destination_id = "SYS-002-DST-03"
        player.cargo_by_ship["active"] = {"iron_ore": 5}
        
        # Create mission manager
        manager = MissionManager()
        manager.missions[mission.mission_id] = mission
        
        # Evaluate on arrival
        result = evaluate_active_missions(
            mission_manager=manager,
            player_state=player,
            current_system_id="SYS-002",
            current_destination_id="SYS-002-DST-03",
            event_context={"event": "travel_arrival", "target_destination_id": "SYS-002-DST-03"},
            world_seed=12345,
            turn=1,
        )
        
        # Assert mission completed
        assert mission.mission_state == MissionState.RESOLVED
        assert mission.outcome == MissionOutcome.COMPLETED
        assert mission.mission_id in result["completed_mission_ids"]
        assert mission.mission_id not in player.active_missions
        assert mission.mission_id in player.completed_missions
    
    def test_delivery_mission_does_not_complete_without_cargo(self):
        """Test that delivery missions don't complete if cargo is missing."""
        mission = MissionEntity(
            mission_id="MIS-DELIVERY-2",
            mission_type="delivery",
            mission_tier=2,
            payout_policy="auto",
            claim_scope="none",
            reward_status="ungranted",
            mission_state=MissionState.ACTIVE,
        )
        mission.target = {
            "target_type": "destination",
            "target_id": "SYS-002-DST-03",
            "system_id": "SYS-002",
        }
        mission.objectives = [
            {
                "objective_id": "OBJ-1",
                "objective_type": "deliver_cargo",
                "status": "pending",
                "parameters": {
                    "goods": [
                        {"good_id": "iron_ore", "quantity": 5}
                    ]
                }
            }
        ]
        
        # Create player state WITHOUT cargo
        player = PlayerState(
            player_id="test_player",
            credits=1000,
            active_missions=["MIS-DELIVERY-2"],
        )
        player.current_system_id = "SYS-002"
        player.current_destination_id = "SYS-002-DST-03"
        player.cargo_by_ship["active"] = {}  # No cargo
        
        # Create mission manager
        manager = MissionManager()
        manager.missions[mission.mission_id] = mission
        
        # Evaluate on arrival
        result = evaluate_active_missions(
            mission_manager=manager,
            player_state=player,
            current_system_id="SYS-002",
            current_destination_id="SYS-002-DST-03",
            event_context={"event": "travel_arrival"},
            world_seed=12345,
            turn=1,
        )
        
        # Assert mission NOT completed
        assert mission.mission_state == MissionState.ACTIVE
        assert mission.outcome is None
        assert mission.mission_id not in result["completed_mission_ids"]
        assert mission.mission_id in player.active_missions
    
    def test_exploration_mission_does_not_complete_at_wrong_destination(self):
        """Test that exploration missions don't complete at wrong destination."""
        mission = MissionEntity(
            mission_id="MIS-EXPLORE-2",
            mission_type="exploration",
            mission_tier=2,
            payout_policy="auto",
            claim_scope="none",
            reward_status="ungranted",
            mission_state=MissionState.ACTIVE,
        )
        mission.target = {
            "target_type": "destination",
            "target_id": "SYS-001-DST-05",
            "system_id": "SYS-001",
        }
        
        # Create player state at different destination
        player = PlayerState(
            player_id="test_player",
            credits=1000,
            active_missions=["MIS-EXPLORE-2"],
        )
        player.current_system_id = "SYS-001"
        player.current_destination_id = "SYS-001-DST-01"  # Wrong destination
        
        # Create mission manager
        manager = MissionManager()
        manager.missions[mission.mission_id] = mission
        
        # Evaluate on arrival
        result = evaluate_active_missions(
            mission_manager=manager,
            player_state=player,
            current_system_id="SYS-001",
            current_destination_id="SYS-001-DST-01",
            event_context={"event": "travel_arrival"},
            world_seed=12345,
            turn=1,
        )
        
        # Assert mission NOT completed
        assert mission.mission_state == MissionState.ACTIVE
        assert mission.outcome is None
        assert mission.mission_id not in result["completed_mission_ids"]
    
    def test_objective_conversion_from_legacy_delivery(self):
        """Test that delivery missions convert objectives correctly."""
        mission = MissionEntity(
            mission_id="MIS-DELIVERY-3",
            mission_type="delivery",
            mission_tier=2,
            payout_policy="auto",
            claim_scope="none",
            reward_status="ungranted",
        )
        mission.target = {
            "target_type": "destination",
            "target_id": "SYS-002-DST-03",
        }
        mission.objectives = [
            {
                "objective_id": "OBJ-1",
                "objective_type": "deliver_cargo",
                "status": "pending",
                "parameters": {
                    "goods": [
                        {"good_id": "steel_ingots", "quantity": 10}
                    ]
                }
            }
        ]
        
        objectives = convert_mission_objectives_to_canonical(mission)
        
        assert len(objectives) == 1
        obj = objectives[0]
        assert obj.objective_type == "deliver_cargo"
        assert obj.target_type == "item"
        assert obj.target_id == "steel_ingots"
        assert obj.required_count == 10
        assert "cargo_item_id" in obj.parameters
        assert obj.parameters["cargo_item_id"] == "steel_ingots"
    
    def test_objective_conversion_from_legacy_exploration(self):
        """Test that exploration missions convert objectives correctly."""
        mission = MissionEntity(
            mission_id="MIS-EXPLORE-3",
            mission_type="exploration",
            mission_tier=2,
            payout_policy="auto",
            claim_scope="none",
            reward_status="ungranted",
        )
        mission.target = {
            "target_type": "destination",
            "target_id": "SYS-019-DST-05",
        }
        
        objectives = convert_mission_objectives_to_canonical(mission)
        
        assert len(objectives) == 1
        obj = objectives[0]
        assert obj.objective_type == "destination_visited"
        assert obj.target_type == "destination"
        assert obj.target_id == "SYS-019-DST-05"
        assert obj.required_count == 1
    
    def test_cargo_acquired_objective_progress_tracking(self):
        """Test that cargo_acquired objectives track progress incrementally."""
        from mission_domain import Objective
        
        objective = Objective(
            objective_id="OBJ-1",
            objective_type="cargo_acquired",
            target_type="item",
            target_id="iron_ore",
            required_count=10,
        )
        
        player = PlayerState(player_id="test", credits=1000)
        player.cargo_by_ship["active"] = {"iron_ore": 5}
        
        context = MissionEventContext(
            event_type="cargo_change",
            current_system_id="SYS-001",
            cargo_snapshot={"iron_ore": 5},
        )
        
        # Evaluate - should not complete yet
        result = evaluate_objective(objective, context, player)
        assert not result
        assert objective.current_count == 5
        assert not objective.is_complete
        
        # Add more cargo
        player.cargo_by_ship["active"]["iron_ore"] = 10
        context.cargo_snapshot = {"iron_ore": 10}
        
        # Evaluate again - should complete
        result = evaluate_objective(objective, context, player)
        assert result
        assert objective.current_count == 10
        assert objective.is_complete
