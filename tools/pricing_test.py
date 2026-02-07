import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"
sys.path.insert(0, str(SRC_ROOT))

from data_catalog import DataCatalog, Good  # noqa: E402
from government_registry import GovernmentRegistry  # noqa: E402
from market import Market, MarketCategory, MarketGood  # noqa: E402
from market_pricing import price_transaction, resolve_substitute_discount  # noqa: E402


def main() -> None:
    tags = {}
    goods = [
        Good(
            sku="basic_rations",
            name="Basic Rations",
            category="FOOD",
            base_price=100,
            tags=[],
            possible_tag=None,
        ),
        Good(
            sku="fresh_produce",
            name="Fresh Produce",
            category="FOOD",
            base_price=100,
            tags=[],
            possible_tag=None,
        ),
    ]
    catalog = DataCatalog(tags=tags, goods=goods, economies={})
    government = GovernmentRegistry.from_file(PROJECT_ROOT / "data" / "governments.json").get_government(
        "anarchic"
    )

    listed = MarketGood(
        sku="basic_rations",
        name="Basic Rations",
        category="FOOD",
        base_price=100,
        tags=(),
    )
    market = Market(
        categories={
            "FOOD": MarketCategory(
                produced=(listed,),
                consumed=(),
                neutral=(),
            )
        },
        primary_economy="trade",
        secondary_economies=(),
    )

    buy = price_transaction(
        catalog=catalog,
        market=market,
        government=government,
        sku="basic_rations",
        action="buy",
        world_seed=12345,
        system_id="SYS-TEST",
    )
    assert buy.breakdown.substitute is False
    assert buy.final_price == 80.0

    discount = resolve_substitute_discount(12345, "SYS-TEST", "fresh_produce")
    sell = price_transaction(
        catalog=catalog,
        market=market,
        government=government,
        sku="fresh_produce",
        action="sell",
        world_seed=12345,
        system_id="SYS-TEST",
    )
    assert sell.breakdown.substitute is True
    assert -0.55 <= discount <= -0.40
    expected = 100 * 0.8 * (1 + discount)
    assert abs(sell.final_price - expected) < 1e-6
    assert sell.final_price <= 80.0
    assert sell.final_price >= 10.0

    _log_market(market)
    _log_pricing("buy", "basic_rations", buy)
    _log_pricing("sell", "fresh_produce", sell)
    print("pricing_test: ok")


def _log_market(market: Market) -> None:
    print("market_test: sample market")
    for category_id, category in market.categories.items():
        produced = [good.sku for good in category.produced]
        consumed = [good.sku for good in category.consumed]
        neutral = [good.sku for good in category.neutral]
        print(f"  {category_id} produced={produced} consumed={consumed} neutral={neutral}")


def _log_pricing(action: str, sku: str, pricing) -> None:
    breakdown = pricing.breakdown
    print(f"pricing_test: {action} sku={sku}")
    print(f"  base_price={breakdown.base_price:.2f}")
    print(f"  category_role={breakdown.category_role}")
    print(f"  substitute={breakdown.substitute} discount={breakdown.substitute_discount:.2f}")
    print(f"  tags={breakdown.tags}")
    print(f"  tag_bias={breakdown.tag_bias:.2f}")
    print(f"  government_bias={breakdown.government_bias:.2f}")
    print(f"  scarcity_modifier={breakdown.scarcity_modifier:.2f}")
    print(f"  final_price={breakdown.final_price:.2f}")
    print(f"  legality={breakdown.legality.value} risk={breakdown.risk_tier.value}")


if __name__ == "__main__":
    main()
