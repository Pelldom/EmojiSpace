from __future__ import annotations

from dataclasses import dataclass, field
import hashlib
import random
from typing import Callable, Literal, Optional

try:
    from pursuit_resolver import resolve_pursuit
except ModuleNotFoundError:
    from src.pursuit_resolver import resolve_pursuit


# NOTE:
# Untyped slot resolution is assumed to have already occurred before building ShipLoadout.
# Modules arriving here must already use effective slot_type values: weapon/defense/utility.

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

TIER_BAND_BASELINE = {1: 1, 2: 1, 3: 2, 4: 2, 5: 3}
FRAME_BAND_BIAS = {
    "MIL": {"weapon": 1, "defense": 1, "engine": -1},
    "CIV": {"weapon": 0, "defense": 0, "engine": 0},
    "FRG": {"weapon": -1, "defense": 0, "engine": -1},
    "XA": {"weapon": 0, "defense": 0, "engine": 1},
    "XB": {"weapon": 2, "defense": 0, "engine": -1},
    "XC": {"weapon": 0, "defense": 2, "engine": -1},
    "ALN": {"weapon": 0, "defense": 0, "engine": 1},
}

TIER_HULL_BASELINE = {1: 8, 2: 10, 3: 12, 4: 15, 5: 18}
FRAME_HULL_BIAS = {"MIL": 2, "CIV": 0, "FRG": 3, "XA": 0, "XB": -2, "XC": 4, "ALN": 1}

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
    subsystem_capacity: dict[str, int]
    repair_uses_remaining: dict[str, int]
    scanned: bool = False

    def to_dict(self) -> dict:
        return {
            "hull_max": self.hull_max,
            "hull_current": self.hull_current,
            "hull_percent": hull_percent(self.hull_current, self.hull_max),
            "hull_band": hull_color_band(self.hull_current, self.hull_max),
            "degradation": dict(self.degradation),
            "subsystem_capacity": dict(self.subsystem_capacity),
            "subsystem_red": {
                subsystem: self.degradation.get(subsystem, 0) >= self.subsystem_capacity.get(subsystem, 1)
                for subsystem in ("weapon", "defense", "engine")
            },
            "repair_uses_remaining": dict(self.repair_uses_remaining),
            "scanned": self.scanned,
        }


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


def _normalized_secondary_set(module: ModuleDef) -> set[str]:
    if module.secondary is None:
        return set()
    if isinstance(module.secondary, str):
        values = {module.secondary}
    else:
        values = set(module.secondary)
    normalized = set()
    for entry in values:
        normalized.add(entry)
        if entry.startswith("secondary:"):
            normalized.add(entry.split("secondary:", 1)[1])
    return normalized


def _has_secondary(module: ModuleDef, secondary_name: str) -> bool:
    entries = _normalized_secondary_set(module)
    return secondary_name in entries or f"secondary:{secondary_name}" in entries


def _module_has_tag(module: ModuleDef, tag_name: str) -> bool:
    if tag_name in module.tags:
        return True
    if ":" in tag_name:
        _, suffix = tag_name.split(":", 1)
        if suffix in module.tags:
            return True
    return False


def _count_crew(crew: list[str], tag_name: str) -> int:
    return sum(1 for tag in crew if tag == tag_name)


def compute_hull_max(loadout: ShipLoadout) -> int:
    hull = TIER_HULL_BASELINE[loadout.tier] + FRAME_HULL_BIAS[loadout.frame]
    is_experimental = loadout.frame in {"XA", "XB", "XC"}
    for module in loadout.modules:
        if _has_secondary(module, "alien") and loadout.frame == "ALN":
            hull += 1
        if _has_secondary(module, "prototype") and is_experimental:
            hull += 1
        if _module_has_tag(module, "combat:defense_armored") or _module_has_tag(module, "defense_armored"):
            hull += 1
        if _has_secondary(module, "unstable"):
            hull -= 1
    return max(4, hull)


def compute_subsystem_capacity(loadout: ShipLoadout) -> dict[str, int]:
    is_experimental = loadout.frame in {"XA", "XB", "XC"}
    weapon_modules = [module for module in loadout.modules if module.slot_type == "weapon"]
    defense_modules = [module for module in loadout.modules if module.slot_type == "defense"]
    utility_modules = [module for module in loadout.modules if module.slot_type == "utility"]

    capacities = {
        "weapon": max(1, len(weapon_modules)),
        "defense": max(1, len(defense_modules)),
        "engine": max(1, len(utility_modules)),
    }

    for subsystem, modules in (
        ("weapon", weapon_modules),
        ("defense", defense_modules),
        ("engine", utility_modules),
    ):
        modifier = 0
        for module in modules:
            if _has_secondary(module, "enhanced"):
                modifier += 1
            if _has_secondary(module, "unstable"):
                modifier -= 1
            if _has_secondary(module, "prototype") and not is_experimental:
                modifier -= 1
        capacities[subsystem] = max(1, capacities[subsystem] + modifier)

    return capacities


def _module_effect_bonus(module: ModuleDef, loadout: ShipLoadout, base_bonus: int) -> int:
    if base_bonus <= 0:
        return 0
    bonus = base_bonus
    if _has_secondary(module, "efficient"):
        bonus += 1
    if _has_secondary(module, "alien") and loadout.frame == "ALN":
        bonus += 1
    return bonus


def _utility_action_bonus(loadout: ShipLoadout, subsystem: str, action: ActionName) -> int:
    total = 0
    for module in loadout.modules:
        if module.slot_type != "utility":
            continue
        if action == "Focus Fire" and _module_has_tag(module, "combat:utility_targeting"):
            total += _module_effect_bonus(module, loadout, 1)
        elif action == "Reinforce Shields" and _module_has_tag(module, "combat:utility_signal_scrambler"):
            total += _module_effect_bonus(module, loadout, 1)
        elif action == "Evasive Maneuvers" and subsystem == "engine":
            if _module_has_tag(module, "combat:utility_engine_boost") or _module_has_tag(module, "combat:utility_overcharger"):
                total += _module_effect_bonus(module, loadout, 1)
    return total


def _focus_target(action: ActionName) -> Optional[str]:
    if action == "Focus Fire":
        return "weapon"
    if action == "Reinforce Shields":
        return "defense"
    if action in {"Evasive Maneuvers", "Attempt Escape"}:
        return "engine"
    return None


def _band_base_potential(loadout: ShipLoadout, subsystem: str) -> int:
    base = max(0, TIER_BAND_BASELINE[loadout.tier] + FRAME_BAND_BIAS[loadout.frame][subsystem])
    if subsystem == "weapon":
        base += sum(1 for module in loadout.modules if module.slot_type == "weapon")
        base += _count_crew(loadout.crew, "crew:gunner")
    elif subsystem == "defense":
        base += sum(1 for module in loadout.modules if module.slot_type == "defense")
        base += _count_crew(loadout.crew, "crew:engineer")
    else:
        base += _count_crew(loadout.crew, "crew:pilot")
    return max(0, base)


def _effective_band(
    loadout: ShipLoadout,
    state: CombatState,
    subsystem: str,
    action: ActionName,
    opponent_loadout: ShipLoadout,
    for_attack: bool,
) -> tuple[int, int]:
    if state.degradation.get(subsystem, 0) >= state.subsystem_capacity.get(subsystem, 1):
        return 0, 0

    value = _band_base_potential(loadout, subsystem)
    value += _utility_action_bonus(loadout, subsystem, action)
    value -= state.degradation.get(subsystem, 0)
    focus_target = _focus_target(action)
    if focus_target == subsystem:
        value += 1
    value = max(0, value)

    rps_bias = 0
    if for_attack and subsystem == "weapon":
        own_weapon = _primary_weapon_type(loadout)
        opponent_defense = _primary_defense_type(opponent_loadout)
        if own_weapon is not None and opponent_defense is not None:
            rps_bias = RPS_MATRIX.get((own_weapon, opponent_defense), 0)
            value = max(0, value + rps_bias)
    return value, rps_bias


def _primary_weapon_type(loadout: ShipLoadout) -> Optional[str]:
    counts = {"energy": 0, "kinetic": 0, "disruptive": 0}
    for module in loadout.modules:
        if module.slot_type != "weapon":
            continue
        if _module_has_tag(module, "combat:weapon_energy"):
            counts["energy"] += 1
        elif _module_has_tag(module, "combat:weapon_kinetic"):
            counts["kinetic"] += 1
        elif _module_has_tag(module, "combat:weapon_disruptive"):
            counts["disruptive"] += 1
    return _stable_max_key(counts)


def _primary_defense_type(loadout: ShipLoadout) -> Optional[str]:
    counts = {"shielded": 0, "armored": 0, "adaptive": 0}
    for module in loadout.modules:
        if module.slot_type != "defense":
            continue
        if _module_has_tag(module, "combat:defense_shielded"):
            counts["shielded"] += 1
        elif _module_has_tag(module, "combat:defense_armored"):
            counts["armored"] += 1
        elif _module_has_tag(module, "combat:defense_adaptive"):
            counts["adaptive"] += 1
    return _stable_max_key(counts)


def _stable_max_key(counts: dict[str, int]) -> Optional[str]:
    if not counts:
        return None
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


def compute_rcp_and_tr(loadout: ShipLoadout) -> tuple[int, int]:
    weapon = _band_base_potential(loadout, "weapon")
    defense = _band_base_potential(loadout, "defense")
    engine = _band_base_potential(loadout, "engine")
    hull = compute_hull_max(loadout)
    repairs = sum(1 for module in loadout.modules if _module_has_tag(module, "combat:utility_repair_system"))
    rcp = weapon + defense + (engine // 2) + (hull // 4) + (2 * repairs)
    tr = map_rcp_to_tr(rcp)
    return rcp, tr


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


def create_initial_state(loadout: ShipLoadout) -> CombatState:
    hull_max = compute_hull_max(loadout)
    repair_uses = {}
    for module in loadout.modules:
        if _module_has_tag(module, "combat:utility_repair_system"):
            repair_uses[module.module_id] = 2
    return CombatState(
        hull_max=hull_max,
        hull_current=hull_max,
        degradation={"weapon": 0, "defense": 0, "engine": 0},
        subsystem_capacity=compute_subsystem_capacity(loadout),
        repair_uses_remaining=repair_uses,
        scanned=False,
    )


def available_actions(loadout: ShipLoadout, state: CombatState) -> list[ActionName]:
    actions: list[ActionName] = [
        "Focus Fire",
        "Reinforce Shields",
        "Evasive Maneuvers",
        "Attempt Escape",
        "Surrender",
    ]
    if any(_module_has_tag(module, "ship:utility_probe_array") for module in loadout.modules):
        actions.append("Scan")
    if any(uses > 0 for uses in state.repair_uses_remaining.values()):
        actions.append("Repair Systems")
    return actions


def make_action_plan_selector(plan: list[ActionName]) -> Callable[..., ActionName]:
    def _selector(
        round_number: int,
        own_state: CombatState,
        enemy_state: CombatState,
        own_loadout: ShipLoadout,
        enemy_loadout: ShipLoadout,
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
    own_loadout: ShipLoadout,
    enemy_loadout: ShipLoadout,
    allowed_actions: list[ActionName],
) -> ActionName:
    if own_state.hull_current <= max(1, own_state.hull_max // 3) and "Repair Systems" in allowed_actions:
        return "Repair Systems"
    return "Focus Fire"


def _repair_once(loadout: ShipLoadout, state: CombatState) -> Optional[dict]:
    if not state.repair_uses_remaining:
        return None
    module_id = None
    for candidate in sorted(state.repair_uses_remaining.keys()):
        if state.repair_uses_remaining[candidate] > 0:
            module_id = candidate
            break
    if module_id is None:
        return None

    module = next((entry for entry in loadout.modules if entry.module_id == module_id), None)
    if module is None:
        return None

    magnitude = 2
    efficient = _has_secondary(module, "efficient")
    alien = _has_secondary(module, "alien") and loadout.frame == "ALN"
    if efficient and alien:
        magnitude = 4
    elif efficient:
        magnitude = 3
    magnitude += _count_crew(loadout.crew, "crew:mechanic")

    old_hull = state.hull_current
    state.hull_current = min(state.hull_max, state.hull_current + magnitude)
    state.repair_uses_remaining[module_id] -= 1
    return {
        "module_id": module_id,
        "hull_before": old_hull,
        "hull_after": state.hull_current,
        "repair_amount": state.hull_current - old_hull,
        "repair_magnitude": magnitude,
        "remaining_uses": state.repair_uses_remaining[module_id],
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
) -> list[dict]:
    events = []
    old_hull = target_state.hull_current
    old_band = _hull_band_index(target_state.hull_current, target_state.hull_max)
    target_state.hull_current = max(0, target_state.hull_current - damage)
    new_band = _hull_band_index(target_state.hull_current, target_state.hull_max)

    if new_band < old_band:
        for _ in range(old_band - new_band):
            subsystem = _choose_degradation_subsystem(rng, round_number, rng_events)
            target_state.degradation[subsystem] = target_state.degradation.get(subsystem, 0) + 1
            events.append(
                {
                    "subsystem": subsystem,
                    "degradation": target_state.degradation[subsystem],
                    "capacity": target_state.subsystem_capacity.get(subsystem, 1),
                    "is_red": target_state.degradation[subsystem] >= target_state.subsystem_capacity.get(subsystem, 1),
                }
            )

    if damage > 0:
        events.insert(
            0,
            {
                "hull_before": old_hull,
                "hull_after": target_state.hull_current,
                "damage": damage,
            },
        )
    return events


def _escape_attempt(
    world_seed: str | int,
    combat_id: str,
    round_number: int,
    fleeing_loadout: ShipLoadout,
    pursuing_loadout: ShipLoadout,
    fleeing_engine_effective: int,
    pursuing_engine_effective: int,
) -> dict:
    fleeing_escape_mod = 0
    pursuing_mod = 0

    if any(_module_has_tag(module, "combat:utility_cloak") for module in fleeing_loadout.modules):
        fleeing_escape_mod += 1
    fleeing_escape_mod += _count_crew(fleeing_loadout.crew, "crew:pilot")

    if any(_module_has_tag(module, "ship:utility_interdiction") for module in pursuing_loadout.modules):
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
        mitigation_roll = rng.randint(
            0, 1, f"mitigation_roll_{defender_side}_vs_{attacker_side}", round_number, rng_events
        )

    damage = max(0, damage_roll - mitigation_roll)
    return {
        "band_delta": band_delta,
        "damage_roll": damage_roll,
        "mitigation_roll": mitigation_roll,
        "damage": damage,
    }


def resolve_combat(
    world_seed: str | int,
    combat_id: str,
    player_loadout: ShipLoadout,
    enemy_loadout: ShipLoadout,
    player_action_selector: Optional[Callable[..., ActionName]] = None,
    enemy_action_selector: Optional[Callable[..., ActionName]] = None,
    max_rounds: int = 20,
) -> CombatResult:
    player_selector = player_action_selector or _default_selector
    enemy_selector = enemy_action_selector or _default_selector

    rcp_player, tr_player = compute_rcp_and_tr(player_loadout)
    rcp_enemy, tr_enemy = compute_rcp_and_tr(enemy_loadout)

    player_state = create_initial_state(player_loadout)
    enemy_state = create_initial_state(enemy_loadout)
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

        player_allowed = available_actions(player_loadout, player_state)
        enemy_allowed = available_actions(enemy_loadout, enemy_state)
        player_action = player_selector(
            round_number, player_state, enemy_state, player_loadout, enemy_loadout, player_allowed
        )
        enemy_action = enemy_selector(
            round_number, enemy_state, player_state, enemy_loadout, player_loadout, enemy_allowed
        )
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
                final_state_player=player_state.to_dict(),
                final_state_enemy=enemy_state.to_dict(),
                log=log,
                tr_player=tr_player,
                tr_enemy=tr_enemy,
                rcp_player=rcp_player,
                rcp_enemy=rcp_enemy,
                surrendered_by="player",
            )
        if enemy_action == "Surrender":
            round_log["outcome"] = {"outcome": "surrender", "surrendered_by": "enemy"}
            log.append(round_log)
            return CombatResult(
                outcome="surrender",
                rounds=round_number,
                winner="player",
                final_state_player=player_state.to_dict(),
                final_state_enemy=enemy_state.to_dict(),
                log=log,
                tr_player=tr_player,
                tr_enemy=tr_enemy,
                rcp_player=rcp_player,
                rcp_enemy=rcp_enemy,
                surrendered_by="enemy",
            )

        if player_action == "Repair Systems":
            round_log["repair"]["player"] = _repair_once(player_loadout, player_state)
        if enemy_action == "Repair Systems":
            round_log["repair"]["enemy"] = _repair_once(enemy_loadout, enemy_state)

        if player_action == "Scan" and any(
            _module_has_tag(module, "ship:utility_probe_array") for module in player_loadout.modules
        ):
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
        if enemy_action == "Scan" and any(
            _module_has_tag(module, "ship:utility_probe_array") for module in enemy_loadout.modules
        ):
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

        player_weapon, player_rps = _effective_band(
            player_loadout, player_state, "weapon", player_action, enemy_loadout, True
        )
        player_defense, _ = _effective_band(player_loadout, player_state, "defense", player_action, enemy_loadout, False)
        player_engine, _ = _effective_band(player_loadout, player_state, "engine", player_action, enemy_loadout, False)
        enemy_weapon, enemy_rps = _effective_band(enemy_loadout, enemy_state, "weapon", enemy_action, player_loadout, True)
        enemy_defense, _ = _effective_band(enemy_loadout, enemy_state, "defense", enemy_action, player_loadout, False)
        enemy_engine, _ = _effective_band(enemy_loadout, enemy_state, "engine", enemy_action, player_loadout, False)

        round_log["bands"] = {
            "player": {"weapon": player_weapon, "defense": player_defense, "engine": player_engine},
            "enemy": {"weapon": enemy_weapon, "defense": enemy_defense, "engine": enemy_engine},
        }
        round_log["rps"] = {
            "player_attack_vs_enemy": player_rps,
            "enemy_attack_vs_player": enemy_rps,
        }

        if player_action == "Attempt Escape":
            escape = _escape_attempt(
                world_seed=world_seed,
                combat_id=combat_id,
                round_number=round_number,
                fleeing_loadout=player_loadout,
                pursuing_loadout=enemy_loadout,
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
                    final_state_player=player_state.to_dict(),
                    final_state_enemy=enemy_state.to_dict(),
                    log=log,
                    tr_player=tr_player,
                    tr_enemy=tr_enemy,
                    rcp_player=rcp_player,
                    rcp_enemy=rcp_enemy,
                )
        if enemy_action == "Attempt Escape":
            escape = _escape_attempt(
                world_seed=world_seed,
                combat_id=f"{combat_id}_enemy",
                round_number=round_number,
                fleeing_loadout=enemy_loadout,
                pursuing_loadout=player_loadout,
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
                    final_state_player=player_state.to_dict(),
                    final_state_enemy=enemy_state.to_dict(),
                    log=log,
                    tr_player=tr_player,
                    tr_enemy=tr_enemy,
                    rcp_player=rcp_player,
                    rcp_enemy=rcp_enemy,
                )

        player_attack = _resolve_attack(
            "player",
            "enemy",
            player_weapon,
            enemy_defense,
            enemy_action,
            rng,
            round_number,
            round_log["rng_events"],
        )
        enemy_attack = _resolve_attack(
            "enemy",
            "player",
            enemy_weapon,
            player_defense,
            player_action,
            rng,
            round_number,
            round_log["rng_events"],
        )
        round_log["attacks"] = {
            "player_to_enemy": player_attack,
            "enemy_to_player": enemy_attack,
        }

        player_degrade = _apply_damage_and_degradation(
            player_state, enemy_attack["damage"], rng, round_number, round_log["rng_events"]
        )
        enemy_degrade = _apply_damage_and_degradation(
            enemy_state, player_attack["damage"], rng, round_number, round_log["rng_events"]
        )
        round_log["degradation_events"] = {"player": player_degrade, "enemy": enemy_degrade}

        round_log["hull"] = {
            "player": {
                "current": player_state.hull_current,
                "max": player_state.hull_max,
                "percent": hull_percent(player_state.hull_current, player_state.hull_max),
            },
            "enemy": {
                "current": enemy_state.hull_current,
                "max": enemy_state.hull_max,
                "percent": hull_percent(enemy_state.hull_current, enemy_state.hull_max),
            },
        }

        player_destroyed = player_state.hull_current <= 0
        enemy_destroyed = enemy_state.hull_current <= 0
        if player_destroyed or enemy_destroyed:
            winner: Literal["player", "enemy", "none"]
            if player_destroyed and enemy_destroyed:
                winner = "none"
            elif enemy_destroyed:
                winner = "player"
            else:
                winner = "enemy"
            destruction = {
                "player_destroyed": player_destroyed,
                "enemy_destroyed": enemy_destroyed,
                "requires_external_insurance_resolution": player_destroyed,
            }
            round_log["destruction"] = destruction
            round_log["outcome"] = {"outcome": "destroyed"}
            log.append(round_log)
            return CombatResult(
                outcome="destroyed",
                rounds=round_number,
                winner=winner,
                final_state_player=player_state.to_dict(),
                final_state_enemy=enemy_state.to_dict(),
                log=log,
                tr_player=tr_player,
                tr_enemy=tr_enemy,
                rcp_player=rcp_player,
                rcp_enemy=rcp_enemy,
                destruction_event=destruction,
            )

        log.append(round_log)

    return CombatResult(
        outcome="max_rounds",
        rounds=max_rounds,
        winner="none",
        final_state_player=player_state.to_dict(),
        final_state_enemy=enemy_state.to_dict(),
        log=log,
        tr_player=tr_player,
        tr_enemy=tr_enemy,
        rcp_player=rcp_player,
        rcp_enemy=rcp_enemy,
    )
