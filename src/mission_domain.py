"""
Mission domain types - canonical models for objectives and rewards.

This module provides the unified domain model for mission objectives and rewards,
used consistently across evaluation, preview, and payout.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List


@dataclass
class Objective:
    """
    Canonical objective model used at runtime.
    
    Objectives track progress toward mission completion conditions.
    All mission completion is driven by objective evaluation, not mission_type branching.
    """
    objective_id: str
    objective_type: str  # destination_visited, cargo_acquired, cargo_delivered, npc_destroyed, combat_victory
    target_type: str = ""  # destination, item, npc, system
    target_id: str = ""
    required_count: int = 1
    current_count: int = 0
    is_complete: bool = False
    parameters: Dict[str, Any] = field(default_factory=dict)
    
    def mark_progress(self, delta: int = 1) -> None:
        """Increment progress by delta and recompute completion."""
        self.current_count = max(0, self.current_count + delta)
        self.recompute_complete()
    
    def recompute_complete(self) -> None:
        """Recompute is_complete based on current_count >= required_count."""
        self.is_complete = self.current_count >= self.required_count
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dict for persistence."""
        return {
            "objective_id": self.objective_id,
            "objective_type": self.objective_type,
            "target_type": self.target_type,
            "target_id": self.target_id,
            "required_count": self.required_count,
            "current_count": self.current_count,
            "is_complete": self.is_complete,
            "parameters": dict(self.parameters),
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Objective":
        """Deserialize from dict."""
        obj = cls(
            objective_id=str(data.get("objective_id", "")),
            objective_type=str(data.get("objective_type", "")),
            target_type=str(data.get("target_type", "")),
            target_id=str(data.get("target_id", "")),
            required_count=int(data.get("required_count", 1)),
            current_count=int(data.get("current_count", 0)),
            is_complete=bool(data.get("is_complete", False)),
            parameters=dict(data.get("parameters", {})),
        )
        # Ensure is_complete is consistent with counts
        obj.recompute_complete()
        return obj
    
    @classmethod
    def from_legacy_dict(cls, data: Dict[str, Any]) -> "Objective":
        """
        Convert legacy objective dict format to canonical Objective.
        
        Legacy format may have:
        - objective_id, objective_type, status, parameters
        - target information in parameters or mission.target
        """
        obj_id = data.get("objective_id", "")
        obj_type = data.get("objective_type", "")
        params = dict(data.get("parameters", {}))
        
        # Extract target info from parameters or use defaults
        target_type = params.get("target_type", "")
        target_id = params.get("target_id", "") or params.get("destination_id", "")
        
        # For destination_visited, extract from parameters
        if obj_type == "destination_visited":
            target_type = "destination"
            target_id = params.get("destination_id", "")
        
        # For cargo objectives, extract from goods list
        if obj_type in ("cargo_delivered", "cargo_acquired", "deliver_cargo"):
            target_type = "item"
            goods = params.get("goods", [])
            if goods and isinstance(goods, list) and len(goods) > 0:
                first_good = goods[0] if isinstance(goods[0], dict) else {}
                target_id = first_good.get("good_id", "")
                required_count = int(first_good.get("quantity", 1))
            else:
                target_id = ""
                required_count = 1
        else:
            required_count = 1
        
        return cls(
            objective_id=obj_id,
            objective_type=obj_type,
            target_type=target_type,
            target_id=target_id,
            required_count=required_count,
            current_count=0,
            is_complete=False,
            parameters=params,
        )


@dataclass
class CargoGrant:
    """Single cargo item grant."""
    item_id: str
    quantity: int


@dataclass
class ModuleGrant:
    """Single module grant."""
    module_id: str
    quantity: int = 1


@dataclass
class HullVoucherGrant:
    """Single hull voucher grant."""
    hull_id: str
    quantity: int = 1


@dataclass
class RewardBundle:
    """
    Unified reward representation used by both preview and payout.
    
    This replaces the fragmented reward_summary format and ensures
    consistent display and application of rewards.
    """
    credits: int = 0
    cargo_grants: List[CargoGrant] = field(default_factory=list)
    module_grants: List[ModuleGrant] = field(default_factory=list)
    hull_vouchers: List[HullVoucherGrant] = field(default_factory=list)
    
    def is_empty(self) -> bool:
        """Check if bundle has any rewards."""
        return (
            self.credits == 0
            and len(self.cargo_grants) == 0
            and len(self.module_grants) == 0
            and len(self.hull_vouchers) == 0
        )
    
    def to_reward_summary_lines(self) -> List[str]:
        """
        Convert to list of display lines for UI.
        
        Returns list of strings like:
        - "+5000 credits"
        - "26x decorative_metals"
        - "ship_module_weapon_mk1"
        - "Hull voucher: xc_t3_bulwark"
        """
        lines: List[str] = []
        
        if self.credits > 0:
            lines.append(f"{self.credits:+d} credits")
        
        for cargo in self.cargo_grants:
            lines.append(f"{cargo.quantity}x {cargo.item_id}")
        
        for module in self.module_grants:
            if module.quantity > 1:
                lines.append(f"{module.quantity}x {module.module_id}")
            else:
                lines.append(module.module_id)
        
        for voucher in self.hull_vouchers:
            if voucher.quantity > 1:
                lines.append(f"{voucher.quantity}x Hull voucher: {voucher.hull_id}")
            else:
                lines.append(f"Hull voucher: {voucher.hull_id}")
        
        # Return "No rewards" if bundle is empty (Commit 4)
        return lines if lines else ["No rewards"]
    
    def to_reward_summary_dict(self) -> List[Dict[str, Any]]:
        """
        Convert to legacy reward_summary format for backward compatibility.
        
        Returns list of dicts compatible with existing CLI formatting.
        """
        summary: List[Dict[str, Any]] = []
        
        if self.credits > 0:
            summary.append({"field": "credits", "delta": self.credits})
        
        for cargo in self.cargo_grants:
            summary.append({
                "field": "goods",
                "sku_id": cargo.item_id,
                "quantity": cargo.quantity,
            })
        
        for module in self.module_grants:
            summary.append({
                "field": "module",
                "module_id": module.module_id,
            })
        
        for voucher in self.hull_vouchers:
            summary.append({
                "field": "hull_voucher",
                "hull_id": voucher.hull_id,
            })
        
        return summary
    
    @classmethod
    def from_reward_calculation(cls, reward_dict: Dict[str, Any]) -> "RewardBundle":
        """
        Create RewardBundle from _calculate_mission_reward output.
        
        reward_dict has structure:
        - {"type": "credits", "amount": int}
        - {"type": "goods", "sku_id": str, "quantity": int}
        - {"type": "module", "module_id": str}
        - {"type": "hull_voucher", "hull_id": str}
        """
        bundle = cls()
        
        reward_type = reward_dict.get("type", "")
        
        if reward_type == "credits":
            bundle.credits = int(reward_dict.get("amount", 0))
        elif reward_type == "goods":
            bundle.cargo_grants.append(CargoGrant(
                item_id=str(reward_dict.get("sku_id", "")),
                quantity=int(reward_dict.get("quantity", 0)),
            ))
        elif reward_type == "module":
            bundle.module_grants.append(ModuleGrant(
                module_id=str(reward_dict.get("module_id", "")),
            ))
        elif reward_type == "hull_voucher":
            bundle.hull_vouchers.append(HullVoucherGrant(
                hull_id=str(reward_dict.get("hull_id", "")),
            ))
        
        return bundle
