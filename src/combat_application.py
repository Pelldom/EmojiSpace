from __future__ import annotations

from typing import Any


def apply_combat_result(
    *,
    player_state,
    player_ship_entity,
    enemy_ship_entity_or_dict,
    combat_result,
    system_id: str,
    encounter_id: str,
    world_seed,
    logger=None,
    turn: int = 0,
) -> dict:
    """
    Apply combat result to player and enemy ship state.
    
    This function:
    - Applies player ship final hull + degradation to player_ship_entity persistent_state
    - Applies enemy ship final hull + degradation if enemy is persisted (if not persisted, skip)
    - Applies salvage_modules to player inventory if present
    - Returns summary dict for logging
    
    Does NOT materialize or apply rewards (that remains where it already happens).
    """
    applied = {
        "player_hull_before": None,
        "player_hull_after": None,
        "player_degradation_before": None,
        "player_degradation_after": None,
        "enemy_hull_before": None,
        "enemy_hull_after": None,
        "salvage_count": 0,
        "salvage_applied": [],
    }
    
    # Apply player ship state
    final_player = getattr(combat_result, "final_state_player", None)
    if isinstance(final_player, dict) and player_ship_entity is not None:
        applied["player_hull_before"] = int(
            player_ship_entity.persistent_state.get("current_hull_integrity", 0) or 0
        )
        applied["player_degradation_before"] = dict(
            player_ship_entity.persistent_state.get("degradation_state", {"weapon": 0, "defense": 0, "engine": 0})
        )
        
        # Apply degradation state
        degradation = final_player.get("degradation", {})
        if isinstance(degradation, dict):
            player_ship_entity.persistent_state["degradation_state"] = dict(degradation)
            applied["player_degradation_after"] = dict(degradation)
        
        # Apply hull integrity
        current_hull = final_player.get("current_hull")
        if isinstance(current_hull, int):
            player_ship_entity.persistent_state["current_hull_integrity"] = int(current_hull)
            applied["player_hull_after"] = int(current_hull)
        
        if logger:
            logger.log(
                turn=turn,
                action="combat_applied",
                state_change=(
                    f"encounter_id={encounter_id} player_hull={applied['player_hull_before']}->{applied['player_hull_after']} "
                    f"degradation={applied['player_degradation_before']}->{applied['player_degradation_after']}"
                ),
            )
    
    # Apply enemy ship state (if enemy is a persisted entity)
    if hasattr(enemy_ship_entity_or_dict, "persistent_state"):
        final_enemy = getattr(combat_result, "final_state_enemy", None)
        if isinstance(final_enemy, dict):
            applied["enemy_hull_before"] = int(
                enemy_ship_entity_or_dict.persistent_state.get("current_hull_integrity", 0) or 0
            )
            
            degradation = final_enemy.get("degradation", {})
            if isinstance(degradation, dict):
                enemy_ship_entity_or_dict.persistent_state["degradation_state"] = dict(degradation)
            
            current_hull = final_enemy.get("current_hull")
            if isinstance(current_hull, int):
                enemy_ship_entity_or_dict.persistent_state["current_hull_integrity"] = int(current_hull)
                applied["enemy_hull_after"] = int(current_hull)
    
    # Apply salvage modules
    salvage_modules = getattr(combat_result, "salvage_modules", [])
    if salvage_modules and isinstance(salvage_modules, list):
        applied["salvage_count"] = len(salvage_modules)
        
        # Store salvage in player_state - add field if it doesn't exist
        # Use a simple list container for now (modules can be installed later via shipdock)
        if not hasattr(player_state, "salvage_modules"):
            player_state.salvage_modules = []
        
        if not isinstance(player_state.salvage_modules, list):
            player_state.salvage_modules = []
        
        # Add salvage modules to player inventory (deep copy to avoid reference issues)
        import copy
        for module in salvage_modules:
            if isinstance(module, dict):
                module_copy = copy.deepcopy(module)
                player_state.salvage_modules.append(module_copy)
                applied["salvage_applied"].append(module.get("module_id", "unknown"))
        
        if logger:
            logger.log(
                turn=turn,
                action="combat_salvage_applied",
                state_change=(
                    f"encounter_id={encounter_id} salvage_count={applied['salvage_count']} "
                    f"modules={applied['salvage_applied']}"
                ),
            )
    
    return applied
