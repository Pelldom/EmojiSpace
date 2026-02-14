from __future__ import annotations

import logging
import math
from functools import lru_cache
from typing import Any

from data_loader import load_hulls, load_modules

logger = logging.getLogger(__name__)

_FRAMES = {"MIL", "CIV", "FRG", "XA", "XB", "XC", "ALN"}
_TIER_BASELINE = {1: 1, 2: 1, 3: 2, 4: 2, 5: 3}
_TIER_HULL_BASELINE = {1: 8, 2: 10, 3: 12, 4: 15, 5: 18}
_FRAME_HULL_BIAS = {"MIL": 2, "CIV": 0, "FRG": 3, "XA": 0, "XB": -2, "XC": 4, "ALN": 1}

_SLOT_DISTRIBUTION = {
    (1, "MIL"): (2, 1, 1, 0, 4),
    (1, "CIV"): (1, 2, 1, 0, 4),
    (1, "FRG"): (1, 1, 2, 0, 4),
    (1, "XA"): (1, 1, 3, 0, 5),
    (1, "XB"): (3, 1, 1, 0, 5),
    (1, "XC"): (1, 3, 1, 0, 5),
    (1, "ALN"): (1, 1, 1, 1, 4),
    (2, "MIL"): (3, 1, 1, 0, 5),
    (2, "CIV"): (1, 2, 2, 0, 5),
    (2, "FRG"): (1, 1, 3, 0, 5),
    (2, "XA"): (1, 1, 4, 0, 6),
    (2, "XB"): (3, 1, 2, 0, 6),
    (2, "XC"): (1, 3, 2, 0, 6),
    (2, "ALN"): (1, 1, 2, 1, 5),
    (3, "MIL"): (3, 2, 1, 0, 6),
    (3, "CIV"): (2, 2, 2, 0, 6),
    (3, "FRG"): (1, 2, 3, 0, 6),
    (3, "XA"): (2, 1, 4, 0, 7),
    (3, "XB"): (4, 1, 2, 0, 7),
    (3, "XC"): (2, 3, 2, 0, 7),
    (3, "ALN"): (1, 1, 2, 2, 6),
    (4, "MIL"): (3, 3, 1, 0, 7),
    (4, "CIV"): (2, 2, 3, 0, 7),
    (4, "FRG"): (1, 2, 4, 0, 7),
    (4, "XA"): (2, 2, 4, 0, 8),
    (4, "XB"): (4, 2, 2, 0, 8),
    (4, "XC"): (2, 4, 2, 0, 8),
    (4, "ALN"): (2, 1, 2, 2, 7),
    (5, "MIL"): (4, 3, 1, 0, 8),
    (5, "CIV"): (3, 2, 3, 0, 8),
    (5, "FRG"): (1, 2, 5, 0, 8),
    (5, "XA"): (2, 2, 5, 0, 9),
    (5, "XB"): (5, 2, 2, 0, 9),
    (5, "XC"): (3, 4, 2, 0, 9),
    (5, "ALN"): (2, 1, 2, 3, 8),
}


def get_slot_distribution(frame: str, tier: int) -> dict[str, int]:
    if frame not in _FRAMES:
        raise ValueError(f"Unknown frame '{frame}'.")
    if tier not in {1, 2, 3, 4, 5}:
        raise ValueError(f"Invalid tier '{tier}'. Must be 1..5.")
    weapon_slots, defense_slots, utility_slots, untyped_slots, total_slots = _SLOT_DISTRIBUTION[(tier, frame)]
    return {
        "weapon_slots": weapon_slots,
        "defense_slots": defense_slots,
        "utility_slots": utility_slots,
        "untyped_slots": untyped_slots,
        "total_slots": total_slots,
    }


def tier_baseline(tier: int) -> int:
    if tier not in _TIER_BASELINE:
        raise ValueError(f"Invalid tier '{tier}'. Must be 1..5.")
    return _TIER_BASELINE[tier]


@lru_cache(maxsize=1)
def _hulls_by_id() -> dict[str, dict[str, Any]]:
    payload = load_hulls()
    return {entry["hull_id"]: entry for entry in payload["hulls"]}


@lru_cache(maxsize=1)
def _modules_by_id() -> dict[str, dict[str, Any]]:
    payload = load_modules()
    return {entry["module_id"]: entry for entry in payload["modules"]}


def _normalized_secondary_tags(module_instance: dict[str, Any]) -> set[str]:
    raw_tags = module_instance.get("secondary_tags", [])
    if raw_tags is None:
        return set()
    if not isinstance(raw_tags, list):
        raise ValueError("Module instance secondary_tags must be a list when present.")
    normalized = set()
    for entry in raw_tags:
        if not isinstance(entry, str):
            raise ValueError("Module instance secondary_tags entries must be strings.")
        normalized.add(entry)
        if entry.startswith("secondary:"):
            normalized.add(entry.split("secondary:", 1)[1])
    return normalized


def _has_secondary(secondary_tags: set[str], name: str) -> bool:
    return name in secondary_tags or f"secondary:{name}" in secondary_tags


def _validate_instance_structure(module_instance: dict[str, Any]) -> None:
    if not isinstance(module_instance, dict):
        raise ValueError("Each module instance must be an object.")
    if "module_id" not in module_instance:
        raise ValueError("Each module instance must include module_id.")
    if not isinstance(module_instance["module_id"], str):
        raise ValueError("module_id must be a string.")
    if "secondary_tags" in module_instance and not isinstance(module_instance["secondary_tags"], list):
        raise ValueError("secondary_tags must be a list when present.")


def _main_numeric_bonus_key(numeric_bonus: dict[str, Any]) -> str | None:
    keys = [key for key in ("weapon", "defense", "engine") if key in numeric_bonus]
    if not keys:
        return None
    return keys[0]


def _module_consumption_units(secondary_tags: set[str]) -> float:
    return 0.5 if _has_secondary(secondary_tags, "compact") else 1.0


def _required_filled_slots(modules_for_type: list[dict[str, Any]]) -> int:
    units = sum(_module_consumption_units(entry["secondary_tags"]) for entry in modules_for_type)
    return int(math.ceil(units))


def _validate_primary_tag_vs_slot_type(slot_type: str, primary_tag: str, module_id: str) -> None:
    if slot_type == "weapon" and not primary_tag.startswith("combat:weapon_"):
        raise ValueError(f"Module '{module_id}' has invalid primary_tag '{primary_tag}' for weapon slot_type.")
    if slot_type == "defense" and not primary_tag.startswith("combat:defense_"):
        raise ValueError(f"Module '{module_id}' has invalid primary_tag '{primary_tag}' for defense slot_type.")
    if slot_type == "utility":
        if not (primary_tag.startswith("combat:utility_") or primary_tag.startswith("ship:utility_")):
            raise ValueError(f"Module '{module_id}' has invalid primary_tag '{primary_tag}' for utility slot_type.")


def compute_hull_max_from_ship_state(ship_state: dict[str, Any]) -> int:
    hull = _hulls_by_id().get(ship_state.get("hull_id"))
    if hull is None:
        raise ValueError(f"Unknown hull_id '{ship_state.get('hull_id')}'.")
    value = _TIER_HULL_BASELINE[hull["tier"]] + _FRAME_HULL_BIAS[hull["frame"]]
    is_experimental_hull = "ship:trait_experimental" in hull.get("traits", [])
    is_alien_hull = "ship:trait_alien" in hull.get("traits", [])
    module_defs = _modules_by_id()
    for module_instance in ship_state.get("module_instances", []):
        module_id = module_instance.get("module_id")
        if not isinstance(module_id, str):
            continue
        module_def = module_defs.get(module_id)
        if module_def is None:
            continue
        secondary_tags = _normalized_secondary_tags(module_instance)
        if _has_secondary(secondary_tags, "alien") and is_alien_hull:
            value += 1
        if _has_secondary(secondary_tags, "prototype") and is_experimental_hull:
            value += 1
        if module_def["primary_tag"] == "combat:defense_armored":
            value += 1
        if _has_secondary(secondary_tags, "unstable"):
            value -= 1
    return max(4, int(value))


def assemble_ship(
    hull_id: str,
    module_instances: list[dict[str, Any]],
    degradation_state: dict[str, int] | None = None,
) -> dict[str, Any]:
    hull = _hulls_by_id().get(hull_id)
    if hull is None:
        raise ValueError(f"Unknown hull_id '{hull_id}'.")
    if not isinstance(module_instances, list):
        raise ValueError("module_instances must be a list.")

    slots = get_slot_distribution(hull["frame"], hull["tier"])
    module_defs = _modules_by_id()

    resolved: list[dict[str, Any]] = []
    for module_instance in module_instances:
        _validate_instance_structure(module_instance)
        module_id = module_instance["module_id"]
        module_def = module_defs.get(module_id)
        if module_def is None:
            raise ValueError(f"Unknown module_id '{module_id}'.")
        secondary_tags = _normalized_secondary_tags(module_instance)
        slot_type = module_def["slot_type"]
        primary_tag = module_def["primary_tag"]
        _validate_primary_tag_vs_slot_type(slot_type, primary_tag, module_id)
        resolved.append(
            {
                "module_id": module_id,
                "slot_type": slot_type,
                "primary_tag": primary_tag,
                "numeric_bonus": module_def.get("numeric_bonus", {}),
                "secondary_tags": secondary_tags,
            }
        )

    by_type = {"weapon": [], "defense": [], "utility": []}
    for entry in resolved:
        by_type[entry["slot_type"]].append(entry)

    required_slots = {slot_type: _required_filled_slots(entries) for slot_type, entries in by_type.items()}
    base_slots = {
        "weapon": slots["weapon_slots"],
        "defense": slots["defense_slots"],
        "utility": slots["utility_slots"],
    }

    untyped_remaining = slots["untyped_slots"]
    untyped_alloc = {"weapon": 0, "defense": 0, "utility": 0}
    base_used = {"weapon": 0, "defense": 0, "utility": 0}

    for slot_type in ("weapon", "defense", "utility"):
        needed = required_slots[slot_type]
        base_used[slot_type] = min(base_slots[slot_type], needed)
        overflow = needed - base_used[slot_type]
        if overflow > 0:
            if overflow > untyped_remaining:
                raise ValueError(
                    f"Loadout exceeds slot capacity for {slot_type}: needs {needed}, "
                    f"base {base_slots[slot_type]}, untyped remaining {untyped_remaining}."
                )
            untyped_alloc[slot_type] = overflow
            untyped_remaining -= overflow

    slot_assignment = {
        "weapon": {
            "base_slots_used": base_used["weapon"],
            "untyped_slots_used": untyped_alloc["weapon"],
            "total_slots_used": required_slots["weapon"],
            "module_count": len(by_type["weapon"]),
            "compact_count": sum(1 for entry in by_type["weapon"] if _has_secondary(entry["secondary_tags"], "compact")),
        },
        "defense": {
            "base_slots_used": base_used["defense"],
            "untyped_slots_used": untyped_alloc["defense"],
            "total_slots_used": required_slots["defense"],
            "module_count": len(by_type["defense"]),
            "compact_count": sum(1 for entry in by_type["defense"] if _has_secondary(entry["secondary_tags"], "compact")),
        },
        "utility": {
            "base_slots_used": base_used["utility"],
            "untyped_slots_used": untyped_alloc["utility"],
            "total_slots_used": required_slots["utility"],
            "module_count": len(by_type["utility"]),
            "compact_count": sum(1 for entry in by_type["utility"] if _has_secondary(entry["secondary_tags"], "compact")),
        },
        "untyped_allocations": dict(untyped_alloc),
    }

    slot_fill_bonus = {
        "weapon": required_slots["weapon"],
        "defense": required_slots["defense"],
        "engine": 0,
    }

    is_alien_hull = "ship:trait_alien" in hull.get("traits", [])
    is_experimental_hull = "ship:trait_experimental" in hull.get("traits", [])

    module_bonus = {"weapon": 0, "defense": 0, "engine": 0}
    ship_utility_effects = {
        "physical_cargo_bonus": 0,
        "data_cargo_bonus": 0,
        "interdiction_bonus": 0,
        "smuggler_flag": False,
        "unlock_mining": False,
        "unlock_probe": False,
    }
    fuel_bonus = 0

    for entry in resolved:
        numeric_bonus = entry["numeric_bonus"] or {}
        for band in ("weapon", "defense", "engine"):
            value = numeric_bonus.get(band, 0)
            if value:
                module_bonus[band] += int(value)

        main_key = _main_numeric_bonus_key(numeric_bonus)
        if main_key is not None:
            secondary_delta = 0
            if _has_secondary(entry["secondary_tags"], "efficient"):
                secondary_delta += 1
            if _has_secondary(entry["secondary_tags"], "alien") and is_alien_hull:
                secondary_delta += 1
            module_bonus[main_key] += secondary_delta

        if entry["primary_tag"] == "ship:utility_extra_cargo":
            ship_utility_effects["physical_cargo_bonus"] += 5
        elif entry["primary_tag"] == "ship:utility_data_array":
            ship_utility_effects["data_cargo_bonus"] += 5
        elif entry["primary_tag"] == "ship:utility_interdiction":
            ship_utility_effects["interdiction_bonus"] += 1
        elif entry["primary_tag"] == "ship:utility_smuggler_hold":
            ship_utility_effects["smuggler_flag"] = True
        elif entry["primary_tag"] == "ship:utility_mining_equipment":
            ship_utility_effects["unlock_mining"] = True
        elif entry["primary_tag"] == "ship:utility_probe_array":
            ship_utility_effects["unlock_probe"] = True
        elif entry["primary_tag"] == "ship:utility_extra_fuel":
            fuel_bonus += 5

    base_bands = {
        "weapon": max(0, tier_baseline(hull["tier"]) + int(hull["bias"]["weapon"])),
        "defense": max(0, tier_baseline(hull["tier"]) + int(hull["bias"]["defense"])),
        "engine": max(0, tier_baseline(hull["tier"]) + int(hull["bias"]["engine"])),
    }

    pre_degradation = {
        band: max(0, base_bands[band] + slot_fill_bonus[band] + module_bonus[band]) for band in ("weapon", "defense", "engine")
    }

    subsystem_modules = {
        "weapon": list(by_type["weapon"]),
        "defense": list(by_type["defense"]),
        "engine": [
            entry
            for entry in by_type["utility"]
            if ("engine" in (entry["numeric_bonus"] or {})) or entry["primary_tag"] == "combat:utility_engine_boost"
        ],
    }

    capacity: dict[str, int] = {}
    for subsystem in ("weapon", "defense", "engine"):
        value = len(subsystem_modules[subsystem])
        for entry in subsystem_modules[subsystem]:
            if _has_secondary(entry["secondary_tags"], "enhanced"):
                value += 1
            if _has_secondary(entry["secondary_tags"], "unstable"):
                value -= 1
            if _has_secondary(entry["secondary_tags"], "prototype") and not is_experimental_hull:
                value -= 1
        capacity[subsystem] = max(1, value)

    state = {"weapon": 0, "defense": 0, "engine": 0}
    if degradation_state is not None:
        if not isinstance(degradation_state, dict):
            raise ValueError("degradation_state must be a dict when provided.")
        for key in ("weapon", "defense", "engine"):
            value = degradation_state.get(key, 0)
            if not isinstance(value, int):
                raise ValueError(f"degradation_state.{key} must be an integer.")
            state[key] = value

    red = {band: state[band] >= capacity[band] for band in ("weapon", "defense", "engine")}
    effective = {}
    for band in ("weapon", "defense", "engine"):
        if red[band]:
            effective[band] = 0
        else:
            effective[band] = max(0, pre_degradation[band] - state[band])

    hull_max = compute_hull_max_from_ship_state(
        {"hull_id": hull_id, "module_instances": module_instances}
    )
    result = {
        "hull_id": hull_id,
        "frame": hull["frame"],
        "tier": hull["tier"],
        "hull_max": int(hull_max),
        "fuel_capacity": int(hull["fuel_capacity_base"]) + fuel_bonus,
        "slots": dict(slots),
        "slot_assignment": slot_assignment,
        "bonuses": {
            "slot_fill": slot_fill_bonus,
            "module_bonus": module_bonus,
        },
        "bands": {
            "base": base_bands,
            "pre_degradation": pre_degradation,
            "effective": effective,
            "red": red,
        },
        "degradation": {
            "capacity": capacity,
            "state": state,
        },
        "ship_utility_effects": ship_utility_effects,
    }

    logger.info(
        "assemble_ship hull_id=%s modules=%s slots_used=%s red=%s",
        hull_id,
        len(module_instances),
        {
            "weapon": required_slots["weapon"],
            "defense": required_slots["defense"],
            "utility": required_slots["utility"],
            "untyped_alloc": dict(untyped_alloc),
        },
        red,
    )
    return result
