from dataclasses import dataclass, field
from typing import Any, Dict, List

try:
    from crew_modifiers import compute_crew_modifiers
except ModuleNotFoundError:
    from src.crew_modifiers import compute_crew_modifiers

from mission_entity import MissionEntity, MissionOutcome, MissionState
from player_state import PlayerState
from reward_applicator import apply_mission_rewards
import math
import json
from pathlib import Path


@dataclass
class MissionManager:
    missions: Dict[str, MissionEntity] = field(default_factory=dict)
    offered: List[str] = field(default_factory=list)
    # DataNet-specific mission offers (per-location, per-turn; ephemeral)
    datanet_offers: Dict[str, List[str]] = field(default_factory=dict)
    
    def calculate_reward_preview(self, mission: MissionEntity) -> Dict[str, Any]:
        """
        Calculate reward preview for a mission (Phase 7.11.2b).
        
        This function does NOT modify mission state, grant rewards, or log events.
        It is purely for presentation layer preview.
        
        Args:
            mission: MissionEntity to calculate preview for
        
        Returns:
            Dict with {"credits": <int>} or empty dict if calculation fails
        """
        if mission.reward_status == "granted":
            # If already granted, don't recalculate - return empty (caller should use stored value)
            return {}
        
        try:
            reward_profiles = _load_reward_profiles()
            credit_reward = _calculate_mission_credit_reward(mission, reward_profiles)
            return {"credits": credit_reward}
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
    
    # Auto payout for completed missions (Phase 7.11.2a)
    # Check all missions (not just active) for auto payout
    # Load reward profiles if not provided
    if reward_profiles is None:
        reward_profiles = _load_reward_profiles()
    
    for mission_id in list(mission_manager.missions.keys()):
        mission = mission_manager.missions.get(mission_id)
        if mission is None:
            continue
        
        # Check if mission is resolved and completed
        if mission.mission_state == MissionState.RESOLVED and mission.outcome == MissionOutcome.COMPLETED:
            # Guard against double payout: only pay when reward_status is 'ungranted'
            if mission.payout_policy == "auto" and mission.reward_status == "ungranted":
                # Calculate and grant reward
                try:
                    credit_reward = _calculate_mission_credit_reward(mission, reward_profiles)
                    player_state.credits += credit_reward
                    mission.reward_status = "granted"
                    mission.reward_granted_turn = turn
                    
                    # Log reward granted
                    if logger is not None:
                        logger.log(
                            turn=turn,
                            action="mission_reward_granted",
                            state_change=(
                                f"mission_id={mission_id} payout_policy=auto "
                                f"credits={credit_reward} new_balance={player_state.credits}"
                            ),
                        )
                        result["logs"].append(f"mission_id={mission_id} reward_granted credits={credit_reward}")
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
