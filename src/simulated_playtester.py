from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
import random
from typing import Any

from game_engine import GameEngine


VALID_ARREST_STATES = {"free", "detained_tier_1", "detained_tier_2"}


@dataclass(frozen=True)
class SimulationDecision:
    name: str
    weight: int
    payload: dict[str, Any]


class SimulatedPlaytester:
    def __init__(self, seed: int, max_turns: int = 250, bias_mode: str = "profit_reputation") -> None:
        self.seed = int(seed)
        self.max_turns = int(max_turns)
        self.bias_mode = str(bias_mode)
        self._output_path = Path(__file__).resolve().parents[1] / "test" / "output"

    def run(self) -> dict[str, Any]:
        first = self._run_once()
        second = self._run_once()

        if first["final_state_hash"] != second["final_state_hash"]:
            first["summary"]["determinism_verified"] = False
            self._write_log(first["summary"])
            raise AssertionError("Determinism verification failed: final state hash mismatch.")

        first["summary"]["determinism_verified"] = True
        self._write_log(first["summary"])
        self._print_summary(first["summary"])
        return dict(first["summary"])

    def _run_once(self) -> dict[str, Any]:
        engine = GameEngine(world_seed=self.seed)
        baseline_player = self._player_profile(engine)
        baseline_system = self._system_profile(engine)
        summary = {
            "engine_version": str(engine.execute({"type": "get_player_profile"}).get("version")),
            "seed": int(self.seed),
            "max_turns": int(self.max_turns),
            "turns_completed": 0,
            "hard_stop": False,
            "hard_stop_reason": None,
            "credit_delta": 0,
            "reputation_delta": 0,
            "heat_delta": 0,
            "enforcement_triggers": 0,
            "travel_count": 0,
            "buy_count": 0,
            "sell_count": 0,
            "refuel_count": 0,
            "determinism_verified": False,
        }
        seen_customs: set[tuple[int, str]] = set()

        for index in range(1, self.max_turns + 1):
            player_profile = self._player_profile(engine)
            destination_profile = self._destination_profile(engine)
            system_profile = self._system_profile(engine)
            decision = self._choose_action(
                engine=engine,
                turn_index=index,
                player_profile=player_profile,
                destination_profile=destination_profile,
                system_profile=system_profile,
            )
            result = engine.execute(decision.payload)
            if result.get("ok") is not True:
                # Keep the harness moving for non-fatal expected gating failures.
                result = engine.execute({"type": "wait", "days": 1})

            summary["turns_completed"] = int(index)
            summary["hard_stop"] = bool(result.get("hard_stop", False))
            summary["hard_stop_reason"] = result.get("hard_stop_reason")

            if decision.name == "travel":
                summary["travel_count"] += 1
            elif decision.name == "market_buy":
                summary["buy_count"] += 1
            elif decision.name == "market_sell":
                summary["sell_count"] += 1
            elif decision.name == "refuel":
                summary["refuel_count"] += 1

            for event in result.get("events", []):
                if not isinstance(event, dict):
                    continue
                if event.get("stage") != "law_checkpoint":
                    continue
                detail = event.get("detail", {})
                if not isinstance(detail, dict):
                    continue
                if detail.get("trigger_type") != "CUSTOMS":
                    continue
                if detail.get("skipped") is True:
                    continue
                summary["enforcement_triggers"] += 1
                key = (
                    int(result.get("turn_after", 0)),
                    str(engine.player_state.current_destination_id),
                )
                if key in seen_customs:
                    raise AssertionError("Duplicate customs trigger in same destination+turn.")
                seen_customs.add(key)

            self._assert_invariants(engine=engine)
            if summary["hard_stop"]:
                break

        final_player = self._player_profile(engine)
        final_system = self._system_profile(engine)
        summary["credit_delta"] = int(final_player["credits"]) - int(baseline_player["credits"])
        summary["reputation_delta"] = int(final_player["reputation_score"]) - int(
            baseline_player["reputation_score"]
        )
        summary["heat_delta"] = int(final_player["heat"]) - int(baseline_player["heat"])
        final_state_hash = self._final_state_hash(final_player=final_player, final_system=final_system)
        return {"summary": summary, "final_state_hash": final_state_hash}

    def _choose_action(
        self,
        *,
        engine: GameEngine,
        turn_index: int,
        player_profile: dict[str, Any],
        destination_profile: dict[str, Any],
        system_profile: dict[str, Any],
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

        at_destination_root = location_id == destination_id
        if at_destination_root:
            destination_actions = self._actions_for(engine, command_type="list_destination_actions", stage="destination_actions")
            action_ids = [str(row.get("action_id")) for row in destination_actions]
            if "refuel" in action_ids and fuel_current * 4 < fuel_capacity:
                decisions.append(
                    SimulationDecision(
                        name="refuel",
                        weight=6,
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
                        weight=4,
                        payload={"type": "enter_location", "location_id": market_locations[0]["location_id"]},
                    )
                )
        else:
            location_rows = [row for row in list(destination_profile.get("locations", [])) if isinstance(row, dict)]
            current_location = next((row for row in location_rows if row.get("location_id") == location_id), None)
            location_type = str(current_location.get("location_type")) if isinstance(current_location, dict) else ""
            if location_type == "market":
                sell_rows = self._market_rows(engine, "market_sell_list")
                buy_rows = self._market_rows(engine, "market_buy_list")
                legal_sell_rows = [row for row in sell_rows if int(row.get("player_has_units", 0)) > 0 and int(row.get("unit_price", 0)) > 0]
                legal_buy_rows = [row for row in buy_rows if int(row.get("unit_price", 0)) > 0]
                if reputation_band < 0:
                    legal_buy_rows = [row for row in legal_buy_rows if str(row.get("legality")) != "ILLEGAL"]
                if cargo_units > 0 and legal_sell_rows:
                    decisions.append(
                        SimulationDecision(
                            name="market_sell",
                            weight=5,
                            payload={
                                "type": "market_sell",
                                "sku_id": str(legal_sell_rows[0]["sku_id"]),
                                "quantity": 1,
                            },
                        )
                    )
                if (cargo_units == 0 or cargo_units < 2) and legal_buy_rows:
                    affordable = [
                        row for row in legal_buy_rows if int(row.get("unit_price", 0)) <= int(player_profile.get("credits", 0))
                    ]
                    if affordable:
                        decisions.append(
                            SimulationDecision(
                                name="market_buy",
                                weight=4,
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
                        weight=2,
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
            reachable = [
                row
                for row in list(system_profile.get("reachable_systems", []))
                if isinstance(row, dict) and bool(row.get("in_range"))
            ]
            if reachable:
                target = sorted(reachable, key=lambda row: str(row.get("system_id")))[0]
                decisions.append(
                    SimulationDecision(
                        name="travel",
                        weight=3,
                        payload={"type": "travel_to_destination", "target_system_id": target["system_id"]},
                    )
                )
            else:
                decisions.append(
                    SimulationDecision(
                        name="wait",
                        weight=1,
                        payload={"type": "wait", "days": 1},
                    )
                )

        return self._weighted_pick(rng=rng, decisions=decisions)

    def _player_profile(self, engine: GameEngine) -> dict[str, Any]:
        result = engine.execute({"type": "get_player_profile"})
        return self._detail_from_stage(result, "player_profile")

    def _system_profile(self, engine: GameEngine) -> dict[str, Any]:
        result = engine.execute({"type": "get_system_profile"})
        return self._detail_from_stage(result, "system_profile")

    def _destination_profile(self, engine: GameEngine) -> dict[str, Any]:
        result = engine.execute({"type": "get_destination_profile"})
        return self._detail_from_stage(result, "destination_profile")

    def _actions_for(self, engine: GameEngine, *, command_type: str, stage: str) -> list[dict[str, Any]]:
        result = engine.execute({"type": command_type})
        detail = self._detail_from_stage(result, stage)
        actions = detail.get("actions", [])
        if not isinstance(actions, list):
            return []
        return [row for row in actions if isinstance(row, dict)]

    def _market_rows(self, engine: GameEngine, command_type: str) -> list[dict[str, Any]]:
        result = engine.execute({"type": command_type})
        stage = "market_buy_list" if command_type == "market_buy_list" else "market_sell_list"
        detail = self._detail_from_stage(result, stage)
        rows = detail.get("rows", [])
        if not isinstance(rows, list):
            return []
        return [row for row in rows if isinstance(row, dict)]

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

    def _assert_invariants(self, *, engine: GameEngine) -> None:
        profile = self._player_profile(engine)
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

    def _write_log(self, summary: dict[str, Any]) -> None:
        self._output_path.mkdir(parents=True, exist_ok=True)
        log_path = self._output_path / f"simulation_log_seed_{self.seed}.json"
        log_path.write_text(json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8")

    def _print_summary(self, summary: dict[str, Any]) -> None:
        print("SIMULATION COMPLETE")
        print(f"Seed: {summary['seed']}")
        print(f"Turns: {summary['turns_completed']}")
        print(f"Credits delta: {summary['credit_delta']}")
        print(f"Enforcement triggers: {summary['enforcement_triggers']}")
        print(f"Determinism verified: {summary['determinism_verified']}")
