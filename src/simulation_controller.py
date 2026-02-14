from __future__ import annotations

from typing import Any

from combat_resolver import resolve_combat
from encounter_generator import generate_encounter
from interaction_layer import (
    HANDLER_COMBAT_STUB,
    HANDLER_PURSUIT_STUB,
    dispatch_destination_action,
    dispatch_player_action,
)
from npc_ship_generator import generate_npc_ship
from pursuit_resolver import resolve_pursuit
from reward_applicator import apply_materialized_reward
from reward_materializer import materialize_reward
from travel_resolution import resolve_travel
from turn_loop import BuyAction, MoveAction, SellAction, TurnLoop


class SimulationController:
    def __init__(self, world_seed, world_state, player):
        self._world_seed = int(world_seed)
        self._world_state = world_state
        self._player = player
        self._sector = _state_get(world_state, "sector")
        self._fleet_by_id = _state_get(world_state, "fleet_by_id", {})
        self._active_situations = _state_get(world_state, "active_situations", [])
        self._active_encounter = _state_get(world_state, "active_encounter")
        self._turn_loop = _state_get(world_state, "turn_loop")
        if self._turn_loop is None:
            self._turn_loop = TurnLoop(
                time_engine=_state_get(world_state, "time_engine"),
                sector=self._sector,
                player_state=player,
                logger=_state_get(world_state, "logger"),
                economy_engine=_state_get(world_state, "economy_engine"),
                law_engine=_state_get(world_state, "law_engine"),
                catalog=_state_get(world_state, "catalog"),
                government_registry=_state_get(world_state, "government_registry"),
                world_seed=self._world_seed,
            )

    def execute(self, command: dict) -> dict:
        result = {
            "ok": False,
            "error": None,
            "events": [],
            "hard_stop": False,
            "hard_stop_reason": None,
        }
        try:
            action_type, payload = self._validate_command(command)
            if action_type == "travel_to_destination":
                result["events"].extend(self._execute_travel_to_destination(payload))
            elif action_type == "location_action":
                result["events"].extend(self._execute_location_action(payload))
            elif action_type == "encounter_action":
                result["events"].extend(self._execute_encounter_action(payload))
            else:
                result["error"] = f"unsupported_action_type:{action_type}"
                return result
            hard_stop, reason = self._hard_stop_status(result["events"])
            result["ok"] = True
            result["hard_stop"] = hard_stop
            result["hard_stop_reason"] = reason
            _state_set(self._world_state, "active_encounter", self._active_encounter)
            return result
        except Exception as exc:  # noqa: BLE001
            result["error"] = str(exc)
            hard_stop, reason = self._hard_stop_status(result["events"])
            result["hard_stop"] = hard_stop
            result["hard_stop_reason"] = reason
            return result

    def _execute_travel_to_destination(self, payload: dict[str, Any]) -> list[dict]:
        target_system_id = payload.get("target_system_id")
        if not isinstance(target_system_id, str) or not target_system_id:
            raise ValueError("payload.target_system_id is required for travel_to_destination.")
        distance_ly = int(payload.get("distance_ly", 1))
        active_ship = self._active_ship()
        travel_result = resolve_travel(
            ship=active_ship,
            inter_system=True,
            distance_ly=distance_ly,
            advance_time=None,
        )
        events = [
            {
                "event_type": "travel_resolution",
                "success": bool(travel_result.success),
                "reason": travel_result.reason,
                "fuel_cost": int(travel_result.fuel_cost),
                "current_fuel": int(travel_result.current_fuel),
                "target_system_id": target_system_id,
            }
        ]
        if not travel_result.success:
            return events

        self._turn_loop.execute_move(MoveAction(target_system_id=target_system_id))
        events.append(
            {
                "event_type": "enforcement_checkpoint_processed",
                "checkpoint": "border",
                "system_id": target_system_id,
            }
        )
        current_system = self._sector.get_system(self._player.current_system_id)
        destination = _find_shipdock_destination(current_system)
        self._player.current_destination_id = getattr(destination, "destination_id", None)
        active_ship.location_id = self._player.current_destination_id or self._player.current_system_id
        active_ship.current_location_id = active_ship.location_id
        events.append(
            {
                "event_type": "travel_applied",
                "system_id": self._player.current_system_id,
                "destination_id": self._player.current_destination_id,
            }
        )

        encounter = generate_encounter(
            encounter_id=f"SC-{self._world_seed}-{self._turn_loop._time_engine.current_turn}",  # noqa: SLF001
            world_seed=str(self._world_seed),
            system_government_id=current_system.government_id,
            active_situations=list(self._active_situations),
            travel_context={"mode": "system_arrival"},
        )
        self._active_encounter = encounter
        events.append(
            {
                "event_type": "encounter_generated",
                "encounter_id": encounter.encounter_id,
                "subtype_id": encounter.subtype_id,
                "posture": encounter.posture,
                "initiative": encounter.initiative,
            }
        )
        events.extend(self._resolve_encounter(encounter, payload.get("encounter_action", "ignore")))
        return events

    def _execute_location_action(self, payload: dict[str, Any]) -> list[dict]:
        action_id = payload.get("action_id")
        if not isinstance(action_id, str) or not action_id:
            raise ValueError("payload.action_id is required for location_action.")
        if action_id == "buy":
            sku = payload.get("sku")
            if not isinstance(sku, str) or not sku:
                raise ValueError("payload.sku is required for buy.")
            self._turn_loop.execute_buy(BuyAction(sku=sku))
            return [{"event_type": "location_action", "action_id": action_id, "sku": sku}]
        if action_id == "sell":
            sku = payload.get("sku")
            if not isinstance(sku, str) or not sku:
                raise ValueError("payload.sku is required for sell.")
            self._turn_loop.execute_sell(SellAction(sku=sku))
            return [{"event_type": "location_action", "action_id": action_id, "sku": sku}]

        current_system = self._sector.get_system(self._player.current_system_id)
        destination = _find_shipdock_destination(current_system)
        if destination is None:
            raise ValueError("No destination available for location_action.")
        from shipdock_inventory import generate_shipdock_inventory

        inventory = generate_shipdock_inventory(self._world_seed, current_system.system_id, current_system.population)
        action_kwargs = {
            "destination": destination,
            "player": self._player,
            "fleet_by_id": self._fleet_by_id,
        }
        if action_id == "refuel":
            active_ship = self._active_ship()
            result = dispatch_destination_action(
                action_id,
                ship=active_ship,
                player_credits=self._player.credits,
                requested_units=payload.get("requested_units"),
                player=self._player,
            )
        elif action_id == "buy_hull":
            hull_id = payload.get("hull_id") or inventory.get("hulls", [{}])[0].get("hull_id")
            ship_id = payload.get("ship_id") or f"SHIP-{self._turn_loop._time_engine.current_turn:03d}"  # noqa: SLF001
            result = dispatch_destination_action(
                action_id,
                **action_kwargs,
                inventory=inventory,
                hull_id=hull_id,
                ship_id=ship_id,
            )
        elif action_id == "sell_hull":
            ship_id = payload.get("ship_id", self._player.active_ship_id)
            result = dispatch_destination_action(action_id, **action_kwargs, ship_id=ship_id)
        elif action_id == "buy_module":
            module_id = payload.get("module_id") or inventory.get("modules", [{}])[0].get("module_id")
            ship_id = payload.get("ship_id", self._player.active_ship_id)
            result = dispatch_destination_action(
                action_id,
                **action_kwargs,
                inventory=inventory,
                ship_id=ship_id,
                module_id=module_id,
            )
        elif action_id == "sell_module":
            ship_id = payload.get("ship_id", self._player.active_ship_id)
            module_id = payload.get("module_id")
            result = dispatch_destination_action(
                action_id,
                **action_kwargs,
                ship_id=ship_id,
                module_id=module_id,
            )
        elif action_id == "repair_ship":
            ship_id = payload.get("ship_id", self._player.active_ship_id)
            result = dispatch_destination_action(
                action_id,
                **action_kwargs,
                ship_id=ship_id,
                system_population=current_system.population,
            )
        else:
            raise ValueError(f"Unsupported location action_id: {action_id}")
        return [{"event_type": "location_action", "action_id": action_id, "result": result}]

    def _execute_encounter_action(self, payload: dict[str, Any]) -> list[dict]:
        action = payload.get("action")
        if not isinstance(action, str) or not action:
            raise ValueError("payload.action is required for encounter_action.")
        if self._active_encounter is None:
            raise ValueError("No active encounter to resolve.")
        events = self._resolve_encounter(self._active_encounter, action)
        self._active_encounter = None
        return events

    def _resolve_encounter(self, encounter, action: str) -> list[dict]:
        dispatch = dispatch_player_action(
            spec=encounter,
            player_action=action,
            world_seed=str(self._world_seed),
            ignore_count=0,
            reputation_band=self._player.reputation_by_system.get(self._player.current_system_id, 50),
            notoriety_band=self._player.progression_tracks.get("notoriety", 0),
        )
        events = [
            {
                "event_type": "encounter_dispatch",
                "encounter_id": encounter.encounter_id,
                "action": action,
                "next_handler": dispatch.next_handler,
                "payload": dispatch.handler_payload,
            }
        ]
        if dispatch.next_handler == HANDLER_PURSUIT_STUB:
            pursuit = resolve_pursuit(
                encounter_id=f"PUR-{encounter.encounter_id}",
                world_seed=str(self._world_seed),
                pursuer_ship={"speed": 3, "pilot_skill": 3, "engine_band": 3, "tr_band": 3},
                pursued_ship={"speed": 3, "pilot_skill": 3, "engine_band": 3, "tr_band": 3},
            )
            events.append(
                {
                    "event_type": "pursuit_resolved",
                    "encounter_id": encounter.encounter_id,
                    "outcome": pursuit.outcome,
                    "escaped": bool(pursuit.escaped),
                }
            )
        elif dispatch.next_handler == HANDLER_COMBAT_STUB:
            current_system = self._sector.get_system(self._player.current_system_id)
            enemy_ship = generate_npc_ship(
                world_seed=self._world_seed,
                system_id=self._player.current_system_id,
                system_population=current_system.population,
                encounter_id=encounter.encounter_id,
                encounter_subtype=encounter.subtype_id,
            )
            active_ship = self._active_ship()
            player_ship_state = {
                "hull_id": active_ship.model_id,
                "module_instances": list(active_ship.persistent_state.get("module_instances", [])),
                "degradation_state": dict(
                    active_ship.persistent_state.get("degradation_state", {"weapon": 0, "defense": 0, "engine": 0})
                ),
                "current_hull_integrity": int(active_ship.persistent_state.get("current_hull_integrity", 0) or 0),
            }
            combat = resolve_combat(
                world_seed=str(self._world_seed),
                combat_id=f"CMB-{encounter.encounter_id}",
                system_id=self._player.current_system_id,
                player_ship_state=player_ship_state,
                enemy_ship_state=enemy_ship,
                max_rounds=3,
            )
            events.append(
                {
                    "event_type": "combat_resolved",
                    "encounter_id": encounter.encounter_id,
                    "outcome": combat.outcome,
                    "winner": combat.winner,
                    "salvage_count": len(combat.salvage_modules),
                }
            )
        current_system = self._sector.get_system(self._player.current_system_id)
        reward = materialize_reward(encounter, [_market_payload(current_system.attributes.get("market"))], str(self._world_seed))
        applied = apply_materialized_reward(player=self._player, reward_payload=reward, context="simulation_controller")
        events.append(
            {
                "event_type": "reward_applied",
                "encounter_id": encounter.encounter_id,
                "reward_profile_id": encounter.reward_profile_id,
                "applied": applied,
            }
        )
        return events

    def _validate_command(self, command: dict) -> tuple[str, dict]:
        if not isinstance(command, dict):
            raise ValueError("command must be a dictionary.")
        action_type = command.get("action_type")
        payload = command.get("payload", {})
        if not isinstance(action_type, str):
            raise ValueError("command.action_type must be a string.")
        if action_type not in {"travel_to_destination", "location_action", "encounter_action"}:
            raise ValueError(f"Unsupported action_type: {action_type}")
        if not isinstance(payload, dict):
            raise ValueError("command.payload must be a dictionary.")
        return action_type, payload

    def _active_ship(self):
        active_ship_id = self._player.active_ship_id
        ship = self._fleet_by_id.get(active_ship_id)
        if ship is None:
            raise ValueError("Player has no active ship.")
        return ship

    def _hard_stop_status(self, events: list[dict]) -> tuple[bool, str | None]:
        if self._player.arrest_state == "detained_tier_2":
            return True, "tier2_detention"
        for event in events:
            if event.get("event_type") == "combat_resolved" and event.get("outcome") == "destroyed" and event.get("winner") == "enemy":
                return True, "player_death"
        return False, None


def _state_get(state: Any, key: str, default: Any = None) -> Any:
    if isinstance(state, dict):
        return state.get(key, default)
    return getattr(state, key, default)


def _state_set(state: Any, key: str, value: Any) -> None:
    if isinstance(state, dict):
        state[key] = value
    else:
        setattr(state, key, value)


def _market_payload(market) -> dict:
    if market is None:
        return {"categories": {}}
    categories = {}
    for category_id, category in market.categories.items():
        categories[category_id] = {
            "produced": [good.sku for good in category.produced],
            "consumed": [good.sku for good in category.consumed],
            "neutral": [good.sku for good in category.neutral],
        }
    return {"categories": categories}


def _find_shipdock_destination(system):
    if system is None:
        return None
    for destination in system.destinations:
        for location in destination.locations:
            if location.location_type == "shipdock" and location.enabled:
                return destination
    return system.destinations[0] if system.destinations else None

