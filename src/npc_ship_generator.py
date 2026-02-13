from __future__ import annotations

import hashlib
import random
from typing import Any

try:
    from data_loader import load_hulls, load_modules
    from ship_assembler import assemble_ship, get_slot_distribution
    from combat_resolver import _compute_hull_max_from_ship_state
except ModuleNotFoundError:
    from src.data_loader import load_hulls, load_modules
    from src.ship_assembler import assemble_ship, get_slot_distribution
    from src.combat_resolver import _compute_hull_max_from_ship_state


TIER_WEIGHTS = {
    1: {1: 45, 2: 30, 3: 15, 4: 7, 5: 3},
    2: {1: 35, 2: 30, 3: 18, 4: 12, 5: 5},
    3: {1: 25, 2: 25, 3: 20, 4: 20, 5: 10},
    4: {1: 15, 2: 20, 3: 22, 4: 23, 5: 20},
    5: {1: 10, 2: 15, 3: 20, 4: 25, 5: 30},
}

FRAME_WEIGHTS_BY_SUBTYPE = {
    "civilian_trader_ship": {"CIV": 80, "FRG": 20},
    "civilian_patrol_ship": {"CIV": 70, "MIL": 30},
    "bounty_hunter": {"MIL": 80, "CIV": 20},
    "pirate_raider_ship": {"MIL": 60, "FRG": 25, "CIV": 15},
    "derelict_ship": {"CIV": 50, "FRG": 35, "MIL": 15},
    "alien_vessel": {"ALN": 100},
    "experimental_vessel": {"XA": 34, "XB": 33, "XC": 33},
    # Existing subtype aliases in data/encounter_types.json.
    "pirate_raider": {"MIL": 60, "FRG": 25, "CIV": 15},
}

HULL_RARITY_WEIGHTS = {"common": 50, "uncommon": 30, "rare": 15, "unique": 5}
FILL_FRACTION_WEIGHTS = [(0.00, 20), (0.25, 25), (0.50, 30), (0.75, 15), (1.00, 10)]

MODULE_RARITY_MULTIPLIERS = {
    1: {"common": 1.00, "uncommon": 0.30, "rare": 0.10, "unique": 0.02},
    2: {"common": 1.00, "uncommon": 0.45, "rare": 0.15, "unique": 0.03},
    3: {"common": 1.00, "uncommon": 0.60, "rare": 0.25, "unique": 0.05},
    4: {"common": 1.00, "uncommon": 0.75, "rare": 0.40, "unique": 0.10},
    5: {"common": 1.00, "uncommon": 0.90, "rare": 0.55, "unique": 0.15},
}

SECONDARY_DISTRIBUTION = [
    ("none", 50),
    ("unstable", 20),
    ("prototype", 10),
    ("compact", 5),
    ("enhanced", 5),
    ("efficient", 5),
    ("alien", 5),
]


def _rng_for_stream(world_seed: int, system_id: str, encounter_id: str, stream_name: str) -> random.Random:
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


def _hulls() -> list[dict[str, Any]]:
    return load_hulls()["hulls"]


def _modules() -> list[dict[str, Any]]:
    return load_modules()["modules"]


def _frame_weights_for_subtype(encounter_subtype: str) -> dict[str, int]:
    return dict(FRAME_WEIGHTS_BY_SUBTYPE.get(encounter_subtype, {"CIV": 100}))


def _nearest_tier_with_hulls(target_tier: int, allowed_frames: set[str], hulls: list[dict[str, Any]]) -> int:
    candidate_tiers = sorted({entry["tier"] for entry in hulls if entry["frame"] in allowed_frames})
    if not candidate_tiers:
        raise ValueError("No eligible hulls available for allowed frames.")
    ranked = sorted(candidate_tiers, key=lambda tier: (abs(tier - target_tier), tier))
    return ranked[0]


def _select_tier(system_population: int, rng: random.Random) -> int:
    if system_population not in TIER_WEIGHTS:
        raise ValueError("system_population must be 1..5.")
    tiers = [1, 2, 3, 4, 5]
    weights = [TIER_WEIGHTS[system_population][tier] for tier in tiers]
    return int(_weighted_choice(tiers, weights, rng))


def _select_hull(selected_tier: int, encounter_subtype: str, rng: random.Random) -> dict[str, Any]:
    hulls = _hulls()
    frame_weights = _frame_weights_for_subtype(encounter_subtype)
    allowed_frames = set(frame_weights.keys())

    tier_for_selection = selected_tier
    if not any(entry["tier"] == tier_for_selection and entry["frame"] in allowed_frames for entry in hulls):
        tier_for_selection = _nearest_tier_with_hulls(tier_for_selection, allowed_frames, hulls)

    frame_candidates = [frame for frame in frame_weights if any(entry["tier"] == tier_for_selection and entry["frame"] == frame for entry in hulls)]
    if not frame_candidates:
        raise ValueError("No eligible frame candidates for selected tier.")

    frame = _weighted_choice(frame_candidates, [frame_weights[key] for key in frame_candidates], rng)
    pool = [entry for entry in hulls if entry["tier"] == tier_for_selection and entry["frame"] == frame]
    if not pool:
        raise ValueError("No hulls in selected tier/frame pool.")
    weights = [HULL_RARITY_WEIGHTS.get(entry.get("rarity_tier", "common"), 1) for entry in pool]
    return _weighted_choice(pool, weights, rng)


def _fill_slots_target(total_slots: int, rng: random.Random) -> int:
    fraction = _weighted_choice([entry[0] for entry in FILL_FRACTION_WEIGHTS], [entry[1] for entry in FILL_FRACTION_WEIGHTS], rng)
    target = int(round(total_slots * float(fraction)))
    return max(0, min(total_slots, target))


def _module_weight(module: dict[str, Any], hull_tier: int) -> float:
    rarity_tier = str(module.get("rarity_tier", "common"))
    multiplier = MODULE_RARITY_MULTIPLIERS[hull_tier].get(rarity_tier, 0.0)
    return float(module.get("rarity_weight", 0)) * multiplier


def _roll_secondary_tags(module_def: dict[str, Any], rng: random.Random) -> list[str]:
    secondary_policy = module_def.get("secondary_policy", {})
    if isinstance(secondary_policy, dict) and secondary_policy.get("allowed") is False:
        return []

    labels = [entry[0] for entry in SECONDARY_DISTRIBUTION]
    weights = [entry[1] for entry in SECONDARY_DISTRIBUTION]
    first = _weighted_choice(labels, weights, rng)
    if first == "none":
        return []
    if first != "alien":
        return [f"secondary:{first}"]

    second_labels = [label for label in labels if label != "alien"]
    second_weights = [weight for label, weight in SECONDARY_DISTRIBUTION if label != "alien"]
    second = _weighted_choice(second_labels, second_weights, rng)
    tags = ["secondary:alien"]
    if second != "none":
        tags.append(f"secondary:{second}")
    return tags


def _candidate_modules_for_slot(slot_type: str, hull_frame: str, hull_tier: int) -> list[tuple[dict[str, Any], float]]:
    candidates: list[tuple[dict[str, Any], float]] = []
    for module in _modules():
        module_slot = module["slot_type"]
        if slot_type != "untyped" and module_slot != slot_type:
            continue
        allowed_frames = module.get("allowed_on_frames")
        if isinstance(allowed_frames, list) and hull_frame not in allowed_frames:
            continue
        weight = _module_weight(module, hull_tier)
        if weight <= 0:
            continue
        candidates.append((module, weight))
    return candidates


def _slot_fill_plan(slots: dict[str, int], target: int) -> list[str]:
    plan: list[str] = []
    remaining = target
    for slot_type, key in (("weapon", "weapon_slots"), ("defense", "defense_slots"), ("utility", "utility_slots"), ("untyped", "untyped_slots")):
        capacity = int(slots[key])
        use = min(capacity, remaining)
        plan.extend([slot_type] * use)
        remaining -= use
        if remaining <= 0:
            break
    return plan


def generate_npc_ship(
    world_seed: int,
    system_id: str,
    system_population: int,
    encounter_id: str,
    encounter_subtype: str,
) -> dict:
    hull_rng = _rng_for_stream(world_seed, system_id, encounter_id, "npc_hull_select")
    fill_rng = _rng_for_stream(world_seed, system_id, encounter_id, "npc_loadout_fill")
    module_rng = _rng_for_stream(world_seed, system_id, encounter_id, "npc_module_select")
    secondary_rng = _rng_for_stream(world_seed, system_id, encounter_id, "npc_secondary_rolls")

    selected_tier = _select_tier(system_population, hull_rng)
    hull = _select_hull(selected_tier, encounter_subtype, hull_rng)
    slots = get_slot_distribution(hull["frame"], hull["tier"])
    fill_target = _fill_slots_target(int(slots["total_slots"]), fill_rng)
    fill_plan = _slot_fill_plan(slots, fill_target)

    module_instances: list[dict[str, Any]] = []
    for slot_type in fill_plan:
        candidates = _candidate_modules_for_slot(slot_type, hull["frame"], hull["tier"])
        if not candidates:
            continue
        module_def = _weighted_choice([entry[0] for entry in candidates], [entry[1] for entry in candidates], module_rng)
        module_instances.append(
            {
                "module_id": module_def["module_id"],
                "secondary_tags": _roll_secondary_tags(module_def, secondary_rng),
            }
        )

    degradation_state = {"weapon": 0, "defense": 0, "engine": 0}
    assembled = assemble_ship(hull["hull_id"], module_instances, degradation_state)
    ship_state = {
        "hull_id": hull["hull_id"],
        "module_instances": list(module_instances),
        "degradation_state": dict(degradation_state),
    }
    max_hull_integrity = _compute_hull_max_from_ship_state(ship_state)
    return {
        "hull_id": hull["hull_id"],
        "module_instances": list(module_instances),
        "degradation_state": dict(degradation_state),
        "current_hull_integrity": int(max_hull_integrity),
        "current_fuel": int(assembled["fuel_capacity"]),
    }
