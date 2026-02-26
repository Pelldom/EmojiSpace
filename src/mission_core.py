"""MissionCore API - Unified mission presentation layer.

This module provides a unified interface for mission operations that separates
mission state logic from presentation surfaces (NPCs, Locations, DataNet, Encounters).

Architecture:
- MissionCore = state machine interface
- NPCs and Locations = presentation adapters
- All mission operations route through MissionCore methods
"""

from typing import Any, Callable

from mission_entity import MissionState
from mission_manager import MissionManager


class MissionCore:
    """Unified API for mission operations across all presentation surfaces."""

    def __init__(self, mission_manager: MissionManager):
        self._mission_manager = mission_manager

    def list_offered(
        self,
        *,
        location_id: str,
        location_type: str | None = None,
        ensure_offers_callback: Callable[[str], list[str]] | None = None,
    ) -> list[dict[str, Any]]:
        """List offered missions for a location.
        
        Args:
            location_id: The location to list missions for.
            location_type: Optional location type (e.g., "bar", "administration").
            ensure_offers_callback: Optional callback to ensure offers exist.
                Should return list[str] of mission_ids.
        
        Returns:
            List of mission row dicts with mission_id, mission_type, mission_tier,
            mission_state, rewards, and optionally giver_npc_id/giver_display_name.
        """
        # Ensure offers exist if callback provided
        if ensure_offers_callback is not None:
            mission_ids = ensure_offers_callback(location_id=location_id)
        else:
            # Fallback: get from manager's offered list
            mission_ids = [
                mid for mid in self._mission_manager.offered
                if self._mission_manager.missions.get(mid) is not None
            ]
        
        rows: list[dict[str, Any]] = []
        for mission_id in mission_ids:
            mission = self._mission_manager.missions.get(mission_id)
            if mission is None:
                continue
            # Only include OFFERED missions
            if mission.mission_state != MissionState.OFFERED:
                continue
            
            # Calculate reward preview if ungranted (Phase 7.11.2b)
            reward_summary = []
            if mission.reward_status == "ungranted":
                preview = self._mission_manager.calculate_reward_preview(mission)
                if preview and "credits" in preview:
                    reward_summary = [{"field": "credits", "delta": preview["credits"]}]
            
            row = {
                "mission_id": mission.mission_id,
                "mission_type": mission.mission_type,
                "mission_tier": int(mission.mission_tier),
                "mission_state": str(mission.mission_state),
                "reward_summary": reward_summary,  # Phase 7.11.2b - Add reward preview
            }
            # Add giver information for Bar locations only
            if location_type == "bar" and mission.mission_contact_seed is not None:
                import hashlib
                npc_hash = hashlib.md5(mission.mission_contact_seed.encode()).hexdigest()[:8]
                giver_npc_id = f"NPC-MSN-{npc_hash}"
                row["giver_npc_id"] = giver_npc_id
                row["giver_display_name"] = f"Mission Contact ({mission.mission_type})"
            rows.append(row)
        return rows

    def get_details(self, mission_id: str) -> dict[str, Any]:
        """Get mission details for discussion/display.
        
        Args:
            mission_id: The mission ID to get details for.
        
        Returns:
            Dict with mission details:
            - For OFFERED: ok, mission_id, mission_type, mission_tier, rewards, offer_only=True
            - For ACTIVE: ok, mission_id, mission_type, mission_tier, status="active", text
            - For RESOLVED: ok, mission_id, text
        
        Raises:
            ValueError: If mission not found.
        """
        mission = self._mission_manager.missions.get(mission_id)
        if mission is None:
            raise ValueError("mission_not_found")
        
        # Compare against enum values directly
        if mission.mission_state == MissionState.OFFERED:
            # Calculate reward preview if ungranted (Phase 7.11.2b)
            reward_summary = []
            if mission.reward_status == "ungranted":
                preview = self._mission_manager.calculate_reward_preview(mission)
                if preview and "credits" in preview:
                    reward_summary = [{"field": "credits", "delta": preview["credits"]}]
            
            return {
                "ok": True,
                "mission_id": mission.mission_id,
                "mission_type": mission.mission_type,
                "mission_tier": int(mission.mission_tier),
                "offer_only": True,
                "reward_summary": reward_summary,  # Phase 7.11.2b - Add reward preview
            }
        # If mission is active, return status message
        elif mission.mission_state == MissionState.ACTIVE:
            return {
                "ok": True,
                "mission_id": mission.mission_id,
                "mission_type": mission.mission_type,
                "mission_tier": int(mission.mission_tier),
                "status": "active",
                "text": "You are already under contract. Complete the objective and return.",
            }
        # If mission is resolved (completed/failed), return placeholder
        elif mission.mission_state == MissionState.RESOLVED:
            return {
                "ok": True,
                "mission_id": mission.mission_id,
                "text": "This contract has already been resolved.",
            }
        # For any other state (e.g., "accepted"), treat as active
        else:
            return {
                "ok": True,
                "mission_id": mission.mission_id,
                "mission_type": mission.mission_type,
                "mission_tier": int(mission.mission_tier),
                "status": str(mission.mission_state),
                "text": "You are already under contract. Complete the objective and return.",
            }

    def accept(
        self,
        mission_id: str,
        *,
        player: Any,
        location_id: str,
        location_type: str | None = None,
        ship: Any | None = None,
        logger: Any | None = None,
        turn: int = 0,
        create_contact_npc_callback: Callable[[str, str], None] | None = None,
    ) -> tuple[bool, str | None]:
        """Accept a mission.
        
        Args:
            mission_id: The mission ID to accept.
            player: PlayerState instance.
            location_id: Current location ID.
            location_type: Optional location type (e.g., "bar", "administration").
            ship: Optional ship instance (not used in new validation).
            logger: Optional logger instance.
            turn: Current turn number.
            create_contact_npc_callback: Optional callback to create contact NPC.
                Called with (mission_id, location_id) if mission is accepted and location_type == "bar".
        
        Returns:
            Tuple of (accepted: bool, error_reason: str | None)
            error_reason will be "mission_accept_failed_total_cap" or 
            "mission_accept_failed_tier_cap" if rejected.
        """
        # Check if mission is offered at this location
        # We need to check against the location's offered list
        # This is handled by the caller ensuring the mission is in the offered list
        
        accepted, error_reason = self._mission_manager.accept(
            mission_id=mission_id,
            player=player,
            logger=logger,
            turn=turn,
            location_type=location_type,
            ship=ship,
        )
        
        if accepted and create_contact_npc_callback is not None and location_type == "bar":
            # Create mission contact NPC for Bar locations
            create_contact_npc_callback(mission_id=mission_id, location_id=location_id)
        
        return accepted, error_reason
