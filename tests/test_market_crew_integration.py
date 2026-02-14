import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"
sys.path.insert(0, str(SRC_ROOT))

from data_catalog import DataCatalog, Good, Tag  # noqa: E402
from government_law_engine import GovernmentPolicyResult, LegalityStatus, RiskTier  # noqa: E402
from government_type import GovernmentType  # noqa: E402
from market import Market, MarketCategory, MarketGood  # noqa: E402
from market_pricing import price_transaction  # noqa: E402
from npc_entity import NPCEntity, NPCPersistenceTier  # noqa: E402
from ship_entity import ShipEntity  # noqa: E402


def _crew(npc_id: str, role: str, tags: list[str] | None = None) -> NPCEntity:
    return NPCEntity(
        npc_id=npc_id,
        is_crew=True,
        crew_role_id=role,
        crew_tags=list(tags or []),
        persistence_tier=NPCPersistenceTier.TIER_2,
    )


def _fixtures() -> tuple[DataCatalog, Market, GovernmentType, GovernmentPolicyResult]:
    tags = {"luxury": Tag(tag_id="luxury", description="luxury")}
    good = Good(
        sku="luxury_basic_rations",
        name="Rations",
        category="food",
        base_price=100,
        tags=["luxury"],
        possible_tag=None,
    )
    catalog = DataCatalog(tags=tags, goods=[good], economies={})
    market = Market(
        categories={
            "food": MarketCategory(
                produced=(
                    MarketGood(
                        sku="luxury_basic_rations",
                        name="Rations",
                        category="food",
                        base_price=100,
                        tags=("luxury",),
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


def _price(action: str, ship: ShipEntity | None) -> float:
    catalog, market, government, policy = _fixtures()
    result = price_transaction(
        catalog=catalog,
        market=market,
        government=government,
        policy=policy,
        sku="luxury_basic_rations",
        action=action,
        world_seed=101,
        system_id="SYS-1",
        scarcity_modifier=1.0,
        ship=ship,
    )
    return result.final_price


def test_buy_no_crew_unchanged() -> None:
    baseline = _price("buy", None)
    no_crew = _price("buy", ShipEntity())
    assert no_crew == baseline


def test_sell_no_crew_unchanged() -> None:
    baseline = _price("sell", None)
    no_crew = _price("sell", ShipEntity())
    assert no_crew == baseline


def test_broker_role_applies() -> None:
    ship = ShipEntity(crew=[_crew("NPC-1", role="broker")])
    base_buy = _price("buy", None)
    base_sell = _price("sell", None)
    mod_buy = _price("buy", ship)
    mod_sell = _price("sell", ship)
    assert mod_buy == round(base_buy * 0.90)
    assert mod_sell == round(base_sell * 1.10)


def test_tag_buy_modifier_applies() -> None:
    ship = ShipEntity(crew=[_crew("NPC-1", role="pilot", tags=["crew:bargain_hunter"])])
    base_buy = _price("buy", None)
    mod_buy = _price("buy", ship)
    assert mod_buy == round(base_buy * 0.95)


def test_tag_sell_modifier_applies() -> None:
    ship = ShipEntity(crew=[_crew("NPC-1", role="pilot", tags=["crew:haggler"])])
    base_sell = _price("sell", None)
    mod_sell = _price("sell", ship)
    assert mod_sell == round(base_sell * 1.05)


def test_blacklisted_increases_buy() -> None:
    ship = ShipEntity(crew=[_crew("NPC-1", role="pilot", tags=["crew:blacklisted"])])
    base_buy = _price("buy", None)
    mod_buy = _price("buy", ship)
    assert mod_buy == round(base_buy * 1.05)


def test_multiplier_stacking() -> None:
    ship = ShipEntity(
        crew=[
            _crew("NPC-1", role="broker"),
            _crew("NPC-2", role="pilot", tags=["crew:bargain_hunter"]),
        ]
    )
    base_buy = _price("buy", None)
    mod_buy = _price("buy", ship)
    assert mod_buy == round(base_buy * 0.90 * 0.95)
