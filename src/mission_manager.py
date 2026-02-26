from dataclasses import dataclass, field
from typing import Any, Dict, List

try:
    from crew_modifiers import compute_crew_modifiers
except ModuleNotFoundError:
    from src.crew_modifiers import compute_crew_modifiers

from mission_entity import MissionEntity, MissionOutcome, MissionState
from player_state import PlayerState
from reward_applicator import apply_mission_rewards, _is_data_cargo
import math
import json
import random
from pathlib import Path


@dataclass
class MissionManager:
    missions: Dict[str, MissionEntity] = field(default_factory=dict)
    offered: List[str] = field(default_factory=list)
    # DataNet-specific mission offers (per-location, per-turn; ephemeral)
    datanet_offers: Dict[str, List[str]] = field(default_factory=dict)
    
    def calculate_reward_preview(self, mission: MissionEntity, world_seed: int | str | None = None) -> Dict[str, Any]:
        """
        Calculate reward preview for a mission (Phase 7.11.3).
        
        This function does NOT modify mission state, grant rewards, or log events.
        It is purely for presentation layer preview.
        
        Args:
            mission: MissionEntity to calculate preview for
            world_seed: Optional world seed for deterministic selection
        
        Returns:
            Dict with reward preview structure or empty dict if calculation fails
        """
        if mission.reward_status == "granted":
            # If already granted, don't recalculate - return empty (caller should use stored value)
            return {}
        
        try:
            reward_profiles = _load_reward_profiles()
            catalogs = {}
            try:
                from data_catalog import load_data_catalog
                catalogs["data_catalog"] = load_data_catalog()
            except Exception:
                pass
            
            reward = _calculate_mission_reward(mission, reward_profiles, catalogs, world_seed)
            reward_type = reward.get("type")
            
            if reward_type == "credits":
                return {"credits": reward.get("amount", 0)}
            elif reward_type == "goods":
                return {
                    "goods": {
                        "sku_id": reward.get("sku_id"),
                        "quantity": reward.get("quantity", 0)
                    }
                }
            elif reward_type == "module":
                return {
                    "module": {
                        "module_id": reward.get("module_id")
                    }
                }
            elif reward_type == "hull_voucher":
                return {
                    "hull_voucher": {
                        "hull_id": reward.get("hull_id")
                    }
                }
            else:
                return {}
        except (ValueError, KeyError):
            # If calculation fails, return empty dict (no preview available)
            return {}

    def offer(self, mission: MissionEntity, logger=None, turn: int = 0) -> None:
        self.missions[mission.mission_id] = mission
        if mission.mission_id not in self.offered:
            self.offered.append(mission.mission_id)
        _log_manager(logger, turn, "offer", mission.mission_id)

    def accept(
        self,
        mission_id: str,
        player: PlayerState,
        logger=None,
        turn: int = 0,
        location_type: str | None = None,
        ship: Any | None = None,
    ) -> tuple[bool, str | None]:
        """Accept a mission with tier-based and global cap validation.
        
        Returns:
            Tuple of (accepted: bool, error_reason: str | None)
            error_reason will be "mission_accept_failed_total_cap" or 
            "mission_accept_failed_tier_cap" if rejected.
        """
        mission = self.missions.get(mission_id)
        if mission is None:
            return False, "mission_not_found"
        
        # DIAGNOSTIC: Log mission_manager instance ID during accept
        if logger is not None:
            _log_manager(logger, turn, "accept_instance_check", mission_id, detail=f"mission_manager_id={id(self)}")
        
        # Tier-based inverse caps
        TIER_CAPS = {
            1: 5,
            2: 4,
            3: 3,
            4: 2,
            5: 1,
        }
        GLOBAL_CAP = 5
        
        # Collect ALL ACTIVE missions across entire galaxy (not just player.active_missions)
        # Count ALL missions in manager with state == ACTIVE (galaxy-wide, not filtered by location/system)
        active_missions: list[MissionEntity] = []
        for m in self.missions.values():
            if m.mission_state == MissionState.ACTIVE:
                active_missions.append(m)
        
        # Diagnostic logging
        total_active_before = len(active_missions)
        tier_counts_before: dict[int, int] = {}
        for active_mission in active_missions:
            tier = int(active_mission.mission_tier)
            tier_counts_before[tier] = tier_counts_before.get(tier, 0) + 1
        
        mission_tier = int(mission.mission_tier)
        tier_cap = TIER_CAPS.get(mission_tier, 1)  # Default to 1 if tier not in mapping
        active_count_for_tier_before = tier_counts_before.get(mission_tier, 0)
        
        if logger is not None:
            _log_manager(
                logger, turn, "accept_validation", mission_id,
                detail=(
                    f"total_active_before={total_active_before} "
                    f"tier_active_before={active_count_for_tier_before} "
                    f"tier_cap={tier_cap} global_cap={GLOBAL_CAP}"
                )
            )
        
        # Check global cap
        if total_active_before >= GLOBAL_CAP:
            _log_manager(logger, turn, "accept_failed_total_cap", mission_id)
            return False, "mission_accept_failed_total_cap"
        
        # Check tier cap for the mission being accepted
        if active_count_for_tier_before >= tier_cap:
            _log_manager(logger, turn, "accept_failed_tier_cap", mission_id)
            return False, "mission_accept_failed_tier_cap"
        
        # Validation passed - proceed with acceptance
        mission.mission_state = MissionState.ACTIVE
        if mission_id in self.offered:
            self.offered.remove(mission_id)
        if mission_id not in player.active_missions:
            player.active_missions.append(mission_id)
        _log_manager(logger, turn, "accept", mission_id)
        return True, None

    def complete(self, mission_id: str, player: PlayerState, logger=None, turn: int = 0) -> None:
        """Complete a mission (Phase 7.11.1: no rewards granted yet)."""
        mission = self.missions.get(mission_id)
        if mission is None:
            return
        mission.mission_state = MissionState.RESOLVED
        mission.outcome = MissionOutcome.COMPLETED
        _remove_from_list(player.active_missions, mission_id)
        if mission_id not in player.completed_missions:
            player.completed_missions.append(mission_id)
        # Phase 7.11.1: Rewards not implemented yet (Phase 7.11.2 will handle via reward_profile_id)
        # Do NOT call apply_mission_rewards - rewards will be materialized in Phase 7.11.2
        _log_manager(logger, turn, "complete", mission_id)

    def fail(self, mission_id: str, player: PlayerState, reason: str | None = None, logger=None, turn: int = 0) -> None:
        mission = self.missions.get(mission_id)
        if mission is None:
            return
        mission.mission_state = MissionState.RESOLVED
        mission.outcome = MissionOutcome.FAILED
        mission.failure_reason = reason
        _remove_from_list(player.active_missions, mission_id)
        if mission_id not in player.failed_missions:
            player.failed_missions.append(mission_id)
        _log_manager(logger, turn, "fail", mission_id)

    def abandon(self, mission_id: str, player: PlayerState, reason: str | None = None, logger=None, turn: int = 0) -> None:
        mission = self.missions.get(mission_id)
        if mission is None:
            return
        mission.mission_state = MissionState.RESOLVED
        mission.outcome = MissionOutcome.ABANDONED
        mission.failure_reason = reason
        _remove_from_list(player.active_missions, mission_id)
        _log_manager(logger, turn, "abandon", mission_id)

    def clear_datanet_offers(self, location_id: str | None = None) -> None:
        """Clear DataNet mission offers.

        If location_id is None, clears all DataNet offers (e.g., on turn advance).
        Otherwise, clears offers only for the specified location.
        """
        if location_id is None:
            self.datanet_offers.clear()
        else:
            self.datanet_offers.pop(str(location_id), None)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "missions": {mission_id: mission.to_dict() for mission_id, mission in self.missions.items()},
            "offered": list(self.offered),
        }

    @classmethod
    def from_dict(cls, payload: Dict[str, Any]) -> "MissionManager":
        manager = cls()
        missions_payload = payload.get("missions", {})
        for mission_id, data in missions_payload.items():
            mission = MissionEntity.from_dict(data)
            mission.mission_id = mission_id
            manager.missions[mission_id] = mission
        manager.offered = list(payload.get("offered", []))
        return manager


def _remove_from_list(items: List[str], value: str) -> None:
    if value in items:
        items.remove(value)


def _effective_mission_slots(*, player: PlayerState, location_type: str | None, ship: Any | None) -> int:
    slots = int(player.mission_slots)
    if location_type not in {"bar", "administration"}:
        return slots
    if ship is None:
        return slots
    crew_mods = compute_crew_modifiers(ship)
    return slots + int(crew_mods.mission_slot_bonus)


def _log_manager(logger, turn: int, action: str, mission_id: str, detail: str | None = None) -> None:
    if logger is None:
        return
    detail_text = f" {detail}" if detail else ""
    logger.log(turn=turn, action="mission_manager", state_change=f"{action} mission_id={mission_id}{detail_text}")


def _load_reward_profiles() -> Dict[str, Any]:
    """
    Load reward profiles from data/reward_profiles.json (Phase 7.11.2a).
    
    Returns:
        Dict mapping reward_profile_id to profile data
    """
    root = Path(__file__).resolve().parents[1]
    profile_path = root / "data" / "reward_profiles.json"
    
    if not profile_path.exists():
        return {}
    
    data = json.loads(profile_path.read_text(encoding="utf-8"))
    profiles_list = data.get("reward_profiles", [])
    
    # Convert list to dict keyed by reward_profile_id
    profiles_dict = {}
    for profile in profiles_list:
        profile_id = profile.get("reward_profile_id")
        if profile_id:
            profiles_dict[profile_id] = profile
    
    return profiles_dict


def evaluate_active_missions(
    *,
    mission_manager: "MissionManager",
    player_state: PlayerState,
    current_system_id: str,
    current_destination_id: str | None,
    event_context: Dict[str, Any],
    reward_profiles: Dict[str, Any] | None = None,
    world_seed: int | str | None = None,
    logger=None,
    turn: int = 0,
) -> Dict[str, Any]:
    """
    Centralized mission lifecycle evaluation authority (Phase 7.11.1).
    
    Evaluates all active missions for completion or failure conditions.
    Deterministic: purely derived from current state + event_context, no RNG.
    
    Args:
        mission_manager: MissionManager instance containing all missions
        player_state: Current player state
        current_system_id: Current system ID
        current_destination_id: Current destination ID (may be None)
        event_context: Dict with event information (e.g., {"event": "travel_arrival"})
        logger: Optional logger instance
        turn: Current turn number
    
    Returns:
        Dict with:
        - evaluated_mission_ids: List of mission IDs that were evaluated
        - completed_mission_ids: List of mission IDs that were completed
        - failed_mission_ids: List of mission IDs that were failed (empty for now)
        - logs: List of log entries (minimal)
    """
    result = {
        "evaluated_mission_ids": [],
        "completed_mission_ids": [],
        "failed_mission_ids": [],
        "logs": [],
    }
    
    # Get all active missions
    active_mission_ids = list(player_state.active_missions)
    
    if not active_mission_ids:
        return result
    
    event_type = event_context.get("event", "unknown")
    
    # Log evaluation start
    if logger is not None:
        logger.log(
            turn=turn,
            action="mission_eval:start",
            state_change=(
                f"event={event_type} active_count={len(active_mission_ids)} "
                f"system_id={current_system_id} destination_id={current_destination_id or 'none'}"
            ),
        )
    
    # Evaluate each active mission
    for mission_id in active_mission_ids:
        mission = mission_manager.missions.get(mission_id)
        if mission is None:
            continue
        if mission.mission_state != MissionState.ACTIVE:
            continue
        
        result["evaluated_mission_ids"].append(mission_id)
        
        # Time limit handling (Phase 7.11.1 - Preparation Only)
        # days_remaining semantics:
        # - None → no time limit (infinite duration)
        # - > 0 → number of turns remaining
        # - 0 → expired (terminal state; should fail mission)
        # - < 0 → invalid state (should never occur)
        # Only decrement if NOT None AND event is turn_tick. Never treat 0 as infinite.
        # CRITICAL: days_remaining must ONLY decrement on turn_tick, not on travel_arrival or other events.
        days_remaining = mission.persistent_state.get("days_remaining")
        if days_remaining is not None and event_type == "turn_tick":
            # Decrement days_remaining ONLY on turn_tick
            days_remaining -= 1
            mission.persistent_state["days_remaining"] = days_remaining
            
            # Check if expired (<= 0)
            if days_remaining <= 0:
                # Mission expired - transition to failed
                old_state = str(mission.mission_state)
                mission.mission_state = MissionState.RESOLVED
                mission.outcome = MissionOutcome.FAILED
                mission.failure_reason = "expired"
                mission.persistent_state["resolved_turn"] = turn
                
                # Remove from active missions
                _remove_from_list(player_state.active_missions, mission_id)
                
                # Add to failed missions (if such collection exists)
                # For now, just mark as resolved with failed outcome
                
                result["failed_mission_ids"].append(mission_id)
                
                # Log expiration
                if logger is not None:
                    logger.log(
                        turn=turn,
                        action="mission_eval:expired",
                        state_change=(
                            f"mission_id={mission_id} mission_type={mission.mission_type} "
                            f"days_remaining={days_remaining}"
                        ),
                    )
                    logger.log(
                        turn=turn,
                        action="mission_state_transition",
                        state_change=(
                            f"mission_id={mission_id} from={old_state} to=resolved "
                            f"outcome=failed reason=expired"
                        ),
                    )
                    result["logs"].append(f"mission_id={mission_id} outcome=failed reason=expired")
                
                # Skip further evaluation for this mission (already failed)
                continue
        
        # Evaluate delivery missions
        if mission.mission_type == "delivery":
            completed = _evaluate_delivery_mission(
                mission=mission,
                mission_manager=mission_manager,
                player_state=player_state,
                current_system_id=current_system_id,
                current_destination_id=current_destination_id,
                logger=logger,
                turn=turn,
            )
            if completed:
                result["completed_mission_ids"].append(mission_id)
                if logger is not None:
                    result["logs"].append(f"mission_id={mission_id} outcome=completed")
        
        # Other mission types (bounty, etc.) - not implemented yet
        # Will be added in future phases
    
    # Auto payout for completed missions (Phase 7.11.3)
    # Check all missions (not just active) for auto payout
    # Load reward profiles if not provided
    if reward_profiles is None:
        reward_profiles = _load_reward_profiles()
    
    # Load catalogs for reward calculation
    catalogs = {}
    try:
        from data_catalog import load_data_catalog
        catalogs["data_catalog"] = load_data_catalog()
    except Exception:
        pass  # Will fail later if needed
    
    for mission_id in list(mission_manager.missions.keys()):
        mission = mission_manager.missions.get(mission_id)
        if mission is None:
            continue
        
        # Check if mission is resolved and completed
        if mission.mission_state == MissionState.RESOLVED and mission.outcome == MissionOutcome.COMPLETED:
            # Guard against double payout: only pay when reward_status is 'ungranted'
            if mission.payout_policy == "auto" and mission.reward_status == "ungranted":
                # Calculate reward using unified authority
                try:
                    reward = _calculate_mission_reward(mission, reward_profiles, catalogs, world_seed)
                    reward_type = reward.get("type")
                    
                    # Apply reward based on type
                    applied = False
                    
                    if reward_type == "credits":
                        amount = reward.get("amount", 0)
                        player_state.credits += amount
                        applied = True
                        
                        if logger is not None:
                            logger.log(
                                turn=turn,
                                action="mission_reward_granted",
                                state_change=(
                                    f"mission_id={mission_id} payout_policy=auto "
                                    f"credits={amount} new_balance={player_state.credits}"
                                ),
                            )
                            result["logs"].append(f"mission_id={mission_id} reward_granted credits={amount}")
                    
                    elif reward_type == "goods":
                        sku_id = reward.get("sku_id")
                        quantity = reward.get("quantity", 0)
                        
                        # Check cargo capacity
                        if _check_cargo_capacity(player_state, sku_id, quantity, catalogs.get("data_catalog")):
                            # Add to cargo
                            player_state.cargo_by_ship.setdefault("active", {})
                            current_qty = player_state.cargo_by_ship["active"].get(sku_id, 0)
                            player_state.cargo_by_ship["active"][sku_id] = current_qty + quantity
                            applied = True
                            
                            if logger is not None:
                                logger.log(
                                    turn=turn,
                                    action="mission_reward_granted",
                                    state_change=(
                                        f"mission_id={mission_id} payout_policy=auto "
                                        f"goods={sku_id} quantity={quantity}"
                                    ),
                                )
                                result["logs"].append(f"mission_id={mission_id} reward_granted goods={sku_id} quantity={quantity}")
                        else:
                            # Insufficient capacity - skip reward
                            if logger is not None:
                                logger.log(
                                    turn=turn,
                                    action="mission_reward_error",
                                    state_change=f"mission_id={mission_id} error=insufficient_cargo_capacity",
                                )
                    
                    elif reward_type == "module":
                        module_id = reward.get("module_id")
                        
                        # Add to salvage_modules
                        if not hasattr(player_state, "salvage_modules"):
                            player_state.salvage_modules = []
                        if not isinstance(player_state.salvage_modules, list):
                            player_state.salvage_modules = []
                        
                        module_dict = {"module_id": module_id, "secondary_tags": []}
                        player_state.salvage_modules.append(module_dict)
                        applied = True
                        
                        if logger is not None:
                            logger.log(
                                turn=turn,
                                action="mission_reward_granted",
                                state_change=(
                                    f"mission_id={mission_id} payout_policy=auto "
                                    f"module={module_id}"
                                ),
                            )
                            result["logs"].append(f"mission_id={mission_id} reward_granted module={module_id}")
                    
                    elif reward_type == "hull_voucher":
                        hull_id = reward.get("hull_id")
                        voucher_sku = f"hull_voucher_{hull_id}"
                        
                        # Check data cargo capacity (vouchers are data cargo)
                        if _check_data_cargo_capacity(player_state, 1):
                            # Add voucher as data cargo
                            player_state.cargo_by_ship.setdefault("active", {})
                            current_qty = player_state.cargo_by_ship["active"].get(voucher_sku, 0)
                            player_state.cargo_by_ship["active"][voucher_sku] = current_qty + 1
                            applied = True
                            
                            if logger is not None:
                                logger.log(
                                    turn=turn,
                                    action="mission_reward_granted",
                                    state_change=(
                                        f"mission_id={mission_id} payout_policy=auto "
                                        f"hull_voucher={hull_id}"
                                    ),
                                )
                                result["logs"].append(f"mission_id={mission_id} reward_granted hull_voucher={hull_id}")
                        else:
                            # Insufficient capacity - skip reward
                            if logger is not None:
                                logger.log(
                                    turn=turn,
                                    action="mission_reward_error",
                                    state_change=f"mission_id={mission_id} error=insufficient_data_cargo_capacity",
                                )
                    
                    # Only update reward_status if reward was successfully applied
                    if applied:
                        mission.reward_status = "granted"
                        mission.reward_granted_turn = turn
                    
                except ValueError as e:
                    # Log error but don't fail evaluation
                    if logger is not None:
                        logger.log(
                            turn=turn,
                            action="mission_reward_error",
                            state_change=f"mission_id={mission_id} error={str(e)}",
                        )
    
    # Log evaluation completion
    if logger is not None and result["evaluated_mission_ids"]:
        logger.log(
            turn=turn,
            action="mission_eval:completed",
            state_change=(
                f"event={event_type} evaluated={len(result['evaluated_mission_ids'])} "
                f"completed={len(result['completed_mission_ids'])} "
                f"failed={len(result['failed_mission_ids'])}"
            ),
        )
    
    return result


def _calculate_mission_credit_reward(
    mission: MissionEntity,
    reward_profiles: Dict[str, Any],
) -> int:
    """
    Calculate credit reward for a mission (Phase 7.11.2a).
    
    Formula:
        reward = base_credits
                 * tier_multiplier_for_mission_tier
                 * (1 + distance_ly * distance_multiplier_per_ly)
    
    Args:
        mission: MissionEntity with reward_profile_id set
        reward_profiles: Dict mapping reward_profile_id to profile data
    
    Returns:
        Credit reward amount (int, floored)
    
    Raises:
        ValueError: If reward_profile_id not found or required fields missing
    """
    profile_id = mission.reward_profile_id
    if not profile_id:
        raise ValueError(f"Mission {mission.mission_id} has no reward_profile_id")
    
    # Lookup profile
    profile = reward_profiles.get(profile_id)
    if profile is None:
        raise ValueError(
            f"Reward profile '{profile_id}' not found for mission {mission.mission_id}"
        )
    
    # Validate required fields
    if "base_credits" not in profile:
        raise ValueError(
            f"Reward profile '{profile_id}' missing required field 'base_credits'"
        )
    if "tier_multiplier" not in profile:
        raise ValueError(
            f"Reward profile '{profile_id}' missing required field 'tier_multiplier'"
        )
    if "distance_multiplier_per_ly" not in profile:
        raise ValueError(
            f"Reward profile '{profile_id}' missing required field 'distance_multiplier_per_ly'"
        )
    
    base_credits = int(profile["base_credits"])
    distance_multiplier_per_ly = float(profile["distance_multiplier_per_ly"])
    
    # Get tier multiplier
    tier_multiplier_data = profile["tier_multiplier"]
    if isinstance(tier_multiplier_data, dict):
        tier_key = str(mission.mission_tier)
        if tier_key not in tier_multiplier_data:
            raise ValueError(
                f"Reward profile '{profile_id}' tier_multiplier missing tier {tier_key}"
            )
        tier_multiplier = float(tier_multiplier_data[tier_key])
    elif isinstance(tier_multiplier_data, list):
        # List indexed by tier (0-indexed, so tier 1 = index 0)
        tier_index = mission.mission_tier - 1
        if tier_index < 0 or tier_index >= len(tier_multiplier_data):
            raise ValueError(
                f"Reward profile '{profile_id}' tier_multiplier list too short for tier {mission.mission_tier}"
            )
        tier_multiplier = float(tier_multiplier_data[tier_index])
    else:
        raise ValueError(
            f"Reward profile '{profile_id}' tier_multiplier must be dict or list"
        )
    
    # Calculate reward
    distance_ly = mission.distance_ly
    reward = base_credits * tier_multiplier * (1 + distance_ly * distance_multiplier_per_ly)
    
    # Floor to int (no rounding)
    return int(math.floor(reward))


def _calculate_mission_reward(
    mission: MissionEntity,
    reward_profiles: Dict[str, Any],
    catalogs: Dict[str, Any] | None = None,
    world_seed: int | str | None = None,
) -> Dict[str, Any]:
    """
    Calculate mission reward for any reward type (Phase 7.11.3).
    
    Unified authority for credits, goods, modules, and hull vouchers.
    
    Args:
        mission: MissionEntity with reward_profile_id set
        reward_profiles: Dict mapping reward_profile_id to profile data
        catalogs: Optional dict with keys: "goods", "modules", "hulls", "data_catalog"
        world_seed: Optional world seed for deterministic selection
    
    Returns:
        Dict with structure:
        - {"type": "credits", "amount": int}
        - {"type": "goods", "sku_id": str, "quantity": int}
        - {"type": "module", "module_id": str}
        - {"type": "hull_voucher", "hull_id": str}
    
    Raises:
        ValueError: If reward_profile_id not found or required fields missing
    """
    profile_id = mission.reward_profile_id
    if not profile_id:
        raise ValueError(f"Mission {mission.mission_id} has no reward_profile_id")
    
    # Load profile
    profile = reward_profiles.get(profile_id)
    if profile is None:
        raise ValueError(
            f"Reward profile '{profile_id}' not found for mission {mission.mission_id}"
        )
    
    # Get reward_type
    reward_type = profile.get("reward_type")
    if not reward_type:
        raise ValueError(
            f"Reward profile '{profile_id}' missing required field 'reward_type'"
        )
    
    # Branch on reward_type
    if reward_type == "credits":
        # Reuse existing credit calculation
        amount = _calculate_mission_credit_reward(mission, reward_profiles)
        return {"type": "credits", "amount": amount}
    
    elif reward_type == "goods":
        return _calculate_mission_goods_reward(mission, profile, catalogs, world_seed)
    
    elif reward_type == "module":
        return _calculate_mission_module_reward(mission, profile, catalogs, world_seed)
    
    elif reward_type == "hull_voucher":
        return _calculate_mission_hull_voucher_reward(mission, profile, catalogs, world_seed)
    
    else:
        raise ValueError(
            f"Reward profile '{profile_id}' has unsupported reward_type '{reward_type}'"
        )


def _calculate_mission_goods_reward(
    mission: MissionEntity,
    profile: Dict[str, Any],
    catalogs: Dict[str, Any] | None,
    world_seed: int | str | None,
) -> Dict[str, Any]:
    """Calculate goods reward for mission (Phase 7.11.3)."""
    # Load catalogs if not provided
    if catalogs is None:
        catalogs = {}
    
    if "data_catalog" not in catalogs:
        try:
            from data_catalog import load_data_catalog
            catalogs["data_catalog"] = load_data_catalog()
        except Exception:
            raise ValueError("Failed to load data catalog for goods selection")
    
    data_catalog = catalogs["data_catalog"]
    
    # Get selector
    selector = profile.get("selector", {})
    
    # Check if sku_id is specified
    sku_id = selector.get("sku_id")
    if sku_id:
        # Use exact SKU
        selected_sku = sku_id
    else:
        # Filter by tags
        include_tags = set(selector.get("include_tags", []))
        exclude_tags = set(selector.get("exclude_tags", []))
        
        # Get all goods from catalog
        candidates = []
        for good in data_catalog.goods:
            good_tags = set(good.tags)
            if isinstance(good.possible_tag, str):
                good_tags.add(good.possible_tag)
            
            # Check include_tags
            if include_tags and not include_tags.issubset(good_tags):
                continue
            
            # Check exclude_tags
            if exclude_tags and exclude_tags.intersection(good_tags):
                continue
            
            candidates.append(good.sku)
        
        if not candidates:
            raise ValueError(
                f"No goods match selector criteria for mission {mission.mission_id}"
            )
        
        # Deterministic selection
        if world_seed is None:
            world_seed = 0
        seed_str = f"{world_seed}:{mission.mission_id}:mission_goods_select"
        rng = random.Random(seed_str)
        candidates_sorted = sorted(candidates)
        selected_sku = rng.choice(candidates_sorted)
    
    # Calculate quantity
    base_quantity = int(profile.get("base_quantity", 1))
    
    # Get tier multiplier
    tier_multiplier_data = profile.get("tier_multiplier", {})
    if isinstance(tier_multiplier_data, dict):
        tier_key = str(mission.mission_tier)
        tier_multiplier = float(tier_multiplier_data.get(tier_key, 1.0))
    elif isinstance(tier_multiplier_data, list):
        tier_index = mission.mission_tier - 1
        if tier_index < 0 or tier_index >= len(tier_multiplier_data):
            tier_multiplier = 1.0
        else:
            tier_multiplier = float(tier_multiplier_data[tier_index])
    else:
        tier_multiplier = 1.0
    
    # Distance multiplier (optional)
    distance_multiplier_per_ly = profile.get("distance_multiplier_per_ly")
    if distance_multiplier_per_ly is not None:
        distance_factor = 1 + mission.distance_ly * float(distance_multiplier_per_ly)
    else:
        distance_factor = 1.0
    
    quantity = base_quantity * tier_multiplier * distance_factor
    quantity = int(math.floor(quantity))
    
    return {"type": "goods", "sku_id": selected_sku, "quantity": quantity}


def _calculate_mission_module_reward(
    mission: MissionEntity,
    profile: Dict[str, Any],
    catalogs: Dict[str, Any] | None,
    world_seed: int | str | None,
) -> Dict[str, Any]:
    """Calculate module reward for mission (Phase 7.11.3)."""
    # Load catalogs if not provided
    if catalogs is None:
        catalogs = {}
    
    if "modules" not in catalogs:
        try:
            from data_loader import load_modules
            modules_data = load_modules()
            catalogs["modules"] = modules_data.get("modules", [])
        except Exception:
            raise ValueError("Failed to load modules catalog")
    
    modules_list = catalogs["modules"]
    
    # Get selector
    selector = profile.get("selector", {})
    
    # Check if module_id is specified
    module_id = selector.get("module_id")
    if module_id:
        # Use exact module
        selected_module_id = module_id
    else:
        # Filter by constraints
        slot_type = selector.get("slot_type")
        include_tags = set(selector.get("include_tags", []))
        exclude_tags = set(selector.get("exclude_tags", []))
        tier = selector.get("tier")
        if tier is None:
            tier = mission.mission_tier
        
        candidates = []
        for module in modules_list:
            # Check slot_type
            if slot_type and module.get("slot_type") != slot_type:
                continue
            
            # Check tier (optional - modules may not have tier field)
            # If tier is specified in selector, filter by it
            # If module has no tier field, include it (tier filtering is optional)
            module_tier = module.get("tier")
            if module_tier is not None and tier is not None and module_tier != tier:
                continue
            
            # Check tags
            module_tags = set(module.get("tags", []))
            primary_tag = module.get("primary_tag")
            if primary_tag:
                module_tags.add(primary_tag)
            
            if include_tags and not include_tags.issubset(module_tags):
                continue
            
            if exclude_tags and exclude_tags.intersection(module_tags):
                continue
            
            candidates.append(module.get("module_id"))
        
        if not candidates:
            raise ValueError(
                f"No modules match selector criteria for mission {mission.mission_id}"
            )
        
        # Deterministic selection
        if world_seed is None:
            world_seed = 0
        seed_str = f"{world_seed}:{mission.mission_id}:mission_module_select"
        rng = random.Random(seed_str)
        candidates_sorted = sorted(candidates)
        selected_module_id = rng.choice(candidates_sorted)
    
    return {"type": "module", "module_id": selected_module_id}


def _calculate_mission_hull_voucher_reward(
    mission: MissionEntity,
    profile: Dict[str, Any],
    catalogs: Dict[str, Any] | None,
    world_seed: int | str | None,
) -> Dict[str, Any]:
    """Calculate hull voucher reward for mission (Phase 7.11.3)."""
    # Load catalogs if not provided
    if catalogs is None:
        catalogs = {}
    
    if "hulls" not in catalogs:
        try:
            from data_loader import load_hulls
            hulls_data = load_hulls()
            catalogs["hulls"] = hulls_data.get("hulls", [])
        except Exception:
            raise ValueError("Failed to load hulls catalog")
    
    hulls_list = catalogs["hulls"]
    
    # Get selector
    selector = profile.get("selector", {})
    
    # Check if hull_id is specified
    hull_id = selector.get("hull_id")
    if hull_id:
        # Use exact hull
        selected_hull_id = hull_id
    else:
        # Filter by constraints
        frame = selector.get("frame")
        include_tags = set(selector.get("include_tags", []))
        exclude_tags = set(selector.get("exclude_tags", []))
        tier = selector.get("tier")
        if tier is None:
            tier = mission.mission_tier
        
        candidates = []
        for hull in hulls_list:
            # Check frame
            if frame and hull.get("frame") != frame:
                continue
            
            # Check tier
            hull_tier = hull.get("tier")
            if hull_tier is not None and hull_tier != tier:
                continue
            
            # Check tags
            hull_tags = set(hull.get("traits", []))
            
            if include_tags and not include_tags.issubset(hull_tags):
                continue
            
            if exclude_tags and exclude_tags.intersection(hull_tags):
                continue
            
            candidates.append(hull.get("hull_id"))
        
        if not candidates:
            raise ValueError(
                f"No hulls match selector criteria for mission {mission.mission_id}"
            )
        
        # Deterministic selection
        if world_seed is None:
            world_seed = 0
        seed_str = f"{world_seed}:{mission.mission_id}:mission_hull_select"
        rng = random.Random(seed_str)
        candidates_sorted = sorted(candidates)
        selected_hull_id = rng.choice(candidates_sorted)
    
    return {"type": "hull_voucher", "hull_id": selected_hull_id}


def _check_cargo_capacity(
    player_state: PlayerState,
    sku_id: str,
    quantity: int,
    data_catalog: Any | None = None,
) -> bool:
    """
    Check if player has sufficient cargo capacity for goods (Phase 7.11.3).
    
    Returns True if capacity is sufficient, False otherwise.
    """
    # Determine if data cargo
    is_data = _is_data_cargo(sku_id, data_catalog)
    
    # Get current cargo usage
    cargo = player_state.cargo_by_ship.get("active", {})
    
    if is_data:
        # Check data cargo capacity
        # Get ship data cargo capacity (would need ship state, simplified for now)
        # For now, assume unlimited if we can't determine
        # TODO: Get actual ship data cargo capacity
        current_data = sum(
            int(qty) for sku, qty in cargo.items()
            if _is_data_cargo(sku, data_catalog)
        )
        # Simplified: assume 100 data cargo capacity if we can't determine
        # This should be replaced with actual ship capacity lookup
        return current_data + quantity <= 100
    else:
        # Check physical cargo capacity
        current_physical = sum(
            int(qty) for sku, qty in cargo.items()
            if not _is_data_cargo(sku, data_catalog)
        )
        # Simplified: assume 100 physical cargo capacity if we can't determine
        # This should be replaced with actual ship capacity lookup
        return current_physical + quantity <= 100


def _check_data_cargo_capacity(
    player_state: PlayerState,
    quantity: int,
) -> bool:
    """
    Check if player has sufficient data cargo capacity (Phase 7.11.3).
    
    Returns True if capacity is sufficient, False otherwise.
    """
    cargo = player_state.cargo_by_ship.get("active", {})
    
    # Count current data cargo
    try:
        from data_catalog import load_data_catalog
        catalog = load_data_catalog()
    except Exception:
        catalog = None
    
    current_data = sum(
        int(qty) for sku, qty in cargo.items()
        if _is_data_cargo(sku, catalog)
    )
    
    # Simplified: assume 100 data cargo capacity if we can't determine
    # This should be replaced with actual ship capacity lookup
    return current_data + quantity <= 100


def _evaluate_delivery_mission(
    *,
    mission: MissionEntity,
    mission_manager: "MissionManager",
    player_state: PlayerState,
    current_system_id: str,
    current_destination_id: str | None,
    logger=None,
    turn: int = 0,
) -> bool:
    """
    Evaluate a single delivery mission for completion.
    
    Completion condition:
    - mission.target.target_type == "destination"
    - current_destination_id == mission.target.target_id
    
    Returns:
        True if mission was completed, False otherwise
    """
    # Read target from structured schema
    target = mission.target
    if not isinstance(target, dict):
        return False
    
    target_type = target.get("target_type")
    target_id = target.get("target_id")
    
    # Validate target structure
    if target_type != "destination":
        return False
    
    if not isinstance(target_id, str) or not target_id:
        return False
    
    # Check completion condition
    if current_destination_id == target_id:
        # Mission completed - transition to resolved
        old_state = str(mission.mission_state)
        
        mission.mission_state = MissionState.RESOLVED
        mission.outcome = MissionOutcome.COMPLETED
        
        # Set resolved_turn in persistent_state (minimal metadata without breaking schema)
        mission.persistent_state["resolved_turn"] = turn
        
        # Remove from active missions
        _remove_from_list(player_state.active_missions, mission.mission_id)
        
        # Add to completed missions
        if mission.mission_id not in player_state.completed_missions:
            player_state.completed_missions.append(mission.mission_id)
        
        # Log state transition
        if logger is not None:
            logger.log(
                turn=turn,
                action="mission_state_transition",
                state_change=(
                    f"mission_id={mission.mission_id} from={old_state} to=resolved "
                    f"outcome=completed target_id={target_id} current_destination_id={current_destination_id}"
                ),
            )
            
            logger.log(
                turn=turn,
                action="mission_eval:completed",
                state_change=(
                    f"mission_id={mission.mission_id} mission_type=delivery "
                    f"target_id={target_id} current_destination_id={current_destination_id}"
                ),
            )
        
        return True
    
    return False
