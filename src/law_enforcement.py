"""
Law Enforcement Module

AUTHORITY BOUNDARIES:
- This module handles law enforcement checkpoints, inspections, and consequences
- This module does NOT resolve combat, ship damage, or salvage
- Combat resolution authority is exclusively in combat_resolver.py via GameEngine
- When ATTACK or FLEE is chosen, this module signals GameEngine to initiate combat/pursuit
- NO ship state mutations (hull, degradation, destruction) occur in this module
- NO salvage handling occurs in this module
"""

from dataclasses import dataclass, replace
from enum import Enum
import json
import os
from pathlib import Path
import random
from typing import Any, Dict, List, Tuple

from types import MappingProxyType

try:
    from crew_modifiers import compute_crew_modifiers
except ModuleNotFoundError:
    from src.crew_modifiers import compute_crew_modifiers

from government_law_engine import GovernmentPolicyResult
from government_type import GovernmentType
from player_state import PlayerState


class TriggerType(str, Enum):
    BORDER = "BORDER"
    CUSTOMS = "CUSTOMS"


class PlayerOption(str, Enum):
    SUBMIT = "SUBMIT"
    FLEE = "FLEE"
    ATTACK = "ATTACK"
    BRIBE = "BRIBE"


class Severity(str, Enum):
    NONE = "NONE"
    MINOR = "MINOR"
    MODERATE = "MODERATE"
    MAJOR = "MAJOR"
    EXTREME = "EXTREME"


@dataclass(frozen=True)
class PlayerSnapshot:
    reputation: int
    heat: int
    warrant: bool
    fines: int


@dataclass(frozen=True)
class CargoSnapshot:
    illegal_present: bool
    restricted_unlicensed_present: bool


@dataclass(frozen=True)
class EnforcementEvent:
    system_id: str
    trigger_type: TriggerType
    legality_state: str
    risk_tier: str
    inspection_score: int
    inspection_roll: int
    player_snapshot: PlayerSnapshot
    cargo_snapshot: CargoSnapshot


@dataclass(frozen=True)
class EnforcementOutcome:
    escaped: bool
    arrested: bool
    dead: bool
    market_access_denied: bool
    ship_lost: bool
    warrant_issued: bool
    fines_added: int
    rep_delta: int
    heat_delta: int
    consequences_applied: List[str]
    confiscation_percent: int
    confiscated_amount: int
    detention_tier: int | None
    severity_base: Severity
    severity_after_enforcement: Severity
    severity_after_reputation: Severity
    severity_final: Severity
    bribery_roll: int | None
    bribery_chance: int | None
    bribery_result: str | None
    lawyer_used: bool
    consumed_lawyer_id: str | None
    route_to_handler: str | None = None  # "combat" or "pursuit" to route to unified systems


def maybe_downgrade_tier2_with_lawyer(player_state, ship, lawyer_id: str | None = None) -> tuple[bool, str | None]:
    if ship is None:
        return False, None

    crew_mods = compute_crew_modifiers(ship)
    available_lawyer_ids = list(crew_mods.lawyer_ids)
    if not available_lawyer_ids:
        return False, None

    if lawyer_id is not None:
        if lawyer_id not in available_lawyer_ids:
            raise ValueError(f"lawyer_id '{lawyer_id}' was not found among ship lawyer crew.")
        consumed_id = lawyer_id
    else:
        consumed_id = available_lawyer_ids[0]

    ship.remove_crew(consumed_id)
    return True, consumed_id
def _load_consequences() -> MappingProxyType:
    path = Path(__file__).resolve().parents[1] / "data" / "consequences.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    if "violations" not in data or "reputation_deltas" not in data:
        raise ValueError("consequences.json must include violations and reputation_deltas.")
    return MappingProxyType(data)


_CONSEQUENCES = _load_consequences()


def get_consequences(violation_type: str, severity: Severity) -> dict | None:
    violations = _CONSEQUENCES.get("violations", {})
    block = violations.get(violation_type, {})
    return block.get(severity.value)




def band_index_from_1_100(value: int) -> int:
    """
    D) Canonical band computation function for reputation/notoriety scores.
    
    Maps a score from 1-100 to a band index:
    - Band -2: value <= 20  (very low)
    - Band -1: 20 < value <= 40  (low)
    - Band  0: 40 < value <= 60  (neutral)
    - Band  1: 60 < value <= 80  (high)
    - Band  2: 80 < value <= 100 (very high)
    
    Boundaries are inclusive on the upper end (e.g., value=20 maps to -2, value=21 maps to -1).
    Negative values are treated as <= 20 (band -2).
    
    This is the single source of truth for band computation.
    Used by reputation_band and notoriety_band calculations.
    """
    if value <= 20:
        return -2
    if value <= 40:
        return -1
    if value <= 60:
        return 0
    if value <= 80:
        return 1
    return 2


def risk_tier_to_numeric_and_band(risk_tier: str) -> Tuple[int, int]:
    mapping = {
        "None": (20, -2),
        "Low": (40, -1),
        "Medium": (60, 0),
        "High": (80, 1),
        "Severe": (100, 2),
    }
    return mapping[risk_tier]


def heat_modifier(band: int) -> int:
    return { -2: 0, -1: 5, 0: 10, 1: 20, 2: 35 }[band]


def reputation_modifier(band: int) -> int:
    return { -2: 15, -1: 5, 0: 0, 1: -10, 2: -20 }[band]


def compute_inspection_score(government: GovernmentType, rep_band: int, heat_band: int) -> int:
    score = government.regulation_level
    score += heat_modifier(heat_band)
    score += reputation_modifier(rep_band)
    return max(0, min(100, score))


def inspection_occurs(rng: random.Random, score: int) -> Tuple[int, bool]:
    roll = rng.randint(1, 100)
    return roll, roll <= score


def compute_base_severity(legality_state: str, risk_band: int) -> Severity:
    if legality_state == "LEGAL":
        return Severity.NONE
    if legality_state == "RESTRICTED":
        if risk_band <= -1:
            return Severity.MINOR
        if risk_band == 0:
            return Severity.MODERATE
        return Severity.MAJOR
    if risk_band <= -1:
        return Severity.MODERATE
    if risk_band == 0:
        return Severity.MAJOR
    return Severity.EXTREME


def adjust_severity_by_enforcement_strength(severity: Severity, enforcement_strength: int) -> Severity:
    if enforcement_strength <= 70:
        return severity
    return _shift_severity(severity, 1)


def adjust_severity_by_reputation(severity: Severity, rep_band: int) -> Severity:
    if rep_band == -2:
        return _shift_severity(severity, 1)
    if rep_band in (1, 2):
        return _shift_severity(severity, -1)
    return severity


def apply_warrant_and_fines_overrides(
    severity: Severity,
    warrant_present: bool,
) -> Severity:
    if warrant_present:
        return max(severity, Severity.MAJOR, key=_severity_index)
    return severity


def compute_bribery_chance(
    government: GovernmentType,
    enforcement_strength: int,
    bribe_tier: str,
    post_inspection: bool,
) -> int:
    tier_bonus = {"SMALL": 0, "MEDIUM": 15, "LARGE": 30}[bribe_tier]
    chance = government.bribery_susceptibility + tier_bonus
    chance -= enforcement_strength // 2
    if post_inspection:
        chance -= 20
    return max(0, min(85, chance))


def resolve_option(
    event: EnforcementEvent,
    option: PlayerOption,
    rng: random.Random,
    config: Dict[str, str],
    policy_results: List[Tuple[str, GovernmentPolicyResult]],
) -> EnforcementOutcome:
    """
    Resolve player option during law enforcement checkpoint.
    
    IMPORTANT: This function does NOT resolve combat, ship damage, or salvage.
    - For ATTACK: Sets route_to_handler="combat" to signal GameEngine to initiate combat
    - For FLEE: Sets route_to_handler="pursuit" to signal GameEngine to initiate pursuit
    - NO combat rounds are resolved here
    - NO ship damage/hull/degradation mutations occur here
    - NO salvage logic exists here
    - Combat resolution authority is exclusively in combat_resolver.py via GameEngine
    """
    bribery_roll = None
    bribery_chance = None
    bribery_result = None
    bribery_success = False

    severity_base = compute_base_severity(event.legality_state, band_index_from_1_100(_risk_numeric(event.risk_tier)))
    severity_after_enforcement = adjust_severity_by_enforcement_strength(
        severity_base, config["enforcement_strength"]
    )
    severity_after_reputation = adjust_severity_by_reputation(severity_after_enforcement, config["rep_band"])
    severity_final = apply_warrant_and_fines_overrides(severity_after_reputation, config["warrant_present"])

    escaped = False
    arrested = False
    dead = False
    market_access_denied = False
    ship_lost = False
    warrant_issued = False
    fines_added = 0
    rep_delta = 0
    heat_delta = 0
    consequences_applied: List[str] = []
    confiscation_percent = 0
    confiscated_amount = 0
    detention_tier: int | None = None
    route_to_handler: str | None = None
    violation_type = _select_violation(event, option, False, policy_results)

    if config["warrant_present"]:
        if option == PlayerOption.BRIBE:
            bribery_chance = compute_bribery_chance(
                config["government"],
                config["enforcement_strength"],
                config["bribe_tier"],
                post_inspection=True,
            )
            bribery_roll = rng.randint(1, 100)
            bribery_result = "success" if bribery_roll <= bribery_chance else "fail"
            if bribery_roll <= bribery_chance:
                bribery_success = True
                arrested = False
                escaped = True
                heat_delta += 5
            else:
                arrested = True
                heat_delta += 10
        else:
            arrested = True
        violation_type = _select_violation(event, option, escaped, policy_results)
        return _finalize_outcome(
            event=event,
            option=option,
            violation_type=violation_type,
            severity_base=severity_base,
            severity_after_enforcement=severity_after_enforcement,
            severity_after_reputation=severity_after_reputation,
            severity_final=severity_final,
            escaped=escaped,
            arrested=arrested,
            dead=dead,
            market_access_denied=market_access_denied,
            ship_lost=ship_lost,
            base_rep_delta=rep_delta,
            base_heat_delta=heat_delta,
            consequences_applied=consequences_applied,
            confiscation_percent=confiscation_percent,
            confiscated_amount=confiscated_amount,
            detention_tier=detention_tier,
            bribery_roll=bribery_roll,
            bribery_chance=bribery_chance,
            bribery_result=bribery_result,
            bribery_success=bribery_success,
            fines_outstanding=config["fines_outstanding"],
            policy_results=policy_results,
        )

    if option == PlayerOption.SUBMIT:
        if event.legality_state == "LEGAL":
            rep_delta += 1
        elif event.legality_state == "RESTRICTED":
            # TODO(Phase 2.7): Restricted submit should offer pay fine, license, bribe, or refuse.
            heat_delta += 5
        else:
            heat_delta += 10
    elif option == PlayerOption.FLEE:
        # Route to unified pursuit system - do not resolve escape here
        # The game engine will handle routing to pursuit_resolver
        route_to_handler = "pursuit"
        # Heat delta will be applied after pursuit resolution
        heat_delta += 10  # Base heat for attempting to flee
    elif option == PlayerOption.ATTACK:
        # Route to unified combat system - do not resolve combat here
        # The game engine will handle routing to combat_resolver
        # NO combat resolution, NO ship damage, NO salvage handling occurs here
        # NO combat rounds are resolved here
        # NO hull/degradation mutations occur here
        # Combat must be initiated ONLY via GameEngine._resolve_encounter_combat()
        route_to_handler = "combat"
        # Heat delta will be applied after combat resolution (by GameEngine)
        heat_delta += 20  # Base heat for attacking enforcement
    elif option == PlayerOption.BRIBE:
        bribery_chance = compute_bribery_chance(
            config["government"],
            config["enforcement_strength"],
            config["bribe_tier"],
            post_inspection=True,
        )
        bribery_roll = rng.randint(1, 100)
        bribery_result = "success" if bribery_roll <= bribery_chance else "fail"
        if bribery_roll <= bribery_chance:
            bribery_success = True
            heat_delta += 5
        else:
            heat_delta += 10
            if event.legality_state == "ILLEGAL":
                arrested = True
    
    violation_type = _select_violation(event, option, escaped, policy_results)
    return _finalize_outcome(
        event=event,
        option=option,
        violation_type=violation_type,
        severity_base=severity_base,
        severity_after_enforcement=severity_after_enforcement,
        severity_after_reputation=severity_after_reputation,
        severity_final=severity_final,
        escaped=escaped,
        arrested=arrested,
        dead=dead,
        market_access_denied=market_access_denied,
        ship_lost=ship_lost,
        base_rep_delta=rep_delta,
        base_heat_delta=heat_delta,
        consequences_applied=consequences_applied,
        confiscation_percent=confiscation_percent,
        confiscated_amount=confiscated_amount,
        detention_tier=detention_tier,
        bribery_roll=bribery_roll,
        bribery_chance=bribery_chance,
        bribery_result=bribery_result,
        bribery_success=bribery_success,
        fines_outstanding=config["fines_outstanding"],
        policy_results=policy_results,
        route_to_handler=route_to_handler,
    )


def enforcement_checkpoint(
    *,
    system_id: str,
    trigger_type: TriggerType,
    government: GovernmentType,
    policy_results: List[Tuple[str, GovernmentPolicyResult]],
    player: PlayerState,
    world_seed: int,
    turn: int,
    cargo_snapshot: CargoSnapshot,
    logger,
    option: PlayerOption | None = None,
    bribe_tier: str = "SMALL",
    ship: Any | None = None,
    lawyer_id: str | None = None,
) -> EnforcementOutcome | None:
    rep_score = player.reputation_by_system.get(system_id, 50)
    heat_score = player.heat_by_system.get(system_id, 0)
    rep_band = band_index_from_1_100(rep_score)
    heat_band = band_index_from_1_100(max(1, heat_score))
    inspection_score = compute_inspection_score(government, rep_band, heat_band)

    rng = _rng_for(world_seed, system_id, turn, trigger_type.value, "inspection")
    inspection_roll, occurs = inspection_occurs(rng, inspection_score)
    logger.log(
        turn=turn,
        action="law_enforcement_checkpoint",
        state_change=(
            f"trigger_type={trigger_type.value} system_id={system_id} "
            f"inspection_score={inspection_score} inspection_roll={inspection_roll} "
            f"inspection_result={occurs} heat={heat_score} rep={rep_score}"
        ),
    )
    if not occurs:
        return None

    legality_state = "LEGAL"
    risk_tier = "None"
    for _, policy in policy_results:
        if policy.legality_state.value == "ILLEGAL":
            legality_state = "ILLEGAL"
        elif policy.legality_state.value == "RESTRICTED" and legality_state != "ILLEGAL":
            legality_state = "RESTRICTED"
        risk_tier = _max_risk_tier(risk_tier, policy.risk_tier.value)

    event = EnforcementEvent(
        system_id=system_id,
        trigger_type=trigger_type,
        legality_state=legality_state,
        risk_tier=risk_tier,
        inspection_score=inspection_score,
        inspection_roll=inspection_roll,
        player_snapshot=PlayerSnapshot(
            reputation=rep_score,
            heat=heat_score,
            warrant=bool(player.warrants_by_system.get(system_id, [])),
            fines=player.outstanding_fines.get(system_id, 0),
        ),
        cargo_snapshot=cargo_snapshot,
    )

    selected_option = _resolve_option(option)
    config = {
        "enforcement_strength": government.enforcement_strength,
        "rep_band": rep_band,
        "warrant_present": bool(player.warrants_by_system.get(system_id, [])),
        "fines_outstanding": player.outstanding_fines.get(system_id, 0),
        "government": government,
        "bribe_tier": bribe_tier,
    }
    rng = _rng_for(world_seed, system_id, turn, trigger_type.value, selected_option.value)
    outcome = resolve_option(event, selected_option, rng, config, policy_results)

    if outcome.confiscation_percent > 0:
        confiscated_amount = _apply_confiscation(
            player=player,
            system_id=system_id,
            violation_type=outcome.consequences_applied[0] if outcome.consequences_applied else "",
            policy_results=policy_results,
            percent=outcome.confiscation_percent,
        )
        outcome = replace(outcome, confiscated_amount=confiscated_amount)
    if outcome.detention_tier == 2:
        downgraded, consumed_lawyer_id = maybe_downgrade_tier2_with_lawyer(player, ship, lawyer_id)
        if downgraded:
            outcome = replace(
                outcome,
                detention_tier=1,
                dead=False,
                arrested=False,
                lawyer_used=True,
                consumed_lawyer_id=consumed_lawyer_id,
            )
            logger.log(
                turn=turn,
                action="detention_tier2_downgraded",
                state_change=(
                    f"system_id={system_id} lawyer_used=True consumed_lawyer_id={consumed_lawyer_id} "
                    "downgrade=tier2_to_tier1"
                ),
            )

    if outcome.detention_tier == 1:
        _confiscate_all(player)
        player.active_ship_id = None
        outcome = replace(outcome, ship_lost=True)
        logger.log(
            turn=turn,
            action="detention_tier1",
            state_change=f"system_id={system_id} ship_lost=True cargo_confiscated=all",
        )
    if outcome.detention_tier == 2:
        outcome = replace(outcome, dead=True, arrested=True)
        logger.log(
            turn=turn,
            action="detention_tier2",
            state_change=f"system_id={system_id} game_over=True",
        )
        player.arrest_state = "detained_tier_2"

    _apply_outcome(player, system_id, outcome)
    logger.log(
        turn=turn,
        action="law_enforcement_event",
        state_change=(
            f"trigger_type={trigger_type.value} system_id={system_id} "
            f"inspection_score={inspection_score} inspection_roll={inspection_roll} "
            f"option={selected_option.value} violation_type={outcome.consequences_applied[0] if outcome.consequences_applied else 'none'} "
            f"severity_base={outcome.severity_base.value} "
            f"severity_after_enforcement={outcome.severity_after_enforcement.value} "
            f"severity_after_reputation={outcome.severity_after_reputation.value} "
            f"severity_final={outcome.severity_final.value} warrant_present={event.player_snapshot.warrant} "
            f"warrant_issued={outcome.warrant_issued} fines_outstanding={event.player_snapshot.fines} "
            f"fines_added={outcome.fines_added} confiscation_percent={outcome.confiscation_percent} "
            f"confiscated_amount={outcome.confiscated_amount} detention_tier={outcome.detention_tier} "
            f"ship_lost={outcome.ship_lost} game_over={outcome.dead} "
            f"bribery_chance={outcome.bribery_chance} "
            f"bribery_roll={outcome.bribery_roll} bribery_result={outcome.bribery_result} "
            f"rep_before={event.player_snapshot.reputation} "
            f"rep_after={player.reputation_by_system.get(system_id, 50)} "
            f"heat_before={event.player_snapshot.heat} "
            f"heat_after={player.heat_by_system.get(system_id, 0)} "
            f"outcome=escaped:{outcome.escaped} arrested:{outcome.arrested}"
        ),
    )
    return outcome


def _apply_outcome(player: PlayerState, system_id: str, outcome: EnforcementOutcome) -> None:
    player.reputation_by_system[system_id] = player.reputation_by_system.get(system_id, 50) + outcome.rep_delta
    player.heat_by_system[system_id] = player.heat_by_system.get(system_id, 0) + outcome.heat_delta
    if outcome.warrant_issued:
        player.warrants_by_system.setdefault(system_id, [])
        player.warrants_by_system[system_id].append({"warrant_id": "AUTO"})
    if outcome.fines_added:
        player.outstanding_fines[system_id] = player.outstanding_fines.get(system_id, 0) + outcome.fines_added


def _resolve_option(option: PlayerOption | None) -> PlayerOption:
    if option is not None:
        return option
    if os.environ.get("ENFORCEMENT_INTERACTIVE") == "1":
        return PlayerOption.SUBMIT
    return PlayerOption.SUBMIT


def _rng_for(world_seed: int, system_id: str, turn: int, checkpoint: str, action: str) -> random.Random:
    token = f"{world_seed}:{system_id}:{turn}:{checkpoint}:{action}"
    value = 0
    for char in token:
        value = (value * 31 + ord(char)) % (2**32)
    return random.Random(value)


def _severity_index(sev: Severity) -> int:
    return [Severity.NONE, Severity.MINOR, Severity.MODERATE, Severity.MAJOR, Severity.EXTREME].index(sev)


def _shift_severity(sev: Severity, delta: int) -> Severity:
    order = [Severity.NONE, Severity.MINOR, Severity.MODERATE, Severity.MAJOR, Severity.EXTREME]
    index = max(1, min(len(order) - 1, order.index(sev) + delta))
    return order[index]


def _risk_numeric(risk_tier: str) -> int:
    return risk_tier_to_numeric_and_band(risk_tier)[0]


def _max_risk_tier(current: str, incoming: str) -> str:
    order = ["None", "Low", "Medium", "High", "Severe"]
    return order[max(order.index(current), order.index(incoming))]


def _select_violation(
    event: EnforcementEvent,
    option: PlayerOption,
    escaped: bool,
    policy_results: List[Tuple[str, GovernmentPolicyResult]],
) -> str | None:
    tags = _policy_tags(policy_results)
    candidates: List[str] = []
    if "piracy" in tags:
        candidates.append("piracy")
    if option == PlayerOption.ATTACK:
        candidates.append(
            "attack_border_inspection" if event.trigger_type == TriggerType.BORDER else "attack_customs"
        )
    if option == PlayerOption.FLEE and escaped:
        candidates.append(
            "avoid_border_inspection" if event.trigger_type == TriggerType.BORDER else "avoid_customs"
        )
    if event.cargo_snapshot.illegal_present:
        candidates.append("illegal_goods_possession")
    if "stolen" in tags:
        candidates.append("stolen_goods_possession")
    if "counterfeit" in tags:
        candidates.append("counterfeit_goods_possession")
    if event.cargo_snapshot.restricted_unlicensed_present:
        candidates.append("restricted_goods_unlicensed")
    priority = [
        "piracy",
        "attack_border_inspection",
        "attack_customs",
        "avoid_border_inspection",
        "avoid_customs",
        "illegal_goods_possession",
        "stolen_goods_possession",
        "counterfeit_goods_possession",
        "restricted_goods_unlicensed",
    ]
    for item in priority:
        if item in candidates:
            return item
    return None


def _policy_tags(policy_results: List[Tuple[str, GovernmentPolicyResult]]) -> List[str]:
    tags: List[str] = []
    for _, policy in policy_results:
        tags.extend(policy.consumed_tags)
    return tags


def _finalize_outcome(
    *,
    event: EnforcementEvent,
    option: PlayerOption,
    violation_type: str | None,
    severity_base: Severity,
    severity_after_enforcement: Severity,
    severity_after_reputation: Severity,
    severity_final: Severity,
    escaped: bool,
    arrested: bool,
    dead: bool,
    market_access_denied: bool,
    ship_lost: bool,
    base_rep_delta: int,
    base_heat_delta: int,
    consequences_applied: List[str],
    confiscation_percent: int,
    confiscated_amount: int,
    detention_tier: int | None,
    bribery_roll: int | None,
    bribery_chance: int | None,
    bribery_result: str | None,
    bribery_success: bool,
    fines_outstanding: int,
    policy_results: List[Tuple[str, GovernmentPolicyResult]],
    route_to_handler: str | None = None,
) -> EnforcementOutcome:
    rep_delta = base_rep_delta
    heat_delta = base_heat_delta
    fines_added = 0
    warrant_eligible = False

    if violation_type is None:
        consequences_applied.append("no_violation")
    else:
        consequences = get_consequences(violation_type, severity_final)
        if consequences is None:
            consequences_applied.append("no_consequences_defined")
        else:
            consequences_applied.append(violation_type)
            rep_key = consequences.get("reputation")
            if rep_key is not None:
                rep_delta = _CONSEQUENCES["reputation_deltas"].get(rep_key, 0)
            fine_block = consequences.get("fine", {})
            if fine_block.get("enabled") or "base" in fine_block:
                fines_added += int(fine_block.get("base", 0))
            confiscation = consequences.get("confiscation", {})
            confiscation_percent = int(confiscation.get("percent", 0))
            detention = consequences.get("detention", {})
            if detention.get("enabled") or "tier" in detention:
                detention_tier = detention.get("tier")
            arrest = consequences.get("arrest", {})
            if arrest.get("enabled"):
                arrested = True
            warrant = consequences.get("warrant", {})
            if warrant.get("eligible") is True:
                warrant_eligible = True
    # Contract overrides
    if event.trigger_type == TriggerType.BORDER and event.legality_state == "RESTRICTED":
        rep_delta = 0
        fines_added = 0
        confiscation_percent = 0
        detention_tier = None
        arrested = False
    if bribery_success:
        rep_delta = -1
        fines_added = 0
        confiscation_percent = 0
        detention_tier = None
        arrested = False
    if detention_tier == 1:
        confiscation_percent = 100
        arrested = False
    if detention_tier == 2:
        dead = True
        arrested = True
    # Existing fines are added only when bribery does not suppress consequences.
    if not bribery_success:
        fines_added += fines_outstanding
    # Warrants are issued only on escape and only if eligible.
    warrant_issued = escaped and warrant_eligible
    return EnforcementOutcome(
        escaped=escaped,
        arrested=arrested,
        dead=dead,
        market_access_denied=market_access_denied,
        ship_lost=ship_lost,
        warrant_issued=warrant_issued,
        fines_added=fines_added,
        rep_delta=rep_delta,
        heat_delta=heat_delta,
        consequences_applied=consequences_applied,
        confiscation_percent=confiscation_percent,
        confiscated_amount=confiscated_amount,
        detention_tier=detention_tier,
        severity_base=severity_base,
        severity_after_enforcement=severity_after_enforcement,
        severity_after_reputation=severity_after_reputation,
        severity_final=severity_final,
        bribery_roll=bribery_roll,
        bribery_chance=bribery_chance,
        bribery_result=bribery_result,
        lawyer_used=False,
        consumed_lawyer_id=None,
        route_to_handler=route_to_handler,
    )


def _apply_confiscation(
    *,
    player: PlayerState,
    system_id: str,
    violation_type: str,
    policy_results: List[Tuple[str, GovernmentPolicyResult]],
    percent: int,
) -> int:
    if percent <= 0:
        return 0
    total = 0
    for sku, policy in policy_results:
        if violation_type in {"attack_border_inspection", "attack_customs", "avoid_border_inspection", "avoid_customs"}:
            if policy.legality_state.value not in {"ILLEGAL", "RESTRICTED"}:
                continue
        elif violation_type == "illegal_goods_possession" and policy.legality_state.value != "ILLEGAL":
            continue
        if violation_type == "restricted_goods_unlicensed" and policy.legality_state.value != "RESTRICTED":
            continue
        if violation_type == "stolen_goods_possession" and "stolen" not in policy.consumed_tags:
            continue
        if violation_type == "counterfeit_goods_possession" and "counterfeit" not in policy.consumed_tags:
            continue
        count = player.cargo_by_ship.get("active", {}).get(sku, 0)
        if count <= 0:
            continue
        take = int(count * (percent / 100.0))
        if take <= 0:
            continue
        remaining = max(0, count - take)
        player.cargo_by_ship.setdefault("active", {})
        player.cargo_by_ship["active"][sku] = remaining
        total += take
    return total


def _confiscate_all(player: PlayerState) -> None:
    holdings = dict(player.cargo_by_ship.get("active", {}))
    for sku, count in holdings.items():
        if count <= 0:
            continue
        player.cargo_by_ship.setdefault("active", {})
        player.cargo_by_ship["active"][sku] = 0
