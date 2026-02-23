from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
import random
from typing import cast
from typing import Any

from game_engine import GameEngine


VALID_ARREST_STATES = {"free", "detained_tier_1", "detained_tier_2"}


@dataclass(frozen=True)
class SimulationDecision:
    name: str
    weight: int
    payload: dict[str, Any]


@dataclass
class SimulationRunContext:
    full_step_results: list[dict[str, Any]]
    current_turn_step_results: list[dict[str, Any]]
    summary_metrics: dict[str, Any] | None = None


class SimulatedPlaytester:
    def __init__(
        self,
        seed: int,
        turns: int = 250,
        bias_mode: str = "B",
        max_turns: int | None = None,
    ) -> None:
        self.seed = int(seed)
        resolved_turns = int(max_turns) if max_turns is not None else int(turns)
        self.max_turns = resolved_turns
        normalized_bias = str(bias_mode).strip().upper()
        if normalized_bias not in {"A", "B"}:
            raise ValueError("bias_mode must be either 'A' or 'B'.")
        self.bias_mode = normalized_bias
        self._output_path = Path(__file__).resolve().parents[1] / "test" / "output"

    def run(self) -> dict[str, Any]:
        first = self._run_once()
        second = self._run_once()

        determinism_verified = self._verify_determinism(first=first, second=second)
        first["summary_metrics"]["determinism_verified"] = determinism_verified

        self._write_log(run_result=first)
        self._print_summary(first["summary_metrics"])
        return dict(first["summary_metrics"])

    def _run_once(self) -> dict[str, Any]:
        engine = GameEngine(world_seed=self.seed)
        context = SimulationRunContext(full_step_results=[], current_turn_step_results=[])
        observed_market_prices: dict[str, dict[str, dict[str, int]]] = {}
        baseline_player = self._player_profile(engine=engine, context=context)
        baseline_system = self._system_profile(engine=engine, context=context)
        systems_visited: set[str] = {str(baseline_player.get("system_id", ""))}
        destinations_visited: set[str] = {str(baseline_player.get("destination_id", ""))}
        summary: dict[str, Any] = {
            "engine_version": str(
                self._execute_and_log(engine=engine, context=context, command={"type": "get_player_profile"}).get("version")
            ),
            "seed": int(self.seed),
            "turns_requested": int(self.max_turns),
            "max_turns": int(self.max_turns),
            "bias_mode": self.bias_mode,
            "turns_completed": 0,
            "hard_stop": False,
            "hard_stop_reason": None,
            "credit_delta": 0,
            "reputation_delta": 0,
            "heat_delta": 0,
            "customs_checks_attempted": 0,
            "customs_checks_triggered": 0,
            "customs_checks_skipped_by_probability": 0,
            "customs_checks_blocked_by_guard": 0,
            "customs_probability_evaluations": 0,
            "customs_probability_evaluation_log": [],
            "enforcement_triggers": 0,
            "enforcement_by_system": {},
            "systems_visited": [],
            "destinations_visited": [],
            "travel_count": 0,
            "intra_system_travel_count": 0,
            "inter_system_travel_count": 0,
            "buy_count": 0,
            "sell_count": 0,
            "refuel_count": 0,
            "determinism_verified": False,
        }
        context.summary_metrics = summary

        for index in range(1, self.max_turns + 1):
            context.current_turn_step_results = []
            player_profile = self._player_profile(engine=engine, context=context)
            destination_profile = self._destination_profile(engine=engine, context=context)
            system_profile = self._system_profile(engine=engine, context=context)
            self._capture_market_observations(
                engine=engine,
                context=context,
                player_profile=player_profile,
                destination_profile=destination_profile,
                observed_market_prices=observed_market_prices,
            )
            decision = self._choose_action(
                engine=engine,
                context=context,
                turn_index=index,
                player_profile=player_profile,
                destination_profile=destination_profile,
                system_profile=system_profile,
                observed_market_prices=observed_market_prices,
                systems_visited=systems_visited,
                destinations_visited=destinations_visited,
            )
            result = self._execute_and_log(engine=engine, context=context, command=decision.payload)
            if result.get("ok") is not True:
                # Keep the harness moving for non-fatal expected gating failures.
                result = self._execute_and_log(engine=engine, context=context, command={"type": "wait", "days": 1})

            summary["turns_completed"] = int(index)
            summary["hard_stop"] = bool(result.get("hard_stop", False))
            summary["hard_stop_reason"] = result.get("hard_stop_reason")
            systems_visited.add(str(engine.player_state.current_system_id))
            destinations_visited.add(str(engine.player_state.current_destination_id))

            if decision.name == "travel":
                summary["travel_count"] += 1
                if decision.payload.get("target_system_id") == player_profile.get("system_id"):
                    summary["intra_system_travel_count"] += 1
                else:
                    summary["inter_system_travel_count"] += 1
            elif decision.name == "market_buy":
                summary["buy_count"] += 1
            elif decision.name == "market_sell":
                summary["sell_count"] += 1
            elif decision.name == "refuel":
                summary["refuel_count"] += 1

            self._assert_invariants(engine=engine, context=context)
            if summary["hard_stop"]:
                break

        final_player = self._player_profile(engine=engine, context=context)
        final_system = self._system_profile(engine=engine, context=context)
        summary["systems_visited"] = sorted(system for system in systems_visited if system)
        summary["destinations_visited"] = sorted(destination for destination in destinations_visited if destination)
        summary["credit_delta"] = int(final_player["credits"]) - int(baseline_player["credits"])
        summary["reputation_delta"] = int(final_player["reputation_score"]) - int(
            baseline_player["reputation_score"]
        )
        summary["heat_delta"] = int(final_player["heat"]) - int(baseline_player["heat"])
        final_state_hash = self._final_state_hash(final_player=final_player, final_system=final_system)
        last_player_state_snapshot_hash = self._player_state_snapshot_hash(player_profile=final_player)
        return {
            "summary_metrics": summary,
            "full_step_results": list(context.full_step_results),
            "final_state_hash": final_state_hash,
            "last_player_state_snapshot_hash": last_player_state_snapshot_hash,
        }

    def _choose_action(
        self,
        *,
        engine: GameEngine,
        context: SimulationRunContext,
        turn_index: int,
        player_profile: dict[str, Any],
        destination_profile: dict[str, Any],
        system_profile: dict[str, Any],
        observed_market_prices: dict[str, dict[str, dict[str, int]]],
        systems_visited: set[str],
        destinations_visited: set[str],
    ) -> SimulationDecision:
        rng = self._turn_rng(turn_index)
        decisions: list[SimulationDecision] = []
        location_id = str(player_profile.get("location_id"))
        destination_id = str(player_profile.get("destination_id"))
        reputation_band = int(player_profile.get("reputation_band", 0))
        cargo_manifest = dict(player_profile.get("cargo_manifest", {}))
        cargo_units = sum(int(v) for v in cargo_manifest.values())
        fuel_current = int(player_profile.get("fuel_current", 0))
        fuel_capacity = max(1, int(player_profile.get("fuel_capacity", 1)))
        credits = int(player_profile.get("credits", 0))
        spread_threshold = 8 if self.bias_mode == "A" else 2

        at_destination_root = location_id == destination_id
        if at_destination_root:
            destination_actions = self._actions_for(
                engine=engine,
                context=context,
                command_type="list_destination_actions",
                stage="destination_actions",
            )
            action_ids = [str(row.get("action_id")) for row in destination_actions]
            if "refuel" in action_ids and fuel_current * 4 < fuel_capacity:
                decisions.append(
                    SimulationDecision(
                        name="refuel",
                        weight=5 if self.bias_mode == "A" else 3,
                        payload={"type": "destination_action", "action_id": "refuel", "action_kwargs": {}},
                    )
                )
            if reputation_band < 0 and "customs_inspection" in action_ids:
                decisions.append(
                    SimulationDecision(
                        name="customs",
                        weight=4,
                        payload={
                            "type": "destination_action",
                            "action_id": "customs_inspection",
                            "action_kwargs": {},
                        },
                    )
                )

            market_locations = [
                row
                for row in list(destination_profile.get("locations", []))
                if isinstance(row, dict) and row.get("location_type") == "market"
            ]
            if market_locations:
                decisions.append(
                    SimulationDecision(
                        name="enter_market",
                        weight=8 if self.bias_mode == "A" else 5,
                        payload={"type": "enter_location", "location_id": market_locations[0]["location_id"]},
                    )
                )
            decisions.extend(
                self._travel_decisions(
                    engine=engine,
                    player_profile=player_profile,
                    system_profile=system_profile,
                    observed_market_prices=observed_market_prices,
                    systems_visited=systems_visited,
                    destinations_visited=destinations_visited,
                    spread_threshold=spread_threshold,
                )
            )
        else:
            location_rows = [row for row in list(destination_profile.get("locations", [])) if isinstance(row, dict)]
            current_location = next((row for row in location_rows if row.get("location_id") == location_id), None)
            location_type = str(current_location.get("location_type")) if isinstance(current_location, dict) else ""
            if location_type == "market":
                sell_rows = self._market_rows(engine=engine, context=context, command_type="market_sell_list")
                buy_rows = self._market_rows(engine=engine, context=context, command_type="market_buy_list")
                self._record_market_rows(
                    destination_id=destination_id,
                    buy_rows=buy_rows,
                    sell_rows=sell_rows,
                    observed_market_prices=observed_market_prices,
                )
                legal_sell_rows = [row for row in sell_rows if int(row.get("player_has_units", 0)) > 0 and int(row.get("unit_price", 0)) > 0]
                legal_buy_rows = [row for row in buy_rows if int(row.get("unit_price", 0)) > 0]
                if reputation_band < 0:
                    legal_buy_rows = [row for row in legal_buy_rows if str(row.get("legality")) != "ILLEGAL"]
                legal_sell_rows = sorted(legal_sell_rows, key=lambda row: int(row.get("unit_price", 0)), reverse=True)
                legal_buy_rows = sorted(legal_buy_rows, key=lambda row: int(row.get("unit_price", 0)))
                if cargo_units > 0 and legal_sell_rows:
                    decisions.append(
                        SimulationDecision(
                            name="market_sell",
                            weight=7 if self.bias_mode == "A" else 6,
                            payload={
                                "type": "market_sell",
                                "sku_id": str(legal_sell_rows[0]["sku_id"]),
                                "quantity": 1,
                            },
                        )
                    )
                if legal_buy_rows:
                    profitable_buys = [
                        row
                        for row in legal_buy_rows
                        if self._best_known_sell_price(
                            observed_market_prices=observed_market_prices,
                            sku_id=str(row.get("sku_id", "")),
                        )
                        - int(row.get("unit_price", 0))
                        >= spread_threshold
                    ]
                    preferred_buy_rows = profitable_buys if profitable_buys else legal_buy_rows
                    affordable = [
                        row for row in preferred_buy_rows if int(row.get("unit_price", 0)) <= credits
                    ]
                    if affordable:
                        decisions.append(
                            SimulationDecision(
                                name="market_buy",
                                weight=4 if self.bias_mode == "A" else 7,
                                payload={
                                    "type": "market_buy",
                                    "sku_id": str(affordable[0]["sku_id"]),
                                    "quantity": 1,
                                },
                            )
                        )
                decisions.append(
                    SimulationDecision(
                        name="return_to_destination",
                        weight=2 if self.bias_mode == "A" else 1,
                        payload={"type": "return_to_destination"},
                    )
                )
            else:
                decisions.append(
                    SimulationDecision(
                        name="return_to_destination",
                        weight=2,
                        payload={"type": "return_to_destination"},
                    )
                )

        if not decisions:
            fallback_travel = self._travel_decisions(
                engine=engine,
                player_profile=player_profile,
                system_profile=system_profile,
                observed_market_prices=observed_market_prices,
                systems_visited=systems_visited,
                destinations_visited=destinations_visited,
                spread_threshold=spread_threshold,
            )
            if fallback_travel:
                decisions.extend(fallback_travel)
            else:
                decisions.append(
                    SimulationDecision(
                        name="wait",
                        weight=1,
                        payload={"type": "wait", "days": 1},
                    )
                )

        return self._weighted_pick(rng=rng, decisions=decisions)

    def _player_profile(self, *, engine: GameEngine, context: SimulationRunContext) -> dict[str, Any]:
        result = self._execute_and_log(engine=engine, context=context, command={"type": "get_player_profile"})
        return self._detail_from_stage(result, "player_profile")

    def _system_profile(self, *, engine: GameEngine, context: SimulationRunContext) -> dict[str, Any]:
        result = self._execute_and_log(engine=engine, context=context, command={"type": "get_system_profile"})
        return self._detail_from_stage(result, "system_profile")

    def _destination_profile(self, *, engine: GameEngine, context: SimulationRunContext) -> dict[str, Any]:
        result = self._execute_and_log(engine=engine, context=context, command={"type": "get_destination_profile"})
        return self._detail_from_stage(result, "destination_profile")

    def _actions_for(
        self,
        *,
        engine: GameEngine,
        context: SimulationRunContext,
        command_type: str,
        stage: str,
    ) -> list[dict[str, Any]]:
        result = self._execute_and_log(engine=engine, context=context, command={"type": command_type})
        detail = self._detail_from_stage(result, stage)
        actions = detail.get("actions", [])
        if not isinstance(actions, list):
            return []
        return [row for row in actions if isinstance(row, dict)]

    def _market_rows(
        self,
        *,
        engine: GameEngine,
        context: SimulationRunContext,
        command_type: str,
    ) -> list[dict[str, Any]]:
        result = self._execute_and_log(engine=engine, context=context, command={"type": command_type})
        stage = "market_buy_list" if command_type == "market_buy_list" else "market_sell_list"
        detail = self._detail_from_stage(result, stage)
        rows = detail.get("rows", [])
        if not isinstance(rows, list):
            return []
        return [row for row in rows if isinstance(row, dict)]

    def _execute_and_log(
        self,
        *,
        engine: GameEngine,
        context: SimulationRunContext,
        command: dict[str, Any],
    ) -> dict[str, Any]:
        result = engine.execute(command)
        jsonable_result = cast(dict[str, Any], self._jsonable(result))
        context.full_step_results.append(jsonable_result)
        context.current_turn_step_results.append(jsonable_result)
        if context.summary_metrics is not None:
            self._instrument_enforcement_metrics(
                summary=context.summary_metrics,
                result=result,
                engine=engine,
            )
        return result

    def _instrument_enforcement_metrics(
        self,
        *,
        summary: dict[str, Any],
        result: dict[str, Any],
        engine: GameEngine,
    ) -> None:
        for event in list(result.get("events", [])):
            if not isinstance(event, dict):
                continue
            stage = str(event.get("stage", ""))
            detail = event.get("detail", {})
            if not isinstance(detail, dict):
                continue
            if stage == "customs_guard" and bool(detail.get("blocked")):
                summary["customs_checks_attempted"] += 1
                summary["customs_checks_blocked_by_guard"] += 1
                continue
            if stage != "law_checkpoint":
                continue
            if str(detail.get("trigger_type", "")) != "CUSTOMS":
                continue
            summary["customs_checks_attempted"] += 1
            if bool(detail.get("skipped")):
                continue
            summary["customs_probability_evaluations"] += 1
            outcome = detail.get("outcome")
            summary["customs_probability_evaluation_log"].append(
                {
                    "turn_after": int(result.get("turn_after", 0)),
                    "system_id": str(engine.player_state.current_system_id),
                    "destination_id": str(engine.player_state.current_destination_id),
                    "probability_evaluated": True,
                    "triggered": outcome is not None,
                }
            )
            if outcome is None:
                summary["customs_checks_skipped_by_probability"] += 1
                continue
            summary["customs_checks_triggered"] += 1
            summary["enforcement_triggers"] += 1
            system_id = str(engine.player_state.current_system_id)
            by_system = cast(dict[str, int], summary["enforcement_by_system"])
            by_system[system_id] = int(by_system.get(system_id, 0)) + 1

    def _travel_decisions(
        self,
        *,
        engine: GameEngine,
        player_profile: dict[str, Any],
        system_profile: dict[str, Any],
        observed_market_prices: dict[str, dict[str, dict[str, int]]],
        systems_visited: set[str],
        destinations_visited: set[str],
        spread_threshold: int,
    ) -> list[SimulationDecision]:
        decisions: list[SimulationDecision] = []
        current_system_id = str(player_profile.get("system_id"))
        current_destination_id = str(player_profile.get("destination_id"))
        reachable = [
            row
            for row in list(system_profile.get("reachable_systems", []))
            if isinstance(row, dict) and bool(row.get("in_range"))
        ]

        # Intra-system travel: if spread exists, or if bias B wants active exploration.
        for destination_id in self._destination_ids_for_system(engine=engine, system_id=current_system_id):
            if destination_id == current_destination_id:
                continue
            spread_score = self._destination_spread_score(
                observed_market_prices=observed_market_prices,
                source_destination_id=current_destination_id,
                target_destination_id=destination_id,
            )
            if spread_score >= spread_threshold:
                decisions.append(
                    SimulationDecision(
                        name="travel",
                        weight=4 if self.bias_mode == "A" else 8,
                        payload={
                            "type": "travel_to_destination",
                            "target_system_id": current_system_id,
                            "target_destination_id": destination_id,
                        },
                    )
                )
            elif self.bias_mode == "B" and destination_id not in destinations_visited:
                decisions.append(
                    SimulationDecision(
                        name="travel",
                        weight=5,
                        payload={
                            "type": "travel_to_destination",
                            "target_system_id": current_system_id,
                            "target_destination_id": destination_id,
                        },
                    )
                )

        # Inter-system travel: reachable systems only, with bias toward profitable or exploratory paths.
        for row in sorted(reachable, key=lambda entry: str(entry.get("system_id"))):
            target_system_id = str(row.get("system_id"))
            destination_ids = self._destination_ids_for_system(engine=engine, system_id=target_system_id)
            if not destination_ids:
                continue
            ranked = sorted(
                destination_ids,
                key=lambda destination_id: self._destination_spread_score(
                    observed_market_prices=observed_market_prices,
                    source_destination_id=current_destination_id,
                    target_destination_id=destination_id,
                ),
                reverse=True,
            )
            target_destination_id = ranked[0]
            spread_score = self._destination_spread_score(
                observed_market_prices=observed_market_prices,
                source_destination_id=current_destination_id,
                target_destination_id=target_destination_id,
            )
            if spread_score >= spread_threshold:
                decisions.append(
                    SimulationDecision(
                        name="travel",
                        weight=3 if self.bias_mode == "A" else 10,
                        payload={
                            "type": "travel_to_destination",
                            "target_system_id": target_system_id,
                            "target_destination_id": target_destination_id,
                        },
                    )
                )
            elif self.bias_mode == "B" and target_system_id not in systems_visited:
                decisions.append(
                    SimulationDecision(
                        name="travel",
                        weight=7,
                        payload={
                            "type": "travel_to_destination",
                            "target_system_id": target_system_id,
                            "target_destination_id": target_destination_id,
                        },
                    )
                )

        return decisions

    def _destination_ids_for_system(self, *, engine: GameEngine, system_id: str) -> list[str]:
        system = engine.sector.get_system(system_id)
        if system is None:
            return []
        destination_ids = [str(destination.destination_id) for destination in list(system.destinations or [])]
        return sorted(destination_ids)

    def _destination_spread_score(
        self,
        *,
        observed_market_prices: dict[str, dict[str, dict[str, int]]],
        source_destination_id: str,
        target_destination_id: str,
    ) -> int:
        source_prices = observed_market_prices.get(source_destination_id, {})
        target_prices = observed_market_prices.get(target_destination_id, {})
        if not source_prices or not target_prices:
            return 0
        best_spread = 0
        for sku_id in set(source_prices).intersection(target_prices):
            source_buy = int(source_prices.get(sku_id, {}).get("buy", 0))
            target_sell = int(target_prices.get(sku_id, {}).get("sell", 0))
            if source_buy <= 0 or target_sell <= 0:
                continue
            best_spread = max(best_spread, target_sell - source_buy)
        return best_spread

    def _best_known_sell_price(
        self,
        *,
        observed_market_prices: dict[str, dict[str, dict[str, int]]],
        sku_id: str,
    ) -> int:
        best = 0
        for destination_prices in observed_market_prices.values():
            best = max(best, int(destination_prices.get(sku_id, {}).get("sell", 0)))
        return best

    def _capture_market_observations(
        self,
        *,
        engine: GameEngine,
        context: SimulationRunContext,
        player_profile: dict[str, Any],
        destination_profile: dict[str, Any],
        observed_market_prices: dict[str, dict[str, dict[str, int]]],
    ) -> None:
        location_id = str(player_profile.get("location_id"))
        destination_id = str(player_profile.get("destination_id"))
        if location_id == destination_id:
            return
        location_rows = [row for row in list(destination_profile.get("locations", [])) if isinstance(row, dict)]
        current_location = next((row for row in location_rows if row.get("location_id") == location_id), None)
        location_type = str(current_location.get("location_type")) if isinstance(current_location, dict) else ""
        if location_type != "market":
            return
        buy_rows = self._market_rows(engine=engine, context=context, command_type="market_buy_list")
        sell_rows = self._market_rows(engine=engine, context=context, command_type="market_sell_list")
        self._record_market_rows(
            destination_id=destination_id,
            buy_rows=buy_rows,
            sell_rows=sell_rows,
            observed_market_prices=observed_market_prices,
        )

    def _record_market_rows(
        self,
        *,
        destination_id: str,
        buy_rows: list[dict[str, Any]],
        sell_rows: list[dict[str, Any]],
        observed_market_prices: dict[str, dict[str, dict[str, int]]],
    ) -> None:
        destination_book = observed_market_prices.setdefault(destination_id, {})
        for row in buy_rows:
            sku_id = str(row.get("sku_id", ""))
            unit_price = int(row.get("unit_price", 0))
            if not sku_id or unit_price <= 0:
                continue
            sku_book = destination_book.setdefault(sku_id, {})
            current_buy = int(sku_book.get("buy", unit_price))
            sku_book["buy"] = min(current_buy, unit_price)
        for row in sell_rows:
            sku_id = str(row.get("sku_id", ""))
            unit_price = int(row.get("unit_price", 0))
            if not sku_id or unit_price <= 0:
                continue
            sku_book = destination_book.setdefault(sku_id, {})
            current_sell = int(sku_book.get("sell", unit_price))
            sku_book["sell"] = max(current_sell, unit_price)

    def _detail_from_stage(self, result: dict[str, Any], stage: str) -> dict[str, Any]:
        for event in list(result.get("events", [])):
            if not isinstance(event, dict):
                continue
            if event.get("stage") != stage:
                continue
            detail = event.get("detail", {})
            if isinstance(detail, dict):
                return detail
        return {}

    def _weighted_pick(self, *, rng: random.Random, decisions: list[SimulationDecision]) -> SimulationDecision:
        ordered = sorted(decisions, key=lambda row: (row.name, json.dumps(row.payload, sort_keys=True)))
        total = sum(max(1, int(row.weight)) for row in ordered)
        pick = rng.uniform(0.0, float(total))
        running = 0.0
        for row in ordered:
            running += float(max(1, int(row.weight)))
            if pick <= running:
                return row
        return ordered[-1]

    def _turn_rng(self, turn_index: int) -> random.Random:
        token = f"{self.seed}_sim_{turn_index}"
        seed_int = int(hashlib.sha256(token.encode("utf-8")).hexdigest(), 16) % (2**32)
        return random.Random(seed_int)

    def _assert_invariants(self, *, engine: GameEngine, context: SimulationRunContext) -> None:
        profile = self._player_profile(engine=engine, context=context)
        if int(profile.get("credits", 0)) < 0:
            raise AssertionError("credits invariant violated")
        fuel_current = int(profile.get("fuel_current", 0))
        fuel_capacity = int(profile.get("fuel_capacity", 0))
        if fuel_current < 0:
            raise AssertionError("fuel_current invariant violated")
        if fuel_current > fuel_capacity:
            raise AssertionError("fuel capacity invariant violated")
        cargo_manifest = dict(profile.get("cargo_manifest", {}))
        for sku_id, quantity in cargo_manifest.items():
            _ = sku_id
            if int(quantity) < 0:
                raise AssertionError("cargo quantity invariant violated")
        arrest_state = str(profile.get("arrest_state", ""))
        if arrest_state not in VALID_ARREST_STATES:
            raise AssertionError("arrest_state invariant violated")

    def _final_state_hash(self, *, final_player: dict[str, Any], final_system: dict[str, Any]) -> str:
        payload = {
            "credits": int(final_player.get("credits", 0)),
            "fuel": int(final_player.get("fuel_current", 0)),
            "cargo_manifest": {
                str(sku_id): int(quantity)
                for sku_id, quantity in sorted(dict(final_player.get("cargo_manifest", {})).items())
            },
            "reputation": int(final_player.get("reputation_score", 0)),
            "heat": int(final_player.get("heat", 0)),
            "system_id": final_player.get("system_id"),
            "destination_id": final_player.get("destination_id"),
            "turn": int(final_player.get("turn", 0)),
            "reachable": [
                (row.get("system_id"), float(row.get("distance_ly", 0.0)), bool(row.get("in_range")))
                for row in sorted(
                    list(final_system.get("reachable_systems", [])),
                    key=lambda entry: str(entry.get("system_id")),
                )
                if isinstance(row, dict)
            ],
        }
        return hashlib.sha256(json.dumps(payload, sort_keys=True).encode("utf-8")).hexdigest()

    def _player_state_snapshot_hash(self, *, player_profile: dict[str, Any]) -> str:
        payload = {
            "credits": int(player_profile.get("credits", 0)),
            "fuel_current": int(player_profile.get("fuel_current", 0)),
            "fuel_capacity": int(player_profile.get("fuel_capacity", 0)),
            "cargo_manifest": {
                str(sku_id): int(quantity)
                for sku_id, quantity in sorted(dict(player_profile.get("cargo_manifest", {})).items())
            },
            "reputation_score": int(player_profile.get("reputation_score", 0)),
            "heat": int(player_profile.get("heat", 0)),
            "arrest_state": str(player_profile.get("arrest_state", "")),
            "system_id": str(player_profile.get("system_id", "")),
            "destination_id": str(player_profile.get("destination_id", "")),
            "location_id": str(player_profile.get("location_id", "")),
            "turn": int(player_profile.get("turn", 0)),
        }
        return hashlib.sha256(json.dumps(payload, sort_keys=True).encode("utf-8")).hexdigest()

    def _verify_determinism(self, *, first: dict[str, Any], second: dict[str, Any]) -> bool:
        first_summary = dict(first.get("summary_metrics", {}))
        second_summary = dict(second.get("summary_metrics", {}))
        first_summary.pop("determinism_verified", None)
        second_summary.pop("determinism_verified", None)
        if first_summary != second_summary:
            return False
        if int(first_summary.get("credit_delta", 0)) != int(second_summary.get("credit_delta", 0)):
            return False
        enforcement_keys = {
            "customs_checks_attempted",
            "customs_checks_triggered",
            "customs_checks_skipped_by_probability",
            "customs_checks_blocked_by_guard",
            "enforcement_triggers",
            "enforcement_by_system",
        }
        for key in enforcement_keys:
            if first_summary.get(key) != second_summary.get(key):
                return False
        if list(first_summary.get("systems_visited", [])) != list(second_summary.get("systems_visited", [])):
            return False
        if first.get("last_player_state_snapshot_hash") != second.get("last_player_state_snapshot_hash"):
            return False
        return True

    def _write_log(self, run_result: dict[str, Any]) -> None:
        self._output_path.mkdir(parents=True, exist_ok=True)
        log_path = self._output_path / f"simulation_full_log_seed_{self.seed}.json"
        payload = {
            "seed": int(self.seed),
            "turns_requested": int(self.max_turns),
            "turns_completed": int(run_result["summary_metrics"]["turns_completed"]),
            "bias_mode": self.bias_mode,
            "summary_metrics": run_result["summary_metrics"],
            "full_step_results": run_result["full_step_results"],
        }
        log_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")

    def _print_summary(self, summary: dict[str, Any]) -> None:
        print("SIMULATION COMPLETE")
        print(f"Seed: {summary['seed']}")
        print(f"Bias mode: {summary['bias_mode']}")
        print(f"Turns: {summary['turns_completed']}/{summary['turns_requested']}")
        print(f"Credits delta: {summary['credit_delta']}")
        print(f"Enforcement triggers: {summary['enforcement_triggers']}")
        print(f"Customs attempted: {summary['customs_checks_attempted']}")
        print(f"Customs triggered: {summary['customs_checks_triggered']}")
        print(f"Customs skipped by probability: {summary['customs_checks_skipped_by_probability']}")
        print(f"Customs blocked by guard: {summary['customs_checks_blocked_by_guard']}")
        print(f"Systems visited: {len(summary['systems_visited'])}")
        print(f"Destinations visited: {len(summary['destinations_visited'])}")
        print(f"Determinism verified: {summary['determinism_verified']}")

    def _jsonable(self, value: Any) -> Any:
        if isinstance(value, (str, int, float, bool)) or value is None:
            return value
        if isinstance(value, list):
            return [self._jsonable(entry) for entry in value]
        if isinstance(value, tuple):
            return [self._jsonable(entry) for entry in value]
        if isinstance(value, dict):
            return {str(key): self._jsonable(val) for key, val in value.items()}
        if hasattr(value, "value"):
            return str(value.value)
        if hasattr(value, "__dict__"):
            return self._jsonable(dict(value.__dict__))
        return str(value)
