from __future__ import annotations

from typing import Any

from player_state import PlayerState


def apply_materialized_reward(*, player: PlayerState, reward_payload, context: str | None = None) -> dict[str, Any]:
    applied = {"credits": 0, "cargo": None, "quantity": 0, "context": context}
    if reward_payload is None:
        return applied
    if isinstance(getattr(reward_payload, "credits", None), int):
        player.credits += int(reward_payload.credits)
        applied["credits"] = int(reward_payload.credits)
    sku_id = getattr(reward_payload, "sku_id", None)
    quantity = getattr(reward_payload, "quantity", None)
    if isinstance(sku_id, str) and isinstance(quantity, int) and quantity > 0:
        player.cargo_by_ship.setdefault("active", {})
        player.cargo_by_ship["active"][sku_id] = player.cargo_by_ship["active"].get(sku_id, 0) + quantity
        applied["cargo"] = sku_id
        applied["quantity"] = quantity
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

