from __future__ import annotations

import hashlib
import json
import random
from pathlib import Path
from typing import Any


def generate_hireable_crew(
    *,
    world_seed: int,
    system_id: str,
    pool_size: int = 3,
    world_state_engine: Any | None = None,
) -> list[dict[str, Any]]:
    if not isinstance(world_seed, int):
        raise ValueError("world_seed must be int.")
    if not isinstance(system_id, str) or not system_id:
        raise ValueError("system_id must be non-empty string.")
    if not isinstance(pool_size, int) or pool_size < 0:
        raise ValueError("pool_size must be a non-negative integer.")

    roles = _load_crew_roles()
    if not roles or pool_size == 0:
        return []

    rng = random.Random(_seed_from_parts(world_seed, system_id, "crew_pool"))
    base_weights = _base_role_weights(roles)
    adjusted_weights = _adjust_role_weights_with_world_state(
        roles=roles,
        base_weights=base_weights,
        world_state_engine=world_state_engine,
        system_id=system_id,
    )

    role_by_id = {str(entry.get("role_id", "")): entry for entry in roles}
    selected_role_ids = _weighted_sample_role_ids_without_replacement(
        role_ids=[str(entry.get("role_id", "")) for entry in roles if str(entry.get("role_id", ""))],
        role_weights=adjusted_weights,
        count=pool_size,
        rng=rng,
    )

    pool: list[dict[str, Any]] = []
    for role_id in selected_role_ids:
        role = role_by_id[role_id]
        hire_min = int(role.get("hire_cost_min", 0))
        hire_max = int(role.get("hire_cost_max", hire_min))
        low = min(hire_min, hire_max)
        high = max(hire_min, hire_max)
        pool.append(
            {
                "role_id": role_id,
                "hire_cost": rng.randint(low, high),
                "daily_wage": int(role.get("base_daily_wage", 0)),
            }
        )
    return pool


def compute_crew_role_weights(
    *,
    world_state_engine: Any | None = None,
    system_id: str | None = None,
) -> dict[str, float]:
    roles = _load_crew_roles()
    base_weights = _base_role_weights(roles)
    return _adjust_role_weights_with_world_state(
        roles=roles,
        base_weights=base_weights,
        world_state_engine=world_state_engine,
        system_id=system_id,
    )


def _adjust_role_weights_with_world_state(
    *,
    roles: list[dict[str, Any]],
    base_weights: dict[str, float],
    world_state_engine: Any | None,
    system_id: str | None,
) -> dict[str, float]:
    if world_state_engine is None or not system_id:
        return dict(base_weights)

    entity_views = [
        {
            "entity_id": str(role.get("role_id", "")),
            "category_id": None,
            "tags": _role_tags(role),
        }
        for role in roles
        if str(role.get("role_id", ""))
    ]
    resolved = world_state_engine.resolve_modifiers_for_entities(
        system_id=system_id,
        domain="crew",
        entity_views=entity_views,
    )
    by_id = resolved.get("resolved", {})
    adjusted: dict[str, float] = {}
    for role_id, base_weight in base_weights.items():
        row = by_id.get(role_id, {})
        # crew_weight_percent is the Slice 11 input. hire_weight_delta remains
        # supported for compatibility with existing crew-domain modifier names.
        crew_weight_percent = int(row.get("crew_weight_percent", row.get("hire_weight_delta", 0)))
        adjusted_weight = base_weight * (1.0 + (float(crew_weight_percent) / 100.0))
        adjusted[role_id] = max(0.0, adjusted_weight)
    return adjusted


def _weighted_sample_role_ids_without_replacement(
    *,
    role_ids: list[str],
    role_weights: dict[str, float],
    count: int,
    rng: random.Random,
) -> list[str]:
    pool_ids = list(role_ids)
    picked: list[str] = []
    for _ in range(max(0, min(count, len(pool_ids)))):
        weights = [float(role_weights.get(role_id, 0.0)) for role_id in pool_ids]
        if sum(weights) <= 0:
            break
        index = _weighted_pick_index(weights, rng)
        picked.append(pool_ids.pop(index))
    return picked


def _weighted_pick_index(weights: list[float], rng: random.Random) -> int:
    total = sum(weights)
    if total <= 0:
        raise ValueError("Weights must sum to a positive value.")
    threshold = rng.random() * total
    running = 0.0
    for index, weight in enumerate(weights):
        running += float(weight)
        if threshold <= running:
            return index
    return len(weights) - 1


def _load_crew_roles() -> list[dict[str, Any]]:
    path = Path(__file__).resolve().parents[1] / "data" / "crew_roles.json"
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, list):
        raise ValueError("crew_roles.json must be a list.")
    return [entry for entry in payload if isinstance(entry, dict)]


def _load_crew_rarity_weights() -> dict[str, int]:
    path = Path(__file__).resolve().parents[1] / "data" / "crew_rarity.json"
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError("crew_rarity.json must be an object.")
    return {str(key): int(value) for key, value in payload.items()}


def _base_role_weights(roles: list[dict[str, Any]]) -> dict[str, float]:
    rarity_weights = _load_crew_rarity_weights()
    out: dict[str, float] = {}
    for role in roles:
        role_id = str(role.get("role_id", ""))
        if not role_id:
            continue
        rarity = str(role.get("rarity", "common"))
        out[role_id] = float(rarity_weights.get(rarity, rarity_weights.get("common", 1)))
    return out


def _role_tags(role: dict[str, Any]) -> list[str]:
    tags = role.get("tags", [])
    if not isinstance(tags, list):
        return []
    return [str(tag) for tag in tags if isinstance(tag, str)]


def _seed_from_parts(world_seed: int, system_id: str, stream: str) -> int:
    token = repr((world_seed, system_id, stream))
    digest = hashlib.sha256(token.encode("ascii")).hexdigest()
    return int(digest[:16], 16)
