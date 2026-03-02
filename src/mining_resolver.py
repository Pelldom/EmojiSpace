"""Mining resolution (Phase 7.12). Deterministic, consumes 1 day and 1 fuel. Uses harvestable flag only."""
from __future__ import annotations

import hashlib
from dataclasses import dataclass
from pathlib import Path
from typing import Any


# Extended depletion model: 0->1.0, 1->0.8, 2->0.6, 3->0.4, 4->0.2, 5->0.1, 6+->0.05
YIELD_MULTIPLIER_TABLE = {
    0: 1.0,
    1: 0.8,
    2: 0.6,
    3: 0.4,
    4: 0.2,
    5: 0.1,
}
MULTIPLIER_FLOOR = 0.05  # attempt_index >= 6


@dataclass(frozen=True)
class MiningResult:
    sku: str | None  # None if no yield (multiplier 0 or capacity fail)
    quantity: int
    attempt_number: int
    multiplier: float
    success: bool  # True if yielded and stored
    message: str  # Error message if success False


def _deterministic_int_mod(seed_string: str, modulus: int) -> int:
    if modulus <= 0:
        return 0
    digest = hashlib.sha256(seed_string.encode("ascii")).digest()
    value = int.from_bytes(digest[:8], byteorder="big", signed=False)
    return value % modulus


def _yield_multiplier(attempt_index: int) -> float:
    """Attempt index is mining_attempts[destination_id] before increment. 6+ -> 0.05."""
    if attempt_index in YIELD_MULTIPLIER_TABLE:
        return YIELD_MULTIPLIER_TABLE[attempt_index]
    return MULTIPLIER_FLOOR  # 6 and above


def _harvestable_sku_pool(catalog: Any) -> list[str]:
    """Build sorted list of SKUs where harvestable==true. Mining relies ONLY on harvestable flag."""
    pool: list[str] = []
    goods = getattr(catalog, "goods", [])
    for good in goods:
        if getattr(good, "harvestable", False):
            pool.append(good.sku)
    pool.sort(key=lambda s: (s,))  # ASCII sort
    return pool


def resolve_mining(
    *,
    world_seed: int | str,
    destination_id: str,
    player_id: str,
    mining_attempts: dict[str, int],
    player_ship_TR_band: int,
    catalog: Any,
    current_cargo: dict[str, int],
    physical_cargo_capacity: int,
) -> tuple[MiningResult, dict[str, int]]:
    """
    Consumes 1 day, 1 fuel (caller must apply).
    Increments mining_attempts[destination_id].
    Diminishing returns by attempt index. Builds SKU pool from goods where harvestable==true.
    If insufficient cargo space, returns success=False and no partial fill.
    Returns (MiningResult, new_mining_attempts); caller must assign attempts and apply cargo.
    """
    attempts = dict(mining_attempts)
    attempt_count = int(attempts.get(destination_id, 0))
    attempts[destination_id] = attempt_count + 1

    multiplier = _yield_multiplier(attempt_count)
    base_quantity = max(0, int(player_ship_TR_band))
    effective_quantity = int(base_quantity * multiplier)

    if effective_quantity <= 0:
        return (
            MiningResult(
                sku=None,
                quantity=0,
                attempt_number=attempt_count + 1,
                multiplier=multiplier,
                success=False,
                message="no_yield",
            ),
            attempts,
        )

    pool = _harvestable_sku_pool(catalog)
    if not pool:
        return (
            MiningResult(
                sku=None,
                quantity=0,
                attempt_number=attempt_count + 1,
                multiplier=multiplier,
                success=False,
                message="no_harvestable_goods",
            ),
            attempts,
        )

    seed_string = f"{world_seed}{destination_id}{player_id}mining_sku"
    index = _deterministic_int_mod(seed_string, len(pool))
    sku = pool[index]

    current_used = sum(int(v) for v in (current_cargo or {}).values())
    if current_used + effective_quantity > physical_cargo_capacity:
        return (
            MiningResult(
                sku=sku,
                quantity=effective_quantity,
                attempt_number=attempt_count + 1,
                multiplier=multiplier,
                success=False,
                message="insufficient_cargo_capacity",
            ),
            attempts,
        )

    return (
        MiningResult(
            sku=sku,
            quantity=effective_quantity,
            attempt_number=attempt_count + 1,
            multiplier=multiplier,
            success=True,
            message="ok",
        ),
        attempts,
    )
