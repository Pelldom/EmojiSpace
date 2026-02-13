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
from law_enforcement import (
    CargoSnapshot,
    TriggerType,
    enforcement_checkpoint,
)
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
            self._apply_heat_decay(action.target_system_id, turn)
            self._logger.log(
                turn=turn,
                action="move",
                state_change=f"failed invalid_target={action.target_system_id}",
            )
            return

        previous = self._player_state.current_system_id
        self._player_state.current_system_id = action.target_system_id
        turn = self._time_engine.advance()
        self._economy.advance_turn(turn=turn)
        self._apply_heat_decay(action.target_system_id, turn)
        self._border_checkpoint(action.target_system_id, turn)
        self._inspect_transport(action.target_system_id, turn)
        self._logger.log(
            turn=turn,
            action="move",
            state_change=f"from={previous} to={action.target_system_id}",
        )

    def execute_buy(self, action: BuyAction) -> None:
        system_id = self._player_state.current_system_id
        market_good = self._market_good(system_id, action.sku)
        if market_good is None:
            turn = self._time_engine.advance()
            self._economy.advance_turn(turn=turn)
            self._apply_heat_decay(system_id, turn)
            self._logger.log(
                turn=turn,
                action="buy",
                state_change=f"failed sku_not_in_market system_id={system_id} sku={action.sku}",
            )
            return
        turn = self._time_engine.current_turn
        if self._customs_checkpoint(system_id, turn) is False:
            turn = self._time_engine.advance()
            self._economy.advance_turn(turn=turn)
            self._apply_heat_decay(system_id, turn)
            self._logger.log(
                turn=turn,
                action="market_access_denied",
                state_change=f"system_id={system_id} sku={action.sku}",
            )
            return
        category_id = market_good.category
        self._player_state.cargo_by_ship.setdefault("active", {})
        self._player_state.cargo_by_ship["active"][action.sku] = (
            self._player_state.cargo_by_ship["active"].get(action.sku, 0) + 1
        )
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
        self._apply_heat_decay(system_id, turn)
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
        system_id = self._player_state.current_system_id
        current = self._player_state.cargo_by_ship.get("active", {}).get(action.sku, 0)
        if current <= 0:
            turn = self._time_engine.advance()
            self._economy.advance_turn(turn=turn)
            self._apply_heat_decay(system_id, turn)
            self._logger.log(
                turn=turn,
                action="sell",
                state_change=f"failed no_holdings system_id={system_id} sku={action.sku}",
            )
            return
        self._player_state.cargo_by_ship.setdefault("active", {})
        self._player_state.cargo_by_ship["active"][action.sku] = current - 1
        category_id = self._sku_category(action.sku)
        if category_id is None:
            turn = self._time_engine.advance()
            self._economy.advance_turn(turn=turn)
            self._apply_heat_decay(system_id, turn)
            self._logger.log(
                turn=turn,
                action="sell",
                state_change=f"failed unknown_sku system_id={system_id} sku={action.sku}",
            )
            return
        if not self._category_present(system_id, category_id):
            turn = self._time_engine.advance()
            self._economy.advance_turn(turn=turn)
            self._apply_heat_decay(system_id, turn)
            self._logger.log(
                turn=turn,
                action="sell",
                state_change=f"failed category_not_present system_id={system_id} sku={action.sku} category_id={category_id}",
            )
            return
        turn = self._time_engine.current_turn
        if self._customs_checkpoint(system_id, turn) is False:
            turn = self._time_engine.advance()
            self._economy.advance_turn(turn=turn)
            self._apply_heat_decay(system_id, turn)
            self._logger.log(
                turn=turn,
                action="market_access_denied",
                state_change=f"system_id={system_id} sku={action.sku}",
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
        self._apply_heat_decay(system_id, turn)
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
        confiscated = 0
        if outcome.confiscated < 0:
            current = self._player_state.cargo_by_ship.get("active", {}).get(sku, 0)
            self._player_state.cargo_by_ship.setdefault("active", {})
            self._player_state.cargo_by_ship["active"][sku] = 0
            confiscated = current
        elif outcome.confiscated > 0:
            current = self._player_state.cargo_by_ship.get("active", {}).get(sku, 0)
            take = min(current, outcome.confiscated)
            self._player_state.cargo_by_ship.setdefault("active", {})
            self._player_state.cargo_by_ship["active"][sku] = max(0, current - take)
            confiscated = take
        if confiscated:
            self._logger.log(
                turn=turn,
                action="confiscation",
                state_change=(
                    f"system_id={system_id} sku={sku} amount={confiscated}"
                ),
            )
        if outcome.reputation_delta != 0:
            current_rep = self._player_state.reputation_by_system.get(system_id, 50)
            self._player_state.reputation_by_system[system_id] = current_rep + outcome.reputation_delta
            self._logger.log(
                turn=turn,
                action="reputation_change",
                state_change=f"delta={outcome.reputation_delta} total={self._player_state.reputation_by_system[system_id]}",
            )

    def _inspect_transport(self, system_id: str, turn: int) -> None:
        holdings = dict(self._player_state.cargo_by_ship.get("active", {}))
        for sku, count in holdings.items():
            if count <= 0:
                continue
            self._inspect_trade(system_id, sku, "transport", turn)

    def _border_checkpoint(self, system_id: str, turn: int) -> None:
        system = self._sector.get_system(system_id)
        if system is None:
            return
        market = system.attributes.get("market")
        if market is None:
            return
        government_id = system.attributes.get("government_id")
        government = self._government_registry.get_government(government_id)
        illegal_present, policies = self._cargo_policy(system_id, check_restricted=False, turn=turn)
        if not illegal_present:
            return
        event = enforcement_checkpoint(
            system_id=system_id,
            trigger_type=TriggerType.BORDER,
            government=government,
            policy_results=policies,
            player=self._player_state,
            world_seed=self._world_seed,
            turn=turn,
            cargo_snapshot=CargoSnapshot(
                illegal_present=illegal_present,
                restricted_unlicensed_present=False,
            ),
            logger=self._logger,
        )
        if event is not None and event.arrested:
            return

    def _customs_checkpoint(self, system_id: str, turn: int) -> bool | None:
        system = self._sector.get_system(system_id)
        if system is None:
            return None
        market = system.attributes.get("market")
        if market is None:
            return None
        government_id = system.attributes.get("government_id")
        government = self._government_registry.get_government(government_id)
        illegal_present, policies = self._cargo_policy(system_id, check_restricted=True, turn=turn)
        restricted_unlicensed = self._restricted_unlicensed_present(system_id, policies)
        if not illegal_present and not restricted_unlicensed:
            return True
        outcome = enforcement_checkpoint(
            system_id=system_id,
            trigger_type=TriggerType.CUSTOMS,
            government=government,
            policy_results=policies,
            player=self._player_state,
            world_seed=self._world_seed,
            turn=turn,
            cargo_snapshot=CargoSnapshot(
                illegal_present=illegal_present,
                restricted_unlicensed_present=restricted_unlicensed,
            ),
            logger=self._logger,
        )
        if outcome is not None and outcome.market_access_denied:
            return False
        if outcome is not None and outcome.arrested:
            return False
        return True

    def _cargo_policy(
        self,
        system_id: str,
        check_restricted: bool,
        turn: int,
    ) -> tuple[bool, list[tuple[str, object]]]:
        government_id = self._sector.get_system(system_id).attributes.get("government_id")
        illegal_present = False
        policies: list[tuple[str, object]] = []
        holdings = dict(self._player_state.cargo_by_ship.get("active", {}))
        for sku, count in holdings.items():
            if count <= 0:
                continue
            tags = self._sku_tags(system_id, sku)
            policy = self._law_engine.evaluate_policy(
                government_id=government_id,
                commodity=Commodity(commodity_id=sku, tags=set(tags)),
                action="enforcement",
                turn=turn,
            )
            policies.append((sku, policy))
            if policy.legality_state.value == "ILLEGAL":
                illegal_present = True
        return illegal_present, policies

    def _restricted_unlicensed_present(self, system_id: str, policies: list[tuple[str, object]]) -> bool:
        for sku, policy in policies:
            if policy.legality_state.value != "RESTRICTED":
                continue
            return True
        return False

    def _apply_heat_decay(self, current_system_id: str, turn: int) -> None:
        for system in self._sector.systems:
            heat_before = self._player_state.heat_by_system.get(system.system_id, 0)
            if heat_before <= 0:
                continue
            decay = 10 if system.system_id == current_system_id else 20
            heat_after = max(0, heat_before - decay)
            self._player_state.heat_by_system[system.system_id] = heat_after
            self._logger.log(
                turn=turn,
                action="heat_decay",
                state_change=(
                    f"system_id={system.system_id} heat_before={heat_before} "
                    f"heat_after={heat_after} decay={decay}"
                ),
            )

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
        tags = self._sku_tags(system_id, sku)
        policy = self._law_engine.evaluate_policy(
            government_id=government_id,
            commodity=Commodity(commodity_id=sku, tags=set(tags)),
            action=action,
            turn=turn,
        )
        return price_transaction(
            catalog=self._catalog,
            market=market,
            government=government,
            policy=policy,
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
        market_good = self._market_good(self._player_state.current_system_id, sku)
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
