from __future__ import annotations

import json
from pathlib import Path
from typing import Any


_ALLOWED_FRAMES = {"MIL", "CIV", "FRG", "XA", "XB", "XC", "ALN"}
_ALLOWED_SLOT_TYPES = {"weapon", "defense", "utility"}
_CREW_BANDS = {
    1: (0, 1),
    2: (1, 2),
    3: (2, 3),
    4: (3, 4),
    5: (4, 5),
}
_CREW_CAPACITY_EXCEPTIONS = {
    "frg_t1_carpenter_ant": 2,
    "mil_t1_paper_wasp": 2,
}

_HULL_REQUIRED_KEYS = {
    "hull_id",
    "name",
    "tier",
    "frame",
    "traits",
    "bias",
    "cargo",
    "crew_capacity",
    "base_price_credits",
    "rarity_tier",
    "mission_grantable",
    "availability_flags",
    "description",
}

_MODULE_REQUIRED_KEYS = {
    "module_id",
    "name",
    "display_names",
    "slot_type",
    "primary_tag",
    "base_price_credits",
    "rarity_weight",
    "rarity_tier",
    "mission_grantable",
    "secondary_policy",
    "salvage_policy",
    "description",
}
_MODULE_OPTIONAL_KEYS = {"numeric_bonus"}
_MODULE_ALLOWED_KEYS = _MODULE_REQUIRED_KEYS | _MODULE_OPTIONAL_KEYS


def _data_root() -> Path:
    return Path(__file__).resolve().parents[1] / "data"


def load_hulls() -> dict[str, Any]:
    payload = _load_json(_data_root() / "hulls.json")
    version = payload.get("version")
    if not isinstance(version, str) or not version:
        raise ValueError("hulls.json root: 'version' must exist and be a non-empty string.")
    hulls = payload.get("hulls")
    if not isinstance(hulls, list):
        raise ValueError("hulls.json root: 'hulls' must be a list.")

    validated = []
    for index, hull in enumerate(hulls):
        if not isinstance(hull, dict):
            raise ValueError(f"hulls.json hull[{index}]: hull must be an object.")
        _validate_hull(hull, index)
        validated.append(hull)
    return {"version": version, "hulls": validated}


def load_modules() -> dict[str, Any]:
    payload = _load_json(_data_root() / "modules.json")
    version = payload.get("version")
    if not isinstance(version, str) or not version:
        raise ValueError("modules.json root: 'version' must exist and be a non-empty string.")
    modules = payload.get("modules")
    if not isinstance(modules, list):
        raise ValueError("modules.json root: 'modules' must be a list.")

    validated = []
    for index, module in enumerate(modules):
        if not isinstance(module, dict):
            raise ValueError(f"modules.json module[{index}]: module must be an object.")
        _validate_module(module, index)
        validated.append(module)
    return {"version": version, "modules": validated}


def _load_json(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as error:
        raise ValueError(f"{path.name}: file not found.") from error
    except json.JSONDecodeError as error:
        raise ValueError(f"{path.name}: invalid JSON.") from error


def _validate_hull(hull: dict[str, Any], index: int) -> None:
    missing = sorted(_HULL_REQUIRED_KEYS - set(hull.keys()))
    if missing:
        raise ValueError(f"hulls.json hull[{index}]: missing required keys: {missing}")
    extra = sorted(set(hull.keys()) - _HULL_REQUIRED_KEYS)
    if extra:
        raise ValueError(f"hulls.json hull[{index}]: unexpected keys: {extra}")

    _require_type(hull, index, "hull_id", str, "hulls.json")
    _require_type(hull, index, "name", str, "hulls.json")
    _require_type(hull, index, "description", str, "hulls.json")
    _require_type(hull, index, "traits", list, "hulls.json")
    _require_type(hull, index, "availability_flags", list, "hulls.json")
    _require_type(hull, index, "rarity_tier", str, "hulls.json")
    _require_type(hull, index, "mission_grantable", bool, "hulls.json")
    _require_type(hull, index, "crew_capacity", int, "hulls.json")
    _require_type(hull, index, "base_price_credits", int, "hulls.json")
    _require_type(hull, index, "tier", int, "hulls.json")
    _require_type(hull, index, "frame", str, "hulls.json")

    tier = hull["tier"]
    if tier not in {1, 2, 3, 4, 5}:
        raise ValueError(f"hulls.json hull[{index}]: 'tier' must be 1..5.")
    if hull["frame"] not in _ALLOWED_FRAMES:
        raise ValueError(f"hulls.json hull[{index}]: invalid frame '{hull['frame']}'.")

    crew_capacity = hull["crew_capacity"]
    low, high = _CREW_BANDS[tier]
    hull_id = hull["hull_id"]
    if hull_id in _CREW_CAPACITY_EXCEPTIONS:
        if crew_capacity != _CREW_CAPACITY_EXCEPTIONS[hull_id]:
            raise ValueError(
                f"hulls.json hull[{index}]: crew_capacity {crew_capacity} must be {_CREW_CAPACITY_EXCEPTIONS[hull_id]}"
                f" for exceptional hull_id '{hull_id}'."
            )
    elif not (low <= crew_capacity <= high):
        raise ValueError(
            f"hulls.json hull[{index}]: crew_capacity {crew_capacity} out of range {low}..{high} for tier {tier}."
        )

    bias = hull.get("bias")
    if not isinstance(bias, dict):
        raise ValueError(f"hulls.json hull[{index}]: 'bias' must be an object.")
    bias_keys = {"weapon", "defense", "engine", "hull"}
    if set(bias.keys()) != bias_keys:
        raise ValueError(f"hulls.json hull[{index}]: 'bias' must have keys {sorted(bias_keys)}.")
    for key in sorted(bias_keys):
        if not isinstance(bias[key], int):
            raise ValueError(f"hulls.json hull[{index}]: bias.{key} must be an integer.")

    cargo = hull.get("cargo")
    if not isinstance(cargo, dict):
        raise ValueError(f"hulls.json hull[{index}]: 'cargo' must be an object.")
    cargo_keys = {"physical_base", "data_base"}
    if set(cargo.keys()) != cargo_keys:
        raise ValueError(f"hulls.json hull[{index}]: 'cargo' must have keys {sorted(cargo_keys)}.")
    if not isinstance(cargo["physical_base"], int):
        raise ValueError(f"hulls.json hull[{index}]: cargo.physical_base must be an integer.")
    if not isinstance(cargo["data_base"], int):
        raise ValueError(f"hulls.json hull[{index}]: cargo.data_base must be an integer.")


def _validate_module(module: dict[str, Any], index: int) -> None:
    missing = sorted(_MODULE_REQUIRED_KEYS - set(module.keys()))
    if missing:
        raise ValueError(f"modules.json module[{index}]: missing required keys: {missing}")
    extra = sorted(set(module.keys()) - _MODULE_ALLOWED_KEYS)
    if extra:
        raise ValueError(f"modules.json module[{index}]: unexpected keys: {extra}")

    _require_type(module, index, "module_id", str, "modules.json")
    _require_type(module, index, "name", str, "modules.json")
    _require_type(module, index, "slot_type", str, "modules.json")
    _require_type(module, index, "primary_tag", str, "modules.json")
    _require_type(module, index, "base_price_credits", int, "modules.json")
    _require_type(module, index, "rarity_weight", int, "modules.json")
    _require_type(module, index, "rarity_tier", str, "modules.json")
    _require_type(module, index, "mission_grantable", bool, "modules.json")
    _require_type(module, index, "description", str, "modules.json")
    _require_type(module, index, "display_names", list, "modules.json")

    display_names = module["display_names"]
    if len(display_names) < 1:
        raise ValueError(f"modules.json module[{index}]: display_names must contain at least one entry.")
    for name_index, display_name in enumerate(display_names):
        if not isinstance(display_name, str):
            raise ValueError(f"modules.json module[{index}]: display_names[{name_index}] must be a string.")
        if not display_name:
            raise ValueError(f"modules.json module[{index}]: display_names[{name_index}] must not be empty.")

    if module["slot_type"] not in _ALLOWED_SLOT_TYPES:
        raise ValueError(f"modules.json module[{index}]: invalid slot_type '{module['slot_type']}'.")

    if module["rarity_weight"] <= 0:
        raise ValueError(f"modules.json module[{index}]: rarity_weight must be > 0.")

    _validate_module_primary_tag(module["slot_type"], module["primary_tag"], index)

    secondary_policy = module.get("secondary_policy")
    if not isinstance(secondary_policy, dict) or set(secondary_policy.keys()) != {"allowed"}:
        raise ValueError(f"modules.json module[{index}]: secondary_policy must be an object with key 'allowed'.")
    if not isinstance(secondary_policy["allowed"], bool):
        raise ValueError(f"modules.json module[{index}]: secondary_policy.allowed must be bool.")

    salvage_policy = module.get("salvage_policy")
    if not isinstance(salvage_policy, dict):
        raise ValueError(f"modules.json module[{index}]: salvage_policy must be an object.")
    salvage_keys = set(salvage_policy.keys())
    allowed_salvage_keys = {"salvageable", "mutation_allowed", "unstable_inject_chance_override"}
    if not {"salvageable", "mutation_allowed"}.issubset(salvage_keys):
        raise ValueError(
            f"modules.json module[{index}]: salvage_policy must contain 'salvageable' and 'mutation_allowed'."
        )
    if not salvage_keys.issubset(allowed_salvage_keys):
        raise ValueError(f"modules.json module[{index}]: salvage_policy has unexpected keys.")
    if not isinstance(salvage_policy["salvageable"], bool):
        raise ValueError(f"modules.json module[{index}]: salvage_policy.salvageable must be bool.")
    if not isinstance(salvage_policy["mutation_allowed"], bool):
        raise ValueError(f"modules.json module[{index}]: salvage_policy.mutation_allowed must be bool.")

    numeric_bonus = module.get("numeric_bonus")
    if numeric_bonus is not None:
        if not isinstance(numeric_bonus, dict):
            raise ValueError(f"modules.json module[{index}]: numeric_bonus must be an object when provided.")
        allowed_bonus_keys = {"weapon", "defense", "engine"}
        extra_bonus_keys = set(numeric_bonus.keys()) - allowed_bonus_keys
        if extra_bonus_keys:
            raise ValueError(
                f"modules.json module[{index}]: numeric_bonus has unexpected keys {sorted(extra_bonus_keys)}."
            )
        for key, value in numeric_bonus.items():
            if not isinstance(value, int):
                raise ValueError(f"modules.json module[{index}]: numeric_bonus.{key} must be an integer.")
            if value > 2:
                raise ValueError(f"modules.json module[{index}]: numeric_bonus.{key} must not exceed 2.")


def _validate_module_primary_tag(slot_type: str, primary_tag: str, index: int) -> None:
    if slot_type == "weapon":
        allowed = (
            "combat:weapon_energy",
            "combat:weapon_kinetic",
            "combat:weapon_disruptive",
        )
        if primary_tag not in allowed:
            raise ValueError(f"modules.json module[{index}]: illegal primary_tag '{primary_tag}' for weapon slot_type.")
        return
    if slot_type == "defense":
        allowed = (
            "combat:defense_shielded",
            "combat:defense_armored",
            "combat:defense_adaptive",
        )
        if primary_tag not in allowed:
            raise ValueError(f"modules.json module[{index}]: illegal primary_tag '{primary_tag}' for defense slot_type.")
        return

    if primary_tag.startswith("combat:utility_") or primary_tag.startswith("ship:utility_"):
        return
    raise ValueError(f"modules.json module[{index}]: illegal primary_tag '{primary_tag}' for utility slot_type.")


def _require_type(container: dict[str, Any], index: int, key: str, expected_type: type, filename: str) -> None:
    value = container.get(key)
    if not isinstance(value, expected_type):
        type_name = expected_type.__name__
        raise ValueError(f"{filename} entry[{index}]: '{key}' must be {type_name}.")
