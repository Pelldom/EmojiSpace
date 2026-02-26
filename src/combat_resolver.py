from __future__ import annotations

from dataclasses import dataclass, field
import hashlib
import random
import secrets
from typing import Any, Callable, Literal, Optional

try:
    from crew_modifiers import CrewModifiers, compute_crew_modifiers
    from data_loader import load_hulls, load_modules
    from pursuit_resolver import resolve_pursuit
    from salvage_resolver import resolve_salvage_modules
    from ship_assembler import assemble_ship, compute_hull_max_from_ship_state
except ModuleNotFoundError:
    from src.crew_modifiers import CrewModifiers, compute_crew_modifiers
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
    repair_amount_bonus: int = 0


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
    combat_rng_seed: int = 0


class CombatRng:
    def __init__(self, combat_rng_seed: int):
        self._rng = random.Random(combat_rng_seed)
        self.combat_rng_seed = combat_rng_seed
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


def _crew_modifiers_for_ship_state(ship_state: dict[str, Any]) -> CrewModifiers:
    module_defs = _modules_by_id()
    normalized_modules = []
    for module_instance in ship_state.get("module_instances", []):
        if not isinstance(module_instance, dict):
            continue
        module_def = module_defs.get(module_instance.get("module_id"))
        primary_tag = module_def.get("primary_tag") if module_def else ""
        normalized_modules.append(
            {
                "primary_tag": primary_tag,
                "secondary_tags": list(module_instance.get("secondary_tags", [])),
            }
        )

    tags = ship_state.get("tags", [])
    class _ProxyShip:
        def __init__(self) -> None:
            self.crew = list(ship_state.get("crew", [])) if isinstance(ship_state.get("crew", []), list) else []
            self.tags = list(tags) if isinstance(tags, list) else []
            self.modules = normalized_modules
            self.persistent_state = {}

    proxy_ship = _ProxyShip()
    return compute_crew_modifiers(proxy_ship)


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




def compute_rcp_and_tr_from_ship_state(ship_state: dict[str, Any]) -> tuple[int, int]:
    assembled = assemble_ship(ship_state["hull_id"], ship_state["module_instances"], ship_state.get("degradation_state", {"weapon": 0, "defense": 0, "engine": 0}))
    w = assembled["bands"]["pre_degradation"]["weapon"]
    d = assembled["bands"]["pre_degradation"]["defense"]
    e = assembled["bands"]["pre_degradation"]["engine"]
    h = int(assembled["hull_max"])
    repairs = sum(1 for instance in ship_state["module_instances"] if _module_is_repair(instance))
    rcp = w + d + (e // 2) + (h // 4) + (2 * repairs)
    return rcp, map_rcp_to_tr(rcp)




def resolve_combat_round(
    combat_rng_seed: int,
    round_number: int,
    player_state: CombatState,
    enemy_state: CombatState,
    player_action: ActionName,
    enemy_action: ActionName,
    player_ship_state: dict[str, Any],
    enemy_ship_state: dict[str, Any],
    system_id: str = "",
) -> dict[str, Any]:
    """
    Execute exactly ONE combat round.
    
    This function mutates player_state and enemy_state in place.
    It does NOT reinitialize CombatState or reset hull_current.
    
    Args:
        combat_rng_seed: Base RNG seed for this combat
        round_number: Current round number (1-indexed)
        player_state: Current player CombatState (mutated in place)
        enemy_state: Current enemy CombatState (mutated in place)
        player_action: Player's action for this round
        enemy_action: Enemy's action for this round
        player_ship_state: Player ship state dict (for module info)
        enemy_ship_state: Enemy ship state dict (for module info)
        system_id: System ID (optional, for logging)
    
    Returns:
        dict with:
        - "player_state": CombatState (same object, mutated)
        - "enemy_state": CombatState (same object, mutated)
        - "combat_ended": bool
        - "outcome": str | None ("destroyed", "escape", "surrender", "max_rounds", or None)
        - "round_summary": dict with round details
    """
    # Create RNG for this round: use combat_rng_seed + round_number for reproducibility
    rng_seed = combat_rng_seed + round_number
    rng = CombatRng(combat_rng_seed=rng_seed)
    rng_events: list[dict] = []
    
    # Check surrender (immediate termination)
    if player_action == "Surrender":
        return {
            "player_state": player_state,
            "enemy_state": enemy_state,
            "combat_ended": True,
            "outcome": "surrender",
            "round_summary": {
                "round": round_number,
                "player_action": player_action,
                "enemy_action": enemy_action,
                "player_hull_current": player_state.hull_current,
                "enemy_hull_current": enemy_state.hull_current,
                "surrendered_by": "player",
            },
        }
    
    if enemy_action == "Surrender":
        return {
            "player_state": player_state,
            "enemy_state": enemy_state,
            "combat_ended": True,
            "outcome": "surrender",
            "round_summary": {
                "round": round_number,
                "player_action": player_action,
                "enemy_action": enemy_action,
                "player_hull_current": player_state.hull_current,
                "enemy_hull_current": enemy_state.hull_current,
                "surrendered_by": "enemy",
            },
        }
    
    # Handle repair actions
    player_crew_mods = _crew_modifiers_for_ship_state(player_ship_state)
    enemy_crew_mods = _crew_modifiers_for_ship_state(enemy_ship_state)
    
    if player_action == "Repair Systems":
        _repair_once(player_ship_state, player_state, action_repair_bonus=int(player_crew_mods.repair_focus_bonus))
    if enemy_action == "Repair Systems":
        _repair_once(enemy_ship_state, enemy_state, action_repair_bonus=int(enemy_crew_mods.repair_focus_bonus))
    
    # Handle scan actions
    module_defs = _modules_by_id()
    if player_action == "Scan" and any(module_defs[entry["module_id"]]["primary_tag"] == "ship:utility_probe_array" for entry in player_ship_state["module_instances"]):
        scan_roll = rng.randint(0, 1, "scan_roll_player", round_number, rng_events)
        if scan_roll == 1:
            enemy_state.scanned = True
    
    if enemy_action == "Scan" and any(module_defs[entry["module_id"]]["primary_tag"] == "ship:utility_probe_array" for entry in enemy_ship_state["module_instances"]):
        scan_roll = rng.randint(0, 1, "scan_roll_enemy", round_number, rng_events)
        if scan_roll == 1:
            player_state.scanned = True
    
    # Assemble ships with current degradation (for effective bands calculation)
    assembled_player = assemble_ship(player_ship_state["hull_id"], player_ship_state["module_instances"], player_state.degradation)
    assembled_enemy = assemble_ship(enemy_ship_state["hull_id"], enemy_ship_state["module_instances"], enemy_state.degradation)
    
    # Calculate RPS adjustments
    player_rps = 0
    enemy_rps = 0
    own_weapon = _primary_weapon_type(player_ship_state)
    opp_def = _primary_defense_type(enemy_ship_state)
    if own_weapon is not None and opp_def is not None:
        player_rps = RPS_MATRIX.get((own_weapon, opp_def), 0)
    own_weapon_e = _primary_weapon_type(enemy_ship_state)
    opp_def_p = _primary_defense_type(player_ship_state)
    if own_weapon_e is not None and opp_def_p is not None:
        enemy_rps = RPS_MATRIX.get((own_weapon_e, opp_def_p), 0)
    
    # Calculate effective bands
    player_weapon = _effective_from_assembled(
        assembled_player,
        player_action,
        "weapon",
        player_rps,
        crew_band_bonus=int(player_crew_mods.attack_band_bonus),
        action_bonus=int(player_crew_mods.focus_fire_bonus if player_action == "Focus Fire" else 0),
    )
    player_defense = _effective_from_assembled(
        assembled_player,
        player_action,
        "defense",
        crew_band_bonus=int(player_crew_mods.defense_band_bonus),
        action_bonus=int(player_crew_mods.reinforce_shields_bonus if player_action == "Reinforce Shields" else 0),
    )
    player_engine = _effective_from_assembled(
        assembled_player,
        player_action,
        "engine",
        crew_band_bonus=int(player_crew_mods.engine_band_bonus),
        action_bonus=int(player_crew_mods.evasive_bonus if player_action == "Evasive Maneuvers" else 0),
    )
    enemy_weapon = _effective_from_assembled(
        assembled_enemy,
        enemy_action,
        "weapon",
        enemy_rps,
        crew_band_bonus=int(enemy_crew_mods.attack_band_bonus),
        action_bonus=int(enemy_crew_mods.focus_fire_bonus if enemy_action == "Focus Fire" else 0),
    )
    enemy_defense = _effective_from_assembled(
        assembled_enemy,
        enemy_action,
        "defense",
        crew_band_bonus=int(enemy_crew_mods.defense_band_bonus),
        action_bonus=int(enemy_crew_mods.reinforce_shields_bonus if enemy_action == "Reinforce Shields" else 0),
    )
    enemy_engine = _effective_from_assembled(
        assembled_enemy,
        enemy_action,
        "engine",
        crew_band_bonus=int(enemy_crew_mods.engine_band_bonus),
        action_bonus=int(enemy_crew_mods.evasive_bonus if enemy_action == "Evasive Maneuvers" else 0),
    )
    
    # Handle escape attempts BEFORE any damage resolution
    #
    # Mutual escape: both sides choose Attempt Escape. This is treated as an immediate
    # disengage with no damage exchanged.
    if player_action == "Attempt Escape" and enemy_action == "Attempt Escape":
        return {
            "player_state": player_state,
            "enemy_state": enemy_state,
            "combat_ended": True,
            "outcome": "escape",
            "round_summary": {
                "round": round_number,
                "player_action": player_action,
                "enemy_action": enemy_action,
                "player_hull_current": player_state.hull_current,
                "enemy_hull_current": enemy_state.hull_current,
                # Mark mutual escape explicitly for downstream consumers/tests.
                "escape": "mutual",
            },
        }
    
    # Single‑side escape attempts happen before damage. If escape fails, combat
    # proceeds to normal damage resolution.
    #
    # Player escape attempt
    if player_action == "Attempt Escape":
        escape = _escape_attempt_in_combat(
            rng=rng,
            round_number=round_number,
            fleeing_ship_state=player_ship_state,
            pursuing_ship_state=enemy_ship_state,
            fleeing_engine_effective=player_engine,
            pursuing_engine_effective=enemy_engine,
            rng_events=rng_events,
        )
        if escape["escaped"]:
            return {
                "player_state": player_state,
                "enemy_state": enemy_state,
                "combat_ended": True,
                "outcome": "escape",
                "round_summary": {
                    "round": round_number,
                    "player_action": player_action,
                    "enemy_action": enemy_action,
                    "player_hull_current": player_state.hull_current,
                    "enemy_hull_current": enemy_state.hull_current,
                    "escaped_by": "player",
                },
            }
    
    # Enemy escape attempt (only if player did not already succeed escaping)
    if enemy_action == "Attempt Escape":
        escape = _escape_attempt_in_combat(
            rng=rng,
            round_number=round_number,
            fleeing_ship_state=enemy_ship_state,
            pursuing_ship_state=player_ship_state,
            fleeing_engine_effective=enemy_engine,
            pursuing_engine_effective=player_engine,
            rng_events=rng_events,
        )
        if escape["escaped"]:
            return {
                "player_state": player_state,
                "enemy_state": enemy_state,
                "combat_ended": True,
                "outcome": "escape",
                "round_summary": {
                    "round": round_number,
                    "player_action": player_action,
                    "enemy_action": enemy_action,
                    "player_hull_current": player_state.hull_current,
                    "enemy_hull_current": enemy_state.hull_current,
                    "escaped_by": "enemy",
                },
            }
    
    # Resolve attacks
    player_attack = _resolve_attack("player", "enemy", player_weapon, enemy_defense, enemy_action, rng, round_number, rng_events)
    enemy_attack = _resolve_attack("enemy", "player", enemy_weapon, player_defense, player_action, rng, round_number, rng_events)
    
    # Apply damage and degradation (mutates player_state and enemy_state)
    _apply_damage_and_degradation(player_state, enemy_attack["damage"], rng, round_number, rng_events, target_ship_state=player_ship_state)
    _apply_damage_and_degradation(enemy_state, player_attack["damage"], rng, round_number, rng_events, target_ship_state=enemy_ship_state)
    
    # Check destruction
    player_destroyed = player_state.hull_current <= 0
    enemy_destroyed = enemy_state.hull_current <= 0
    
    if player_destroyed or enemy_destroyed:
        if player_destroyed and enemy_destroyed:
            winner: Literal["player", "enemy", "none"] = "none"
        elif enemy_destroyed:
            winner = "player"
        else:
            winner = "enemy"
        
        return {
            "player_state": player_state,
            "enemy_state": enemy_state,
            "combat_ended": True,
            "outcome": "destroyed",
            "round_summary": {
                "round": round_number,
                "player_action": player_action,
                "enemy_action": enemy_action,
                "player_hull_current": player_state.hull_current,
                "enemy_hull_current": enemy_state.hull_current,
                "winner": winner,
            },
        }
    
    # Combat continues (no termination conditions met)
    return {
        "player_state": player_state,
        "enemy_state": enemy_state,
        "combat_ended": False,
        "outcome": None,
        "round_summary": {
            "round": round_number,
            "player_action": player_action,
            "enemy_action": enemy_action,
            "player_hull_current": player_state.hull_current,
            "enemy_hull_current": enemy_state.hull_current,
        },
    }


def _create_initial_state_from_ship_state(ship_state: dict[str, Any]) -> CombatState:
    assembled = assemble_ship(ship_state["hull_id"], ship_state["module_instances"], {"weapon": 0, "defense": 0, "engine": 0})
    hull_max = int(assembled["hull_max"])
    crew_modifiers = _crew_modifiers_for_ship_state(ship_state)
    repair_uses = {}
    for index, module_instance in enumerate(ship_state["module_instances"]):
        if _module_is_repair(module_instance):
            repair_uses[str(index)] = 2
    if repair_uses and int(crew_modifiers.repair_uses_bonus) != 0:
        first_key = sorted(repair_uses.keys())[0]
        repair_uses[first_key] = max(0, repair_uses[first_key] + int(crew_modifiers.repair_uses_bonus))
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
        repair_amount_bonus=int(crew_modifiers.repair_amount_bonus),
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


def _repair_once(ship_state: dict[str, Any], state: CombatState, action_repair_bonus: int = 0) -> Optional[dict]:
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
    magnitude += int(state.repair_amount_bonus)
    magnitude += int(action_repair_bonus)

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


def _escape_attempt_in_combat(
    rng: CombatRng,
    round_number: int,
    fleeing_ship_state: dict[str, Any],
    pursuing_ship_state: dict[str, Any],
    fleeing_engine_effective: int,
    pursuing_engine_effective: int,
    rng_events: list[dict],
) -> dict:
    """
    Resolve escape attempt inside combat using combat RNG.
    Uses engine band delta + modifiers (cloak helps escape; interdiction hurts escape).
    """
    module_defs = _modules_by_id()
    
    # Extract cloaking and interdiction devices
    fleeing_cloak = any(
        module_defs.get(entry.get("module_id", ""), {}).get("primary_tag") == "combat:utility_cloak"
        or module_defs.get(entry.get("module_id", ""), {}).get("primary_tag") == "ship:utility_cloak"
        for entry in fleeing_ship_state.get("module_instances", [])
    )
    pursuing_interdiction = any(
        module_defs.get(entry.get("module_id", ""), {}).get("primary_tag") == "ship:utility_interdiction"
        for entry in pursuing_ship_state.get("module_instances", [])
    )
    
    # Count pilot crew
    fleeing_pilot_count = sum(1 for crew in fleeing_ship_state.get("crew", []) if crew == "crew:pilot")
    pursuing_pilot_count = sum(1 for crew in pursuing_ship_state.get("crew", []) if crew == "crew:pilot")
    
    # Calculate engine delta
    engine_delta = fleeing_engine_effective - pursuing_engine_effective
    
    # Apply modifiers
    escape_modifier = 0
    if fleeing_cloak:
        escape_modifier += 1
    escape_modifier += fleeing_pilot_count
    
    pursuer_modifier = 0
    if pursuing_interdiction:
        pursuer_modifier += 1
    pursuer_modifier += pursuing_pilot_count
    
    # Final delta with modifiers
    final_delta = engine_delta + escape_modifier - pursuer_modifier
    
    # Roll escape: need positive delta to escape
    if final_delta > 0:
        # Escape succeeds
        roll = rng.randint(1, 100, "escape_roll", round_number, rng_events)
        threshold = 50  # Simple threshold for positive delta
        escaped = True
    else:
        # Escape fails
        roll = rng.randint(1, 100, "escape_roll", round_number, rng_events)
        threshold = 100  # Impossible threshold
        escaped = False
    
    return {
        "escaped": escaped,
        "roll": roll,
        "threshold": threshold,
        "engine_delta": engine_delta,
        "escape_modifier": escape_modifier,
        "pursuer_modifier": pursuer_modifier,
        "final_delta": final_delta,
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
    crew_band_bonus: int = 0,
    action_bonus: int = 0,
) -> int:
    value = assembled["bands"]["effective"][subsystem]
    value += int(crew_band_bonus)
    if _focus_target(action) == subsystem:
        value += 1
    value += int(action_bonus)
    if subsystem == "weapon":
        value = max(0, value + rps_bias)
    return max(0, value)


def _normalize_ship_state(ship_state: dict[str, Any], role: str) -> dict[str, Any]:
    if ship_state is None:
        raise ValueError(f"Missing {role} ship input. ship_state is required.")
    if "hull_id" not in ship_state:
        raise ValueError(f"Missing {role} ship input. hull_id is required.")
    if "module_instances" not in ship_state:
        raise ValueError(f"Missing {role} ship input. module_instances is required.")
    normalized = {
        "hull_id": ship_state["hull_id"],
        "module_instances": list(ship_state["module_instances"]),
        "degradation_state": dict(ship_state.get("degradation_state", {"weapon": 0, "defense": 0, "engine": 0})),
    }
    if "crew" in ship_state:
        normalized["crew"] = list(ship_state.get("crew", []))
    if "tags" in ship_state:
        normalized["tags"] = list(ship_state.get("tags", []))
    return normalized




def resolve_combat(
    world_seed: str | int,
    combat_id: str,
    player_ship_state: dict[str, Any],
    enemy_ship_state: dict[str, Any],
    player_action_selector: Optional[Callable[..., ActionName]] = None,
    enemy_action_selector: Optional[Callable[..., ActionName]] = None,
    max_rounds: int = 20,
    system_id: str = "",
    combat_rng_seed: int | None = None,
) -> CombatResult:
    # Generate or use provided combat RNG seed
    if combat_rng_seed is None:
        combat_rng_seed = secrets.randbits(64)
    
    # Normalize ship states
    player_ship = _normalize_ship_state(player_ship_state, "player")
    enemy_ship = _normalize_ship_state(enemy_ship_state, "enemy")
    
    # Assemble ships once at combat start (with initial degradation)
    player_initial_degradation = dict(player_ship.get("degradation_state", {"weapon": 0, "defense": 0, "engine": 0}))
    enemy_initial_degradation = dict(enemy_ship.get("degradation_state", {"weapon": 0, "defense": 0, "engine": 0}))
    
    assembled_player_base = assemble_ship(player_ship["hull_id"], player_ship["module_instances"], player_initial_degradation)
    assembled_enemy_base = assemble_ship(enemy_ship["hull_id"], enemy_ship["module_instances"], enemy_initial_degradation)
    
    # Store base pre-degradation bands (immutable)
    player_base_bands = dict(assembled_player_base["bands"]["pre_degradation"])
    enemy_base_bands = dict(assembled_enemy_base["bands"]["pre_degradation"])
    
    # Compute RCP and TR
    rcp_player, tr_player = compute_rcp_and_tr_from_ship_state(player_ship)
    rcp_enemy, tr_enemy = compute_rcp_and_tr_from_ship_state(enemy_ship)
    
    # Initialize combat states
    player_state = _create_initial_state_from_ship_state(player_ship)
    enemy_state = _create_initial_state_from_ship_state(enemy_ship)
    player_state.degradation.update(player_initial_degradation)
    enemy_state.degradation.update(enemy_initial_degradation)
    player_crew_mods = _crew_modifiers_for_ship_state(player_ship)
    enemy_crew_mods = _crew_modifiers_for_ship_state(enemy_ship)
    
    # Create combat RNG
    rng = CombatRng(combat_rng_seed)
    log: list[dict] = []
    
    # Log combat start with combat_rng_seed
    log.append({
        "combat_start": True,
        "combat_id": combat_id,
        "combat_rng_seed": combat_rng_seed,
    })

    for round_number in range(1, max_rounds + 1):
        round_log = {
            "round": round_number,
            "combat_rng_seed": combat_rng_seed,
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
        
        # Action selectors - support both old signature (with args) and new (no args)
        if player_action_selector:
            try:
                player_action = player_action_selector(round_number, player_state, enemy_state, player_ship, enemy_ship, player_allowed)
            except TypeError:
                player_action = player_action_selector()
        else:
            player_action = _default_selector(round_number, player_state, enemy_state, player_ship, enemy_ship, player_allowed)
        
        if enemy_action_selector:
            try:
                enemy_action = enemy_action_selector(round_number, enemy_state, player_state, enemy_ship, player_ship, enemy_allowed)
            except TypeError:
                enemy_action = enemy_action_selector()
        else:
            enemy_action = _default_selector(round_number, enemy_state, player_state, enemy_ship, player_ship, enemy_allowed)
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
                combat_rng_seed=combat_rng_seed,
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
                combat_rng_seed=combat_rng_seed,
            )

        if player_action == "Repair Systems":
            round_log["repair"]["player"] = _repair_once(
                player_ship,
                player_state,
                action_repair_bonus=int(player_crew_mods.repair_focus_bonus),
            )
        if enemy_action == "Repair Systems":
            round_log["repair"]["enemy"] = _repair_once(
                enemy_ship,
                enemy_state,
                action_repair_bonus=int(enemy_crew_mods.repair_focus_bonus),
            )

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

        # Compute RPS (unchanged)
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
        
        # Compute effective bands from base bands + degradation + focus + RPS + crew bonuses
        # Check for RED state (degradation >= capacity)
        player_red = {
            "weapon": player_state.degradation.get("weapon", 0) >= player_state.subsystem_capacity.get("weapon", 1),
            "defense": player_state.degradation.get("defense", 0) >= player_state.subsystem_capacity.get("defense", 1),
            "engine": player_state.degradation.get("engine", 0) >= player_state.subsystem_capacity.get("engine", 1),
        }
        enemy_red = {
            "weapon": enemy_state.degradation.get("weapon", 0) >= enemy_state.subsystem_capacity.get("weapon", 1),
            "defense": enemy_state.degradation.get("defense", 0) >= enemy_state.subsystem_capacity.get("defense", 1),
            "engine": enemy_state.degradation.get("engine", 0) >= enemy_state.subsystem_capacity.get("engine", 1),
        }
        
        def _compute_effective_band(base_band: int, degradation: int, subsystem: str, action: ActionName, rps_bias: int, crew_bonus: int, action_bonus: int, is_red: bool) -> int:
            if is_red:
                return 0
            effective = max(0, base_band - degradation)
            effective += crew_bonus
            if _focus_target(action) == subsystem:
                effective += 1
            effective += action_bonus
            if subsystem == "weapon":
                effective = max(0, effective + rps_bias)
            return max(0, effective)
        
        player_weapon = _compute_effective_band(
            player_base_bands["weapon"],
            player_state.degradation.get("weapon", 0),
            "weapon",
            player_action,
            player_rps,
            int(player_crew_mods.attack_band_bonus),
            int(player_crew_mods.focus_fire_bonus if player_action == "Focus Fire" else 0),
            player_red["weapon"],
        )
        player_defense = _compute_effective_band(
            player_base_bands["defense"],
            player_state.degradation.get("defense", 0),
            "defense",
            player_action,
            0,
            int(player_crew_mods.defense_band_bonus),
            int(player_crew_mods.reinforce_shields_bonus if player_action == "Reinforce Shields" else 0),
            player_red["defense"],
        )
        player_engine = _compute_effective_band(
            player_base_bands["engine"],
            player_state.degradation.get("engine", 0),
            "engine",
            player_action,
            0,
            int(player_crew_mods.engine_band_bonus),
            int(player_crew_mods.evasive_bonus if player_action == "Evasive Maneuvers" else 0),
            player_red["engine"],
        )
        enemy_weapon = _compute_effective_band(
            enemy_base_bands["weapon"],
            enemy_state.degradation.get("weapon", 0),
            "weapon",
            enemy_action,
            enemy_rps,
            int(enemy_crew_mods.attack_band_bonus),
            int(enemy_crew_mods.focus_fire_bonus if enemy_action == "Focus Fire" else 0),
            enemy_red["weapon"],
        )
        enemy_defense = _compute_effective_band(
            enemy_base_bands["defense"],
            enemy_state.degradation.get("defense", 0),
            "defense",
            enemy_action,
            0,
            int(enemy_crew_mods.defense_band_bonus),
            int(enemy_crew_mods.reinforce_shields_bonus if enemy_action == "Reinforce Shields" else 0),
            enemy_red["defense"],
        )
        enemy_engine = _compute_effective_band(
            enemy_base_bands["engine"],
            enemy_state.degradation.get("engine", 0),
            "engine",
            enemy_action,
            0,
            int(enemy_crew_mods.engine_band_bonus),
            int(enemy_crew_mods.evasive_bonus if enemy_action == "Evasive Maneuvers" else 0),
            enemy_red["engine"],
        )

        round_log["bands"] = {
            "player": {"weapon": player_weapon, "defense": player_defense, "engine": player_engine},
            "enemy": {"weapon": enemy_weapon, "defense": enemy_defense, "engine": enemy_engine},
        }
        round_log["rps"] = {"player_attack_vs_enemy": player_rps, "enemy_attack_vs_player": enemy_rps}

        if player_action == "Attempt Escape":
            escape = _escape_attempt_in_combat(
                rng=rng,
                round_number=round_number,
                fleeing_ship_state=player_ship,
                pursuing_ship_state=enemy_ship,
                fleeing_engine_effective=player_engine,
                pursuing_engine_effective=enemy_engine,
                rng_events=round_log["rng_events"],
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
                    combat_rng_seed=combat_rng_seed,
                )
        if enemy_action == "Attempt Escape":
            escape = _escape_attempt_in_combat(
                rng=rng,
                round_number=round_number,
                fleeing_ship_state=enemy_ship,
                pursuing_ship_state=player_ship,
                fleeing_engine_effective=enemy_engine,
                pursuing_engine_effective=player_engine,
                rng_events=round_log["rng_events"],
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
                    combat_rng_seed=combat_rng_seed,
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
                combat_rng_seed=combat_rng_seed,
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
        combat_rng_seed=combat_rng_seed,
    )
