from __future__ import annotations

from dataclasses import dataclass, field
import hashlib
import random
from typing import Any, Callable, Literal, Optional

try:
    from data_loader import load_hulls, load_modules
    from pursuit_resolver import resolve_pursuit
    from salvage_resolver import resolve_salvage_modules
    from ship_assembler import assemble_ship, compute_hull_max_from_ship_state
except ModuleNotFoundError:
    from src.data_loader import load_hulls, load_modules
    from src.pursuit_resolver import resolve_pursuit
    from src.salvage_resolver import resolve_salvage_modules
    from src.ship_assembler import assemble_ship, compute_hull_max_from_ship_state

ActionName = Literal[
    "Focus Fire",
    "Reinforce Shields",
    "Evasive Maneuvers",
    "Attempt Escape",
    "Surrender",
    "Scan",
    "Repair Systems",
]

OutcomeName = Literal["destroyed", "escape", "surrender", "max_rounds"]
SideName = Literal["player", "enemy"]

RPS_MATRIX = {
    ("energy", "armored"): 1,
    ("energy", "shielded"): -1,
    ("energy", "adaptive"): 0,
    ("kinetic", "shielded"): 1,
    ("kinetic", "adaptive"): -1,
    ("kinetic", "armored"): 0,
    ("disruptive", "adaptive"): 1,
    ("disruptive", "armored"): -1,
    ("disruptive", "shielded"): 0,
}


@dataclass
class ModuleDef:
    module_id: str
    slot_type: Literal["weapon", "defense", "utility"]
    tags: set[str] = field(default_factory=set)
    secondary: Optional[str | set[str]] = None


@dataclass
class CrewDef:
    crew_tags: list[str] = field(default_factory=list)


@dataclass
class ShipLoadout:
    name: str
    tier: int
    frame: str
    weapon_slots: int
    defense_slots: int
    utility_slots: int
    untyped_slots: int
    modules: list[ModuleDef]
    crew: list[str] = field(default_factory=list)
    seed_salt: str | int | None = None


@dataclass
class CombatState:
    hull_max: int
    hull_current: int
    degradation: dict[str, int]
    repair_uses_remaining: dict[str, int]
    scanned: bool = False
    ship_state: Optional[dict[str, Any]] = None
    subsystem_capacity: dict[str, int] = field(default_factory=lambda: {"weapon": 1, "defense": 1, "engine": 1})


@dataclass
class CombatResult:
    outcome: OutcomeName
    rounds: int
    winner: Optional[Literal["player", "enemy", "none"]]
    final_state_player: dict
    final_state_enemy: dict
    log: list[dict]
    tr_player: int
    tr_enemy: int
    rcp_player: int
    rcp_enemy: int
    destruction_event: Optional[dict] = None
    surrendered_by: Optional[SideName] = None
    salvage_modules: list[dict[str, Any]] = field(default_factory=list)


class CombatRng:
    def __init__(self, world_seed: str | int, salt: str):
        seed_text = f"{world_seed}|{salt}"
        digest = hashlib.sha256(seed_text.encode("ascii")).hexdigest()
        self._rng = random.Random(int(digest[:16], 16))
        self.seed_text = seed_text
        self.counter = 0

    def randint(self, low: int, high: int, label: str, round_number: int, event_log: list[dict]) -> int:
        self.counter += 1
        value = self._rng.randint(low, high)
        event_log.append(
            {
                "kind": "rng",
                "index": self.counter,
                "label": label,
                "range": [low, high],
                "value": value,
                "round": round_number,
            }
        )
        return value


def _hulls_by_id() -> dict[str, dict[str, Any]]:
    return {entry["hull_id"]: entry for entry in load_hulls()["hulls"]}


def _modules_by_id() -> dict[str, dict[str, Any]]:
    return {entry["module_id"]: entry for entry in load_modules()["modules"]}


def _normalize_secondary_list(raw: Any) -> list[str]:
    if raw is None:
        return []
    if isinstance(raw, str):
        return [raw]
    if isinstance(raw, set):
        return sorted(raw)
    if isinstance(raw, list):
        return [str(entry) for entry in raw]
    return []


def _secondary_set(module_instance: dict[str, Any]) -> set[str]:
    values = set()
    for entry in _normalize_secondary_list(module_instance.get("secondary_tags", [])):
        values.add(entry)
        if entry.startswith("secondary:"):
            values.add(entry.split("secondary:", 1)[1])
    return values


def _has_secondary(module_instance: dict[str, Any], tag: str) -> bool:
    s = _secondary_set(module_instance)
    return tag in s or f"secondary:{tag}" in s


def _ship_state_to_dict(ship_state: dict[str, Any], state: CombatState) -> dict[str, Any]:
    assembled = assemble_ship(
        hull_id=ship_state["hull_id"],
        module_instances=ship_state["module_instances"],
        degradation_state=state.degradation,
    )
    return {
        "hull_max": state.hull_max,
        "hull_current": state.hull_current,
        "hull_percent": hull_percent(state.hull_current, state.hull_max),
        "hull_band": hull_color_band(state.hull_current, state.hull_max),
        "degradation": dict(state.degradation),
        "subsystem_capacity": dict(assembled["degradation"]["capacity"]),
        "subsystem_red": dict(assembled["bands"]["red"]),
        "repair_uses_remaining": dict(state.repair_uses_remaining),
        "scanned": state.scanned,
    }


def _primary_weapon_type(ship_state: dict[str, Any]) -> Optional[str]:
    module_defs = _modules_by_id()
    counts = {"energy": 0, "kinetic": 0, "disruptive": 0}
    for instance in ship_state["module_instances"]:
        module = module_defs.get(instance["module_id"])
        if not module:
            continue
        tag = module["primary_tag"]
        if tag == "combat:weapon_energy":
            counts["energy"] += 1
        elif tag == "combat:weapon_kinetic":
            counts["kinetic"] += 1
        elif tag == "combat:weapon_disruptive":
            counts["disruptive"] += 1
    return _stable_max_key(counts)


def _primary_defense_type(ship_state: dict[str, Any]) -> Optional[str]:
    module_defs = _modules_by_id()
    counts = {"shielded": 0, "armored": 0, "adaptive": 0}
    for instance in ship_state["module_instances"]:
        module = module_defs.get(instance["module_id"])
        if not module:
            continue
        tag = module["primary_tag"]
        if tag == "combat:defense_shielded":
            counts["shielded"] += 1
        elif tag == "combat:defense_armored":
            counts["armored"] += 1
        elif tag == "combat:defense_adaptive":
            counts["adaptive"] += 1
    return _stable_max_key(counts)


def _stable_max_key(counts: dict[str, int]) -> Optional[str]:
    best_key = None
    best_value = -1
    for key in sorted(counts.keys()):
        value = counts[key]
        if value > best_value:
            best_key = key
            best_value = value
    if best_value <= 0:
        return None
    return best_key


def _focus_target(action: ActionName) -> Optional[str]:
    if action == "Focus Fire":
        return "weapon"
    if action == "Reinforce Shields":
        return "defense"
    if action in {"Evasive Maneuvers", "Attempt Escape"}:
        return "engine"
    return None


def hull_percent(hull_current: int, hull_max: int) -> int:
    if hull_max <= 0:
        return 0
    return (hull_current * 100) // hull_max


def hull_color_band(hull_current: int, hull_max: int) -> str:
    pct = hull_percent(hull_current, hull_max)
    if pct > 66:
        return "green"
    if pct > 33:
        return "yellow"
    return "red"


def _hull_band_index(hull_current: int, hull_max: int) -> int:
    pct = hull_percent(hull_current, hull_max)
    if pct > 66:
        return 2
    if pct > 33:
        return 1
    return 0


def map_rcp_to_tr(rcp: int) -> int:
    if rcp <= 6:
        return 1
    if rcp <= 13:
        return 2
    if rcp <= 20:
        return 3
    if rcp <= 26:
        return 4
    return 5


def _module_is_repair(module_instance: dict[str, Any]) -> bool:
    module = _modules_by_id().get(module_instance["module_id"])
    return bool(module and module["primary_tag"] == "combat:utility_repair_system")


def _legacy_loadout_to_ship_state(loadout: ShipLoadout) -> dict[str, Any]:
    hulls = [
        entry["hull_id"]
        for entry in load_hulls()["hulls"]
        if entry["tier"] == loadout.tier and entry["frame"] == loadout.frame
    ]
    if not hulls:
        raise ValueError(f"No hull available for tier/frame {loadout.tier}/{loadout.frame}.")
    hull_id = sorted(hulls)[0]

    tag_to_module = {
        "combat:weapon_energy": "weapon_energy_mk1",
        "combat:weapon_kinetic": "weapon_kinetic_mk1",
        "combat:weapon_disruptive": "weapon_disruptive_mk1",
        "combat:defense_shielded": "defense_shielded_mk1",
        "combat:defense_armored": "defense_armored_mk1",
        "combat:defense_adaptive": "defense_adaptive_mk1",
        "combat:utility_engine_boost": "combat_utility_engine_boost_mk1",
        "combat:utility_targeting": "combat_utility_targeting_mk1",
        "combat:utility_repair_system": "combat_utility_repair_system_mk1",
        "combat:utility_signal_scrambler": "combat_utility_signal_scrambler_mk1",
        "combat:utility_overcharger": "combat_utility_overcharger_mk1",
            "combat:utility_cloak": "ship_utility_probe_array",
        "ship:utility_extra_cargo": "ship_utility_extra_cargo",
        "ship:utility_data_array": "ship_utility_data_array",
        "ship:utility_smuggler_hold": "ship_utility_smuggler_hold",
        "ship:utility_mining_equipment": "ship_utility_mining_equipment",
        "ship:utility_probe_array": "ship_utility_probe_array",
        "ship:utility_interdiction": "ship_utility_interdiction",
    }

    module_instances = []
    for module in loadout.modules:
        mapped = None
        for tag in sorted(module.tags):
            mapped = tag_to_module.get(tag)
            if mapped:
                break
        if not mapped:
            raise ValueError(f"Unable to map legacy module '{module.module_id}' to catalog module_id.")
        module_instances.append(
            {
                "module_id": mapped,
                "secondary_tags": _normalize_secondary_list(module.secondary),
                "legacy_module_id": module.module_id,
            }
        )
    return {"hull_id": hull_id, "module_instances": module_instances, "degradation_state": {"weapon": 0, "defense": 0, "engine": 0}}


def compute_rcp_and_tr(loadout: ShipLoadout) -> tuple[int, int]:
    ship_state = _legacy_loadout_to_ship_state(loadout)
    assembled = assemble_ship(ship_state["hull_id"], ship_state["module_instances"], ship_state["degradation_state"])
    w = assembled["bands"]["pre_degradation"]["weapon"]
    d = assembled["bands"]["pre_degradation"]["defense"]
    e = assembled["bands"]["pre_degradation"]["engine"]
    h = int(assembled["hull_max"])
    repairs = sum(1 for instance in ship_state["module_instances"] if _module_is_repair(instance))
    rcp = w + d + (e // 2) + (h // 4) + (2 * repairs)
    return rcp, map_rcp_to_tr(rcp)


def create_initial_state(loadout: ShipLoadout) -> CombatState:
    ship_state = _legacy_loadout_to_ship_state(loadout)
    return _create_initial_state_from_ship_state(ship_state)


def _create_initial_state_from_ship_state(ship_state: dict[str, Any]) -> CombatState:
    assembled = assemble_ship(ship_state["hull_id"], ship_state["module_instances"], {"weapon": 0, "defense": 0, "engine": 0})
    hull_max = int(assembled["hull_max"])
    repair_uses = {}
    for index, module_instance in enumerate(ship_state["module_instances"]):
        if _module_is_repair(module_instance):
            repair_uses[str(index)] = 2
    return CombatState(
        hull_max=hull_max,
        hull_current=hull_max,
        degradation={"weapon": 0, "defense": 0, "engine": 0},
        repair_uses_remaining=repair_uses,
        scanned=False,
        ship_state={
            "hull_id": ship_state["hull_id"],
            "module_instances": list(ship_state["module_instances"]),
            "degradation_state": dict(ship_state.get("degradation_state", {"weapon": 0, "defense": 0, "engine": 0})),
        },
        subsystem_capacity=dict(assembled["degradation"]["capacity"]),
    )


def available_actions(ship_state: dict[str, Any], state: CombatState) -> list[ActionName]:
    actions: list[ActionName] = [
        "Focus Fire",
        "Reinforce Shields",
        "Evasive Maneuvers",
        "Attempt Escape",
        "Surrender",
    ]
    module_defs = _modules_by_id()
    has_probe = any(module_defs[entry["module_id"]]["primary_tag"] == "ship:utility_probe_array" for entry in ship_state["module_instances"])
    if has_probe:
        actions.append("Scan")
    if any(uses > 0 for uses in state.repair_uses_remaining.values()):
        actions.append("Repair Systems")
    return actions


def make_action_plan_selector(plan: list[ActionName]) -> Callable[..., ActionName]:
    def _selector(
        round_number: int,
        own_state: CombatState,
        enemy_state: CombatState,
        own_ship_state: dict[str, Any],
        enemy_ship_state: dict[str, Any],
        allowed_actions: list[ActionName],
    ) -> ActionName:
        if 1 <= round_number <= len(plan):
            action = plan[round_number - 1]
            if action in allowed_actions:
                return action
        return "Focus Fire"

    return _selector


def _default_selector(
    round_number: int,
    own_state: CombatState,
    enemy_state: CombatState,
    own_ship_state: dict[str, Any],
    enemy_ship_state: dict[str, Any],
    allowed_actions: list[ActionName],
) -> ActionName:
    if own_state.hull_current <= max(1, own_state.hull_max // 3) and "Repair Systems" in allowed_actions:
        return "Repair Systems"
    return "Focus Fire"


def _repair_once(ship_state: ShipLoadout | dict[str, Any], state: CombatState) -> Optional[dict]:
    if isinstance(ship_state, ShipLoadout):
        ship_state = _legacy_loadout_to_ship_state(ship_state)
    if not state.repair_uses_remaining:
        return None
    module_key = None
    for candidate in sorted(state.repair_uses_remaining.keys()):
        if state.repair_uses_remaining[candidate] > 0:
            module_key = candidate
            break
    if module_key is None:
        return None
    module_index = int(module_key)
    module_instance = ship_state["module_instances"][module_index]
    module_id = module_instance["module_id"]
    module_defs = _modules_by_id()
    module = module_defs.get(module_id)
    if module is None:
        return None

    instance = module_instance
    magnitude = 2
    if _has_secondary(instance, "efficient"):
        magnitude += 1
    hull_traits = _hulls_by_id()[ship_state["hull_id"]].get("traits", [])
    if _has_secondary(instance, "alien") and "ship:trait_alien" in hull_traits:
        magnitude += 1

    old_hull = state.hull_current
    state.hull_current = min(state.hull_max, state.hull_current + magnitude)
    state.repair_uses_remaining[module_key] -= 1
    return {
        "module_id": module_instance.get("legacy_module_id", module_id),
        "hull_before": old_hull,
        "hull_after": state.hull_current,
        "repair_amount": state.hull_current - old_hull,
        "repair_magnitude": magnitude,
        "remaining_uses": state.repair_uses_remaining[module_key],
    }


def _choose_degradation_subsystem(rng: CombatRng, round_number: int, rng_events: list[dict]) -> str:
    roll = rng.randint(0, 2, "degradation_subsystem", round_number, rng_events)
    if roll == 0:
        return "weapon"
    if roll == 1:
        return "defense"
    return "engine"


def _apply_damage_and_degradation(
    target_state: CombatState,
    damage: int,
    rng: CombatRng,
    round_number: int,
    rng_events: list[dict],
    target_ship_state: dict[str, Any] | None = None,
) -> list[dict]:
    if target_ship_state is None:
        if target_state.ship_state is None:
            raise ValueError("target_ship_state is required when state has no ship_state.")
        target_ship_state = target_state.ship_state
    events = []
    old_hull = target_state.hull_current
    old_band = _hull_band_index(target_state.hull_current, target_state.hull_max)
    target_state.hull_current = max(0, target_state.hull_current - damage)
    new_band = _hull_band_index(target_state.hull_current, target_state.hull_max)

    if new_band < old_band:
        for _ in range(old_band - new_band):
            subsystem = _choose_degradation_subsystem(rng, round_number, rng_events)
            target_state.degradation[subsystem] = target_state.degradation.get(subsystem, 0) + 1
            assembled = assemble_ship(
                hull_id=target_ship_state["hull_id"],
                module_instances=target_ship_state["module_instances"],
                degradation_state=target_state.degradation,
            )
            events.append(
                {
                    "subsystem": subsystem,
                    "degradation": target_state.degradation[subsystem],
                    "capacity": assembled["degradation"]["capacity"][subsystem],
                    "is_red": assembled["bands"]["red"][subsystem],
                }
            )

    if damage > 0:
        events.insert(0, {"hull_before": old_hull, "hull_after": target_state.hull_current, "damage": damage})
    return events


def _escape_attempt(
    world_seed: str | int,
    combat_id: str,
    round_number: int,
    fleeing_ship_state: dict[str, Any],
    pursuing_ship_state: dict[str, Any],
    fleeing_engine_effective: int,
    pursuing_engine_effective: int,
) -> dict:
    module_defs = _modules_by_id()
    fleeing_escape_mod = 0
    pursuing_mod = 0

    for entry in fleeing_ship_state["module_instances"]:
        if module_defs[entry["module_id"]]["primary_tag"] == "combat:utility_cloak":
            fleeing_escape_mod += 1
    for entry in pursuing_ship_state["module_instances"]:
        if module_defs[entry["module_id"]]["primary_tag"] == "ship:utility_interdiction":
            pursuing_mod += 1

    pursued_speed = max(0, fleeing_engine_effective + fleeing_escape_mod)
    pursuer_speed = max(0, pursuing_engine_effective + pursuing_mod)
    encounter_id = f"{combat_id}_escape_r{round_number}"
    pursuit = resolve_pursuit(
        encounter_id=encounter_id,
        world_seed=str(world_seed),
        pursuer_ship={"speed": pursuer_speed, "pilot_skill": 3},
        pursued_ship={"speed": pursued_speed, "pilot_skill": 3},
    )
    return {
        "encounter_id": encounter_id,
        "escaped": bool(pursuit.escaped),
        "roll": pursuit.roll,
        "threshold": pursuit.threshold,
        "pursuer_speed": pursuer_speed,
        "pursued_speed": pursued_speed,
        "fleeing_escape_mod": fleeing_escape_mod,
        "pursuing_mod": pursuing_mod,
        "pursuit_log": pursuit.log,
    }


def _resolve_attack(
    attacker_side: SideName,
    defender_side: SideName,
    attacker_weapon: int,
    defender_defense: int,
    defender_action: ActionName,
    rng: CombatRng,
    round_number: int,
    rng_events: list[dict],
) -> dict:
    band_delta = attacker_weapon - defender_defense
    if band_delta > 0:
        damage_roll = rng.randint(1, band_delta, f"damage_roll_{attacker_side}_to_{defender_side}", round_number, rng_events)
    elif band_delta == 0:
        damage_roll = rng.randint(0, 1, f"damage_roll_{attacker_side}_to_{defender_side}", round_number, rng_events)
    else:
        damage_roll = 0

    mitigation_roll = 0
    if defender_action == "Evasive Maneuvers":
        mitigation_roll = rng.randint(0, 1, f"mitigation_roll_{defender_side}_vs_{attacker_side}", round_number, rng_events)

    return {
        "band_delta": band_delta,
        "damage_roll": damage_roll,
        "mitigation_roll": mitigation_roll,
        "damage": max(0, damage_roll - mitigation_roll),
    }


def _effective_from_assembled(
    assembled: dict[str, Any],
    action: ActionName,
    subsystem: str,
    rps_bias: int = 0,
) -> int:
    value = assembled["bands"]["effective"][subsystem]
    if _focus_target(action) == subsystem:
        value += 1
    if subsystem == "weapon":
        value = max(0, value + rps_bias)
    return max(0, value)


def _to_ship_state(loadout: Optional[ShipLoadout], ship_state: Optional[dict[str, Any]], role: str) -> dict[str, Any]:
    if ship_state is not None:
        return {
            "hull_id": ship_state["hull_id"],
            "module_instances": list(ship_state["module_instances"]),
            "degradation_state": dict(ship_state.get("degradation_state", {"weapon": 0, "defense": 0, "engine": 0})),
        }
    if loadout is not None:
        return _legacy_loadout_to_ship_state(loadout)
    raise ValueError(f"Missing {role} ship input.")


def _effective_band(
    loadout: ShipLoadout,
    state: CombatState,
    subsystem: str,
    action: ActionName,
    opponent_loadout: ShipLoadout,
    for_attack: bool,
) -> tuple[int, int]:
    ship_state = _legacy_loadout_to_ship_state(loadout)
    opponent_state = _legacy_loadout_to_ship_state(opponent_loadout)
    assembled = assemble_ship(ship_state["hull_id"], ship_state["module_instances"], state.degradation)
    rps_bias = 0
    if for_attack and subsystem == "weapon":
        own_weapon = _primary_weapon_type(ship_state)
        opp_def = _primary_defense_type(opponent_state)
        if own_weapon is not None and opp_def is not None:
            rps_bias = RPS_MATRIX.get((own_weapon, opp_def), 0)
    return _effective_from_assembled(assembled, action, subsystem, rps_bias if subsystem == "weapon" else 0), rps_bias


def resolve_combat(
    world_seed: str | int,
    combat_id: str,
    player_loadout: ShipLoadout | None = None,
    enemy_loadout: ShipLoadout | None = None,
    player_ship_state: dict[str, Any] | None = None,
    enemy_ship_state: dict[str, Any] | None = None,
    player_action_selector: Optional[Callable[..., ActionName]] = None,
    enemy_action_selector: Optional[Callable[..., ActionName]] = None,
    max_rounds: int = 20,
    system_id: str = "",
) -> CombatResult:
    player_selector = player_action_selector or _default_selector
    enemy_selector = enemy_action_selector or _default_selector

    player_ship = _to_ship_state(player_loadout, player_ship_state, "player")
    enemy_ship = _to_ship_state(enemy_loadout, enemy_ship_state, "enemy")

    if player_loadout is not None:
        rcp_player, tr_player = compute_rcp_and_tr(player_loadout)
    else:
        assembled_player = assemble_ship(player_ship["hull_id"], player_ship["module_instances"], {"weapon": 0, "defense": 0, "engine": 0})
        rcp_player = (
            assembled_player["bands"]["pre_degradation"]["weapon"]
            + assembled_player["bands"]["pre_degradation"]["defense"]
            + (assembled_player["bands"]["pre_degradation"]["engine"] // 2)
            + (int(assembled_player["hull_max"]) // 4)
            + (2 * sum(1 for entry in player_ship["module_instances"] if _module_is_repair(entry)))
        )
        tr_player = map_rcp_to_tr(rcp_player)
    if enemy_loadout is not None:
        rcp_enemy, tr_enemy = compute_rcp_and_tr(enemy_loadout)
    else:
        assembled_enemy = assemble_ship(enemy_ship["hull_id"], enemy_ship["module_instances"], {"weapon": 0, "defense": 0, "engine": 0})
        rcp_enemy = (
            assembled_enemy["bands"]["pre_degradation"]["weapon"]
            + assembled_enemy["bands"]["pre_degradation"]["defense"]
            + (assembled_enemy["bands"]["pre_degradation"]["engine"] // 2)
            + (int(assembled_enemy["hull_max"]) // 4)
            + (2 * sum(1 for entry in enemy_ship["module_instances"] if _module_is_repair(entry)))
        )
        tr_enemy = map_rcp_to_tr(rcp_enemy)

    player_state = _create_initial_state_from_ship_state(player_ship)
    enemy_state = _create_initial_state_from_ship_state(enemy_ship)
    player_state.degradation.update(player_ship.get("degradation_state", {}))
    enemy_state.degradation.update(enemy_ship.get("degradation_state", {}))

    rng = CombatRng(world_seed=world_seed, salt=f"{combat_id}_combat")
    log: list[dict] = []

    for round_number in range(1, max_rounds + 1):
        round_log = {
            "round": round_number,
            "rng_seed": rng.seed_text,
            "actions": {},
            "bands": {},
            "rps": {},
            "attacks": {},
            "repair": {},
            "scan": {},
            "escape": {},
            "degradation_events": {"player": [], "enemy": []},
            "hull": {},
            "destruction": {},
            "rng_events": [],
        }

        player_allowed = available_actions(player_ship, player_state)
        enemy_allowed = available_actions(enemy_ship, enemy_state)
        player_action = player_selector(round_number, player_state, enemy_state, player_ship, enemy_ship, player_allowed)
        enemy_action = enemy_selector(round_number, enemy_state, player_state, enemy_ship, player_ship, enemy_allowed)
        if player_action not in player_allowed:
            player_action = "Focus Fire"
        if enemy_action not in enemy_allowed:
            enemy_action = "Focus Fire"
        round_log["actions"] = {"player": player_action, "enemy": enemy_action}

        if player_action == "Surrender":
            round_log["outcome"] = {"outcome": "surrender", "surrendered_by": "player"}
            log.append(round_log)
            return CombatResult(
                outcome="surrender",
                rounds=round_number,
                winner="enemy",
                final_state_player=_ship_state_to_dict(player_ship, player_state),
                final_state_enemy=_ship_state_to_dict(enemy_ship, enemy_state),
                log=log,
                tr_player=tr_player,
                tr_enemy=tr_enemy,
                rcp_player=rcp_player,
                rcp_enemy=rcp_enemy,
                surrendered_by="player",
                salvage_modules=[],
            )
        if enemy_action == "Surrender":
            round_log["outcome"] = {"outcome": "surrender", "surrendered_by": "enemy"}
            log.append(round_log)
            return CombatResult(
                outcome="surrender",
                rounds=round_number,
                winner="player",
                final_state_player=_ship_state_to_dict(player_ship, player_state),
                final_state_enemy=_ship_state_to_dict(enemy_ship, enemy_state),
                log=log,
                tr_player=tr_player,
                tr_enemy=tr_enemy,
                rcp_player=rcp_player,
                rcp_enemy=rcp_enemy,
                surrendered_by="enemy",
                salvage_modules=[],
            )

        if player_action == "Repair Systems":
            round_log["repair"]["player"] = _repair_once(player_ship, player_state)
        if enemy_action == "Repair Systems":
            round_log["repair"]["enemy"] = _repair_once(enemy_ship, enemy_state)

        module_defs = _modules_by_id()
        if player_action == "Scan" and any(module_defs[entry["module_id"]]["primary_tag"] == "ship:utility_probe_array" for entry in player_ship["module_instances"]):
            scan_roll = rng.randint(0, 1, "scan_roll_player", round_number, round_log["rng_events"])
            scan_success = scan_roll == 1
            if scan_success:
                enemy_state.scanned = True
            round_log["scan"]["player"] = {
                "temporary_placeholder": True,
                "roll": scan_roll,
                "success": scan_success,
                "enemy_scanned": enemy_state.scanned,
            }
        if enemy_action == "Scan" and any(module_defs[entry["module_id"]]["primary_tag"] == "ship:utility_probe_array" for entry in enemy_ship["module_instances"]):
            scan_roll = rng.randint(0, 1, "scan_roll_enemy", round_number, round_log["rng_events"])
            scan_success = scan_roll == 1
            if scan_success:
                player_state.scanned = True
            round_log["scan"]["enemy"] = {
                "temporary_placeholder": True,
                "roll": scan_roll,
                "success": scan_success,
                "enemy_scanned": player_state.scanned,
            }

        assembled_player = assemble_ship(player_ship["hull_id"], player_ship["module_instances"], player_state.degradation)
        assembled_enemy = assemble_ship(enemy_ship["hull_id"], enemy_ship["module_instances"], enemy_state.degradation)

        player_rps = 0
        enemy_rps = 0
        own_weapon = _primary_weapon_type(player_ship)
        opp_def = _primary_defense_type(enemy_ship)
        if own_weapon is not None and opp_def is not None:
            player_rps = RPS_MATRIX.get((own_weapon, opp_def), 0)
        own_weapon_e = _primary_weapon_type(enemy_ship)
        opp_def_p = _primary_defense_type(player_ship)
        if own_weapon_e is not None and opp_def_p is not None:
            enemy_rps = RPS_MATRIX.get((own_weapon_e, opp_def_p), 0)

        player_weapon = _effective_from_assembled(assembled_player, player_action, "weapon", player_rps)
        player_defense = _effective_from_assembled(assembled_player, player_action, "defense")
        player_engine = _effective_from_assembled(assembled_player, player_action, "engine")
        enemy_weapon = _effective_from_assembled(assembled_enemy, enemy_action, "weapon", enemy_rps)
        enemy_defense = _effective_from_assembled(assembled_enemy, enemy_action, "defense")
        enemy_engine = _effective_from_assembled(assembled_enemy, enemy_action, "engine")

        round_log["bands"] = {
            "player": {"weapon": player_weapon, "defense": player_defense, "engine": player_engine},
            "enemy": {"weapon": enemy_weapon, "defense": enemy_defense, "engine": enemy_engine},
        }
        round_log["rps"] = {"player_attack_vs_enemy": player_rps, "enemy_attack_vs_player": enemy_rps}

        if player_action == "Attempt Escape":
            escape = _escape_attempt(
                world_seed=world_seed,
                combat_id=combat_id,
                round_number=round_number,
                fleeing_ship_state=player_ship,
                pursuing_ship_state=enemy_ship,
                fleeing_engine_effective=player_engine,
                pursuing_engine_effective=enemy_engine,
            )
            round_log["escape"]["player"] = escape
            if escape["escaped"]:
                round_log["outcome"] = {"outcome": "escape", "escaped_by": "player"}
                log.append(round_log)
                return CombatResult(
                    outcome="escape",
                    rounds=round_number,
                    winner="player",
                    final_state_player=_ship_state_to_dict(player_ship, player_state),
                    final_state_enemy=_ship_state_to_dict(enemy_ship, enemy_state),
                    log=log,
                    tr_player=tr_player,
                    tr_enemy=tr_enemy,
                    rcp_player=rcp_player,
                    rcp_enemy=rcp_enemy,
                    salvage_modules=[],
                )
        if enemy_action == "Attempt Escape":
            escape = _escape_attempt(
                world_seed=world_seed,
                combat_id=f"{combat_id}_enemy",
                round_number=round_number,
                fleeing_ship_state=enemy_ship,
                pursuing_ship_state=player_ship,
                fleeing_engine_effective=enemy_engine,
                pursuing_engine_effective=player_engine,
            )
            round_log["escape"]["enemy"] = escape
            if escape["escaped"]:
                round_log["outcome"] = {"outcome": "escape", "escaped_by": "enemy"}
                log.append(round_log)
                return CombatResult(
                    outcome="escape",
                    rounds=round_number,
                    winner="enemy",
                    final_state_player=_ship_state_to_dict(player_ship, player_state),
                    final_state_enemy=_ship_state_to_dict(enemy_ship, enemy_state),
                    log=log,
                    tr_player=tr_player,
                    tr_enemy=tr_enemy,
                    rcp_player=rcp_player,
                    rcp_enemy=rcp_enemy,
                    salvage_modules=[],
                )

        player_attack = _resolve_attack(
            "player", "enemy", player_weapon, enemy_defense, enemy_action, rng, round_number, round_log["rng_events"]
        )
        enemy_attack = _resolve_attack(
            "enemy", "player", enemy_weapon, player_defense, player_action, rng, round_number, round_log["rng_events"]
        )
        round_log["attacks"] = {"player_to_enemy": player_attack, "enemy_to_player": enemy_attack}

        player_degrade = _apply_damage_and_degradation(
            player_state,
            enemy_attack["damage"],
            rng,
            round_number,
            round_log["rng_events"],
            target_ship_state=player_ship,
        )
        enemy_degrade = _apply_damage_and_degradation(
            enemy_state,
            player_attack["damage"],
            rng,
            round_number,
            round_log["rng_events"],
            target_ship_state=enemy_ship,
        )
        round_log["degradation_events"] = {"player": player_degrade, "enemy": enemy_degrade}

        round_log["hull"] = {
            "player": {"current": player_state.hull_current, "max": player_state.hull_max, "percent": hull_percent(player_state.hull_current, player_state.hull_max)},
            "enemy": {"current": enemy_state.hull_current, "max": enemy_state.hull_max, "percent": hull_percent(enemy_state.hull_current, enemy_state.hull_max)},
        }

        player_destroyed = player_state.hull_current <= 0
        enemy_destroyed = enemy_state.hull_current <= 0
        if player_destroyed or enemy_destroyed:
            if player_destroyed and enemy_destroyed:
                winner: Literal["player", "enemy", "none"] = "none"
            elif enemy_destroyed:
                winner = "player"
            else:
                winner = "enemy"
            destruction = {
                "player_destroyed": player_destroyed,
                "enemy_destroyed": enemy_destroyed,
                "requires_external_insurance_resolution": player_destroyed,
            }
            salvage_modules: list[dict[str, Any]] = []
            if enemy_destroyed:
                salvage_modules.extend(
                    resolve_salvage_modules(
                        world_seed=world_seed,
                        system_id=system_id,
                        encounter_id=f"{combat_id}_enemy_destroyed",
                        destroyed_ship=enemy_ship,
                    )
                )
            round_log["destruction"] = destruction
            round_log["salvage_modules"] = list(salvage_modules)
            round_log["outcome"] = {"outcome": "destroyed"}
            log.append(round_log)
            return CombatResult(
                outcome="destroyed",
                rounds=round_number,
                winner=winner,
                final_state_player=_ship_state_to_dict(player_ship, player_state),
                final_state_enemy=_ship_state_to_dict(enemy_ship, enemy_state),
                log=log,
                tr_player=tr_player,
                tr_enemy=tr_enemy,
                rcp_player=rcp_player,
                rcp_enemy=rcp_enemy,
                destruction_event=destruction,
                salvage_modules=salvage_modules,
            )
        log.append(round_log)

    return CombatResult(
        outcome="max_rounds",
        rounds=max_rounds,
        winner="none",
        final_state_player=_ship_state_to_dict(player_ship, player_state),
        final_state_enemy=_ship_state_to_dict(enemy_ship, enemy_state),
        log=log,
        tr_player=tr_player,
        tr_enemy=tr_enemy,
        rcp_player=rcp_player,
        rcp_enemy=rcp_enemy,
        salvage_modules=[],
    )
