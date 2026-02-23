import sys
from pathlib import Path
import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"
sys.path.insert(0, str(SRC_ROOT))

from data_catalog import DataCatalog, Good  # noqa: E402
from government_law_engine import Commodity, GovernmentLawEngine, GovernmentPolicyResult, LegalityStatus, RiskTier  # noqa: E402
from government_type import GovernmentType  # noqa: E402
from market import Market, MarketCategory, MarketGood  # noqa: E402
from market_pricing import price_transaction  # noqa: E402


class _NullLogger:
    def log(self, **kwargs):  # noqa: ANN003
        return None


class _Registry:
    def __init__(self, government: GovernmentType) -> None:
        self._government = government

    def get_government(self, government_id: str) -> GovernmentType:
        if government_id != self._government.id:
            raise KeyError(government_id)
        return self._government


def _government() -> GovernmentType:
    return GovernmentType(
        id="gov",
        name="Gov",
        description="test",
        regulation_level=50,
        enforcement_strength=50,
        penalty_severity=50,
        tolerance_bias=50,
        bribery_susceptibility=50,
        ideological_modifiers={"favored_tags": [], "restricted_tags": ["weaponized"]},
        illegal_goods=[],
    )


def _policy() -> GovernmentPolicyResult:
    return GovernmentPolicyResult(
        legality_state=LegalityStatus.LEGAL,
        risk_tier=RiskTier.LOW,
        consumed_tags=[],
    )


def _catalog() -> DataCatalog:
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
            sku="counterfeit_food",
            name="Counterfeit Food",
            category="food",
            base_price=100,
            tags=["counterfeit"],
            possible_tag=None,
        ),
        Good(
            sku="weapon_food",
            name="Weapon Food",
            category="food",
            base_price=100,
            tags=["weaponized"],
            possible_tag=None,
        ),
        Good(
            sku="lux_weapon_food",
            name="Lux Weapon Food",
            category="food",
            base_price=100,
            tags=["luxury", "weaponized"],
            possible_tag=None,
        ),
        Good(
            sku="alt_food",
            name="Alt Food",
            category="food",
            base_price=100,
            tags=["luxury"],
            possible_tag=None,
        ),
    ]
    return DataCatalog(tags={}, goods=goods, economies={})


def _market_with_skus(*skus: str) -> Market:
    produced = tuple(
        MarketGood(
            sku=sku,
            name=sku,
            category="food",
            base_price=100,
            tags=tuple(),
        )
        for sku in skus
    )
    return Market(
        categories={
            "food": MarketCategory(
                produced=produced,
                consumed=(),
                neutral=(),
            )
        },
        primary_economy="trade",
        secondary_economies=(),
    )


def _price(market: Market, sku: str, action: str) -> float:
    return price_transaction(
        catalog=_catalog(),
        market=market,
        government=_government(),
        policy=_policy(),
        sku=sku,
        action=action,
        world_seed=101,
        system_id="SYS-1",
        scarcity_modifier=1.0,
    ).final_price


def test_luxury_modifier_increases_price_by_30_percent() -> None:
    market = _market_with_skus("base_food", "lux_food")
    base = _price(market, "base_food", "buy")
    luxury = _price(market, "lux_food", "buy")
    assert luxury == base * 1.30


def test_counterfeit_modifier_decreases_price_by_30_percent() -> None:
    market = _market_with_skus("base_food", "counterfeit_food")
    base = _price(market, "base_food", "buy")
    counterfeit = _price(market, "counterfeit_food", "buy")
    assert counterfeit == pytest.approx(base * 0.70)


def test_weaponized_modifier_increases_price_by_50_percent() -> None:
    market = _market_with_skus("base_food", "weapon_food")
    base = _price(market, "base_food", "buy")
    weaponized = _price(market, "weapon_food", "buy")
    assert weaponized == base * 1.50


def test_tag_modifiers_stack_additively() -> None:
    market = _market_with_skus("base_food", "lux_weapon_food")
    base = _price(market, "base_food", "buy")
    stacked = _price(market, "lux_weapon_food", "buy")
    assert stacked == base * 1.80


def test_substitution_buy_applies_substitution_discount() -> None:
    exact_market = _market_with_skus("alt_food")
    substitute_market = _market_with_skus("base_food")
    exact = _price(exact_market, "alt_food", "buy")
    substitute = _price(substitute_market, "alt_food", "buy")
    assert substitute < exact


def test_substitution_sell_applies_substitution_discount() -> None:
    exact_market = _market_with_skus("alt_food")
    substitute_market = _market_with_skus("base_food")
    exact = _price(exact_market, "alt_food", "sell")
    substitute = _price(substitute_market, "alt_food", "sell")
    assert substitute < exact


def test_legality_logic_unchanged() -> None:
    government = _government()
    law_engine = GovernmentLawEngine(registry=_Registry(government), logger=_NullLogger(), seed=1)
    policy = law_engine.evaluate_policy(
        government_id=government.id,
        commodity=Commodity(commodity_id="weapon_food", tags={"weaponized"}),
        action="buy",
        turn=1,
    )
    assert policy.legality_state == LegalityStatus.RESTRICTED
