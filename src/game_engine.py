from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
import hashlib
import json
import random
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
    dispatch_player_action,
)
from law_enforcement import CargoSnapshot, PlayerOption, TriggerType, enforcement_checkpoint
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
from travel_resolution import resolve_travel
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
        target_system_id = payload.get("target_system_id")
        if not isinstance(target_system_id, str) or not target_system_id:
            raise ValueError("travel_to_destination requires target_system_id.")
        system = self.sector.get_system(target_system_id)
        if system is None:
            raise ValueError(f"Unknown target_system_id: {target_system_id}")

        inter_system = bool(payload.get("inter_system", True))
        distance_ly = self._coerce_distance(payload.get("distance_ly", 1 if inter_system else 0), inter_system)
        target_destination_id = self._resolve_destination_id(system, payload.get("target_destination_id"))
        route_id = payload.get("route_id")
        route_tags = payload.get("route_tags")
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
                "distance_ly": distance_ly,
            },
        )

        active_ship = self._active_ship()
        travel_rng = self._rng_for_stable_id(stable_id=travel_id, stream_name=ENGINE_STREAM_NAME)
        travel_result = resolve_travel(
            ship=active_ship,
            inter_system=inter_system,
            distance_ly=distance_ly,
            advance_time=None,
            player_state=self.player_state,
            world_state_engine=self._world_state_engine(),
            current_system_id=self.player_state.current_system_id,
            route_id=route_id,
            route_tags=list(route_tags) if isinstance(route_tags, list) else None,
            rng=travel_rng,
        )
        self._event(
            context,
            stage="travel",
            subsystem="travel_resolution",
            detail={
                "travel_id": travel_id,
                "success": bool(travel_result.success),
                "reason": travel_result.reason,
                "fuel_cost": int(travel_result.fuel_cost),
                "current_fuel": int(travel_result.current_fuel),
            },
        )
        if not travel_result.success:
            return

        self.player_state.current_system_id = target_system_id
        self.player_state.current_destination_id = target_destination_id
        self.player_state.current_location_id = target_destination_id
        active_ship.current_system_id = target_system_id
        active_ship.current_destination_id = target_destination_id
        active_ship.current_location_id = target_destination_id
        active_ship.location_id = target_destination_id

        days = self._travel_days(inter_system=inter_system, distance_ly=distance_ly)
        time_result = self._advance_time(days=days, reason=f"travel:{travel_id}")
        self._event(
            context,
            stage="time_advance",
            subsystem="time_engine",
            detail={
                "travel_id": travel_id,
                "days_requested": int(days),
                "days_completed": int(time_result.days_completed),
                "hard_stop_reason": time_result.hard_stop_reason,
            },
        )

        if time_result.hard_stop_reason is not None:
            context.hard_stop = True
            context.hard_stop_reason = time_result.hard_stop_reason
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
        action_id = payload.get("action_id")
        if not isinstance(action_id, str) or not action_id:
            raise ValueError("location_action requires action_id.")
        kwargs = payload.get("kwargs", {})
        if kwargs is None:
            kwargs = {}
        if not isinstance(kwargs, dict):
            raise ValueError("location_action.kwargs must be an object.")

        destination = self._current_destination()
        if destination is None:
            raise ValueError("No current destination for location_action.")

        if self._is_market_scope_action(action_id):
            self._run_law_checkpoint(context, trigger_type=TriggerType.CUSTOMS)

        action_kwargs = self._build_destination_action_kwargs(action_id=action_id, destination=destination, kwargs=kwargs)
        result = dispatch_destination_action(action_id=action_id, **action_kwargs)
        self._event(
            context,
            stage="destination_interaction",
            subsystem="interaction_layer",
            detail={"action_id": action_id, "result": _jsonable(result)},
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

    def _travel_days(self, *, inter_system: bool, distance_ly: int) -> int:
        if inter_system:
            return max(1, int(distance_ly))
        return 1

    def _coerce_distance(self, value: Any, inter_system: bool) -> int:
        if not inter_system:
            return 0
        if not isinstance(value, (int, float)):
            raise ValueError("travel_to_destination.distance_ly must be a number for inter-system travel.")
        if value < 0:
            raise ValueError("travel_to_destination.distance_ly must be >= 0.")
        return int(value)

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

    def _rng_for_stable_id(self, *, stable_id: str, stream_name: str) -> random.Random:
        token = f"{self.world_seed}|{stable_id}|{stream_name}"
        digest = hashlib.sha256(token.encode("ascii")).hexdigest()
        return random.Random(int(digest[:16], 16))

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
        action_kwargs: dict[str, Any] = {"destination": destination}
        action_kwargs.update(kwargs)

        if action_id == "refuel":
            action_kwargs.setdefault("ship", self._active_ship())
            action_kwargs.setdefault("player_credits", int(self.player_state.credits))
            action_kwargs.setdefault("player", self.player_state)
            return action_kwargs

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
