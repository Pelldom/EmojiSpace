from __future__ import annotations

from typing import Any

from player_state import PlayerState


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

