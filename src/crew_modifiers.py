from dataclasses import dataclass
from typing import Any, Iterable

from ship_entity import ShipEntity


@dataclass
class CrewModifiers:
    attack_band_bonus: int = 0
    defense_band_bonus: int = 0
    engine_band_bonus: int = 0

    focus_fire_bonus: int = 0
    reinforce_shields_bonus: int = 0
    evasive_bonus: int = 0
    repair_focus_bonus: int = 0

    repair_uses_bonus: int = 0
    repair_amount_bonus: int = 0

    fuel_delta: int = 0
    cargo_delta: int = 0
    data_cargo_delta: int = 0

    buy_multiplier: float = 1.0
    sell_multiplier: float = 1.0

    inspection_band_delta: int = 0

    mission_slot_bonus: int = 0

    daily_wage_total: int = 0


def compute_crew_modifiers(ship: ShipEntity) -> CrewModifiers:
    modifiers = CrewModifiers()
    crew_members = getattr(ship, "crew", []) or []
    if not crew_members:
        return modifiers

    alien_tag_count = 0
    for member in crew_members:
        role_id = getattr(member, "crew_role_id", None)
        crew_tags = [tag for tag in getattr(member, "crew_tags", []) if isinstance(tag, str) and tag.startswith("crew:")]
        _apply_role_effects(modifiers, role_id)
        alien_tag_count += sum(1 for tag in crew_tags if tag == "crew:alien")
        _apply_tag_effects(modifiers, crew_tags)
        modifiers.daily_wage_total += int(getattr(member, "daily_wage", 0))

    aligned_alien_elements = _count_aligned_alien_elements(ship)
    synergy_points = aligned_alien_elements * alien_tag_count
    if synergy_points > 0:
        _apply_alien_synergy(modifiers, synergy_points)

    modifiers.attack_band_bonus = _clamp_band(modifiers.attack_band_bonus)
    modifiers.defense_band_bonus = _clamp_band(modifiers.defense_band_bonus)
    modifiers.engine_band_bonus = _clamp_band(modifiers.engine_band_bonus)
    return modifiers


def _apply_role_effects(modifiers: CrewModifiers, role_id: Any) -> None:
    if role_id == "pilot":
        modifiers.engine_band_bonus += 1
    elif role_id == "gunner":
        modifiers.attack_band_bonus += 1
    elif role_id == "tactician":
        modifiers.defense_band_bonus += 1
    elif role_id == "engineer":
        modifiers.repair_uses_bonus += 1
    elif role_id == "mechanic":
        modifiers.repair_amount_bonus += 1
    elif role_id == "navigator":
        modifiers.fuel_delta -= 2
    elif role_id == "broker":
        modifiers.buy_multiplier *= 0.90
        modifiers.sell_multiplier *= 1.10
    elif role_id == "quartermaster":
        modifiers.cargo_delta += 3
    elif role_id == "science":
        modifiers.data_cargo_delta += 2


def _apply_tag_effects(modifiers: CrewModifiers, crew_tags: list[str]) -> None:
    for tag in crew_tags:
        if tag == "crew:steady_aim":
            modifiers.focus_fire_bonus += 1
        elif tag == "crew:trigger_happy":
            modifiers.focus_fire_bonus -= 1
        elif tag == "crew:evasive":
            modifiers.evasive_bonus += 1
        elif tag == "crew:slow_reactions":
            modifiers.evasive_bonus -= 1
        elif tag == "crew:damage_control":
            modifiers.repair_focus_bonus += 1
        elif tag == "crew:overconfident":
            modifiers.reinforce_shields_bonus -= 1
        elif tag == "crew:fuel_efficient":
            modifiers.fuel_delta -= 1
        elif tag == "crew:wasteful":
            modifiers.fuel_delta += 1
        elif tag == "crew:organized":
            modifiers.cargo_delta += 1
        elif tag == "crew:cluttered":
            modifiers.cargo_delta -= 1
        elif tag == "crew:haggler":
            modifiers.sell_multiplier *= 1.05
        elif tag == "crew:bargain_hunter":
            modifiers.buy_multiplier *= 0.95
        elif tag == "crew:awkward":
            modifiers.sell_multiplier *= 0.95
        elif tag == "crew:blacklisted":
            modifiers.buy_multiplier *= 1.05
        elif tag == "crew:undercover":
            modifiers.inspection_band_delta -= 1
        elif tag == "crew:wanted":
            modifiers.inspection_band_delta += 1
        elif tag == "crew:data_savvy":
            modifiers.data_cargo_delta += 2
        elif tag == "crew:connected":
            modifiers.mission_slot_bonus += 1


def _count_aligned_alien_elements(ship: ShipEntity) -> int:
    count = sum(1 for tag in _iter_str(getattr(ship, "tags", [])) if tag.endswith("_alien"))
    for module in _iter_modules(ship):
        primary_tag = module.get("primary_tag")
        if isinstance(primary_tag, str) and primary_tag.endswith("_alien"):
            count += 1
        secondary_tags = module.get("secondary_tags", [])
        count += sum(1 for tag in _iter_str(secondary_tags) if "_alien" in tag)
    return count


def _iter_modules(ship: ShipEntity) -> Iterable[dict[str, Any]]:
    # Supports both direct module lists and module payloads nested in persistent state.
    direct = getattr(ship, "modules", None)
    if isinstance(direct, list):
        for entry in direct:
            if isinstance(entry, dict):
                yield entry

    payload_modules = getattr(ship, "persistent_state", {}).get("modules", [])
    if isinstance(payload_modules, list):
        for entry in payload_modules:
            if isinstance(entry, dict):
                yield entry


def _iter_str(values: Any) -> Iterable[str]:
    if not isinstance(values, list):
        return []
    return [value for value in values if isinstance(value, str)]


def _apply_alien_synergy(modifiers: CrewModifiers, synergy_points: int) -> None:
    numeric_fields = (
        "attack_band_bonus",
        "defense_band_bonus",
        "engine_band_bonus",
        "focus_fire_bonus",
        "reinforce_shields_bonus",
        "evasive_bonus",
        "repair_focus_bonus",
        "repair_uses_bonus",
        "repair_amount_bonus",
        "fuel_delta",
        "cargo_delta",
        "data_cargo_delta",
        "inspection_band_delta",
        "mission_slot_bonus",
    )
    for field in numeric_fields:
        value = getattr(modifiers, field)
        if value > 0:
            setattr(modifiers, field, value + synergy_points)
        elif value < 0:
            setattr(modifiers, field, value - synergy_points)


def _clamp_band(value: int) -> int:
    if value > 3:
        return 3
    if value < -3:
        return -3
    return value
