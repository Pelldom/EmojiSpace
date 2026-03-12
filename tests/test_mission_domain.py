"""
Tests for mission domain types (Commit 1).

Validates Objective, RewardBundle, and MissionOutcome normalization.
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"
sys.path.insert(0, str(SRC_ROOT))

import pytest
from mission_domain import (
    Objective,
    RewardBundle,
    CargoGrant,
    ModuleGrant,
    HullVoucherGrant,
)
from mission_entity import MissionEntity, MissionOutcome, MissionState


class TestObjective:
    """Test Objective model."""
    
    def test_objective_creation(self):
        """Test basic objective creation."""
        obj = Objective(
            objective_id="OBJ-1",
            objective_type="destination_visited",
            target_type="destination",
            target_id="SYS-001-DST-01",
            required_count=1,
        )
        assert obj.objective_id == "OBJ-1"
        assert obj.objective_type == "destination_visited"
        assert obj.target_id == "SYS-001-DST-01"
        assert obj.required_count == 1
        assert obj.current_count == 0
        assert not obj.is_complete
    
    def test_objective_progress(self):
        """Test progress tracking."""
        obj = Objective(
            objective_id="OBJ-1",
            objective_type="cargo_acquired",
            required_count=5,
        )
        assert not obj.is_complete
        
        obj.mark_progress(3)
        assert obj.current_count == 3
        assert not obj.is_complete
        
        obj.mark_progress(2)
        assert obj.current_count == 5
        assert obj.is_complete
    
    def test_objective_recompute(self):
        """Test recompute_complete logic."""
        obj = Objective(
            objective_id="OBJ-1",
            objective_type="cargo_acquired",
            required_count=3,
            current_count=2,
        )
        obj.recompute_complete()
        assert not obj.is_complete
        
        obj.current_count = 3
        obj.recompute_complete()
        assert obj.is_complete
    
    def test_objective_serialization(self):
        """Test to_dict/from_dict round-trip."""
        obj = Objective(
            objective_id="OBJ-1",
            objective_type="destination_visited",
            target_type="destination",
            target_id="SYS-001-DST-01",
            required_count=1,
            current_count=1,
            is_complete=True,
            parameters={"test": "value"},
        )
        
        data = obj.to_dict()
        restored = Objective.from_dict(data)
        
        assert restored.objective_id == obj.objective_id
        assert restored.objective_type == obj.objective_type
        assert restored.target_type == obj.target_type
        assert restored.target_id == obj.target_id
        assert restored.required_count == obj.required_count
        assert restored.current_count == obj.current_count
        assert restored.is_complete == obj.is_complete
        assert restored.parameters == obj.parameters
    
    def test_objective_from_legacy_destination_visited(self):
        """Test conversion from legacy destination_visited format."""
        legacy = {
            "objective_id": "OBJ-1",
            "objective_type": "destination_visited",
            "status": "pending",
            "parameters": {
                "destination_id": "SYS-001-DST-01",
                "system_id": "SYS-001",
            },
        }
        
        obj = Objective.from_legacy_dict(legacy)
        assert obj.objective_type == "destination_visited"
        assert obj.target_type == "destination"
        assert obj.target_id == "SYS-001-DST-01"
        assert obj.required_count == 1
    
    def test_objective_from_legacy_cargo_delivered(self):
        """Test conversion from legacy cargo_delivered format."""
        legacy = {
            "objective_id": "OBJ-1",
            "objective_type": "deliver_cargo",
            "status": "pending",
            "parameters": {
                "goods": [
                    {"good_id": "iron_ore", "quantity": 5}
                ],
            },
        }
        
        obj = Objective.from_legacy_dict(legacy)
        assert obj.objective_type == "deliver_cargo"
        assert obj.target_type == "item"
        assert obj.target_id == "iron_ore"
        assert obj.required_count == 5


class TestRewardBundle:
    """Test RewardBundle model."""
    
    def test_empty_bundle(self):
        """Test empty bundle detection."""
        bundle = RewardBundle()
        assert bundle.is_empty()
        
        bundle.credits = 100
        assert not bundle.is_empty()
    
    def test_credits_only(self):
        """Test credits-only bundle."""
        bundle = RewardBundle(credits=5000)
        assert not bundle.is_empty()
        
        lines = bundle.to_reward_summary_lines()
        assert len(lines) == 1
        assert "+5000 credits" in lines[0]
    
    def test_cargo_grants(self):
        """Test cargo grants."""
        bundle = RewardBundle(
            cargo_grants=[
                CargoGrant(item_id="iron_ore", quantity=10),
                CargoGrant(item_id="steel_ingots", quantity=5),
            ]
        )
        assert not bundle.is_empty()
        
        lines = bundle.to_reward_summary_lines()
        assert len(lines) == 2
        assert any("10x iron_ore" in line for line in lines)
        assert any("5x steel_ingots" in line for line in lines)
    
    def test_module_grants(self):
        """Test module grants."""
        bundle = RewardBundle(
            module_grants=[
                ModuleGrant(module_id="ship_module_weapon_mk1"),
                ModuleGrant(module_id="ship_module_defense_mk2", quantity=2),
            ]
        )
        assert not bundle.is_empty()
        
        lines = bundle.to_reward_summary_lines()
        assert len(lines) == 2
        assert any("ship_module_weapon_mk1" in line for line in lines)
        assert any("2x ship_module_defense_mk2" in line for line in lines)
    
    def test_hull_vouchers(self):
        """Test hull voucher grants."""
        bundle = RewardBundle(
            hull_vouchers=[
                HullVoucherGrant(hull_id="xc_t3_bulwark"),
            ]
        )
        assert not bundle.is_empty()
        
        lines = bundle.to_reward_summary_lines()
        assert len(lines) == 1
        assert "Hull voucher: xc_t3_bulwark" in lines[0]
    
    def test_mixed_rewards(self):
        """Test bundle with multiple reward types."""
        bundle = RewardBundle(
            credits=1000,
            cargo_grants=[CargoGrant(item_id="iron_ore", quantity=5)],
            module_grants=[ModuleGrant(module_id="ship_module_weapon_mk1")],
        )
        
        lines = bundle.to_reward_summary_lines()
        assert len(lines) == 3
        assert any("+1000 credits" in line for line in lines)
        assert any("5x iron_ore" in line for line in lines)
        assert any("ship_module_weapon_mk1" in line for line in lines)
    
    def test_from_reward_calculation_credits(self):
        """Test creating bundle from credit reward calculation."""
        reward_dict = {"type": "credits", "amount": 5000}
        bundle = RewardBundle.from_reward_calculation(reward_dict)
        
        assert bundle.credits == 5000
        assert len(bundle.cargo_grants) == 0
        assert len(bundle.module_grants) == 0
    
    def test_from_reward_calculation_goods(self):
        """Test creating bundle from goods reward calculation."""
        reward_dict = {"type": "goods", "sku_id": "iron_ore", "quantity": 10}
        bundle = RewardBundle.from_reward_calculation(reward_dict)
        
        assert bundle.credits == 0
        assert len(bundle.cargo_grants) == 1
        assert bundle.cargo_grants[0].item_id == "iron_ore"
        assert bundle.cargo_grants[0].quantity == 10
    
    def test_from_reward_calculation_module(self):
        """Test creating bundle from module reward calculation."""
        reward_dict = {"type": "module", "module_id": "ship_module_weapon_mk1"}
        bundle = RewardBundle.from_reward_calculation(reward_dict)
        
        assert len(bundle.module_grants) == 1
        assert bundle.module_grants[0].module_id == "ship_module_weapon_mk1"
    
    def test_from_reward_calculation_hull_voucher(self):
        """Test creating bundle from hull voucher reward calculation."""
        reward_dict = {"type": "hull_voucher", "hull_id": "xc_t3_bulwark"}
        bundle = RewardBundle.from_reward_calculation(reward_dict)
        
        assert len(bundle.hull_vouchers) == 1
        assert bundle.hull_vouchers[0].hull_id == "xc_t3_bulwark"
    
    def test_to_reward_summary_dict(self):
        """Test conversion to legacy reward_summary format."""
        bundle = RewardBundle(
            credits=1000,
            cargo_grants=[CargoGrant(item_id="iron_ore", quantity=5)],
            module_grants=[ModuleGrant(module_id="ship_module_weapon_mk1")],
        )
        
        summary = bundle.to_reward_summary_dict()
        assert len(summary) == 3
        
        credits_entry = next((e for e in summary if e.get("field") == "credits"), None)
        assert credits_entry is not None
        assert credits_entry["delta"] == 1000
        
        goods_entry = next((e for e in summary if e.get("field") == "goods"), None)
        assert goods_entry is not None
        assert goods_entry["sku_id"] == "iron_ore"
        assert goods_entry["quantity"] == 5
        
        module_entry = next((e for e in summary if e.get("field") == "module"), None)
        assert module_entry is not None
        assert module_entry["module_id"] == "ship_module_weapon_mk1"


class TestMissionOutcomeNormalization:
    """Test MissionOutcome enum normalization in serialization."""
    
    def test_outcome_enum_storage(self):
        """Test that outcome is stored as enum."""
        mission = MissionEntity(
            mission_id="TEST-1",
            mission_type="delivery",
            mission_tier=1,
            payout_policy="auto",
            claim_scope="none",
            reward_status="ungranted",
        )
        mission.outcome = MissionOutcome.COMPLETED
        
        assert isinstance(mission.outcome, MissionOutcome)
        assert mission.outcome == MissionOutcome.COMPLETED
    
    def test_outcome_serialization_round_trip(self):
        """Test that outcome serializes and deserializes correctly."""
        mission = MissionEntity(
            mission_id="TEST-1",
            mission_type="delivery",
            mission_tier=1,
            payout_policy="auto",
            claim_scope="none",
            reward_status="ungranted",
        )
        mission.mission_state = MissionState.RESOLVED
        mission.outcome = MissionOutcome.COMPLETED
        
        # Serialize
        data = mission.to_dict()
        assert data["outcome"] == "completed"
        
        # Deserialize
        restored = MissionEntity.from_dict(data)
        assert isinstance(restored.outcome, MissionOutcome)
        assert restored.outcome == MissionOutcome.COMPLETED
    
    def test_outcome_string_deserialization(self):
        """Test that string outcomes are normalized to enum."""
        data = {
            "mission_id": "TEST-1",
            "mission_type": "delivery",
            "mission_tier": 1,
            "payout_policy": "auto",
            "claim_scope": "none",
            "reward_status": "ungranted",
            "mission_state": "resolved",
            "outcome": "completed",  # String format
        }
        
        mission = MissionEntity.from_dict(data)
        assert isinstance(mission.outcome, MissionOutcome)
        assert mission.outcome == MissionOutcome.COMPLETED
    
    def test_outcome_uppercase_string_deserialization(self):
        """Test that uppercase string outcomes are normalized."""
        data = {
            "mission_id": "TEST-1",
            "mission_type": "delivery",
            "mission_tier": 1,
            "payout_policy": "auto",
            "claim_scope": "none",
            "reward_status": "ungranted",
            "mission_state": "resolved",
            "outcome": "COMPLETED",  # Uppercase
        }
        
        mission = MissionEntity.from_dict(data)
        assert isinstance(mission.outcome, MissionOutcome)
        assert mission.outcome == MissionOutcome.COMPLETED
    
    def test_outcome_none_handling(self):
        """Test that None outcome is preserved."""
        mission = MissionEntity(
            mission_id="TEST-1",
            mission_type="delivery",
            mission_tier=1,
            payout_policy="auto",
            claim_scope="none",
            reward_status="ungranted",
        )
        mission.outcome = None
        
        data = mission.to_dict()
        assert data["outcome"] is None
        
        restored = MissionEntity.from_dict(data)
        assert restored.outcome is None
    
    def test_outcome_invalid_string_handling(self):
        """Test that invalid outcome strings become None."""
        data = {
            "mission_id": "TEST-1",
            "mission_type": "delivery",
            "mission_tier": 1,
            "payout_policy": "auto",
            "claim_scope": "none",
            "reward_status": "ungranted",
            "outcome": "invalid_outcome",
        }
        
        mission = MissionEntity.from_dict(data)
        assert mission.outcome is None
    
    def test_all_outcome_values(self):
        """Test all valid outcome enum values."""
        outcomes = [MissionOutcome.COMPLETED, MissionOutcome.FAILED, MissionOutcome.ABANDONED]
        
        for outcome in outcomes:
            mission = MissionEntity(
                mission_id="TEST-1",
                mission_type="delivery",
                mission_tier=1,
                payout_policy="auto",
                claim_scope="none",
                reward_status="ungranted",
            )
            mission.outcome = outcome
            
            data = mission.to_dict()
            restored = MissionEntity.from_dict(data)
            
            assert restored.outcome == outcome
            assert isinstance(restored.outcome, MissionOutcome)
