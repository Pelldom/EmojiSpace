from dataclasses import dataclass

from data_catalog import DataCatalog
from economy_engine import EconomyEngine, TradeAction
from government_law_engine import (
    Commodity,
    GovernmentLawEngine,
    InspectionContext,
    PlayerInspectionResponse,
)
from government_registry import GovernmentRegistry
from market_pricing import PricingResult, price_transaction
from logger import Logger
from player_state import PlayerState
from time_engine import TimeEngine
from world_generator import Sector


@dataclass(frozen=True)
class MoveAction:
    target_system_id: str


@dataclass(frozen=True)
class BuyAction:
    sku: str


@dataclass(frozen=True)
class SellAction:
    sku: str


class TurnLoop:
    def __init__(
        self,
        time_engine: TimeEngine,
        sector: Sector,
        player_state: PlayerState,
        logger: Logger,
        economy_engine: EconomyEngine,
        law_engine: GovernmentLawEngine,
        catalog: DataCatalog,
        government_registry: GovernmentRegistry,
        world_seed: int,
    ) -> None:
        self._time_engine = time_engine
        self._sector = sector
        self._player_state = player_state
        self._logger = logger
        self._economy = economy_engine
        self._law_engine = law_engine
        self._catalog = catalog
        self._government_registry = government_registry
        self._world_seed = world_seed

    def execute_move(self, action: MoveAction) -> None:
        if self._sector.get_system(action.target_system_id) is None:
            turn = self._time_engine.advance()
            self._economy.advance_turn(turn=turn)
            self._logger.log(
                turn=turn,
                action="move",
                state_change=f"failed invalid_target={action.target_system_id}",
            )
            return

        previous = self._player_state.move_to(action.target_system_id)
        turn = self._time_engine.advance()
        self._economy.advance_turn(turn=turn)
        self._inspect_transport(action.target_system_id, turn)
        self._logger.log(
            turn=turn,
            action="move",
            state_change=f"from={previous} to={action.target_system_id}",
        )

    def execute_buy(self, action: BuyAction) -> None:
        system_id = self._player_state.location_system_id
        market_good = self._market_good(system_id, action.sku)
        if market_good is None:
            turn = self._time_engine.advance()
            self._economy.advance_turn(turn=turn)
            self._logger.log(
                turn=turn,
                action="buy",
                state_change=f"failed sku_not_in_market system_id={system_id} sku={action.sku}",
            )
            return
        category_id = market_good.category
        self._player_state.buy(action.sku)
        turn = self._time_engine.advance()
        self._economy.advance_turn(
            turn=turn,
            trade_action=TradeAction(
                system_id=system_id,
                category_id=category_id,
                delta=-1,
                cause="player_buy",
            ),
        )
        pricing = self._price_quote(system_id, action.sku, "buy", turn)
        self._inspect_trade(system_id, action.sku, "buy", turn)
        self._logger.log(
            turn=turn,
            action="buy",
            state_change=f"system_id={system_id} sku={action.sku} category_id={category_id}",
        )
        if pricing is not None:
            self._log_pricing_transaction(system_id, action.sku, "buy", pricing)

    def execute_sell(self, action: SellAction) -> None:
        system_id = self._player_state.location_system_id
        if not self._player_state.sell(action.sku):
            turn = self._time_engine.advance()
            self._economy.advance_turn(turn=turn)
            self._logger.log(
                turn=turn,
                action="sell",
                state_change=f"failed no_holdings system_id={system_id} sku={action.sku}",
            )
            return
        category_id = self._sku_category(action.sku)
        if category_id is None:
            turn = self._time_engine.advance()
            self._economy.advance_turn(turn=turn)
            self._logger.log(
                turn=turn,
                action="sell",
                state_change=f"failed unknown_sku system_id={system_id} sku={action.sku}",
            )
            return
        if not self._category_present(system_id, category_id):
            turn = self._time_engine.advance()
            self._economy.advance_turn(turn=turn)
            self._logger.log(
                turn=turn,
                action="sell",
                state_change=f"failed category_not_present system_id={system_id} sku={action.sku} category_id={category_id}",
            )
            return
        turn = self._time_engine.advance()
        self._economy.advance_turn(
            turn=turn,
            trade_action=TradeAction(
                system_id=system_id,
                category_id=category_id,
                delta=1,
                cause="player_sell",
            ),
        )
        pricing = self._price_quote(system_id, action.sku, "sell", turn)
        self._inspect_trade(system_id, action.sku, "sell", turn)
        self._logger.log(
            turn=turn,
            action="sell",
            state_change=f"system_id={system_id} sku={action.sku} category_id={category_id}",
        )
        if pricing is not None:
            self._log_pricing_transaction(system_id, action.sku, "sell", pricing)

    def _inspect_trade(self, system_id: str, sku: str, action: str, turn: int) -> None:
        system = self._sector.get_system(system_id)
        if system is None:
            return
        government_id = system.attributes.get("government_id")
        population_level = system.attributes.get("population_level", 3)
        tags = self._sku_tags(system_id, sku)
        commodity = Commodity(commodity_id=sku, tags=set(tags))
        triggered = self._law_engine.inspection_check(
            system_id=system_id,
            population_level=population_level,
            government_id=government_id,
            commodity=commodity,
            action=action,
            turn=turn,
        )
        if not triggered:
            return
        response = PlayerInspectionResponse.SUBMIT
        context = InspectionContext.MARKET if action in ("buy", "sell") else InspectionContext.TRANSPORT
        outcome = self._law_engine.resolve_enforcement(
            system_id=system_id,
            government_id=government_id,
            commodity=commodity,
            action=action,
            context=context,
            response=response,
            turn=turn,
        )
        if outcome.confiscated < 0:
            confiscated = self._player_state.confiscate(sku, None)
        else:
            confiscated = self._player_state.confiscate(sku, outcome.confiscated)
        if confiscated:
            self._logger.log(
                turn=turn,
                action="confiscation",
                state_change=(
                    f"system_id={system_id} sku={sku} amount={confiscated}"
                ),
            )
        if outcome.reputation_delta != 0:
            self._player_state.adjust_reputation(outcome.reputation_delta)
            self._logger.log(
                turn=turn,
                action="reputation_change",
                state_change=f"delta={outcome.reputation_delta} total={self._player_state.reputation()}",
            )

    def _inspect_transport(self, system_id: str, turn: int) -> None:
        holdings = self._player_state.holdings_snapshot()
        for sku, count in holdings.items():
            if count <= 0:
                continue
            self._inspect_trade(system_id, sku, "transport", turn)

    def _price_quote(self, system_id: str, sku: str, action: str, turn: int) -> PricingResult | None:
        system = self._sector.get_system(system_id)
        if system is None:
            return
        market = system.attributes.get("market")
        if market is None:
            return
        government_id = system.attributes.get("government_id")
        government = self._government_registry.get_government(government_id)
        category_id = self._sku_category(sku)
        if category_id is None:
            return
        scarcity = self._economy.scarcity_modifier(system_id, category_id)
        return price_transaction(
            catalog=self._catalog,
            market=market,
            government=government,
            sku=sku,
            action=action,
            world_seed=self._world_seed,
            system_id=system_id,
            scarcity_modifier=scarcity,
            logger=self._logger,
            turn=turn,
        )

    def _log_pricing_transaction(self, system_id: str, sku: str, action: str, pricing: PricingResult) -> None:
        breakdown = pricing.breakdown
        self._logger.log(
            turn=self._time_engine.current_turn,
            action="price_transaction",
            state_change=(
                f"system_id={system_id} sku={sku} action={action} "
                f"base={breakdown.base_price:.2f} role={breakdown.category_role} "
                f"substitute={breakdown.substitute} discount={breakdown.substitute_discount:.2f} "
                f"tags={breakdown.tags} tag_bias={breakdown.tag_bias:.2f} "
                f"gov_bias={breakdown.government_bias:.2f} scarcity={breakdown.scarcity_modifier:.2f} "
                f"final={breakdown.final_price:.2f} legality={breakdown.legality.value} "
                f"risk={breakdown.risk_tier.value}"
            ),
        )

    def _market_good(self, system_id: str, sku: str) -> object | None:
        system = self._sector.get_system(system_id)
        if system is None:
            return None
        market = system.attributes.get("market")
        if market is None:
            return None
        for category in market.categories.values():
            for good in category.produced + category.consumed + category.neutral:
                if good.sku == sku:
                    return good
        return None

    def _sku_category(self, sku: str) -> str | None:
        market_good = self._market_good(self._player_state.location_system_id, sku)
        if market_good is not None:
            return market_good.category
        try:
            return self._catalog.good_by_sku(sku).category
        except KeyError:
            base_sku = self._strip_possible_tag(sku)
            if base_sku is None:
                return None
            try:
                return self._catalog.good_by_sku(base_sku).category
            except KeyError:
                return None

    def _sku_tags(self, system_id: str, sku: str) -> list[str]:
        market_good = self._market_good(system_id, sku)
        if market_good is not None:
            return list(market_good.tags)
        try:
            return list(self._catalog.good_by_sku(sku).tags)
        except KeyError:
            base_sku = self._strip_possible_tag(sku)
            if base_sku is None:
                return []
            try:
                base_tags = list(self._catalog.good_by_sku(base_sku).tags)
            except KeyError:
                return []
            prefix = sku.split("_", 1)[0]
            return base_tags + [prefix]

    @staticmethod
    def _strip_possible_tag(sku: str) -> str | None:
        possible_tags = {
            "luxury",
            "weaponized",
            "counterfeit",
            "propaganda",
            "stolen",
            "hazardous",
            "cybernetic",
        }
        if "_" not in sku:
            return None
        prefix, remainder = sku.split("_", 1)
        if prefix in possible_tags and remainder:
            return remainder
        return None

    def _category_present(self, system_id: str, category_id: str) -> bool:
        system = self._sector.get_system(system_id)
        if system is None:
            return False
        market = system.attributes.get("market")
        if market is None:
            return False
        return category_id in market.categories
