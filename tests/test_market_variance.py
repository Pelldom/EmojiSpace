import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"
sys.path.insert(0, str(SRC_ROOT))

from data_catalog import DataCatalog, Good  # noqa: E402
from government_law_engine import GovernmentPolicyResult, LegalityStatus, RiskTier  # noqa: E402
from government_type import GovernmentType  # noqa: E402
from market import Market, MarketCategory, MarketGood  # noqa: E402
from market_pricing import _resolve_market_variance, price_transaction  # noqa: E402


def _fixtures() -> tuple[DataCatalog, Market, GovernmentType, GovernmentPolicyResult]:
    goods = [
        Good(sku="base_food", name="Base Food", category="food", base_price=100, tags=[], possible_tag=None),
        Good(
            sku="lux_food",
            name="Luxury Food",
            category="food",
            base_price=100,
            tags=["luxury"],
            possible_tag=None,
        ),
        Good(
            sku="alt_food",
            name="Alt Food",
            category="food",
            base_price=100,
            tags=[],
            possible_tag=None,
        ),
    ]
    catalog = DataCatalog(tags={}, goods=goods, economies={})
    market = Market(
        categories={
            "food": MarketCategory(
                produced=(
                    MarketGood(sku="base_food", name="Base Food", category="food", base_price=100, tags=()),
                ),
                consumed=(),
                neutral=(),
            )
        },
        primary_economy="trade",
        secondary_economies=(),
    )
    government = GovernmentType(
        id="gov",
        name="Gov",
        description="test",
        regulation_level=50,
        enforcement_strength=50,
        penalty_severity=50,
        tolerance_bias=50,
        bribery_susceptibility=50,
        ideological_modifiers={"favored_tags": [], "restricted_tags": []},
        illegal_goods=[],
    )
    policy = GovernmentPolicyResult(
        legality_state=LegalityStatus.LEGAL,
        risk_tier=RiskTier.LOW,
        consumed_tags=[],
    )
    return catalog, market, government, policy


def _price(*, sku: str, action: str, destination_id: str | None) -> float:
    catalog, market, government, policy = _fixtures()
    return price_transaction(
        catalog=catalog,
        market=market,
        government=government,
        policy=policy,
        sku=sku,
        action=action,
        world_seed=12345,
        system_id="SYS-001",
        destination_id=destination_id,
        scarcity_modifier=1.0,
    ).final_price


def test_market_variance_deterministic_for_same_inputs() -> None:
    first = _resolve_market_variance(12345, "SYS-001", "SYS-001-DST-01")
    second = _resolve_market_variance(12345, "SYS-001", "SYS-001-DST-01")
    assert first == second


def test_market_variance_differs_for_different_destinations() -> None:
    left = _resolve_market_variance(12345, "SYS-001", "SYS-001-DST-01")
    right = _resolve_market_variance(12345, "SYS-001", "SYS-001-DST-02")
    assert left != right


def test_market_variance_multiplier_range() -> None:
    value = _resolve_market_variance(12345, "SYS-001", "SYS-001-DST-01")
    assert 0.95 <= value <= 1.05


def test_buy_and_sell_use_same_variance_for_same_destination() -> None:
    destination_id = "SYS-001-DST-01"
    baseline_buy = _price(sku="base_food", action="buy", destination_id=None)
    baseline_sell = _price(sku="base_food", action="sell", destination_id=None)
    varied_buy = _price(sku="base_food", action="buy", destination_id=destination_id)
    varied_sell = _price(sku="base_food", action="sell", destination_id=destination_id)
    buy_ratio = varied_buy / baseline_buy
    sell_ratio = varied_sell / baseline_sell
    assert buy_ratio == pytest.approx(sell_ratio)


def test_variance_applies_after_tag_modifiers() -> None:
    destination_id = "SYS-001-DST-01"
    no_variance = _price(sku="lux_food", action="buy", destination_id=None)
    variance = _resolve_market_variance(12345, "SYS-001", destination_id)
    with_variance = _price(sku="lux_food", action="buy", destination_id=destination_id)
    assert with_variance == pytest.approx(no_variance * variance)
