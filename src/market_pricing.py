from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List
import json
import random

try:
    from crew_modifiers import compute_crew_modifiers
except ModuleNotFoundError:
    from src.crew_modifiers import compute_crew_modifiers

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
    world_state_price_bias_percent: int
    world_state_demand_bias_percent: int
    world_state_availability_delta: int
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


@lru_cache(maxsize=1)
def _goods_pricing_modifiers() -> Dict[str, float]:
    path = Path(__file__).resolve().parents[1] / "data" / "goods_pricing_modifiers.json"
    if not path.exists():
        return {}
    raw = json.loads(path.read_text(encoding="utf-8", errors="replace"))
    if not isinstance(raw, dict):
        return {}
    mapping: Dict[str, float] = {}
    for key, value in raw.items():
        if isinstance(key, str) and isinstance(value, (int, float)):
            mapping[key] = float(value)
    return mapping


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
    destination_id: str | None = None,
    scarcity_modifier: float = 1.0,
    logger: Logger | None = None,
    turn: int = 0,
    ship: Any | None = None,
    world_state_engine: Any | None = None,
    tags_override: List[str] | None = None,
    substitute_override: bool | None = None,
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
    if market_good is None:
        if good.category not in market.categories:
            if action == "buy":
                raise ValueError(f"SKU {sku} not available to buy in system {system_id}.")
            raise ValueError(f"Category {good.category} not present for selling in system {system_id}.")
        substitute = True
    if isinstance(substitute_override, bool):
        substitute = substitute_override

    base_price = float(market_good.base_price) if market_good is not None else float(good.base_price)
    price = base_price

    world_state_price_bias_percent = 0
    world_state_demand_bias_percent = 0
    world_state_availability_delta = 0
    if world_state_engine is not None and system_id:
        entity_views = [
            {
                "entity_id": good.sku,
                "category_id": good.category,
                "tags": _resolved_tags(good, market_good),
            }
        ]
        resolved = world_state_engine.resolve_modifiers_for_entities(
            system_id=system_id,
            domain="goods",
            entity_views=entity_views,
        )
        by_entity = resolved.get("resolved", {})
        row = by_entity.get(good.sku, {})
        world_state_price_bias_percent = int(row.get("price_bias_percent", 0))
        world_state_demand_bias_percent = int(row.get("demand_bias_percent", 0))
        world_state_availability_delta = int(row.get("availability_delta", 0))

    # Step 2: market supply/demand modifier.
    market_scarcity_modifier = float(scarcity_modifier)
    price *= _category_pressure_multiplier(category_role)
    price *= market_scarcity_modifier

    # Step 3: substitution modifier for category substitutions (buy and sell).
    substitute_discount = 0.0
    if substitute:
        substitute_discount = resolve_substitute_discount(world_seed, system_id, sku)
        price *= 1.0 + substitute_discount

    tags = list(tags_override) if isinstance(tags_override, list) else _resolved_tags(good, market_good)
    skipped_tags: List[str] = [tag for tag in tags if tag not in _goods_pricing_modifiers()]
    interpreted_tags = [tag for tag in tags if tag in _goods_pricing_modifiers()]

    # Step 4: goods pricing tag modifiers from pricing data.
    tag_bias = sum(_goods_pricing_modifiers().get(tag, 0.0) for tag in interpreted_tags)
    price *= 1.0 + tag_bias

    # Step 5: government modifier.
    government_bias = 0.0  # TODO(Phase 2.6): Government bias is derived from tag interpretation only.
    price *= 1.0 + government_bias

    # Step 6: situation/world-state modifiers.
    effective_scarcity_modifier = market_scarcity_modifier + float(world_state_availability_delta)
    if market_scarcity_modifier != 0.0:
        price *= effective_scarcity_modifier / market_scarcity_modifier
    else:
        price *= effective_scarcity_modifier
    demand_multiplier = 1.0 + (float(world_state_demand_bias_percent) / 100.0)
    price *= demand_multiplier
    world_state_price_bias = float(world_state_price_bias_percent) / 100.0
    price *= 1.0 + world_state_price_bias

    # Apply deterministic per-destination market variance after all modifiers.
    if isinstance(destination_id, str) and destination_id:
        variance = _resolve_market_variance(world_seed, system_id, destination_id)
        price *= variance

    # Step 7: clamp final multiplier to non-negative only (no upper clamp)
    final_multiplier = 0.0 if base_price == 0 else (price / base_price)
    final_multiplier = max(0.0, final_multiplier)
    price = base_price * final_multiplier

    # Phase 5.6: apply crew multipliers at pricing source of truth only.
    multiplier = 1.0
    if ship is not None:
        crew_mods = compute_crew_modifiers(ship)
        if action == "buy":
            multiplier = float(crew_mods.buy_multiplier)
        elif action == "sell":
            multiplier = float(crew_mods.sell_multiplier)
    if multiplier != 1.0:
        price = round(price * multiplier)

    breakdown = PricingBreakdown(
        base_price=base_price,
        category_role=category_role,
        substitute=substitute,
        substitute_discount=substitute_discount,
        tag_bias=tag_bias,
        government_bias=government_bias,
        scarcity_modifier=effective_scarcity_modifier,
        world_state_price_bias_percent=world_state_price_bias_percent,
        world_state_demand_bias_percent=world_state_demand_bias_percent,
        world_state_availability_delta=world_state_availability_delta,
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


def _resolve_market_variance(world_seed: int, system_id: str, destination_id: str) -> float:
    rng = random.Random(_stable_seed(world_seed, system_id, destination_id, "market_variance"))
    return 1.0 + rng.uniform(-0.05, 0.05)


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
    _ = market_good
    return list(good.tags)


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


def _stable_seed(world_seed: int, *parts: str) -> int:
    value = world_seed
    for part in parts:
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
            f"ws_price_bias={breakdown.world_state_price_bias_percent} "
            f"ws_demand_bias={breakdown.world_state_demand_bias_percent} "
            f"ws_availability_delta={breakdown.world_state_availability_delta} "
            f"final={breakdown.final_price:.2f} legality={breakdown.legality.value} "
            f"risk={breakdown.risk_tier.value}"
        ),
    )


@dataclass(frozen=True)
class EquipmentPricingBreakdown:
    base_price: float
    world_state_price_bias_percent: int
    resale_multiplier: float
    final_price: float
    entity_id: str
    transaction_type: str


def price_hull_transaction(
    *,
    base_price_credits: int,
    hull_id: str,
    system_id: str,
    transaction_type: str,
    world_state_engine: Any | None = None,
    logger: Logger | None = None,
    turn: int = 0,
) -> EquipmentPricingBreakdown:
    """
    Deterministic pricing for hull transactions (buy/sell).
    
    Applies:
    - World state price_bias_percent modifiers (clamped to +/-40%)
    - Base resale multiplier (0.5) for sell transactions
    
    Does NOT apply:
    - Substitute discount
    - Category pressure
    - Goods scarcity
    - Government illegal penalties
    - SKU-specific logic
    """
    if transaction_type not in {"buy", "sell"}:
        raise ValueError(f"transaction_type must be 'buy' or 'sell', got: {transaction_type}")
    
    base_price = float(base_price_credits)
    price = base_price
    
    # Resolve world state modifiers for ships domain
    world_state_price_bias_percent = 0
    if world_state_engine is not None and system_id:
        entity_views = [
            {
                "entity_id": hull_id,
                "category_id": None,
                "tags": [],
            }
        ]
        resolved = world_state_engine.resolve_modifiers_for_entities(
            system_id=system_id,
            domain="ships",
            entity_views=entity_views,
        )
        by_entity = resolved.get("resolved", {})
        row = by_entity.get(hull_id, {})
        world_state_price_bias_percent = int(row.get("price_bias_percent", 0))
        # Clamp to contract caps: +/-40%
        world_state_price_bias_percent = int(_clamp(
            float(world_state_price_bias_percent),
            -40.0,
            40.0
        ))
    
    # Apply world state price bias
    world_state_multiplier = 1.0 + (float(world_state_price_bias_percent) / 100.0)
    price *= world_state_multiplier
    
    # Apply resale multiplier for sell transactions
    resale_multiplier = 1.0
    if transaction_type == "sell":
        resale_multiplier = 0.5
        price *= resale_multiplier
    
    # Clamp to non-negative
    price = max(0.0, price)
    final_price = float(round(price))
    
    breakdown = EquipmentPricingBreakdown(
        base_price=base_price,
        world_state_price_bias_percent=world_state_price_bias_percent,
        resale_multiplier=resale_multiplier,
        final_price=final_price,
        entity_id=hull_id,
        transaction_type=transaction_type,
    )
    
    if logger is not None:
        logger.log(
            turn=turn,
            action="price_hull_transaction",
            state_change=(
                f"hull_id={hull_id} system_id={system_id} transaction_type={transaction_type} "
                f"base={base_price:.2f} ws_bias_percent={world_state_price_bias_percent} "
                f"resale_mult={resale_multiplier:.2f} final={final_price:.2f}"
            ),
        )
    
    return breakdown


def price_module_transaction(
    *,
    base_price_credits: int,
    module_id: str,
    system_id: str,
    transaction_type: str,
    secondary_tags: List[str] | None = None,
    world_state_engine: Any | None = None,
    logger: Logger | None = None,
    turn: int = 0,
) -> EquipmentPricingBreakdown:
    """
    Deterministic pricing for module transactions (buy/sell).
    
    Applies:
    - World state price_bias_percent modifiers (clamped to +/-40%)
    - Base resale multiplier (0.5) for sell transactions
    - Secondary tag resale multipliers (prototype: 1.5x, alien: 2.0x) for sell transactions
    
    Does NOT apply:
    - Substitute discount
    - Category pressure
    - Goods scarcity
    - Government illegal penalties
    - SKU-specific logic
    """
    if transaction_type not in {"buy", "sell"}:
        raise ValueError(f"transaction_type must be 'buy' or 'sell', got: {transaction_type}")
    
    base_price = float(base_price_credits)
    price = base_price
    
    # Resolve world state modifiers for modules domain
    world_state_price_bias_percent = 0
    if world_state_engine is not None and system_id:
        entity_views = [
            {
                "entity_id": module_id,
                "category_id": None,
                "tags": list(secondary_tags or []),
            }
        ]
        resolved = world_state_engine.resolve_modifiers_for_entities(
            system_id=system_id,
            domain="modules",
            entity_views=entity_views,
        )
        by_entity = resolved.get("resolved", {})
        row = by_entity.get(module_id, {})
        world_state_price_bias_percent = int(row.get("price_bias_percent", 0))
        # Clamp to contract caps: +/-40%
        world_state_price_bias_percent = int(_clamp(
            float(world_state_price_bias_percent),
            -40.0,
            40.0
        ))
    
    # Apply world state price bias
    world_state_multiplier = 1.0 + (float(world_state_price_bias_percent) / 100.0)
    price *= world_state_multiplier
    
    # Apply resale multipliers for sell transactions
    resale_multiplier = 1.0
    if transaction_type == "sell":
        resale_multiplier = 0.5  # Base resale multiplier
        
        # Apply secondary tag multipliers multiplicatively
        secondary_tag_set = set(secondary_tags or [])
        if "secondary:prototype" in secondary_tag_set or "prototype" in secondary_tag_set:
            resale_multiplier *= 1.5
        if "secondary:alien" in secondary_tag_set or "alien" in secondary_tag_set:
            resale_multiplier *= 2.0
        
        price *= resale_multiplier
    
    # Clamp to non-negative
    price = max(0.0, price)
    final_price = float(round(price))
    
    breakdown = EquipmentPricingBreakdown(
        base_price=base_price,
        world_state_price_bias_percent=world_state_price_bias_percent,
        resale_multiplier=resale_multiplier,
        final_price=final_price,
        entity_id=module_id,
        transaction_type=transaction_type,
    )
    
    if logger is not None:
        logger.log(
            turn=turn,
            action="price_module_transaction",
            state_change=(
                f"module_id={module_id} system_id={system_id} transaction_type={transaction_type} "
                f"base={base_price:.2f} ws_bias_percent={world_state_price_bias_percent} "
                f"resale_mult={resale_multiplier:.2f} secondary_tags={secondary_tags} "
                f"final={final_price:.2f}"
            ),
        )
    
    return breakdown