from dataclasses import dataclass
from enum import Enum
from typing import Set
import random

from government_registry import GovernmentRegistry
from logger import Logger


class LegalityStatus(str, Enum):
    LEGAL = "LEGAL"
    RESTRICTED = "RESTRICTED"
    ILLEGAL = "ILLEGAL"


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


class GovernmentLawEngine:
    def __init__(self, registry: GovernmentRegistry, logger: Logger, seed: int) -> None:
        self._registry = registry
        self._logger = logger
        self._seed = seed

    def resolve_legality(
        self,
        government_id: str,
        commodity: Commodity,
        action: str,
        turn: int,
    ) -> LegalityStatus:
        government = self._registry.get_government(government_id)
        regulation_level = government.regulation_level
        tags = commodity.tags
        restricted_tags = set(government.ideological_modifiers.get("restricted_tags", []))

        if commodity.commodity_id in government.illegal_goods:
            result = LegalityStatus.ILLEGAL
            reason = "illegal_goods"
        elif tags.intersection(restricted_tags):
            if regulation_level >= 70:
                result = LegalityStatus.ILLEGAL
            elif regulation_level >= 40:
                result = LegalityStatus.RESTRICTED
            else:
                result = LegalityStatus.LEGAL
            reason = "restricted_tags"
        else:
            if regulation_level >= 85:
                result = LegalityStatus.RESTRICTED
            else:
                result = LegalityStatus.LEGAL
            reason = "regulation_level"

        self._logger.log(
            turn=turn,
            action="legality_check",
            state_change=(
                f"government_id={government.id} government_name={government.name} "
                f"commodity_id={commodity.commodity_id} action={action} "
                f"result={result.value} reason={reason}"
            ),
        )
        return result

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
        legality = self.resolve_legality(
            government_id=government_id,
            commodity=commodity,
            action=action,
            turn=turn,
        )
        chance = self._inspection_chance(
            enforcement_strength=government.enforcement_strength,
            population_level=population_level,
            legality=legality,
        )
        roll = self._roll(system_id, government_id, commodity.commodity_id, action, turn)
        triggered = roll <= chance
        self._logger.log(
            turn=turn,
            action="inspection_check",
            state_change=(
                f"system_id={system_id} government_id={government.id} "
                f"government_name={government.name} commodity_id={commodity.commodity_id} "
                f"action={action} legality={legality.value} "
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
        legality = self.resolve_legality(
            government_id=government_id,
            commodity=commodity,
            action=action,
            turn=turn,
        )

        outcome = EnforcementOutcome(fine=0, confiscated=0, reputation_delta=0, notes="")

        if response == PlayerInspectionResponse.SUBMIT:
            outcome = self._submit_outcome(government, legality)
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
                f"action={action} context={context.value} legality={legality.value} "
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
