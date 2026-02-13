from __future__ import annotations

import copy
import hashlib
import random
from typing import Any

try:
    from data_loader import load_modules
except ModuleNotFoundError:
    from src.data_loader import load_modules


SALVAGE_COUNT_WEIGHTS = {0: 50, 1: 40, 2: 10}
RARITY_FACTOR = {"common": 1.0, "uncommon": 2.0, "rare": 4.0, "unique": 8.0}


def _rng_for_stream(world_seed: int | str, system_id: str, encounter_id: str, stream_name: str) -> random.Random:
    seed_string = f"{world_seed}|{system_id}|{encounter_id}|{stream_name}"
    digest = hashlib.sha256(seed_string.encode("ascii")).hexdigest()
    return random.Random(int(digest[:16], 16))


def _weighted_choice(items: list[Any], weights: list[float], rng: random.Random) -> Any:
    if not items or len(items) != len(weights):
        raise ValueError("weighted_choice requires non-empty equal-length item/weight arrays.")
    total = float(sum(weights))
    if total <= 0:
        raise ValueError("weighted_choice requires positive total weight.")
    threshold = rng.random() * total
    running = 0.0
    for item, weight in zip(items, weights):
        running += float(weight)
        if threshold < running:
            return item
    return items[-1]


def _weighted_sample_without_replacement(
    items: list[dict[str, Any]],
    weights: list[float],
    count: int,
    rng: random.Random,
) -> list[dict[str, Any]]:
    pool = list(items)
    pool_weights = list(weights)
    picked: list[dict[str, Any]] = []
    for _ in range(max(0, min(count, len(pool)))):
        selected = _weighted_choice(pool, pool_weights, rng)
        index = pool.index(selected)
        picked.append(selected)
        pool.pop(index)
        pool_weights.pop(index)
    return picked


def _modules_by_id() -> dict[str, dict[str, Any]]:
    return {entry["module_id"]: entry for entry in load_modules()["modules"]}


def _secondary_set(module_instance: dict[str, Any]) -> set[str]:
    raw = module_instance.get("secondary_tags", [])
    values: set[str] = set()
    if isinstance(raw, str):
        values.add(raw)
    elif isinstance(raw, list):
        values.update(str(entry) for entry in raw)
    for entry in list(values):
        if entry.startswith("secondary:"):
            values.add(entry.split("secondary:", 1)[1])
    return values


def _secondary_factor(module_instance: dict[str, Any]) -> float:
    secondaries = _secondary_set(module_instance)
    if not secondaries:
        return 1.0
    has_alien = "alien" in secondaries or "secondary:alien" in secondaries
    has_non_alien = any(tag not in {"alien", "secondary:alien"} for tag in secondaries)
    if has_alien and has_non_alien:
        return 3.0
    if has_alien:
        return 2.5
    if "prototype" in secondaries or "secondary:prototype" in secondaries:
        return 1.75
    if "unstable" in secondaries or "secondary:unstable" in secondaries:
        return 1.25
    return 1.0


def _salvage_weight(module_instance: dict[str, Any], module_def: dict[str, Any] | None) -> float:
    rarity_tier = "common" if module_def is None else str(module_def.get("rarity_tier", "common"))
    rarity_factor = RARITY_FACTOR.get(rarity_tier, 1.0)
    return rarity_factor * _secondary_factor(module_instance)


def resolve_salvage_modules(
    world_seed: int | str,
    system_id: str,
    encounter_id: str,
    destroyed_ship: dict,
) -> list:
    module_instances = list(destroyed_ship.get("module_instances", []))
    if not module_instances:
        return []

    count_rng = _rng_for_stream(world_seed, system_id, encounter_id, "npc_salvage_count")
    select_rng = _rng_for_stream(world_seed, system_id, encounter_id, "npc_salvage_select")
    mutation_rng = _rng_for_stream(world_seed, system_id, encounter_id, "npc_salvage_mutation")

    salvage_count = int(_weighted_choice([0, 1, 2], [SALVAGE_COUNT_WEIGHTS[0], SALVAGE_COUNT_WEIGHTS[1], SALVAGE_COUNT_WEIGHTS[2]], count_rng))
    salvage_count = max(0, min(2, salvage_count))
    if salvage_count == 0:
        return []
    if len(module_instances) <= salvage_count:
        selected = [copy.deepcopy(entry) for entry in module_instances]
    else:
        module_defs = _modules_by_id()
        weights = [_salvage_weight(entry, module_defs.get(entry.get("module_id", ""))) for entry in module_instances]
        selected = [copy.deepcopy(entry) for entry in _weighted_sample_without_replacement(module_instances, weights, salvage_count, select_rng)]

    module_defs = _modules_by_id()
    for instance in selected:
        if _secondary_set(instance):
            continue
        module_def = module_defs.get(instance.get("module_id", ""))
        mutation_allowed = True
        if module_def is not None:
            salvage_policy = module_def.get("salvage_policy")
            if isinstance(salvage_policy, dict):
                mutation_allowed = bool(salvage_policy.get("mutation_allowed", True))
        if not mutation_allowed:
            continue
        if mutation_rng.random() < 0.20:
            instance["secondary_tags"] = ["secondary:unstable"]
    return selected
