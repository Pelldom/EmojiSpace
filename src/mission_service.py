"""
Mission service - event-driven mission evaluation hooks.

This module provides event handlers that trigger mission evaluation
when game events occur (arrival, cargo changes, combat resolution).
"""

from typing import Any, Dict, Optional
from mission_manager import MissionManager, evaluate_active_missions
from mission_objective_evaluator import MissionEventContext
from player_state import PlayerState


def on_arrival(
    *,
    mission_manager: MissionManager,
    player_state: PlayerState,
    new_system_id: str,
    new_destination_id: Optional[str],
    new_location_id: Optional[str] = None,
    reward_profiles: Optional[Dict[str, Any]] = None,
    world_seed: Optional[int | str] = None,
    logger=None,
    turn: int = 0,
) -> Dict[str, Any]:
    """
    Handle travel arrival event - evaluate missions for destination-based objectives.
    
    Args:
        mission_manager: MissionManager instance
        player_state: Current player state
        new_system_id: System ID player arrived at
        new_destination_id: Destination ID player arrived at
        new_location_id: Optional location ID within destination
        reward_profiles: Optional reward profiles dict (loaded if None)
        world_seed: Optional world seed for deterministic reward calculation
        logger: Optional logger instance
        turn: Current turn number
    
    Returns:
        Result dict from evaluate_active_missions
    """
    event_context = {
        "event": "travel_arrival",
        "target_system_id": new_system_id,
        "target_destination_id": new_destination_id,
    }
    
    return evaluate_active_missions(
        mission_manager=mission_manager,
        player_state=player_state,
        current_system_id=new_system_id,
        current_destination_id=new_destination_id,
        event_context=event_context,
        reward_profiles=reward_profiles,
        world_seed=world_seed,
        logger=logger,
        turn=turn,
    )


def on_cargo_change(
    *,
    mission_manager: MissionManager,
    player_state: PlayerState,
    cargo_delta: Optional[Dict[str, int]] = None,
    reward_profiles: Optional[Dict[str, Any]] = None,
    world_seed: Optional[int | str] = None,
    logger=None,
    turn: int = 0,
) -> Dict[str, Any]:
    """
    Handle cargo change event - evaluate missions for cargo-based objectives.
    
    Args:
        mission_manager: MissionManager instance
        player_state: Current player state
        cargo_delta: Optional dict of {item_id: quantity_change} (not used yet, but available for future)
        reward_profiles: Optional reward profiles dict (loaded if None)
        world_seed: Optional world seed for deterministic reward calculation
        logger: Optional logger instance
        turn: Current turn number
    
    Returns:
        Result dict from evaluate_active_missions
    """
    event_context = {
        "event": "cargo_change",
        "cargo_delta": cargo_delta or {},
    }
    
    return evaluate_active_missions(
        mission_manager=mission_manager,
        player_state=player_state,
        current_system_id=player_state.current_system_id,
        current_destination_id=player_state.current_destination_id,
        event_context=event_context,
        reward_profiles=reward_profiles,
        world_seed=world_seed,
        logger=logger,
        turn=turn,
    )


def on_combat_resolved(
    *,
    mission_manager: MissionManager,
    player_state: PlayerState,
    combat_result: Dict[str, Any],
    reward_profiles: Optional[Dict[str, Any]] = None,
    world_seed: Optional[int | str] = None,
    logger=None,
    turn: int = 0,
) -> Dict[str, Any]:
    """
    Handle combat resolution event - evaluate missions for combat-based objectives.
    
    Args:
        mission_manager: MissionManager instance
        player_state: Current player state
        combat_result: Dict with combat outcome, destroyed ships, etc.
        reward_profiles: Optional reward profiles dict (loaded if None)
        world_seed: Optional world seed for deterministic reward calculation
        logger: Optional logger instance
        turn: Current turn number
    
    Returns:
        Result dict from evaluate_active_missions
    """
    event_context = {
        "event": "combat_complete",
        "combat_result": combat_result,
    }
    
    return evaluate_active_missions(
        mission_manager=mission_manager,
        player_state=player_state,
        current_system_id=player_state.current_system_id,
        current_destination_id=player_state.current_destination_id,
        event_context=event_context,
        reward_profiles=reward_profiles,
        world_seed=world_seed,
        logger=logger,
        turn=turn,
    )
