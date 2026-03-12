"""
Objective evaluators for mission completion.

Each evaluator handles a specific objective_type and checks if the objective
is complete based on the current game state and event context.
"""

from typing import Any, Dict, List, Optional
from mission_domain import Objective
from player_state import PlayerState


class MissionEventContext:
    """Context passed to objective evaluators."""
    
    def __init__(
        self,
        *,
        event_type: str,
        current_system_id: str,
        current_destination_id: Optional[str] = None,
        current_location_id: Optional[str] = None,
        cargo_snapshot: Optional[Dict[str, int]] = None,
        combat_result: Optional[Dict[str, Any]] = None,
    ):
        self.event_type = event_type
        self.current_system_id = current_system_id
        self.current_destination_id = current_destination_id
        self.current_location_id = current_location_id
        self.cargo_snapshot = cargo_snapshot or {}
        self.combat_result = combat_result or {}


def evaluate_objective(
    objective: Objective,
    context: MissionEventContext,
    player_state: PlayerState,
) -> bool:
    """
    Evaluate a single objective for completion.
    
    Returns True if the objective should be marked complete, False otherwise.
    This function may update objective.current_count and call recompute_complete().
    """
    obj_type = objective.objective_type
    
    if obj_type == "destination_visited":
        return _evaluate_destination_visited(objective, context)
    elif obj_type in ("cargo_delivered", "deliver_cargo"):
        return _evaluate_cargo_delivered(objective, context, player_state)
    elif obj_type == "cargo_acquired":
        return _evaluate_cargo_acquired(objective, context, player_state)
    elif obj_type == "npc_destroyed":
        return _evaluate_npc_destroyed(objective, context)
    elif obj_type == "combat_victory":
        return _evaluate_combat_victory(objective, context)
    else:
        # Unknown objective type - cannot evaluate
        return False


def _evaluate_destination_visited(
    objective: Objective,
    context: MissionEventContext,
) -> bool:
    """
    Evaluate destination_visited objective.
    
    Completes when:
    - event_type == "travel_arrival" or "arrival"
    - current_destination_id == objective.target_id
    """
    if context.event_type not in ("travel_arrival", "arrival"):
        return False
    
    if not context.current_destination_id:
        return False
    
    if context.current_destination_id == objective.target_id:
        objective.current_count = objective.required_count
        objective.recompute_complete()
        return True
    
    return False


def _evaluate_cargo_delivered(
    objective: Objective,
    context: MissionEventContext,
    player_state: PlayerState,
) -> bool:
    """
    Evaluate cargo_delivered objective.
    
    Completes when:
    - event_type == "travel_arrival" or "arrival"
    - current_destination_id matches target (if target_type is destination)
    - Required cargo is present in player inventory (delivery validation)
    
    Note: In a full implementation, we'd verify cargo was removed after delivery.
    For now, we check that player has cargo and is at destination.
    """
    if context.event_type not in ("travel_arrival", "arrival"):
        return False
    
    # Check destination match if target_type is destination
    if objective.target_type == "destination":
        if not context.current_destination_id or context.current_destination_id != objective.target_id:
            return False
    
    # Get cargo item ID from parameters or use target_id
    cargo_item_id = objective.parameters.get("cargo_item_id", "")
    if not cargo_item_id:
        # Fallback: if target_type is not destination, target_id might be the cargo item
        if objective.target_type != "destination":
            cargo_item_id = objective.target_id
    
    # If we still don't have a cargo item ID, check mission objectives for cargo info
    if not cargo_item_id:
        # This is a fallback - ideally cargo_item_id should be in parameters
        return False
    
    # Check cargo availability
    cargo = player_state.cargo_by_ship.get("active", {})
    item_quantity = cargo.get(cargo_item_id, 0)
    
    # For delivery, we need to have the cargo at the destination
    if item_quantity >= objective.required_count:
        objective.current_count = objective.required_count
        objective.recompute_complete()
        return True
    
    return False


def _evaluate_cargo_acquired(
    objective: Objective,
    context: MissionEventContext,
    player_state: PlayerState,
) -> bool:
    """
    Evaluate cargo_acquired objective.
    
    Completes when:
    - Player cargo contains target_id with quantity >= required_count
    """
    cargo = player_state.cargo_by_ship.get("active", {})
    item_quantity = cargo.get(objective.target_id, 0)
    
    if item_quantity >= objective.required_count:
        objective.current_count = objective.required_count
        objective.recompute_complete()
        return True
    
    # Update current_count to reflect progress
    objective.current_count = min(item_quantity, objective.required_count)
    objective.recompute_complete()
    return False


def _evaluate_npc_destroyed(
    objective: Objective,
    context: MissionEventContext,
) -> bool:
    """
    Evaluate npc_destroyed objective.
    
    Completes when:
    - event_type == "combat_complete" or "npc_destroyed"
    - combat_result or context indicates target NPC was destroyed
    """
    if context.event_type not in ("combat_complete", "npc_destroyed"):
        return False
    
    # Check combat result for destroyed NPC
    destroyed_npcs = context.combat_result.get("destroyed_npcs", [])
    if objective.target_id in destroyed_npcs:
        objective.current_count = objective.required_count
        objective.recompute_complete()
        return True
    
    return False


def _evaluate_combat_victory(
    objective: Objective,
    context: MissionEventContext,
) -> bool:
    """
    Evaluate combat_victory objective.
    
    Completes when:
    - event_type == "combat_complete"
    - combat_result indicates player victory
    """
    if context.event_type != "combat_complete":
        return False
    
    # Check if player won
    outcome = context.combat_result.get("outcome", "")
    if outcome in ("victory", "player_victory", "win"):
        objective.current_count = objective.required_count
        objective.recompute_complete()
        return True
    
    return False


def convert_mission_objectives_to_canonical(
    mission: Any,
) -> List[Objective]:
    """
    Convert mission.objectives (legacy dict format) to canonical Objective objects.
    
    This bridges the gap between legacy objective storage and the new Objective model.
    """
    objectives: List[Objective] = []
    
    if not hasattr(mission, "objectives") or not mission.objectives:
        # If no objectives, try to infer from mission structure
        # This handles delivery missions that use mission.target instead of objectives
        if hasattr(mission, "target") and isinstance(mission.target, dict):
            target = mission.target
            target_type = target.get("target_type", "")
            target_id = target.get("target_id", "")
            
            if target_type == "destination" and target_id:
                # Create appropriate objective based on mission type
                if mission.mission_type == "delivery":
                    # Delivery missions need cargo_delivered
                    # Extract cargo info from mission objectives if available
                    cargo_good_id = ""
                    cargo_quantity = 1
                    
                    # Check if mission has objectives with cargo info
                    if hasattr(mission, "objectives") and mission.objectives:
                        for obj_data in mission.objectives:
                            if isinstance(obj_data, dict):
                                params = obj_data.get("parameters", {})
                                goods = params.get("goods", [])
                                if goods and isinstance(goods, list) and len(goods) > 0:
                                    first_good = goods[0] if isinstance(goods[0], dict) else {}
                                    cargo_good_id = first_good.get("good_id", "")
                                    cargo_quantity = int(first_good.get("quantity", 1))
                                    break
                    
                    obj = Objective(
                        objective_id="OBJ-1",
                        objective_type="cargo_delivered",
                        target_type="destination",
                        target_id=target_id,
                        required_count=cargo_quantity,
                        parameters={"cargo_item_id": cargo_good_id} if cargo_good_id else {},
                    )
                    objectives.append(obj)
                elif mission.mission_type == "exploration":
                    obj = Objective(
                        objective_id="OBJ-1",
                        objective_type="destination_visited",
                        target_type="destination",
                        target_id=target_id,
                        required_count=1,
                    )
                    objectives.append(obj)
        
        return objectives
    
        # Convert each legacy objective dict to Objective
    for idx, obj_data in enumerate(mission.objectives):
        if isinstance(obj_data, dict):
            obj = Objective.from_legacy_dict(obj_data)
            if not obj.objective_id:
                obj.objective_id = f"OBJ-{idx + 1}"
            
            # For cargo_delivered/deliver_cargo objectives, ensure cargo_item_id is in parameters
            if obj.objective_type in ("cargo_delivered", "deliver_cargo"):
                if "cargo_item_id" not in obj.parameters:
                    # Extract from goods list in parameters
                    goods = obj.parameters.get("goods", [])
                    if goods and isinstance(goods, list) and len(goods) > 0:
                        first_good = goods[0] if isinstance(goods[0], dict) else {}
                        cargo_item_id = first_good.get("good_id", "")
                        if cargo_item_id:
                            obj.parameters["cargo_item_id"] = cargo_item_id
                            # Also set target_id if not set
                            if not obj.target_id and obj.target_type != "destination":
                                obj.target_id = cargo_item_id
            
            objectives.append(obj)
        elif isinstance(obj_data, str):
            # Legacy string format - skip (handled by from_legacy_dict)
            continue
    
    return objectives
