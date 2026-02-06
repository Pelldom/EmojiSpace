from dataclasses import dataclass

from economy_engine import EconomyEngine, TradeAction
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
    ) -> None:
        self._time_engine = time_engine
        self._sector = sector
        self._player_state = player_state
        self._logger = logger
        self._economy = economy_engine

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
        self._logger.log(
            turn=turn,
            action="sell",
            state_change=f"system_id={system_id} good_id={action.good_id}",
        )
