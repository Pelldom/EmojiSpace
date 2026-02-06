from dataclasses import dataclass

from economy_data import get_good
from economy_engine import EconomyEngine, TradeAction
from government_law_engine import (
    Commodity,
    GovernmentLawEngine,
    InspectionContext,
    PlayerInspectionResponse,
)
from logger import Logger
from player_state import PlayerState
from time_engine import TimeEngine
from world_generator import Sector


@dataclass(frozen=True)
class MoveAction:
    target_system_id: str


@dataclass(frozen=True)
class BuyAction:
    good_id: str


@dataclass(frozen=True)
class SellAction:
    good_id: str


class TurnLoop:
    def __init__(
        self,
        time_engine: TimeEngine,
        sector: Sector,
        player_state: PlayerState,
        logger: Logger,
        economy_engine: EconomyEngine,
        law_engine: GovernmentLawEngine,
    ) -> None:
        self._time_engine = time_engine
        self._sector = sector
        self._player_state = player_state
        self._logger = logger
        self._economy = economy_engine
        self._law_engine = law_engine

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
        self._player_state.buy(action.good_id)
        turn = self._time_engine.advance()
        self._economy.advance_turn(
            turn=turn,
            trade_action=TradeAction(
                system_id=system_id,
                good_id=action.good_id,
                delta=-1,
                cause="player_buy",
            ),
        )
        self._inspect_trade(system_id, action.good_id, "buy", turn)
        self._logger.log(
            turn=turn,
            action="buy",
            state_change=f"system_id={system_id} good_id={action.good_id}",
        )

    def execute_sell(self, action: SellAction) -> None:
        system_id = self._player_state.location_system_id
        if not self._player_state.sell(action.good_id):
            turn = self._time_engine.advance()
            self._economy.advance_turn(turn=turn)
            self._logger.log(
                turn=turn,
                action="sell",
                state_change=f"failed no_holdings system_id={system_id} good_id={action.good_id}",
            )
            return

        turn = self._time_engine.advance()
        self._economy.advance_turn(
            turn=turn,
            trade_action=TradeAction(
                system_id=system_id,
                good_id=action.good_id,
                delta=1,
                cause="player_sell",
            ),
        )
        self._inspect_trade(system_id, action.good_id, "sell", turn)
        self._logger.log(
            turn=turn,
            action="sell",
            state_change=f"system_id={system_id} good_id={action.good_id}",
        )

    def _inspect_trade(self, system_id: str, good_id: str, action: str, turn: int) -> None:
        system = self._sector.get_system(system_id)
        if system is None:
            return
        government_id = system.attributes.get("government_id")
        population_level = system.attributes.get("population_level", 3)
        good = get_good(good_id)
        commodity = Commodity(commodity_id=good.good_id, tags=set(good.tags))
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
            confiscated = self._player_state.confiscate(good_id, None)
        else:
            confiscated = self._player_state.confiscate(good_id, outcome.confiscated)
        if confiscated:
            self._logger.log(
                turn=turn,
                action="confiscation",
                state_change=(
                    f"system_id={system_id} good_id={good_id} amount={confiscated}"
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
        for good_id, count in holdings.items():
            if count <= 0:
                continue
            self._inspect_trade(system_id, good_id, "transport", turn)
