from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Set

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"
import sys

if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from game_engine import GameEngine  # type: ignore[import]


@dataclass
class MissionStats:
    max_turn_seen: int = 0
    seed: int = 0

    # Discovery
    discovered_ids: Set[str] | None = None
    discovered_by_location_type: Counter[str] | None = None
    discovered_by_type: Counter[str] | None = None

    # Acceptance
    accepted_ids: Set[str] | None = None
    accepted_by_type: Counter[str] | None = None
    accepted_by_tier: Counter[int] | None = None
    accepted_by_reward_profile: Counter[str] | None = None

    # Completion
    completed_ids: Set[str] | None = None
    completed_by_type: Counter[str] | None = None
    completed_by_tier: Counter[int] | None = None
    completed_by_reward_profile: Counter[str] | None = None

    def __post_init__(self) -> None:
        self.discovered_ids = set()
        self.discovered_by_location_type = Counter()
        self.discovered_by_type = Counter()

        self.accepted_ids = set()
        self.accepted_by_type = Counter()
        self.accepted_by_tier = Counter()
        self.accepted_by_reward_profile = Counter()

        self.completed_ids = set()
        self.completed_by_type = Counter()
        self.completed_by_tier = Counter()
        self.completed_by_reward_profile = Counter()


def _detail_from_stage(result: Dict[str, Any], stage: str, subsystem: str | None = None) -> Dict[str, Any]:
    """Extract detail payload for a given stage (and optional subsystem) from engine.execute result."""
    for event in list(result.get("events", [])):
        if not isinstance(event, dict):
            continue
        if event.get("stage") != stage:
            continue
        if subsystem is not None and event.get("subsystem") != subsystem:
            continue
        detail = event.get("detail", {})
        if isinstance(detail, dict):
            return detail
    return {}


def _rows_from_stage(result: Dict[str, Any], stage: str, subsystem: str | None = None) -> List[Dict[str, Any]]:
    detail = _detail_from_stage(result, stage, subsystem=subsystem)
    rows = detail.get("rows") or detail.get("missions") or []
    if not isinstance(rows, list):
        return []
    return [row for row in rows if isinstance(row, dict)]


def _destination_ids_for_system(engine: GameEngine, system_id: str) -> List[str]:
    system = engine.sector.get_system(system_id)
    if system is None:
        return []
    return sorted(str(destination.destination_id) for destination in list(system.destinations or []))


def _record_discovered_mission(
    *,
    engine: GameEngine,
    mission_id: str,
    location_type: str,
    stats: MissionStats,
) -> None:
    if mission_id in stats.discovered_ids:
        return
    mission = engine._mission_manager.missions.get(mission_id)  # type: ignore[attr-defined]
    if mission is None:
        return
    stats.discovered_ids.add(mission_id)
    stats.discovered_by_location_type[location_type] += 1  # type: ignore[index]
    stats.discovered_by_type[str(mission.mission_type)] += 1  # type: ignore[index]


def _maybe_accept_mission(
    *,
    engine: GameEngine,
    mission_row: Dict[str, Any],
    player_profile: Dict[str, Any],
    stats: MissionStats,
) -> None:
    mission_id = str(mission_row.get("mission_id", "") or "")
    if not mission_id or mission_id in stats.accepted_ids:
        return

    mission = engine._mission_manager.missions.get(mission_id)  # type: ignore[attr-defined]
    if mission is None:
        return

    # Simple capability heuristic: allow missions up to ship_tier + 1
    ship_info = player_profile.get("ship", {})
    ship_tier = int(ship_info.get("tier", 1) or 1)
    mission_tier = int(mission.mission_tier)
    if mission_tier > ship_tier + 1:
        return

    # Respect mission slot capacity if available
    max_slots = int(player_profile.get("mission_slots", 3) or 3)
    active_ids = list(player_profile.get("active_missions", []))
    if len(active_ids) >= max_slots:
        return

    # Attempt acceptance via mission_accept command (uses MissionCore & MissionManager)
    result = engine.execute({"type": "mission_accept", "mission_id": mission_id})
    if not result.get("ok", False):
        return

    stats.accepted_ids.add(mission_id)
    stats.accepted_by_type[str(mission.mission_type)] += 1  # type: ignore[index]
    stats.accepted_by_tier[int(mission.mission_tier)] += 1  # type: ignore[index]
    reward_profile_id = str(getattr(mission, "reward_profile_id", "") or "")
    if reward_profile_id:
        stats.accepted_by_reward_profile[reward_profile_id] += 1  # type: ignore[index]


def _visit_mission_location(
    *,
    engine: GameEngine,
    location_id: str,
    location_type: str,
    player_profile: Dict[str, Any],
    stats: MissionStats,
) -> None:
    # Enter location
    engine.execute({"type": "enter_location", "location_id": location_id})

    # Administration uses admin_mission_board; Bar uses mission_list.
    if location_type == "administration":
        list_result = engine.execute({"type": "location_action", "action_id": "admin_mission_board"})
        missions = _rows_from_stage(list_result, stage="location_action", subsystem="mission")
    elif location_type == "bar":
        list_result = engine.execute({"type": "location_action", "action_id": "mission_list"})
        missions = _rows_from_stage(list_result, stage="location_action", subsystem="mission")
    else:
        missions = []

    for row in missions:
        mission_id = str(row.get("mission_id", "") or "")
        if not mission_id:
            continue
        _record_discovered_mission(engine=engine, mission_id=mission_id, location_type=location_type, stats=stats)
        _maybe_accept_mission(engine=engine, mission_row=row, player_profile=player_profile, stats=stats)

    # Return to destination root after interactions
    engine.execute({"type": "return_to_destination"})


def _travel_toward_active_mission(engine: GameEngine) -> bool:
    """Travel toward the first active delivery mission target, if any."""
    mm = engine._mission_manager  # type: ignore[attr-defined]
    for mission in mm.missions.values():
        if str(mission.mission_type) != "delivery":
            continue
        if str(mission.mission_state) != "ACTIVE":
            continue
        target = getattr(mission, "target", {}) or {}
        target_system_id = str(target.get("system_id", "") or "")
        target_destination_id = str(target.get("target_id", "") or "")
        if not target_system_id or not target_destination_id:
            continue
        engine.execute(
            {
                "type": "travel_to_destination",
                "target_system_id": target_system_id,
                "target_destination_id": target_destination_id,
            }
        )
        return True
    return False


def _simple_exploration_travel(engine: GameEngine, destination_profile: Dict[str, Any], system_profile: Dict[str, Any]) -> None:
    """Fallback travel behavior when there is no active mission."""
    # Try intra-system travel first
    destination_id = str(destination_profile.get("destination_id", "") or "")
    system_id = str(destination_profile.get("system_id", "") or "")
    if system_id:
        intra_ids = _destination_ids_for_system(engine=engine, system_id=system_id)
        for dest_id in intra_ids:
            if dest_id == destination_id:
                continue
            engine.execute(
                {
                    "type": "travel_to_destination",
                    "target_system_id": system_id,
                    "target_destination_id": dest_id,
                }
            )
            return

    # Otherwise try first reachable system
    reachable = [
        row
        for row in list(system_profile.get("reachable_systems", []))
        if isinstance(row, dict) and bool(row.get("in_range"))
    ]
    if reachable:
        target_row = sorted(reachable, key=lambda r: str(r.get("system_id", "")))[0]
        target_system_id = str(target_row.get("system_id", "") or "")
        dest_ids = _destination_ids_for_system(engine=engine, system_id=target_system_id)
        if dest_ids:
            engine.execute(
                {
                    "type": "travel_to_destination",
                    "target_system_id": target_system_id,
                    "target_destination_id": dest_ids[0],
                }
            )
            return

    # Final fallback: wait 1 day
    engine.execute({"type": "wait", "days": 1})


def _update_completed_stats(engine: GameEngine, stats: MissionStats) -> None:
    """Scan mission manager for newly completed missions and update stats."""
    mm = engine._mission_manager  # type: ignore[attr-defined]
    for mission in mm.missions.values():
        mission_id = str(mission.mission_id)
        if mission_id in stats.completed_ids:
            continue
        # MissionState and outcome are enums; compare string values
        if str(mission.mission_state) != "RESOLVED":
            continue
        if str(getattr(mission, "outcome", "")) != "MissionOutcome.COMPLETED" and str(
            getattr(mission, "outcome", "")
        ) != "COMPLETED":
            # Be tolerant to different enum string formats
            continue

        stats.completed_ids.add(mission_id)
        stats.completed_by_type[str(mission.mission_type)] += 1  # type: ignore[index]
        stats.completed_by_tier[int(mission.mission_tier)] += 1  # type: ignore[index]
        reward_profile_id = str(getattr(mission, "reward_profile_id", "") or "")
        if reward_profile_id:
            stats.completed_by_reward_profile[reward_profile_id] += 1  # type: ignore[index]


def run_mission_playtest(seed: int, max_turns: int, output_path: Path) -> Dict[str, Any]:
    engine = GameEngine(world_seed=int(seed))
    stats = MissionStats(seed=int(seed))

    output_path.parent.mkdir(parents=True, exist_ok=True)

    while True:
        # Snapshot current state
        system_result = engine.execute({"type": "get_system_profile"})
        destination_result = engine.execute({"type": "get_destination_profile"})
        player_result = engine.execute({"type": "get_player_profile"})

        system_profile = _detail_from_stage(system_result, "system_profile")
        destination_profile = _detail_from_stage(destination_result, "destination_profile")
        player_profile = _detail_from_stage(player_result, "player_profile")

        current_turn = int(player_profile.get("turn", 0) or 0)
        stats.max_turn_seen = max(stats.max_turn_seen, current_turn)
        if current_turn >= max_turns:
            break

        location_id = str(player_profile.get("location_id", "") or "")
        destination_id = str(player_profile.get("destination_id", "") or "")

        # If not at destination root, return there first
        if location_id and destination_id and location_id != destination_id:
            engine.execute({"type": "return_to_destination"})
            continue

        # Visit Administration and Bar (if present) to interact with missions
        locations = list(destination_profile.get("locations", []))
        for row in locations:
            if not isinstance(row, dict):
                continue
            loc_type = str(row.get("location_type", "") or "")
            loc_id = str(row.get("location_id", "") or "")
            if loc_type not in ("administration", "bar"):
                continue
            _visit_mission_location(
                engine=engine,
                location_id=loc_id,
                location_type=loc_type,
                player_profile=player_profile,
                stats=stats,
            )

        # Try to advance or complete active missions via travel
        if not _travel_toward_active_mission(engine):
            _simple_exploration_travel(engine, destination_profile=destination_profile, system_profile=system_profile)

        # After actions, update completion stats
        _update_completed_stats(engine, stats)

    summary: Dict[str, Any] = {
        "seed": stats.seed,
        "max_turn_seen": stats.max_turn_seen,
        "requested_turns": max_turns,
        "missions": {
            "discovered_by_location": dict(stats.discovered_by_location_type),
            "discovered_by_type": dict(stats.discovered_by_type),
            "accepted_by_type": dict(stats.accepted_by_type),
            "accepted_by_tier": dict(stats.accepted_by_tier),
            "accepted_by_reward_profile": dict(stats.accepted_by_reward_profile),
            "completed_by_type": dict(stats.completed_by_type),
            "completed_by_tier": dict(stats.completed_by_tier),
            "completed_by_reward_profile": dict(stats.completed_by_reward_profile),
        },
    }

    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(summary, handle, indent=2, sort_keys=True)

    return summary


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Run a non-interactive mission-focused playtest and emit a JSON summary.\n"
            "This harness uses only public GameEngine commands and does not modify game logic."
        )
    )
    parser.add_argument("--seed", type=int, default=12345, help="World seed (default: 12345)")
    parser.add_argument("--turns", type=int, default=100, help="Target turn count (default: 100)")
    parser.add_argument(
        "--output",
        type=str,
        default="test/output/mission_playtest_seed_12345.json",
        help="Output JSON path (default: test/output/mission_playtest_seed_12345.json)",
    )
    args = parser.parse_args()

    project_root = Path(__file__).resolve().parents[1]
    output_path = (project_root / args.output).resolve()

    summary = run_mission_playtest(seed=args.seed, max_turns=args.turns, output_path=output_path)
    print(json.dumps(summary, indent=2, sort_keys=True))
    print(f"\nSummary written to: {output_path}")


if __name__ == "__main__":
    main()

