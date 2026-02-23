from __future__ import annotations

from collections import deque
from dataclasses import dataclass
import argparse
import hashlib
import json
from pathlib import Path
import random
from typing import Any

from game_engine import GameEngine


@dataclass(frozen=True)
class PlannedCommand:
    command: dict[str, Any]
    reason: str
    key: str


@dataclass
class ActionPlanner:
    seed: int
    bias: str
    scripted_commands: list[dict[str, Any]] | None = None

    def __post_init__(self) -> None:
        self._script_index = 0
        self._seen_prices: dict[str, dict[str, dict[str, int]]] = {}
        self._recent: deque[tuple[str, bool]] = deque(maxlen=10)

    def choose_command(
        self,
        *,
        step: int,
        engine: GameEngine,
        player_profile: dict[str, Any],
        destination_profile: dict[str, Any],
        system_profile: dict[str, Any],
    ) -> PlannedCommand:
        scripted = self._next_scripted_command()
        if scripted is not None:
            return scripted

        candidates: list[PlannedCommand] = []
        location_id = str(player_profile.get("location_id", ""))
        destination_id = str(player_profile.get("destination_id", ""))
        current_system_id = str(player_profile.get("system_id", ""))
        credits = int(player_profile.get("credits", 0))
        fuel_current = int(player_profile.get("fuel_current", 0))
        fuel_capacity = max(1, int(player_profile.get("fuel_capacity", 1)))
        at_destination_root = location_id == destination_id

        if at_destination_root:
            destination_actions = _list_actions(engine=engine, command_type="list_destination_actions", stage="destination_actions")
            action_ids = {str(row.get("action_id", "")) for row in destination_actions}
            market_locations = [
                row
                for row in list(destination_profile.get("locations", []))
                if isinstance(row, dict) and str(row.get("location_type", "")) == "market"
            ]
            if market_locations:
                market_location_id = str(market_locations[0].get("location_id", ""))
                candidates.append(
                    _planned(
                        {"type": "enter_location", "location_id": market_location_id},
                        "bias B: enter market to inspect offers and cargo liquidity.",
                    )
                )
            if "refuel" in action_ids and fuel_current * 3 < fuel_capacity:
                candidates.append(
                    _planned(
                        {"type": "destination_action", "action_id": "refuel", "action_kwargs": {}},
                        "bias B: fuel low enough to justify refuel before exploration.",
                    )
                )
            candidates.extend(
                self._travel_candidates(
                    engine=engine,
                    current_system_id=current_system_id,
                    current_destination_id=destination_id,
                    system_profile=system_profile,
                    include_intra=True,
                )
            )
            candidates.append(_planned({"type": "wait", "days": 1}, "fallback: advance time when no stronger action is available."))
        else:
            location_type = _current_location_type(destination_profile=destination_profile, location_id=location_id)
            if location_type == "market":
                buy_rows = _market_rows(engine=engine, command_type="market_buy_list")
                sell_rows = _market_rows(engine=engine, command_type="market_sell_list")
                self._record_market_rows(destination_id=destination_id, buy_rows=buy_rows, sell_rows=sell_rows)
                profitable_sell = sorted(
                    [
                        row
                        for row in sell_rows
                        if int(row.get("player_has_units", 0)) > 0 and int(row.get("unit_price", 0)) > 0
                    ],
                    key=lambda row: int(row.get("unit_price", 0)),
                    reverse=True,
                )
                if profitable_sell:
                    top = profitable_sell[0]
                    candidates.append(
                        _planned(
                            {"type": "market_sell", "sku_id": str(top.get("sku_id", "")), "quantity": 1},
                            "bias B: realize immediate value by selling best visible offer.",
                        )
                    )
                affordable = sorted(
                    [
                        row
                        for row in buy_rows
                        if int(row.get("unit_price", 0)) > 0 and int(row.get("unit_price", 0)) <= credits
                    ],
                    key=lambda row: int(row.get("unit_price", 0)),
                )
                if affordable:
                    best_buy = self._best_buy_candidate(destination_id=destination_id, rows=affordable)
                    if best_buy is not None:
                        candidates.append(
                            _planned(
                                {"type": "market_buy", "sku_id": str(best_buy.get("sku_id", "")), "quantity": 1},
                                "bias B: buy affordable trade good with best known resale spread.",
                            )
                        )
                candidates.append(
                    _planned({"type": "return_to_destination"}, "bias B: return to destination root to unlock travel options.")
                )
            else:
                candidates.append(_planned({"type": "return_to_destination"}, "not in market; return to destination root."))
                candidates.extend(
                    self._travel_candidates(
                        engine=engine,
                        current_system_id=current_system_id,
                        current_destination_id=destination_id,
                        system_profile=system_profile,
                        include_intra=True,
                    )
                )
                candidates.append(_planned({"type": "wait", "days": 1}, "fallback: no useful local action found."))

        if not candidates:
            return _planned({"type": "wait", "days": 1}, "fallback: no candidates generated.")
        return self._choose_with_repeat_guard(step=step, candidates=candidates)

    def note_outcome(self, *, command_key: str, changed: bool) -> None:
        self._recent.append((command_key, bool(changed)))

    def _next_scripted_command(self) -> PlannedCommand | None:
        if not self.scripted_commands:
            return None
        if self._script_index >= len(self.scripted_commands):
            return None
        command = dict(self.scripted_commands[self._script_index])
        self._script_index += 1
        return _planned(command, "scripted command sequence.")

    def _choose_with_repeat_guard(self, *, step: int, candidates: list[PlannedCommand]) -> PlannedCommand:
        weighted = list(candidates)
        order_rng = _step_rng(seed=self.seed, step=step, stream="policy_order")
        order_rng.shuffle(weighted)
        weighted = sorted(weighted, key=lambda row: row.key)
        for candidate in weighted:
            if not self._is_stuck_repeat(candidate.key):
                return candidate
        for candidate in weighted:
            if candidate.command.get("type") != "wait":
                return candidate
        return weighted[0]

    def _is_stuck_repeat(self, command_key: str) -> bool:
        recent_same = [entry for entry in list(self._recent) if entry[0] == command_key]
        if len(recent_same) < 2:
            return False
        return all(changed is False for _, changed in recent_same[-2:])

    def _travel_candidates(
        self,
        *,
        engine: GameEngine,
        current_system_id: str,
        current_destination_id: str,
        system_profile: dict[str, Any],
        include_intra: bool,
    ) -> list[PlannedCommand]:
        candidates: list[PlannedCommand] = []
        if include_intra:
            for destination_id in _destination_ids_for_system(engine=engine, system_id=current_system_id):
                if destination_id == current_destination_id:
                    continue
                spread = _spread_between_destinations(
                    seen_prices=self._seen_prices,
                    source_destination_id=current_destination_id,
                    target_destination_id=destination_id,
                )
                if spread > 0:
                    reason = "bias B: intra-system destination with visible spread."
                else:
                    reason = "bias B: explore local destination to gather market intelligence."
                candidates.append(
                    _planned(
                        {
                            "type": "travel_to_destination",
                            "target_system_id": current_system_id,
                            "target_destination_id": destination_id,
                        },
                        reason,
                    )
                )

        reachable = [
            row
            for row in list(system_profile.get("reachable_systems", []))
            if isinstance(row, dict) and bool(row.get("in_range"))
        ]
        for row in sorted(reachable, key=lambda entry: str(entry.get("system_id", ""))):
            target_system_id = str(row.get("system_id", ""))
            destination_ids = _destination_ids_for_system(engine=engine, system_id=target_system_id)
            if not destination_ids:
                continue
            ranked = sorted(
                destination_ids,
                key=lambda destination_id: _spread_between_destinations(
                    seen_prices=self._seen_prices,
                    source_destination_id=current_destination_id,
                    target_destination_id=destination_id,
                ),
                reverse=True,
            )
            target_destination_id = ranked[0]
            candidates.append(
                _planned(
                    {
                        "type": "travel_to_destination",
                        "target_system_id": target_system_id,
                        "target_destination_id": target_destination_id,
                    },
                    "bias B: explore reachable system for potential arbitrage.",
                )
            )
        return candidates

    def _record_market_rows(
        self,
        *,
        destination_id: str,
        buy_rows: list[dict[str, Any]],
        sell_rows: list[dict[str, Any]],
    ) -> None:
        destination_book = self._seen_prices.setdefault(destination_id, {})
        for row in buy_rows:
            sku_id = str(row.get("sku_id", ""))
            unit_price = int(row.get("unit_price", 0))
            if not sku_id or unit_price <= 0:
                continue
            sku_book = destination_book.setdefault(sku_id, {})
            current = int(sku_book.get("buy", unit_price))
            sku_book["buy"] = min(current, unit_price)
        for row in sell_rows:
            sku_id = str(row.get("sku_id", ""))
            unit_price = int(row.get("unit_price", 0))
            if not sku_id or unit_price <= 0:
                continue
            sku_book = destination_book.setdefault(sku_id, {})
            current = int(sku_book.get("sell", unit_price))
            sku_book["sell"] = max(current, unit_price)

    def _best_buy_candidate(self, *, destination_id: str, rows: list[dict[str, Any]]) -> dict[str, Any] | None:
        ranked: list[tuple[int, int, dict[str, Any]]] = []
        for row in rows:
            sku_id = str(row.get("sku_id", ""))
            buy_price = int(row.get("unit_price", 0))
            if buy_price <= 0:
                continue
            best_sell = 0
            for seen_destination_id, entries in self._seen_prices.items():
                if seen_destination_id == destination_id:
                    continue
                best_sell = max(best_sell, int(entries.get(sku_id, {}).get("sell", 0)))
            spread = best_sell - buy_price
            ranked.append((spread, -buy_price, row))
        if not ranked:
            return None
        ranked.sort(reverse=True)
        return ranked[0][2]


def run_playtest(seed: int, turns: int, bias: str, output_dir: str) -> dict[str, Any]:
    seed = int(seed)
    turns = int(turns)
    bias = str(bias).strip().upper()
    if bias != "B":
        raise ValueError("This runner currently supports bias='B' only.")

    engine = GameEngine(world_seed=seed)
    planner = ActionPlanner(seed=seed, bias=bias, scripted_commands=None)
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    transcript_path = output_path / f"playtest_seed_{seed}_transcript.txt"
    events_path = output_path / f"playtest_seed_{seed}_events.json"

    first_profile_result = engine.execute({"type": "get_player_profile"})
    version = str(first_profile_result.get("version", "unknown"))
    player_before = _detail_from_stage(first_profile_result, "player_profile")
    turns_completed = 0
    hard_stop = False
    hard_stop_reason: str | None = None

    with transcript_path.open("w", encoding="utf-8") as transcript, events_path.open("w", encoding="utf-8") as events_file:
        transcript.write("EMOJISPACE PLAYTEST TRANSCRIPT\n")
        transcript.write(f"seed={seed}\n")
        transcript.write(f"turns_requested={turns}\n")
        transcript.write(f"bias={bias}\n")
        transcript.write(f"version={version}\n")
        transcript.write("\n")

        for step in range(1, turns + 1):
            system_profile = _detail_from_stage(engine.execute({"type": "get_system_profile"}), "system_profile")
            destination_profile = _detail_from_stage(engine.execute({"type": "get_destination_profile"}), "destination_profile")
            player_before = _detail_from_stage(engine.execute({"type": "get_player_profile"}), "player_profile")

            planned = planner.choose_command(
                step=step,
                engine=engine,
                player_profile=player_before,
                destination_profile=destination_profile,
                system_profile=system_profile,
            )
            result = engine.execute(planned.command)
            player_after = _detail_from_stage(engine.execute({"type": "get_player_profile"}), "player_profile")
            turns_completed = step
            hard_stop = bool(result.get("hard_stop", False))
            hard_stop_reason = _as_optional_str(result.get("hard_stop_reason"))

            delta = _state_delta(before=player_before, after=player_after)
            planner.note_outcome(command_key=planned.key, changed=delta["changed"])

            transcript.write(f"Step {step}\n")
            transcript.write(f"Command: {json.dumps(planned.command, sort_keys=True)}\n")
            transcript.write(f"Reason: {planned.reason}\n")
            transcript.write(f"Result: {_result_summary(result)}\n")
            transcript.write(f"State Delta: {_delta_line(delta)}\n")
            transcript.write(f"Snapshot: {_snapshot_line(player_after)}\n")

            if _is_in_market(destination_profile=destination_profile, location_id=str(player_after.get("location_id", ""))):
                market_profile = _detail_from_stage(engine.execute({"type": "get_market_profile"}), "market_profile")
                buy_rows = _rows_from_stage(engine.execute({"type": "market_buy_list"}), "market_buy_list")
                sell_rows = _rows_from_stage(engine.execute({"type": "market_sell_list"}), "market_sell_list")
                transcript.write(_market_block(player_after=player_after, market_profile=market_profile, buy_rows=buy_rows, sell_rows=sell_rows))
            transcript.write("\n")

            event_row = {
                "step": int(step),
                "command": planned.command,
                "engine_result": {"ok": bool(result.get("ok")), "error": result.get("error")},
                "turn_before": int(result.get("turn_before", player_before.get("turn", 0))),
                "turn_after": int(result.get("turn_after", player_after.get("turn", 0))),
                "events": result.get("events", []),
            }
            events_file.write(json.dumps(_jsonable(event_row), sort_keys=True) + "\n")

            if hard_stop:
                break

    return {
        "seed": seed,
        "turns_requested": turns,
        "turns_completed": turns_completed,
        "bias": bias,
        "version": version,
        "hard_stop": hard_stop,
        "hard_stop_reason": hard_stop_reason,
        "transcript_path": str(transcript_path),
        "events_path": str(events_path),
    }


def _planned(command: dict[str, Any], reason: str) -> PlannedCommand:
    key = json.dumps(command, sort_keys=True)
    return PlannedCommand(command=command, reason=reason, key=key)


def _step_rng(*, seed: int, step: int, stream: str) -> random.Random:
    token = f"{seed}:{step}:{stream}"
    seed_int = int(hashlib.sha256(token.encode("utf-8")).hexdigest(), 16) % (2**32)
    return random.Random(seed_int)


def _as_optional_str(value: Any) -> str | None:
    if value is None:
        return None
    return str(value)


def _detail_from_stage(result: dict[str, Any], stage: str) -> dict[str, Any]:
    for event in list(result.get("events", [])):
        if not isinstance(event, dict):
            continue
        if event.get("stage") != stage:
            continue
        detail = event.get("detail", {})
        if isinstance(detail, dict):
            return detail
    return {}


def _rows_from_stage(result: dict[str, Any], stage: str) -> list[dict[str, Any]]:
    detail = _detail_from_stage(result, stage)
    rows = detail.get("rows", [])
    if not isinstance(rows, list):
        return []
    return [row for row in rows if isinstance(row, dict)]


def _list_actions(*, engine: GameEngine, command_type: str, stage: str) -> list[dict[str, Any]]:
    detail = _detail_from_stage(engine.execute({"type": command_type}), stage)
    actions = detail.get("actions", [])
    if not isinstance(actions, list):
        return []
    return [entry for entry in actions if isinstance(entry, dict)]


def _market_rows(*, engine: GameEngine, command_type: str) -> list[dict[str, Any]]:
    stage = "market_buy_list" if command_type == "market_buy_list" else "market_sell_list"
    return _rows_from_stage(engine.execute({"type": command_type}), stage)


def _current_location_type(*, destination_profile: dict[str, Any], location_id: str) -> str:
    for row in list(destination_profile.get("locations", [])):
        if not isinstance(row, dict):
            continue
        if str(row.get("location_id", "")) != location_id:
            continue
        return str(row.get("location_type", ""))
    return ""


def _destination_ids_for_system(*, engine: GameEngine, system_id: str) -> list[str]:
    system = engine.sector.get_system(system_id)
    if system is None:
        return []
    return sorted(str(destination.destination_id) for destination in list(system.destinations or []))


def _spread_between_destinations(
    *,
    seen_prices: dict[str, dict[str, dict[str, int]]],
    source_destination_id: str,
    target_destination_id: str,
) -> int:
    source = seen_prices.get(source_destination_id, {})
    target = seen_prices.get(target_destination_id, {})
    best = 0
    for sku_id in set(source).intersection(target):
        buy_price = int(source.get(sku_id, {}).get("buy", 0))
        sell_price = int(target.get(sku_id, {}).get("sell", 0))
        if buy_price <= 0 or sell_price <= 0:
            continue
        best = max(best, sell_price - buy_price)
    return best


def _compact_manifest(manifest: dict[str, Any]) -> str:
    entries = []
    for sku_id, qty in sorted(manifest.items()):
        count = int(qty)
        if count <= 0:
            continue
        entries.append(f"{sku_id}:{count}")
    return ",".join(entries) if entries else "-"


def _state_delta(*, before: dict[str, Any], after: dict[str, Any]) -> dict[str, Any]:
    fields = ["credits", "fuel_current", "turn", "system_id", "destination_id", "location_id"]
    changes: dict[str, tuple[Any, Any]] = {}
    for field in fields:
        prev = before.get(field)
        curr = after.get(field)
        if prev != curr:
            changes[field] = (prev, curr)
    before_manifest = dict(before.get("cargo_manifest", {}))
    after_manifest = dict(after.get("cargo_manifest", {}))
    if before_manifest != after_manifest:
        changes["cargo_manifest"] = (_compact_manifest(before_manifest), _compact_manifest(after_manifest))
    return {"changed": bool(changes), "changes": changes}


def _delta_line(delta: dict[str, Any]) -> str:
    changes = dict(delta.get("changes", {}))
    if not changes:
        return "no_state_change"
    parts = [f"{name}:{prev}->{curr}" for name, (prev, curr) in sorted(changes.items())]
    return "; ".join(parts)


def _snapshot_line(profile: dict[str, Any]) -> str:
    manifest = _compact_manifest(dict(profile.get("cargo_manifest", {})))
    return (
        f"credits={profile.get('credits')} fuel={profile.get('fuel_current')}/{profile.get('fuel_capacity')} "
        f"turn={profile.get('turn')} system_id={profile.get('system_id')} "
        f"destination_id={profile.get('destination_id')} location_id={profile.get('location_id')} "
        f"cargo={manifest}"
    )


def _result_summary(result: dict[str, Any]) -> str:
    ok = bool(result.get("ok"))
    error = result.get("error")
    hard_stop = bool(result.get("hard_stop", False))
    hard_stop_reason = result.get("hard_stop_reason")
    event_count = len(list(result.get("events", [])))
    return (
        f"ok={ok} error={error} hard_stop={hard_stop} "
        f"hard_stop_reason={hard_stop_reason} events={event_count}"
    )


def _is_in_market(*, destination_profile: dict[str, Any], location_id: str) -> bool:
    return _current_location_type(destination_profile=destination_profile, location_id=location_id) == "market"


def _market_block(
    *,
    player_after: dict[str, Any],
    market_profile: dict[str, Any],
    buy_rows: list[dict[str, Any]],
    sell_rows: list[dict[str, Any]],
) -> str:
    lines = []
    lines.append("Market View:")
    lines.append(
        f"  destination_id={market_profile.get('destination_id')} "
        f"primary_economy={market_profile.get('primary_economy_id')} "
        f"active_situations={market_profile.get('active_situations', [])}"
    )
    lines.append(f"  cargo={_compact_manifest(dict(player_after.get('cargo_manifest', {})))}")
    lines.append("  buy_offers:")
    for row in sorted(buy_rows, key=lambda entry: str(entry.get("sku_id", ""))):
        lines.append(
            "    "
            + f"{row.get('sku_id')} price={row.get('unit_price')} legality={row.get('legality')} risk={row.get('risk_tier')}"
        )
    lines.append("  sell_offers:")
    for row in sorted(sell_rows, key=lambda entry: str(entry.get("sku_id", ""))):
        lines.append(
            "    "
            + f"{row.get('sku_id')} units={row.get('player_has_units')} "
            + f"price={row.get('unit_price')} legality={row.get('legality')} risk={row.get('risk_tier')}"
        )
    return "\n".join(lines) + "\n"


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


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Deterministic gameplay playtest runner.")
    parser.add_argument("--seed", type=int, default=12345)
    parser.add_argument("--turns", type=int, default=250)
    parser.add_argument("--bias", type=str, default="B")
    parser.add_argument("--output-dir", type=str, default="tests/output")
    return parser.parse_args()


def main() -> None:
    args = _parse_args()
    summary = run_playtest(
        seed=int(args.seed),
        turns=int(args.turns),
        bias=str(args.bias),
        output_dir=str(args.output_dir),
    )
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
