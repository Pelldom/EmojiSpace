from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
import hashlib
import json
import math
import random
from typing import Any, Union

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
    dispatch_location_action,
    dispatch_destination_action,
    destination_actions,
    destination_has_datanet_service,
    dispatch_player_action,
)
from law_enforcement import (
    CargoSnapshot,
    PlayerOption,
    TriggerType,
    band_index_from_1_100,
    enforcement_checkpoint,
)
from market_pricing import price_transaction
from mission_factory import create_mission
from mission_generator import select_weighted_mission_type
from mission_manager import MissionManager
from mission_entity import MissionState
from mission_core import MissionCore
from npc_ship_generator import generate_npc_ship
from npc_entity import NPCEntity, NPCPersistenceTier
from npc_placement import resolve_npcs_for_location
from npc_registry import NPCRegistry
from player_state import PlayerState
from pursuit_resolver import resolve_pursuit
from reaction_engine import get_npc_outcome
from reward_applicator import apply_materialized_reward
from reward_materializer import materialize_reward
from ship_assembler import assemble_ship, compute_hull_max_from_ship_state
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
from logger import Logger


ENGINE_STREAM_NAME = "engine_orchestration"
WAREHOUSE_CAPACITY_COST_PER_TURN = 2


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
    parameters: list[Union[str, dict[str, Any]]] = field(default_factory=list)


class GameEngine:
    def __init__(self, world_seed: int, config: dict | None = None) -> None:
        self.world_seed = int(world_seed)
        self.config = dict(config or {})
        self._version = self.config.get("version", _read_version())
        self._silent_logger = _SilentLogger()
        self._logger = Logger(version=self._version)
        self._logging_enabled = False
        self._log_path: str | None = None

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
        # Fog-of-war correction: the player starts physically present in a system/destination,
        # so both must be marked discovered at initialization.
        start_system_marked = False
        start_destination_marked = False
        if isinstance(self.player_state.current_system_id, str) and self.player_state.current_system_id:
            before = len(self.player_state.visited_system_ids)
            self.player_state.visited_system_ids.add(self.player_state.current_system_id)
            start_system_marked = len(self.player_state.visited_system_ids) > before
        if isinstance(self.player_state.current_destination_id, str) and self.player_state.current_destination_id:
            before = len(self.player_state.visited_destination_ids)
            self.player_state.visited_destination_ids.add(self.player_state.current_destination_id)
            start_destination_marked = len(self.player_state.visited_destination_ids) > before
        self._pending_initialization_event = {
            "starting_system_marked_visited": bool(start_system_marked),
            "starting_destination_marked_visited": bool(start_destination_marked),
        }
        self.fleet_by_id = self._build_default_fleet()

        self.time_engine = TimeEngine(
            logger=None,
            world_seed=self.world_seed,
            sector=self.sector,
            player_state=self.player_state,
            event_frequency_percent=int(self.config.get("event_frequency_percent", 8)),
        )
        self._active_encounters: list[Any] = []
        self._mission_manager = MissionManager()
        self._mission_core = MissionCore(self._mission_manager)
        # DIAGNOSTIC: Log mission_manager instance ID at engine init (will be logged when logging is enabled)
        # Note: Logger may not be initialized yet, so we log this in _execute_set_logging
        # Initialize persistent mission offer storage in player_state (duck-typed)
        # mission_offers_by_location is the authoritative source of truth: dict[str, list[str]]
        if not hasattr(self.player_state, "mission_offers_by_location"):
            self.player_state.mission_offers_by_location = {}
        self._npc_registry = NPCRegistry()
        self._location_npc_ids: dict[str, list[str]] = {}
        # Mission offer caches removed - player_state.mission_offers_by_location is the only authoritative source

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
            elif command_type == "list_location_npcs":
                self._execute_list_location_npcs(context)
            elif command_type == "list_npc_interactions":
                self._execute_list_npc_interactions(context, payload)
            elif command_type == "npc_interact":
                self._execute_npc_interact(context, payload)
            elif command_type == "list_destination_actions":
                self._execute_list_destination_actions(context)
            elif command_type == "destination_action":
                self._execute_destination_action(context, payload)
            elif command_type == "mission_discuss":
                # Internal MissionCore API - not a location action
                mission_id = payload.get("mission_id")
                if not isinstance(mission_id, str) or not mission_id:
                    raise ValueError("mission_discuss requires mission_id")
                # DIAGNOSTIC: Log mission_manager instance ID during mission_discuss
                if self._logging_enabled and self._logger is not None:
                    self._logger.log(
                        turn=int(get_current_turn()),
                        action="mission_discuss_instance_check",
                        state_change=f"mission_manager_id={id(self._mission_manager)} mission_id={mission_id}"
                    )
                result = self._mission_core.get_details(mission_id)
                self._event(
                    context,
                    stage="mission",
                    subsystem="mission_core",
                    detail={"action_id": "mission_discuss", "result": result},
                )
            elif command_type == "mission_accept":
                # Internal MissionCore API - not a location action
                location = self._current_location()
                if location is None:
                    raise ValueError("not_in_location")
                location_id = str(getattr(location, "location_id", "") or "")
                location_type = str(getattr(location, "location_type", "") or "")
                mission_id = payload.get("mission_id")
                if not isinstance(mission_id, str) or not mission_id:
                    raise ValueError("mission_accept requires mission_id")
                # DIAGNOSTIC: Log mission_manager instance ID during mission_accept
                if self._logging_enabled and self._logger is not None:
                    self._logger.log(
                        turn=int(get_current_turn()),
                        action="mission_accept_instance_check",
                        state_change=f"mission_manager_id={id(self._mission_manager)} mission_id={mission_id} location_id={location_id}"
                    )
                # Validate against persisted offers (no regeneration)
                # Source of truth: player_state.mission_offers_by_location
                offered_ids = self.player_state.mission_offers_by_location.get(location_id, [])
                if mission_id not in offered_ids:
                    raise ValueError("mission_not_offered_here")
                accepted, error_reason = self._mission_core.accept(
                    mission_id=mission_id,
                    player=self.player_state,
                    location_id=location_id,
                    location_type=location_type,
                    ship=self._active_ship(),
                    logger=self._logger if self._logging_enabled else None,
                    turn=int(get_current_turn()),
                    create_contact_npc_callback=self._create_mission_contact_npc,
                )
                if not accepted:
                    # Raise with specific error reason
                    if error_reason is not None:
                        raise ValueError(error_reason)
                    raise ValueError("mission_accept_failed")
                
                # Remove accepted mission from persistent storage
                if location_id in self.player_state.mission_offers_by_location:
                    if mission_id in self.player_state.mission_offers_by_location[location_id]:
                        self.player_state.mission_offers_by_location[location_id].remove(mission_id)
                
                self._event(
                    context,
                    stage="mission",
                    subsystem="mission_core",
                    detail={"action_id": "mission_accept", "mission_id": mission_id, "accepted": True},
                )
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
            elif command_type == "shipdock_hull_list":
                self._execute_shipdock_hull_list(context)
            elif command_type == "shipdock_module_list":
                self._execute_shipdock_module_list(context)
            elif command_type == "shipdock_ship_list":
                self._execute_shipdock_ship_list(context)
            elif command_type == "shipdock_installed_modules_list":
                self._execute_shipdock_installed_modules_list(context, payload)
            elif command_type == "get_player_profile":
                self._execute_get_player_profile(context)
            elif command_type == "get_system_profile":
                self._execute_get_system_profile(context)
            elif command_type == "get_destination_profile":
                self._execute_get_destination_profile(context)
            elif command_type == "encounter_action":
                self._execute_encounter_action(context, payload)
            elif command_type == "warehouse_cancel":
                self._execute_warehouse_cancel(context, payload)
            elif command_type == "set_logging":
                self._execute_set_logging(context, payload)
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

        # Capture credits before travel for bankruptcy warning safety
        credits_before_travel = int(self.player_state.credits)

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
        self.player_state.visited_system_ids.add(target_system_id)
        if isinstance(target_destination_id, str):
            self.player_state.visited_destination_ids.add(target_destination_id)
        active_ship.current_system_id = target_system_id
        active_ship.current_destination_id = target_destination_id
        active_ship.destination_id = target_destination_id

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

        # Travel safety: Set bankruptcy warning only after arrival if credits reached 0 during travel
        if self.player_state.credits == 0 and self.player_state.bankruptcy_warning_turn is None:
            current_turn = int(get_current_turn())
            self.player_state.bankruptcy_warning_turn = current_turn

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

    def _execute_warehouse_cancel(self, context: EngineContext, payload: dict[str, Any]) -> None:
        destination_id = payload.get("destination_id")
        if not isinstance(destination_id, str) or not destination_id:
            raise ValueError("warehouse_cancel requires destination_id.")
        warehouse = self.player_state.warehouses.pop(destination_id, None)
        if not isinstance(warehouse, dict):
            self._event(
                context,
                stage="warehouse_cancel",
                subsystem="interaction_layer",
                detail={"destination_id": destination_id, "cancelled": False, "reason": "warehouse_not_found"},
            )
            return
        forfeited_goods = self._warehouse_goods(warehouse)
        self._event(
            context,
            stage="warehouse_cancel",
            subsystem="interaction_layer",
            detail={
                "destination_id": destination_id,
                "cancelled": True,
                "forfeited_goods": forfeited_goods,
                "forfeited_units": int(sum(forfeited_goods.values())),
                "capacity_removed": int(self._warehouse_capacity(warehouse)),
            },
        )

    def _execute_set_logging(self, context: EngineContext, payload: dict[str, Any]) -> None:
        enabled = bool(payload.get("enabled", False))
        default_path = str(Path(__file__).resolve().parents[1] / "logs" / f"gameplay_seed_{self.world_seed}.log")
        requested_path = payload.get("log_path")
        log_path = str(requested_path) if isinstance(requested_path, str) and requested_path else default_path
        truncate = bool(payload.get("truncate", False))
        configured_path = self._logger.configure_file_logging(enabled=enabled, log_path=log_path, truncate=truncate)
        self._logging_enabled = bool(enabled and configured_path)
        self._log_path = configured_path if self._logging_enabled else None
        # DIAGNOSTIC: Log mission_manager instance ID when logging is enabled
        if enabled and self._logger is not None:
            self._logger.log(
                turn=int(get_current_turn()),
                action="engine_init",
                state_change=f"mission_manager_id={id(self._mission_manager)}"
            )
        if self._logging_enabled and isinstance(getattr(self, "_pending_initialization_event", None), dict):
            try:
                self._logger.log(
                    turn=int(get_current_turn()),
                    action="engine:initialization",
                    state_change=json.dumps(
                        {
                            "subsystem": "engine",
                            "stage": "initialization",
                            "detail": dict(self._pending_initialization_event),
                        },
                        sort_keys=True,
                        ensure_ascii=True,
                    ),
                )
            except Exception:  # noqa: BLE001
                pass
            self._pending_initialization_event = None
        self._event(
            context,
            stage="logging",
            subsystem="engine",
            detail={
                "enabled": bool(self._logging_enabled),
                "log_path": self._log_path,
                "truncate": bool(truncate),
            },
        )

    def _execute_warehouse_rent(self, context: EngineContext, kwargs: dict[str, Any]) -> None:
        destination_id = self._current_destination_id_required()
        units = kwargs.get("units")
        if not isinstance(units, int) or units <= 0:
            raise ValueError("warehouse_rent requires positive integer units.")
        warehouse = self._ensure_warehouse_entry(destination_id)
        before_capacity = int(warehouse.get("capacity", 0) or 0)
        warehouse["capacity"] = before_capacity + int(units)
        self._event(
            context,
            stage="location_action",
            subsystem="interaction_layer",
            detail={
                "action_id": "warehouse_rent",
                "result_summary": {
                    "result_ok": True,
                    "destination_id": destination_id,
                    "units_rented": int(units),
                    "capacity_before": before_capacity,
                    "capacity_after": int(warehouse.get("capacity", 0)),
                    "cost_per_turn_per_capacity": int(WAREHOUSE_CAPACITY_COST_PER_TURN),
                },
                "result": {"ok": True, "reason": "ok"},
            },
        )

    def _execute_warehouse_deposit(self, context: EngineContext, kwargs: dict[str, Any]) -> None:
        destination_id = self._current_destination_id_required()
        sku_id = kwargs.get("sku_id")
        quantity = kwargs.get("quantity")
        if not isinstance(sku_id, str) or not sku_id:
            raise ValueError("warehouse_deposit requires sku_id.")
        if not isinstance(quantity, int) or quantity <= 0:
            raise ValueError("warehouse_deposit requires positive integer quantity.")
        location = self._current_location()
        result = dispatch_location_action(
            "warehouse_deposit",
            location_type=str(getattr(location, "location_type", "") or ""),
            payload={
                "player": self.player_state,
                "destination_id": destination_id,
                "sku_id": sku_id,
                "quantity": int(quantity),
            },
        )
        if result.get("ok") is not True:
            raise ValueError(str(result.get("reason", "warehouse_deposit_failed")))
        summary = result.get("result_summary", {})
        self._event(
            context,
            stage="location_action",
            subsystem="interaction_layer",
            detail={
                "action_id": "warehouse_deposit",
                "result_summary": summary,
                "result": {"ok": True, "reason": "ok"},
            },
        )

    def _execute_warehouse_withdraw(self, context: EngineContext, kwargs: dict[str, Any]) -> None:
        destination_id = self._current_destination_id_required()
        sku_id = kwargs.get("sku_id")
        quantity = kwargs.get("quantity")
        if not isinstance(sku_id, str) or not sku_id:
            raise ValueError("warehouse_withdraw requires sku_id.")
        if not isinstance(quantity, int) or quantity <= 0:
            raise ValueError("warehouse_withdraw requires positive integer quantity.")
        location = self._current_location()
        active_ship = self._active_ship()
        cargo_capacity_value = int(getattr(active_ship, "get_effective_physical_capacity", lambda: 0)() or 0)
        cargo_capacity = cargo_capacity_value if cargo_capacity_value > 0 else None
        result = dispatch_location_action(
            "warehouse_withdraw",
            location_type=str(getattr(location, "location_type", "") or ""),
            payload={
                "player": self.player_state,
                "destination_id": destination_id,
                "sku_id": sku_id,
                "quantity": int(quantity),
                "cargo_capacity": cargo_capacity,
            },
        )
        if result.get("ok") is not True:
            raise ValueError(str(result.get("reason", "warehouse_withdraw_failed")))
        summary = result.get("result_summary", {})
        self._event(
            context,
            stage="location_action",
            subsystem="interaction_layer",
            detail={
                "action_id": "warehouse_withdraw",
                "result_summary": summary,
                "result": {"ok": True, "reason": "ok"},
            },
        )

    def _mission_rng_for_location(self, *, location_id: str, turn: int | None = None) -> random.Random:
        # Deterministic RNG for mission generation (turn parameter kept for backward compatibility but not used)
        seed_value = self.world_seed
        parts = [self.player_state.current_system_id, self.player_state.current_destination_id or "", location_id]
        # Note: turn is no longer used for mission generation to ensure persistence
        for part in parts:
            for char in str(part):
                seed_value = (seed_value * 31 + ord(char)) % (2**32)
        return random.Random(seed_value)

    def _mission_candidates(self) -> list[dict[str, Any]]:
        return [
            {"mission_type_id": "delivery", "base_weight": 1.0, "mission_tags": ["data"]},
            {"mission_type_id": "recovery", "base_weight": 1.0, "mission_tags": ["industrial"]},
            {"mission_type_id": "escort", "base_weight": 1.0, "mission_tags": ["essential"]},
        ]

    def _ensure_location_mission_offers(self, *, location_id: str) -> list[str]:
        """Ensure mission offers exist for a location.
        
        Source of truth: player_state.mission_offers_by_location (dict[str, list[str]])
        Offers are generated ONCE per location and persist until explicitly removed.
        NO implicit regeneration based on turn or any other condition.
        """
        # If location_id exists in player_state.mission_offers_by_location, return those mission_ids
        if location_id in self.player_state.mission_offers_by_location:
            mission_ids = self.player_state.mission_offers_by_location[location_id]
            # Return missions from MissionManager registry using those mission_ids
            # Filter to only return missions that still exist and are OFFERED
            valid_mission_ids = []
            for mission_id in mission_ids:
                mission = self._mission_manager.missions.get(mission_id)
                if mission is not None and mission.mission_state == MissionState.OFFERED:
                    valid_mission_ids.append(mission_id)
            
            # Update storage if any missions were removed (e.g., accepted elsewhere)
            if len(valid_mission_ids) != len(mission_ids):
                self.player_state.mission_offers_by_location[location_id] = valid_mission_ids
            
            return valid_mission_ids
        
        # No offers exist - generate ONCE
        # Get destination population for deterministic mission count
        destination = self._current_destination()
        population = int(getattr(destination, "population", 0) or 0) if destination else 0
        max_offers = population + 1
        
        # Deterministic mission count based on location (no turn dependency)
        rng = self._mission_rng_for_location(location_id=location_id, turn=None)
        mission_count = rng.randint(0, max_offers)
        
        # Generate new mission offers
        offered_ids: list[str] = []
        for index in range(mission_count):
            mission_type, _ = select_weighted_mission_type(
                eligible_missions=self._mission_candidates(),
                rng=rng,
                world_state_engine=self._world_state_engine(),
                system_id=self.player_state.current_system_id,
            )
            mission_type_id = mission_type if isinstance(mission_type, str) and mission_type else "delivery"
            # Deterministic mission_id seed (no turn dependency for persistence)
            mission = create_mission(
                source_type="system",
                source_id=f"{location_id}:{index}",
                system_id=self.player_state.current_system_id,
                destination_id=self.player_state.current_destination_id,
                mission_type=mission_type_id,
                mission_tier=1 + int(rng.randint(0, 2)),
                persistence_scope="ephemeral",
                objectives=[f"{mission_type_id}:complete_objective"],
                rewards=[{"type": "credits", "amount": 100 + (index * 50)}],
            )
            # Set location_id on mission for location matching
            mission.location_id = location_id
            mission.mission_contact_seed = f"{self.world_seed}|{self.player_state.current_system_id}|{location_id}|{mission.mission_id}|contact"
            self._mission_manager.offer(mission)
            offered_ids.append(mission.mission_id)
        
        # Store mission_ids in player_state.mission_offers_by_location[location_id]
        self.player_state.mission_offers_by_location[location_id] = list(offered_ids)
        return offered_ids

    def _mission_rows_for_location(self, *, location_id: str, location_type: str | None = None) -> list[dict[str, Any]]:
        mission_ids = self._ensure_location_mission_offers(location_id=location_id)
        rows: list[dict[str, Any]] = []
        for mission_id in mission_ids:
            mission = self._mission_manager.missions.get(mission_id)
            if mission is None:
                continue
            row = {
                "mission_id": mission.mission_id,
                "mission_type": mission.mission_type,
                "mission_tier": int(mission.mission_tier),
                "mission_state": str(mission.mission_state),
                "rewards": list(mission.rewards),
            }
            # Add giver information for Bar locations only
            if location_type == "bar" and mission.mission_contact_seed is not None:
                npc_hash = hashlib.md5(mission.mission_contact_seed.encode()).hexdigest()[:8]
                giver_npc_id = f"NPC-MSN-{npc_hash}"
                row["giver_npc_id"] = giver_npc_id
                row["giver_display_name"] = f"Mission Contact ({mission.mission_type})"
            rows.append(row)
        return rows

    def _execute_mission_list(self, context: EngineContext) -> None:
        location = self._current_location()
        if location is None:
            raise ValueError("not_in_location")
        location_id = str(getattr(location, "location_id", "") or "")
        if not location_id:
            raise ValueError("invalid_location")
        location_type = str(getattr(location, "location_type", "") or "")
        # DIAGNOSTIC: Log mission_manager instance ID during mission_list
        if self._logging_enabled and self._logger is not None:
            self._logger.log(
                turn=int(get_current_turn()),
                action="mission_list_instance_check",
                state_change=f"mission_manager_id={id(self._mission_manager)} location_id={location_id}"
            )
        # Use MissionCore to list offered missions (uses persisted offers, no regeneration)
        rows = self._mission_core.list_offered(
            location_id=location_id,
            location_type=location_type,
            ensure_offers_callback=self._ensure_location_mission_offers,
        )
        # Deterministic regression safeguard: verify mission list consistency
        if self._logging_enabled and self._logger is not None:
            persisted_ids = self.player_state.mission_offers_by_location.get(location_id, [])
            row_ids = [row.get("mission_id") for row in rows if row.get("mission_id")]
            if set(row_ids) != set(persisted_ids):
                self._logger.log(
                    turn=int(get_current_turn()),
                    action="mission_list_consistency_check",
                    state_change=f"location_id={location_id} persisted_count={len(persisted_ids)} row_count={len(row_ids)}"
                )
        self._event(
            context,
            stage="location_action",
            subsystem="mission",
            detail={"action_id": "mission_list", "missions": rows},
        )

    def _create_mission_contact_npc(self, *, mission_id: str, location_id: str) -> None:
        """Helper to create mission contact NPC for Bar locations."""
        mission = self._mission_manager.missions.get(mission_id)
        if mission is None:
            return
        if mission.mission_contact_seed is None or mission.mission_giver_npc_id is not None:
            return
        npc_hash = hashlib.md5(mission.mission_contact_seed.encode()).hexdigest()[:8]
        npc_id = f"NPC-MSN-{npc_hash}"
        system_id = self.player_state.current_system_id
        npc = NPCEntity(
            npc_id=npc_id,
            persistence_tier=NPCPersistenceTier.TIER_2,
            display_name=f"Mission Contact ({mission.mission_type})",
            current_location_id=location_id,
            current_system_id=system_id,
            role_tags=["mission_giver"],
        )
        logger = self._logger if self._logging_enabled else None
        turn = int(get_current_turn())
        self._npc_registry.add(npc, logger=logger, turn=turn)
        mission.mission_giver_npc_id = npc_id
        if logger is not None:
            logger.log(turn=turn, action="mission_contact_created", state_change=f"mission_id={mission_id} npc_id={npc_id}")

    def _execute_mission_accept(self, context: EngineContext, kwargs: dict[str, Any]) -> None:
        """Internal handler for mission acceptance (used by MissionCore)."""
        location = self._current_location()
        if location is None:
            raise ValueError("not_in_location")
        location_id = str(getattr(location, "location_id", "") or "")
        location_type = str(getattr(location, "location_type", "") or "")
        mission_id = kwargs.get("mission_id")
        if not isinstance(mission_id, str) or not mission_id:
            raise ValueError("mission_accept requires mission_id")
        # Validate against persisted offers (no regeneration)
        # Source of truth: player_state.mission_offers_by_location
        offered_ids = self.player_state.mission_offers_by_location.get(location_id, [])
        if mission_id not in offered_ids:
            raise ValueError("mission_not_offered_here")
        # Use MissionCore to accept mission
        accepted, error_reason = self._mission_core.accept(
            mission_id=mission_id,
            player=self.player_state,
            location_id=location_id,
            location_type=location_type,
            ship=self._active_ship(),
            logger=self._logger if self._logging_enabled else None,
            turn=int(get_current_turn()),
            create_contact_npc_callback=self._create_mission_contact_npc,
        )
        if not accepted:
            # Raise with specific error reason
            if error_reason is not None:
                raise ValueError(error_reason)
            raise ValueError("mission_accept_failed")
        
        # Remove accepted mission from persistent storage
        if location_id in self.player_state.mission_offers_by_location:
            if mission_id in self.player_state.mission_offers_by_location[location_id]:
                self.player_state.mission_offers_by_location[location_id].remove(mission_id)
        
        self._event(
            context,
            stage="location_action",
            subsystem="mission",
            detail={"action_id": "mission_accept", "mission_id": mission_id, "accepted": True},
        )

    def _execute_bar_talk(self, context: EngineContext) -> None:
        self._event(
            context,
            stage="location_action",
            subsystem="interaction_layer",
            detail={"action_id": "bar_talk", "result": {"ok": True, "reason": "ok"}},
        )

    def _execute_bar_rumors(self, context: EngineContext) -> None:
        bartender = self._role_npc_for_current_location("bartender")
        npc_id = str(getattr(bartender, "npc_id", "") or "NPC-BARTENDER")
        result = self._build_bartender_rumor_payload(npc_id=npc_id)
        self._event(
            context,
            stage="location_action",
            subsystem="interaction_layer",
            detail={"action_id": "bar_rumors", "result": result},
        )

    def _execute_bar_hire_crew(self, context: EngineContext) -> None:
        """
        Hire crew from bar location.
        
        Requirements:
        - NPC must be is_crew=True and persistence_tier=TIER_2
        - Ship must have available crew capacity
        - Player must have sufficient credits
        """
        location = self._current_location()
        if location is None:
            raise ValueError("not_in_location")
        location_id = str(getattr(location, "location_id", "") or "")
        location_type = str(getattr(location, "location_type", "") or "")
        
        if location_type != "bar":
            raise ValueError("bar_location_required")
        
        # Get available crew at this location
        available_crew = [
            npc for npc in self._list_current_location_npcs()
            if isinstance(npc, NPCEntity) and npc.is_crew and npc.persistence_tier == NPCPersistenceTier.TIER_2
            and npc.current_ship_id is None  # Not already hired
        ]
        
        if not available_crew:
            self._event(
                context,
                stage="location_action",
                subsystem="interaction_layer",
                detail={"action_id": "bar_hire_crew", "result": {"ok": False, "reason": "no_crew_available"}},
            )
            return
        
        # For now, hire the first available crew member
        # TODO: In future, could add selection UI
        crew_npc = available_crew[0]
        
        # Validate NPC contract
        if not crew_npc.is_crew:
            raise ValueError("npc_not_crew")
        if crew_npc.persistence_tier != NPCPersistenceTier.TIER_2:
            raise ValueError("crew_must_be_tier_2")
        
        # Get active ship
        active_ship = self._active_ship()
        
        # Check crew capacity
        current_crew_count = len(active_ship.crew)
        if current_crew_count >= active_ship.crew_capacity:
            self._event(
                context,
                stage="location_action",
                subsystem="interaction_layer",
                detail={"action_id": "bar_hire_crew", "result": {"ok": False, "reason": "crew_capacity_exceeded"}},
            )
            return
        
        # Check credits
        hire_cost = int(crew_npc.hire_cost)
        if int(self.player_state.credits) < hire_cost:
            self._event(
                context,
                stage="location_action",
                subsystem="interaction_layer",
                detail={"action_id": "bar_hire_crew", "result": {"ok": False, "reason": "insufficient_credits", "required": hire_cost, "available": int(self.player_state.credits)}},
            )
            return
        
        # Success: hire the crew
        credits_before = int(self.player_state.credits)
        self.player_state.credits = max(0, credits_before - hire_cost)
        
        # Update NPC location/ship assignment
        crew_npc.current_location_id = None
        crew_npc.current_ship_id = active_ship.ship_id
        
        # Update registry
        self._npc_registry.update(crew_npc, logger=self._logger if self._logging_enabled else None, turn=int(get_current_turn()))
        
        # Add to ship
        active_ship.add_crew(crew_npc)
        
        self._event(
            context,
            stage="location_action",
            subsystem="interaction_layer",
            detail={
                "action_id": "bar_hire_crew",
                "result": {
                    "ok": True,
                    "reason": "ok",
                    "npc_id": crew_npc.npc_id,
                    "crew_role_id": crew_npc.crew_role_id,
                    "hire_cost": hire_cost,
                    "daily_wage": int(crew_npc.daily_wage),
                    "credits_before": credits_before,
                    "credits_after": int(self.player_state.credits),
                },
            },
        )

    def _execute_admin_talk(self, context: EngineContext) -> None:
        self._event(
            context,
            stage="location_action",
            subsystem="interaction_layer",
            detail={"action_id": "admin_talk", "result": {"ok": True, "reason": "ok"}},
        )

    def _execute_admin_pay_fines(self, context: EngineContext) -> None:
        result = self._admin_pay_fines_result()
        self._event(
            context,
            stage="location_action",
            subsystem="law_enforcement",
            detail={"action_id": "admin_pay_fines", "result": result},
        )

    def _execute_admin_apply_license(self, context: EngineContext) -> None:
        self._event(
            context,
            stage="location_action",
            subsystem="law_enforcement",
            detail={"action_id": "admin_apply_license", "result": {"ok": False, "reason": "not_implemented"}},
        )

    def _execute_admin_turn_in(self, context: EngineContext) -> None:
        system_id = self.player_state.current_system_id
        warrants = list(self.player_state.warrants_by_system.get(system_id, []))
        if not warrants:
            result = {"ok": True, "reason": "no_warrants"}
        else:
            self.player_state.warrants_by_system[system_id] = []
            result = {"ok": True, "reason": "ok", "cleared_warrants": len(warrants)}
        self._event(
            context,
            stage="location_action",
            subsystem="law_enforcement",
            detail={"action_id": "admin_turn_in", "result": result},
        )

    def _execute_admin_mission_board(self, context: EngineContext) -> None:
        # Use existing mission_list logic for Administration
        self._execute_mission_list(context)

    def _execute_location_action(self, context: EngineContext, payload: dict[str, Any]) -> None:
        location = self._current_location()
        if location is None:
            raise ValueError("not_in_location")

        action_id = payload.get("action_id")
        if not isinstance(action_id, str) or not action_id:
            raise ValueError("location_action requires action_id.")
        kwargs = payload.get("kwargs") or payload.get("action_kwargs") or {}
        if not isinstance(kwargs, dict):
            raise ValueError("location_action.kwargs must be an object.")

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
        if action_id == "warehouse_rent":
            self._execute_warehouse_rent(context, kwargs)
            return
        if action_id == "warehouse_deposit":
            self._execute_warehouse_deposit(context, kwargs)
            return
        if action_id == "warehouse_withdraw":
            self._execute_warehouse_withdraw(context, kwargs)
            return
        if action_id == "mission_list":
            self._execute_mission_list(context)
            return
        # mission_accept and mission_discuss are internal-only, not exposed as location actions
        # They are accessed through MissionCore API
        if action_id == "bar_talk":
            self._execute_bar_talk(context)
            return
        if action_id == "bar_rumors":
            self._execute_bar_rumors(context)
            return
        if action_id == "bar_hire_crew":
            self._execute_bar_hire_crew(context)
            return
        if action_id == "admin_talk":
            self._execute_admin_talk(context)
            return
        if action_id == "admin_pay_fines":
            self._execute_admin_pay_fines(context)
            return
        if action_id == "admin_apply_license":
            self._execute_admin_apply_license(context)
            return
        if action_id == "admin_turn_in":
            self._execute_admin_turn_in(context)
            return
        if action_id == "admin_mission_board":
            self._execute_admin_mission_board(context)
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
            self.player_state.credits = max(0, int(result["credits"]))
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

    def _execute_list_location_npcs(self, context: EngineContext) -> None:
        npcs = self._list_current_location_npcs()
        rows = [self._npc_summary(npc) for npc in npcs]
        self._event(
            context,
            stage="location_npcs",
            subsystem="engine",
            detail={"location_id": self.player_state.current_location_id, "npcs": rows},
        )

    def _execute_list_npc_interactions(self, context: EngineContext, payload: dict[str, Any]) -> None:
        npc_id = payload.get("npc_id")
        if not isinstance(npc_id, str) or not npc_id:
            raise ValueError("list_npc_interactions requires npc_id")
        npc = self._npc_for_current_location(npc_id)
        if npc is None:
            raise ValueError("npc_not_in_location")
        role = self._npc_primary_role(npc)
        interactions = self._npc_interaction_rows_for_role(role)
        self._event(
            context,
            stage="npc_interactions",
            subsystem="interaction_layer",
            detail={"npc_id": npc_id, "role": role, "interactions": interactions},
        )

    def _execute_npc_interact(self, context: EngineContext, payload: dict[str, Any]) -> None:
        npc_id = payload.get("npc_id")
        interaction_id = payload.get("interaction_id")
        if not isinstance(npc_id, str) or not npc_id:
            raise ValueError("npc_interact requires npc_id")
        if not isinstance(interaction_id, str) or not interaction_id:
            raise ValueError("npc_interact requires interaction_id")
        npc = self._npc_for_current_location(npc_id)
        if npc is None:
            raise ValueError("npc_not_in_location")
        role = self._npc_primary_role(npc)
        allowed = {row["action_id"] for row in self._npc_interaction_rows_for_role(role)}
        if interaction_id not in allowed:
            raise ValueError("interaction_not_available_for_npc")

        result: dict[str, Any]
        if interaction_id == "npc_talk":
            result = {"ok": True, "text": self._npc_talk_text(npc=npc, role=role)}
        elif interaction_id == "bartender_rumors":
            result = self._build_bartender_rumor_payload(npc_id=npc_id)
        elif interaction_id == "admin_pay_fines":
            result = self._admin_pay_fines_result()
        elif interaction_id == "admin_apply_license":
            result = {"ok": False, "reason": "not_implemented"}
        elif interaction_id == "admin_turn_in":
            system_id = self.player_state.current_system_id
            warrants = list(self.player_state.warrants_by_system.get(system_id, []))
            if not warrants:
                result = {"ok": True, "reason": "no_warrants"}
            else:
                self.player_state.warrants_by_system[system_id] = []
                result = {"ok": True, "reason": "ok", "cleared_warrants": len(warrants)}
        elif interaction_id == "admin_mission_board":
            # Route to mission_list logic
            location = self._current_location()
            if location is None:
                raise ValueError("not_in_location")
            location_id = str(getattr(location, "location_id", "") or "")
            if not location_id:
                raise ValueError("invalid_location")
            location_type = str(getattr(location, "location_type", "") or "")
            rows = self._mission_rows_for_location(location_id=location_id, location_type=location_type)
            result = {"ok": True, "missions": rows}
        elif interaction_id == "mission_discuss":
            # State-aware mission discussion (NPC path) - uses MissionCore
            mission_id = self._mission_id_for_giver_npc_id(npc_id)
            if mission_id is None:
                raise ValueError("mission_not_found_for_giver")
            result = self._mission_core.get_details(mission_id)
        else:
            raise ValueError("unknown_npc_interaction")

        self._event(
            context,
            stage="npc_interaction",
            subsystem="interaction_layer",
            detail={"npc_id": npc_id, "interaction_id": interaction_id, "result": result},
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
            self.player_state.credits = max(0, int(result["credits"]))
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
        selected_location_id = str(getattr(selected_location, "location_id", "") or "")
        
        # Ensure mission offers exist for mission-capable locations (generated once and persisted)
        if location_type in {"bar", "administration"} and selected_location_id:
            # Offers are generated once per location and persist across engine re-init
            self._ensure_location_mission_offers(location_id=selected_location_id)
        
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
        # Ship remains at destination level, only player navigates to locations
        npcs = resolve_npcs_for_location(
            location_id=selected_location_id,
            location_type=location_type,
            system_id=self.player_state.current_system_id,
            registry=self._npc_registry,
            logger=self._logger if self._logging_enabled else None,
            turn=int(get_current_turn()),
        )
        self._location_npc_ids[selected_location_id] = sorted(
            {
                str(getattr(row, "npc_id", ""))
                for row in npcs
                if isinstance(getattr(row, "npc_id", None), str) and str(getattr(row, "npc_id", ""))
            }
        )
        self._event(
            context,
            stage="location_navigation",
            subsystem="engine",
            detail={
                "action": "enter_location",
                "location_id": selected_location_id,
                "location_type": location_type,
                "resolved_npc_ids": [getattr(row, "npc_id", None) for row in npcs],
            },
        )

    def _execute_return_to_destination(self, context: EngineContext) -> None:
        destination_id = self.player_state.current_destination_id
        self.player_state.current_location_id = destination_id
        active_ship = self._active_ship()
        # Ship remains at destination level, only player navigates to locations
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

    def _execute_shipdock_hull_list(self, context: EngineContext) -> None:
        """List available hulls at shipdock with prices."""
        destination = self._current_destination()
        if destination is None:
            raise ValueError("No current destination for shipdock_hull_list.")
        from interaction_resolvers import destination_has_shipdock_service
        if not destination_has_shipdock_service(destination):
            raise ValueError("Current location does not have shipdock service.")
        
        system = self.sector.get_system(self.player_state.current_system_id)
        if system is None:
            raise ValueError("No current system for shipdock_hull_list.")
        
        from shipdock_inventory import generate_shipdock_inventory
        inventory = generate_shipdock_inventory(
            self.world_seed,
            system.system_id,
            int(system.population),
            world_state_engine=self._world_state_engine(),
        )
        
        from data_loader import load_hulls
        from hull_utils import is_shipdock_sellable_hull
        hulls_data = load_hulls()
        hulls_by_id = {hull["hull_id"]: hull for hull in hulls_data.get("hulls", [])}
        
        rows = []
        for hull_entry in inventory.get("hulls", []):
            hull_id = hull_entry.get("hull_id", "")
            if not hull_id:
                continue
            hull_data = hulls_by_id.get(hull_id)
            if hull_data is None:
                continue
            
            # Defense in depth: apply shipdock eligibility filter
            if not is_shipdock_sellable_hull(hull_id, hull_data=hull_data):
                continue
            
            # Calculate price using pricing contract
            from market_pricing import price_hull_transaction
            pricing = price_hull_transaction(
                base_price_credits=int(hull_data.get("base_price_credits", 0)),
                hull_id=hull_id,
                system_id=system.system_id,
                transaction_type="buy",
                world_state_engine=self._world_state_engine(),
                logger=self._logger if self._logging_enabled else None,
                turn=int(get_current_turn()),
            )
            
            # C) Apply shipdock price variance multiplier (locked per market)
            final_price = pricing.final_price
            if destination.market is not None:
                final_price = final_price * destination.market.shipdock_price_multiplier
                final_price = max(1.0, round(final_price))  # Round and ensure minimum 1
            
            rows.append({
                "hull_id": hull_id,
                "display_name": hull_data.get("name", hull_id),
                "tier": int(hull_data.get("tier", 0)),
                "price": int(final_price),
            })
        
        self._event(
            context,
            stage="shipdock_hull_list",
            subsystem="shipdock",
            detail={"destination_id": self.player_state.current_destination_id, "rows": rows},
        )

    def _execute_shipdock_module_list(self, context: EngineContext) -> None:
        """List available modules at shipdock with prices."""
        destination = self._current_destination()
        if destination is None:
            raise ValueError("No current destination for shipdock_module_list.")
        from interaction_resolvers import destination_has_shipdock_service
        if not destination_has_shipdock_service(destination):
            raise ValueError("Current location does not have shipdock service.")
        
        system = self.sector.get_system(self.player_state.current_system_id)
        if system is None:
            raise ValueError("No current system for shipdock_module_list.")
        
        from shipdock_inventory import generate_shipdock_inventory
        inventory = generate_shipdock_inventory(
            self.world_seed,
            system.system_id,
            int(system.population),
            world_state_engine=self._world_state_engine(),
        )
        
        from data_loader import load_modules
        modules_data = load_modules()
        modules_by_id = {module["module_id"]: module for module in modules_data.get("modules", [])}
        
        rows = []
        for module_entry in inventory.get("modules", []):
            module_id = module_entry.get("module_id", "")
            if not module_id:
                continue
            module_data = modules_by_id.get(module_id)
            if module_data is None:
                continue
            
            # Calculate price using pricing contract
            from market_pricing import price_module_transaction
            pricing = price_module_transaction(
                base_price_credits=int(module_data.get("base_price_credits", 0)),
                module_id=module_id,
                system_id=system.system_id,
                transaction_type="buy",
                secondary_tags=[],
                world_state_engine=self._world_state_engine(),
                logger=self._logger if self._logging_enabled else None,
                turn=int(get_current_turn()),
            )
            
            # C) Apply shipdock price variance multiplier (locked per market)
            final_price = pricing.final_price
            if destination.market is not None:
                final_price = final_price * destination.market.shipdock_price_multiplier
                final_price = max(1.0, round(final_price))  # Round and ensure minimum 1
            
            rows.append({
                "module_id": module_id,
                "display_name": module_data.get("name", module_id),
                "slot_type": module_data.get("slot_type", ""),
                "price": int(pricing.final_price),
            })
        
        self._event(
            context,
            stage="shipdock_module_list",
            subsystem="shipdock",
            detail={"destination_id": self.player_state.current_destination_id, "rows": rows},
        )

    def _execute_shipdock_ship_list(self, context: EngineContext) -> None:
        """List owned ships eligible to sell at current destination."""
        destination = self._current_destination()
        if destination is None:
            raise ValueError("No current destination for shipdock_ship_list.")
        from interaction_resolvers import destination_has_shipdock_service, _ship_present_at_destination
        if not destination_has_shipdock_service(destination):
            raise ValueError("Current location does not have shipdock service.")
        
        destination_id = self.player_state.current_destination_id
        rows = []
        for ship_id in self.player_state.owned_ship_ids:
            ship = self.fleet_by_id.get(ship_id)
            if ship is None:
                continue
            if not _ship_present_at_destination(ship, self.player_state):
                continue
            
            from data_loader import load_hulls
            hulls_data = load_hulls()
            hull_data = None
            for hull in hulls_data.get("hulls", []):
                if hull.get("hull_id") == ship.model_id:
                    hull_data = hull
                    break
            
            if hull_data is None:
                continue
            
            # Calculate sell price
            system = self.sector.get_system(self.player_state.current_system_id)
            if system is None:
                continue
            
            from market_pricing import price_hull_transaction
            pricing = price_hull_transaction(
                base_price_credits=int(hull_data.get("base_price_credits", 0)),
                hull_id=ship.model_id,
                system_id=system.system_id,
                transaction_type="sell",
                world_state_engine=self._world_state_engine(),
                logger=self._logger if self._logging_enabled else None,
                turn=int(get_current_turn()),
            )
            
            rows.append({
                "ship_id": ship_id,
                "hull_id": ship.model_id,
                "display_name": f"{hull_data.get('name', ship.model_id)} ({ship_id})",
                "tier": int(hull_data.get("tier", 0)),
                "price": int(pricing.final_price),
            })
        
        self._event(
            context,
            stage="shipdock_ship_list",
            subsystem="shipdock",
            detail={"destination_id": destination_id, "rows": rows},
        )

    def _execute_shipdock_installed_modules_list(self, context: EngineContext, payload: dict[str, Any]) -> None:
        """List installed modules on a ship."""
        ship_id = payload.get("ship_id")
        if not isinstance(ship_id, str) or not ship_id:
            # Default to active ship
            ship_id = self.player_state.active_ship_id
        
        if not ship_id:
            raise ValueError("No ship_id provided and no active ship.")
        
        ship = self.fleet_by_id.get(ship_id)
        if ship is None:
            raise ValueError(f"Ship {ship_id} not found.")
        
        module_instances = ship.persistent_state.get("module_instances", [])
        if not isinstance(module_instances, list):
            module_instances = []
        
        from data_loader import load_modules
        modules_data = load_modules()
        modules_by_id = {module["module_id"]: module for module in modules_data.get("modules", [])}
        
        rows = []
        for instance in module_instances:
            if not isinstance(instance, dict):
                continue
            module_id = instance.get("module_id", "")
            if not module_id:
                continue
            module_data = modules_by_id.get(module_id)
            if module_data is None:
                continue
            
            # Calculate sell price
            destination = self._current_destination()
            if destination is None:
                continue
            system = self.sector.get_system(self.player_state.current_system_id)
            if system is None:
                continue
            
            secondary_tags = list(instance.get("secondary_tags", []))
            from market_pricing import price_module_transaction
            pricing = price_module_transaction(
                base_price_credits=int(module_data.get("base_price_credits", 0)),
                module_id=module_id,
                system_id=system.system_id,
                transaction_type="sell",
                secondary_tags=secondary_tags,
                world_state_engine=self._world_state_engine(),
                logger=self._logger if self._logging_enabled else None,
                turn=int(get_current_turn()),
            )
            
            rows.append({
                "module_id": module_id,
                "display_name": module_data.get("name", module_id),
                "slot_type": module_data.get("slot_type", ""),
                "price": int(pricing.final_price),
            })
        
        self._event(
            context,
            stage="shipdock_installed_modules_list",
            subsystem="shipdock",
            detail={"ship_id": ship_id, "rows": rows},
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
            destination = self._current_destination()
            if destination is None:
                raise ValueError("no_current_destination")
            system = self.sector.get_system(self.player_state.current_system_id)
            if system is None:
                raise ValueError("current_system_not_found")
            government = self.government_registry.get_government(system.government_id)
            quote = self._market_price_quote(
                destination=destination,
                government=government,
                sku=str(sku_id),
                action="buy",
            )
            if quote is None:
                raise ValueError("sku_not_available_for_buy")
            row = {
                "sku_id": sku_id,
                "display_name": self._display_name_for_sku(destination=destination, sku=sku_id),
                "legality": quote["legality"],
                "risk_tier": quote["risk_tier"],
                "unit_price": int(quote["unit_price"]),
                "available_units": None,
            }
        unit_price = int(row["unit_price"])
        total_cost = int(unit_price * quantity)
        credits_before = int(self.player_state.credits)
        if credits_before < total_cost:
            raise ValueError("insufficient_credits")
        self._ensure_cargo_capacity_for_add(quantity)

        holdings = self.player_state.cargo_by_ship.setdefault("active", {})
        holdings[sku_id] = int(holdings.get(sku_id, 0) + quantity)
        self.player_state.credits = max(0, credits_before - total_cost)
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
        self.player_state.credits = max(0, credits_before + total_gain)
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

    def _execute_get_player_profile(self, context: EngineContext) -> None:
        ship = self._active_ship()
        system_id = self.player_state.current_system_id
        reputation_score = int(self.player_state.reputation_by_system.get(system_id, 50))
        heat = int(self.player_state.heat_by_system.get(system_id, 0))
        notoriety_score = int(self.player_state.progression_tracks.get("notoriety", 0))
        insurance_cost = int(self._insurance_cost_per_turn())
        crew_wages = int(self._crew_wages_per_turn())
        warehouse_cost = int(self._warehouse_cost_per_turn())
        
        # Project ship information from assembler output
        hull_id = ship.model_id
        module_instances = list(ship.persistent_state.get("module_instances", []))
        degradation_state = ship.persistent_state.get("degradation_state", {"weapon": 0, "defense": 0, "engine": 0})
        assembled = assemble_ship(hull_id, module_instances, degradation_state)
        
        # Load hull data for tier, crew_capacity, and cargo base
        from data_loader import load_hulls
        hulls_data = load_hulls()
        hull_data = None
        for hull in hulls_data.get("hulls", []):
            if hull.get("hull_id") == hull_id:
                hull_data = hull
                break
        
        # Compute cargo capacities: base from hull + module bonuses from assembler
        cargo_base = hull_data.get("cargo", {}) if hull_data else {}
        physical_cargo_base = int(cargo_base.get("physical_base", 0))
        data_cargo_base = int(cargo_base.get("data_base", 0))
        utility_effects = assembled.get("ship_utility_effects", {})
        physical_cargo_capacity = physical_cargo_base + int(utility_effects.get("physical_cargo_bonus", 0))
        data_cargo_capacity = data_cargo_base + int(utility_effects.get("data_cargo_bonus", 0))
        
        # Get effective capacities (includes crew modifiers)
        effective_physical_capacity = int(ship.get_effective_physical_capacity())
        effective_data_capacity = int(ship.get_effective_data_capacity())
        
        # Extract subsystem bands from assembler
        bands = assembled.get("bands", {})
        effective_bands = bands.get("effective", {})
        
        # Extract crew list with IDs and wages
        crew_list = []
        for crew_member in ship.crew:
            if hasattr(crew_member, "npc_id") and hasattr(crew_member, "daily_wage"):
                crew_list.append({
                    "npc_id": str(crew_member.npc_id),
                    "daily_wage": int(crew_member.daily_wage),
                })
        
        ship_info = {
            "ship_id": ship.ship_id,
            "hull_id": hull_id,
            "model_id": hull_id,
            "tier": int(hull_data.get("tier", 1)) if hull_data else None,
            "crew_capacity": int(hull_data.get("crew_capacity", 0)) if hull_data else int(ship.crew_capacity),
            "crew_current": len(ship.crew),
            "physical_cargo_capacity": physical_cargo_capacity,
            "data_cargo_capacity": data_cargo_capacity,
            "effective_physical_cargo_capacity": effective_physical_capacity,
            "effective_data_cargo_capacity": effective_data_capacity,
            "fuel_capacity": int(ship.fuel_capacity),
            "current_fuel": int(ship.current_fuel),
            "subsystem_bands": {
                "weapon": int(effective_bands.get("weapon", 0)),
                "defense": int(effective_bands.get("defense", 0)),
                "engine": int(effective_bands.get("engine", 0)),
            },
            "installed_modules": [str(inst.get("module_id", "")) for inst in module_instances if isinstance(inst, dict)],
            "crew": crew_list,
        }
        
        self._event(
            context,
            stage="player_profile",
            subsystem="engine",
            detail={
                "credits": int(self.player_state.credits),
                "fuel_current": int(ship.current_fuel),
                "fuel_capacity": int(ship.fuel_capacity),
                "cargo_manifest": {
                    str(sku_id): int(quantity)
                    for sku_id, quantity in sorted(self.player_state.cargo_by_ship.get("active", {}).items())
                },
                "reputation_score": reputation_score,
                "reputation_band": int(band_index_from_1_100(reputation_score)),
                "heat": heat,
                "notoriety_score": notoriety_score,
                "notoriety_band": int(band_index_from_1_100(notoriety_score)),
                "arrest_state": self.player_state.arrest_state,
                "warrants": list(self.player_state.warrants_by_system.get(system_id, [])),
                "system_id": system_id,
                "destination_id": self.player_state.current_destination_id,
                "location_id": self.player_state.current_location_id,
                "turn": int(get_current_turn()),
                "insurance_cost_per_turn": insurance_cost,
                "crew_wages_per_turn": crew_wages,
                "warehouse_cost_per_turn": warehouse_cost,
                "total_recurring_cost_per_turn": int(insurance_cost + crew_wages + warehouse_cost),
                "warehouses": self._warehouse_profile_rows(),
                "ship": ship_info,
            },
        )

    def _execute_get_system_profile(self, context: EngineContext) -> None:
        system = self.sector.get_system(self.player_state.current_system_id)
        if system is None:
            raise ValueError("current_system_not_found")
        ship = self._active_ship()
        fuel_limit = int(ship.current_fuel)
        reachable: list[dict[str, Any]] = []
        for target in sorted(self.sector.systems, key=lambda entry: entry.system_id):
            if target.system_id == system.system_id:
                continue
            distance_ly = float(self._warp_distance_ly(origin=system, target=target))
            reachable.append(
                {
                    "system_id": target.system_id,
                    "name": target.name,
                    "distance_ly": distance_ly,
                    "in_range": bool(distance_ly <= float(fuel_limit)),
                }
            )

        active_situations = self._active_situation_rows_for_system(system_id=system.system_id)
        flags = self._system_flags_for_current_system()
        self._event(
            context,
            stage="system_profile",
            subsystem="engine",
            detail={
                "system_id": system.system_id,
                "name": system.name,
                "government_id": system.government_id,
                "population": int(system.population),
                "coordinates": {"x": float(system.x), "y": float(system.y)},
                "active_system_situations": active_situations,
                "active_system_flags": flags,
                "reachable_systems": reachable,
            },
        )

    def _execute_get_destination_profile(self, context: EngineContext) -> None:
        destination = self._current_destination()
        if destination is None:
            raise ValueError("current_destination_not_found")
        locations = sorted(
            list(getattr(destination, "locations", []) or []),
            key=lambda row: str(getattr(row, "location_id", "")),
        )
        crew_rows = self._active_crew_rows()
        mission_rows = self._active_mission_rows()
        self._event(
            context,
            stage="destination_profile",
            subsystem="engine",
            detail={
                "destination_id": destination.destination_id,
                "name": destination.display_name,
                "population": int(destination.population),
                "primary_economy": destination.primary_economy_id,
                "market_attached": bool(destination.market is not None),
                "locations": [
                    {
                        "location_id": getattr(row, "location_id", None),
                        "location_type": getattr(row, "location_type", None),
                    }
                    for row in locations
                ],
                "active_destination_situations": self._active_destination_situations(
                    destination_id=destination.destination_id
                ),
                "active_crew": crew_rows,
                "active_missions": mission_rows,
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
        allowed.add("list_location_npcs")
        allowed.add("list_npc_interactions")
        allowed.add("npc_interact")
        allowed.add("list_destination_actions")
        allowed.add("destination_action")
        allowed.add("enter_location")
        allowed.add("return_to_destination")
        allowed.add("get_market_profile")
        allowed.add("market_buy_list")
        allowed.add("market_sell_list")
        allowed.add("market_buy")
        allowed.add("market_sell")
        allowed.add("shipdock_hull_list")
        allowed.add("shipdock_module_list")
        allowed.add("shipdock_ship_list")
        allowed.add("shipdock_installed_modules_list")
        allowed.add("get_player_profile")
        allowed.add("get_system_profile")
        allowed.add("get_destination_profile")
        allowed.add("warehouse_cancel")
        allowed.add("set_logging")
        allowed.add("mission_discuss")
        allowed.add("mission_accept")
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
        event_payload = {
            "stage": stage,
            "world_seed": int(self.world_seed),
            "turn": int(get_current_turn()),
            "command_type": context.command_type,
            "subsystem": subsystem,
            "detail": _jsonable(detail),
        }
        context.events.append(event_payload)
        if self._logging_enabled:
            try:
                self._logger.log(
                    turn=int(get_current_turn()),
                    action=f"{subsystem}:{stage}",
                    state_change=json.dumps(event_payload, sort_keys=True, ensure_ascii=True),
                )
            except Exception:  # noqa: BLE001
                return

    def _advance_time(self, *, days: int, reason: str) -> Any:
        _set_player_action_context(True)
        try:
            result = advance_time(days=int(days), reason=reason)
        finally:
            _set_player_action_context(False)
        self._apply_recurring_costs(days_completed=int(result.days_completed))
        # Update bankruptcy warning after time advance completes
        self._update_bankruptcy_warning()
        return result

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
        """
        Enforce starting ship: Midge (civ_t1_midge) with no modules.
        
        This is deterministic and occurs only on new game initialization.
        All ship stats derive from assemble_ship() output.
        """
        hull_id = "civ_t1_midge"
        module_instances = []
        degradation_state = {"weapon": 0, "defense": 0, "engine": 0}
        
        assembled = assemble_ship(hull_id, module_instances, degradation_state)
        
        # Extract hull data for crew_capacity and cargo base
        from data_loader import load_hulls
        hulls_data = load_hulls()
        hull_data = None
        for hull in hulls_data.get("hulls", []):
            if hull.get("hull_id") == hull_id:
                hull_data = hull
                break
        
        if hull_data is None:
            raise ValueError(f"Hull data not found for {hull_id}")
        
        # Extract cargo capacities: base from hull + module bonuses from assembler
        cargo_base = hull_data.get("cargo", {})
        physical_cargo_base = int(cargo_base.get("physical_base", 0))
        data_cargo_base = int(cargo_base.get("data_base", 0))
        utility_effects = assembled.get("ship_utility_effects", {})
        physical_cargo_capacity = physical_cargo_base + int(utility_effects.get("physical_cargo_bonus", 0))
        data_cargo_capacity = data_cargo_base + int(utility_effects.get("data_cargo_bonus", 0))
        
        # Extract crew capacity from hull data
        crew_capacity = int(hull_data.get("crew_capacity", 0))
        
        # Extract subsystem bands from assembler
        bands = assembled.get("bands", {})
        effective_bands = bands.get("effective", {})
        
        ship = ShipEntity(
            ship_id="PLAYER-SHIP-001",
            model_id=hull_id,
            owner_id=self.player_state.player_id,
            owner_type="player",
            activity_state="active",
            destination_id=self.player_state.current_destination_id,
            current_system_id=self.player_state.current_system_id,
            current_destination_id=self.player_state.current_destination_id,
            fuel_capacity=int(assembled["fuel_capacity"]),
            current_fuel=int(assembled["fuel_capacity"]),
            crew_capacity=crew_capacity,
            physical_cargo_capacity=physical_cargo_capacity,
            data_cargo_capacity=data_cargo_capacity,
        )
        ship.persistent_state["module_instances"] = list(module_instances)
        ship.persistent_state["degradation_state"] = dict(degradation_state)
        ship.persistent_state["max_hull_integrity"] = int(assembled.get("hull_max", 0))
        ship.persistent_state["current_hull_integrity"] = int(assembled.get("hull_max", 0))
        ship.persistent_state["assembled"] = assembled
        ship.persistent_state["subsystem_bands"] = {
            "weapon": int(effective_bands.get("weapon", 0)),
            "defense": int(effective_bands.get("defense", 0)),
            "engine": int(effective_bands.get("engine", 0)),
        }
        
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

    def _active_situation_rows_for_system(self, *, system_id: str) -> list[dict[str, Any]]:
        engine = self._world_state_engine()
        if engine is None:
            return []
        active = engine.get_active_situations(system_id)
        rows: list[dict[str, Any]] = []
        for entry in sorted(
            active,
            key=lambda row: (
                str(getattr(row, "situation_id", "")),
                str(getattr(row, "scope", "")),
                str(getattr(row, "target_id", "")),
            ),
        ):
            rows.append(
                {
                    "situation_id": getattr(entry, "situation_id", None),
                    "scope": getattr(entry, "scope", None),
                    "target_id": getattr(entry, "target_id", None),
                }
            )
        return rows

    def _active_destination_situations(self, *, destination_id: str) -> list[str]:
        rows = self._active_situation_rows_for_system(system_id=self.player_state.current_system_id)
        ids: list[str] = []
        for row in rows:
            if row.get("scope") != "destination":
                continue
            target_id = row.get("target_id")
            if target_id is not None and target_id != destination_id:
                continue
            situation_id = row.get("situation_id")
            if isinstance(situation_id, str):
                ids.append(situation_id)
        return sorted(ids)

    def _system_flags_for_current_system(self) -> list[str]:
        engine = self._world_state_engine()
        if engine is None:
            return []
        if hasattr(engine, "get_system_flags"):
            return list(engine.get_system_flags(self.player_state.current_system_id))
        return []

    def _active_crew_rows(self) -> list[dict[str, Any]]:
        ship = self._active_ship()
        rows: list[dict[str, Any]] = []
        for member in sorted(ship.crew, key=lambda row: str(getattr(row, "npc_id", ""))):
            rows.append(
                {
                    "crew_id": getattr(member, "npc_id", None),
                    "name": getattr(member, "display_name", None),
                    "role": getattr(member, "primary_role", None),
                    "traits": list(getattr(member, "personality_traits", []) or []),
                    "modifiers": list(getattr(member, "special_modifiers", []) or []),
                }
            )
        return rows

    def _active_mission_rows(self) -> list[dict[str, Any]]:
        rows: list[dict[str, Any]] = []
        for mission_id in sorted(self.player_state.active_missions):
            mission = self._mission_manager.missions.get(mission_id)
            rows.append(
                {
                    "mission_id": mission_id,
                    "mission_type": getattr(mission, "mission_type", None),
                    "origin_system_id": getattr(mission, "system_id", None),
                    "target_system_id": getattr(mission, "destination_location_id", None),
                    "status": "active",
                    "days_remaining": None,
                    "reward_summary": list(getattr(mission, "rewards", []) or []) if mission is not None else None,
                }
            )
        return rows

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

    # PHASE 7.6 AUDIT NOTES
    # - BAR support pre-pass: location type may be generated, but action catalog was empty.
    # - ADMINISTRATION support pre-pass: location type may be generated, but action catalog was empty.
    # - mission_list / mission_accept pre-pass: no engine command or location action exposure.
    # - Crew hiring pre-pass: crew entity system exists, but no location action wiring in GameEngine.
    # - Fines/licensing/wanted pre-pass: law data exists, but no administration location routing.

    def _available_location_actions(self, location: Any) -> list[LocationActionModel]:
        destination = self._current_destination()
        if destination is None:
            return []
        location_type = str(getattr(location, "location_type", "") or "")
        destination_action_ids = list(destination_actions(destination))
        if location_type == "market":
            destination_action_ids = ["buy", "sell"]
        if location_type == "warehouse":
            destination_action_ids = self._warehouse_action_ids_for_current_destination()
        if location_type == "bar":
            destination_action_ids = ["bar_talk", "bar_rumors", "mission_list", "mission_accept", "bar_hire_crew"]
        if location_type == "administration":
            destination_action_ids = [
                "admin_talk",
                "admin_pay_fines",
                "admin_apply_license",
                "admin_turn_in",
                "admin_mission_board",
                "mission_accept",
            ]
        supported_ids = {
            "buy",
            "sell",
            "buy_hull",
            "sell_hull",
            "buy_module",
            "sell_module",
            "repair_ship",
            "warehouse_rent",
            "warehouse_deposit",
            "warehouse_withdraw",
            "bar_talk",
            "bar_rumors",
            "mission_list",
            "mission_accept",
            "bar_hire_crew",
            "admin_talk",
            "admin_pay_fines",
            "admin_apply_license",
            "admin_turn_in",
            "admin_mission_board",
        }
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
            return {"warehouse_rent", "warehouse_deposit", "warehouse_withdraw"}
        if location_type == "bar":
            return {"bar_talk", "bar_rumors", "mission_list", "mission_accept", "bar_hire_crew"}
        if location_type == "administration":
            return {"admin_talk", "admin_pay_fines", "admin_apply_license", "admin_turn_in", "admin_mission_board"}
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
                parameters=[
                    {"name": "ship_id", "type": "str", "prompt": "Ship ID to buy the hull for (example: PLAYER-SHIP-001)"},
                    {"name": "hull_id", "type": "str", "prompt": "Hull ID to purchase (from shipdock inventory)"},
                ],
            ),
            "sell_hull": LocationActionModel(
                action_id="sell_hull",
                display_name="Sell Hull",
                description="Sell an owned hull currently present at destination.",
                requires_confirm=True,
                parameters=[
                    {"name": "ship_id", "type": "str", "prompt": "Ship ID (hull) to sell"},
                ],
            ),
            "buy_module": LocationActionModel(
                action_id="buy_module",
                display_name="Buy Module",
                description="Purchase a module for an eligible ship.",
                parameters=[
                    {"name": "ship_id", "type": "str", "prompt": "Ship ID to install the module on (example: PLAYER-SHIP-001)"},
                    {"name": "module_id", "type": "str", "prompt": "Module ID to purchase (from shipdock inventory)"},
                ],
            ),
            "sell_module": LocationActionModel(
                action_id="sell_module",
                display_name="Sell Module",
                description="Sell a module installed on an eligible ship.",
                parameters=[
                    {"name": "ship_id", "type": "str", "prompt": "Ship ID with the module to sell (example: PLAYER-SHIP-001)"},
                    {"name": "module_id", "type": "str", "prompt": "Module ID to sell"},
                ],
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
            "warehouse_rent": LocationActionModel(
                action_id="warehouse_rent",
                display_name="Rent Warehouse Space",
                description="Rent additional warehouse capacity at this destination.",
                parameters=["units"],
            ),
            "warehouse_deposit": LocationActionModel(
                action_id="warehouse_deposit",
                display_name="Deposit Cargo",
                description="Move cargo from ship hold to destination warehouse.",
                parameters=["sku_id", "quantity"],
            ),
            "warehouse_withdraw": LocationActionModel(
                action_id="warehouse_withdraw",
                display_name="Withdraw Cargo",
                description="Move goods from destination warehouse to ship hold.",
                parameters=["sku_id", "quantity"],
            ),
            "bar_talk": LocationActionModel(
                action_id="bar_talk",
                display_name="Talk",
                description="Talk to locals at the bar.",
            ),
            "bar_rumors": LocationActionModel(
                action_id="bar_rumors",
                display_name="Ask For Rumors",
                description="Collect local rumors.",
            ),
            "mission_list": LocationActionModel(
                action_id="mission_list",
                display_name="List Missions",
                description="List available missions for this location.",
            ),
            "mission_accept": LocationActionModel(
                action_id="mission_accept",
                display_name="Accept Mission",
                description="Accept an offered mission by mission id.",
                parameters=["mission_id"],
            ),
            "bar_hire_crew": LocationActionModel(
                action_id="bar_hire_crew",
                display_name="Hire Crew",
                description="Attempt to hire available crew contacts.",
            ),
            "admin_talk": LocationActionModel(
                action_id="admin_talk",
                display_name="Talk",
                description="Talk to administration personnel.",
            ),
            "admin_pay_fines": LocationActionModel(
                action_id="admin_pay_fines",
                display_name="Pay Fines",
                description="Pay outstanding fines for this system.",
            ),
            "admin_apply_license": LocationActionModel(
                action_id="admin_apply_license",
                display_name="Apply License",
                description="Apply for restricted trade license.",
            ),
            "admin_turn_in": LocationActionModel(
                action_id="admin_turn_in",
                display_name="Turn In",
                description="Turn in outstanding warrants.",
            ),
            "admin_mission_board": LocationActionModel(
                action_id="admin_mission_board",
                display_name="View Mission Board",
                description="Review officially posted contracts.",
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

    def _list_current_location_npcs(self) -> list[Any]:
        location = self._current_location()
        if location is None:
            raise ValueError("not_in_location")
        location_id = str(getattr(location, "location_id", "") or "")
        location_type = str(getattr(location, "location_type", "") or "")
        if not location_id:
            return []

        resolved_ids = [npc_id for npc_id in self._location_npc_ids.get(location_id, []) if isinstance(npc_id, str)]
        if not resolved_ids:
            npcs = resolve_npcs_for_location(
                location_id=location_id,
                location_type=location_type,
                system_id=self.player_state.current_system_id,
                registry=self._npc_registry,
                logger=self._logger if self._logging_enabled else None,
                turn=int(get_current_turn()),
            )
            resolved_ids = sorted(
                {
                    str(getattr(row, "npc_id", ""))
                    for row in npcs
                    if isinstance(getattr(row, "npc_id", None), str) and str(getattr(row, "npc_id", ""))
                }
            )
            self._location_npc_ids[location_id] = list(resolved_ids)

        by_id: dict[str, Any] = {}
        # B) Crew NPC Visibility Fix: Include all NPCs at this location, excluding hired crew
        # Filter out any NPC with current_ship_id set (hired crew)
        npc_list = [
            n for n in self._npc_registry.list_by_location(location_id)
            if not getattr(n, "current_ship_id", None)
        ]
        for npc in npc_list:
            npc_id = str(getattr(npc, "npc_id", "") or "")
            if npc_id:
                by_id[npc_id] = npc
        
        # When merging resolved_ids, only add NPCs that:
        # 1. Exist in registry
        # 2. Are actually at this location (current_location_id == location_id)
        # 3. Are not hired (current_ship_id is None)
        for npc_id in resolved_ids:
            npc = self._npc_registry.get(npc_id)
            if npc is None:
                continue
            # Ensure NPC is actually at this location
            if str(getattr(npc, "current_location_id", "") or "") != str(location_id):
                continue
            # Exclude hired crew (those assigned to a ship)
            if getattr(npc, "current_ship_id", None):
                continue
            by_id[npc_id] = npc

        ordered = sorted(by_id.values(), key=lambda row: str(getattr(row, "npc_id", "")))
        structural_role = "bartender" if location_type == "bar" else "administrator" if location_type == "administration" else ""
        if not structural_role:
            return ordered

        primary: Any | None = None
        for npc in ordered:
            if self._npc_primary_role(npc) == structural_role:
                primary = npc
                break
        
        # A) Mandatory Tier 3 NPC Enforcement
        # Ensure required Tier 3 NPC exists for bar/administration locations
        if primary is None:
            # Create missing Tier 3 NPC using existing deterministic logic
            from npc_placement import _deterministic_npc_id
            required_npc_id = _deterministic_npc_id(location_id, structural_role)
            required_npc = self._npc_registry.get(required_npc_id)
            if required_npc is None:
                required_npc = NPCEntity(
                    npc_id=required_npc_id,
                    persistence_tier=NPCPersistenceTier.TIER_3,
                    display_name=structural_role.replace("_", " ").title(),
                    role_tags=[structural_role],
                    current_location_id=location_id,
                    current_system_id=self.player_state.current_system_id,
                )
                self._npc_registry.add(
                    required_npc,
                    logger=self._logger if self._logging_enabled else None,
                    turn=int(get_current_turn()),
                )
                if self._logging_enabled and self._logger:
                    self._logger.log(
                        turn=int(get_current_turn()),
                        action="npc_enforcement",
                        state_change=f"created_required_npc role={structural_role} location_id={location_id} npc_id={required_npc_id}",
                    )
            primary = required_npc
            # Add to ordered list if not already present
            if required_npc_id not in by_id:
                by_id[required_npc_id] = required_npc
                ordered = sorted(by_id.values(), key=lambda row: str(getattr(row, "npc_id", "")))
        
        # Ensure primary exists before building ordered_with_mission_givers
        # Never inject None into the list
        if primary is None:
            ordered_with_mission_givers = ordered
        else:
            ordered_with_mission_givers = [primary] + [npc for npc in ordered if str(getattr(npc, "npc_id", "")) != str(getattr(primary, "npc_id", ""))]
        
        # Inject ephemeral mission giver NPCs and spawn crew for Bar locations only
        if location_type == "bar":
            mission_ids = self._ensure_location_mission_offers(location_id=location_id)
            mission_givers: list[dict[str, Any]] = []
            for mission_id in mission_ids:
                mission = self._mission_manager.missions.get(mission_id)
                if mission is None or mission.mission_contact_seed is None:
                    continue
                # Derive deterministic npc_id (matches accept-time creation)
                npc_hash = hashlib.md5(mission.mission_contact_seed.encode()).hexdigest()[:8]
                giver_npc_id = f"NPC-MSN-{npc_hash}"
                # Only add if not already a persistent NPC (not yet accepted)
                if giver_npc_id not in by_id:
                    mission_givers.append({
                        "npc_id": giver_npc_id,
                        "display_name": f"Mission Contact ({mission.mission_type})",
                        "persistence_tier": 1,
                        "role": "mission_giver",
                        "_ephemeral": True,
                        "_mission_id": mission_id,
                    })
            # Sort mission givers by npc_id for determinism
            mission_givers.sort(key=lambda x: x["npc_id"])
            
            # Spawn hireable crew at bar locations
            # Filter out hired crew (those with current_ship_id set)
            crew_npcs = self._spawn_crew_for_bar_location(location_id=location_id, system_id=self.player_state.current_system_id)
            crew_npcs = [npc for npc in crew_npcs if not getattr(npc, "current_ship_id", None)]
            return ordered_with_mission_givers + mission_givers + crew_npcs
        
        return ordered_with_mission_givers

    def _spawn_crew_for_bar_location(self, *, location_id: str, system_id: str) -> list[NPCEntity]:
        """
        Spawn hireable crew at bar location with 20% chance and population-based cap.
        
        Returns list of crew NPCEntity objects (empty if spawn roll fails or cap is 0).
        """
        # Check for existing TIER_2 crew at this location
        existing_crew = [
            npc for npc in self._npc_registry.list_by_location(location_id)
            if npc.is_crew and npc.persistence_tier == NPCPersistenceTier.TIER_2
        ]
        if existing_crew:
            # Respect existing persistent crew - do not regenerate
            return existing_crew
        
        # Deterministic spawn roll: 20% chance
        # Use hash for deterministic seed (same as other deterministic RNG streams)
        spawn_seed_token = repr((self.world_seed, location_id, "bar_spawn"))
        spawn_seed = int(hashlib.sha256(spawn_seed_token.encode("ascii")).hexdigest()[:16], 16)
        spawn_rng = random.Random(spawn_seed)
        spawn_roll = spawn_rng.random()
        
        if spawn_roll >= 0.20:
            # Spawn roll failed
            return []
        
        # Get system population for cap
        system = self.sector.get_system(system_id)
        if system is None:
            return []
        
        pop = int(system.population)
        if pop in (1, 2):
            max_spawn = 1
        elif pop in (3, 4):
            max_spawn = 2
        else:
            max_spawn = 3
        
        # Generate crew pool
        from crew_generator import generate_hireable_crew
        crew_pool = generate_hireable_crew(
            world_seed=self.world_seed,
            system_id=system_id,
            pool_size=max_spawn * 2,  # Generate more than needed for selection
            world_state_engine=self._world_state_engine(),
        )
        
        # Limit to max_spawn
        crew_pool = crew_pool[:max_spawn]
        
        # Create NPCEntity for each crew member
        spawned_crew: list[NPCEntity] = []
        for index, crew_data in enumerate(crew_pool):
            # Deterministic npc_id based on location and index
            crew_npc_id = f"NPC-CREW-{hashlib.md5(f'{location_id}:crew:{index}'.encode()).hexdigest()[:8]}"
            
            # Check if already exists in registry
            existing = self._npc_registry.get(crew_npc_id)
            if existing is not None:
                if existing.is_crew and existing.persistence_tier == NPCPersistenceTier.TIER_2:
                    spawned_crew.append(existing)
                    continue
            
            # Create new crew NPC
            role_id = str(crew_data.get("role_id", ""))
            # Load crew roles to get display name
            from crew_generator import _load_crew_roles
            crew_roles = _load_crew_roles()
            role_data = None
            for role in crew_roles:
                if str(role.get("role_id", "")) == role_id:
                    role_data = role
                    break
            
            display_name = str(role_data.get("name", role_id)) if role_data else f"Crew ({role_id})"
            
            crew_npc = NPCEntity(
                npc_id=crew_npc_id,
                persistence_tier=NPCPersistenceTier.TIER_2,
                display_name=display_name,
                role_tags=[role_id] if role_id else [],
                current_location_id=location_id,
                current_system_id=system_id,
                is_crew=True,
                crew_role_id=role_id,
                hire_cost=int(crew_data.get("hire_cost", 0)),
                daily_wage=int(crew_data.get("daily_wage", 0)),
            )
            
                    # Crew entity contract: is_crew=True, persistence_tier=TIER_2, crew_role_id set
                    # No explicit validate() method needed - contract enforced by construction
            
            # Add to registry
            self._npc_registry.add(crew_npc, logger=self._logger if self._logging_enabled else None, turn=int(get_current_turn()))
            
            spawned_crew.append(crew_npc)
        
        return spawned_crew

    def _npc_for_current_location(self, npc_id: str) -> Any | None:
        for npc in self._list_current_location_npcs():
            # Handle both NPCEntity objects and ephemeral dicts
            if isinstance(npc, dict):
                if str(npc.get("npc_id", "")) == npc_id:
                    return npc
            else:
                if str(getattr(npc, "npc_id", "")) == npc_id:
                    return npc
        return None

    def _role_npc_for_current_location(self, role: str) -> Any | None:
        for npc in self._list_current_location_npcs():
            if self._npc_primary_role(npc) == role:
                return npc
        return None

    def _npc_primary_role(self, npc: Any) -> str:
        # Handle ephemeral mission giver dicts
        if isinstance(npc, dict) and "role" in npc:
            return str(npc["role"])
        role_tags = getattr(npc, "role_tags", [])
        if isinstance(role_tags, list):
            for role in role_tags:
                if isinstance(role, str) and role:
                    return role
        roles = getattr(npc, "roles", [])
        if isinstance(roles, list):
            for role in roles:
                if isinstance(role, str) and role:
                    return role
        return "unknown"

    def _npc_summary(self, npc: Any) -> dict[str, Any]:
        # Handle ephemeral mission giver dicts
        if isinstance(npc, dict):
            return {
                "npc_id": str(npc.get("npc_id", "")),
                "display_name": str(npc.get("display_name", "")),
                "role": str(npc.get("role", "unknown")),
                "persistence_tier": int(npc.get("persistence_tier", 1)),
            }
        tier_raw = getattr(npc, "persistence_tier", 1)
        tier_value = int(getattr(tier_raw, "value", tier_raw))
        return {
            "npc_id": str(getattr(npc, "npc_id", "") or ""),
            "display_name": str(getattr(npc, "display_name", "") or ""),
            "role": self._npc_primary_role(npc),
            "persistence_tier": int(tier_value),
        }

    def _npc_interaction_rows_for_role(self, role: str) -> list[dict[str, Any]]:
        base = [
            {
                "action_id": "npc_talk",
                "display_name": "Talk",
                "description": "Have a short conversation.",
                "parameters": [],
            }
        ]
        if role == "bartender":
            return base + [
                {
                    "action_id": "bartender_rumors",
                    "display_name": "Ask for rumors",
                    "description": "Request a local rumor.",
                    "parameters": [],
                }
            ]
        if role == "administrator":
            return base + [
                {
                    "action_id": "admin_pay_fines",
                    "display_name": "Pay fines",
                    "description": "Pay outstanding fines in this system.",
                    "parameters": [],
                },
                {
                    "action_id": "admin_apply_license",
                    "display_name": "Apply license",
                    "description": "Apply for restricted trade license.",
                    "parameters": [],
                },
                {
                    "action_id": "admin_turn_in",
                    "display_name": "Turn in",
                    "description": "Turn in outstanding warrants.",
                    "parameters": [],
                },
                {
                    "action_id": "admin_mission_board",
                    "display_name": "View Mission Board",
                    "description": "Review officially posted contracts.",
                    "parameters": [],
                },
            ]
        if role == "mission_giver":
            return base + [
                {
                    "action_id": "mission_discuss",
                    "display_name": "Discuss job",
                    "description": "Ask about the available job.",
                    "parameters": [],
                }
            ]
        return base

    def _mission_id_for_giver_npc_id(self, npc_id: str) -> str | None:
        """Find mission_id for a mission giver npc_id by matching hash against mission_contact_seed or mission_giver_npc_id."""
        location = self._current_location()
        if location is None:
            return None
        location_id = str(getattr(location, "location_id", "") or "")
        if not location_id:
            return None
        
        # Search all missions (not just offered ones) to find ACTIVE missions after acceptance
        for mission_id, mission in self._mission_manager.missions.items():
            if mission is None:
                continue
            
            # Match by mission_giver_npc_id (for ACTIVE missions after acceptance)
            if mission.mission_giver_npc_id == npc_id:
                # Verify mission is at current location
                # Check source_id (contains location_id) or location_id field
                mission_location_match = (
                    (hasattr(mission, "location_id") and str(getattr(mission, "location_id", "") or "") == location_id) or
                    (hasattr(mission, "source_id") and str(mission.source_id or "").startswith(location_id + ":"))
                )
                if mission_location_match:
                    return mission_id
            
            # Match by mission_contact_seed hash (for OFFERED missions)
            if mission.mission_contact_seed is not None:
                npc_hash = hashlib.md5(mission.mission_contact_seed.encode()).hexdigest()[:8]
                giver_npc_id = f"NPC-MSN-{npc_hash}"
                if giver_npc_id == npc_id:
                    # Verify mission is at current location by checking origin_location_id or location_id
                    # Also check if mission was offered at this location via source_id
                    mission_location_match = (
                        (mission.origin_location_id is not None and str(mission.origin_location_id) == location_id) or
                        (hasattr(mission, "location_id") and str(getattr(mission, "location_id", "") or "") == location_id) or
                        (hasattr(mission, "source_id") and str(mission.source_id or "").startswith(location_id + ":"))
                    )
                    if mission_location_match:
                        return mission_id
        
        return None

    def _npc_talk_text(self, *, npc: Any, role: str) -> str:
        name = str(getattr(npc, "display_name", "") or "Contact")
        if role == "bartender":
            return f"{name} polishes a glass and nods."
        if role == "administrator":
            return f"{name} reviews your record and waits."
        return f"{name} acknowledges you."

    def _admin_pay_fines_result(self) -> dict[str, Any]:
        system_id = self.player_state.current_system_id
        due = int(self.player_state.outstanding_fines.get(system_id, 0) or 0)
        if due <= 0:
            return {"ok": True, "reason": "no_fines_due", "paid": 0}
        if int(self.player_state.credits) < due:
            return {"ok": False, "reason": "insufficient_credits", "paid": 0}
        self.player_state.credits = max(0, int(self.player_state.credits) - due)
        self.player_state.outstanding_fines[system_id] = 0
        return {"ok": True, "reason": "ok", "paid": due}

    def _build_bartender_rumor_payload(self, *, npc_id: str) -> dict[str, Any]:
        destination_id = str(self.player_state.current_destination_id or "")
        location_id = str(self.player_state.current_location_id or "")
        turn_value = int(get_current_turn())
        rng = random.Random(
            self._stable_seed(
                self.world_seed,
                self.player_state.current_system_id,
                destination_id,
                location_id,
                npc_id,
                turn_value,
                "bartender_rumor",
            )
        )

        rumor_type = ["red_herring", "lore", "world_state_hint"][int(rng.randint(0, 2))]
        if rumor_type == "red_herring":
            return {
                "ok": True,
                "rumor_type": "red_herring",
                "rumor_text": "A trader swears hidden riches drift near old debris.",
            }
        if rumor_type == "lore":
            return {
                "ok": True,
                "rumor_type": "lore",
                "rumor_text": "Long-haulers say every port keeps a story no map can hold.",
            }

        hint_choices: list[dict[str, str | None]] = []
        current_system = self.sector.get_system(self.player_state.current_system_id)
        if current_system is not None:
            for destination in sorted(list(current_system.destinations), key=lambda row: row.destination_id):
                hint_choices.append(
                    {
                        "system_id": str(current_system.system_id),
                        "destination_id": str(destination.destination_id),
                    }
                )
            ship = self._active_ship()
            fuel_limit = int(ship.current_fuel)
            for target in sorted(self.sector.systems, key=lambda entry: entry.system_id):
                if target.system_id == current_system.system_id:
                    continue
                distance_ly = float(self._warp_distance_ly(origin=current_system, target=target))
                if distance_ly <= float(fuel_limit):
                    hint_choices.append({"system_id": str(target.system_id), "destination_id": None})
        if not hint_choices:
            return {
                "ok": True,
                "rumor_type": "lore",
                "rumor_text": "The bar goes quiet when routes run dry.",
            }

        hint = hint_choices[int(rng.randint(0, len(hint_choices) - 1))]
        hint_system_id = str(hint.get("system_id") or "")
        hint_destination_id = hint.get("destination_id")
        destination_known = isinstance(hint_destination_id, str) and hint_destination_id in self.player_state.visited_destination_ids
        system_known = hint_system_id in self.player_state.visited_system_ids
        if destination_known:
            rumor_text = f"Someone mentioned unusual traffic near {hint_destination_id}."
        elif system_known:
            rumor_text = f"Pilots keep circling a point in {hint_system_id} without saying why."
        else:
            rumor_text = "A pilot hints at movement along a reachable route."

        payload: dict[str, Any] = {
            "ok": True,
            "rumor_type": "world_state_hint",
            "rumor_text": rumor_text,
            "hint": {"system_id": hint_system_id},
        }
        if isinstance(hint_destination_id, str):
            payload["hint"]["destination_id"] = hint_destination_id
        return payload

    def _stable_seed(self, *parts: Any) -> int:
        value = 0
        for part in parts:
            for char in str(part):
                value = (value * 31 + ord(char)) % (2**32)
        return value

    def _current_destination_id_required(self) -> str:
        destination_id = self.player_state.current_destination_id
        if not isinstance(destination_id, str) or not destination_id:
            raise ValueError("no_current_destination")
        return destination_id

    def _ensure_warehouse_entry(self, destination_id: str) -> dict[str, Any]:
        warehouse = self.player_state.warehouses.get(destination_id)
        if not isinstance(warehouse, dict):
            warehouse = {"capacity": 0, "goods": {}}
            self.player_state.warehouses[destination_id] = warehouse
        if not isinstance(warehouse.get("goods"), dict):
            warehouse["goods"] = {}
        if not isinstance(warehouse.get("capacity"), int):
            warehouse["capacity"] = int(warehouse.get("capacity", 0) or 0)
        return warehouse

    def _warehouse_capacity(self, warehouse: dict[str, Any]) -> int:
        return max(0, int(warehouse.get("capacity", 0) or 0))

    def _warehouse_goods(self, warehouse: dict[str, Any]) -> dict[str, int]:
        goods_raw = warehouse.get("goods", {})
        if not isinstance(goods_raw, dict):
            return {}
        return {
            str(sku_id): int(quantity)
            for sku_id, quantity in goods_raw.items()
            if isinstance(quantity, int) and int(quantity) > 0
        }

    def _warehouse_used_capacity(self, warehouse: dict[str, Any]) -> int:
        return int(sum(self._warehouse_goods(warehouse).values()))

    def _warehouse_available_capacity(self, warehouse: dict[str, Any]) -> int:
        return max(0, int(self._warehouse_capacity(warehouse) - self._warehouse_used_capacity(warehouse)))

    def _warehouse_action_ids_for_current_destination(self) -> list[str]:
        destination_id = self.player_state.current_destination_id
        if not isinstance(destination_id, str) or not destination_id:
            return []
        warehouse = self.player_state.warehouses.get(destination_id)
        actions = ["warehouse_rent"]
        cargo_manifest = self.player_state.cargo_by_ship.get("active", {})
        has_cargo = isinstance(cargo_manifest, dict) and any(
            isinstance(quantity, int) and int(quantity) > 0 for quantity in cargo_manifest.values()
        )
        if isinstance(warehouse, dict):
            if has_cargo and self._warehouse_available_capacity(warehouse) > 0:
                actions.append("warehouse_deposit")
            if self._warehouse_used_capacity(warehouse) > 0:
                actions.append("warehouse_withdraw")
        return actions

    def _warehouse_cost_per_turn(self) -> int:
        total_capacity = 0
        for warehouse in self.player_state.warehouses.values():
            if not isinstance(warehouse, dict):
                continue
            total_capacity += self._warehouse_capacity(warehouse)
        return int(total_capacity * WAREHOUSE_CAPACITY_COST_PER_TURN)

    def _insurance_cost_per_turn(self) -> int:
        total = 0
        for policy in self.player_state.insurance_policies:
            if not isinstance(policy, dict):
                continue
            value = policy.get("premium_per_turn", policy.get("cost_per_turn", 0))
            if isinstance(value, int):
                total += int(value)
        return int(total)

    def _crew_wages_per_turn(self) -> int:
        active_ship = self.fleet_by_id.get(self.player_state.active_ship_id)
        return int(getattr(active_ship, "get_total_daily_wages", lambda: 0)() or 0)

    def _recurring_cost_per_turn(self) -> int:
        return int(self._insurance_cost_per_turn() + self._crew_wages_per_turn() + self._warehouse_cost_per_turn())

    def _apply_recurring_costs(self, *, days_completed: int) -> None:
        if int(days_completed) <= 0:
            return
        per_turn = int(self._recurring_cost_per_turn())
        if per_turn <= 0:
            return
        self.player_state.credits = max(0, int(self.player_state.credits) - (per_turn * int(days_completed)))

    def _update_bankruptcy_warning(self) -> None:
        """Update bankruptcy warning turn based on current credits state."""
        current_turn = int(get_current_turn())
        if self.player_state.credits > 0:
            self.player_state.bankruptcy_warning_turn = None
        elif self.player_state.credits == 0:
            if self.player_state.bankruptcy_warning_turn is None:
                self.player_state.bankruptcy_warning_turn = current_turn

    def _warehouse_profile_rows(self) -> list[dict[str, Any]]:
        rows: list[dict[str, Any]] = []
        for destination_id in sorted(self.player_state.warehouses):
            warehouse = self.player_state.warehouses[destination_id]
            if not isinstance(warehouse, dict):
                continue
            capacity = int(self._warehouse_capacity(warehouse))
            goods = self._warehouse_goods(warehouse)
            used = int(sum(goods.values()))
            rows.append(
                {
                    "destination_id": destination_id,
                    "capacity": capacity,
                    "used": used,
                    "available": max(0, int(capacity - used)),
                    "cost_per_turn": int(capacity * WAREHOUSE_CAPACITY_COST_PER_TURN),
                    "goods": goods,
                }
            )
        return rows

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
                generate_shipdock_inventory(
                    self.world_seed,
                    system.system_id,
                    int(system.population),
                    world_state_engine=self._world_state_engine(),
                ),
            )
        if action_id == "repair_ship":
            action_kwargs.setdefault("system_population", int(system.population))
        if action_id in {"buy_module", "sell_module", "sell_hull", "repair_ship"}:
            action_kwargs.setdefault("ship_id", self.player_state.active_ship_id)
        
        # Pass world_state_engine, system_id, logger, and turn for pricing contract integration
        if action_id in {"buy_hull", "sell_hull", "buy_module", "sell_module"}:
            action_kwargs.setdefault("system_id", system.system_id)
            action_kwargs.setdefault("world_state_engine", self._world_state_engine())
            action_kwargs.setdefault("logger", self._logger if self._logging_enabled else None)
            action_kwargs.setdefault("turn", int(get_current_turn()))
        
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

    def _possible_variant_tags(self) -> set[str]:
        return {
            str(good.possible_tag)
            for good in self.catalog.goods
            if isinstance(good.possible_tag, str) and good.possible_tag
        }

    def _resolve_base_sku_and_variant_tags(self, *, sku: str) -> tuple[str | None, list[str]]:
        try:
            self.catalog.good_by_sku(sku)
            return sku, []
        except KeyError:
            pass
        known_tags = self._possible_variant_tags()
        if not known_tags:
            return None, []
        parts = [part for part in sku.split("_") if part]
        if not parts:
            return None, []
        candidates: list[tuple[str, list[str]]] = []
        max_strip = len(parts) - 1
        for prefix_count in range(0, max_strip + 1):
            for suffix_count in range(0, max_strip - prefix_count + 1):
                if prefix_count == 0 and suffix_count == 0:
                    continue
                prefix_parts = parts[:prefix_count]
                suffix_parts = parts[len(parts) - suffix_count :] if suffix_count > 0 else []
                stripped_parts = prefix_parts + suffix_parts
                if not stripped_parts or any(part not in known_tags for part in stripped_parts):
                    continue
                core = parts[prefix_count : len(parts) - suffix_count]
                if not core:
                    continue
                candidate_sku = "_".join(core)
                try:
                    self.catalog.good_by_sku(candidate_sku)
                except KeyError:
                    continue
                candidates.append((candidate_sku, stripped_parts))
        if not candidates:
            return None, []
        candidates.sort(key=lambda entry: (-len(entry[0]), len(entry[1]), entry[0], tuple(entry[1])))
        return candidates[0]

    def _market_goods_with_roles(self, market: Any) -> list[tuple[Any, str]]:
        rows: list[tuple[Any, str]] = []
        for category in market.categories.values():
            for good in category.produced:
                rows.append((good, "produced"))
            for good in category.neutral:
                rows.append((good, "neutral"))
            for good in category.consumed:
                rows.append((good, "consumed"))
        return rows

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
        market_entries = self._market_goods_with_roles(market)
        exact_entry = next((entry for entry in market_entries if str(entry[0].sku) == sku), None)

        base_sku, inferred_variant_tags = self._resolve_base_sku_and_variant_tags(sku=sku)
        if base_sku is None and exact_entry is None:
            return None
        catalog_good = None
        if isinstance(base_sku, str):
            try:
                catalog_good = self.catalog.good_by_sku(base_sku)
            except KeyError:
                catalog_good = None

        if exact_entry is not None:
            exact_good = exact_entry[0]
            category = str(getattr(exact_good, "category", ""))
            sold_tags = list(getattr(exact_good, "tags", ()) or [])
            sold_base_sku = base_sku if isinstance(base_sku, str) else None
            if sold_base_sku is None:
                resolved_base, _ = self._resolve_base_sku_and_variant_tags(sku=str(exact_good.sku))
                sold_base_sku = resolved_base
        else:
            if catalog_good is None:
                return None
            category = str(catalog_good.category)
            sold_tags = list(catalog_good.tags)
            for tag in inferred_variant_tags:
                if tag not in sold_tags:
                    sold_tags.append(tag)
            sold_base_sku = base_sku

        if category not in market.categories:
            return None

        near_match_entry = None
        if exact_entry is None and isinstance(sold_base_sku, str):
            base_matches: list[tuple[Any, str]] = []
            for entry in market_entries:
                market_good = entry[0]
                if str(getattr(market_good, "category", "")) != category:
                    continue
                market_base, _ = self._resolve_base_sku_and_variant_tags(sku=str(market_good.sku))
                if market_base == sold_base_sku:
                    base_matches.append(entry)
            if base_matches:
                base_matches.sort(key=lambda entry: str(entry[0].sku))
                near_match_entry = base_matches[0]

        if exact_entry is not None:
            pricing_sku = sku
            substitute_override = None
        elif near_match_entry is not None:
            pricing_sku = str(near_match_entry[0].sku)
            substitute_override = False
        elif isinstance(sold_base_sku, str):
            pricing_sku = sold_base_sku
            substitute_override = True
        else:
            return None

        try:
            pricing = price_transaction(
                catalog=self.catalog,
                market=market,
                government=government,
                policy=self._law_engine.evaluate_policy(
                    government_id=government.id,
                    commodity=Commodity(commodity_id=sku, tags=set(sold_tags)),
                    action=action,
                    turn=int(get_current_turn()),
                ),
                sku=pricing_sku,
                action=action,
                world_seed=self.world_seed,
                system_id=self.player_state.current_system_id,
                destination_id=self.player_state.current_destination_id,
                scarcity_modifier=1.0,
                ship=self._active_ship(),
                world_state_engine=self._world_state_engine(),
                tags_override=sold_tags,
                substitute_override=substitute_override,
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
