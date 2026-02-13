from __future__ import annotations

import hashlib
import random
from typing import Any

try:
    from data_loader import load_hulls, load_modules
except ModuleNotFoundError:
    from src.data_loader import load_hulls, load_modules


MODULE_STOCK_CHANCE = {1: 0.50, 2: 0.65, 3: 0.80, 4: 0.90, 5: 0.95}
HULL_STOCK_CHANCE = {1: 0.70, 2: 0.80, 3: 0.90, 4: 0.95, 5: 0.98}
MODULE_MAX_COUNT = {1: 2, 2: 3, 3: 5, 4: 6, 5: 8}
HULL_MAX_COUNT = {1: 2, 2: 3, 3: 4, 4: 5, 5: 6}
MODULE_RARE_CAP = {1: 0, 2: 0, 3: 1, 4: 2, 5: 3}


def _seed_from_parts(world_seed: int, system_id: str, stream: str) -> int:
    token = repr((world_seed, system_id, stream))
    digest = hashlib.sha256(token.encode("ascii")).hexdigest()
    return int(digest[:16], 16)


def _weighted_pick_index(weights: list[int], rng: random.Random) -> int:
    total = sum(weights)
    if total <= 0:
        raise ValueError("Weights must sum to a positive value.")
    threshold = rng.uniform(0, total)
    running = 0.0
    for index, value in enumerate(weights):
        running += value
        if threshold <= running:
            return index
    return len(weights) - 1


def _weighted_sample_without_replacement(
    candidates: list[dict[str, Any]],
    weights: list[int],
    count: int,
    rng: random.Random,
) -> list[dict[str, Any]]:
    pool = list(candidates)
    pool_weights = list(weights)
    picked: list[dict[str, Any]] = []
    for _ in range(max(0, min(count, len(pool)))):
        if not pool:
            break
        index = _weighted_pick_index(pool_weights, rng)
        picked.append(pool.pop(index))
        pool_weights.pop(index)
    return picked


def _module_has_banned_secondary(module: dict[str, Any]) -> bool:
    values: list[str] = []
    for key in ("secondary", "secondary_tags", "secondaries", "secondary_defaults"):
        raw = module.get(key)
        if isinstance(raw, str):
            values.append(raw)
        elif isinstance(raw, list):
            values.extend(str(entry) for entry in raw)
        elif isinstance(raw, set):
            values.extend(str(entry) for entry in sorted(raw))
    normalized = set(values)
    expanded = set(normalized)
    for value in normalized:
        if value.startswith("secondary:"):
            expanded.add(value.split("secondary:", 1)[1])
    return "prototype" in expanded or "alien" in expanded or "secondary:prototype" in expanded or "secondary:alien" in expanded


def _eligible_modules() -> list[dict[str, Any]]:
    modules = load_modules()["modules"]
    eligible = []
    for module in modules:
        if _module_has_banned_secondary(module):
            continue
        eligible.append(module)
    return eligible


def _eligible_hulls() -> list[dict[str, Any]]:
    hulls = load_hulls()["hulls"]
    eligible = []
    for hull in hulls:
        flags = set(hull.get("availability_flags", []))
        if "experimental" in flags or "alien" in flags:
            continue
        eligible.append(hull)
    return eligible


def generate_shipdock_inventory(world_seed: int, system_id: str, system_population: int) -> dict:
    if not isinstance(world_seed, int):
        raise ValueError("world_seed must be int.")
    if not isinstance(system_id, str) or not system_id:
        raise ValueError("system_id must be non-empty string.")
    if system_population not in {1, 2, 3, 4, 5}:
        raise ValueError("system_population must be int in range 1..5.")

    module_rng = random.Random(_seed_from_parts(world_seed, system_id, "shipdock_modules"))
    hull_rng = random.Random(_seed_from_parts(world_seed, system_id, "shipdock_hulls"))

    module_inventory: list[dict[str, Any]] = []
    hull_inventory: list[dict[str, Any]] = []

    if module_rng.random() <= MODULE_STOCK_CHANCE[system_population]:
        module_count = module_rng.randint(0, MODULE_MAX_COUNT[system_population])
        module_candidates = _eligible_modules()
        module_weights = [int(module.get("rarity_weight", 1)) for module in module_candidates]
        selected_modules = _weighted_sample_without_replacement(module_candidates, module_weights, module_count, module_rng)

        rare_cap = MODULE_RARE_CAP[system_population]
        rare_selected = [entry for entry in selected_modules if entry.get("rarity_tier") == "rare"]
        if len(rare_selected) > rare_cap:
            excess = len(rare_selected) - rare_cap
            drop_ids = {entry["module_id"] for entry in sorted(rare_selected, key=lambda item: item["module_id"], reverse=True)[:excess]}
            selected_modules = [entry for entry in selected_modules if entry["module_id"] not in drop_ids]

            selected_ids = {entry["module_id"] for entry in selected_modules}
            common_pool = [
                entry
                for entry in module_candidates
                if entry["rarity_tier"] == "common" and entry["module_id"] not in selected_ids
            ]
            common_weights = [int(entry.get("rarity_weight", 1)) for entry in common_pool]
            replacements = _weighted_sample_without_replacement(common_pool, common_weights, excess, module_rng)
            selected_modules.extend(replacements)

        module_inventory = [
            {"module_id": entry["module_id"], "base_price_credits": int(entry["base_price_credits"])}
            for entry in selected_modules
        ]

    if hull_rng.random() <= HULL_STOCK_CHANCE[system_population]:
        hull_count = hull_rng.randint(0, HULL_MAX_COUNT[system_population])
        hull_candidates = _eligible_hulls()
        hull_weights = [int(entry.get("rarity_weight", 1)) for entry in hull_candidates]
        selected_hulls = _weighted_sample_without_replacement(hull_candidates, hull_weights, hull_count, hull_rng)
        hull_inventory = [
            {"hull_id": entry["hull_id"], "base_price_credits": int(entry["base_price_credits"])}
            for entry in selected_hulls
        ]

    return {"modules": module_inventory, "hulls": hull_inventory}
