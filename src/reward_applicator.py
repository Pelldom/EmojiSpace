from __future__ import annotations

from typing import Any

from player_state import PlayerState


def _is_data_cargo(sku_id: str, catalog: Any | None = None) -> bool:
    """
    Determine if a SKU is data cargo (has "data" tag) or physical cargo.
    
    Per ship_entity_contract.md Section 5: Goods with "data" tag are DIGITAL cargo.
    """
    if catalog is None:
        # Fallback: try to load catalog if not provided
        try:
            from data_catalog import load_data_catalog
            catalog = load_data_catalog()
        except Exception:
            # If catalog unavailable, assume physical (safer default)
            return False
    
    try:
        good = catalog.good_by_sku(sku_id)
        tags = set(good.tags)
        if isinstance(good.possible_tag, str):
            tags.add(good.possible_tag)
        return "data" in tags
    except (KeyError, AttributeError):
        # Unknown SKU or catalog issue: assume physical
        return False


def apply_materialized_reward(
    *,
    player: PlayerState,
    reward_payload,
    context: str | None = None,
    catalog: Any | None = None,
    physical_cargo_capacity: int | None = None,
    data_cargo_capacity: int | None = None,
    enforce_capacity: bool = False,
    stolen_applied: bool = False,
) -> dict[str, Any]:
    """
    Apply materialized reward to player state.
    
    Args:
        player: PlayerState to mutate
        reward_payload: RewardResult from materialize_reward
        context: Optional context string for logging
        catalog: Optional DataCatalog for cargo type determination
        physical_cargo_capacity: Optional physical cargo capacity limit
        data_cargo_capacity: Optional data cargo capacity limit
        enforce_capacity: If True, check capacity and return error if overflow
        stolen_applied: If True, mark cargo as stolen (for law enforcement)
    
    Returns:
        dict with:
        - "credits": int (credits applied)
        - "cargo": str | None (sku_id if cargo applied)
        - "quantity": int (quantity applied)
        - "context": str | None
        - "error": str | None ("cargo_capacity_exceeded" if overflow and enforce_capacity=True)
        - "stolen": bool (whether cargo was marked stolen)
    """
    applied = {
        "credits": 0,
        "cargo": None,
        "quantity": 0,
        "context": context,
        "error": None,
        "stolen": False,
    }
    if reward_payload is None:
        return applied
    
    # Apply credits (always allowed, no capacity limit)
    if isinstance(getattr(reward_payload, "credits", None), int):
        player.credits = max(0, int(player.credits) + int(reward_payload.credits))
        applied["credits"] = int(reward_payload.credits)
    
    # Apply cargo (with capacity checking if enabled)
    sku_id = getattr(reward_payload, "sku_id", None)
    quantity = getattr(reward_payload, "quantity", None)
    if isinstance(sku_id, str) and isinstance(quantity, int) and quantity > 0:
        # Determine cargo type
        is_data = _is_data_cargo(sku_id, catalog)
        
        # Check capacity if enforcement enabled
        if enforce_capacity:
            if is_data:
                capacity = data_cargo_capacity
                current_usage_key = "_data_cargo_usage"
            else:
                capacity = physical_cargo_capacity
                current_usage_key = "_physical_cargo_usage"
            
            if capacity is not None and capacity > 0:
                # Calculate current cargo usage
                current_usage = 0
                holdings = player.cargo_by_ship.get("active", {})
                for existing_sku, existing_qty in holdings.items():
                    if _is_data_cargo(existing_sku, catalog) == is_data:
                        current_usage += int(existing_qty)
                
                # Check if adding would overflow
                if current_usage + int(quantity) > int(capacity):
                    applied["error"] = "cargo_capacity_exceeded"
                    applied["cargo"] = sku_id
                    applied["quantity"] = quantity
                    applied["stolen"] = stolen_applied
                    return applied
        
        # Apply cargo (capacity check passed or not enforced)
        player.cargo_by_ship.setdefault("active", {})
        current_qty = player.cargo_by_ship["active"].get(sku_id, 0)
        player.cargo_by_ship["active"][sku_id] = current_qty + quantity
        
        # Store stolen flag in cargo metadata (minimal persistence for law enforcement)
        # Store as a special marker in cargo_by_ship structure
        if stolen_applied:
            # Use a metadata structure: store stolen flag alongside quantity
            # For now, use a simple approach: store in a separate dict key
            if not hasattr(player, "_cargo_metadata"):
                player._cargo_metadata = {}
            if "active" not in player._cargo_metadata:
                player._cargo_metadata["active"] = {}
            if sku_id not in player._cargo_metadata["active"]:
                player._cargo_metadata["active"][sku_id] = {}
            player._cargo_metadata["active"][sku_id]["stolen"] = True
        
        applied["cargo"] = sku_id
        applied["quantity"] = quantity
        applied["stolen"] = stolen_applied
    
    return applied


def apply_mission_rewards(
    *,
    mission_id: str,
    rewards: list[dict[str, Any]],
    player: PlayerState,
    logger=None,
    turn: int = 0,
) -> None:
    for reward in rewards:
        field_name = reward.get("field")
        delta = reward.get("delta")
        if not field_name or not isinstance(delta, int):
            continue
        if not hasattr(player, field_name):
            continue
        current = getattr(player, field_name)
        if isinstance(current, int):
            setattr(player, field_name, current + delta)
            _log_reward(logger, turn, mission_id, f"{field_name}={current + delta}")


def _log_reward(logger, turn: int, mission_id: str, detail: str) -> None:
    if logger is None:
        return
    logger.log(
        turn=turn,
        action="reward_applied",
        state_change=f"mission_id={mission_id} {detail}",
    )

