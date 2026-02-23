import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"
sys.path.insert(0, str(SRC_ROOT))

from game_engine import GameEngine  # noqa: E402
from government_type import GovernmentType  # noqa: E402
from market import Market, MarketCategory, MarketGood  # noqa: E402
from world_state_engine import WorldStateEngine  # noqa: E402


def _food_market_with_skus(*skus: str) -> Market:
    produced = tuple(
        MarketGood(
            sku=sku,
            name=sku.replace("_", " ").title(),
            category="FOOD",
            base_price=120,
            tags=("luxury",) if "luxury" in sku else (),
        )
        for sku in skus
    )
    return Market(
        categories={
            "FOOD": MarketCategory(
                produced=produced,
                consumed=(),
                neutral=(),
            )
        },
        primary_economy="trade",
        secondary_economies=(),
    )


def _set_current_destination_market(engine: GameEngine, market: Market) -> object:
    system = engine.sector.get_system(engine.player_state.current_system_id)
    destination = None
    for row in system.destinations:
        if row.destination_id == engine.player_state.current_destination_id:
            destination = row
            break
    object.__setattr__(destination, "market", market)
    return destination


def _sell_quote(engine: GameEngine, destination: object, sku: str) -> dict | None:
    system = engine.sector.get_system(engine.player_state.current_system_id)
    government = engine.government_registry.get_government(system.government_id)
    return engine._market_price_quote(destination=destination, government=government, sku=sku, action="sell")


def _buy_quote(engine: GameEngine, destination: object, sku: str) -> dict | None:
    system = engine.sector.get_system(engine.player_state.current_system_id)
    government = engine.government_registry.get_government(system.government_id)
    return engine._market_price_quote(destination=destination, government=government, sku=sku, action="buy")


def _enter_market_location(engine: GameEngine) -> None:
    destination = engine._current_destination()
    for location in list(getattr(destination, "locations", [])):
        if str(getattr(location, "location_type", "")) == "market":
            result = engine.execute({"type": "enter_location", "location_id": str(location.location_id)})
            assert result.get("ok") is True
            return
    raise AssertionError("No market location available for test")


def _set_luxury_favorable_government(engine: GameEngine) -> None:
    system = engine.sector.get_system(engine.player_state.current_system_id)
    government_id = system.government_id
    current = engine.government_registry.get_government(government_id)
    favorable = GovernmentType(
        id=current.id,
        name=current.name,
        description=current.description,
        regulation_level=current.regulation_level,
        enforcement_strength=current.enforcement_strength,
        penalty_severity=current.penalty_severity,
        tolerance_bias=80,
        bribery_susceptibility=current.bribery_susceptibility,
        ideological_modifiers=current.ideological_modifiers,
        illegal_goods=current.illegal_goods,
    )
    engine.government_registry._governments[government_id] = favorable


def test_variant_of_listed_base_is_sellable_and_premium() -> None:
    engine = GameEngine(world_seed=12345)
    _set_luxury_favorable_government(engine)
    destination = _set_current_destination_market(engine, _food_market_with_skus("fresh_produce"))

    base_quote = _sell_quote(engine, destination, "fresh_produce")
    luxury_quote = _sell_quote(engine, destination, "fresh_produce_luxury")

    assert base_quote is not None
    assert luxury_quote is not None
    assert int(luxury_quote["unit_price"]) > int(base_quote["unit_price"])


def test_base_into_listed_variant_is_sellable_and_discounted() -> None:
    engine = GameEngine(world_seed=12345)
    _set_luxury_favorable_government(engine)
    destination = _set_current_destination_market(engine, _food_market_with_skus("fresh_produce_luxury"))

    luxury_quote = _sell_quote(engine, destination, "fresh_produce_luxury")
    base_quote = _sell_quote(engine, destination, "fresh_produce")

    assert luxury_quote is not None
    assert base_quote is not None
    assert int(base_quote["unit_price"]) < int(luxury_quote["unit_price"])


def test_category_substitution_sellable_but_discounted_vs_own_exact() -> None:
    engine = GameEngine(world_seed=12345)
    _set_luxury_favorable_government(engine)
    destination_sub = _set_current_destination_market(engine, _food_market_with_skus("fresh_produce"))
    substitution_quote = _sell_quote(engine, destination_sub, "nutrient_paste_luxury")
    substitution_base_quote = _sell_quote(engine, destination_sub, "nutrient_paste")

    destination_exact = _set_current_destination_market(engine, _food_market_with_skus("nutrient_paste_luxury"))
    exact_quote = _sell_quote(engine, destination_exact, "nutrient_paste_luxury")

    assert substitution_quote is not None
    assert substitution_base_quote is not None
    assert exact_quote is not None
    assert int(substitution_quote["unit_price"]) < int(exact_quote["unit_price"])
    assert int(substitution_quote["unit_price"]) > int(substitution_base_quote["unit_price"])


def test_category_absent_not_sellable() -> None:
    engine = GameEngine(world_seed=12345)
    ore_market = Market(
        categories={
            "ORE": MarketCategory(
                produced=(
                    MarketGood(
                        sku="iron_ore",
                        name="Iron Ore",
                        category="ORE",
                        base_price=120,
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
    destination = _set_current_destination_market(engine, ore_market)
    quote = _sell_quote(engine, destination, "servitor_units")
    assert quote is None


def test_situations_modifiers_can_push_price_above_base() -> None:
    engine = GameEngine(world_seed=12345)
    destination = _set_current_destination_market(engine, _food_market_with_skus("fresh_produce"))
    ws = WorldStateEngine()
    ws.register_system(engine.player_state.current_system_id)
    ws.active_modifiers_by_system[engine.player_state.current_system_id] = [
        {
            "domain": "goods",
            "target_type": "ALL",
            "target_id": None,
            "modifier_type": "price_bias_percent",
            "modifier_value": 40,
            "source_type": "event",
            "source_id": "E-BOOST",
        },
        {
            "domain": "goods",
            "target_type": "ALL",
            "target_id": None,
            "modifier_type": "availability_delta",
            "modifier_value": 3,
            "source_type": "event",
            "source_id": "E-SCARCITY",
        },
    ]
    import time_engine as time_engine_module

    time_engine_module._world_state_engine = ws
    quote = _sell_quote(engine, destination, "fresh_produce")
    assert quote is not None
    assert int(quote["unit_price"]) > 120


def test_substitution_buy_is_supported_for_category_match() -> None:
    engine = GameEngine(world_seed=12345)
    destination = _set_current_destination_market(engine, _food_market_with_skus("fresh_produce"))
    buy_quote = _buy_quote(engine, destination, "nutrient_paste")
    assert buy_quote is not None

    _enter_market_location(engine)
    engine.player_state.credits = 10_000
    result = engine.execute({"type": "market_buy", "sku_id": "nutrient_paste", "quantity": 1})
    assert result.get("ok") is True
