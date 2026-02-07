from dataclasses import dataclass
from enum import Enum
from typing import List, Set
import random

from government_registry import GovernmentRegistry
from logger import Logger


class LegalityStatus(str, Enum):
    LEGAL = "LEGAL"
    RESTRICTED = "RESTRICTED"
    ILLEGAL = "ILLEGAL"


class RiskTier(str, Enum):
    NONE = "None"
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    SEVERE = "Severe"


class InspectionContext(str, Enum):
    MARKET = "MARKET"
    TRANSPORT = "TRANSPORT"


class PlayerInspectionResponse(str, Enum):
    SUBMIT = "SUBMIT"
    FLEE = "FLEE"
    ATTACK = "ATTACK"
    BRIBE = "BRIBE"


@dataclass(frozen=True)
class EnforcementOutcome:
    fine: int
    confiscated: int
    reputation_delta: int
    notes: str


@dataclass(frozen=True)
class Commodity:
    commodity_id: str
    tags: Set[str]


@dataclass(frozen=True)
class GovernmentPolicyResult:
    legality_state: LegalityStatus
    risk_tier: RiskTier
    consumed_tags: List[str]


class GovernmentLawEngine:
    def __init__(self, registry: GovernmentRegistry, logger: Logger, seed: int) -> None:
        self._registry = registry
        self._logger = logger
        self._seed = seed

    def evaluate_policy(
        self,
        government_id: str,
        commodity: Commodity,
        action: str,
        turn: int,
    ) -> GovernmentPolicyResult:
        government = self._registry.get_government(government_id)
        tags = commodity.tags
        restricted_tags = set(government.ideological_modifiers.get("restricted_tags", []))
        consumed_tags = set()

        if commodity.commodity_id in government.illegal_goods:
            legality = LegalityStatus.ILLEGAL
            reason = "illegal_goods"
        elif tags.intersection(restricted_tags):
            legality = LegalityStatus.RESTRICTED
            reason = "restricted_tags"
            consumed_tags.update(tags.intersection(restricted_tags))
        else:
            legality = LegalityStatus.LEGAL
            reason = "regulation_level"

        tag_bias, tag_risk, interpreted_tags = self._interpret_tags(government, tags)
        consumed_tags.update(interpreted_tags)
        risk_tier = self._combine_risk(self._government_base_risk(government), tag_risk)

        self._logger.log(
            turn=turn,
            action="legality_check",
            state_change=(
                f"government_id={government.id} government_name={government.name} "
                f"commodity_id={commodity.commodity_id} action={action} "
                f"result={legality.value} reason={reason} "
                f"risk={risk_tier.value} consumed_tags={sorted(consumed_tags)}"
            ),
        )
        return GovernmentPolicyResult(
            legality_state=legality,
            risk_tier=risk_tier,
            consumed_tags=sorted(consumed_tags),
        )

    def inspection_check(
        self,
        system_id: str,
        population_level: int,
        government_id: str,
        commodity: Commodity,
        action: str,
        turn: int,
    ) -> bool:
        government = self._registry.get_government(government_id)
        policy = self.evaluate_policy(
            government_id=government_id,
            commodity=commodity,
            action=action,
            turn=turn,
        )
        chance = self._inspection_chance(
            enforcement_strength=government.enforcement_strength,
            population_level=population_level,
            legality=policy.legality_state,
        )
        roll = self._roll(system_id, government_id, commodity.commodity_id, action, turn)
        triggered = roll <= chance
        self._logger.log(
            turn=turn,
            action="inspection_check",
            state_change=(
                f"system_id={system_id} government_id={government.id} "
                f"government_name={government.name} commodity_id={commodity.commodity_id} "
                f"action={action} legality={policy.legality_state.value} "
                f"chance={chance:.2f} roll={roll} triggered={triggered}"
            ),
        )
        return triggered

    def resolve_enforcement(
        self,
        system_id: str,
        government_id: str,
        commodity: Commodity,
        action: str,
        context: InspectionContext,
        response: PlayerInspectionResponse,
        turn: int,
    ) -> EnforcementOutcome:
        government = self._registry.get_government(government_id)
        policy = self.evaluate_policy(
            government_id=government_id,
            commodity=commodity,
            action=action,
            turn=turn,
        )

        if context == InspectionContext.TRANSPORT and policy.legality_state == LegalityStatus.RESTRICTED:
            outcome = EnforcementOutcome(fine=0, confiscated=0, reputation_delta=0, notes="restricted_ignored_transport")
            self._logger.log(
                turn=turn,
                action="inspection_response",
                state_change=(
                    f"system_id={system_id} government_id={government.id} "
                    f"government_name={government.name} commodity_id={commodity.commodity_id} "
                    f"action={action} context={context.value} legality={policy.legality_state.value} "
                    f"response={response.value} fine={outcome.fine} "
                    f"confiscated={outcome.confiscated} reputation_delta={outcome.reputation_delta} "
                    f"notes={outcome.notes}"
                ),
            )
            return outcome

        outcome = EnforcementOutcome(fine=0, confiscated=0, reputation_delta=0, notes="")

        if response == PlayerInspectionResponse.SUBMIT:
            outcome = self._submit_outcome(government, policy.legality_state)
        elif response == PlayerInspectionResponse.FLEE:
            outcome = EnforcementOutcome(
                fine=0,
                confiscated=0,
                reputation_delta=-1,
                notes="attempted_flee",
            )
        elif response == PlayerInspectionResponse.ATTACK:
            outcome = EnforcementOutcome(
                fine=0,
                confiscated=0,
                reputation_delta=0,
                notes="combat_placeholder",
            )
        elif response == PlayerInspectionResponse.BRIBE:
            outcome = self._bribe_outcome(government)

        self._logger.log(
            turn=turn,
            action="inspection_response",
            state_change=(
                f"system_id={system_id} government_id={government.id} "
                f"government_name={government.name} commodity_id={commodity.commodity_id} "
                f"action={action} context={context.value} legality={policy.legality_state.value} "
                f"response={response.value} fine={outcome.fine} "
                f"confiscated={outcome.confiscated} reputation_delta={outcome.reputation_delta} "
                f"notes={outcome.notes}"
            ),
        )
        return outcome

    @staticmethod
    def _inspection_chance(
        enforcement_strength: int,
        population_level: int,
        legality: LegalityStatus,
    ) -> float:
        legality_multiplier = {
            LegalityStatus.LEGAL: 0.2,
            LegalityStatus.RESTRICTED: 0.6,
            LegalityStatus.ILLEGAL: 1.0,
        }[legality]
        population_adjustment = population_level * 5
        chance = enforcement_strength * legality_multiplier + population_adjustment
        return max(0.0, min(100.0, chance))

    def _roll(self, system_id: str, government_id: str, commodity_id: str, action: str, turn: int) -> int:
        seed = self._seed
        seed = self._stable_seed(seed, system_id, government_id, commodity_id, action, str(turn))
        rng = random.Random(seed)
        return rng.randint(1, 100)

    @staticmethod
    def _stable_seed(base: int, *parts: str) -> int:
        value = base
        for part in parts:
            for char in part:
                value = (value * 31 + ord(char)) % (2**32)
        return value

    @staticmethod
    def _government_base_risk(government: object) -> RiskTier:
        score = (
            getattr(government, "regulation_level")
            + getattr(government, "enforcement_strength")
            + getattr(government, "penalty_severity")
            - getattr(government, "tolerance_bias")
            - getattr(government, "bribery_susceptibility")
        )
        if score <= -50:
            return RiskTier.NONE
        if score <= 0:
            return RiskTier.LOW
        if score <= 50:
            return RiskTier.MEDIUM
        if score <= 100:
            return RiskTier.HIGH
        return RiskTier.SEVERE

    @staticmethod
    def _combine_risk(current: RiskTier, incoming: RiskTier) -> RiskTier:
        order = [RiskTier.NONE, RiskTier.LOW, RiskTier.MEDIUM, RiskTier.HIGH, RiskTier.SEVERE]
        return order[max(order.index(current), order.index(incoming))]

    def _interpret_tags(
        self,
        government: object,
        tags: Set[str],
    ) -> tuple[float, RiskTier, Set[str]]:
        possible_tags = {
            "luxury",
            "weaponized",
            "counterfeit",
            "stolen",
            "propaganda",
            "hazardous",
            "cybernetic",
        }
        bias = 0.0
        risk = RiskTier.NONE
        interpreted: Set[str] = set()
        for tag in tags:
            if tag not in possible_tags:
                continue
            tag_bias, tag_risk = self._tag_effect(government, tag)
            bias += tag_bias
            risk = self._combine_risk(risk, tag_risk)
            interpreted.add(tag)
        return bias, risk, interpreted

    def _tag_effect(self, government: object, tag: str) -> tuple[float, RiskTier]:
        favored_tags = set(getattr(government, "ideological_modifiers").get("favored_tags", []))
        restricted_tags = set(getattr(government, "ideological_modifiers").get("restricted_tags", []))
        gov_id = getattr(government, "id")
        regulation = getattr(government, "regulation_level")
        enforcement = getattr(government, "enforcement_strength")
        tolerance = getattr(government, "tolerance_bias")
        bribery = getattr(government, "bribery_susceptibility")

        bias = 0.0
        risk = RiskTier.NONE

        if tag == "luxury":
            if tolerance > 60:
                bias += 0.20
                risk = self._combine_risk(risk, RiskTier.LOW)
            if regulation > 70:
                bias -= 0.20
                risk = self._combine_risk(risk, RiskTier.MEDIUM)
            if tag in favored_tags:
                bias += 0.20
                risk = self._combine_risk(risk, RiskTier.LOW)
            if tag in restricted_tags:
                bias -= 0.20
                risk = self._combine_risk(risk, RiskTier.MEDIUM)
        elif tag == "weaponized":
            if gov_id in {"military", "fascist", "dictatorship"}:
                bias += 0.20
                risk = self._combine_risk(risk, RiskTier.MEDIUM)
            if gov_id in {"democracy", "collective_commune"}:
                bias -= 0.20
                risk = self._combine_risk(risk, RiskTier.HIGH)
            if gov_id == "anarchic":
                risk = self._combine_risk(risk, RiskTier.LOW)
            if tag in favored_tags:
                bias += 0.20
                risk = self._combine_risk(risk, RiskTier.MEDIUM)
            if tag in restricted_tags:
                bias -= 0.20
                risk = self._combine_risk(risk, RiskTier.HIGH)
        elif tag == "counterfeit":
            if bribery > 60:
                bias += 0.10
                risk = self._combine_risk(risk, RiskTier.MEDIUM)
            if enforcement > 70:
                bias -= 0.30
                risk = self._combine_risk(risk, RiskTier.HIGH)
            if regulation > 70:
                bias -= 0.20
                risk = self._combine_risk(risk, RiskTier.HIGH)
            if gov_id == "anarchic":
                risk = self._combine_risk(risk, RiskTier.LOW)
        elif tag == "stolen":
            if bribery > 60:
                bias += 0.10
                risk = self._combine_risk(risk, RiskTier.HIGH)
            if enforcement > 70:
                bias -= 0.30
                risk = self._combine_risk(risk, RiskTier.SEVERE)
            if tolerance > 70:
                risk = self._combine_risk(risk, RiskTier.MEDIUM)
        elif tag == "propaganda":
            if tag in favored_tags:
                bias += 0.20
                risk = self._combine_risk(risk, RiskTier.LOW)
            if tag in restricted_tags:
                bias -= 0.20
                risk = self._combine_risk(risk, RiskTier.HIGH)
            if regulation > 70:
                bias -= 0.10
                risk = self._combine_risk(risk, RiskTier.MEDIUM)
        elif tag == "hazardous":
            if regulation > 70:
                bias -= 0.20
                risk = self._combine_risk(risk, RiskTier.HIGH)
            if enforcement > 70:
                bias -= 0.10
                risk = self._combine_risk(risk, RiskTier.MEDIUM)
            if gov_id == "anarchic":
                risk = self._combine_risk(risk, RiskTier.LOW)
        elif tag == "cybernetic":
            if "technological" in favored_tags:
                bias += 0.20
                risk = self._combine_risk(risk, RiskTier.MEDIUM)
            if gov_id == "theocracy":
                bias -= 0.20
                risk = self._combine_risk(risk, RiskTier.HIGH)
            if gov_id == "anarchic":
                risk = self._combine_risk(risk, RiskTier.LOW)

        return bias, risk

    @staticmethod
    def _submit_outcome(government: object, legality: LegalityStatus) -> EnforcementOutcome:
        penalty_severity = getattr(government, "penalty_severity")
        if legality == LegalityStatus.LEGAL:
            return EnforcementOutcome(
                fine=0,
                confiscated=0,
                reputation_delta=1,
                notes="warning_only",
            )
        if legality == LegalityStatus.RESTRICTED:
            fine = penalty_severity * 2
            return EnforcementOutcome(
                fine=fine,
                confiscated=1,
                reputation_delta=0,
                notes="restricted_fine_partial_confiscation",
            )
        fine = penalty_severity * 5
        return EnforcementOutcome(
            fine=fine,
            confiscated=-1,
            reputation_delta=-2,
            notes="illegal_fine_confiscation",
        )

    @staticmethod
    def _bribe_outcome(government: object) -> EnforcementOutcome:
        susceptibility = getattr(government, "bribery_susceptibility")
        reputation_delta = 1 if susceptibility >= 50 else -1
        return EnforcementOutcome(
            fine=0,
            confiscated=0,
            reputation_delta=reputation_delta,
            notes="bribery_placeholder",
        )
