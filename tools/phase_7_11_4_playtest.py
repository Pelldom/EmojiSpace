from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Set

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"
import sys

if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from game_engine import GameEngine  # type: ignore[import]


@dataclass
class MissionOffer:
    """Detailed record of a discovered mission offer."""
    turn_number: int
    location_type: str
    mission_id: str
    mission_type_id: str
    mission_tier: int
    reward_profile_id: str
    tags: List[str]
    emoji_id: str = ""


@dataclass
class MissionTransition:
    """Record of mission state transition."""
    mission_id: str
    transition_type: str  # "accepted", "completed", "failed", "abandoned"
    turn: int


@dataclass
class PlaytestStats:
    """Comprehensive playtest statistics."""
    seed: int = 12345
    max_turn_seen: int = 0
    
    # Discovery tracking
    discovered_offers: List[MissionOffer] = field(default_factory=list)
    discovered_by_location: Counter[str] = field(default_factory=Counter)
    discovered_by_type: Counter[str] = field(default_factory=Counter)
    
    # Acceptance tracking
    accepted_ids: Set[str] = field(default_factory=set)
    accepted_by_type: Counter[str] = field(default_factory=Counter)
    accepted_by_tier: Counter[int] = field(default_factory=Counter)
    accepted_by_reward_profile: Counter[str] = field(default_factory=Counter)
    acceptance_transitions: List[MissionTransition] = field(default_factory=list)
    
    # Completion tracking
    completed_ids: Set[str] = field(default_factory=set)
    completed_by_type: Counter[str] = field(default_factory=Counter)
    completed_by_tier: Counter[int] = field(default_factory=Counter)
    completed_by_reward_profile: Counter[str] = field(default_factory=Counter)
    completion_transitions: List[MissionTransition] = field(default_factory=list)
    
    # Failure/abandonment tracking
    failed_ids: Set[str] = field(default_factory=set)
    abandoned_ids: Set[str] = field(default_factory=set)
    
    # Reward tracking
    reward_profile_offers: Counter[str] = field(default_factory=Counter)
    hull_voucher_awards: Counter[str] = field(default_factory=Counter)  # By frame (XA/XB/XC/ALN/Generic)
    
    # Alien chain tracking
    alien_offers_seen: int = 0
    alien_accepted: int = 0
    alien_completed: int = 0
    alien_completed_by_stage: Counter[int] = field(default_factory=Counter)
    highest_alien_stage: int = 0
    aln_mission_offered: bool = False
    aln_voucher_awarded: bool = False
    
    # Progression context
    completed_by_tag: Counter[str] = field(default_factory=Counter)
    
    # DataNet validation
    datanet_mission_list_works: bool = False
    datanet_mission_accept_works: bool = False
    
    # Stability
    crashes: int = 0
    softlocks: int = 0
    infinite_loops: int = 0


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


def _record_discovered_mission(
    *,
    engine: GameEngine,
    mission_row: Dict[str, Any],
    location_type: str,
    current_turn: int,
    stats: PlaytestStats,
) -> None:
    """Record a discovered mission offer with full details."""
    mission_id = str(mission_row.get("mission_id", "") or "")
    if not mission_id:
        return
    
    # Check if already recorded
    if any(offer.mission_id == mission_id for offer in stats.discovered_offers):
        return
    
    mission = engine._mission_manager.missions.get(mission_id)  # type: ignore[attr-defined]
    if mission is None:
        return
    
    # Extract mission details
    mission_type_id = str(mission.mission_type) or "unknown"
    mission_tier = int(mission.mission_tier)
    reward_profile_id = str(getattr(mission, "reward_profile_id", "") or "")
    tags = list(getattr(mission, "tags", []) or [])
    emoji_id = str(getattr(mission, "emoji", "") or "")
    
    # Create offer record
    offer = MissionOffer(
        turn_number=current_turn,
        location_type=location_type,
        mission_id=mission_id,
        mission_type_id=mission_type_id,
        mission_tier=mission_tier,
        reward_profile_id=reward_profile_id,
        tags=tags,
        emoji_id=emoji_id,
    )
    
    stats.discovered_offers.append(offer)
    stats.discovered_by_location[location_type] += 1
    stats.discovered_by_type[mission_type_id] += 1
    stats.reward_profile_offers[reward_profile_id] += 1
    
    # Track alien missions
    if "ship:trait_alien" in tags:
        stats.alien_offers_seen += 1
        if mission_id.startswith("alien_series_4") or "finale" in mission_id.lower():
            stats.aln_mission_offered = True


def _maybe_accept_mission(
    *,
    engine: GameEngine,
    mission_row: Dict[str, Any],
    player_profile: Dict[str, Any],
    current_turn: int,
    stats: PlaytestStats,
) -> None:
    """Attempt to accept a mission if conditions are met."""
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

    # Attempt acceptance
    result = engine.execute({"type": "mission_accept", "mission_id": mission_id})
    if not result.get("ok", False):
        return

    stats.accepted_ids.add(mission_id)
    stats.accepted_by_type[str(mission.mission_type)] += 1
    stats.accepted_by_tier[int(mission.mission_tier)] += 1
    reward_profile_id = str(getattr(mission, "reward_profile_id", "") or "")
    if reward_profile_id:
        stats.accepted_by_reward_profile[reward_profile_id] += 1
    
    stats.acceptance_transitions.append(
        MissionTransition(mission_id=mission_id, transition_type="accepted", turn=current_turn)
    )
    
    # Track alien missions
    tags = list(getattr(mission, "tags", []) or [])
    if "ship:trait_alien" in tags:
        stats.alien_accepted += 1


def _visit_mission_location(
    *,
    engine: GameEngine,
    location_id: str,
    location_type: str,
    player_profile: Dict[str, Any],
    current_turn: int,
    stats: PlaytestStats,
) -> None:
    """Visit a location and interact with missions."""
    # Enter location
    engine.execute({"type": "enter_location", "location_id": location_id})

    # Determine action based on location type
    if location_type == "administration":
        list_result = engine.execute({"type": "location_action", "action_id": "admin_mission_board"})
        missions = _rows_from_stage(list_result, stage="location_action", subsystem="mission")
    elif location_type == "bar":
        list_result = engine.execute({"type": "location_action", "action_id": "mission_list"})
        missions = _rows_from_stage(list_result, stage="location_action", subsystem="mission")
    elif location_type == "datanet":
        # Phase 7.11.4: Test datanet mission_list
        try:
            list_result = engine.execute({"type": "location_action", "action_id": "mission_list"})
            stats.datanet_mission_list_works = True
            missions = _rows_from_stage(list_result, stage="location_action", subsystem="mission")
        except Exception as e:
            missions = []
    else:
        missions = []

    # Record discovered missions
    for row in missions:
        mission_id = str(row.get("mission_id", "") or "")
        if not mission_id:
            continue
        _record_discovered_mission(
            engine=engine,
            mission_row=row,
            location_type=location_type,
            current_turn=current_turn,
            stats=stats,
        )
        _maybe_accept_mission(
            engine=engine,
            mission_row=row,
            player_profile=player_profile,
            current_turn=current_turn,
            stats=stats,
        )
        
        # Test datanet mission_accept if applicable
        if location_type == "datanet" and mission_id in stats.accepted_ids:
            stats.datanet_mission_accept_works = True

    # Return to destination root after interactions
    engine.execute({"type": "return_to_destination"})


def _destination_ids_for_system(engine: GameEngine, system_id: str) -> List[str]:
    system = engine.sector.get_system(system_id)
    if system is None:
        return []
    return sorted(str(destination.destination_id) for destination in list(system.destinations or []))


def _travel_toward_active_mission(engine: GameEngine) -> bool:
    """Travel toward the first active mission target, if any."""
    mm = engine._mission_manager  # type: ignore[attr-defined]
    for mission in mm.missions.values():
        if str(mission.mission_state) not in ("ACTIVE", "active"):
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

    engine.execute({"type": "wait", "days": 1})


def _update_completed_stats(engine: GameEngine, stats: PlaytestStats, current_turn: int) -> None:
    """Scan mission manager for newly completed/failed missions and update stats."""
    mm = engine._mission_manager  # type: ignore[attr-defined]
    for mission in mm.missions.values():
        mission_id = str(mission.mission_id)
        
        # Check completion
        if str(mission.mission_state) == "RESOLVED":
            outcome = str(getattr(mission, "outcome", "") or "")
            
            if outcome in ("COMPLETED", "MissionOutcome.COMPLETED", "completed"):
                if mission_id not in stats.completed_ids:
                    stats.completed_ids.add(mission_id)
                    stats.completed_by_type[str(mission.mission_type)] += 1
                    stats.completed_by_tier[int(mission.mission_tier)] += 1
                    reward_profile_id = str(getattr(mission, "reward_profile_id", "") or "")
                    if reward_profile_id:
                        stats.completed_by_reward_profile[reward_profile_id] += 1
                    
                    stats.completion_transitions.append(
                        MissionTransition(mission_id=mission_id, transition_type="completed", turn=current_turn)
                    )
                    
                    # Track alien completions
                    tags = list(getattr(mission, "tags", []) or [])
                    if "ship:trait_alien" in tags:
                        stats.alien_completed += 1
                        # Determine stage from mission_id
                        if "alien_series_1" in mission_id or "series_1" in mission_id:
                            stats.alien_completed_by_stage[1] += 1
                            stats.highest_alien_stage = max(stats.highest_alien_stage, 1)
                        elif "alien_series_2" in mission_id or "series_2" in mission_id:
                            stats.alien_completed_by_stage[2] += 1
                            stats.highest_alien_stage = max(stats.highest_alien_stage, 2)
                        elif "alien_series_3" in mission_id or "series_3" in mission_id:
                            stats.alien_completed_by_stage[3] += 1
                            stats.highest_alien_stage = max(stats.highest_alien_stage, 3)
                        elif "alien_series_4" in mission_id or "finale" in mission_id.lower():
                            stats.alien_completed_by_stage[4] += 1
                            stats.highest_alien_stage = max(stats.highest_alien_stage, 4)
                            if reward_profile_id == "mission_hull_voucher_aln":
                                stats.aln_voucher_awarded = True
                    
                    # Track completed missions by tag for progression context
                    for tag in tags:
                        stats.completed_by_tag[tag] += 1
                    
                    # Track hull voucher awards (if reward was granted)
                    if "hull_voucher" in reward_profile_id:
                        # Extract frame from reward_profile_id
                        if "_xa" in reward_profile_id.lower():
                            stats.hull_voucher_awards["XA"] += 1
                        elif "_xb" in reward_profile_id.lower():
                            stats.hull_voucher_awards["XB"] += 1
                        elif "_xc" in reward_profile_id.lower():
                            stats.hull_voucher_awards["XC"] += 1
                        elif "_aln" in reward_profile_id.lower():
                            stats.hull_voucher_awards["ALN"] += 1
                        elif "generic" in reward_profile_id.lower():
                            stats.hull_voucher_awards["Generic"] += 1
            
            elif outcome in ("FAILED", "MissionOutcome.FAILED", "failed"):
                if mission_id not in stats.failed_ids:
                    stats.failed_ids.add(mission_id)
                    stats.completion_transitions.append(
                        MissionTransition(mission_id=mission_id, transition_type="failed", turn=current_turn)
                    )
            
            elif outcome in ("ABANDONED", "MissionOutcome.ABANDONED", "abandoned"):
                if mission_id not in stats.abandoned_ids:
                    stats.abandoned_ids.add(mission_id)
                    stats.completion_transitions.append(
                        MissionTransition(mission_id=mission_id, transition_type="abandoned", turn=current_turn)
                    )


def run_playtest(seed: int, max_turns: int) -> PlaytestStats:
    """Run the playtest and collect statistics."""
    engine = GameEngine(world_seed=int(seed))
    stats = PlaytestStats(seed=int(seed))
    
    consecutive_no_progress = 0
    last_turn = 0
    
    while True:
        try:
            # Snapshot current state
            system_result = engine.execute({"type": "get_system_profile"})
            destination_result = engine.execute({"type": "get_destination_profile"})
            player_result = engine.execute({"type": "get_player_profile"})

            system_profile = _detail_from_stage(system_result, "system_profile")
            destination_profile = _detail_from_stage(destination_result, "destination_profile")
            player_profile = _detail_from_stage(player_result, "player_profile")

            current_turn = int(player_profile.get("turn", 0) or 0)
            stats.max_turn_seen = max(stats.max_turn_seen, current_turn)
            
            # Check for infinite loops
            if current_turn == last_turn:
                consecutive_no_progress += 1
                if consecutive_no_progress > 10:
                    stats.infinite_loops += 1
                    break
            else:
                consecutive_no_progress = 0
                last_turn = current_turn
            
            if current_turn >= max_turns:
                break

            location_id = str(player_profile.get("location_id", "") or "")
            destination_id = str(player_profile.get("destination_id", "") or "")

            # If not at destination root, return there first
            if location_id and destination_id and location_id != destination_id:
                engine.execute({"type": "return_to_destination"})
                continue

            # Visit all mission locations (Administration, Bar, DataNet)
            locations = list(destination_profile.get("locations", []))
            for row in locations:
                if not isinstance(row, dict):
                    continue
                loc_type = str(row.get("location_type", "") or "")
                loc_id = str(row.get("location_id", "") or "")
                if loc_type in ("administration", "bar", "datanet"):
                    _visit_mission_location(
                        engine=engine,
                        location_id=loc_id,
                        location_type=loc_type,
                        player_profile=player_profile,
                        current_turn=current_turn,
                        stats=stats,
                    )

            # Try to advance or complete active missions via travel
            if not _travel_toward_active_mission(engine):
                _simple_exploration_travel(engine, destination_profile=destination_profile, system_profile=system_profile)

            # After actions, update completion stats
            _update_completed_stats(engine, stats, current_turn)
            
        except Exception as e:
            stats.crashes += 1
            print(f"Error at turn {stats.max_turn_seen}: {e}")
            break

    return stats


def generate_report(stats: PlaytestStats) -> str:
    """Generate the structured markdown report."""
    lines = []
    lines.append("=" * 78)
    lines.append("PHASE 7.11.4 PLAYTEST REPORT (POST-FIX)")
    lines.append(f"Seed: {stats.seed}")
    lines.append(f"Turns: {stats.max_turn_seen}")
    lines.append("=" * 78)
    lines.append("")
    
    # 1) Mission Discovery Summary
    lines.append("1) Mission Discovery Summary")
    lines.append("-" * 78)
    lines.append(f"- Total offers by location:")
    for loc_type, count in stats.discovered_by_location.most_common():
        lines.append(f"  - {loc_type}: {count}")
    lines.append(f"- Offers by mission_type_id:")
    for mission_type, count in stats.discovered_by_type.most_common():
        lines.append(f"  - {mission_type}: {count}")
    lines.append("")
    
    # 2) Mission Acceptance Summary
    lines.append("2) Mission Acceptance Summary")
    lines.append("-" * 78)
    lines.append(f"- Accepted by type:")
    for mission_type, count in stats.accepted_by_type.most_common():
        lines.append(f"  - {mission_type}: {count}")
    lines.append(f"- Accepted by tier:")
    for tier, count in sorted(stats.accepted_by_tier.items()):
        lines.append(f"  - Tier {tier}: {count}")
    lines.append(f"- Accepted by reward_profile_id (top 10):")
    for profile_id, count in stats.accepted_by_reward_profile.most_common(10):
        lines.append(f"  - {profile_id}: {count}")
    lines.append("")
    
    # 3) Mission Completion Summary
    lines.append("3) Mission Completion Summary")
    lines.append("-" * 78)
    lines.append(f"- Completed by type:")
    for mission_type, count in stats.completed_by_type.most_common():
        lines.append(f"  - {mission_type}: {count}")
    lines.append(f"- Completed by reward_profile_id:")
    for profile_id, count in stats.completed_by_reward_profile.most_common():
        lines.append(f"  - {profile_id}: {count}")
    lines.append(f"- Completed by tier:")
    for tier, count in sorted(stats.completed_by_tier.items()):
        lines.append(f"  - Tier {tier}: {count}")
    lines.append(f"- Totals: Completed={len(stats.completed_ids)}, Failed={len(stats.failed_ids)}, Abandoned={len(stats.abandoned_ids)}")
    lines.append("")
    
    # 4) Reward Variety Verification
    lines.append("4) Reward Variety Verification")
    lines.append("-" * 78)
    credits_offers = sum(1 for p in stats.reward_profile_offers if "credits" in p.lower())
    goods_offers = sum(1 for p in stats.reward_profile_offers if "goods" in p.lower())
    module_offers = sum(1 for p in stats.reward_profile_offers if "module" in p.lower())
    hull_voucher_offers = sum(1 for p in stats.reward_profile_offers if "hull_voucher" in p.lower())
    lines.append(f"- Credits offers: {credits_offers}")
    lines.append(f"- Goods offers: {goods_offers}")
    for profile_id, count in stats.reward_profile_offers.most_common():
        if "goods" in profile_id.lower():
            lines.append(f"  - {profile_id}: {count}")
    lines.append(f"- Module offers: {module_offers}")
    for profile_id, count in stats.reward_profile_offers.most_common():
        if "module" in profile_id.lower():
            lines.append(f"  - {profile_id}: {count}")
    lines.append(f"- Hull voucher offers: {hull_voucher_offers}")
    for profile_id, count in stats.reward_profile_offers.most_common():
        if "hull_voucher" in profile_id.lower():
            lines.append(f"  - {profile_id}: {count}")
    lines.append(f"- Hull voucher AWARDS:")
    for frame, count in stats.hull_voucher_awards.most_common():
        lines.append(f"  - {frame}: {count}")
    lines.append("")
    
    # 5) Alien Chain Analysis
    lines.append("5) Alien Chain Analysis")
    lines.append("-" * 78)
    lines.append(f"- Alien-tagged offers seen: {stats.alien_offers_seen}")
    lines.append(f"- Alien-tagged accepted: {stats.alien_accepted}")
    lines.append(f"- Alien-tagged completed: {stats.alien_completed}")
    lines.append(f"- Completed by stage:")
    for stage, count in sorted(stats.alien_completed_by_stage.items()):
        lines.append(f"  - Stage {stage}: {count}")
    lines.append(f"- Highest alien stage unlocked: {stats.highest_alien_stage}")
    lines.append(f"- ALN mission offered? {'yes' if stats.aln_mission_offered else 'no'}")
    lines.append(f"- ALN voucher awarded? {'yes' if stats.aln_voucher_awarded else 'no'}")
    lines.append("")
    
    # 6) DataNet Validation
    lines.append("6) DataNet Validation")
    lines.append("-" * 78)
    lines.append(f"- mission_list works: {'yes' if stats.datanet_mission_list_works else 'no'}")
    lines.append(f"- mission_accept works: {'yes' if stats.datanet_mission_accept_works else 'no'}")
    lines.append("")
    
    # 7) Observed Issues
    lines.append("7) Observed Issues")
    lines.append("-" * 78)
    expected_types = {"delivery", "bounty", "patrol", "smuggling", "exploration", "retrieval"}
    seen_types = set(stats.discovered_by_type.keys())
    missing_types = expected_types - seen_types
    if missing_types:
        lines.append(f"- Mission types never appearing: {', '.join(sorted(missing_types))}")
    else:
        lines.append("- All expected mission types appeared")
    
    # Check for incorrect hull voucher profiles
    issues = []
    for offer in stats.discovered_offers:
        if "hull_voucher_xa" in offer.reward_profile_id and offer.mission_type_id != "smuggling":
            issues.append(f"XA voucher in {offer.mission_type_id} mission (should only be in smuggling)")
        if "hull_voucher_xb" in offer.reward_profile_id and offer.mission_type_id not in ("bounty", "patrol"):
            issues.append(f"XB voucher in {offer.mission_type_id} mission (should only be in bounty/patrol)")
        if "hull_voucher_xc" in offer.reward_profile_id and offer.mission_type_id not in ("bounty", "patrol", "exploration"):
            issues.append(f"XC voucher in {offer.mission_type_id} mission (should only be in bounty/patrol/exploration)")
        if "hull_voucher_generic" in offer.reward_profile_id and offer.mission_type_id != "delivery":
            issues.append(f"Generic voucher in {offer.mission_type_id} mission (should only be in delivery T4)")
        if "hull_voucher_aln" in offer.reward_profile_id and offer.mission_type_id not in ("delivery", "retrieval"):
            issues.append(f"ALN voucher in {offer.mission_type_id} mission (should only be in alien finale)")
    
    if issues:
        for issue in issues:
            lines.append(f"- {issue}")
    else:
        lines.append("- No incorrect hull voucher profile assignments observed")
    lines.append("")
    
    # 8) Stability
    lines.append("8) Stability")
    lines.append("-" * 78)
    lines.append(f"- Crashes? {'yes' if stats.crashes > 0 else 'no'} ({stats.crashes})")
    lines.append(f"- Softlocks? {'yes' if stats.softlocks > 0 else 'no'} ({stats.softlocks})")
    lines.append(f"- Infinite loops? {'yes' if stats.infinite_loops > 0 else 'no'} ({stats.infinite_loops})")
    lines.append("")
    
    lines.append("END")
    lines.append("")
    lines.append("Note: This report contains only observed data from the playtest run.")
    
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run Phase 7.11.4 post-fix playtest and generate structured report."
    )
    parser.add_argument("--seed", type=int, default=12345, help="World seed (default: 12345)")
    parser.add_argument("--turns", type=int, default=100, help="Target turn count (default: 100)")
    parser.add_argument(
        "--output",
        type=str,
        default="docs/100_turn_test.md",
        help="Output markdown report path (default: docs/100_turn_test.md)",
    )
    args = parser.parse_args()

    project_root = Path(__file__).resolve().parents[1]
    output_path = (project_root / args.output).resolve()

    print(f"Running playtest: seed={args.seed}, turns={args.turns}")
    stats = run_playtest(seed=args.seed, max_turns=args.turns)
    
    report = generate_report(stats)
    
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as f:
        f.write(report)
    
    print(f"\nReport written to: {output_path}")
    print("\n" + "=" * 78)
    print("QUICK SUMMARY")
    print("=" * 78)
    print(f"Turns completed: {stats.max_turn_seen}")
    print(f"Mission types discovered: {len(stats.discovered_by_type)}")
    print(f"Missions accepted: {len(stats.accepted_ids)}")
    print(f"Missions completed: {len(stats.completed_ids)}")
    print(f"Alien missions seen: {stats.alien_offers_seen}")
    print(f"Highest alien stage: {stats.highest_alien_stage}")


if __name__ == "__main__":
    main()
