from dataclasses import dataclass
from typing import Dict, List
import random

from data_catalog import DataCatalog, Good
from government_law_engine import GovernmentPolicyResult, LegalityStatus, RiskTier
from government_type import GovernmentType
from logger import Logger
from market import Market, MarketGood


@dataclass(frozen=True)
class PricingBreakdown:
    base_price: float
    category_role: str
    substitute: bool
    substitute_discount: float
    tag_bias: float
    government_bias: float
    scarcity_modifier: float
    final_price: float
    tags: List[str]
    skipped_tags: List[str]
    interpreted_tags: List[str]
    risk_tier: RiskTier
    legality: LegalityStatus
    notes: str


@dataclass(frozen=True)
class PricingResult:
    final_price: float
    legality: LegalityStatus
    risk_tier: RiskTier
    breakdown: PricingBreakdown


SUBSTITUTE_DISCOUNT_MIN = -0.55
SUBSTITUTE_DISCOUNT_MAX = -0.40
TAG_BIAS_CAP_POSITIVE = 0.40
TAG_BIAS_CAP_NEGATIVE = -0.50
CATEGORY_ROLE_MULT: Dict[str, float] = {
    "produced": 0.80,
    "neutral": 1.00,
    "consumed": 1.20,
}
BASE_POSSIBLE_TAGS = {
    "luxury",
    "weaponized",
    "counterfeit",
    "stolen",
    "propaganda",
    "hazardous",
    "cybernetic",
}
def price_transaction(
    *,
    catalog: DataCatalog,
    market: Market,
    government: GovernmentType,
    policy: GovernmentPolicyResult,
    sku: str,
    action: str,
    world_seed: int,
    system_id: str,
    scarcity_modifier: float = 1.0,
    logger: Logger | None = None,
    turn: int = 0,
) -> PricingResult:
    market_good, _ = _find_market_good(market, sku)
    try:
        good = catalog.good_by_sku(sku)
    except KeyError:
        if market_good is None:
            raise
        good = Good(
            sku=market_good.sku,
            name=market_good.name,
            category=market_good.category,
            base_price=market_good.base_price,
            tags=list(market_good.tags),
            possible_tag=None,
        )
    substitute = False
    category_role = _category_role(market, good.category)
    if action == "buy":
        if market_good is None:
            raise ValueError(f"SKU {sku} not available to buy in system {system_id}.")
    else:
        if market_good is None:
            if good.category not in market.categories:
                raise ValueError(f"Category {good.category} not present for selling in system {system_id}.")
            substitute = True

    base_price = float(market_good.base_price) if market_good is not None else float(good.base_price)
    price = base_price

    # Step 2: category pressure (produced / neutral / consumed)
    price *= _category_pressure_multiplier(category_role)

    # Step 3: scarcity modifier (from Phase 1 economy availability)
    price *= scarcity_modifier

    # Step 4: substitute discount (selling only)
    substitute_discount = 0.0
    if action == "sell" and substitute:
        substitute_discount = resolve_substitute_discount(world_seed, system_id, sku)
        price *= 1.0 + substitute_discount

    tags = _resolved_tags(good, market_good)
    skipped_tags = [tag for tag in tags if tag in policy.consumed_tags]
    interpreted_tags = [tag for tag in tags if tag not in policy.consumed_tags]

    # Step 5: tag-based price interpretation
    tag_bias, _ = _interpret_tags(government, interpreted_tags)
    tag_bias = _clamp(tag_bias, TAG_BIAS_CAP_NEGATIVE, TAG_BIAS_CAP_POSITIVE)
    price *= 1.0 + tag_bias

    # Step 6: government price bias (coarse and capped)
    government_bias = 0.0  # TODO(Phase 2.6): Government bias is derived from tag interpretation only.
    price *= 1.0 + government_bias

    # Step 7: clamp final price
    price = max(price, _salvage_floor(base_price))
    if action == "sell" and substitute:
        ideal_price = _ideal_price_without_substitute(
            base_price=base_price,
            category_role=category_role,
            scarcity_modifier=scarcity_modifier,
            tag_bias=tag_bias,
            government_bias=government_bias,
        )
        price = min(price, ideal_price)

    breakdown = PricingBreakdown(
        base_price=base_price,
        category_role=category_role,
        substitute=substitute,
        substitute_discount=substitute_discount,
        tag_bias=tag_bias,
        government_bias=government_bias,
        scarcity_modifier=scarcity_modifier,
        final_price=price,
        tags=tags,
        skipped_tags=skipped_tags,
        interpreted_tags=interpreted_tags,
        risk_tier=policy.risk_tier,
        legality=policy.legality_state,
        notes="pricing_contract_v2_6",
    )
    result = PricingResult(
        final_price=price,
        legality=policy.legality_state,
        risk_tier=policy.risk_tier,
        breakdown=breakdown,
    )
    if logger is not None:
        _log_pricing(logger, turn, system_id, sku, action, breakdown)
    return result


def resolve_substitute_discount(world_seed: int, system_id: str, sku: str) -> float:
    rng = random.Random(_stable_seed(world_seed, system_id, sku))
    return rng.uniform(SUBSTITUTE_DISCOUNT_MIN, SUBSTITUTE_DISCOUNT_MAX)


def _find_market_good(market: Market, sku: str) -> tuple[MarketGood | None, str]:
    for category in market.categories.values():
        for good in category.produced:
            if good.sku == sku:
                return good, "produced"
        for good in category.consumed:
            if good.sku == sku:
                return good, "consumed"
        for good in category.neutral:
            if good.sku == sku:
                return good, "neutral"
    return None, ""


def _resolved_tags(good: Good, market_good: MarketGood | None) -> List[str]:
    if market_good is None:
        return list(good.tags)
    return list(market_good.tags)


def _interpret_tags(
    government: GovernmentType,
    tags: List[str],
) -> tuple[float, RiskTier]:
    bias = 0.0
    risk = RiskTier.NONE
    for tag in tags:
        if tag not in BASE_POSSIBLE_TAGS:
            continue
        tag_bias, tag_risk = _tag_effect(government, tag)
        bias += tag_bias
        risk = _combine_risk(risk, tag_risk)
    return bias, risk


def _tag_effect(government: GovernmentType, tag: str) -> tuple[float, RiskTier]:
    favored_tags = set(government.ideological_modifiers.get("favored_tags", []))
    restricted_tags = set(government.ideological_modifiers.get("restricted_tags", []))
    gov_id = government.id
    regulation = government.regulation_level
    enforcement = government.enforcement_strength
    tolerance = government.tolerance_bias
    bribery = government.bribery_susceptibility

    bias = 0.0
    risk = RiskTier.NONE

    if tag == "luxury":
        if tolerance > 60:
            bias += 0.20
            risk = _combine_risk(risk, RiskTier.LOW)
        if regulation > 70:
            bias -= 0.20
            risk = _combine_risk(risk, RiskTier.MEDIUM)
        if tag in favored_tags:
            bias += 0.20
            risk = _combine_risk(risk, RiskTier.LOW)
        if tag in restricted_tags:
            bias -= 0.20
            risk = _combine_risk(risk, RiskTier.MEDIUM)
    elif tag == "weaponized":
        if gov_id in {"military", "fascist", "dictatorship"}:
            bias += 0.20
            risk = _combine_risk(risk, RiskTier.MEDIUM)
        if gov_id in {"democracy", "collective_commune"}:
            bias -= 0.20
            risk = _combine_risk(risk, RiskTier.HIGH)
        if gov_id == "anarchic":
            risk = _combine_risk(risk, RiskTier.LOW)
        if tag in favored_tags:
            bias += 0.20
            risk = _combine_risk(risk, RiskTier.MEDIUM)
        if tag in restricted_tags:
            bias -= 0.20
            risk = _combine_risk(risk, RiskTier.HIGH)
    elif tag == "counterfeit":
        if bribery > 60:
            bias += 0.10
            risk = _combine_risk(risk, RiskTier.MEDIUM)
        if enforcement > 70:
            bias -= 0.30
            risk = _combine_risk(risk, RiskTier.HIGH)
        if regulation > 70:
            bias -= 0.20
            risk = _combine_risk(risk, RiskTier.HIGH)
        if gov_id == "anarchic":
            risk = _combine_risk(risk, RiskTier.LOW)
    elif tag == "stolen":
        if bribery > 60:
            bias += 0.10
            risk = _combine_risk(risk, RiskTier.HIGH)
        if enforcement > 70:
            bias -= 0.30
            risk = _combine_risk(risk, RiskTier.SEVERE)
        if tolerance > 70:
            risk = _combine_risk(risk, RiskTier.MEDIUM)
    elif tag == "propaganda":
        if tag in favored_tags:
            bias += 0.20
            risk = _combine_risk(risk, RiskTier.LOW)
        if tag in restricted_tags:
            bias -= 0.20
            risk = _combine_risk(risk, RiskTier.HIGH)
        if regulation > 70:
            bias -= 0.10
            risk = _combine_risk(risk, RiskTier.MEDIUM)
    elif tag == "hazardous":
        if regulation > 70:
            bias -= 0.20
            risk = _combine_risk(risk, RiskTier.HIGH)
        if enforcement > 70:
            bias -= 0.10
            risk = _combine_risk(risk, RiskTier.MEDIUM)
        if gov_id == "anarchic":
            risk = _combine_risk(risk, RiskTier.LOW)
    elif tag == "cybernetic":
        if "technological" in favored_tags:
            bias += 0.20
            risk = _combine_risk(risk, RiskTier.MEDIUM)
        if gov_id == "theocracy":
            bias -= 0.20
            risk = _combine_risk(risk, RiskTier.HIGH)
        if gov_id == "anarchic":
            risk = _combine_risk(risk, RiskTier.LOW)

    return bias, risk


def _category_pressure_multiplier(category_role: str) -> float:
    return CATEGORY_ROLE_MULT[category_role]


def _ideal_price_without_substitute(
    *,
    base_price: float,
    category_role: str,
    scarcity_modifier: float,
    tag_bias: float,
    government_bias: float,
) -> float:
    price = base_price
    price *= _category_pressure_multiplier(category_role)
    price *= scarcity_modifier
    price *= 1.0 + tag_bias
    price *= 1.0 + government_bias
    return price


def _stable_seed(world_seed: int, system_id: str, sku: str) -> int:
    value = world_seed
    for part in (system_id, sku):
        for char in part:
            value = (value * 31 + ord(char)) % (2**32)
    return value


def _clamp(value: float, minimum: float, maximum: float) -> float:
    return max(minimum, min(value, maximum))


def _salvage_floor(base_price: float) -> float:
    return max(1.0, float(round(base_price * 0.10)))


def _category_role(market: Market, category_id: str) -> str:
    category = market.categories.get(category_id)
    if category is None:
        raise ValueError(f"Category {category_id} not present in market.")
    if category.produced:
        return "produced"
    if category.neutral:
        return "neutral"
    if category.consumed:
        return "consumed"
    raise ValueError(f"Category {category_id} has no role assignments.")


def _log_pricing(
    logger: Logger,
    turn: int,
    system_id: str,
    sku: str,
    action: str,
    breakdown: PricingBreakdown,
) -> None:
    logger.log(
        turn=turn,
        action="price_quote",
        state_change=(
            f"system_id={system_id} sku={sku} action={action} "
            f"base={breakdown.base_price:.2f} role={breakdown.category_role} "
            f"substitute={breakdown.substitute} discount={breakdown.substitute_discount:.2f} "
            f"tags={breakdown.tags} tag_bias={breakdown.tag_bias:.2f} "
            f"skipped_tags={breakdown.skipped_tags} interpreted_tags={breakdown.interpreted_tags} "
            f"gov_bias={breakdown.government_bias:.2f} scarcity={breakdown.scarcity_modifier:.2f} "
            f"final={breakdown.final_price:.2f} legality={breakdown.legality.value} "
            f"risk={breakdown.risk_tier.value}"
        ),
    )
