from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
import json
import math
from typing import Any

from combat_resolver import resolve_combat
from data_catalog import load_data_catalog
from encounter_generator import generate_travel_encounters
from end_game_evaluator import evaluate_end_game
from government_law_engine import Commodity, GovernmentLawEngine
from government_registry import GovernmentRegistry
from interaction_layer import (
    ACTION_IGNORE,
    HANDLER_COMBAT_STUB,
    HANDLER_LAW_STUB,
    HANDLER_PURSUIT_STUB,
    HANDLER_REACTION,
    dispatch_destination_action,
    destination_actions,
    destination_has_datanet_service,
    dispatch_player_action,
)
from law_enforcement import CargoSnapshot, PlayerOption, TriggerType, enforcement_checkpoint
from market_pricing import price_transaction
from npc_ship_generator import generate_npc_ship
from player_state import PlayerState
from pursuit_resolver import resolve_pursuit
from reaction_engine import get_npc_outcome
from reward_applicator import apply_materialized_reward
from reward_materializer import materialize_reward
from ship_assembler import assemble_ship
from ship_entity import ShipEntity
from time_engine import (
    TimeEngine,
    _reset_time_state_for_test,
    _set_hard_stop_state,
    _set_player_action_context,
    advance_time,
    get_current_turn,
)
from world_generator import Destination, System, WorldGenerator


ENGINE_STREAM_NAME = "engine_orchestration"


class _SilentLogger:
    def log(self, turn: int, action: str, state_change: str) -> None:
        _ = (turn, action, state_change)


@dataclass
class EngineContext:
    command: dict[str, Any]
    command_type: str
    turn_before: int
    turn_after: int
    events: list[dict[str, Any]] = field(default_factory=list)
    hard_stop: bool = False
    hard_stop_reason: str | None = None
    active_encounters: list[Any] = field(default_factory=list)


@dataclass(frozen=True)
class LocationActionModel:
    action_id: str
    display_name: str
    description: str
    time_cost_days: int = 0
    fuel_cost: int = 0
    requires_confirm: bool = False
    parameters: list[str] = field(default_factory=list)


class GameEngine:
    def __init__(self, world_seed: int, config: dict | None = None) -> None:
        self.world_seed = int(world_seed)
        self.config = dict(config or {})
        self._version = self.config.get("version", _read_version())
        self._silent_logger = _SilentLogger()

        _reset_time_state_for_test()

        self.catalog = load_data_catalog()
        self.government_registry = GovernmentRegistry.from_file(
            Path(__file__).resolve().parents[1] / "data" / "governments.json"
        )
        self._law_engine = GovernmentLawEngine(
            registry=self.government_registry,
            logger=self._silent_logger,
            seed=self.world_seed,
        )

        system_count = int(self.config.get("system_count", 5))
        self.sector = WorldGenerator(
            seed=self.world_seed,
            system_count=system_count,
            government_ids=self.government_registry.government_ids(),
            catalog=self.catalog,
            logger=None,
        ).generate()
        if not self.sector.systems:
            raise ValueError("Generated sector has no systems.")

        self.player_state = PlayerState(
            current_system_id=self.sector.systems[0].system_id,
            credits=int(self.config.get("starting_credits", 5000)),
        )
        self._apply_default_start_location()
        self.fleet_by_id = self._build_default_fleet()

        self.time_engine = TimeEngine(
            logger=None,
            world_seed=self.world_seed,
            sector=self.sector,
            player_state=self.player_state,
            event_frequency_percent=int(self.config.get("event_frequency_percent", 8)),
        )
        self._active_encounters: list[Any] = []

    def execute(self, command: dict) -> dict:
        turn_before = int(get_current_turn())
        command_type, payload, error = self._parse_command(command)
        if error is not None:
            return self._build_step_result(
                context=EngineContext(
                    command=command if isinstance(command, dict) else {},
                    command_type=command_type,
                    turn_before=turn_before,
                    turn_after=int(get_current_turn()),
                ),
                ok=False,
                error=error,
            )

        context = EngineContext(
            command=payload,
            command_type=command_type,
            turn_before=turn_before,
            turn_after=turn_before,
            active_encounters=list(self._active_encounters),
        )
        self._event(context, stage="start", subsystem="engine", detail={"command_type": command_type})

        try:
            if command_type == "travel_to_destination":
                self._execute_travel_to_destination(context, payload)
            elif command_type == "wait":
                self._execute_wait(context, payload)
            elif command_type == "location_action":
                self._execute_location_action(context, payload)
            elif command_type == "list_location_actions":
                self._execute_list_location_actions(context)
            elif command_type == "list_destination_actions":
                self._execute_list_destination_actions(context)
            elif command_type == "destination_action":
                self._execute_destination_action(context, payload)
            elif command_type == "enter_location":
                self._execute_enter_location(context, payload)
            elif command_type == "return_to_destination":
                self._execute_return_to_destination(context)
            elif command_type == "get_market_profile":
                self._execute_get_market_profile(context)
            elif command_type == "market_buy_list":
                self._execute_market_buy_list(context)
            elif command_type == "market_sell_list":
                self._execute_market_sell_list(context)
            elif command_type == "market_buy":
                self._execute_market_buy(context, payload)
            elif command_type == "market_sell":
                self._execute_market_sell(context, payload)
            elif command_type == "encounter_action":
                self._execute_encounter_action(context, payload)
            elif command_type == "quit":
                self._event(context, stage="command", subsystem="engine", detail={"quit": True})
            else:
                return self._build_step_result(
                    context=context,
                    ok=False,
                    error=f"unsupported_command_type:{command_type}",
                )
        except Exception as exc:  # noqa: BLE001
            context.turn_after = int(get_current_turn())
            self._active_encounters = list(context.active_encounters)
            return self._build_step_result(context=context, ok=False, error=str(exc))

        self._evaluate_hard_stop(context)
        context.turn_after = int(get_current_turn())
        self._active_encounters = list(context.active_encounters)
        return self._build_step_result(context=context, ok=True, error=None)

    def _execute_travel_to_destination(self, context: EngineContext, payload: dict[str, Any]) -> None:
        current_system = self.sector.get_system(self.player_state.current_system_id)
        if current_system is None:
            raise ValueError("Current system not found.")
        target_system_id = payload.get("target_system_id")
        if not isinstance(target_system_id, str) or not target_system_id:
            raise ValueError("travel_to_destination requires target_system_id.")
        system = self.sector.get_system(target_system_id)
        if system is None:
            raise ValueError(f"Unknown target_system_id: {target_system_id}")

        inter_system = current_system.system_id != system.system_id
        distance_ly = self._warp_distance_ly(origin=current_system, target=system) if inter_system else 0.0
        target_destination_id = self._resolve_destination_id(system, payload.get("target_destination_id"))

        if (
            target_system_id == self.player_state.current_system_id
            and target_destination_id == self.player_state.current_destination_id
        ):
            raise ValueError("already_at_destination")

        raw_days = int(math.ceil(distance_ly)) if inter_system else 1
        days = max(1, raw_days) if inter_system else 1
        fuel_cost = max(1, raw_days) if inter_system else 0
        route_id = payload.get("route_id")
        travel_id = self._travel_id(
            origin_system_id=self.player_state.current_system_id,
            target_system_id=target_system_id,
            target_destination_id=target_destination_id,
            turn=context.turn_before,
            route_id=route_id,
        )

        self._event(
            context,
            stage="travel",
            subsystem="travel_resolution",
            detail={
                "travel_id": travel_id,
                "target_system_id": target_system_id,
                "target_destination_id": target_destination_id,
                "inter_system": inter_system,
                "distance_ly": float(distance_ly),
                "distance_ly_ceiled": int(math.ceil(distance_ly)) if inter_system else 0,
            },
        )

        active_ship = self._active_ship()
        fuel_capacity = int(getattr(active_ship, "fuel_capacity", 0) or 5)
        current_fuel = int(getattr(active_ship, "current_fuel", 0) or 0)
        if inter_system and float(distance_ly) > float(fuel_capacity):
            raise ValueError("warp_range_exceeded")
        if current_fuel < fuel_cost:
            raise ValueError("insufficient_fuel")

        active_ship.current_fuel = current_fuel - fuel_cost
        self._event(
            context,
            stage="travel",
            subsystem="travel_resolution",
            detail={
                "travel_id": travel_id,
                "success": True,
                "reason": "ok",
                "fuel_cost": int(fuel_cost),
                "current_fuel": int(active_ship.current_fuel),
                "fuel_capacity": int(fuel_capacity),
            },
        )

        self.player_state.current_system_id = target_system_id
        self.player_state.current_destination_id = target_destination_id
        self.player_state.current_location_id = target_destination_id
        active_ship.current_system_id = target_system_id
        active_ship.current_destination_id = target_destination_id
        active_ship.current_location_id = target_destination_id
        active_ship.location_id = target_destination_id

        time_result = self._advance_time_in_chunks(days=days, reason=f"travel:{travel_id}")
        self._event(
            context,
            stage="time_advance",
            subsystem="time_engine",
            detail={
                "travel_id": travel_id,
                "days_requested": int(days),
                "days_completed": int(time_result["days_completed"]),
                "hard_stop_reason": time_result["hard_stop_reason"],
            },
        )

        if time_result["hard_stop_reason"] is not None:
            context.hard_stop = True
            context.hard_stop_reason = str(time_result["hard_stop_reason"])
            return

        border_outcome = self._run_law_checkpoint(context, trigger_type=TriggerType.BORDER)
        if border_outcome is not None and (border_outcome.get("arrested") or border_outcome.get("dead")):
            self._evaluate_hard_stop(context)
            if context.hard_stop:
                return

        active_situation_ids = self._active_situation_ids_for_current_system()
        encounters = generate_travel_encounters(
            world_seed=str(self.world_seed),
            travel_id=travel_id,
            population=int(system.population),
            system_government_id=str(system.government_id),
            active_situations=active_situation_ids,
            travel_context={"mode": "system_arrival" if inter_system else "in_system"},
            world_state_engine=self._world_state_engine(),
            current_system_id=self.player_state.current_system_id,
        )
        encounters = sorted(encounters, key=lambda entry: str(getattr(entry, "encounter_id", "")))
        context.active_encounters = list(encounters)
        self._event(
            context,
            stage="encounter_gen",
            subsystem="encounter_generator",
            detail={"travel_id": travel_id, "encounter_count": len(encounters)},
        )

        for encounter in list(context.active_encounters):
            if context.hard_stop:
                break
            self._resolve_encounter(
                context=context,
                spec=encounter,
                player_action=str(payload.get("encounter_action", ACTION_IGNORE)),
            )
            context.active_encounters = [
                row
                for row in context.active_encounters
                if str(getattr(row, "encounter_id", "")) != str(getattr(encounter, "encounter_id", ""))
            ]
            self._evaluate_hard_stop(context)

    def _execute_wait(self, context: EngineContext, payload: dict[str, Any]) -> None:
        days_raw = payload.get("days")
        if not isinstance(days_raw, int):
            raise ValueError("wait requires integer days.")
        if days_raw < 1 or days_raw > 10:
            raise ValueError("wait.days must be in range 1..10.")
        result = self._advance_time(days=days_raw, reason="wait")
        self._event(
            context,
            stage="time_advance",
            subsystem="time_engine",
            detail={
                "days_requested": int(days_raw),
                "days_completed": int(result.days_completed),
                "hard_stop_reason": result.hard_stop_reason,
            },
        )

    def _execute_location_action(self, context: EngineContext, payload: dict[str, Any]) -> None:
        location = self._current_location()
        if location is None:
            raise ValueError("not_in_location")

        action_id = payload.get("action_id")
        if not isinstance(action_id, str) or not action_id:
            raise ValueError("location_action requires action_id.")
        kwargs = payload.get("action_kwargs", payload.get("kwargs", {}))
        if kwargs is None:
            kwargs = {}
        if not isinstance(kwargs, dict):
            raise ValueError("location_action.action_kwargs must be an object.")

        available = {entry.action_id: entry for entry in self._available_location_actions(location)}
        if action_id not in available:
            raise ValueError("action_not_available_for_location")

        if action_id == "buy":
            sku_id = kwargs.get("sku_id")
            quantity = kwargs.get("quantity")
            if not isinstance(sku_id, str) or not sku_id:
                raise ValueError("location buy requires sku_id.")
            if not isinstance(quantity, int):
                raise ValueError("location buy requires integer quantity.")
            self._execute_market_buy(context, {"sku_id": sku_id, "quantity": quantity})
            return
        if action_id == "sell":
            sku_id = kwargs.get("sku_id")
            quantity = kwargs.get("quantity")
            if not isinstance(sku_id, str) or not sku_id:
                raise ValueError("location sell requires sku_id.")
            if not isinstance(quantity, int):
                raise ValueError("location sell requires integer quantity.")
            self._execute_market_sell(context, {"sku_id": sku_id, "quantity": quantity})
            return

        destination = self._current_destination()
        if destination is None:
            raise ValueError("No current destination for location_action.")

        active_ship = self._active_ship()
        fuel_before = int(active_ship.current_fuel)
        credits_before = int(self.player_state.credits)
        action_kwargs = self._build_destination_action_kwargs(action_id=action_id, destination=destination, kwargs=kwargs)
        result = dispatch_destination_action(action_id=action_id, **action_kwargs)
        if action_id == "refuel" and isinstance(result.get("credits"), int):
            self.player_state.credits = int(result["credits"])
        fuel_after = int(active_ship.current_fuel)
        credits_after = int(self.player_state.credits)
        summary = {
            "result_ok": bool(result.get("ok", False)),
            "reason": result.get("reason"),
            "fuel_before": fuel_before,
            "fuel_after": fuel_after,
            "credits_before": credits_before,
            "credits_after": credits_after,
        }
        if action_id == "refuel":
            units = int(result.get("units_purchased", 0) or 0)
            total_cost = int(result.get("total_cost", 0) or 0)
            unit_price = int(total_cost / units) if units > 0 else 0
            summary.update(
                {
                    "units_purchased": units,
                    "unit_price": unit_price,
                    "total_cost": total_cost,
                }
            )
        self._event(
            context,
            stage="location_action",
            subsystem="interaction_layer",
            detail={"action_id": action_id, "result_summary": summary, "result": _jsonable(result)},
        )

    def _execute_list_location_actions(self, context: EngineContext) -> None:
        location = self._current_location()
        if location is None:
            raise ValueError("not_in_location")
        models = [self._location_action_to_dict(entry) for entry in self._available_location_actions(location)]
        self._event(
            context,
            stage="location_actions",
            subsystem="interaction_layer",
            detail={"location_id": getattr(location, "location_id", None), "actions": models},
        )

    def _execute_list_destination_actions(self, context: EngineContext) -> None:
        models = [self._location_action_to_dict(entry) for entry in self._available_destination_actions()]
        self._event(
            context,
            stage="destination_actions",
            subsystem="interaction_layer",
            detail={
                "destination_id": self.player_state.current_destination_id,
                "actions": models,
            },
        )

    def _execute_destination_action(self, context: EngineContext, payload: dict[str, Any]) -> None:
        action_id = payload.get("action_id")
        if not isinstance(action_id, str) or not action_id:
            raise ValueError("destination_action requires action_id.")
        kwargs = payload.get("action_kwargs", payload.get("kwargs", {}))
        if kwargs is None:
            kwargs = {}
        if not isinstance(kwargs, dict):
            raise ValueError("destination_action.action_kwargs must be an object.")

        available = {entry.action_id: entry for entry in self._available_destination_actions()}
        if action_id not in available:
            raise ValueError("destination_action_not_available")

        if action_id == "refuel":
            self._execute_destination_refuel(context, kwargs)
            return
        if action_id == "customs_inspection":
            allow_repeat = bool(kwargs.get("allow_repeat", False))
            customs = self._run_customs_with_guard(
                context=context,
                kind="voluntary",
                allow_repeat=allow_repeat,
                option_name=kwargs.get("option"),
            )
            self._event(
                context,
                stage="destination_action",
                subsystem="law_enforcement",
                detail={
                    "action_id": "customs_inspection",
                    "customs": customs,
                },
            )
            return
        raise ValueError(f"unsupported_destination_action:{action_id}")

    def _execute_destination_refuel(self, context: EngineContext, kwargs: dict[str, Any]) -> None:
        destination = self._current_destination()
        if destination is None:
            raise ValueError("No current destination for refuel.")
        if not destination_has_datanet_service(destination):
            raise ValueError("datanet_required_for_refuel")
        requested_units = kwargs.get("requested_units")
        if requested_units is not None and not isinstance(requested_units, int):
            raise ValueError("requested_units must be an integer.")

        active_ship = self._active_ship()
        fuel_before = int(active_ship.current_fuel)
        credits_before = int(self.player_state.credits)
        action_kwargs = self._build_destination_action_kwargs(
            action_id="refuel",
            destination=destination,
            kwargs={"requested_units": requested_units},
        )
        result = dispatch_destination_action(action_id="refuel", **action_kwargs)
        if isinstance(result.get("credits"), int):
            self.player_state.credits = int(result["credits"])
        fuel_after = int(active_ship.current_fuel)
        credits_after = int(self.player_state.credits)
        units = int(result.get("units_purchased", 0) or 0)
        total_cost = int(result.get("total_cost", 0) or 0)
        unit_price = int(total_cost / units) if units > 0 else 0
        self._event(
            context,
            stage="destination_action",
            subsystem="interaction_layer",
            detail={
                "action_id": "refuel",
                "result_summary": {
                    "result_ok": bool(result.get("ok", False)),
                    "reason": result.get("reason"),
                    "fuel_before": fuel_before,
                    "fuel_after": fuel_after,
                    "credits_before": credits_before,
                    "credits_after": credits_after,
                    "units_purchased": units,
                    "unit_price": unit_price,
                    "total_cost": total_cost,
                },
                "result": _jsonable(result),
            },
        )

    def _execute_enter_location(self, context: EngineContext, payload: dict[str, Any]) -> None:
        destination = self._current_destination()
        if destination is None:
            raise ValueError("no_current_destination")
        locations = list(getattr(destination, "locations", []) or [])
        if not locations:
            raise ValueError("no_locations_available")

        location_id = payload.get("location_id")
        location_index = payload.get("location_index")
        selected_location = None
        if isinstance(location_id, str) and location_id:
            for location in locations:
                if getattr(location, "location_id", None) == location_id:
                    selected_location = location
                    break
            if selected_location is None:
                raise ValueError("location_not_found")
        elif isinstance(location_index, int):
            if location_index < 1 or location_index > len(locations):
                raise ValueError("location_index_out_of_range")
            selected_location = locations[location_index - 1]
        else:
            raise ValueError("enter_location requires location_id or location_index.")

        location_type = str(getattr(selected_location, "location_type", "") or "")
        if location_type == "market":
            customs = self._run_customs_with_guard(context=context, kind="auto_market_entry")
            outcome = customs.get("outcome")
            if isinstance(outcome, dict):
                if bool(outcome.get("market_access_denied")):
                    raise ValueError("market_access_denied")
                if bool(outcome.get("arrested")) or bool(outcome.get("dead")):
                    raise ValueError("market_entry_blocked_by_enforcement")

        selected_location_id = str(getattr(selected_location, "location_id", ""))
        self.player_state.current_location_id = selected_location_id
        active_ship = self._active_ship()
        active_ship.current_location_id = selected_location_id
        active_ship.location_id = selected_location_id
        self._event(
            context,
            stage="location_navigation",
            subsystem="engine",
            detail={
                "action": "enter_location",
                "location_id": selected_location_id,
                "location_type": location_type,
            },
        )

    def _execute_return_to_destination(self, context: EngineContext) -> None:
        destination_id = self.player_state.current_destination_id
        self.player_state.current_location_id = destination_id
        active_ship = self._active_ship()
        active_ship.current_location_id = destination_id
        active_ship.location_id = destination_id
        self._event(
            context,
            stage="location_navigation",
            subsystem="engine",
            detail={"action": "return_to_destination", "destination_id": destination_id},
        )

    def _execute_get_market_profile(self, context: EngineContext) -> None:
        destination = self._current_destination()
        if destination is None:
            raise ValueError("no_current_destination")
        market = getattr(destination, "market", None)
        if market is None:
            raise ValueError("market_not_available")
        location = self._current_location()
        if location is not None and str(getattr(location, "location_type", "")) not in {"market"}:
            raise ValueError("market_profile_requires_destination_or_market_location")

        categories: dict[str, Any] = {}
        for category_id in sorted(market.categories):
            category = market.categories[category_id]
            categories[category_id] = {
                "produced": sorted([entry.sku for entry in category.produced]),
                "consumed": sorted([entry.sku for entry in category.consumed]),
                "neutral": sorted([entry.sku for entry in category.neutral]),
            }
        self._event(
            context,
            stage="market_profile",
            subsystem="market",
            detail={
                "system_id": self.player_state.current_system_id,
                "destination_id": destination.destination_id,
                "primary_economy_id": getattr(destination, "primary_economy_id", None),
                "secondary_economy_ids": sorted(list(getattr(destination, "secondary_economy_ids", []) or [])),
                "categories": categories,
                "active_situations": self._active_situation_ids_for_current_system(),
            },
        )

    def _execute_market_buy_list(self, context: EngineContext) -> None:
        self._require_market_location()
        rows = self._market_price_rows(action="buy")
        self._event(
            context,
            stage="market_buy_list",
            subsystem="market",
            detail={"destination_id": self.player_state.current_destination_id, "rows": rows},
        )

    def _execute_market_sell_list(self, context: EngineContext) -> None:
        self._require_market_location()
        rows = self._market_price_rows(action="sell")
        self._event(
            context,
            stage="market_sell_list",
            subsystem="market",
            detail={"destination_id": self.player_state.current_destination_id, "rows": rows},
        )

    def _execute_market_buy(self, context: EngineContext, payload: dict[str, Any]) -> None:
        self._require_market_location()
        sku_id = payload.get("sku_id")
        quantity = payload.get("quantity")
        if not isinstance(sku_id, str) or not sku_id:
            raise ValueError("market_buy requires sku_id.")
        if not isinstance(quantity, int) or quantity < 1:
            raise ValueError("market_buy requires quantity >= 1.")

        customs = self._run_customs_with_guard(context=context, kind="auto_market_entry")
        outcome = customs.get("outcome")
        if isinstance(outcome, dict):
            if bool(outcome.get("market_access_denied")):
                raise ValueError("market_access_denied")
            if bool(outcome.get("arrested")) or bool(outcome.get("dead")):
                raise ValueError("market_trade_blocked_by_enforcement")

        row = self._market_row_by_sku(action="buy", sku_id=sku_id)
        if row is None:
            raise ValueError("sku_not_available_for_buy")
        unit_price = int(row["unit_price"])
        total_cost = int(unit_price * quantity)
        credits_before = int(self.player_state.credits)
        if credits_before < total_cost:
            raise ValueError("insufficient_credits")
        self._ensure_cargo_capacity_for_add(quantity)

        holdings = self.player_state.cargo_by_ship.setdefault("active", {})
        holdings[sku_id] = int(holdings.get(sku_id, 0) + quantity)
        self.player_state.credits = credits_before - total_cost
        self._event(
            context,
            stage="market_trade",
            subsystem="market",
            detail={
                "action": "buy",
                "sku_id": sku_id,
                "quantity": int(quantity),
                "unit_price": int(unit_price),
                "total_cost": int(total_cost),
                "credits_before": credits_before,
                "credits_after": int(self.player_state.credits),
                "cargo_after": int(holdings.get(sku_id, 0)),
            },
        )

    def _execute_market_sell(self, context: EngineContext, payload: dict[str, Any]) -> None:
        self._require_market_location()
        sku_id = payload.get("sku_id")
        quantity = payload.get("quantity")
        if not isinstance(sku_id, str) or not sku_id:
            raise ValueError("market_sell requires sku_id.")
        if not isinstance(quantity, int) or quantity < 1:
            raise ValueError("market_sell requires quantity >= 1.")

        holdings = self.player_state.cargo_by_ship.setdefault("active", {})
        current_units = int(holdings.get(sku_id, 0))
        if current_units < quantity:
            raise ValueError("insufficient_cargo_units")

        customs = self._run_customs_with_guard(context=context, kind="auto_market_entry")
        outcome = customs.get("outcome")
        if isinstance(outcome, dict):
            if bool(outcome.get("market_access_denied")):
                raise ValueError("market_access_denied")
            if bool(outcome.get("arrested")) or bool(outcome.get("dead")):
                raise ValueError("market_trade_blocked_by_enforcement")

        row = self._market_row_by_sku(action="sell", sku_id=sku_id)
        if row is None:
            raise ValueError("sku_not_available_for_sell")
        unit_price = int(row["unit_price"])
        total_gain = int(unit_price * quantity)
        credits_before = int(self.player_state.credits)

        holdings[sku_id] = current_units - quantity
        self.player_state.credits = credits_before + total_gain
        self._event(
            context,
            stage="market_trade",
            subsystem="market",
            detail={
                "action": "sell",
                "sku_id": sku_id,
                "quantity": int(quantity),
                "unit_price": int(unit_price),
                "total_gain": int(total_gain),
                "credits_before": credits_before,
                "credits_after": int(self.player_state.credits),
                "cargo_after": int(holdings.get(sku_id, 0)),
            },
        )

    def _execute_encounter_action(self, context: EngineContext, payload: dict[str, Any]) -> None:
        if not context.active_encounters:
            raise ValueError("encounter_action requires an active encounter.")
        action_id = payload.get("action_id")
        if not isinstance(action_id, str) or not action_id:
            raise ValueError("encounter_action requires action_id.")
        kwargs = payload.get("kwargs", {})
        if kwargs is None:
            kwargs = {}
        if not isinstance(kwargs, dict):
            raise ValueError("encounter_action.kwargs must be an object.")

        spec = context.active_encounters[0]
        self._resolve_encounter(
            context=context,
            spec=spec,
            player_action=action_id,
            player_kwargs=kwargs,
        )
        context.active_encounters = context.active_encounters[1:]

    def _resolve_encounter(
        self,
        *,
        context: EngineContext,
        spec: Any,
        player_action: str,
        player_kwargs: dict[str, Any] | None = None,
    ) -> None:
        player_kwargs = dict(player_kwargs or {})
        dispatch = dispatch_player_action(
            spec=spec,
            player_action=player_action,
            world_seed=str(self.world_seed),
            ignore_count=0,
            reputation_band=int(self.player_state.reputation_by_system.get(self.player_state.current_system_id, 50)),
            notoriety_band=int(self.player_state.progression_tracks.get("notoriety", 0)),
        )
        self._event(
            context,
            stage="interaction_dispatch",
            subsystem="interaction_layer",
            detail={
                "encounter_id": str(spec.encounter_id),
                "action_id": player_action,
                "next_handler": str(dispatch.next_handler),
                "handler_payload": _jsonable(dispatch.handler_payload),
            },
        )

        resolver_outcome: dict[str, Any] = {"resolver": "none", "outcome": None}
        handler = str(dispatch.next_handler)
        if handler == HANDLER_REACTION:
            npc_outcome, npc_log = get_npc_outcome(
                spec=spec,
                player_action=player_action,
                world_seed=str(self.world_seed),
                ignore_count=0,
                reputation_score=int(self.player_state.reputation_by_system.get(self.player_state.current_system_id, 50)),
                notoriety_score=int(self.player_state.progression_tracks.get("notoriety", 0)),
            )
            resolver_outcome = {"resolver": "reaction", "outcome": npc_outcome, "log": _jsonable(npc_log)}
        elif handler == HANDLER_PURSUIT_STUB:
            pursuer_ship, pursued_ship = self._pursuit_ships_for_spec(spec)
            pursuit = resolve_pursuit(
                encounter_id=f"PUR-{spec.encounter_id}",
                world_seed=str(self.world_seed),
                pursuer_ship=pursuer_ship,
                pursued_ship=pursued_ship,
            )
            resolver_outcome = {
                "resolver": "pursuit",
                "outcome": pursuit.outcome,
                "escaped": bool(pursuit.escaped),
                "threshold": float(pursuit.threshold),
            }
        elif handler == HANDLER_COMBAT_STUB:
            combat = self._resolve_encounter_combat(spec)
            resolver_outcome = {
                "resolver": "combat",
                "outcome": str(combat.outcome),
                "winner": str(combat.winner),
                "rounds": int(combat.rounds),
            }
        elif handler == HANDLER_LAW_STUB:
            option = player_kwargs.get("option", "SUBMIT")
            law_outcome = self._run_law_checkpoint(
                context,
                trigger_type=TriggerType.CUSTOMS,
                option_name=str(option),
            )
            resolver_outcome = {"resolver": "law", "outcome": law_outcome}
        self._event(
            context,
            stage="resolver",
            subsystem="resolver_router",
            detail={"encounter_id": str(spec.encounter_id), "resolver_outcome": _jsonable(resolver_outcome)},
        )

        qualifies = self._reward_qualifies(dispatch=dispatch, resolver_outcome=resolver_outcome, spec=spec)
        self._event(
            context,
            stage="conditional_rewards",
            subsystem="reward_gate",
            detail={"encounter_id": str(spec.encounter_id), "qualifies": bool(qualifies)},
        )
        if not qualifies:
            return

        reward_payload = materialize_reward(
            spec,
            self._system_market_payloads(self.sector.get_system(self.player_state.current_system_id)),
            str(self.world_seed),
        )
        applied = apply_materialized_reward(player=self.player_state, reward_payload=reward_payload, context="game_engine")
        self._event(
            context,
            stage="conditional_rewards",
            subsystem="reward_applicator",
            detail={
                "encounter_id": str(spec.encounter_id),
                "reward_profile_id": str(getattr(spec, "reward_profile_id", "")),
                "applied": _jsonable(applied),
            },
        )

    def _resolve_encounter_combat(self, spec: Any) -> Any:
        system = self.sector.get_system(self.player_state.current_system_id)
        if system is None:
            raise ValueError("Current system not found for combat resolution.")
        enemy_ship = generate_npc_ship(
            world_seed=self.world_seed,
            system_id=self.player_state.current_system_id,
            system_population=int(system.population),
            encounter_id=str(spec.encounter_id),
            encounter_subtype=str(spec.subtype_id),
        )
        player_ship = self._active_ship()
        player_ship_state = {
            "hull_id": player_ship.model_id,
            "module_instances": list(player_ship.persistent_state.get("module_instances", [])),
            "degradation_state": dict(
                player_ship.persistent_state.get("degradation_state", {"weapon": 0, "defense": 0, "engine": 0})
            ),
            "current_hull_integrity": int(player_ship.persistent_state.get("current_hull_integrity", 0) or 0),
        }
        combat = resolve_combat(
            world_seed=str(self.world_seed),
            combat_id=f"CMB-{spec.encounter_id}",
            system_id=self.player_state.current_system_id,
            player_ship_state=player_ship_state,
            enemy_ship_state=enemy_ship,
            max_rounds=int(self.config.get("combat_max_rounds", 3)),
        )
        final_player = getattr(combat, "final_state_player", None)
        if isinstance(final_player, dict):
            player_ship.persistent_state["degradation_state"] = dict(
                final_player.get("degradation", {"weapon": 0, "defense": 0, "engine": 0})
            )
            if isinstance(final_player.get("current_hull"), int):
                player_ship.persistent_state["current_hull_integrity"] = int(final_player["current_hull"])
        return combat

    def _run_law_checkpoint(
        self,
        context: EngineContext,
        *,
        trigger_type: TriggerType,
        option_name: str | None = None,
    ) -> dict[str, Any] | None:
        system = self.sector.get_system(self.player_state.current_system_id)
        if system is None:
            return None
        government = self.government_registry.get_government(system.government_id)
        policies = self._cargo_policy(system_id=system.system_id, turn=get_current_turn())
        illegal_present = any(policy.legality_state.value == "ILLEGAL" for _, policy in policies)
        restricted_unlicensed = any(policy.legality_state.value == "RESTRICTED" for _, policy in policies)
        if not illegal_present and not restricted_unlicensed:
            self._event(
                context,
                stage="law_checkpoint",
                subsystem="law_enforcement",
                detail={"trigger_type": trigger_type.value, "skipped": True},
            )
            return None

        option = _parse_player_option(option_name)
        outcome = enforcement_checkpoint(
            system_id=system.system_id,
            trigger_type=trigger_type,
            government=government,
            policy_results=policies,
            player=self.player_state,
            world_seed=self.world_seed,
            turn=int(get_current_turn()),
            cargo_snapshot=CargoSnapshot(
                illegal_present=illegal_present,
                restricted_unlicensed_present=restricted_unlicensed,
            ),
            logger=self._silent_logger,
            option=option,
            ship=self._active_ship(),
        )
        payload = _law_outcome_payload(outcome)
        self._event(
            context,
            stage="law_checkpoint",
            subsystem="law_enforcement",
            detail={"trigger_type": trigger_type.value, "outcome": payload},
        )
        return payload

    def _cargo_policy(self, *, system_id: str, turn: int) -> list[tuple[str, Any]]:
        government_id = self.sector.get_system(system_id).government_id
        policies: list[tuple[str, Any]] = []
        holdings = dict(self.player_state.cargo_by_ship.get("active", {}))
        for sku in sorted(holdings):
            count = int(holdings.get(sku, 0))
            if count <= 0:
                continue
            try:
                good = self.catalog.good_by_sku(sku)
            except KeyError:
                continue
            tags = set(good.tags)
            if isinstance(good.possible_tag, str):
                tags.add(good.possible_tag)
            policy = self._law_engine.evaluate_policy(
                government_id=government_id,
                commodity=Commodity(commodity_id=sku, tags=tags),
                action="enforcement",
                turn=turn,
            )
            policies.append((sku, policy))
        return policies

    def _reward_qualifies(self, *, dispatch: Any, resolver_outcome: dict[str, Any], spec: Any) -> bool:
        if getattr(spec, "reward_profile_id", None) is None:
            return False

        resolver = str(resolver_outcome.get("resolver", "none"))
        outcome = resolver_outcome.get("outcome")
        if resolver == "combat":
            return str(resolver_outcome.get("winner")) == "player"
        if resolver == "pursuit":
            return str(outcome) == "escape_success"
        if resolver == "reaction":
            return str(outcome) in {"accept"}
        if resolver == "law":
            return False

        payload = getattr(dispatch, "handler_payload", {}) or {}
        npc_outcome = payload.get("npc_outcome")
        if isinstance(npc_outcome, str) and npc_outcome in {"accept"}:
            return True
        return False

    def _evaluate_hard_stop(self, context: EngineContext) -> None:
        if context.hard_stop:
            return
        end_state = evaluate_end_game(player=self.player_state, missions=[])
        if end_state.status != "lose":
            _set_hard_stop_state(player_dead=False, tier2_detention=False)
            return
        reason = "end_game_lose"
        failures = list(end_state.failure_reasons)
        if "tier2_arrest" in failures:
            reason = "tier2_detention"
            _set_hard_stop_state(player_dead=False, tier2_detention=True)
        elif "death" in failures:
            reason = "player_death"
            _set_hard_stop_state(player_dead=True, tier2_detention=False)
        else:
            _set_hard_stop_state(player_dead=False, tier2_detention=False)
        context.hard_stop = True
        context.hard_stop_reason = reason
        self._event(context, stage="hard_stop", subsystem="end_game_evaluator", detail={"reason": reason})

    def _parse_command(self, command: Any) -> tuple[str, dict[str, Any], str | None]:
        if not isinstance(command, dict):
            return "", {}, "command must be an object."
        if "action_type" in command and "payload" in command:
            command_type = command.get("action_type")
            payload = command.get("payload")
        else:
            command_type = command.get("type")
            payload = {k: v for k, v in command.items() if k != "type"}
        if not isinstance(command_type, str):
            return "", {}, "command type must be a string."
        if not isinstance(payload, dict):
            return command_type, {}, "command payload must be an object."
        allowed = {"travel_to_destination", "location_action", "encounter_action", "wait", "quit"}
        allowed.add("list_location_actions")
        allowed.add("list_destination_actions")
        allowed.add("destination_action")
        allowed.add("enter_location")
        allowed.add("return_to_destination")
        allowed.add("get_market_profile")
        allowed.add("market_buy_list")
        allowed.add("market_sell_list")
        allowed.add("market_buy")
        allowed.add("market_sell")
        if command_type not in allowed:
            return command_type, payload, f"unsupported command type: {command_type}"
        return command_type, payload, None

    def _build_step_result(self, *, context: EngineContext, ok: bool, error: str | None) -> dict[str, Any]:
        return {
            "ok": bool(ok),
            "error": error,
            "command_type": context.command_type,
            "turn_before": int(context.turn_before),
            "turn_after": int(context.turn_after),
            "hard_stop": bool(context.hard_stop),
            "hard_stop_reason": context.hard_stop_reason,
            "events": list(context.events),
            "player": {
                "system_id": self.player_state.current_system_id,
                "destination_id": self.player_state.current_destination_id,
                "location_id": self.player_state.current_location_id,
                "credits": int(self.player_state.credits),
                "arrest_state": self.player_state.arrest_state,
            },
            "active_encounter_count": len(context.active_encounters),
            "version": self._version,
        }

    def _event(self, context: EngineContext, *, stage: str, subsystem: str, detail: dict[str, Any]) -> None:
        context.events.append(
            {
                "stage": stage,
                "world_seed": int(self.world_seed),
                "turn": int(get_current_turn()),
                "command_type": context.command_type,
                "subsystem": subsystem,
                "detail": _jsonable(detail),
            }
        )

    def _advance_time(self, *, days: int, reason: str) -> Any:
        _set_player_action_context(True)
        try:
            return advance_time(days=int(days), reason=reason)
        finally:
            _set_player_action_context(False)

    def _advance_time_in_chunks(self, *, days: int, reason: str) -> dict[str, Any]:
        remaining = int(days)
        completed = 0
        hard_stop_reason = None
        while remaining > 0:
            chunk = min(10, remaining)
            result = self._advance_time(days=chunk, reason=reason)
            completed += int(result.days_completed)
            remaining -= int(result.days_completed)
            if result.hard_stop_reason is not None:
                hard_stop_reason = str(result.hard_stop_reason)
                break
            if int(result.days_completed) < chunk:
                break
        return {"days_requested": int(days), "days_completed": int(completed), "hard_stop_reason": hard_stop_reason}

    def _apply_default_start_location(self) -> None:
        system = self.sector.systems[0]
        destination_id = None
        if system.destinations:
            destination_id = system.destinations[0].destination_id
        self.player_state.current_destination_id = destination_id
        self.player_state.current_location_id = destination_id

    def _build_default_fleet(self) -> dict[str, ShipEntity]:
        assembled = assemble_ship("civ_t1_midge", [], {"weapon": 0, "defense": 0, "engine": 0})
        ship = ShipEntity(
            ship_id="PLAYER-SHIP-001",
            model_id="civ_t1_midge",
            owner_id=self.player_state.player_id,
            activity_state="active",
            location_id=self.player_state.current_destination_id or self.player_state.current_system_id,
            current_system_id=self.player_state.current_system_id,
            current_destination_id=self.player_state.current_destination_id,
            current_location_id=self.player_state.current_destination_id or self.player_state.current_system_id,
            fuel_capacity=int(assembled["fuel_capacity"]),
            current_fuel=int(assembled["fuel_capacity"]),
        )
        ship.persistent_state["module_instances"] = []
        ship.persistent_state["degradation_state"] = {"weapon": 0, "defense": 0, "engine": 0}
        fleet = {ship.ship_id: ship}
        self.player_state.active_ship_id = ship.ship_id
        self.player_state.owned_ship_ids = [ship.ship_id]
        return fleet

    def _active_ship(self) -> ShipEntity:
        ship_id = self.player_state.active_ship_id
        ship = self.fleet_by_id.get(ship_id)
        if ship is None:
            raise ValueError("Player has no active ship.")
        return ship

    def _world_state_engine(self) -> Any | None:
        import time_engine as time_engine_module

        return getattr(time_engine_module, "_world_state_engine", None)

    def _resolve_destination_id(self, system: System, destination_id: Any) -> str | None:
        if isinstance(destination_id, str) and destination_id:
            for destination in system.destinations:
                if destination.destination_id == destination_id:
                    return destination_id
            raise ValueError(f"Unknown destination_id for target system: {destination_id}")
        if system.destinations:
            return system.destinations[0].destination_id
        return None

    def _travel_id(
        self,
        *,
        origin_system_id: str,
        target_system_id: str,
        target_destination_id: str | None,
        turn: int,
        route_id: Any,
    ) -> str:
        route_part = str(route_id) if isinstance(route_id, str) and route_id else "auto_route"
        destination_part = target_destination_id or "none"
        token = f"{origin_system_id}:{target_system_id}:{destination_part}:{turn}:{route_part}"
        return f"TRAVEL-{token}"

    def _warp_distance_ly(self, *, origin: System, target: System) -> float:
        dx = float(target.x) - float(origin.x)
        dy = float(target.y) - float(origin.y)
        return math.sqrt((dx * dx) + (dy * dy))

    def _active_situation_ids_for_current_system(self) -> list[str]:
        engine = self._world_state_engine()
        if engine is None:
            return []
        active = engine.get_active_situations(self.player_state.current_system_id)
        ids = [entry.situation_id for entry in active if hasattr(entry, "situation_id")]
        return sorted(ids)

    def _current_destination(self) -> Destination | None:
        system = self.sector.get_system(self.player_state.current_system_id)
        if system is None:
            return None
        target_destination_id = self.player_state.current_destination_id
        if isinstance(target_destination_id, str):
            for destination in system.destinations:
                if destination.destination_id == target_destination_id:
                    return destination
        if system.destinations:
            return system.destinations[0]
        return None

    def _current_location(self) -> Any | None:
        destination = self._current_destination()
        if destination is None:
            return None
        location_id = self.player_state.current_location_id
        destination_id = self.player_state.current_destination_id
        if not isinstance(location_id, str):
            return None
        if location_id == destination_id:
            return None
        for location in list(getattr(destination, "locations", []) or []):
            if getattr(location, "location_id", None) == location_id:
                return location
        return None

    def _available_location_actions(self, location: Any) -> list[LocationActionModel]:
        destination = self._current_destination()
        if destination is None:
            return []
        location_type = str(getattr(location, "location_type", "") or "")
        destination_action_ids = list(destination_actions(destination))
        if location_type == "market":
            destination_action_ids = ["buy", "sell"]
        supported_ids = {"buy", "sell", "buy_hull", "sell_hull", "buy_module", "sell_module", "repair_ship"}
        scoped_allowed = self._allowed_action_ids_for_location_type(location_type)

        actions: list[LocationActionModel] = []
        for action_id in sorted(destination_action_ids):
            if action_id not in supported_ids:
                continue
            if action_id not in scoped_allowed:
                continue
            if action_id == "refuel" and not destination_has_datanet_service(destination):
                continue
            actions.append(self._location_action_model(action_id))
        return sorted(actions, key=lambda entry: entry.action_id)

    def _available_destination_actions(self) -> list[LocationActionModel]:
        destination = self._current_destination()
        if destination is None:
            return []
        actions = [
            LocationActionModel(
                action_id="customs_inspection",
                display_name="Customs Inspection",
                description="Run a voluntary customs inspection at destination level.",
            )
        ]
        if destination_has_datanet_service(destination):
            actions.append(
                LocationActionModel(
                    action_id="refuel",
                    display_name="Refuel",
                    description="Purchase fuel units up to ship fuel capacity.",
                    parameters=["requested_units"],
                )
            )
        return sorted(actions, key=lambda entry: entry.action_id)

    def _allowed_action_ids_for_location_type(self, location_type: str) -> set[str]:
        if location_type == "datanet":
            return set()
        if location_type == "shipdock":
            return {"buy_hull", "sell_hull", "buy_module", "sell_module", "repair_ship"}
        if location_type == "market":
            return {"buy", "sell"}
        if location_type == "warehouse":
            return set()
        if location_type == "bar":
            return set()
        return set()

    def _location_action_model(self, action_id: str) -> LocationActionModel:
        catalog = {
            "refuel": LocationActionModel(
                action_id="refuel",
                display_name="Refuel",
                description="Purchase fuel units up to ship fuel capacity.",
                time_cost_days=0,
                fuel_cost=0,
                requires_confirm=False,
                parameters=[],
            ),
            "buy_hull": LocationActionModel(
                action_id="buy_hull",
                display_name="Buy Hull",
                description="Purchase a hull from shipdock inventory.",
            ),
            "sell_hull": LocationActionModel(
                action_id="sell_hull",
                display_name="Sell Hull",
                description="Sell an owned hull currently present at destination.",
                requires_confirm=True,
            ),
            "buy_module": LocationActionModel(
                action_id="buy_module",
                display_name="Buy Module",
                description="Purchase a module for an eligible ship.",
            ),
            "sell_module": LocationActionModel(
                action_id="sell_module",
                display_name="Sell Module",
                description="Sell a module installed on an eligible ship.",
            ),
            "repair_ship": LocationActionModel(
                action_id="repair_ship",
                display_name="Repair Ship",
                description="Restore hull and subsystem degradation at shipdock.",
            ),
            "buy": LocationActionModel(
                action_id="buy",
                display_name="Buy",
                description="Buy listed market goods.",
                parameters=["sku_id", "quantity"],
            ),
            "sell": LocationActionModel(
                action_id="sell",
                display_name="Sell",
                description="Sell cargo to local market.",
                parameters=["sku_id", "quantity"],
            ),
        }
        return catalog[action_id]

    def _location_action_to_dict(self, model: LocationActionModel) -> dict[str, Any]:
        return {
            "action_id": model.action_id,
            "display_name": model.display_name,
            "description": model.description,
            "time_cost_days": int(model.time_cost_days),
            "fuel_cost": int(model.fuel_cost),
            "requires_confirm": bool(model.requires_confirm),
            "parameters": list(model.parameters),
        }

    def _build_destination_action_kwargs(
        self,
        *,
        action_id: str,
        destination: Destination,
        kwargs: dict[str, Any],
    ) -> dict[str, Any]:
        system = self.sector.get_system(self.player_state.current_system_id)
        if system is None:
            raise ValueError("No current system for destination action.")
        action_kwargs: dict[str, Any] = {}
        action_kwargs.update(kwargs)

        if action_id == "refuel":
            action_kwargs.setdefault("ship", self._active_ship())
            action_kwargs.setdefault("player_credits", int(self.player_state.credits))
            return action_kwargs

        action_kwargs.setdefault("destination", destination)
        action_kwargs.setdefault("player", self.player_state)
        action_kwargs.setdefault("fleet_by_id", self.fleet_by_id)
        if action_id in {"buy_hull", "buy_module"}:
            from shipdock_inventory import generate_shipdock_inventory

            action_kwargs.setdefault(
                "inventory",
                generate_shipdock_inventory(self.world_seed, system.system_id, int(system.population)),
            )
        if action_id == "repair_ship":
            action_kwargs.setdefault("system_population", int(system.population))
        if action_id in {"buy_module", "sell_module", "sell_hull", "repair_ship"}:
            action_kwargs.setdefault("ship_id", self.player_state.active_ship_id)
        return action_kwargs

    def _is_market_scope_action(self, action_id: str) -> bool:
        return action_id in {"buy", "sell"}

    def _is_at_destination_root(self) -> bool:
        return self.player_state.current_location_id == self.player_state.current_destination_id

    def _require_market_location(self) -> None:
        location = self._current_location()
        if location is None:
            raise ValueError("not_in_location")
        if str(getattr(location, "location_type", "")) != "market":
            raise ValueError("not_in_market_location")

    def _run_customs_with_guard(
        self,
        *,
        context: EngineContext,
        kind: str,
        allow_repeat: bool = False,
        option_name: Any = None,
    ) -> dict[str, Any]:
        destination_id = self.player_state.current_destination_id
        turn = int(get_current_turn())
        same_turn_same_destination = (
            self.player_state.last_customs_turn == turn
            and self.player_state.last_customs_destination_id == destination_id
        )
        if same_turn_same_destination and not allow_repeat:
            blocked = {
                "blocked": True,
                "reason": "customs_already_processed_this_turn",
                "last_kind": self.player_state.last_customs_kind,
            }
            self._event(
                context,
                stage="customs_guard",
                subsystem="law_enforcement",
                detail=blocked,
            )
            return blocked

        outcome = self._run_law_checkpoint(
            context,
            trigger_type=TriggerType.CUSTOMS,
            option_name=str(option_name) if isinstance(option_name, str) else None,
        )
        self.player_state.last_customs_turn = turn
        self.player_state.last_customs_destination_id = destination_id
        self.player_state.last_customs_kind = kind
        return {"blocked": False, "kind": kind, "outcome": outcome}

    def _market_price_rows(self, *, action: str) -> list[dict[str, Any]]:
        destination = self._current_destination()
        if destination is None:
            raise ValueError("no_current_destination")
        market = getattr(destination, "market", None)
        if market is None:
            raise ValueError("market_not_available")
        system = self.sector.get_system(self.player_state.current_system_id)
        if system is None:
            raise ValueError("current_system_not_found")
        government = self.government_registry.get_government(system.government_id)
        holdings = self.player_state.cargo_by_ship.get("active", {})

        rows: list[dict[str, Any]] = []
        candidates: set[str] = set()
        if action == "buy":
            for category in market.categories.values():
                for good in list(category.produced) + list(category.consumed) + list(category.neutral):
                    candidates.add(good.sku)
        else:
            for sku in sorted(holdings):
                if int(holdings.get(sku, 0)) > 0:
                    candidates.add(sku)

        for sku in sorted(candidates):
            quote = self._market_price_quote(
                destination=destination,
                government=government,
                sku=sku,
                action=action,
            )
            if quote is None:
                continue
            row = {
                "sku_id": sku,
                "display_name": self._display_name_for_sku(destination=destination, sku=sku),
                "legality": quote["legality"],
                "risk_tier": quote["risk_tier"],
                "unit_price": int(quote["unit_price"]),
                "available_units": None,
            }
            if action == "sell":
                row["player_has_units"] = int(holdings.get(sku, 0))
            rows.append(row)
        return rows

    def _market_row_by_sku(self, *, action: str, sku_id: str) -> dict[str, Any] | None:
        for row in self._market_price_rows(action=action):
            if row.get("sku_id") == sku_id:
                return row
        return None

    def _market_price_quote(
        self,
        *,
        destination: Destination,
        government: Any,
        sku: str,
        action: str,
    ) -> dict[str, Any] | None:
        market = destination.market
        if market is None:
            return None
        try:
            good = self.catalog.good_by_sku(sku)
            tags = set(good.tags)
            if isinstance(good.possible_tag, str):
                tags.add(good.possible_tag)
        except KeyError:
            tags = set()
            if "_" in sku:
                prefix, remainder = sku.split("_", 1)
                try:
                    base_good = self.catalog.good_by_sku(remainder)
                    tags = set(base_good.tags)
                    tags.add(prefix)
                except KeyError:
                    return None
            else:
                return None

        policy = self._law_engine.evaluate_policy(
            government_id=government.id,
            commodity=Commodity(commodity_id=sku, tags=tags),
            action=action,
            turn=int(get_current_turn()),
        )
        try:
            pricing = price_transaction(
                catalog=self.catalog,
                market=market,
                government=government,
                policy=policy,
                sku=sku,
                action=action,
                world_seed=self.world_seed,
                system_id=self.player_state.current_system_id,
                scarcity_modifier=1.0,
                ship=self._active_ship(),
                world_state_engine=self._world_state_engine(),
            )
        except Exception:  # noqa: BLE001
            return None
        return {
            "unit_price": int(round(float(pricing.final_price))),
            "legality": str(pricing.legality.value),
            "risk_tier": str(pricing.risk_tier.value),
        }

    def _display_name_for_sku(self, *, destination: Destination, sku: str) -> str:
        market = destination.market
        if market is not None:
            for category in market.categories.values():
                for good in list(category.produced) + list(category.consumed) + list(category.neutral):
                    if good.sku == sku:
                        return str(good.name)
        try:
            return str(self.catalog.good_by_sku(sku).name)
        except KeyError:
            return sku

    def _ensure_cargo_capacity_for_add(self, quantity: int) -> None:
        ship = self._active_ship()
        capacity = int(ship.get_effective_physical_capacity())
        if capacity <= 0:
            return
        current_units = 0
        holdings = self.player_state.cargo_by_ship.get("active", {})
        for sku in holdings:
            current_units += int(holdings.get(sku, 0))
        if current_units + int(quantity) > capacity:
            raise ValueError("cargo_capacity_exceeded")

    def _system_market_payloads(self, system: System | None) -> list[dict[str, Any]]:
        if system is None:
            return []
        payloads: list[dict[str, Any]] = []
        for destination in sorted(system.destinations, key=lambda entry: entry.destination_id):
            market = destination.market
            if market is None:
                continue
            categories: dict[str, Any] = {}
            for category_id in sorted(market.categories):
                category = market.categories[category_id]
                categories[category_id] = {
                    "produced": [entry.sku for entry in category.produced],
                    "consumed": [entry.sku for entry in category.consumed],
                    "neutral": [entry.sku for entry in category.neutral],
                }
            payloads.append({"categories": categories})
        return payloads

    def _pursuit_ships_for_spec(self, spec: Any) -> tuple[dict[str, Any], dict[str, Any]]:
        player_ship = self._active_ship()
        player_state = {
            "speed": 3,
            "pilot_skill": 3,
            "engine_band": 3,
            "tr_band": 3,
            "cloaking_device": False,
            "interdiction_device": False,
        }
        modules = list(player_ship.persistent_state.get("module_instances", []))
        for module in modules:
            module_id = str(module.get("module_id", ""))
            if "cloak" in module_id:
                player_state["cloaking_device"] = True
            if "interdict" in module_id:
                player_state["interdiction_device"] = True

        system = self.sector.get_system(self.player_state.current_system_id)
        if system is None:
            return player_state, player_state
        npc_state = generate_npc_ship(
            world_seed=self.world_seed,
            system_id=system.system_id,
            system_population=int(system.population),
            encounter_id=str(spec.encounter_id),
            encounter_subtype=str(spec.subtype_id),
        )
        npc_ship = {
            "speed": 3,
            "pilot_skill": 3,
            "engine_band": 3,
            "tr_band": int(getattr(spec, "threat_rating_tr", 3) or 3),
            "cloaking_device": False,
            "interdiction_device": False,
        }
        for module in list(npc_state.get("module_instances", [])):
            module_id = str(module.get("module_id", ""))
            if "cloak" in module_id:
                npc_ship["cloaking_device"] = True
            if "interdict" in module_id:
                npc_ship["interdiction_device"] = True
        if str(getattr(spec, "initiative", "")) == "npc":
            return npc_ship, player_state
        return npc_ship, player_state


def _parse_player_option(option_name: str | None) -> PlayerOption | None:
    if option_name is None:
        return None
    normalized = option_name.strip().upper()
    if normalized in {"SUBMIT", "FLEE", "ATTACK", "BRIBE"}:
        return PlayerOption[normalized]
    return None


def _law_outcome_payload(outcome: Any) -> dict[str, Any] | None:
    if outcome is None:
        return None
    return {
        "escaped": bool(outcome.escaped),
        "arrested": bool(outcome.arrested),
        "dead": bool(outcome.dead),
        "market_access_denied": bool(outcome.market_access_denied),
        "ship_lost": bool(outcome.ship_lost),
        "warrant_issued": bool(outcome.warrant_issued),
        "fines_added": int(outcome.fines_added),
        "rep_delta": int(outcome.rep_delta),
        "heat_delta": int(outcome.heat_delta),
        "detention_tier": outcome.detention_tier,
    }


def _jsonable(value: Any) -> Any:
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    if isinstance(value, list):
        return [_jsonable(entry) for entry in value]
    if isinstance(value, tuple):
        return [_jsonable(entry) for entry in value]
    if isinstance(value, dict):
        return {str(key): _jsonable(val) for key, val in value.items()}
    if hasattr(value, "value"):
        return str(value.value)
    if hasattr(value, "__dict__"):
        return _jsonable(dict(value.__dict__))
    return str(value)


def _read_version() -> str:
    version_path = Path(__file__).resolve().parents[1] / "VERSION"
    if not version_path.exists():
        return "0.0.0"
    content = version_path.read_text(encoding="utf-8", errors="replace")
    for line in content.splitlines():
        if line.startswith("Version:"):
            return line.split("Version:", 1)[1].strip()
    return "0.0.0"


def run_step_as_json(engine: GameEngine, command: dict[str, Any]) -> str:
    return json.dumps(engine.execute(command), sort_keys=True)
