from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
import hashlib
import json
import math
import random
from typing import Any, Literal, Optional, Union

from combat_resolver import resolve_combat
from data_catalog import load_data_catalog
from encounter_generator import generate_travel_encounters
from end_game_evaluator import evaluate_end_game
from government_law_engine import Commodity, GovernmentLawEngine
from government_registry import GovernmentRegistry
from interaction_layer import (
    ACTION_IGNORE,
    ACTION_RESPOND,
    ACTION_HAIL,
    ACTION_ATTACK,
    HANDLER_COMBAT,
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
from mission_factory import create_mission, create_delivery_mission, CREATOR_BY_TYPE
from mission_generator import select_weighted_mission_type
from mission_registry import mission_type_candidates_for_source
from mission_manager import MissionManager, evaluate_active_missions
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
from ship_assembler import assemble_ship, compute_hull_max_from_ship_state, get_slot_distribution
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
    game_over_reason: str | None = None
    pending_loot: dict[str, Any] | None = None
    claim_mission_error: str | None = None  # Phase 7.11.1: Store claim error for CLI


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
    def __init__(self, world_seed: int, config: dict | None = None, starting_ship_override: dict | None = None) -> None:
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
        self.fleet_by_id = self._build_default_fleet(starting_ship_override=starting_ship_override)

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
        self._pending_travel: dict[str, Any] | None = None
        self._pending_combat: dict[str, Any] | None = None
        self._pending_loot: dict[str, Any] | None = None

    def execute(self, command: dict) -> dict:
        turn_before = int(get_current_turn())
        
        # Enforce run-end gating (Option 3 model)
        # Check if run has ended before processing any command
        if self.player_state.run_ended:
            command_type, payload, error = self._parse_command(command)
            # Allow quit command even after run ended
            if command_type != "quit":
                return self._build_step_result(
                    context=EngineContext(
                        command=command if isinstance(command, dict) else {},
                        command_type=command_type or "unknown",
                        turn_before=turn_before,
                        turn_after=int(get_current_turn()),
                        game_over_reason=self.player_state.run_end_reason,
                    ),
                    ok=False,
                    error="game_over",
                )
        
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
            elif command_type == "dismiss_crew":
                self._execute_dismiss_crew(context, payload)
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
            elif command_type == "encounter_decision":
                self._execute_encounter_decision(context, payload)
            elif command_type == "combat_action":
                self._execute_combat_action(context, payload)
            elif command_type == "warehouse_cancel":
                self._execute_warehouse_cancel(context, payload)
            elif command_type == "set_active_ship":
                self._execute_set_active_ship(context, payload)
            elif command_type == "transfer_cargo":
                self._execute_transfer_cargo(context, payload)
            elif command_type == "abandon_mission":
                self._execute_abandon_mission(context, payload)
            elif command_type == "claim_mission":
                self._execute_claim_mission(context, payload)
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
        
        # Check for claim_mission error (Phase 7.11.1)
        claim_error = context.claim_mission_error
        if claim_error:
            return self._build_step_result(context=context, ok=False, error=claim_error)
        
        return self._build_step_result(context=context, ok=True, error=None)

    def has_pending_encounter(self) -> bool:
        """Check if there is a pending encounter requiring player input."""
        return self._pending_travel is not None and self._pending_travel.get("current_encounter") is not None
    
    def get_pending_loot(self) -> dict[str, Any] | None:
        """Get pending loot bundle from last combat (if any)."""
        return getattr(self, "_pending_loot", None)
    
    def clear_pending_loot(self) -> None:
        """Clear pending loot bundle after application."""
        self._pending_loot = None
    
    def resolve_pending_loot(self, take_all: bool) -> dict[str, Any]:
        """
        Resolve pending loot bundle.
        
        Args:
            take_all: If True, apply all loot. If False, discard all loot.
        
        Returns:
            dict with "ok" and optional "error" keys
        """
        if not self._pending_loot:
            return {"ok": False, "error": "no_pending_loot"}
        
        loot_bundle = self._pending_loot
        
        if take_all:
            # Apply credits immediately
            credits = loot_bundle.get("credits", 0)
            if credits > 0:
                self.player_state.credits = max(0, int(self.player_state.credits) + int(credits))
            
            # Apply cargo via reward_applicator (capacity-safe)
            reward_payload = loot_bundle.get("reward_payload")
            if reward_payload:
                sku_id = getattr(reward_payload, "sku_id", None)
                quantity = getattr(reward_payload, "quantity", 0)
                if sku_id and quantity > 0:
                    # Get ship capacities
                    try:
                        ship = self._active_ship()
                        physical_capacity = int(ship.get_effective_physical_capacity())
                        data_capacity = int(ship.get_effective_data_capacity())
                    except Exception:
                        physical_capacity = None
                        data_capacity = None
                    
                    # Apply cargo with capacity enforcement
                    applied = apply_materialized_reward(
                        player=self.player_state,
                        reward_payload=reward_payload,
                        context="game_engine_resolve_loot",
                        catalog=self.catalog if hasattr(self, "catalog") else None,
                        physical_cargo_capacity=physical_capacity,
                        data_cargo_capacity=data_capacity,
                        enforce_capacity=True,
                        stolen_applied=loot_bundle.get("stolen_applied", False),
                    )
                    
                    # If capacity exceeded, cargo is not applied (error returned but not fatal)
                    if applied.get("error") == "cargo_capacity_exceeded":
                        # Cargo could not be applied due to capacity
                        pass
            
            # Apply salvage modules (convert to physical cargo: 1 module = 1 physical cargo unit)
            salvage_modules = loot_bundle.get("salvage_modules", [])
            if salvage_modules:
                # Get ship capacity
                try:
                    ship = self._active_ship()
                    physical_capacity = int(ship.get_effective_physical_capacity())
                except Exception:
                    physical_capacity = None
                
                # Enforce physical cargo capacity if known; otherwise treat as unlimited
                from reward_applicator import _is_data_cargo
                catalog = self.catalog if hasattr(self, "catalog") else None

                # Initialize cargo structure
                self.player_state.cargo_by_ship.setdefault("active", {})
                holdings = self.player_state.cargo_by_ship.get("active", {})

                # Calculate current physical cargo usage
                current_physical_usage = 0
                if physical_capacity is not None and physical_capacity > 0:
                    for sku, qty in holdings.items():
                        try:
                            if not _is_data_cargo(sku, catalog):
                                current_physical_usage += int(qty)
                        except Exception:
                            # If SKU is unknown in catalog, treat as physical
                            try:
                                current_physical_usage += int(qty)
                            except Exception:
                                pass

                # Iterate salvage modules deterministically; accept up to capacity
                for module in salvage_modules:
                    if not isinstance(module, dict):
                        continue
                    module_id = module.get("module_id")
                    if not isinstance(module_id, str) or not module_id:
                        continue

                    # If capacity is known and enforced, check remaining space
                    if physical_capacity is not None and physical_capacity > 0:
                        # One unit per module
                        if current_physical_usage + 1 > physical_capacity:
                            # Reject excess salvage deterministically (stop applying further modules)
                            break

                    # capacity_before/after in terms of physical usage
                    capacity_before = current_physical_usage

                    # Apply salvage as cargo: 1 unit of physical cargo with SKU = module_id
                    current_qty = holdings.get(module_id, 0)
                    holdings[module_id] = current_qty + 1

                    # Update usage if capacity is tracked
                    if physical_capacity is not None and physical_capacity > 0:
                        current_physical_usage += 1

                    capacity_after = current_physical_usage

                    # Log salvage application event for diagnostics
                    try:
                        self._event(
                            context,
                            stage="salvage_applied",
                            subsystem="reward_application",
                            detail={
                                "module_id": module_id,
                                "quantity": 1,
                                "capacity_before": int(capacity_before),
                                "capacity_after": int(capacity_after),
                                "physical_capacity": int(physical_capacity) if physical_capacity is not None else None,
                            },
                        )
                    except Exception:
                        # Logging must never break loot application
                        pass
        
        # Clear pending loot
        self._pending_loot = None
        
        # Check if there are remaining encounters to process
        # After loot resolution, if encounters remain, we need to resume encounter flow
        # Use the helper function to ensure encounter immutability
        if self._pending_travel is not None:
            remaining_encounters = self._pending_travel.get("remaining_encounters", [])
            if remaining_encounters:
                # Use helper function to resume encounters (ensures immutability)
                from time_engine import get_current_turn
                temp_context = EngineContext(
                    command={"type": "resolve_pending_loot"},
                    command_type="resolve_pending_loot",
                    turn_before=int(get_current_turn()),
                    turn_after=int(get_current_turn()),
                )
                
                has_more = self._resume_travel_encounters_if_any(temp_context)
                if has_more:
                    return {"ok": True, "resume_encounters": True}
        
        return {"ok": True}

    def has_pending_combat(self) -> bool:
        """Check if there is a pending combat session requiring player input."""
        return self._pending_combat is not None

    def get_pending_encounter_info(self) -> dict[str, Any] | None:
        """Get the pending encounter information for CLI display. Returns None if no pending encounter."""
        if not self.has_pending_encounter():
            return None
        encounter_context = self._pending_travel.get("encounter_context", {})
        current_encounter = self._pending_travel.get("current_encounter")
        
        # Extract encounter description and ship info
        encounter_description = None
        npc_ship_info = None
        
        if current_encounter is not None:
            subtype_id = getattr(current_encounter, "subtype_id", None)
            if subtype_id:
                encounter_description = self._get_encounter_description(subtype_id)
            
            # Generate NPC ship info for display (deterministic, same as combat will use)
            try:
                from npc_ship_generator import generate_npc_ship
                system = self.sector.get_system(self.player_state.current_system_id)
                if system is not None:
                    encounter_id = str(getattr(current_encounter, "encounter_id", ""))
                    enemy_ship_dict = generate_npc_ship(
                        world_seed=self.world_seed,
                        system_id=self.player_state.current_system_id,
                        system_population=int(system.population),
                        encounter_id=encounter_id,
                        encounter_subtype=str(subtype_id),
                    )
                    # Format ship info with only frame (no modules/stats)
                    npc_ship_info = self._format_ship_info_frame_only(enemy_ship_dict)
            except Exception:
                # If ship generation fails, just skip ship info
                npc_ship_info = None
        
        return {
            "encounter_id": encounter_context.get("encounter_id"),
            "options": encounter_context.get("options", []),
            "encounter_description": encounter_description,
            "npc_ship_info": npc_ship_info,
        }

    def get_pending_combat_info(self) -> dict[str, Any] | None:
        """Get the pending combat information for CLI display. Returns None if no pending combat."""
        if not self.has_pending_combat():
            return None
        pending = self._pending_combat
        # Build the pending_combat payload similar to _build_step_result
        from combat_resolver import available_actions, hull_percent
        
        player_ship_state = pending.get("player_ship_state")
        player_state = pending.get("player_state")
        enemy_state = pending.get("enemy_state")
        enemy_ship_dict = pending.get("enemy_ship_dict")
        spec = pending.get("spec")
        
        if not player_ship_state or not player_state:
            return None
        
        allowed_actions_list = available_actions(player_ship_state, player_state)
        round_number = pending.get("round_number", 0) + 1  # Next round
        player_hull_pct = hull_percent(player_state.hull_current, player_state.hull_max) if player_state.hull_max > 0 else 0
        enemy_hull_pct = hull_percent(enemy_state.hull_current, enemy_state.hull_max) if enemy_state and enemy_state.hull_max > 0 else 0
        
        # Check for invalid state (hull_max <= 0)
        invalid_state = False
        error_msg = None
        if player_state.hull_max <= 0 or (enemy_state and enemy_state.hull_max <= 0):
            invalid_state = True
            error_msg = f"invalid_combat_state: player_hull_max={player_state.hull_max}, enemy_hull_max={enemy_state.hull_max if enemy_state else 'None'}, player_hull_id={player_ship_state.get('hull_id', 'unknown')}, enemy_hull_id={pending.get('enemy_ship_dict', {}).get('hull_id', 'unknown')}"
        
        # Map contract action names to lower_snake_case IDs
        action_options = []
        for action in allowed_actions_list:
            action_id = action.lower().replace(" ", "_")
            action_options.append({"id": action_id, "label": action})
        
        # Extract encounter description and enemy ship info
        encounter_description = None
        enemy_ship_info = None
        
        if spec is not None:
            subtype_id = getattr(spec, "subtype_id", None)
            if subtype_id:
                encounter_description = self._get_encounter_description(subtype_id)
        
        if enemy_ship_dict is not None:
            enemy_ship_info = self._format_ship_info(enemy_ship_dict)
        
        return {
            "combat_id": pending.get("combat_id"),
            "encounter_id": pending.get("encounter_id"),
            "round_number": round_number,
            "player_hull_pct": player_hull_pct,
            "enemy_hull_pct": enemy_hull_pct,
            "allowed_actions": action_options,
            "invalid_state": invalid_state,
            "error": error_msg,
            "player_hull_max": player_state.hull_max if player_state else 0,
            "enemy_hull_max": enemy_state.hull_max if enemy_state else 0,
            "encounter_description": encounter_description,
            "enemy_ship_info": enemy_ship_info,
        }

    def _execute_travel_to_destination(self, context: EngineContext, payload: dict[str, Any]) -> None:
        # Travel safety guard: prevent stacking travel while pending state exists
        if self._pending_travel is not None:
            # Check if there's a current encounter or remaining encounters
            if self._pending_travel.get("current_encounter") is not None or self._pending_travel.get("remaining_encounters"):
                context.hard_stop = True
                context.hard_stop_reason = "pending_encounter_decision"
                return
        if self._pending_loot is not None:
            context.hard_stop = True
            context.hard_stop_reason = "pending_loot_decision"
            return
        if self._pending_combat is not None:
            context.hard_stop = True
            context.hard_stop_reason = "pending_combat_action"
            return
        
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
        required_fuel = max(1, int(math.ceil(distance_ly))) if inter_system else 0
        
        if inter_system and float(distance_ly) > float(current_fuel):
            raise ValueError("warp_range_exceeded")
        if current_fuel < required_fuel:
            raise ValueError("insufficient_fuel")

        new_fuel = max(0, min(current_fuel - required_fuel, fuel_capacity))
        active_ship.set_current_fuel(new_fuel, self._logger, context.turn_before)
        self._event(
            context,
            stage="travel",
            subsystem="travel_resolution",
            detail={
                "travel_id": travel_id,
                "success": True,
                "reason": "ok",
                "fuel_cost": int(required_fuel),
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
        
        # Evaluate active missions after player state is updated (for delivery missions)
        # This runs even if encounters are pending, so delivery missions can complete on arrival
        evaluate_active_missions(
            mission_manager=self._mission_manager,
            player_state=self.player_state,
            current_system_id=target_system_id,
            current_destination_id=target_destination_id,
            event_context={"event": "travel_arrival", "target_system_id": target_system_id, "target_destination_id": target_destination_id},
            logger=self._logger if self._logging_enabled else None,
            turn=context.turn_before,
        )

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
        
        # Store original encounter list IMMEDIATELY after generation - never reconstruct
        original_encounters = list(encounters)  # Make a copy to preserve immutability
        original_encounter_count = len(original_encounters)
        
        # Do NOT use context.active_encounters as authoritative queue - set to empty to avoid confusion
        context.active_encounters = []
        self._event(
            context,
            stage="encounter_gen",
            subsystem="encounter_generator",
            detail={"travel_id": travel_id, "encounter_count": original_encounter_count},
        )

        # Initialize pending_travel with cursor-based tracking
        # Store all encounters in remaining_encounters, cursor starts at 0
        # This is the ONLY authoritative queue for travel encounters
        self._pending_travel = {
            "travel_id": travel_id,
            "target_system_id": target_system_id,
            "target_destination_id": target_destination_id,
            "payload": payload,
            "original_encounter_count": original_encounter_count,
            "encounter_cursor": 0,  # Track how many encounters have been processed
            "remaining_encounters": original_encounters.copy(),  # Full list, will be popped from
            "current_encounter": None,
            "encounter_context": None,
            "events_so_far": list(context.events),
        }
        
        # Check if encounter_action is explicitly provided in payload
        encounter_action = payload.get("encounter_action")
        if encounter_action is None:
            # No explicit action provided - require player input
            # Use resume function to set up first encounter
            self._resume_travel_encounters_if_any(context)
        else:
            # Explicit action provided - resolve encounters automatically
            # Loop using ONLY pending_travel["remaining_encounters"] as authoritative queue
            while self._pending_travel is not None and self._pending_travel.get("remaining_encounters") and not context.hard_stop:
                # Pop next encounter from authoritative queue
                next_encounter = self._pending_travel["remaining_encounters"].pop(0)
                self._pending_travel["current_encounter"] = next_encounter
                self._pending_travel["encounter_cursor"] = self._pending_travel.get("encounter_cursor", 0) + 1
                
                # Resolve the encounter
                self._resolve_encounter(
                    context=context,
                    spec=next_encounter,
                    player_action=str(encounter_action),
                )
                
                # Append events from resolved encounter to travel events
                events_so_far = self._pending_travel.get("events_so_far", [])
                events_so_far.extend(context.events)
                context.events = list(events_so_far)
                self._pending_travel["events_so_far"] = list(events_so_far)
                
                # Clear current_encounter after resolution
                self._pending_travel["current_encounter"] = None
                
                # Evaluate hard stop (combat, loot, game_over, etc)
                self._evaluate_hard_stop(context)
                
                # If hard stop is active, preserve pending_travel state and stop
                if context.hard_stop:
                    break
            
            # End-of-travel cleanup: only clear if all encounters processed AND no hard stop
            if self._pending_travel is not None:
                remaining = self._pending_travel.get("remaining_encounters", [])
                if not remaining and not context.hard_stop:
                    # All encounters processed, no hard stop - clear pending travel
                    self._pending_travel = None
                context.active_encounters = [
                    row
                    for row in context.active_encounters
                    if str(getattr(row, "encounter_id", "")) != str(getattr(encounter, "encounter_id", ""))
                ]
                self._evaluate_hard_stop(context)
                
                # Evaluate active missions after travel completes (handled by travel_arrival event)
                # Mission evaluation already runs on travel arrival, so skip here to avoid duplicate evaluation

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

    def _execute_set_active_ship(self, context: EngineContext, payload: dict[str, Any]) -> None:
        """Set active ship with validation."""
        ship_id = payload.get("ship_id")
        if not isinstance(ship_id, str) or not ship_id:
            raise ValueError("set_active_ship requires ship_id.")
        
        # Validate ship is owned
        if ship_id not in self.player_state.owned_ship_ids:
            raise ValueError("ship_not_owned")
        
        target_ship = self.fleet_by_id.get(ship_id)
        if target_ship is None:
            raise ValueError("ship_not_found")
        
        # Validate no active combat
        if self._pending_combat is not None:
            raise ValueError("cannot_change_ship_during_combat")
        
        # Validate same destination
        current_destination = self.player_state.current_destination_id
        target_destination = target_ship.destination_id or target_ship.current_destination_id
        if target_destination != current_destination:
            raise ValueError("ship_at_different_destination")
        
        # Change active ship
        old_ship_id = self.player_state.active_ship_id
        self.player_state.active_ship_id = ship_id
        
        self._event(
            context,
            stage="ship_change",
            subsystem="engine",
            detail={
                "action": "ship_change_active",
                "old_ship_id": old_ship_id,
                "new_ship_id": ship_id,
            },
        )

    def _execute_transfer_cargo(self, context: EngineContext, payload: dict[str, Any]) -> None:
        """Transfer cargo between ships with capacity validation."""
        source_ship_id = payload.get("source_ship_id")
        target_ship_id = payload.get("target_ship_id")
        sku = payload.get("sku")
        quantity = payload.get("quantity")
        
        if not isinstance(source_ship_id, str) or not source_ship_id:
            raise ValueError("transfer_cargo requires source_ship_id.")
        if not isinstance(target_ship_id, str) or not target_ship_id:
            raise ValueError("transfer_cargo requires target_ship_id.")
        if not isinstance(sku, str) or not sku:
            raise ValueError("transfer_cargo requires sku.")
        if not isinstance(quantity, int) or quantity < 1:
            raise ValueError("transfer_cargo requires positive quantity.")
        
        # Validate both ships are owned
        if source_ship_id not in self.player_state.owned_ship_ids:
            raise ValueError("source_ship_not_owned")
        if target_ship_id not in self.player_state.owned_ship_ids:
            raise ValueError("target_ship_not_owned")
        
        # Validate same destination
        source_ship = self.fleet_by_id.get(source_ship_id)
        target_ship = self.fleet_by_id.get(target_ship_id)
        if source_ship is None or target_ship is None:
            raise ValueError("ship_not_found")
        
        source_dest = source_ship.destination_id or source_ship.current_destination_id
        target_dest = target_ship.destination_id or target_ship.current_destination_id
        if source_dest != target_dest:
            raise ValueError("ships_at_different_destinations")
        
        # Get cargo manifests
        source_cargo = self.player_state.cargo_by_ship.get(source_ship_id, {})
        target_cargo = self.player_state.cargo_by_ship.get(target_ship_id, {})
        
        # Validate source has enough cargo
        available = int(source_cargo.get(sku, 0) or 0)
        if available < quantity:
            raise ValueError("insufficient_cargo")
        
        # Determine cargo type and validate capacity
        from data_loader import load_goods
        goods_data = load_goods()
        is_data_cargo = False
        for good in goods_data.get("goods", []):
            if good.get("sku_id") == sku:
                tags = good.get("tags", [])
                if "data" in tags:
                    is_data_cargo = True
                break
        
        # Calculate target capacity (simplified - would need ship assembler for accurate capacity)
        target_physical_capacity = target_ship.physical_cargo_capacity or 0
        target_data_capacity = target_ship.data_cargo_capacity or 0
        
        # Calculate current usage
        current_physical = sum(int(qty) for sku_id, qty in target_cargo.items() if not _is_data_cargo_sku(sku_id))
        current_data = sum(int(qty) for sku_id, qty in target_cargo.items() if _is_data_cargo_sku(sku_id))
        
        # Validate capacity
        if is_data_cargo:
            if current_data + quantity > target_data_capacity:
                raise ValueError("target_ship_data_capacity_exceeded")
        else:
            if current_physical + quantity > target_physical_capacity:
                raise ValueError("target_ship_physical_capacity_exceeded")
        
        # Transfer cargo
        if source_ship_id not in self.player_state.cargo_by_ship:
            self.player_state.cargo_by_ship[source_ship_id] = {}
        if target_ship_id not in self.player_state.cargo_by_ship:
            self.player_state.cargo_by_ship[target_ship_id] = {}
        
        source_cargo = self.player_state.cargo_by_ship[source_ship_id]
        target_cargo = self.player_state.cargo_by_ship[target_ship_id]
        
        source_cargo[sku] = int(source_cargo.get(sku, 0) or 0) - quantity
        if source_cargo[sku] <= 0:
            del source_cargo[sku]
        
        target_cargo[sku] = int(target_cargo.get(sku, 0) or 0) + quantity
        
        self._event(
            context,
            stage="cargo_transfer",
            subsystem="engine",
            detail={
                "action": "cargo_transfer",
                "source_ship_id": source_ship_id,
                "target_ship_id": target_ship_id,
                "sku": sku,
                "quantity": quantity,
            },
        )

    def _execute_abandon_mission(self, context: EngineContext, payload: dict[str, Any]) -> None:
        """Abandon an active mission."""
        mission_id = payload.get("mission_id")
        if not isinstance(mission_id, str) or not mission_id:
            raise ValueError("abandon_mission requires mission_id.")
        
        if mission_id not in self.player_state.active_missions:
            raise ValueError("mission_not_active")
        
        self._mission_manager.abandon(
            mission_id=mission_id,
            player=self.player_state,
            reason="player_abandoned",
            logger=self._logger if self._logging_enabled else None,
            turn=int(get_current_turn()),
        )
        
        self._event(
            context,
            stage="mission",
            subsystem="mission_manager",
            detail={
                "action": "mission_abandon",
                "mission_id": mission_id,
            },
        )

    def _execute_claim_mission(self, context: EngineContext, payload: dict[str, Any]) -> None:
        """Claim mission reward (Phase 7.11.2a)."""
        from mission_manager import _calculate_mission_credit_reward, _load_reward_profiles
        
        mission_id = payload.get("mission_id")
        if not isinstance(mission_id, str) or not mission_id:
            context.claim_mission_error = "claim_mission requires mission_id."
            self._event(
                context,
                stage="mission",
                subsystem="mission_manager",
                detail={
                    "action": "claim_mission",
                    "mission_id": mission_id,
                    "ok": False,
                    "reason": "claim_mission requires mission_id.",
                },
            )
            return
        
        # Fetch mission
        mission = self._mission_manager.missions.get(mission_id)
        if mission is None:
            context.claim_mission_error = f"Mission {mission_id} not found."
            self._event(
                context,
                stage="mission",
                subsystem="mission_manager",
                detail={
                    "action": "claim_mission",
                    "mission_id": mission_id,
                    "ok": False,
                    "reason": f"Mission {mission_id} not found.",
                },
            )
            return
        
        # Validate mission state
        if mission.mission_state.value != "resolved":
            context.claim_mission_error = f"Mission {mission_id} is not resolved (state: {mission.mission_state.value})."
            self._event(
                context,
                stage="mission",
                subsystem="mission_manager",
                detail={
                    "action": "claim_mission",
                    "mission_id": mission_id,
                    "ok": False,
                    "reason": f"Mission {mission_id} is not resolved.",
                },
            )
            return
        
        if mission.outcome != "completed":
            context.claim_mission_error = f"Mission {mission_id} was not completed (outcome: {mission.outcome})."
            self._event(
                context,
                stage="mission",
                subsystem="mission_manager",
                detail={
                    "action": "claim_mission",
                    "mission_id": mission_id,
                    "ok": False,
                    "reason": f"Mission {mission_id} was not completed.",
                },
            )
            return
        
        if mission.reward_status != "ungranted":
            context.claim_mission_error = f"Mission {mission_id} reward already granted (status: {mission.reward_status})."
            self._event(
                context,
                stage="mission",
                subsystem="mission_manager",
                detail={
                    "action": "claim_mission",
                    "mission_id": mission_id,
                    "ok": False,
                    "reason": f"Mission {mission_id} reward already granted.",
                },
            )
            return
        
        if mission.payout_policy != "claim_required":
            context.claim_mission_error = f"Mission {mission_id} does not require claim (payout_policy: {mission.payout_policy})."
            self._event(
                context,
                stage="mission",
                subsystem="mission_manager",
                detail={
                    "action": "claim_mission",
                    "mission_id": mission_id,
                    "ok": False,
                    "reason": f"Mission {mission_id} does not require claim.",
                },
            )
            return
        
        # Validate claim_scope
        claim_scope = mission.claim_scope
        if claim_scope == "none":
            context.claim_mission_error = f"Mission {mission_id} has claim_scope='none' (invalid for claim_required)."
            self._event(
                context,
                stage="mission",
                subsystem="mission_manager",
                detail={
                    "action": "claim_mission",
                    "mission_id": mission_id,
                    "ok": False,
                    "reason": f"Mission {mission_id} has invalid claim_scope.",
                },
            )
            return
        
        # Get current location/entity for validation
        current_location_id = self.player_state.current_location_id
        mission_source = mission.source
        
        # Validate claim_scope
        if claim_scope == "source_entity":
            # Must be interacting with the exact source entity
            source_id = mission_source.get("source_id")
            if not source_id or current_location_id != source_id:
                context.claim_mission_error = f"Must claim reward from source entity '{source_id}' (currently at '{current_location_id}')."
                self._event(
                    context,
                    stage="mission",
                    subsystem="mission_manager",
                    detail={
                        "action": "claim_mission",
                        "mission_id": mission_id,
                        "ok": False,
                        "reason": f"Must claim from source entity '{source_id}'.",
                    },
                )
                return
        elif claim_scope == "any_source_type":
            # Must be interacting with any entity of the same source_type
            source_type = mission_source.get("source_type")
            # For now, we'll check if current_location_id matches any location with that source_type
            # This is a simplified check - in a full implementation, we'd check the location's type
            # For Phase 7.11.2a, we'll allow if source_type matches (simplified validation)
            # TODO: Full validation would check location.entity_type or location.source_type
            if not source_type:
                context.claim_mission_error = f"Mission {mission_id} has invalid source_type."
                self._event(
                    context,
                    stage="mission",
                    subsystem="mission_manager",
                    detail={
                        "action": "claim_mission",
                        "mission_id": mission_id,
                        "ok": False,
                        "reason": f"Mission {mission_id} has invalid source_type.",
                    },
                )
                return
            # Simplified: allow if we're at a location (full validation would check location type)
            if not current_location_id:
                context.claim_mission_error = f"Must be at a location to claim reward (source_type: {source_type})."
                self._event(
                    context,
                    stage="mission",
                    subsystem="mission_manager",
                    detail={
                        "action": "claim_mission",
                        "mission_id": mission_id,
                        "ok": False,
                        "reason": f"Must be at a location to claim reward.",
                    },
                )
                return
        
        # All validations passed - grant reward
        try:
            reward_profiles = _load_reward_profiles()
            credit_reward = _calculate_mission_credit_reward(mission, reward_profiles)
            self.player_state.credits += credit_reward
            mission.reward_status = "granted"
            mission.reward_granted_turn = context.turn_before
            
            # Log reward granted
            if self._logging_enabled and self._logger:
                self._logger.log(
                    turn=context.turn_before,
                    action="mission_reward_granted",
                    state_change=(
                        f"mission_id={mission_id} payout_policy=claim_required "
                        f"claim_scope={claim_scope} credits={credit_reward} new_balance={self.player_state.credits}"
                    ),
                )
            
            # Emit success event
            self._event(
                context,
                stage="mission",
                subsystem="mission_manager",
                detail={
                    "action": "claim_mission",
                    "mission_id": mission_id,
                    "ok": True,
                    "credits": credit_reward,
                    "new_balance": self.player_state.credits,
                },
            )
        except ValueError as e:
            context.claim_mission_error = f"Failed to calculate reward: {str(e)}"
            self._event(
                context,
                stage="mission",
                subsystem="mission_manager",
                detail={
                    "action": "claim_mission",
                    "mission_id": mission_id,
                    "ok": False,
                    "reason": f"Failed to calculate reward: {str(e)}",
                },
            )

    def _evaluate_active_missions_on_turn_tick(self, *, logger=None, turn=0) -> None:
        """Lightweight evaluation on turn advance (secondary trigger)."""
        evaluate_active_missions(
            mission_manager=self._mission_manager,
            player_state=self.player_state,
            current_system_id=self.player_state.current_system_id,
            current_destination_id=self.player_state.current_destination_id,
            event_context={"event": "turn_tick"},
            logger=logger,
            turn=turn,
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

    def _select_mission_tier(self, source_type: str, rng: random.Random) -> int:
        """Select mission tier deterministically based on source_type (Phase 7.11.x).

        Tier rules:
        - BAR:
            roll = rng.randint(0, 99)
            if roll < 85: tier = rng.randint(1, 3), rare_flag=False
            else:        tier = rng.randint(4, 5), rare_flag=True
        - ADMINISTRATION:
            roll = rng.randint(0, 99)
            if roll < 85: tier = rng.randint(2, 4), rare_flag=False
            else:        tier = rng.choice([1, 5]), rare_flag=True
        - DATANET:
            tier = rng.randint(4, 5), rare_flag=False  (never below 4)
        """
        source_type = str(source_type or "").strip()
        rare_flag = False
        tier_roll: int | None = None

        if source_type == "bar":
            tier_roll = rng.randint(0, 99)
            if tier_roll < 85:
                tier = rng.randint(1, 3)
                rare_flag = False
            else:
                tier = rng.randint(4, 5)
                rare_flag = True
        elif source_type == "administration":
            tier_roll = rng.randint(0, 99)
            if tier_roll < 85:
                tier = rng.randint(2, 4)
                rare_flag = False
            else:
                tier = rng.choice([1, 5])
                rare_flag = True
        elif source_type == "datanet":
            # Datanet missions are always high tier (4–5)
            tier = rng.randint(4, 5)
            rare_flag = False
            tier_roll = None
        else:
            # Should not occur given ALLOWED_LOCATION_TYPES, but keep deterministic default
            tier = 1
            rare_flag = False
            tier_roll = None

        # Structured logging for tier selection
        if self._logging_enabled and self._logger:
            self._logger.log(
                turn=int(get_current_turn()),
                action="mission_generation:tier_roll",
                state_change=(
                    f"source_type={source_type} "
                    f"tier_roll={tier_roll if tier_roll is not None else 'NA'} "
                    f"selected_tier={tier} rare_flag={rare_flag}"
                ),
            )

        return tier

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
        
        # Get location type for source field
        location = self._current_location()
        location_type = str(getattr(location, "location_type", "") or "") if location else ""
        
        # Map location_type to source_type: "bar" -> "bar", "administration" -> "administration", "datanet" -> "datanet"
        # Victory missions should explicitly pass source_type="victory" (not mapped from location_type)
        ALLOWED_LOCATION_TYPES = {"bar", "administration", "datanet"}
        
        if location_type not in ALLOWED_LOCATION_TYPES:
            # Raise clear error for unrecognized location_type (no default to "system")
            if location_type:
                raise ValueError(
                    f"Unrecognized location_type '{location_type}' for mission generation. "
                    f"Allowed location_types: {sorted(ALLOWED_LOCATION_TYPES)}. "
                    f"Victory missions should explicitly pass source_type='victory'."
                )
            else:
                # Empty location_type - skip mission generation
                return []
        
        source_type = location_type  # Direct mapping: location_type -> source_type
        
        # Deterministic mission count based on location (no turn dependency)
        rng = self._mission_rng_for_location(location_id=location_id, turn=None)
        mission_count = 0

        # Phase 7.11.x - Deterministic mission count per source_type
        if source_type == "bar":
            # BAR: count = rng.randint(1, int(population * 1.5)) with safe upper bound
            upper = int(population * 1.5)
            if upper < 1:
                upper = 1
            mission_count = rng.randint(1, upper)
        elif source_type == "administration":
            # ADMINISTRATION: count = rng.randint(1, population) with safe upper bound
            upper = population if population > 0 else 1
            mission_count = rng.randint(1, upper)
        elif source_type == "datanet":
            # DATANET: two-stage rarity gate
            gate_roll = rng.randint(0, 99)
            if self._logging_enabled and self._logger:
                # Log datanet gate decision
                # final_count will be logged below once determined
                self._logger.log(
                    turn=int(get_current_turn()),
                    action="mission_generation:datanet_gate",
                    state_change=(
                        f"source_type={source_type} population={population} "
                        f"gate_roll={gate_roll}"
                    ),
                )
            if gate_roll < 20:
                mission_count = rng.randint(1, 2)
            else:
                mission_count = 0

        # Structured logging for mission counts
        if self._logging_enabled and self._logger:
            self._logger.log(
                turn=int(get_current_turn()),
                action="mission_generation:count",
                state_change=(
                    f"source_type={source_type} population={population} "
                    f"final_count={mission_count}"
                ),
            )
        
        # Generate new mission offers
        offered_ids: list[str] = []
        for index in range(mission_count):
            # Phase 7.11.2: Mission type selection is data-driven via mission_registry
            # and filtered to implemented creators only.
            candidates = mission_type_candidates_for_source(source_type=source_type)

            # Filter to mission types that have implemented creators
            implemented_candidates: list[dict[str, Any]] = []
            for row in candidates:
                mt_id = str(row.get("mission_type_id", "") or "")
                if mt_id in CREATOR_BY_TYPE:
                    implemented_candidates.append(row)
                else:
                    # Deterministic log for registry entries without creators
                    if self._logging_enabled and self._logger:
                        self._logger.log(
                            turn=int(get_current_turn()),
                            action="mission_generation:skipped_unimplemented_type",
                            state_change=(
                                f"location_id={location_id} source_type={source_type} "
                                f"mission_type_id={mt_id}"
                            ),
                        )

            if not implemented_candidates:
                raise ValueError(
                    f"No implemented mission types available for source_type='{source_type}' "
                    f"at location '{location_id}'."
                )

            mission_type, _ = select_weighted_mission_type(
                eligible_missions=implemented_candidates,
                rng=rng,
                world_state_engine=self._world_state_engine(),
                system_id=self.player_state.current_system_id,
            )

            mission_type_id = mission_type if isinstance(mission_type, str) and mission_type else "delivery"

            if mission_type_id not in CREATOR_BY_TYPE:
                raise ValueError(
                    f"Selected mission_type_id '{mission_type_id}' has no creator in CREATOR_BY_TYPE."
                )
            # Deterministic mission_id seed (no turn dependency for persistence)
            
            # Use structured delivery mission creation for delivery missions
            if mission_type_id == "delivery":
                mission_tier = self._select_mission_tier(source_type=source_type, rng=rng)
                mission = create_delivery_mission(
                    source_type=source_type,
                    source_id=f"{location_id}:{index}",
                    origin_system_id=self.player_state.current_system_id,
                    origin_destination_id=self.player_state.current_destination_id,
                    origin_location_id=location_id,
                    mission_tier=mission_tier,
                    galaxy=self.sector,
                    catalog=self.catalog,
                    rng=rng,
                    logger=self._logger if self._logging_enabled else None,
                    turn=int(get_current_turn()),
                )
            else:
                # For Phase 7.11.2, only delivery missions are implemented and
                # should be selectable. If we ever reach this branch, it
                # indicates a registry/creator mismatch.
                raise ValueError(
                    f"Unsupported mission_type_id '{mission_type_id}' for generation. "
                    f"Only structured types with creators are allowed."
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

    def _execute_dismiss_crew(self, context: EngineContext, payload: dict[str, Any]) -> None:
        """
        Dismiss a crew member from the player's active ship.
        Relocates the crew NPC to the nearest bar location deterministically.
        """
        npc_id = payload.get("npc_id")
        if not isinstance(npc_id, str) or not npc_id:
            raise ValueError("dismiss_crew requires npc_id")
        
        # Get active ship
        active_ship = self._active_ship()
        
        # Find the crew member
        crew_npc = None
        for member in active_ship.crew:
            if getattr(member, "npc_id", None) == npc_id:
                crew_npc = member
                break
        
        if crew_npc is None:
            self._event(
                context,
                stage="crew_dismissal",
                subsystem="engine",
                detail={"action": "dismiss_crew", "result": {"ok": False, "reason": "crew_not_found", "npc_id": npc_id}},
            )
            return
        
        # Validate crew NPC contract
        if not isinstance(crew_npc, NPCEntity):
            raise ValueError("crew member must be NPCEntity")
        if crew_npc.persistence_tier != NPCPersistenceTier.TIER_2:
            raise ValueError("crew must be TIER_2")
        
        # Find nearest bar location for relocation
        current_system_id = self.player_state.current_system_id
        current_destination_id = self.player_state.current_destination_id
        
        try:
            target_system_id, target_destination_id, target_location_id = self._find_nearest_bar_location(
                system_id=current_system_id,
                preferred_destination_id=current_destination_id,
            )
        except RuntimeError as e:
            self._event(
                context,
                stage="crew_dismissal",
                subsystem="engine",
                detail={"action": "dismiss_crew", "result": {"ok": False, "reason": "no_bar_found", "error": str(e)}},
            )
            return
        
        # Update NPC: remove from ship, relocate to bar
        crew_npc.current_ship_id = None
        crew_npc.current_system_id = target_system_id
        crew_npc.current_location_id = target_location_id
        # Ensure persistence tier remains TIER_2 (do not downgrade)
        if crew_npc.persistence_tier != NPCPersistenceTier.TIER_2:
            crew_npc.persistence_tier = NPCPersistenceTier.TIER_2
        
        # Remove from ship's crew list
        active_ship.remove_crew(npc_id)
        
        # Update registry (persist NPC back)
        self._npc_registry.update(
            crew_npc,
            logger=self._logger if self._logging_enabled else None,
            turn=int(get_current_turn()),
        )
        
        self._event(
            context,
            stage="crew_dismissal",
            subsystem="engine",
            detail={
                "action": "dismiss_crew",
                "result": {
                    "ok": True,
                    "reason": "ok",
                    "npc_id": npc_id,
                    "relocated_to": {
                        "system_id": target_system_id,
                        "destination_id": target_destination_id,
                        "location_id": target_location_id,
                    },
                },
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

    def _ensure_datanet_mission_offers(self, *, location_id: str) -> list[str]:
        """Ensure DataNet mission offers exist for a datanet location (Phase 7.x).

        DataNet rules:
        - 20% activation chance per access
        - If inactive: zero missions
        - If active: generate 1–2 missions
        - Tier floor: 4 (tier 4 or 5 only)
        - source_type = \"datanet\"
        - Offers persist until refresh or turn advance.
        """
        key = str(location_id or "")
        if not key:
            return []

        # If offers already exist for this location, return cached list
        existing = self._mission_manager.datanet_offers.get(key)
        if isinstance(existing, list):
            return list(existing)

        # Generate new offers for this DataNet location
        rng = self._mission_rng_for_location(location_id=key, turn=None)
        gate_roll = rng.randint(0, 99)

        # Log DataNet gate decision
        if self._logging_enabled and self._logger:
            self._logger.log(
                turn=int(get_current_turn()),
                action="mission_generation:datanet_gate",
                state_change=(
                    f"source_type=datanet population=NA gate_roll={gate_roll}"
                ),
            )

        mission_ids: list[str] = []
        if gate_roll < 20:
            # Active: generate 1–2 missions
            count = rng.randint(1, 2)
            for index in range(count):
                # For now, only delivery missions are implemented
                mission_tier = self._select_mission_tier(source_type="datanet", rng=rng)
                mission = create_delivery_mission(
                    source_type="datanet",
                    source_id=f"{key}:{index}",
                    origin_system_id=self.player_state.current_system_id,
                    origin_destination_id=self.player_state.current_destination_id,
                    origin_location_id=key,
                    mission_tier=mission_tier,
                    galaxy=self.sector,
                    catalog=self.catalog,
                    rng=rng,
                    logger=self._logger if self._logging_enabled else None,
                    turn=int(get_current_turn()),
                )
                mission.location_id = key
                mission.mission_contact_seed = f"{self.world_seed}|{self.player_state.current_system_id}|{key}|{mission.mission_id}|contact"
                self._mission_manager.offer(mission)
                mission_ids.append(mission.mission_id)

        # Persist offers for this location until refresh or turn advance
        self._mission_manager.datanet_offers[key] = list(mission_ids)

        # Structured logging for count
        if self._logging_enabled and self._logger:
            self._logger.log(
                turn=int(get_current_turn()),
                action="mission_generation:count",
                state_change=(
                    f"source_type=datanet population=NA final_count={len(mission_ids)}"
                ),
            )

        return mission_ids

    def _datanet_mission_rows_for_location(self, *, location_id: str) -> list[dict[str, Any]]:
        """Build mission rows for a DataNet location from datanet_offers."""
        mission_ids = self._ensure_datanet_mission_offers(location_id=location_id)
        rows: list[dict[str, Any]] = []
        for mission_id in mission_ids:
            mission = self._mission_manager.missions.get(mission_id)
            if mission is None:
                continue
            rows.append(
                {
                    "mission_id": mission.mission_id,
                    "mission_type": mission.mission_type,
                    "mission_tier": int(mission.mission_tier),
                    "mission_state": str(mission.mission_state),
                }
            )
        return rows

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

    def _execute_encounter_decision(self, context: EngineContext, payload: dict[str, Any]) -> None:
        """Handle encounter decision from CLI and resume travel processing."""
        # Validate pending travel exists
        if self._pending_travel is None:
            raise ValueError("encounter_decision requires a pending travel.")
        
        # Validate encounter_id matches
        encounter_id = payload.get("encounter_id")
        decision_id = payload.get("decision_id")
        if not isinstance(encounter_id, str) or not encounter_id:
            raise ValueError("encounter_decision requires encounter_id.")
        if not isinstance(decision_id, str) or not decision_id:
            raise ValueError("encounter_decision requires decision_id.")
        
        current_encounter = self._pending_travel.get("current_encounter")
        if current_encounter is None:
            raise ValueError("encounter_decision: no current encounter in pending travel.")
        
        stored_encounter_id = str(getattr(current_encounter, "encounter_id", ""))
        if stored_encounter_id != encounter_id:
            raise ValueError(f"encounter_decision: encounter_id mismatch. Expected {stored_encounter_id}, got {encounter_id}.")
        
        # Resolve the current encounter with the decision
        self._resolve_encounter(
            context=context,
            spec=current_encounter,
            player_action=str(decision_id),
        )
        
        # Append events from resolved encounter to travel events
        events_so_far = self._pending_travel.get("events_so_far", [])
        events_so_far.extend(context.events)
        context.events = list(events_so_far)
        self._pending_travel["events_so_far"] = list(events_so_far)
        
        # Clear current_encounter after resolution
        self._pending_travel["current_encounter"] = None
        
        # Explicit resume logic: only resume when encounter is fully resolved
        # Do NOT resume if:
        # - Combat was triggered (hard_stop_reason == "pending_combat_action")
        # - Loot is pending (hard_stop_reason == "pending_loot_decision")
        # - Game over (hard_stop_reason == "game_over")
        # Resume ONLY if:
        # - No hard_stop (encounter fully resolved without combat/loot)
        # - OR hard_stop is set but for a reason that allows resuming
        
        if context.hard_stop:
            # Check if hard_stop is for a reason that prevents resuming
            if context.hard_stop_reason in ("pending_combat_action", "pending_loot_decision", "game_over"):
                # Combat, loot, or game over pending - do NOT resume encounters yet
                return
            # Other hard_stop reasons - allow resume (shouldn't happen in normal flow)
        
        # Encounter resolved without combat/loot - resume next encounter if any
        if self._pending_travel is not None:
            remaining = self._pending_travel.get("remaining_encounters", [])
            if remaining:
                # More encounters remain - resume
                self._resume_travel_encounters_if_any(context)
            else:
                # No more encounters - clear pending travel
                self._pending_travel = None

    def _resume_travel_encounters_if_any(self, context: EngineContext) -> bool:
        """
        Resume travel encounter queue if encounters remain.
        
        Checks if there are remaining encounters in the current travel sequence.
        If yes, sets up the next encounter and configures context for player input.
        
        ENCOUNTER IMMUTABILITY RULE:
        - Encounters are created exactly once during generation
        - This function ONLY pops from remaining_encounters list
        - Absolutely NO reconstruction, re-indexing, or re-derivation of encounters
        - Cursor tracks how many encounters have been processed
        
        Args:
            context: EngineContext to update with hard_stop state
            
        Returns:
            True if next encounter was set up, False if no encounters remain
        """
        # Check if we're in a travel sequence with remaining encounters
        if self._pending_travel is None:
            return False
        
        remaining_encounters = self._pending_travel.get("remaining_encounters", [])
        if not remaining_encounters:
            # No more encounters - clear pending travel
            self._pending_travel = None
            return False
        
        # Guard assertion: verify encounter count consistency using cursor
        original_count = self._pending_travel.get("original_encounter_count")
        cursor = self._pending_travel.get("encounter_cursor", 0)
        
        if original_count is not None:
            expected_remaining = original_count - cursor
            actual_remaining = len(remaining_encounters)
            if actual_remaining != expected_remaining:
                raise ValueError(
                    f"Encounter count mismatch during resume: original={original_count}, "
                    f"cursor={cursor}, expected_remaining={expected_remaining}, "
                    f"actual_remaining={actual_remaining}. "
                    f"Encounter objects must not be reconstructed or modified."
                )
        
        # THE ONLY ALLOWED ADVANCEMENT LOGIC: pop from list
        # Absolutely forbid: recomputing index, constructing encounter_id, building new objects
        next_encounter = remaining_encounters.pop(0)  # Use pop(0) to modify list in place
        
        # Increment cursor exactly once per pop
        self._pending_travel["encounter_cursor"] = cursor + 1
        
        # Get allowed actions for this encounter (read-only operation)
        from interaction_layer import allowed_actions_initial
        allowed = allowed_actions_initial(next_encounter)
        allowed = sorted(allowed)  # Deterministic ordering
        
        # Build options list for CLI (read-only operation)
        options = []
        for action_id in allowed:
            label_map = {
                ACTION_IGNORE: "Ignore",
                ACTION_RESPOND: "Respond",
                ACTION_HAIL: "Hail",
                ACTION_ATTACK: "Attack",
            }
            label = label_map.get(action_id, action_id.replace("_", " ").title())
            options.append({"id": action_id, "label": label})
        
        # Update pending_travel with next encounter (list already modified by pop)
        self._pending_travel["current_encounter"] = next_encounter
        self._pending_travel["remaining_encounters"] = remaining_encounters  # Already updated by pop
        self._pending_travel["encounter_context"] = {
            "encounter_id": str(next_encounter.encounter_id),  # Read existing ID, never construct
            "options": options,
        }
        
        # Set hard_stop to require player input for next encounter
        context.hard_stop = True
        context.hard_stop_reason = "pending_encounter_decision"
        
        return True

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
        elif handler == HANDLER_COMBAT or handler == HANDLER_COMBAT_STUB:
            # For interactive combat (HANDLER_COMBAT), initialize session and return hard_stop
            # For simulation (HANDLER_COMBAT_STUB), use one-shot resolution
            if handler == HANDLER_COMBAT:
                # Initialize interactive combat session
                self._initialize_combat_session(spec, context)
                # Set hard_stop to pause for player combat action
                context.hard_stop = True
                context.hard_stop_reason = "pending_combat_action"
                resolver_outcome = {
                    "resolver": "combat",
                    "status": "combat_started",
                }
            else:
                # Legacy one-shot combat for simulation
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
        
        # Skip combat rewards here - they are handled by _apply_post_combat_rewards_and_salvage
        # to allow for loot prompts and capacity checks
        resolver = str(resolver_outcome.get("resolver", "none"))
        if resolver == "combat":
            self._event(
                context,
                stage="conditional_rewards",
                subsystem="reward_gate",
                detail={
                    "encounter_id": str(spec.encounter_id),
                    "skipped": True,
                    "reason": "combat_rewards_handled_by_post_combat",
                },
            )
            return

        reward_payload = materialize_reward(
            spec,
            self._system_market_payloads(self.sector.get_system(self.player_state.current_system_id)),
            str(self.world_seed),
        )
        # For non-combat rewards, apply immediately (no capacity enforcement for now to preserve existing behavior)
        applied = apply_materialized_reward(
            player=self.player_state,
            reward_payload=reward_payload,
            context="game_engine",
            catalog=self.catalog if hasattr(self, "catalog") else None,
            enforce_capacity=False,  # Non-combat rewards don't enforce capacity (preserve existing behavior)
            stolen_applied=getattr(reward_payload, "stolen_applied", False) if reward_payload else False,
        )
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
            player_ship_state=player_ship_state,
            enemy_ship_state=enemy_ship,
            max_rounds=int(self.config.get("combat_max_rounds", 3)),
            system_id=self.player_state.current_system_id,
        )
        final_player = getattr(combat, "final_state_player", None)
        if isinstance(final_player, dict):
            player_ship.persistent_state["degradation_state"] = dict(
                final_player.get("degradation", {"weapon": 0, "defense": 0, "engine": 0})
            )
            if isinstance(final_player.get("current_hull"), int):
                player_ship.persistent_state["current_hull_integrity"] = int(final_player["current_hull"])
        return combat

    def _initialize_combat_session(self, spec: Any, context: EngineContext) -> None:
        """
        Initialize an interactive combat session.
        
        Per combat_resolution_contract.md Section 3: "CORE ACTIONS"
        Always available: Focus Fire, Reinforce Shields, Evasive Maneuvers, Attempt Escape, Surrender
        
        This method sets up the pending combat state but does NOT process any rounds.
        Combat will be processed round-by-round via _process_combat_round().
        """
        from combat_resolver import (
            _create_initial_state_from_ship_state,
            assemble_ship,
            _module_is_repair,
            map_rcp_to_tr,
        )
        from npc_ship_generator import generate_npc_ship
        
        system = self.sector.get_system(self.player_state.current_system_id)
        if system is None:
            raise ValueError("Current system not found for combat initialization.")
        
        encounter_id = str(spec.encounter_id)
        combat_id = f"CMB-{encounter_id}"
        
        # Generate NPC ship (deterministic)
        enemy_ship_dict = generate_npc_ship(
            world_seed=self.world_seed,
            system_id=self.player_state.current_system_id,
            system_population=int(system.population),
            encounter_id=encounter_id,
            encounter_subtype=str(spec.subtype_id),
        )
        
        # Get player ship
        player_ship_entity = self._active_ship()
        player_ship_state = {
            "hull_id": player_ship_entity.model_id,
            "module_instances": list(player_ship_entity.persistent_state.get("module_instances", [])),
            "degradation_state": dict(
                player_ship_entity.persistent_state.get("degradation_state", {"weapon": 0, "defense": 0, "engine": 0})
            ),
            "current_hull_integrity": int(player_ship_entity.persistent_state.get("current_hull_integrity", 0) or 0),
        }
        
        # Validate player ship_state has hull_id
        if not player_ship_state.get("hull_id"):
            raise ValueError(f"invalid_player_ship_state: hull_id missing for encounter_id={encounter_id}")
        
        # Validate enemy ship_dict has hull_id
        if not enemy_ship_dict.get("hull_id"):
            raise ValueError(f"invalid_enemy_ship_state: hull_id missing for encounter_id={encounter_id}")
        
        # Initialize combat states (will raise if hull_id invalid via assemble_ship)
        try:
            player_state = _create_initial_state_from_ship_state(player_ship_state)
            enemy_state = _create_initial_state_from_ship_state(enemy_ship_dict)
        except ValueError as e:
            raise ValueError(f"combat_initialization_failed: encounter_id={encounter_id}, player_hull_id={player_ship_state.get('hull_id')}, enemy_hull_id={enemy_ship_dict.get('hull_id')}, error={str(e)}") from e
        
        # Validate hull_max > 0
        if player_state.hull_max <= 0:
            raise ValueError(f"invalid_player_hull_max: encounter_id={encounter_id}, hull_id={player_ship_state.get('hull_id')}, hull_max={player_state.hull_max}")
        if enemy_state.hull_max <= 0:
            raise ValueError(f"invalid_enemy_hull_max: encounter_id={encounter_id}, hull_id={enemy_ship_dict.get('hull_id')}, hull_max={enemy_state.hull_max}")
        
        player_state.degradation.update(player_ship_state.get("degradation_state", {}))
        enemy_state.degradation.update(enemy_ship_dict.get("degradation_state", {}))
        
        # Set initial hull from persistent state (default to full hull if unset)
        player_hull_integrity = player_ship_state.get("current_hull_integrity", 0) or 0
        if player_hull_integrity <= 0:
            # Unset or invalid: default to full hull
            player_state.hull_current = player_state.hull_max
            # Also update persistent state to keep it aligned
            player_ship_entity.persistent_state["current_hull_integrity"] = player_state.hull_max
            player_ship_entity.persistent_state["max_hull_integrity"] = player_state.hull_max
        else:
            player_state.hull_current = min(player_hull_integrity, player_state.hull_max)
        
        # Calculate TR/RCP
        assembled_player = assemble_ship(player_ship_state["hull_id"], player_ship_state["module_instances"], {"weapon": 0, "defense": 0, "engine": 0})
        rcp_player = (
            assembled_player["bands"]["pre_degradation"]["weapon"]
            + assembled_player["bands"]["pre_degradation"]["defense"]
            + (assembled_player["bands"]["pre_degradation"]["engine"] // 2)
            + (int(assembled_player["hull_max"]) // 4)
            + (2 * sum(1 for entry in player_ship_state["module_instances"] if _module_is_repair(entry)))
        )
        tr_player = map_rcp_to_tr(rcp_player)
        
        assembled_enemy = assemble_ship(enemy_ship_dict["hull_id"], enemy_ship_dict["module_instances"], {"weapon": 0, "defense": 0, "engine": 0})
        rcp_enemy = (
            assembled_enemy["bands"]["pre_degradation"]["weapon"]
            + assembled_enemy["bands"]["pre_degradation"]["defense"]
            + (assembled_enemy["bands"]["pre_degradation"]["engine"] // 2)
            + (int(assembled_enemy["hull_max"]) // 4)
            + (2 * sum(1 for entry in enemy_ship_dict["module_instances"] if _module_is_repair(entry)))
        )
        tr_enemy = map_rcp_to_tr(rcp_enemy)
        
        # Generate combat RNG seed (non-deterministic per combat)
        import secrets
        combat_rng_seed = secrets.randbits(64)
        
        # Store pending combat state
        self._pending_combat = {
            "combat_id": combat_id,
            "encounter_id": encounter_id,
            "spec": spec,
            "player_ship_entity": player_ship_entity,
            "enemy_ship_dict": enemy_ship_dict,
            "player_ship_state": player_ship_state,
            "round_number": 0,  # 0 = not started, will be 1+ when first round processes
            "player_state": player_state,
            "enemy_state": enemy_state,
            "tr_player": tr_player,
            "tr_enemy": tr_enemy,
            "rcp_player": rcp_player,
            "rcp_enemy": rcp_enemy,
            "log": [],
            "context": context,
            "max_rounds": int(self.config.get("combat_max_rounds", 20)),
            "combat_rng_seed": combat_rng_seed,
        }
        
        # Log combat started with hull info
        self._event(
            context,
            stage="combat",
            subsystem="combat_initialization",
            detail={
                "encounter_id": encounter_id,
                "combat_id": combat_id,
                "system_id": self.player_state.current_system_id,
                "player_hull_id": player_ship_state["hull_id"],
                "enemy_hull_id": enemy_ship_dict["hull_id"],
                "player_hull_max": player_state.hull_max,
                "enemy_hull_max": enemy_state.hull_max,
            },
        )

    def _process_combat_round(self, player_action: str) -> dict[str, Any]:
        """
        Process one round of interactive combat.
        
        Per combat_resolution_contract.md:
        - Each round: player selects action, enemy selects action (deterministic),
          bands calculated, resolution executes, damage applied, termination checked.
        
        Returns dict with:
        - "combat_ended": bool
        - "combat_result": CombatResult | None (only if combat_ended)
        - "round_number": int
        - "player_hull_pct": int
        - "enemy_hull_pct": int
        """
        if self._pending_combat is None:
            raise ValueError("No pending combat session.")
        
        from combat_resolver import (
            CombatRng,
            CombatResult,
            available_actions,
            _crew_modifiers_for_ship_state,
            assemble_ship,
            _primary_weapon_type,
            _primary_defense_type,
            RPS_MATRIX,
            _effective_from_assembled,
            _resolve_attack,
            _apply_damage_and_degradation,
            _escape_attempt,
            _repair_once,
            _ship_state_to_dict,
            resolve_salvage_modules,
            hull_percent,
            _module_is_repair,
            _modules_by_id,
        )
        from combat_resolver import _default_selector
        
        pending = self._pending_combat
        round_number = pending["round_number"] + 1
        pending["round_number"] = round_number
        
        player_state = pending["player_state"]
        enemy_state = pending["enemy_state"]
        player_ship_state = pending["player_ship_state"]
        enemy_ship_dict = pending["enemy_ship_dict"]
        combat_id = pending["combat_id"]
        max_rounds = pending["max_rounds"]
        
        rng = CombatRng(world_seed=str(self.world_seed), salt=f"{combat_id}_combat")
        
        # Get allowed actions
        player_allowed = available_actions(player_ship_state, player_state)
        enemy_allowed = available_actions(enemy_ship_dict, enemy_state)
        
        # Validate player action
        if player_action not in player_allowed:
            player_action = "Focus Fire"  # Default fallback
        
        # Get enemy action (deterministic)
        enemy_selector = _default_selector
        enemy_action = enemy_selector(round_number, enemy_state, player_state, enemy_ship_dict, player_ship_state, enemy_allowed)
        if enemy_action not in enemy_allowed:
            enemy_action = "Focus Fire"
        
        # Check surrender (immediate termination)
        if player_action == "Surrender":
            pending["log"].append({"round": round_number, "outcome": "surrender", "surrendered_by": "player"})
            combat_result = CombatResult(
                outcome="surrender",
                rounds=round_number,
                winner="enemy",
                final_state_player=_ship_state_to_dict(player_ship_state, player_state),
                final_state_enemy=_ship_state_to_dict(enemy_ship_dict, enemy_state),
                log=pending["log"],
                tr_player=pending["tr_player"],
                tr_enemy=pending["tr_enemy"],
                rcp_player=pending["rcp_player"],
                rcp_enemy=pending["rcp_enemy"],
                surrendered_by="player",
                salvage_modules=[],
            )
            return {
                "combat_ended": True,
                "combat_result": combat_result,
                "round_number": round_number,
                "player_hull_pct": hull_percent(player_state.hull_current, player_state.hull_max),
                "enemy_hull_pct": hull_percent(enemy_state.hull_current, enemy_state.hull_max),
            }
        
        if enemy_action == "Surrender":
            pending["log"].append({"round": round_number, "outcome": "surrender", "surrendered_by": "enemy"})
            combat_result = CombatResult(
                outcome="surrender",
                rounds=round_number,
                winner="player",
                final_state_player=_ship_state_to_dict(player_ship_state, player_state),
                final_state_enemy=_ship_state_to_dict(enemy_ship_dict, enemy_state),
                log=pending["log"],
                tr_player=pending["tr_player"],
                tr_enemy=pending["tr_enemy"],
                rcp_player=pending["rcp_player"],
                rcp_enemy=pending["rcp_enemy"],
                surrendered_by="enemy",
                salvage_modules=[],
            )
            return {
                "combat_ended": True,
                "combat_result": combat_result,
                "round_number": round_number,
                "player_hull_pct": hull_percent(player_state.hull_current, player_state.hull_max),
                "enemy_hull_pct": hull_percent(enemy_state.hull_current, enemy_state.hull_max),
            }
        
        # Handle repair actions
        player_crew_mods = _crew_modifiers_for_ship_state(player_ship_state)
        enemy_crew_mods = _crew_modifiers_for_ship_state(enemy_ship_dict)
        
        if player_action == "Repair Systems":
            _repair_once(player_ship_state, player_state, action_repair_bonus=int(player_crew_mods.repair_focus_bonus))
        if enemy_action == "Repair Systems":
            _repair_once(enemy_ship_dict, enemy_state, action_repair_bonus=int(enemy_crew_mods.repair_focus_bonus))
        
        # Handle scan actions
        module_defs = _modules_by_id()
        if player_action == "Scan" and any(module_defs[entry["module_id"]]["primary_tag"] == "ship:utility_probe_array" for entry in player_ship_state["module_instances"]):
            scan_roll = rng.randint(0, 1, "scan_roll_player", round_number, [])
            if scan_roll == 1:
                enemy_state.scanned = True
        
        if enemy_action == "Scan" and any(module_defs[entry["module_id"]]["primary_tag"] == "ship:utility_probe_array" for entry in enemy_ship_dict["module_instances"]):
            scan_roll = rng.randint(0, 1, "scan_roll_enemy", round_number, [])
            if scan_roll == 1:
                player_state.scanned = True
        
        # Assemble ships with current degradation
        assembled_player = assemble_ship(player_ship_state["hull_id"], player_ship_state["module_instances"], player_state.degradation)
        assembled_enemy = assemble_ship(enemy_ship_dict["hull_id"], enemy_ship_dict["module_instances"], enemy_state.degradation)
        
        # Calculate RPS adjustments
        player_rps = 0
        enemy_rps = 0
        own_weapon = _primary_weapon_type(player_ship_state)
        opp_def = _primary_defense_type(enemy_ship_dict)
        if own_weapon is not None and opp_def is not None:
            player_rps = RPS_MATRIX.get((own_weapon, opp_def), 0)
        own_weapon_e = _primary_weapon_type(enemy_ship_dict)
        opp_def_p = _primary_defense_type(player_ship_state)
        if own_weapon_e is not None and opp_def_p is not None:
            enemy_rps = RPS_MATRIX.get((own_weapon_e, opp_def_p), 0)
        
        # Calculate effective bands
        player_weapon = _effective_from_assembled(
            assembled_player,
            player_action,
            "weapon",
            player_rps,
            crew_band_bonus=int(player_crew_mods.attack_band_bonus),
            action_bonus=int(player_crew_mods.focus_fire_bonus if player_action == "Focus Fire" else 0),
        )
        player_defense = _effective_from_assembled(
            assembled_player,
            player_action,
            "defense",
            crew_band_bonus=int(player_crew_mods.defense_band_bonus),
            action_bonus=int(player_crew_mods.reinforce_shields_bonus if player_action == "Reinforce Shields" else 0),
        )
        player_engine = _effective_from_assembled(
            assembled_player,
            player_action,
            "engine",
            crew_band_bonus=int(player_crew_mods.engine_band_bonus),
            action_bonus=int(player_crew_mods.evasive_bonus if player_action == "Evasive Maneuvers" else 0),
        )
        enemy_weapon = _effective_from_assembled(
            assembled_enemy,
            enemy_action,
            "weapon",
            enemy_rps,
            crew_band_bonus=int(enemy_crew_mods.attack_band_bonus),
            action_bonus=int(enemy_crew_mods.focus_fire_bonus if enemy_action == "Focus Fire" else 0),
        )
        enemy_defense = _effective_from_assembled(
            assembled_enemy,
            enemy_action,
            "defense",
            crew_band_bonus=int(enemy_crew_mods.defense_band_bonus),
            action_bonus=int(enemy_crew_mods.reinforce_shields_bonus if enemy_action == "Reinforce Shields" else 0),
        )
        enemy_engine = _effective_from_assembled(
            assembled_enemy,
            enemy_action,
            "engine",
            crew_band_bonus=int(enemy_crew_mods.engine_band_bonus),
            action_bonus=int(enemy_crew_mods.evasive_bonus if enemy_action == "Evasive Maneuvers" else 0),
        )
        
        # Handle escape attempt
        if player_action == "Attempt Escape":
            escape = _escape_attempt(
                world_seed=str(self.world_seed),
                combat_id=combat_id,
                round_number=round_number,
                fleeing_ship_state=player_ship_state,
                pursuing_ship_state=enemy_ship_dict,
                fleeing_engine_effective=player_engine,
                pursuing_engine_effective=enemy_engine,
                fleeing_combat_state=player_state,
                pursuing_combat_state=enemy_state,
            )
            if escape["escaped"]:
                pending["log"].append({"round": round_number, "outcome": "escape", "escaped_by": "player"})
                combat_result = CombatResult(
                    outcome="escape",
                    rounds=round_number,
                    winner="player",
                    final_state_player=_ship_state_to_dict(player_ship_state, player_state),
                    final_state_enemy=_ship_state_to_dict(enemy_ship_dict, enemy_state),
                    log=pending["log"],
                    tr_player=pending["tr_player"],
                    tr_enemy=pending["tr_enemy"],
                    rcp_player=pending["rcp_player"],
                    rcp_enemy=pending["rcp_enemy"],
                    salvage_modules=[],
                )
                return {
                    "combat_ended": True,
                    "combat_result": combat_result,
                    "round_number": round_number,
                    "player_hull_pct": hull_percent(player_state.hull_current, player_state.hull_max),
                    "enemy_hull_pct": hull_percent(enemy_state.hull_current, enemy_state.hull_max),
                }
        
        if enemy_action == "Attempt Escape":
            escape = _escape_attempt(
                world_seed=str(self.world_seed),
                combat_id=f"{combat_id}_enemy",
                round_number=round_number,
                fleeing_ship_state=enemy_ship_dict,
                pursuing_ship_state=player_ship_state,
                fleeing_engine_effective=enemy_engine,
                pursuing_engine_effective=player_engine,
                fleeing_combat_state=enemy_state,
                pursuing_combat_state=player_state,
            )
            if escape["escaped"]:
                pending["log"].append({"round": round_number, "outcome": "escape", "escaped_by": "enemy"})
                combat_result = CombatResult(
                    outcome="escape",
                    rounds=round_number,
                    winner="enemy",
                    final_state_player=_ship_state_to_dict(player_ship_state, player_state),
                    final_state_enemy=_ship_state_to_dict(enemy_ship_dict, enemy_state),
                    log=pending["log"],
                    tr_player=pending["tr_player"],
                    tr_enemy=pending["tr_enemy"],
                    rcp_player=pending["rcp_player"],
                    rcp_enemy=pending["rcp_enemy"],
                    salvage_modules=[],
                )
                return {
                    "combat_ended": True,
                    "combat_result": combat_result,
                    "round_number": round_number,
                    "player_hull_pct": hull_percent(player_state.hull_current, player_state.hull_max),
                    "enemy_hull_pct": hull_percent(enemy_state.hull_current, enemy_state.hull_max),
                }
        
        # Resolve attacks
        rng_events = []
        player_attack = _resolve_attack("player", "enemy", player_weapon, enemy_defense, enemy_action, rng, round_number, rng_events)
        enemy_attack = _resolve_attack("enemy", "player", enemy_weapon, player_defense, player_action, rng, round_number, rng_events)
        
        # Apply damage and degradation
        player_degrade = _apply_damage_and_degradation(player_state, enemy_attack["damage"], rng, round_number, rng_events, target_ship_state=player_ship_state)
        enemy_degrade = _apply_damage_and_degradation(enemy_state, player_attack["damage"], rng, round_number, rng_events, target_ship_state=enemy_ship_dict)
        
        # Check destruction
        player_destroyed = player_state.hull_current <= 0
        enemy_destroyed = enemy_state.hull_current <= 0
        
        if player_destroyed or enemy_destroyed:
            if player_destroyed and enemy_destroyed:
                winner: Literal["player", "enemy", "none"] = "none"
            elif enemy_destroyed:
                winner = "player"
            else:
                winner = "enemy"
            
            destruction = {
                "player_destroyed": player_destroyed,
                "enemy_destroyed": enemy_destroyed,
                "requires_external_insurance_resolution": player_destroyed,
            }
            
            salvage_modules: list[dict[str, Any]] = []
            if enemy_destroyed:
                salvage_modules.extend(
                    resolve_salvage_modules(
                        world_seed=str(self.world_seed),
                        system_id=self.player_state.current_system_id,
                        encounter_id=f"{combat_id}_enemy_destroyed",
                        destroyed_ship=enemy_ship_dict,
                    )
                )
            
            pending["log"].append({"round": round_number, "outcome": "destroyed", "winner": winner})
            combat_result = CombatResult(
                outcome="destroyed",
                rounds=round_number,
                winner=winner,
                final_state_player=_ship_state_to_dict(player_ship_state, player_state),
                final_state_enemy=_ship_state_to_dict(enemy_ship_dict, enemy_state),
                log=pending["log"],
                tr_player=pending["tr_player"],
                tr_enemy=pending["tr_enemy"],
                rcp_player=pending["rcp_player"],
                rcp_enemy=pending["rcp_enemy"],
                destruction_event=destruction,
                salvage_modules=salvage_modules,
            )
            return {
                "combat_ended": True,
                "combat_result": combat_result,
                "round_number": round_number,
                "player_hull_pct": hull_percent(player_state.hull_current, player_state.hull_max),
                "enemy_hull_pct": hull_percent(enemy_state.hull_current, enemy_state.hull_max),
            }
        
        # Check max rounds
        if round_number >= max_rounds:
            pending["log"].append({"round": round_number, "outcome": "max_rounds"})
            combat_result = CombatResult(
                outcome="max_rounds",
                rounds=round_number,
                winner="none",
                final_state_player=_ship_state_to_dict(player_ship_state, player_state),
                final_state_enemy=_ship_state_to_dict(enemy_ship_dict, enemy_state),
                log=pending["log"],
                tr_player=pending["tr_player"],
                tr_enemy=pending["tr_enemy"],
                rcp_player=pending["rcp_player"],
                rcp_enemy=pending["rcp_enemy"],
                salvage_modules=[],
            )
            return {
                "combat_ended": True,
                "combat_result": combat_result,
                "round_number": round_number,
                "player_hull_pct": hull_percent(player_state.hull_current, player_state.hull_max),
                "enemy_hull_pct": hull_percent(enemy_state.hull_current, enemy_state.hull_max),
            }
        
        # Combat continues
        pending["log"].append({"round": round_number, "actions": {"player": player_action, "enemy": enemy_action}})
        return {
            "combat_ended": False,
            "combat_result": None,
            "round_number": round_number,
            "player_hull_pct": hull_percent(player_state.hull_current, player_state.hull_max),
            "enemy_hull_pct": hull_percent(enemy_state.hull_current, enemy_state.hull_max),
        }

    def _handle_player_ship_destruction(self, combat_id: str) -> dict[str, Any]:
        """
        Handle player ship destruction with insurance logic.
        
        Returns a result dict with hard_stop, hard_stop_reason, and game_over flags.
        """
        import random
        
        # Clear pending combat immediately
        self._pending_combat = None
        
        # Check insurance
        if self.player_state.has_ship_insurance:
            roll = random.random()
            if roll < 0.5:
                # Insurance save - ship destroyed but run continues
                self.player_state.ship_destroyed = True
                self.player_state.ship_insurance_consumed = True
                self.player_state.has_ship_insurance = False
                
                return {
                    "hard_stop": True,
                    "hard_stop_reason": "ship_destroyed_insured",
                    "game_over": False,
                    "error": None,
                    "game_over_reason": None,
                }
            else:
                # Insurance failed
                self.player_state.run_ended = True
                self.player_state.run_end_reason = "ship_destroyed"
                
                return {
                    "hard_stop": True,
                    "hard_stop_reason": "game_over",
                    "game_over": True,
                    "error": "game_over",
                    "game_over_reason": "ship_destroyed",
                }
        else:
            # No insurance - Game Over
            self.player_state.run_ended = True
            self.player_state.run_end_reason = "ship_destroyed"
            
            return {
                "hard_stop": True,
                "hard_stop_reason": "game_over",
                "game_over": True,
                "error": "game_over",
                "game_over_reason": "ship_destroyed",
            }
    
    def _execute_combat_action(self, context: EngineContext, payload: dict[str, Any]) -> None:
        """
        Execute player combat action for one round.
        
        Command format:
        {
            "type": "combat_action",
            "action": "Focus Fire" | "Reinforce Shields" | "Evasive Maneuvers" | "Attempt Escape" | "Surrender",
            "encounter_id": str (optional, for validation)
        }
        
        Per combat_resolution_contract.md Section 3: "CORE ACTIONS"
        Always available: Focus Fire, Reinforce Shields, Evasive Maneuvers, Attempt Escape, Surrender
        """
        if self._pending_combat is None:
            raise ValueError("No pending combat session.")
        
        # Validate encounter_id if provided
        encounter_id = payload.get("encounter_id")
        if encounter_id and str(encounter_id) != self._pending_combat["encounter_id"]:
            raise ValueError(f"Encounter ID mismatch: expected {self._pending_combat['encounter_id']}, got {encounter_id}")
        
        # Get action (map from action_id to contract name if needed)
        action_id = payload.get("action")
        if not isinstance(action_id, str):
            raise ValueError("combat_action requires 'action' (string).")
        
        # Map lower_snake_case to contract names if needed
        action_map = {
            "focus_fire": "Focus Fire",
            "reinforce_shields": "Reinforce Shields",
            "evasive_maneuvers": "Evasive Maneuvers",
            "attempt_escape": "Attempt Escape",
            "surrender": "Surrender",
        }
        player_action = action_map.get(action_id, action_id)  # Use as-is if already contract name
        
        # Load current pending combat session
        pending = self._pending_combat
        combat_rng_seed = pending["combat_rng_seed"]
        round_number = pending["round_number"] + 1  # Next round to execute
        player_state = pending["player_state"]
        enemy_state = pending["enemy_state"]
        player_ship_state = pending["player_ship_state"]
        enemy_ship_dict = pending["enemy_ship_dict"]
        max_rounds = pending["max_rounds"]
        
        # Store initial state for progress validation
        initial_player_hull = player_state.hull_current
        initial_enemy_hull = enemy_state.hull_current
        initial_round = round_number
        
        # Determine enemy action (simple deterministic AI for now)
        enemy_action: str = "Focus Fire"
        
        # Execute one round using resolve_combat_round
        from combat_resolver import resolve_combat_round, available_actions, CombatResult, _ship_state_to_dict, hull_percent
        
        # Validate player action is allowed
        player_allowed = available_actions(player_ship_state, player_state)
        if player_action not in player_allowed:
            player_action = "Focus Fire"  # Default fallback
        
        # Check max rounds before executing (if at max, force termination)
        if round_number > max_rounds:
            # Already exceeded max rounds - force termination
            from combat_resolver import CombatResult, _ship_state_to_dict
            combat_result = CombatResult(
                outcome="max_rounds",
                rounds=round_number - 1,  # Last completed round
                winner="none",
                final_state_player=_ship_state_to_dict(player_ship_state, player_state),
                final_state_enemy=_ship_state_to_dict(enemy_ship_dict, enemy_state),
                log=pending["log"],
                tr_player=pending["tr_player"],
                tr_enemy=pending["tr_enemy"],
                rcp_player=pending["rcp_player"],
                rcp_enemy=pending["rcp_enemy"],
                salvage_modules=[],
                combat_rng_seed=combat_rng_seed,
            )
            
            # Apply combat results
            from combat_application import apply_combat_result
            from time_engine import get_current_turn
            
            apply_combat_result(
                player_state=self.player_state,
                player_ship_entity=pending["player_ship_entity"],
                enemy_ship_entity_or_dict=enemy_ship_dict,
                combat_result=combat_result,
                system_id=self.player_state.current_system_id,
                encounter_id=pending["encounter_id"],
                world_seed=self.world_seed,
                logger=self._silent_logger,
                turn=int(get_current_turn()),
            )
            
            # Clear pending combat
            self._pending_combat = None
            context.hard_stop = False
            return
        
        # Execute the round
        round_result = resolve_combat_round(
            combat_rng_seed=combat_rng_seed,
            round_number=round_number,
            player_state=player_state,
            enemy_state=enemy_state,
            player_action=player_action,
            enemy_action=enemy_action,
            player_ship_state=player_ship_state,
            enemy_ship_state=enemy_ship_dict,
            system_id=self.player_state.current_system_id,
        )
        
        # Update pending combat state
        pending["round_number"] = round_number
        pending["player_state"] = round_result["player_state"]
        pending["enemy_state"] = round_result["enemy_state"]
        pending["log"].append(round_result["round_summary"])
        
        # Check max rounds after execution
        if round_number >= max_rounds and not round_result["combat_ended"]:
            # Force termination at max rounds
            from combat_resolver import CombatResult, _ship_state_to_dict
            combat_result = CombatResult(
                outcome="max_rounds",
                rounds=round_number,
                winner="none",
                final_state_player=_ship_state_to_dict(player_ship_state, player_state),
                final_state_enemy=_ship_state_to_dict(enemy_ship_dict, enemy_state),
                log=pending["log"],
                tr_player=pending["tr_player"],
                tr_enemy=pending["tr_enemy"],
                rcp_player=pending["rcp_player"],
                rcp_enemy=pending["rcp_enemy"],
                salvage_modules=[],
                combat_rng_seed=combat_rng_seed,
            )
            round_result["combat_ended"] = True
            round_result["outcome"] = "max_rounds"
        
        if round_result["combat_ended"]:
            # Combat ended - build CombatResult and apply
            outcome = round_result["outcome"]
            round_summary = round_result["round_summary"]
            
            # Determine winner based on outcome
            winner: Literal["player", "enemy", "none"] = "none"
            surrendered_by: Optional[str] = None
            
            if outcome == "surrender":
                surrendered_by = round_summary.get("surrendered_by", "player")
                winner = "enemy" if surrendered_by == "player" else "player"
            elif outcome == "escape":
                escaped_by = round_summary.get("escaped_by", "player")
                winner = "player" if escaped_by == "player" else "enemy"
            elif outcome == "destroyed":
                winner = round_summary.get("winner", "none")
            
            # Handle player ship destruction immediately
            # Check if player was destroyed (winner == "enemy" or player hull <= 0)
            if outcome == "destroyed" and (winner == "enemy" or player_state.hull_current <= 0):
                destruction_result = self._handle_player_ship_destruction(pending["combat_id"])
                
                # If game over, set context and return early
                if destruction_result.get("game_over"):
                    context.hard_stop = True
                    context.hard_stop_reason = destruction_result.get("hard_stop_reason", "game_over")
                    # Store game over info in context for result building
                    context.game_over_reason = destruction_result.get("game_over_reason", "ship_destroyed")
                    return
            
            from combat_resolver import resolve_salvage_modules
            salvage_modules: list[dict[str, Any]] = []
            if outcome == "destroyed" and winner == "player":
                salvage_modules.extend(
                    resolve_salvage_modules(
                        world_seed=str(self.world_seed),
                        system_id=self.player_state.current_system_id,
                        encounter_id=f"{pending['combat_id']}_enemy_destroyed",
                        destroyed_ship=enemy_ship_dict,
                    )
                )
            
            combat_result = CombatResult(
                outcome=outcome,
                rounds=round_number,
                winner=winner,
                final_state_player=_ship_state_to_dict(player_ship_state, player_state),
                final_state_enemy=_ship_state_to_dict(enemy_ship_dict, enemy_state),
                log=pending["log"],
                tr_player=pending["tr_player"],
                tr_enemy=pending["tr_enemy"],
                rcp_player=pending["rcp_player"],
                rcp_enemy=pending["rcp_enemy"],
                salvage_modules=salvage_modules,
                surrendered_by=surrendered_by,
                combat_rng_seed=combat_rng_seed,
            )
            
            # Apply combat results (hull/degradation/state only; no rewards here)
            from combat_application import apply_combat_result
            from time_engine import get_current_turn

            apply_combat_result(
                player_state=self.player_state,
                player_ship_entity=pending["player_ship_entity"],
                enemy_ship_entity_or_dict=enemy_ship_dict,
                combat_result=combat_result,
                system_id=self.player_state.current_system_id,
                encounter_id=pending["encounter_id"],
                world_seed=self.world_seed,
                logger=self._silent_logger,
                turn=int(get_current_turn()),
            )

            # Decide whether post-combat rewards handler should run (engine layer only)
            apply_rewards = False
            if combat_result.outcome in {"destroyed", "surrender", "escape"}:
                # Player victory or successful escape by player can qualify
                if combat_result.outcome == "destroyed" and combat_result.winner == "player":
                    apply_rewards = True
                elif combat_result.outcome == "surrender":
                    # Only apply if enemy surrendered (player did not surrender)
                    surrendered_by = getattr(combat_result, "surrendered_by", None)
                    if surrendered_by == "enemy":
                        apply_rewards = True
                elif combat_result.outcome == "escape":
                    # Treat player escape as escape_success; enemy escape should not trigger rewards
                    escaped_by = round_summary.get("escaped_by")
                    if escaped_by == "player":
                        apply_rewards = True

            # Log combat action result BEFORE invoking reward handler
            # This ensures layering: combat_action log precedes reward_handler:post_combat
            self._event(
                context,
                stage="combat",
                subsystem="combat_action",
                detail={
                    "action": "resolved",
                    "combat_id": pending["combat_id"],
                    "round_executed": round_number,
                    "player_action": player_action,
                    "enemy_action": enemy_action,
                    "player_hull_current": player_state.hull_current,
                    "enemy_hull_current": enemy_state.hull_current,
                        "outcome": outcome,
                },
            )

            # Invoke post-combat reward handler ONLY after terminal state is logged
            if apply_rewards:
                self._apply_post_combat_rewards_and_salvage(
                    context=context,
                    combat_result=combat_result,
                    encounter_id=pending["encounter_id"],
                )
                
                # Evaluate active missions after combat (all mission types through centralized authority)
                # Delivery missions are evaluated on travel arrival, not after combat
                # Bounty missions can be evaluated here if needed, but all evaluation goes through evaluate_active_missions()
                evaluate_active_missions(
                    mission_manager=self._mission_manager,
                    player_state=self.player_state,
                    current_system_id=self.player_state.current_system_id,
                    current_destination_id=self.player_state.current_destination_id,
                    event_context={"event": "combat_complete"},
                    logger=self._logger if self._logging_enabled else None,
                    turn=context.turn_after,
                )

            # Clear pending combat after rewards/loot have been prepared
            self._pending_combat = None

            # If loot handler did not set a loot decision hard_stop, resume travel encounters
            if context.hard_stop_reason != "pending_loot_decision":
                # No loot pending - check if we should resume travel encounters
                # This will set hard_stop=True with pending_encounter_decision if encounters remain
                # or hard_stop=False if no encounters remain
                self._resume_travel_encounters_if_any(context)
        else:
            # Combat continues - set hard_stop for next round
            context.hard_stop = True
            context.hard_stop_reason = "pending_combat_action"
            
            # Log combat action resolved
            self._event(
                context,
                stage="combat",
                subsystem="combat_action",
                detail={
                    "action": "resolved",
                    "combat_id": pending["combat_id"],
                    "round_executed": round_number,
                    "player_action": player_action,
                    "enemy_action": enemy_action,
                    "player_hull_current": player_state.hull_current,
                    "enemy_hull_current": enemy_state.hull_current,
                },
            )

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
            # Only grant rewards for actual wins (destroyed or enemy surrender), not escapes
            winner = str(resolver_outcome.get("winner", "none"))
            if winner != "player":
                return False
            # Check outcome: destroyed or surrender (but not player escape)
            if str(outcome) == "escape":
                return False  # Player escaped, no rewards
            if str(outcome) == "surrender":
                # Only grant if enemy surrendered
                surrendered_by = resolver_outcome.get("surrendered_by")
                return str(surrendered_by) == "enemy"
            # destroyed or max_rounds with player win
            return str(outcome) in {"destroyed", "max_rounds"}
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

    def _apply_post_combat_rewards_and_salvage(
        self,
        context: EngineContext,
        combat_result: Any,
        encounter_id: str,
    ) -> None:
        """
        Post-combat reward and salvage handler.
        
        This function:
        - Materializes rewards from encounter reward_profile_id
        - Combines rewards with salvage modules into a loot bundle
        - Stores the bundle in context for player prompt (deferred application)
        - Does NOT apply rewards immediately (player must accept via prompt)
        """
        # Defensive guard: only run for terminal combat outcomes
        outcome = getattr(combat_result, "outcome", None)
        if outcome not in {"destroyed", "surrender", "escape", "max_rounds"}:
            raise ValueError(f"post_combat_rewards_called_for_non_terminal_outcome:{outcome}")

        # Use encounter spec stored on pending combat (authoritative)
        if self._pending_combat is None:
            return

        spec = self._pending_combat.get("spec")
        if spec is None:
            return
        
        # Only materialize if encounter has a reward profile
        reward_profile_id = getattr(spec, "reward_profile_id", None)
        if reward_profile_id is None:
            # No reward profile, but salvage may still be available
            self._event(
                context,
                stage="post_combat",
                subsystem="reward_handler",
                detail={
                    "encounter_id": encounter_id,
                    "reward_profile_id": None,
                    "salvage_count": len(getattr(combat_result, "salvage_modules", [])),
                    "loot_bundle_created": False,
                },
            )
            return
        
        # Materialize reward (deterministic, uses existing seed strategy)
        from reward_materializer import materialize_reward
        
        system = self.sector.get_system(self.player_state.current_system_id)
        if system is None:
            return
        
        reward_payload = materialize_reward(
            spec,
            self._system_market_payloads(system),
            str(self.world_seed),
        )
        
        # Get salvage modules from combat result
        salvage_modules = list(getattr(combat_result, "salvage_modules", []))
        
        # Create loot bundle (deferred application - player must accept)
        loot_bundle = {
            "encounter_id": encounter_id,
            "reward_payload": reward_payload,
            "salvage_modules": salvage_modules,
            "credits": getattr(reward_payload, "credits", 0) if reward_payload else 0,
            "cargo": None,
            "cargo_quantity": 0,
            "cargo_sku": None,
            "stolen_applied": False,
        }
        
        if reward_payload:
            loot_bundle["cargo_sku"] = getattr(reward_payload, "sku_id", None)
            loot_bundle["cargo_quantity"] = getattr(reward_payload, "quantity", 0)
            loot_bundle["stolen_applied"] = getattr(reward_payload, "stolen_applied", False)
        
        # Store loot bundle in context for CLI prompt (deferred application)
        if not hasattr(context, "pending_loot"):
            context.pending_loot = None
        context.pending_loot = loot_bundle
        
        # Also store in engine state for CLI access
        self._pending_loot = loot_bundle
        
        # Set hard_stop to require loot decision
        context.hard_stop = True
        context.hard_stop_reason = "pending_loot_decision"
        
        self._event(
            context,
            stage="post_combat",
            subsystem="reward_handler",
            detail={
                "encounter_id": encounter_id,
                "reward_profile_id": str(reward_profile_id),
                "credits": loot_bundle["credits"],
                "cargo_sku": loot_bundle["cargo_sku"],
                "cargo_quantity": loot_bundle["cargo_quantity"],
                "salvage_count": len(salvage_modules),
                "stolen_applied": loot_bundle["stolen_applied"],
                "loot_bundle_created": True,
            },
        )

    def _apply_loot_bundle(
        self,
        context: EngineContext,
        loot_bundle: dict[str, Any],
        accepted_items: dict[str, bool],
    ) -> dict[str, Any]:
        """
        Apply accepted items from loot bundle to player state.
        
        Args:
            context: EngineContext
            loot_bundle: Loot bundle from _apply_post_combat_rewards_and_salvage
            accepted_items: Dict with keys "credits", "cargo", "salvage_modules" -> bool
        
        Returns:
            dict with application results and any errors
        """
        result = {
            "credits_applied": 0,
            "cargo_applied": None,
            "cargo_quantity": 0,
            "salvage_applied": 0,
            "errors": [],
        }
        
        if not loot_bundle:
            return result
        
        # Get ship capacities for enforcement
        try:
            ship = self._active_ship()
            physical_capacity = int(ship.get_effective_physical_capacity())
            data_capacity = int(ship.get_effective_data_capacity())
        except Exception:
            physical_capacity = None
            data_capacity = None
        
        # Apply credits if accepted
        if accepted_items.get("credits", False):
            credits = loot_bundle.get("credits", 0)
            if credits > 0:
                self.player_state.credits = max(0, int(self.player_state.credits) + int(credits))
                result["credits_applied"] = int(credits)
        
        # Apply cargo if accepted
        if accepted_items.get("cargo", False):
            reward_payload = loot_bundle.get("reward_payload")
            if reward_payload:
                sku_id = getattr(reward_payload, "sku_id", None)
                quantity = getattr(reward_payload, "quantity", 0)
                stolen = loot_bundle.get("stolen_applied", False)
                
                if sku_id and quantity > 0:
                    applied = apply_materialized_reward(
                        player=self.player_state,
                        reward_payload=reward_payload,
                        context="game_engine_post_combat",
                        catalog=self.catalog if hasattr(self, "catalog") else None,
                        physical_cargo_capacity=physical_capacity,
                        data_cargo_capacity=data_capacity,
                        enforce_capacity=True,
                        stolen_applied=stolen,
                    )
                    
                    if applied.get("error") == "cargo_capacity_exceeded":
                        result["errors"].append("cargo_capacity_exceeded")
                    else:
                        result["cargo_applied"] = applied.get("cargo")
                        result["cargo_quantity"] = applied.get("quantity", 0)
        
        # Apply salvage modules if accepted
        if accepted_items.get("salvage_modules", False):
            salvage_modules = loot_bundle.get("salvage_modules", [])
            if salvage_modules:
                # Each module consumes 1 physical cargo unit when stored as cargo
                # For now, store in salvage_modules list (player can install later via shipdock)
                # But we need to check capacity
                module_count = len(salvage_modules)
                
                if physical_capacity is not None and physical_capacity > 0:
                    # Calculate current physical cargo usage
                    from reward_applicator import _is_data_cargo
                    current_physical_usage = 0
                    holdings = self.player_state.cargo_by_ship.get("active", {})
                    for sku, qty in holdings.items():
                        try:
                            if not _is_data_cargo(sku, self.catalog if hasattr(self, "catalog") else None):
                                current_physical_usage += int(qty)
                        except Exception:
                            pass
                    
                    # Check if modules would fit
                    if current_physical_usage + module_count > physical_capacity:
                        result["errors"].append("salvage_capacity_exceeded")
                    else:
                        # Store modules in salvage_modules list
                        if not hasattr(self.player_state, "salvage_modules"):
                            self.player_state.salvage_modules = []
                        if not isinstance(self.player_state.salvage_modules, list):
                            self.player_state.salvage_modules = []
                        
                        import copy
                        for module in salvage_modules:
                            if isinstance(module, dict):
                                module_copy = copy.deepcopy(module)
                                self.player_state.salvage_modules.append(module_copy)
                                result["salvage_applied"] += 1
                else:
                    # No capacity limit or unknown: store anyway
                    if not hasattr(self.player_state, "salvage_modules"):
                        self.player_state.salvage_modules = []
                    if not isinstance(self.player_state.salvage_modules, list):
                        self.player_state.salvage_modules = []
                    
                    import copy
                    for module in salvage_modules:
                        if isinstance(module, dict):
                            module_copy = copy.deepcopy(module)
                            self.player_state.salvage_modules.append(module_copy)
                            result["salvage_applied"] += 1
        
        # Log application
        self._event(
            context,
            stage="post_combat",
            subsystem="loot_applicator",
            detail={
                "encounter_id": loot_bundle.get("encounter_id", ""),
                "credits_applied": result["credits_applied"],
                "cargo_applied": result["cargo_applied"],
                "cargo_quantity": result["cargo_quantity"],
                "salvage_applied": result["salvage_applied"],
                "errors": result["errors"],
            },
        )
        
        return result

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
        allowed = {"travel_to_destination", "location_action", "encounter_action", "encounter_decision", "wait", "quit"}
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
        allowed.add("abandon_mission")  # Phase 7.x.1 - abandon routing
        allowed.add("claim_mission")
        allowed.add("dismiss_crew")
        allowed.add("combat_action")
        if command_type not in allowed:
            return command_type, payload, f"unsupported command type: {command_type}"
        return command_type, payload, None

    def _build_step_result(self, *, context: EngineContext, ok: bool, error: str | None) -> dict[str, Any]:
        result = {
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
        
        # Add game_over_reason if present
        if context.game_over_reason is not None:
            result["game_over_reason"] = context.game_over_reason
        elif error == "game_over" and self.player_state.run_end_reason:
            result["game_over_reason"] = self.player_state.run_end_reason
        
        # Add pending_combat payload if hard_stop is due to pending combat action
        if context.hard_stop and context.hard_stop_reason == "pending_combat_action" and self._pending_combat:
            from combat_resolver import available_actions, hull_percent
            
            pending = self._pending_combat
            player_ship_state = pending.get("player_ship_state")
            player_state = pending.get("player_state")
            enemy_state = pending.get("enemy_state")
            
            if player_ship_state and player_state:
                allowed_actions = available_actions(player_ship_state, player_state)
                round_number = pending.get("round_number", 0) + 1  # Next round
                player_hull_pct = hull_percent(player_state.hull_current, player_state.hull_max) if player_state.hull_max > 0 else 0
                enemy_hull_pct = hull_percent(enemy_state.hull_current, enemy_state.hull_max) if enemy_state and enemy_state.hull_max > 0 else 0
                
                # Check for invalid state (hull_max <= 0)
                invalid_state = False
                error_msg = None
                if player_state.hull_max <= 0 or (enemy_state and enemy_state.hull_max <= 0):
                    invalid_state = True
                    error_msg = f"invalid_combat_state: player_hull_max={player_state.hull_max}, enemy_hull_max={enemy_state.hull_max if enemy_state else 'None'}, player_hull_id={player_ship_state.get('hull_id', 'unknown')}, enemy_hull_id={pending.get('enemy_ship_dict', {}).get('hull_id', 'unknown')}"
                
                # Map contract action names to lower_snake_case IDs
                action_options = []
                for action in allowed_actions:
                    action_id = action.lower().replace(" ", "_")
                    action_options.append({"id": action_id, "label": action})
                
                result["pending_combat"] = {
                    "combat_id": pending.get("combat_id", ""),
                    "encounter_id": pending.get("encounter_id", ""),
                    "round_number": round_number,
                    "player_hull_pct": player_hull_pct,
                    "enemy_hull_pct": enemy_hull_pct,
                    "allowed_actions": action_options,
                    "invalid_state": invalid_state,
                    "error": error_msg,
                    "player_hull_max": player_state.hull_max if player_state else 0,
                    "enemy_hull_max": enemy_state.hull_max if enemy_state else 0,
                }
        
        return result

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
        
        # Lightweight mission evaluation on turn advance (secondary trigger)
        if int(result.days_completed) > 0:
            self._evaluate_active_missions_on_turn_tick(
                logger=self._logger if self._logging_enabled else None,
                turn=int(get_current_turn()),
            )
            # Clear all DataNet mission offers on turn advance (Phase 7.x)
            self._mission_manager.clear_datanet_offers(location_id=None)
        
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

    def _build_default_fleet(self, starting_ship_override: dict | None = None) -> dict[str, ShipEntity]:
        """
        Build default starting ship with config-driven or data-driven hull selection.
        
        This is deterministic and occurs only on new game initialization.
        All ship stats derive from assemble_ship() output.
        
        If starting_ship_override is provided, it must contain:
        - hull_id: str
        - modules: list[dict] where each dict has module_id: str
        """
        from data_loader import load_hulls, load_modules
        
        # Handle admin override
        if starting_ship_override is not None:
            return self._build_override_fleet(starting_ship_override)
        
        # Default logic (unchanged)
        hulls_data = load_hulls()
        hulls_list = hulls_data.get("hulls", [])
        
        if not hulls_list:
            raise ValueError("no_hulls_available: No hulls found in hulls.json")
        
        # Try config-provided starting_hull_id first
        config_hull_id = self.config.get("starting_hull_id")
        hull_id = None
        hull_data = None
        
        if config_hull_id:
            # Validate config hull exists
            for hull in hulls_list:
                if hull.get("hull_id") == config_hull_id:
                    hull_data = hull
                    hull_id = config_hull_id
                    break
            if hull_id is None:
                # Config provided invalid hull_id, fall through to fallback
                pass
        
        # Fallback: pick first tier 1 CIV frame hull, or first hull if no match
        if hull_id is None:
            for hull in hulls_list:
                if hull.get("tier") == 1 and hull.get("frame") == "CIV":
                    hull_data = hull
                    hull_id = hull.get("hull_id")
                    break
            # If still no match, use first hull (deterministic)
            if hull_id is None:
                hull_data = hulls_list[0]
                hull_id = hull_data.get("hull_id")
        
        if not hull_id or not hull_data:
            raise ValueError("no_hulls_available: Could not select valid starting hull")
        
        module_instances = []
        degradation_state = {"weapon": 0, "defense": 0, "engine": 0}
        
        # assemble_ship will raise ValueError if hull_id is invalid
        assembled = assemble_ship(hull_id, module_instances, degradation_state)
        
        # Validate assembled ship has valid hull_max
        if assembled.get("hull_max", 0) <= 0:
            raise ValueError(f"invalid_hull_assembly: hull_id={hull_id} resulted in hull_max={assembled.get('hull_max', 0)}")
        
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

    def _build_override_fleet(self, override: dict) -> dict[str, ShipEntity]:
        """
        Build starting ship from admin override.
        
        Validates:
        - hull_id exists in catalog
        - module_ids exist in catalog
        - Slot compatibility (modules don't exceed available slots)
        - No secondaries allowed
        
        Raises ValueError on any validation failure.
        """
        from data_loader import load_hulls, load_modules
        
        # Validate override structure
        if not isinstance(override, dict):
            raise ValueError("starting_ship_override must be a dict")
        
        hull_id = override.get("hull_id")
        if not isinstance(hull_id, str):
            raise ValueError("starting_ship_override.hull_id must be a string")
        
        modules_override = override.get("modules")
        if not isinstance(modules_override, list):
            raise ValueError("starting_ship_override.modules must be a list")
        
        # Load catalogs
        hulls_data = load_hulls()
        hulls_list = hulls_data.get("hulls", [])
        modules_data = load_modules()
        modules_list = modules_data.get("modules", [])
        
        # Build lookup dictionaries
        hulls_by_id = {hull.get("hull_id"): hull for hull in hulls_list}
        modules_by_id = {module.get("module_id"): module for module in modules_list}
        
        # Validate hull_id exists
        if hull_id not in hulls_by_id:
            raise ValueError(f"starting_ship_override: hull_id '{hull_id}' not found in hull catalog")
        
        hull_data = hulls_by_id[hull_id]
        
        # Get slot distribution from ship system contract
        frame = hull_data.get("frame")
        tier = hull_data.get("tier")
        if not isinstance(frame, str) or not isinstance(tier, int):
            raise ValueError(f"starting_ship_override: hull '{hull_id}' has invalid frame or tier")
        
        slots = get_slot_distribution(frame, tier)
        weapon_slots = slots["weapon_slots"]
        defense_slots = slots["defense_slots"]
        utility_slots = slots["utility_slots"]
        untyped_slots = slots["untyped_slots"]
        total_slots = slots["total_slots"]
        
        # Validate and build module_instances
        module_instances = []
        module_ids_list = []
        slot_type_counts = {"weapon": 0, "defense": 0, "utility": 0}
        
        for module_entry in modules_override:
            if not isinstance(module_entry, dict):
                raise ValueError("starting_ship_override.modules entries must be dicts")
            
            module_id = module_entry.get("module_id")
            if not isinstance(module_id, str):
                raise ValueError("starting_ship_override.modules entries must have module_id as string")
            
            # Validate module_id exists
            if module_id not in modules_by_id:
                raise ValueError(f"starting_ship_override: module_id '{module_id}' not found in module catalog")
            
            module_def = modules_by_id[module_id]
            slot_type = module_def.get("slot_type")
            
            if slot_type not in ("weapon", "defense", "utility"):
                raise ValueError(f"starting_ship_override: module '{module_id}' has invalid slot_type '{slot_type}'")
            
            # Check for secondaries (not allowed)
            if module_entry.get("secondaries"):
                raise ValueError(f"starting_ship_override: module '{module_id}' must not have secondaries")
            
            # Count by slot type
            slot_type_counts[slot_type] += 1
            module_ids_list.append(module_id)
            
            # Build module instance with empty secondaries
            module_instances.append({
                "module_id": module_id,
                "secondaries": []
            })
        
        # Validate slot compatibility
        # Each module consumes 1 slot (no compact secondaries allowed)
        total_modules = len(module_instances)
        if total_modules > total_slots:
            raise ValueError(
                f"starting_ship_override: {total_modules} modules exceed total slots {total_slots} "
                f"(weapon={weapon_slots}, defense={defense_slots}, utility={utility_slots}, untyped={untyped_slots})"
            )
        
        # Check typed slot limits
        untyped_remaining = untyped_slots
        for slot_type in ("weapon", "defense", "utility"):
            needed = slot_type_counts[slot_type]
            base_slots = {
                "weapon": weapon_slots,
                "defense": defense_slots,
                "utility": utility_slots,
            }[slot_type]
            
            base_used = min(base_slots, needed)
            overflow = needed - base_used
            
            if overflow > 0:
                if overflow > untyped_remaining:
                    raise ValueError(
                        f"starting_ship_override: {slot_type} modules exceed capacity: "
                        f"needs {needed}, base slots {base_slots}, untyped remaining {untyped_remaining}"
                    )
                untyped_remaining -= overflow
        
        # Build ship using assemble_ship (single authority)
        degradation_state = {"weapon": 0, "defense": 0, "engine": 0}
        assembled = assemble_ship(hull_id, module_instances, degradation_state)
        
        # Validate assembled ship
        if assembled.get("hull_max", 0) <= 0:
            raise ValueError(
                f"starting_ship_override: hull_id={hull_id} resulted in invalid hull_max={assembled.get('hull_max', 0)}"
            )
        
        # Log admin override event (immediately after successful override application)
        self._logger.log(
            turn=0,
            action="admin_override_starting_ship",
            state_change=json.dumps({
                "event": "admin_override_starting_ship",
                "hull_id": hull_id,
                "modules": module_ids_list,
            }),
        )
        
        # Extract cargo capacities
        cargo_base = hull_data.get("cargo", {})
        physical_cargo_base = int(cargo_base.get("physical_base", 0))
        data_cargo_base = int(cargo_base.get("data_base", 0))
        utility_effects = assembled.get("ship_utility_effects", {})
        physical_cargo_capacity = physical_cargo_base + int(utility_effects.get("physical_cargo_bonus", 0))
        data_cargo_capacity = data_cargo_base + int(utility_effects.get("data_cargo_bonus", 0))
        
        # Extract crew capacity
        crew_capacity = int(hull_data.get("crew_capacity", 0))
        
        # Extract subsystem bands
        bands = assembled.get("bands", {})
        effective_bands = bands.get("effective", {})
        
        # Create ShipEntity
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

    def _get_encounter_description(self, subtype_id: str) -> str:
        """Get human-readable description for an encounter subtype."""
        # Map subtype_id to display name
        description_map = {
            "civilian_trader_ship": "Civilian Trader",
            "customs_patrol": "Border Patrol",
            "bounty_hunter": "Bounty Hunter",
            "pirate_raider": "Pirate Raider",
            "merchant_convoy": "Merchant Convoy",
            "smuggler": "Smuggler",
            "scavenger": "Scavenger",
            "military_patrol": "Military Patrol",
        }
        return description_map.get(subtype_id, subtype_id.replace("_", " ").title())

    def _format_ship_info_frame_only(self, ship_dict: dict[str, Any]) -> dict[str, Any]:
        """Format ship information for encounter display - only frame, no modules/stats."""
        from data_loader import load_hulls
        
        hull_id = ship_dict.get("hull_id", "unknown")
        hulls_data = load_hulls()
        hulls_list = hulls_data.get("hulls", [])
        
        hull_name = "Unknown Ship"
        frame = "UNKNOWN"
        tier = 0
        
        for hull in hulls_list:
            if hull.get("hull_id") == hull_id:
                hull_name = hull.get("name", hull_id)
                frame = hull.get("frame", "UNKNOWN")
                tier = hull.get("tier", 0)
                break
        
        return {
            "hull_id": hull_id,
            "hull_name": hull_name,
            "frame": frame,
            "tier": tier,
        }

    def _format_ship_info(self, ship_dict: dict[str, Any]) -> dict[str, Any]:
        """Format ship information for combat display - includes modules/stats."""
        from data_loader import load_hulls, load_modules
        
        hull_id = ship_dict.get("hull_id", "unknown")
        hulls_data = load_hulls()
        hulls_list = hulls_data.get("hulls", [])
        
        hull_name = "Unknown Ship"
        for hull in hulls_list:
            if hull.get("hull_id") == hull_id:
                hull_name = hull.get("name", hull_id)
                break
        
        # Count modules by type using module catalog
        module_instances = ship_dict.get("module_instances", [])
        modules_data = load_modules()
        modules_list = modules_data.get("modules", [])
        modules_by_id = {m.get("module_id"): m for m in modules_list}
        
        weapon_count = 0
        defense_count = 0
        utility_count = 0
        for module_instance in module_instances:
            module_id = module_instance.get("module_id")
            module_def = modules_by_id.get(module_id)
            if module_def:
                slot_type = module_def.get("slot_type", "")
                if slot_type == "weapon":
                    weapon_count += 1
                elif slot_type == "defense":
                    defense_count += 1
                elif slot_type == "utility":
                    utility_count += 1
        
        return {
            "hull_id": hull_id,
            "hull_name": hull_name,
            "module_count": len(module_instances),
            "weapon_modules": weapon_count,
            "defense_modules": defense_count,
            "utility_modules": utility_count,
        }

    # Read-only accessors for CLI/UI
    def get_owned_ships(self) -> list[dict[str, Any]]:
        """Get list of all owned ships with summary information."""
        ships = []
        for ship_id in self.player_state.owned_ship_ids:
            ship = self.fleet_by_id.get(ship_id)
            if ship is None:
                continue
            hull_integrity = ship.persistent_state.get("current_hull_integrity", 0) or 0
            max_hull = ship.persistent_state.get("max_hull_integrity", 0) or 0
            ships.append({
                "ship_id": ship.ship_id,
                "hull_id": ship.model_id,
                "destination_id": ship.destination_id or ship.current_destination_id,
                "hull_integrity": {
                    "current": int(hull_integrity),
                    "max": int(max_hull),
                },
                "fuel": {
                    "current": int(ship.current_fuel or 0),
                    "capacity": int(ship.fuel_capacity or 0),
                },
            })
        return ships

    def get_active_ship(self) -> dict[str, Any] | None:
        """Get active ship summary information."""
        ship_id = self.player_state.active_ship_id
        if not ship_id:
            return None
        ship = self.fleet_by_id.get(ship_id)
        if ship is None:
            return None
        hull_integrity = ship.persistent_state.get("current_hull_integrity", 0) or 0
        max_hull = ship.persistent_state.get("max_hull_integrity", 0) or 0
        return {
            "ship_id": ship.ship_id,
            "hull_id": ship.model_id,
            "destination_id": ship.destination_id or ship.current_destination_id,
            "hull_integrity": {
                "current": int(hull_integrity),
                "max": int(max_hull),
            },
            "fuel": {
                "current": int(ship.current_fuel or 0),
                "capacity": int(ship.fuel_capacity or 0),
            },
        }

    def get_ship_modules(self, ship_id: str) -> list[dict[str, Any]]:
        """Get installed modules for a ship."""
        ship = self.fleet_by_id.get(ship_id)
        if ship is None:
            return []
        module_instances = ship.persistent_state.get("module_instances", [])
        if not isinstance(module_instances, list):
            return []
        modules = []
        for idx, module in enumerate(module_instances):
            if isinstance(module, dict):
                modules.append({
                    "slot_index": idx,
                    "module_id": module.get("module_id", "N/A"),
                    "slot_type": module.get("slot_type", "N/A"),
                })
        return modules

    def get_ship_cargo(self, ship_id: str) -> dict[str, int]:
        """Get cargo manifest for a ship."""
        return dict(self.player_state.cargo_by_ship.get(ship_id, {}))

    def get_warehouse_rentals(self) -> list[dict[str, Any]]:
        """Get list of warehouse rentals."""
        warehouses = self.player_state.warehouses
        rentals = []
        for destination_id, warehouse in warehouses.items():
            if not isinstance(warehouse, dict):
                continue
            capacity = int(warehouse.get("capacity", 0) or 0)
            goods = warehouse.get("goods", {})
            used = sum(int(qty) for qty in goods.values() if isinstance(qty, (int, str)))
            cost_per_turn = int(warehouse.get("cost_per_turn", 0) or 0)
            expiration_day = warehouse.get("expiration_day", "N/A")
            rentals.append({
                "destination_id": destination_id,
                "capacity": capacity,
                "used": used,
                "available": capacity - used,
                "cost_per_turn": cost_per_turn,
                "expiration_day": expiration_day,
            })
        return rentals

    def get_active_missions(self) -> list[dict[str, Any]]:
        """Get list of active missions."""
        return self._active_mission_rows()

    def get_claimable_missions(self) -> list[dict[str, Any]]:
        """Get list of completed missions with unclaimed rewards (Phase 7.11.2b)."""
        claimable = []
        for mission_id, mission in self._mission_manager.missions.items():
            # Phase 7.11.2b - Only include missions that meet ALL criteria:
            # - payout_policy == "claim_required"
            # - reward_status == "ungranted"
            # - mission_state == "resolved"
            if (mission.payout_policy == "claim_required" 
                and mission.reward_status == "ungranted"
                and mission.mission_state.value == "resolved"):
                claimable.append({
                    "mission_id": mission.mission_id,
                    "mission_type": mission.mission_type,
                    "mission_tier": mission.mission_tier,
                })
        return claimable

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

    def get_current_destination_context(self) -> Dict[str, Any]:
        """Get standardized destination context information.
        
        Returns structured dict with destination, system, and context information.
        For unvisited systems, only includes limited fields (no economy/situations).
        """
        destination = self._current_destination()
        if destination is None:
            return {
                "destination_name": "Unknown",
                "destination_type": "unknown",
                "population": 0,
                "system_id": self.player_state.current_system_id or "",
                "system_name": "Unknown",
                "system_government": "",
                "primary_economy": None,
                "secondary_economies": [],
                "active_situations": [],
            }
        
        system = self.sector.get_system(self.player_state.current_system_id)
        if system is None:
            return {
                "destination_name": destination.display_name,
                "destination_type": destination.destination_type,
                "population": int(destination.population),
                "system_id": "",
                "system_name": "Unknown",
                "system_government": "",
                "primary_economy": None,
                "secondary_economies": [],
                "active_situations": [],
            }
        
        system_visited = system.system_id in self.player_state.visited_system_ids
        
        # Base context (always available)
        context: Dict[str, Any] = {
            "destination_name": destination.display_name,
            "destination_type": destination.destination_type,
            "population": int(destination.population),
            "system_id": system.system_id,
            "system_name": system.name,
            "system_government": "",
            "primary_economy": None,
            "secondary_economies": [],
            "active_situations": [],
        }
        
        # Only include sensitive data if system is visited
        if system_visited:
            # Get government name
            try:
                government = self.government_registry.get_government(system.government_id)
                context["system_government"] = government.name
            except (KeyError, AttributeError):
                context["system_government"] = system.government_id
            
            # Get economy info from destination
            context["primary_economy"] = destination.primary_economy_id
            context["secondary_economies"] = list(destination.secondary_economy_ids) if destination.secondary_economy_ids else []
            
            # Get active situations for the system
            situation_rows = self._active_situation_rows_for_system(system_id=system.system_id)
            situation_ids = []
            for row in situation_rows:
                situation_id = row.get("situation_id")
                if isinstance(situation_id, str) and situation_id:
                    situation_ids.append(situation_id)
            context["active_situations"] = sorted(situation_ids)
        
        return context

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
            # Get target from structured schema (Phase 7.11.2b)
            target = getattr(mission, "target", {})
            target_id = target.get("target_id") if isinstance(target, dict) else None
            target_system_id = target.get("system_id") if isinstance(target, dict) else None
            
            # Get source from structured schema
            source = getattr(mission, "source", {})
            source_type = source.get("source_type") if isinstance(source, dict) else None
            source_id = source.get("source_id") if isinstance(source, dict) else None
            
            # Get payout policy (collection format)
            payout_policy = getattr(mission, "payout_policy", "auto")
            collection_format = "Auto" if payout_policy == "auto" else "Claim"
            
            # Calculate reward preview if ungranted (Phase 7.11.2b)
            reward_summary = []
            if mission.reward_status == "ungranted":
                preview = self._mission_manager.calculate_reward_preview(mission)
                if preview and "credits" in preview:
                    reward_summary = [{"field": "credits", "delta": preview["credits"]}]
            # If already granted, reward_summary remains empty (not shown in active missions)
            
            rows.append(
                {
                    "mission_id": mission_id,
                    "mission_type": getattr(mission, "mission_type", None),
                    "mission_tier": getattr(mission, "mission_tier", 1),
                    "origin_system_id": getattr(mission, "system_id", None),
                    "target_system_id": target_system_id,  # Phase 7.11.2b - Use mission.target["system_id"]
                    "target_destination_id": target_id,  # Phase 7.11.2b - Use mission.target["target_id"]
                    "source_type": source_type,
                    "source_id": source_id,
                    "payout_policy": payout_policy,
                    "collection_format": collection_format,
                    "status": "active",
                    "days_remaining": None,
                    "reward_summary": reward_summary,  # Phase 7.11.2b - Use preview calculation
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

    def _find_bar_locations_in_system(self, system_id: str) -> list[tuple[str, str]]:
        """
        Find all bar locations in a system.
        Returns list of (destination_id, location_id) tuples for enabled bars.
        """
        bars = []
        system = self.sector.get_system(system_id)
        if system is None:
            return bars
        
        for destination in system.destinations:
            for location in destination.locations:
                if location.location_type == "bar" and location.enabled:
                    bars.append((destination.destination_id, location.location_id))
        
        return bars
    
    def _pick_bar_in_system(self, system_id: str, preferred_destination_id: str | None = None) -> tuple[str, str, str] | None:
        """
        Pick a deterministic bar location in a system.
        Prefers preferred_destination_id if available, otherwise picks by smallest destination_id then location_id.
        Returns (system_id, destination_id, location_id) or None if no bars found.
        """
        bars = self._find_bar_locations_in_system(system_id)
        if not bars:
            return None
        
        # If preferred destination exists, pick from those
        preferred_bars = [(dest_id, loc_id) for dest_id, loc_id in bars if dest_id == preferred_destination_id] if preferred_destination_id else []
        
        if preferred_bars:
            # Pick smallest location_id among preferred bars
            preferred_bars.sort(key=lambda x: x[1])  # Sort by location_id
            dest_id, loc_id = preferred_bars[0]
            return (system_id, dest_id, loc_id)
        
        # Otherwise pick smallest destination_id, then smallest location_id
        bars.sort(key=lambda x: (x[0], x[1]))  # Sort by destination_id, then location_id
        dest_id, loc_id = bars[0]
        return (system_id, dest_id, loc_id)
    
    def _find_nearest_bar_location(self, system_id: str, preferred_destination_id: str | None = None) -> tuple[str, str, str]:
        """
        Find the nearest bar location using BFS from the given system.
        First checks current system, then expands outward by neighbor hops.
        Returns (target_system_id, target_destination_id, target_location_id).
        Raises RuntimeError if no bar exists in reachable systems.
        """
        # First try current system
        result = self._pick_bar_in_system(system_id, preferred_destination_id)
        if result is not None:
            return result
        
        # BFS outward by neighbor hops
        visited = {system_id}
        frontier = [system_id]
        
        while frontier:
            next_frontier = []
            candidate_systems_with_bars = []
            
            # Expand frontier: collect neighbors of all systems in current frontier
            for sid in frontier:
                system = self.sector.get_system(sid)
                if system is None:
                    continue
                # Iterate neighbors in sorted order for determinism
                for neighbor_id in sorted(system.neighbors):
                    if neighbor_id in visited:
                        continue
                    visited.add(neighbor_id)
                    next_frontier.append(neighbor_id)
            
            # Evaluate bars for systems in this hop ring
            for nid in sorted(set(next_frontier)):
                if self._pick_bar_in_system(nid, preferred_destination_id=None) is not None:
                    candidate_systems_with_bars.append(nid)
            
            # If any candidates found in this hop ring, pick the first one deterministically
            if candidate_systems_with_bars:
                target_system_id = min(candidate_systems_with_bars)  # Deterministic: smallest system_id
                result = self._pick_bar_in_system(target_system_id, preferred_destination_id=None)
                if result is not None:
                    return result
            
            frontier = next_frontier
        
        # No bar found in reachable systems
        raise RuntimeError(f"No bar location found in reachable systems from {system_id}")
    
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


def _is_data_cargo_sku(sku_id: str) -> bool:
    """Helper to determine if SKU is data cargo (simplified check)."""
    from data_loader import load_goods
    goods_data = load_goods()
    for good in goods_data.get("goods", []):
        if good.get("sku_id") == sku_id:
            tags = good.get("tags", [])
            return "data" in tags
    return False


def run_step_as_json(engine: GameEngine, command: dict[str, Any]) -> str:
    return json.dumps(engine.execute(command), sort_keys=True)
