"""Exploration resolution (Phase 7.12). Deterministic, consumes 1 day and 1 fuel."""
from __future__ import annotations

import hashlib
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class ExplorationResult:
    success: bool
    stage_before: int
    stage_after: int
    rng_roll: float


def _deterministic_float(seed_string: str) -> float:
    digest = hashlib.sha256(seed_string.encode("ascii")).digest()
    value = int.from_bytes(digest[:8], byteorder="big", signed=False)
    return value / (2**64)


def resolve_exploration(
    *,
    world_seed: int | str,
    destination_id: str,
    player_id: str,
    exploration_attempts: dict[str, int],
    exploration_progress: dict[str, int],
) -> tuple[ExplorationResult, dict[str, int], dict[str, int]]:
    """
    Consumes 1 day, 1 fuel (caller must apply).
    Increments exploration_attempts[destination_id].
    RNG: world_seed + destination_id + player_id + "explore".
    Base success chance 0.50. On success, increments exploration_progress[destination_id].
    Returns (ExplorationResult, new_attempts, new_progress); caller must assign back to player state.
    """
    attempts = dict(exploration_attempts)
    progress = dict(exploration_progress)
    attempt_count = int(attempts.get(destination_id, 0))
    stage_before = int(progress.get(destination_id, 0))
    attempts[destination_id] = attempt_count + 1

    seed_string = f"{world_seed}{destination_id}{player_id}explore"
    rng_roll = _deterministic_float(seed_string)
    success = rng_roll < 0.50

    if success:
        progress[destination_id] = stage_before + 1
    stage_after = int(progress.get(destination_id, 0))

    result = ExplorationResult(
        success=success,
        stage_before=stage_before,
        stage_after=stage_after,
        rng_roll=rng_roll,
    )
    return result, attempts, progress
