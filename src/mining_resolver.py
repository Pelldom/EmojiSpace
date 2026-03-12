"""Mining resolution (Phase 7.12). Deterministic, consumes 1 day and 1 fuel. Uses harvestable flag and category weighting."""
from __future__ import annotations

import hashlib
from dataclasses import dataclass
from pathlib import Path
from typing import Any


# Category weights for mining: ORE most common, METAL least common. Only these categories are mined.
MINING_CATEGORY_WEIGHTS = {
    "ORE": 10,
    "CHEMICALS": 6,
    "ENERGY": 3,
    "METAL": 1,
}

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
    category: str | None = None  # Good category when sku is set (for logging)


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


def _harvestable_weighted_sku_pool(catalog: Any) -> list[tuple[str, str]]:
    """
    Build weighted pool of (sku, category) for harvestable goods with known category weights.
    Each good is appended weight times so selection is deterministic and category-biased.
    """
    weighted_pool: list[tuple[str, str]] = []
    goods = getattr(catalog, "goods", [])
    for good in goods:
        if not getattr(good, "harvestable", False):
            continue
        category = getattr(good, "category", None)
        if category is None:
            continue
        weight = MINING_CATEGORY_WEIGHTS.get(category)
        if weight is None:
            continue
        sku = getattr(good, "sku", None)
        if not sku:
            continue
        for _ in range(weight):
            weighted_pool.append((sku, category))
    # Deterministic order: sort by (sku, category) so same catalog => same pool order
    weighted_pool.sort(key=lambda p: (p[0], p[1]))
    return weighted_pool


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
    increment_on_failure: bool = True,
) -> tuple[MiningResult, dict[str, int]]:
    """
    Consumes 1 day, 1 fuel (caller must apply).
    Increments mining_attempts[destination_id] when: yield produced, or no_yield (diminishing floor),
    or on other failure if increment_on_failure is True.
    Diminishing returns by attempt index. Builds SKU pool from goods where harvestable==true.
    If insufficient cargo space, returns success=False and no partial fill.
    Returns (MiningResult, new_mining_attempts); caller must assign attempts and apply cargo.
    """
    attempts = dict(mining_attempts)
    attempt_count = int(attempts.get(destination_id, 0))
    attempt_index_before = attempt_count
    # Tentative increment; reverted for certain failures when increment_on_failure is False
    attempts[destination_id] = attempt_count + 1

    multiplier = _yield_multiplier(attempt_count)
    base_quantity = max(0, int(player_ship_TR_band))
    effective_quantity = int(base_quantity * multiplier)

    if effective_quantity <= 0:
        # no_yield: always count as completed attempt (diminishing returns floor)
        return (
            MiningResult(
                sku=None,
                quantity=0,
                attempt_number=attempt_count + 1,
                multiplier=multiplier,
                success=False,
                message="no_yield",
                category=None,
            ),
            attempts,
        )

    weighted_pool = _harvestable_weighted_sku_pool(catalog)
    if not weighted_pool:
        if not increment_on_failure:
            attempts[destination_id] = attempt_index_before
        raise RuntimeError("Mining resolver: no harvestable SKUs found")

    seed_string = f"{world_seed}{destination_id}{player_id}mining_sku"
    index = _deterministic_int_mod(seed_string, len(weighted_pool))
    sku, category = weighted_pool[index]

    current_used = sum(int(v) for v in (current_cargo or {}).values())
    if current_used + effective_quantity > physical_cargo_capacity:
        if not increment_on_failure:
            attempts[destination_id] = attempt_index_before
        return (
            MiningResult(
                sku=sku,
                quantity=effective_quantity,
                attempt_number=attempt_count + 1,
                multiplier=multiplier,
                success=False,
                message="insufficient_cargo_capacity",
                category=category,
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
            category=category,
        ),
        attempts,
    )
