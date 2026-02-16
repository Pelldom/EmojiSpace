import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"
sys.path.insert(0, str(SRC_ROOT))

from data_catalog import DataCatalog, Good  # noqa: E402
from government_law_engine import GovernmentPolicyResult, LegalityStatus, RiskTier  # noqa: E402
from government_type import GovernmentType  # noqa: E402
from market import Market, MarketCategory, MarketGood  # noqa: E402
from market_pricing import price_transaction  # noqa: E402
from world_state_engine import WorldStateEngine  # noqa: E402


def _fixtures() -> tuple[DataCatalog, Market, GovernmentType, GovernmentPolicyResult]:
    good = Good(
        sku="basic_rations",
        name="Rations",
        category="food",
        base_price=100,
        tags=[],
        possible_tag=None,
    )
    catalog = DataCatalog(tags={}, goods=[good], economies={})
    market = Market(
        categories={
            "food": MarketCategory(
                produced=(
                    MarketGood(
                        sku="basic_rations",
                        name="Rations",
                        category="food",
                        base_price=100,
                        tags=(),
                    ),
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


def _price(*, world_state_engine=None, scarcity_modifier: float = 1.0):
    catalog, market, government, policy = _fixtures()
    return price_transaction(
        catalog=catalog,
        market=market,
        government=government,
        policy=policy,
        sku="basic_rations",
        action="buy",
        world_seed=101,
        system_id="SYS-1",
        scarcity_modifier=scarcity_modifier,
        world_state_engine=world_state_engine,
    )


def test_no_world_state_pricing_unchanged_baseline() -> None:
    baseline = _price()
    no_ws = _price(world_state_engine=None)
    assert no_ws.final_price == baseline.final_price
    assert no_ws.breakdown.world_state_price_bias_percent == 0
    assert no_ws.breakdown.world_state_demand_bias_percent == 0
    assert no_ws.breakdown.world_state_availability_delta == 0


def test_world_state_price_bias_increases_price_deterministically() -> None:
    ws = WorldStateEngine()
    ws.register_system("SYS-1")
    ws.active_modifiers_by_system["SYS-1"] = [
        {
            "domain": "goods",
            "target_type": "ALL",
            "target_id": None,
            "modifier_type": "price_bias_percent",
            "modifier_value": 10,
            "source_type": "event",
            "source_id": "E-1",
        }
    ]
    result = _price(world_state_engine=ws, scarcity_modifier=1.0)
    assert result.final_price == 88.0  # base(100) * produced(0.8) * (1+0.10)
    assert result.breakdown.world_state_price_bias_percent == 10


def test_no_upper_clamp_on_final_multiplier() -> None:
    ws = WorldStateEngine()
    ws.register_system("SYS-1")
    ws.active_modifiers_by_system["SYS-1"] = [
        {
            "domain": "goods",
            "target_type": "ALL",
            "target_id": None,
            "modifier_type": "price_bias_percent",
            "modifier_value": 999,  # capped by resolver to +40
            "source_type": "event",
            "source_id": "E-1",
        },
        {
            "domain": "goods",
            "target_type": "ALL",
            "target_id": None,
            "modifier_type": "availability_delta",
            "modifier_value": 999,  # capped by resolver to +3
            "source_type": "event",
            "source_id": "E-2",
        },
    ]
    result = _price(world_state_engine=ws, scarcity_modifier=2.0)
    assert result.final_price > 150.0


def test_final_multiplier_never_negative() -> None:
    result = _price(world_state_engine=None, scarcity_modifier=-5.0)
    assert result.final_price == 0.0
