from __future__ import annotations

import argparse
import contextlib
import io
import json
import math
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

# Ensure src directory is on path for imports when running as module
try:
    _src_dir = Path(__file__).resolve().parent
except NameError:
    # __file__ not defined (e.g., in interactive mode)
    _src_dir = Path.cwd() / "src"
if str(_src_dir) not in sys.path:
    sys.path.insert(0, str(_src_dir))

from game_engine import GameEngine
from logger import Logger, LogEntry
from time_engine import get_current_turn
from emoji_profile_builder import build_emoji_profile, build_emoji_profile_parts
from types import SimpleNamespace


# Global context for playtest logging (set in main())
_playtest_context: Dict[str, Any] = {}


def _format_result(result: Dict[str, Any], action_type: str = "action") -> None:
    """
    Format engine result for player-facing output.
    
    In verbose mode, shows full JSON. Otherwise, shows clean summary.
    """
    verbose = _playtest_context.get("verbose", False)
    playtest_logger = _playtest_context.get("playtest_logger")
    
    # Record action for Markdown
    if playtest_logger:
        turn = get_current_turn()
        playtest_logger.record_action(turn, action_type, result)
    
    if verbose:
        print(json.dumps(result, sort_keys=True, indent=2))
    else:
        # Clean player-facing output
        if result.get("ok"):
            # Success - show minimal feedback
            detail = result.get("detail", {})
            if isinstance(detail, dict):
                # Show key information from detail
                if "message" in detail:
                    print(detail["message"])
                elif "state_change" in detail:
                    print(f"✓ {detail['state_change']}")
        else:
            # Error - show error message
            error = result.get("error", "unknown_error")
            print(f"✗ Error: {error}")


# Global flag to suppress logger console output
_logger_console_suppressed = False


@contextlib.contextmanager
def _suppress_logger_console():
    """Context manager to suppress Logger print output while preserving file logging."""
    global _logger_console_suppressed
    old_suppress = _logger_console_suppressed
    _logger_console_suppressed = True
    try:
        # Monkey-patch Logger.log to check suppression flag
        original_log = Logger.log
        
        def suppressed_log(self, turn: int, action: str, state_change: str) -> None:
            entry = LogEntry(
                turn=turn,
                version=self._version,
                action=action,
                state_change=state_change,
            )
            line = entry.format_line()
            # Only print if not suppressed
            if not _logger_console_suppressed:
                print(line)
            # Always write to file if enabled
            if self._file_enabled and isinstance(self._file_path, str):
                try:
                    with open(self._file_path, "a", encoding="ascii", errors="replace") as handle:
                        handle.write(line)
                        handle.write("\n")
                except Exception:  # noqa: BLE001
                    pass
        
        Logger.log = suppressed_log
        yield
    finally:
        Logger.log = original_log
        _logger_console_suppressed = old_suppress


# ============================================================================
# NAME RESOLUTION HELPERS (Part 1: Display Names, Not IDs)
# ============================================================================

def _format_name_with_profile(entity: object, name: str, visible: bool) -> str:
    """
    Return name only, or 'name  profile' when visible and profile available.
    Entity may be an object with .emoji_id, .tier, .tags or a dict with those keys.
    Failsafe: on any error or missing profile, return name only. No placeholder glyph.
    """
    if not visible:
        return name
    try:
        if isinstance(entity, dict):
            entity = SimpleNamespace(
                emoji_id=entity.get("emoji_id"),
                tier=entity.get("tier"),
                tags=entity.get("tags") or [],
            )
        profile = build_emoji_profile(entity)
    except Exception:
        return name
    if not profile:
        return name
    return f"{name}  {profile}"


def _format_good_name_with_profile(good_or_row: object, name: str, visible: bool = True) -> str:
    """
    Format goods as [category emoji] Name [secondary emoji...].
    good_or_row: Good instance or dict with category and tags.
    If nothing resolves, return plain name.
    """
    if not visible or not name:
        return name or ""
    try:
        if isinstance(good_or_row, dict):
            category = good_or_row.get("category")
            tags = good_or_row.get("tags") or []
        else:
            category = getattr(good_or_row, "category", None)
            tags = getattr(good_or_row, "tags", None) or []
        entity = SimpleNamespace(category=category, tags=tags)
        primary, _, secondary = build_emoji_profile_parts(entity)
        parts = []
        if primary:
            parts.append(primary)
        parts.append(name)
        parts.extend(secondary)
        result = " ".join(parts).strip()
        return result if result else name
    except Exception:
        return name


def _get_good_display_name(engine: GameEngine, sku_id: str) -> str:
    """Resolve sku_id to good display string: [category] Name [tags]. Falls back to plain name on error."""
    if not sku_id:
        return "Unknown Good"
    try:
        from data_catalog import load_data_catalog
        catalog = load_data_catalog()
        good = catalog.good_by_sku(sku_id)
        return _format_good_name_with_profile(good, good.name, True)
    except (KeyError, Exception):  # noqa: BLE001
        return sku_id


def _get_system_name(engine: GameEngine, system_id: str) -> str:
    """Resolve system_id to system name."""
    if not system_id:
        return "Unknown System"
    system = engine.sector.get_system(system_id)
    if system:
        return system.name
    return system_id  # Fallback to ID if system not found


def _get_destination_name(engine: GameEngine, destination_id: str | None) -> str:
    """Resolve destination_id to destination display_name."""
    if not destination_id:
        return "Unknown Destination"
    # Find destination in sector
    for system in engine.sector.systems:
        for destination in system.destinations:
            if destination.destination_id == destination_id:
                return destination.display_name
    return destination_id  # Fallback to ID if destination not found


def _get_destination_object(engine: GameEngine, destination_id: str | None) -> object | None:
    """Return destination object for destination_id, or None if not found."""
    if not destination_id:
        return None
    for system in engine.sector.systems:
        for destination in system.destinations:
            if destination.destination_id == destination_id:
                return destination
    return None


def _get_npc_name(engine: GameEngine, npc_id: str | None) -> str:
    """Resolve npc_id to NPC display_name."""
    if not npc_id:
        return "Unknown NPC"
    # Try to get NPC from registry
    try:
        npc_registry = getattr(engine, "_npc_registry", None)
        if npc_registry:
            npc = npc_registry.get_npc(npc_id)
            if npc:
                return getattr(npc, "display_name", npc_id)
    except Exception:  # noqa: BLE001
        pass
    return npc_id  # Fallback to ID if NPC not found


def _get_good_name(engine: GameEngine, sku_id: str) -> str:
    """Resolve sku_id to good name (plain). For display with emoji profile use _get_good_display_name."""
    if not sku_id:
        return "Unknown Good"
    try:
        from data_catalog import load_data_catalog
        catalog = load_data_catalog()
        good = catalog.good_by_sku(sku_id)
        return good.name
    except (KeyError, Exception):  # noqa: BLE001
        return sku_id  # Fallback to ID if good not found


def _format_mission_objectives(engine: GameEngine, mission: Dict[str, Any]) -> List[str]:
    """
    Format mission objectives for display (Part 2 & 3).
    
    Returns list of objective description strings.
    """
    objectives = mission.get("objectives", [])
    if not objectives:
        return ["No objectives specified"]
    
    # Get target destination from mission if not in objective parameters
    # Target is stored as: {"target_type": "destination", "target_id": destination_id, "system_id": system_id}
    mission_target = mission.get("target", {})
    mission_target_dest_id = None
    if isinstance(mission_target, dict):
        mission_target_dest_id = mission_target.get("target_id")
    # Fallback to direct field if target dict not available
    if not mission_target_dest_id:
        mission_target_dest_id = mission.get("target_destination_id")
    
    lines = []
    for obj in objectives:
        if not isinstance(obj, dict):
            continue
        
        obj_type = obj.get("objective_type", "")
        params = obj.get("parameters", {})
        
        if obj_type == "destination_visited":
            dest_id = params.get("destination_id") or obj.get("target_id", "") or mission_target_dest_id
            dest_name = _get_destination_name(engine, dest_id)
            lines.append(f"Visit {dest_name}")
        
        elif obj_type in ("cargo_delivered", "deliver_cargo"):
            # Extract delivery requirements
            goods = params.get("goods", [])
            if goods and isinstance(goods, list):
                for good_entry in goods:
                    if isinstance(good_entry, dict):
                        good_id = good_entry.get("good_id") or good_entry.get("sku_id", "")
                        quantity = good_entry.get("quantity", 1)
                        good_name = _get_good_display_name(engine, good_id)
                        # Try multiple sources for destination_id
                        dest_id = (params.get("destination_id") or 
                                  obj.get("target_id", "") or 
                                  mission_target_dest_id)
                        dest_name = _get_destination_name(engine, dest_id) if dest_id else "Unknown Destination"
                        lines.append(f"Deliver {quantity}x {good_name} to {dest_name}")
            else:
                # Fallback: try to extract from target_id or parameters
                good_id = params.get("good_id") or params.get("sku_id") or obj.get("target_id", "")
                quantity = params.get("quantity", obj.get("required_count", 1))
                good_name = _get_good_display_name(engine, good_id)
                # Try multiple sources for destination_id
                dest_id = (params.get("destination_id", "") or 
                          obj.get("target_id", "") or 
                          mission_target_dest_id)
                dest_name = _get_destination_name(engine, dest_id) if dest_id else "Unknown Destination"
                lines.append(f"Deliver {quantity}x {good_name} to {dest_name}")
        
        elif obj_type == "cargo_acquired":
            goods = params.get("goods", [])
            if goods and isinstance(goods, list):
                for good_entry in goods:
                    if isinstance(good_entry, dict):
                        good_id = good_entry.get("good_id") or good_entry.get("sku_id", "")
                        quantity = good_entry.get("quantity", 1)
                        good_name = _get_good_display_name(engine, good_id)
                        lines.append(f"Acquire {quantity}x {good_name}")
        
        elif obj_type in ("npc_destroyed", "combat_victory"):
            target_id = obj.get("target_id", "")
            target_type = obj.get("target_type", "")
            if target_type == "npc":
                npc_name = _get_npc_name(engine, target_id)
                lines.append(f"Destroy {npc_name}")
            else:
                lines.append(f"Defeat target: {target_id}")
        
        else:
            # Generic objective display
            target_id = obj.get("target_id", "")
            if target_id:
                lines.append(f"{obj_type}: {target_id}")
            else:
                lines.append(f"{obj_type}")
    
    return lines if lines else ["No objectives specified"]


def _format_mission_rewards(engine: GameEngine, mission: Dict[str, Any]) -> List[str]:
    """
    Format mission rewards (Part 2) - DISPLAY ONLY, NO RECALCULATION.
    
    Returns list of reward display strings from existing mission data.
    """
    # Use reward_summary_lines if available (from mission_core.get_details)
    reward_summary_lines = mission.get("reward_summary_lines", [])
    if reward_summary_lines:
        return reward_summary_lines
    
    # Use reward_summary if available (legacy format)
    reward_summary = mission.get("reward_summary", [])
    if reward_summary:
        lines = []
        for reward in reward_summary:
            if not isinstance(reward, dict):
                continue
            field = reward.get("field", "")
            if field == "credits":
                delta = reward.get("delta", 0)
                lines.append(f"{delta:+d} credits")
            elif field == "goods":
                sku_id = reward.get("sku_id", "")
                quantity = reward.get("quantity", 1)
                good_name = _get_good_display_name(engine, sku_id)
                lines.append(f"{quantity}x {good_name}")
            elif field == "module":
                module_id = reward.get("module_id", "")
                lines.append(module_id)  # Module ID is the display name
            elif field == "hull_voucher":
                hull_id = reward.get("hull_id", "")
                lines.append(f"Hull voucher: {hull_id}")
        
        return lines if lines else ["No rewards"]
    
    return ["No rewards"]


class PlaytestLogger:
    """
    Logger wrapper that collects structured logs per turn and writes Markdown playtest files.
    
    Does not interfere with engine logging - wraps the existing Logger and collects logs
    for later Markdown formatting.
    """
    
    def __init__(self, base_logger: Logger, verbose: bool = False):
        self._base_logger = base_logger
        self._verbose = verbose
        self._logs_by_turn: Dict[int, List[LogEntry]] = {}
        self._actions_by_turn: Dict[int, List[Dict[str, Any]]] = {}
        self._current_turn = 0
    
    @property
    def version(self) -> str:
        return self._base_logger.version
    
    def configure_file_logging(self, *, enabled: bool, log_path: str | None = None, truncate: bool = False) -> str | None:
        return self._base_logger.configure_file_logging(enabled=enabled, log_path=log_path, truncate=truncate)
    
    def log(self, turn: int, action: str, state_change: str) -> None:
        """Log entry - forwards to base logger and collects for Markdown."""
        # Forward to base logger (preserves existing behavior)
        self._base_logger.log(turn, action, state_change)
        
        # Collect for Markdown
        entry = LogEntry(turn=turn, version=self.version, action=action, state_change=state_change)
        if turn not in self._logs_by_turn:
            self._logs_by_turn[turn] = []
        self._logs_by_turn[turn].append(entry)
        
        # Update current turn tracking
        self._current_turn = max(self._current_turn, turn)
    
    def record_action(self, turn: int, action_type: str, action_data: Dict[str, Any]) -> None:
        """Record a player action for this turn."""
        if turn not in self._actions_by_turn:
            self._actions_by_turn[turn] = []
        self._actions_by_turn[turn].append({
            "type": action_type,
            "data": action_data,
        })
    
    def load_logs_from_file(self, log_path: Path) -> None:
        """
        Load structured logs from engine's log file.
        
        Parses log file format: [v{version}][turn {turn}] action={action} change={state_change}
        """
        if not log_path.exists():
            return
        
        try:
            with open(log_path, "r", encoding="utf-8", errors="replace") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    
                    # Parse format: [v{version}][turn {turn}] action={action} change={state_change}
                    match = re.match(r'\[v([^\]]+)\]\[turn (\d+)\] action=([^ ]+) change=(.+)$', line)
                    if match:
                        version_str, turn_str, action_str, state_change_str = match.groups()
                        turn = int(turn_str)
                        entry = LogEntry(
                            turn=turn,
                            version=version_str,
                            action=action_str,
                            state_change=state_change_str,
                        )
                        if turn not in self._logs_by_turn:
                            self._logs_by_turn[turn] = []
                        self._logs_by_turn[turn].append(entry)
                        self._current_turn = max(self._current_turn, turn)
        except Exception:
            # If parsing fails, silently continue (logs already collected via log() calls)
            pass
    
    def write_markdown(self, output_path: Path, seed: int, version: str, log_file_path: Path | None = None) -> None:
        """
        Write collected logs to Markdown playtest file.
        
        Format:
        # Playtest Log
        
        **Seed:** {seed}  
        **Date/Time:** {timestamp}  
        **Version:** {version}
        
        ## Turn X
        - Action: {action_type}
        - Result: {summary}
        - Player State: {changes}
        - Missions: {updates}
        - Combat: {events}
        
        <details>
        <summary>Raw Logs</summary>
        
        ```json
        {structured_logs}
        ```
        
        </details>
        """
        # Load logs from file if provided (to capture engine's internal logs)
        if log_file_path:
            self.load_logs_from_file(log_file_path)
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, "w", encoding="utf-8") as f:
            # Header
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            f.write("# Playtest Log\n\n")
            f.write(f"**Seed:** {seed}\n")
            f.write(f"**Date/Time:** {timestamp}\n")
            f.write(f"**Version:** {version}\n\n")
            f.write("---\n\n")
            
            # Turn-by-turn sections
            all_turns = sorted(set(self._logs_by_turn.keys()) | set(self._actions_by_turn.keys()))
            
            for turn in all_turns:
                f.write(f"## Turn {turn}\n\n")
                
                # Action taken
                actions = self._actions_by_turn.get(turn, [])
                if actions:
                    for action in actions:
                        f.write(f"- **Action:** {action['type']}\n")
                        if action.get('data'):
                            f.write(f"  - Details: {json.dumps(action['data'], sort_keys=True)}\n")
                else:
                    f.write("- **Action:** (no recorded action)\n")
                
                # Engine result summary (from logs)
                logs = self._logs_by_turn.get(turn, [])
                if logs:
                    # Group by action type for summary
                    action_groups: Dict[str, List[str]] = {}
                    for log_entry in logs:
                        action_type = log_entry.action
                        if action_type not in action_groups:
                            action_groups[action_type] = []
                        action_groups[action_type].append(log_entry.state_change)
                    
                    # Write summary
                    f.write("\n**Engine Events:**\n")
                    for action_type, changes in sorted(action_groups.items()):
                        f.write(f"- {action_type}: {len(changes)} event(s)\n")
                        # Show first few changes as examples
                        for change in changes[:3]:
                            if len(change) > 100:
                                change = change[:97] + "..."
                            f.write(f"  - {change}\n")
                        if len(changes) > 3:
                            f.write(f"  - ... and {len(changes) - 3} more\n")
                
                # Raw logs in collapsible section
                if logs:
                    f.write("\n<details>\n")
                    f.write("<summary>Raw Structured Logs</summary>\n\n")
                    f.write("```json\n")
                    logs_json = [
                        {
                            "turn": entry.turn,
                            "version": entry.version,
                            "action": entry.action,
                            "state_change": entry.state_change,
                        }
                        for entry in logs
                    ]
                    f.write(json.dumps(logs_json, indent=2, sort_keys=True))
                    f.write("\n```\n\n")
                    f.write("</details>\n\n")
                
                f.write("\n---\n\n")
        
        print(f"\nPlaytest log written to {output_path}")


def _is_game_over_result(result: dict) -> bool:
    """Check if a result indicates game over."""
    if not isinstance(result, dict):
        return False
    if result.get("error") == "game_over":
        return True
    if result.get("game_over_reason"):
        return True
    # also support engine returning detail.reason if needed
    detail = result.get("detail")
    if isinstance(detail, dict) and detail.get("reason") in ("ship_destroyed", "tier2_arrest"):
        return True
    return False


def _print_game_over(result: dict) -> None:
    """Print game over message with reason."""
    reason = result.get("game_over_reason")
    if not reason:
        detail = result.get("detail")
        if isinstance(detail, dict):
            reason = detail.get("reason")
    if not reason:
        reason = "unknown"
    print("")
    print("=== GAME OVER ===")
    print(f"Reason: {reason}")
    print("Only option is Quit.")
    print("")


def _game_over_loop(engine: GameEngine, last_result: dict) -> None:
    """Enter quit-only loop after game over."""
    while True:
        print("1) Quit")
        choice = input("Select: ").strip()
        if choice == "1":
            engine.execute({"type": "quit"})
            raise SystemExit(0)
        else:
            print("Game over. Please quit.")


def _prompt_seed() -> int:
    raw = input("Seed [12345]: ").strip()
    if not raw:
        return 12345
    try:
        return int(raw)
    except ValueError:
        return 12345


def _prompt_admin_override() -> dict | None:
    """
    Prompt for admin starting ship override.
    Returns override dict or None if user declines.
    """
    response = input("Use admin custom starting ship? (y/n): ").strip().lower()
    if response != "y":
        return None
    
    # Load hull catalog
    from data_loader import load_hulls, load_modules
    from ship_assembler import get_slot_distribution
    
    hulls_data = load_hulls()
    hulls_list = hulls_data.get("hulls", [])
    
    if not hulls_list:
        raise ValueError("No hulls found in hulls.json")
    
    # Print indexed hull list
    print("\nAvailable Hulls:")
    for idx, hull in enumerate(hulls_list, start=1):
        name = hull.get("name", "Unknown")
        hull_id = hull.get("hull_id", "unknown")
        tier = hull.get("tier", "?")
        frame = hull.get("frame", "?")
        print(f"  [{idx}] {name} | {hull_id} | tier {tier} | {frame}")
    
    # Prompt for hull selection
    while True:
        raw = input("\nSelect hull index: ").strip()
        try:
            hull_idx = int(raw)
            if 1 <= hull_idx <= len(hulls_list):
                selected_hull = hulls_list[hull_idx - 1]
                hull_id = selected_hull.get("hull_id")
                frame = selected_hull.get("frame")
                tier = selected_hull.get("tier")
                break
            else:
                print(f"Invalid index. Please choose 1-{len(hulls_list)}")
        except ValueError:
            print("Invalid input. Please enter a number.")
    
    # Determine slot distribution
    slots = get_slot_distribution(frame, tier)
    weapon_slots = slots["weapon_slots"]
    defense_slots = slots["defense_slots"]
    utility_slots = slots["utility_slots"]
    untyped_slots = slots["untyped_slots"]
    total_slots = slots["total_slots"]
    
    print(f"\nSlot distribution: weapon={weapon_slots}, defense={defense_slots}, utility={utility_slots}, untyped={untyped_slots}, total={total_slots}")
    
    # Load module catalog
    modules_data = load_modules()
    modules_list = modules_data.get("modules", [])
    
    if not modules_list:
        raise ValueError("No modules found in modules.json")
    
    # Build modules by slot type
    modules_by_slot = {
        "weapon": [m for m in modules_list if m.get("slot_type") == "weapon"],
        "defense": [m for m in modules_list if m.get("slot_type") == "defense"],
        "utility": [m for m in modules_list if m.get("slot_type") == "utility"],
    }
    
    # Build slot list with types
    slot_list = []
    for _ in range(weapon_slots):
        slot_list.append("weapon")
    for _ in range(defense_slots):
        slot_list.append("defense")
    for _ in range(utility_slots):
        slot_list.append("utility")
    for _ in range(untyped_slots):
        slot_list.append("untyped")
    
    # Prompt for each slot
    selected_modules = []
    for slot_idx, slot_type in enumerate(slot_list, start=1):
        print(f"\nSlot {slot_idx} ({slot_type.upper()})")
        print("  0) Leave empty")
        
        # Show modules matching slot type (or all if untyped)
        if slot_type == "untyped":
            available_modules = modules_list
        else:
            available_modules = modules_by_slot[slot_type]
        
        if not available_modules:
            print("  (No modules available for this slot type)")
        else:
            for mod_idx, module in enumerate(available_modules, start=1):
                module_name = module.get("name", "Unknown")
                module_id = module.get("module_id", "unknown")
                print(f"  [{mod_idx}] {module_name} ({module_id})")
        
        # Prompt for module selection
        while True:
            raw = input("Select module index for this slot: ").strip()
            try:
                mod_idx = int(raw)
                if mod_idx == 0:
                    # Leave empty
                    break
                elif 1 <= mod_idx <= len(available_modules):
                    selected_module = available_modules[mod_idx - 1]
                    module_id = selected_module.get("module_id")
                    selected_modules.append({"module_id": module_id})
                    break
                else:
                    print(f"Invalid index. Please choose 0-{len(available_modules)}")
            except ValueError:
                print("Invalid input. Please enter a number.")
    
    # Build override dict
    override = {
        "hull_id": hull_id,
        "modules": selected_modules,
    }
    
    return override


def _show_player_info(engine: GameEngine) -> None:
    """Main Player / Ship Info submenu entry point."""
    # Get player profile for summary display
    result = engine.execute({"type": "get_player_profile"})
    detail = _extract_detail_from_stage(step_result=result, stage="player_profile")
    if not isinstance(detail, dict):
        print("Error: Could not retrieve player profile.")
        return
    
    destination_result = engine.execute({"type": "get_destination_profile"})
    if _is_game_over_result(destination_result):
        _print_game_over(destination_result)
        _game_over_loop(engine, destination_result)
        return
    
    destination_profile = _extract_detail_from_stage(
        step_result=destination_result,
        stage="destination_profile",
    )
    
    cargo_manifest = _compact_manifest(detail.get("cargo_manifest", {}))
    insurance_cost = int(detail.get("insurance_cost_per_turn", 0) or 0)
    warehouse_cost = int(detail.get("warehouse_cost_per_turn", 0) or 0)
    crew_wages = int(detail.get("crew_wages_per_turn", 0) or 0)
    recurring_total = int(detail.get("total_recurring_cost_per_turn", 0) or 0)
    warehouses = detail.get("warehouses", [])
    if not isinstance(warehouses, list):
        warehouses = []
    
    # Display comprehensive player information summary
    print("\n=== PLAYER / SHIP INFO ===")
    print(f"Credits: {detail.get('credits', 0)}")
    fuel_current = int(detail.get('fuel_current', 0) or 0)
    fuel_capacity = int(detail.get('fuel_capacity', 0) or 0)
    print(f"Fuel: {fuel_current}/{fuel_capacity}")
    if fuel_current > 0:
        print(f"Max reachable distance: {fuel_current} LY")
    print(f"Cargo manifest: {cargo_manifest}")
    print(f"Reputation: {detail.get('reputation_score', 0)} band={detail.get('reputation_band', 0)}")
    print(f"Heat: {detail.get('heat', 0)}")
    print(f"Notoriety: {detail.get('notoriety_score', 0)} band={detail.get('notoriety_band', 0)}")
    print(f"Arrest state: {detail.get('arrest_state', 'free')}")
    print(f"Warrants: {detail.get('warrants', [])}")
    print(f"Location: {detail.get('system_id', 'N/A')} / {detail.get('destination_id', 'N/A')} / {detail.get('location_id', 'N/A')}")
    print(f"Turn: {detail.get('turn', 0)}")
    
    # Display ship information from engine-provided profile
    ship_info = detail.get("ship")
    if ship_info:
        try:
            from hull_utils import get_hull_display_name
        except ModuleNotFoundError:
            from src.hull_utils import get_hull_display_name
        
        hull_id = ship_info.get('hull_id', 'N/A')
        hull_display_name = get_hull_display_name(hull_id) if isinstance(hull_id, str) else 'N/A'
        hull_display = _format_name_with_profile(ship_info, str(hull_display_name), True)
        print("\nSHIP:")
        print(f"  Hull: {hull_display}" + (f" ({hull_id})" if hull_id != 'N/A' else ""))
        print(f"  Tier: {ship_info.get('tier', 'N/A')}")
        print(f"  Crew: {ship_info.get('crew_current', 0)}/{ship_info.get('crew_capacity', 0)}")
        print(f"  Cargo capacity: Physical {ship_info.get('effective_physical_cargo_capacity', 0)}, Data {ship_info.get('effective_data_cargo_capacity', 0)}")
        print(f"  Fuel capacity: {ship_info.get('fuel_capacity', 0)}")
        subsystem_bands = ship_info.get("subsystem_bands", {})
        if subsystem_bands:
            print(f"  Subsystem bands: Weapon {subsystem_bands.get('weapon', 0)}, Defense {subsystem_bands.get('defense', 0)}, Engine {subsystem_bands.get('engine', 0)}")
        installed_modules = ship_info.get("installed_modules", [])
        if installed_modules:
            active_ship = engine.get_active_ship()
            ship_id = active_ship.get("ship_id", "") if active_ship else ""
            modules = engine.get_ship_modules(ship_id) if ship_id else []
            if modules:
                print("  Installed modules:")
                for mod in modules:
                    name = mod.get("display_name", mod.get("module_id", "N/A"))
                    display = _format_name_with_profile(mod, str(name), True)
                    print(f"    {display}")
            else:
                print(f"  Installed modules: {', '.join(installed_modules)}")
        else:
            print("  Installed modules: None")
        crew_list = ship_info.get("crew", [])
        if crew_list:
            print("  Crew members:")
            for index, crew_member in enumerate(crew_list, start=1):
                npc_id = crew_member.get('npc_id', 'N/A')
                daily_wage = crew_member.get('daily_wage', 0)
                npc_name = _get_npc_name(engine, npc_id)
                npc = None
                try:
                    npc_registry = getattr(engine, "_npc_registry", None)
                    if npc_registry:
                        npc = npc_registry.get_npc(npc_id)
                except Exception:  # noqa: BLE001
                    pass
                display = _format_name_with_profile(npc, npc_name, True) if npc is not None else npc_name
                print(f"    {index}) {display} (wage: {daily_wage})")
        else:
            print("  Crew: None")
    
    # Display short summary of active missions (detailed info in Missions submenu)
    active_missions = engine.get_active_missions()
    if active_missions:
        print(f"\nACTIVE MISSIONS: {len(active_missions)}")
        for mission in active_missions:
            mission_type = mission.get("mission_type", "N/A")
            mission_tier = mission.get("mission_tier", 0)
            target_dest_id = mission.get("target_destination_id") or mission.get("target_system_id")
            if target_dest_id:
                if mission.get("target_destination_id"):
                    target_name = _get_destination_name(engine, target_dest_id)
                    target_obj = _get_destination_object(engine, target_dest_id)
                    target_visible = target_dest_id in _visited_destination_ids(engine)
                else:
                    target_name = _get_system_name(engine, target_dest_id)
                    target_obj = engine.sector.get_system(target_dest_id)
                    target_visible = target_dest_id in _visited_system_ids(engine)
                target_display = _format_name_with_profile(
                    target_obj or SimpleNamespace(emoji_id=None, tier=None, tags=[]),
                    target_name,
                    target_visible,
                )
            else:
                target_display = "N/A"
            mission_display = _format_name_with_profile(mission, str(mission_type), True)
            print(f"  {mission_display} (T{mission_tier}) → {target_display}")
    else:
        print("\nACTIVE MISSIONS: None")
    
    print("\nONGOING COSTS")
    print(f"  Insurance: {insurance_cost}")
    print(f"  Warehouse rental: {warehouse_cost}")
    print(f"  Crew wages: {crew_wages}")
    print(f"  Total recurring cost: {recurring_total}")
    
    print("\nWAREHOUSE RENTALS")
    if not warehouses:
        print("  none")
    else:
        for index, row in enumerate(warehouses, start=1):
            destination_id = row.get("destination_id")
            capacity = int(row.get("capacity", 0) or 0)
            used = int(row.get("used", 0) or 0)
            available = int(row.get("available", 0) or 0)
            cost = int(row.get("cost_per_turn", 0) or 0)
            goods = row.get("goods", {})
            dest_name = _get_destination_name(engine, destination_id) if destination_id else "N/A"
            dest_obj = _get_destination_object(engine, destination_id) if destination_id else None
            visible = destination_id in _visited_destination_ids(engine) if destination_id else False
            dest_display = _format_name_with_profile(
                dest_obj or SimpleNamespace(emoji_id=None, tier=None, tags=[]),
                dest_name,
                visible,
            )
            print(
                f"  {index}) {dest_display} capacity={capacity} "
                f"used={used} available={available} cost/turn={cost} goods={goods}"
            )
    
    # Submenu for detailed management
    while True:
        print("\nOptions:")
        print("0) Back")
        print("1) Ships And Modules")
        print("2) Financial")
        print("3) Missions")
        choice = input("Select: ").strip()
        
        if choice == "0":
            return
        elif choice == "1":
            _show_ships_and_modules(engine)
        elif choice == "2":
            _show_financial(engine)
        elif choice == "3":
            _show_missions(engine)
        else:
            print("Invalid selection.")


def _show_ships_and_modules(engine: GameEngine) -> None:
    """Ships And Modules submenu."""
    # Get owned ships from engine
    owned_ships = engine.get_owned_ships()
    active_ship = engine.get_active_ship()
    
    print("\n=== SHIPS AND MODULES ===")
    
    # Display active ship
    if active_ship:
        print("\nACTIVE SHIP:")
        try:
            from hull_utils import get_hull_display_name as _get_hull_name
        except ModuleNotFoundError:
            from src.hull_utils import get_hull_display_name as _get_hull_name
        ship_name = active_ship.get("display_name") or _get_hull_name(active_ship.get("hull_id", "") or "")
        ship_display = _format_name_with_profile(active_ship, str(ship_name), True)
        print(f"  {ship_display}")
        print(f"  Ship ID: {active_ship.get('ship_id', 'N/A')}")
        print(f"  Hull ID: {active_ship.get('hull_id', 'N/A')}")
        hull_integrity = active_ship.get('hull_integrity', {})
        if isinstance(hull_integrity, dict):
            current = hull_integrity.get('current', 0)
            max_hull = hull_integrity.get('max', 0)
            pct = int((current / max_hull * 100)) if max_hull > 0 else 0
            print(f"  Hull Integrity: {current}/{max_hull} ({pct}%)")
        fuel_info = active_ship.get('fuel', {})
        if isinstance(fuel_info, dict):
            current = fuel_info.get('current', 0)
            capacity = fuel_info.get('capacity', 0)
            print(f"  Fuel: {current}/{capacity}")
        
        # Installed modules
        modules = engine.get_ship_modules(active_ship.get('ship_id', ''))
        if modules:
            print("  Installed Modules:")
            for module in modules:
                name = module.get("display_name", module.get("module_id", "N/A"))
                display = _format_name_with_profile(module, str(name), True)
                print(f"    {display}")
        else:
            print("  Installed Modules: None")
        
        # Cargo summary
        cargo = engine.get_ship_cargo(active_ship.get('ship_id', ''))
        if cargo:
            cargo_summary = _compact_manifest(cargo)
            print(f"  Cargo: {cargo_summary}")
        else:
            print("  Cargo: None")
    else:
        print("\nACTIVE SHIP: None")
    
    # Display inactive ships
    active_ship_id = active_ship.get('ship_id') if active_ship else None
    inactive_ships = [s for s in owned_ships if s.get('ship_id') != active_ship_id]
    if inactive_ships:
        print("\nINACTIVE SHIPS:")
        for ship in inactive_ships:
            name = ship.get("display_name") or ship.get("hull_id", "N/A")
            display = _format_name_with_profile(ship, str(name), True)
            print(f"  {display}")
            print(f"    Ship ID: {ship.get('ship_id', 'N/A')}")
            print(f"    Destination: {ship.get('destination_id', 'N/A')}")
            hull_integrity = ship.get('hull_integrity', {})
            if isinstance(hull_integrity, dict):
                current = hull_integrity.get('current', 0)
                max_hull = hull_integrity.get('max', 0)
                pct = int((current / max_hull * 100)) if max_hull > 0 else 0
                print(f"    Hull Integrity: {current}/{max_hull} ({pct}%)")
            cargo = engine.get_ship_cargo(ship.get('ship_id', ''))
            if cargo:
                cargo_summary = _compact_manifest(cargo)
                print(f"    Cargo: {cargo_summary}")
            else:
                print(f"    Cargo: None")
    
    # Submenu options
    while True:
        print("\nOptions:")
        print("0) Back")
        print("1) Change Active Ship")
        print("2) Install Module")
        print("3) Uninstall Module")
        print("4) Transfer Cargo")
        choice = input("Select: ").strip()
        
        if choice == "0":
            return
        elif choice == "1":
            _change_active_ship(engine)
            break
        elif choice == "2":
            _install_module(engine)
            break
        elif choice == "3":
            _uninstall_module(engine)
            break
        elif choice == "4":
            _transfer_cargo(engine)
            break
        else:
            print("Invalid selection.")


def _change_active_ship(engine: GameEngine) -> None:
    """Change active ship submenu."""
    owned_ships = engine.get_owned_ships()
    active_ship = engine.get_active_ship()
    
    if len(owned_ships) <= 1:
        print("Only one ship owned. Cannot change active ship.")
        return
    
    active_ship_id = active_ship.get('ship_id') if active_ship else None
    inactive_ships = [s for s in owned_ships if s.get('ship_id') != active_ship_id]
    if not inactive_ships:
        print("No inactive ships available.")
        return
    
    print("\nInactive Ships:")
    for idx, ship in enumerate(inactive_ships, start=1):
        name = ship.get("display_name") or ship.get("hull_id", "N/A")
        display = _format_name_with_profile(ship, str(name), True)
        print(f"  {idx}) {display} at {ship.get('destination_id', 'N/A')}")
    
    try:
        raw = input("\nSelect ship index [0 cancel]: ").strip()
        if raw == "0":
            return
        selected_idx = int(raw)
        if selected_idx < 1 or selected_idx > len(inactive_ships):
            print("Invalid selection.")
            return
        target_ship = inactive_ships[selected_idx - 1]
        ship_id = target_ship.get('ship_id')
        if not ship_id:
            print("Invalid ship ID.")
            return
        
        result = engine.execute({"type": "set_active_ship", "ship_id": ship_id})
        if _is_game_over_result(result):
            _print_game_over(result)
            _game_over_loop(engine, result)
            return
        if result.get("ok"):
            print(f"Active ship changed to {ship_id}.")
        else:
            error = result.get("error", "unknown_error")
            print(f"Failed to change active ship: {error}")
    except ValueError:
        print("Invalid input.")


def _install_module(engine: GameEngine) -> None:
    """Install module submenu (stub - requires shipdock integration)."""
    print("\nInstall Module:")
    print("This feature requires shipdock location access.")
    print("Please visit a shipdock to install modules.")
    input("Press Enter to continue...")


def _uninstall_module(engine: GameEngine) -> None:
    """Uninstall module submenu (stub - requires shipdock integration)."""
    print("\nUninstall Module:")
    print("This feature requires shipdock location access.")
    print("Please visit a shipdock to uninstall modules.")
    input("Press Enter to continue...")


def _transfer_cargo(engine: GameEngine) -> None:
    """Transfer cargo between ships submenu."""
    owned_ships = engine.get_owned_ships()
    active_ship = engine.get_active_ship()
    current_destination = engine.player_state.current_destination_id
    
    if not active_ship:
        print("No active ship.")
        return
    
    # Find ships at same destination
    same_dest_ships = [s for s in owned_ships if s.get('destination_id') == current_destination and s.get('ship_id') != active_ship.get('ship_id')]
    if not same_dest_ships:
        print("No other ships at current destination.")
        return
    
    print("\nShips at current destination:")
    for idx, ship in enumerate(same_dest_ships, start=1):
        name = ship.get("display_name") or ship.get("hull_id", "N/A")
        display = _format_name_with_profile(ship, str(name), True)
        print(f"  {idx}) {display}")
    
    try:
        raw = input("\nSelect target ship index [0 cancel]: ").strip()
        if raw == "0":
            return
        target_idx = int(raw)
        if target_idx < 1 or target_idx > len(same_dest_ships):
            print("Invalid selection.")
            return
        target_ship = same_dest_ships[target_idx - 1]
        target_ship_id = target_ship.get('ship_id')
        if not target_ship_id:
            print("Invalid ship ID.")
            return
        
        # List cargo on active ship
        source_cargo = engine.get_ship_cargo(active_ship.get('ship_id', ''))
        if not source_cargo:
            print("No cargo to transfer.")
            return
        
        cargo_list = sorted(source_cargo.items())
        print("\nAvailable cargo:")
        for idx, (sku, qty) in enumerate(cargo_list, start=1):
            display_name = _get_good_display_name(engine, sku)
            print(f"  {idx}) {display_name}: {qty}")
        
        raw_sku = input("\nSelect cargo SKU [0 cancel]: ").strip()
        if raw_sku == "0":
            return
        try:
            sku_idx = int(raw_sku)
            if sku_idx < 1 or sku_idx > len(cargo_list):
                print("Invalid selection.")
                return
            sku_id, available_qty = cargo_list[sku_idx - 1]
        except ValueError:
            sku_id = raw_sku
            available_qty = source_cargo.get(sku_id, 0)
            if available_qty == 0:
                print("Cargo not found.")
                return
        
        raw_qty = input(f"Quantity to transfer (max {available_qty}) [0 cancel]: ").strip()
        if raw_qty == "0":
            return
        try:
            qty = int(raw_qty)
            if qty < 1 or qty > available_qty:
                print("Invalid quantity.")
                return
        except ValueError:
            print("Invalid quantity.")
            return
        
        result = engine.execute({
            "type": "transfer_cargo",
            "source_ship_id": active_ship.get('ship_id'),
            "target_ship_id": target_ship_id,
            "sku": sku_id,
            "quantity": qty,
        })
        if _is_game_over_result(result):
            _print_game_over(result)
            _game_over_loop(engine, result)
            return
        if result.get("ok"):
            print(f"Transferred {qty} units of {sku_id}.")
        else:
            error = result.get("error", "unknown_error")
            print(f"Failed to transfer cargo: {error}")
    except ValueError:
        print("Invalid input.")


def _show_financial(engine: GameEngine) -> None:
    """Financial submenu."""
    result = engine.execute({"type": "get_player_profile"})
    detail = _extract_detail_from_stage(step_result=result, stage="player_profile")
    if not isinstance(detail, dict):
        print("Error: Could not retrieve player profile.")
        return
    
    print("\n=== FINANCIAL ===")
    print(f"\nCREDITS: {detail.get('credits', 0)}")
    
    # Warehouse rentals
    warehouses = engine.get_warehouse_rentals()
    print("\nWAREHOUSE RENTALS:")
    if not warehouses:
        print("  None")
    else:
        for idx, rental in enumerate(warehouses, start=1):
            destination_id = rental.get("destination_id", "N/A")
            capacity = rental.get("capacity", 0)
            cost = rental.get("cost_per_turn", 0)
            expiration = rental.get("expiration_day", "N/A")
            dest_name = _get_destination_name(engine, destination_id)
            dest_obj = _get_destination_object(engine, destination_id) if destination_id != "N/A" else None
            visible = destination_id in _visited_destination_ids(engine) if destination_id != "N/A" else False
            display = _format_name_with_profile(
                dest_obj or SimpleNamespace(emoji_id=None, tier=None, tags=[]),
                dest_name,
                visible,
            )
            print(f"  {idx}) Location: {display}, Capacity: {capacity}, Cost/turn: {cost}, Expiration: {expiration}")
    
    # Insurance stub
    print("\nINSURANCE:")
    insurance_policies = detail.get("insurance_policies", [])
    if not insurance_policies:
        print("  None")
    else:
        for idx, policy in enumerate(insurance_policies, start=1):
            print(f"  {idx}) {policy}")
    
    # Submenu options
    while True:
        print("\nOptions:")
        print("0) Back")
        print("1) Cancel Warehouse Rental")
        print("2) Cancel Insurance")
        choice = input("Select: ").strip()
        
        if choice == "0":
            return
        elif choice == "1":
            _cancel_warehouse_rental(engine)
            break
        elif choice == "2":
            print("\nCancel Insurance: Not yet implemented.")
            input("Press Enter to continue...")
            break
        else:
            print("Invalid selection.")


def _cancel_warehouse_rental(engine: GameEngine) -> None:
    """Cancel warehouse rental submenu."""
    warehouses = engine.get_warehouse_rentals()
    if not warehouses:
        print("No warehouse rentals to cancel.")
        return
    
    print("\nWarehouse Rentals:")
    for idx, rental in enumerate(warehouses, start=1):
        destination_id = rental.get("destination_id", "N/A")
        capacity = rental.get("capacity", 0)
        cost = rental.get("cost_per_turn", 0)
        dest_name = _get_destination_name(engine, destination_id) if destination_id != "N/A" else "N/A"
        dest_obj = _get_destination_object(engine, destination_id) if destination_id != "N/A" else None
        visible = destination_id in _visited_destination_ids(engine) if destination_id != "N/A" else False
        display = _format_name_with_profile(
            dest_obj or SimpleNamespace(emoji_id=None, tier=None, tags=[]),
            dest_name,
            visible,
        )
        print(f"  {idx}) {display} - Capacity: {capacity}, Cost/turn: {cost}")
    
    try:
        raw = input("\nSelect rental index to cancel [0 cancel]: ").strip()
        if raw == "0":
            return
        selected = int(raw)
        if selected < 1 or selected > len(warehouses):
            print("Invalid selection.")
            return
        rental = warehouses[selected - 1]
        destination_id = rental.get("destination_id")
        if not destination_id:
            print("Invalid destination ID.")
            return
        
        result = engine.execute({"type": "warehouse_cancel", "destination_id": destination_id})
        if _is_game_over_result(result):
            _print_game_over(result)
            _game_over_loop(engine, result)
            return
        if result.get("ok"):
            dest_name = _get_destination_name(engine, destination_id)
            dest_obj = _get_destination_object(engine, destination_id)
            visible = destination_id in _visited_destination_ids(engine)
            dest_display = _format_name_with_profile(
                dest_obj or SimpleNamespace(emoji_id=None, tier=None, tags=[]),
                dest_name,
                visible,
            )
            print(f"Warehouse rental at {dest_display} cancelled.")
        else:
            error = result.get("error", "unknown_error")
            print(f"Failed to cancel warehouse rental: {error}")
    except ValueError:
        print("Invalid input.")


def _show_missions(engine: GameEngine) -> None:
    """Missions submenu with detailed mission information."""
    active_missions = engine.get_active_missions()
    claimable_missions = engine.get_claimable_missions()
    
    print("\n=== MISSIONS ===")
    
    print("\nACTIVE MISSIONS:")
    if not active_missions:
        print("  None")
    else:
        for idx, mission in enumerate(active_missions, start=1):
            mission_id = mission.get("mission_id", "N/A")
            mission_type = mission.get("mission_type", "N/A")
            mission_tier = mission.get("mission_tier", 0)
            
            # Get mission entity ONLY to access objectives - NO RECALCULATION
            mission_entity = None
            try:
                mission_manager = engine._mission_manager
                mission_entity = mission_manager.missions.get(mission_id)
            except Exception:  # noqa: BLE001
                pass
            
            # Part 1: Target information with names and emoji profiles
            target_destination_id = mission.get("target_destination_id")
            target_system_id = mission.get("target_system_id")
            if target_destination_id:
                dest_name = _get_destination_name(engine, target_destination_id)
                dest_obj = _get_destination_object(engine, target_destination_id)
                dest_visible = target_destination_id in _visited_destination_ids(engine)
                dest_display = _format_name_with_profile(
                    dest_obj or SimpleNamespace(emoji_id=None, tier=None, tags=[]),
                    dest_name,
                    dest_visible,
                )
                if target_system_id:
                    system_name = _get_system_name(engine, target_system_id)
                    system_obj = engine.sector.get_system(target_system_id) if target_system_id else None
                    system_visible = target_system_id in _visited_system_ids(engine)
                    system_display = _format_name_with_profile(
                        system_obj or SimpleNamespace(emoji_id=None, tier=None, tags=[]),
                        system_name,
                        system_visible,
                    )
                    target_display = f"{dest_display} ({system_display})"
                else:
                    target_display = dest_display
            elif target_system_id:
                system_name = _get_system_name(engine, target_system_id)
                system_obj = engine.sector.get_system(target_system_id)
                system_visible = target_system_id in _visited_system_ids(engine)
                target_display = _format_name_with_profile(
                    system_obj or SimpleNamespace(emoji_id=None, tier=None, tags=[]),
                    system_name,
                    system_visible,
                )
            else:
                target_display = "Unknown"
            
            # Part 2 & 3: Objectives - from mission entity ONLY (not in mission dict)
            objective_text = "No objectives specified"
            if mission_entity:
                mission_dict_for_obj = mission_entity.to_dict()
                objective_lines = _format_mission_objectives(engine, mission_dict_for_obj)
                if objective_lines:
                    objective_text = "; ".join(objective_lines)
            
            # Part 2: Rewards - use reward_summary_lines from mission dict (already calculated by engine)
            reward_lines = mission.get("reward_summary_lines", [])
            reward_text = ", ".join(reward_lines) if reward_lines else "No rewards"
            
            # Mission Title - from mission entity if available, else use mission_id
            title = mission_id
            if mission_entity:
                title = mission_entity.name or mission_id
            title_display = _format_name_with_profile(
                mission_entity or mission,
                str(title),
                True,
            )
            # Collection format - from mission dict
            collection_format = mission.get("collection_format", "Auto")
            
            print(f"\n  Mission {idx}: {title_display}")
            print(f"    Type: {mission_type} (Tier {mission_tier})")
            print(f"    Target: {target_display}")
            print(f"    Objectives: {objective_text}")
            print(f"    Rewards: {reward_text}")
            print(f"    Collection: {collection_format}")
    
    # Submenu options
    while True:
        print("\nOptions:")
        print("0) Back")
        print("1) Abandon Mission")
        # Phase 7.11.2b - Only show claim option if there are claimable missions
        if claimable_missions:
            print("2) Claim Mission Reward")
        choice = input("Select: ").strip()
        
        if choice == "0":
            return
        elif choice == "1":
            _abandon_mission(engine)
            break
        elif choice == "2" and claimable_missions:
            _claim_mission_reward(engine)
            break
        else:
            print("Invalid selection.")


def _abandon_mission(engine: GameEngine) -> None:
    """Abandon mission submenu."""
    active_missions = engine.get_active_missions()
    if not active_missions:
        print("No active missions to abandon.")
        return
    
    print("\nActive Missions:")
    for idx, mission in enumerate(active_missions, start=1):
        mission_id = mission.get("mission_id", "N/A")
        title = mission.get("title", mission.get("mission_type", "N/A"))
        display = _format_name_with_profile(mission, str(title), True)
        print(f"  {idx}) {mission_id}: {display}")
    
    try:
        raw = input("\nSelect mission index to abandon [0 cancel]: ").strip()
        if raw == "0":
            return
        selected = int(raw)
        if selected < 1 or selected > len(active_missions):
            print("Invalid selection.")
            return
        mission = active_missions[selected - 1]
        mission_id = mission.get("mission_id")
        if not mission_id:
            print("Invalid mission ID.")
            return
        
        result = engine.execute({"type": "abandon_mission", "mission_id": mission_id})
        if _is_game_over_result(result):
            _print_game_over(result)
            _game_over_loop(engine, result)
            return
        if result.get("ok"):
            print(f"Mission {mission_id} abandoned.")
        else:
            error = result.get("error", "unknown_error")
            print(f"Failed to abandon mission: {error}")
    except ValueError:
        print("Invalid input.")


def _format_reward_summary(reward_summary: object) -> str:
    """Format reward_summary consistently for all mission displays (Phase 7.x).

    Expected input:
      reward_summary: list[dict] with entries like {"field": "credits", "delta": int}

    Output:
      "+4800 credits" / "+1000 credits" / "No rewards"
    """
    if not isinstance(reward_summary, list) or not reward_summary:
        return "No rewards"

    parts: list[str] = []
    for reward in reward_summary:
        if not isinstance(reward, dict):
            continue
        field = reward.get("field", "")
        delta = reward.get("delta", 0)
        if field == "credits":
            parts.append(f"{delta:+d} credits")
        else:
            parts.append(f"{field}: {delta}")

    return ", ".join(parts) if parts else "No rewards"


def _claim_mission_reward(engine: GameEngine) -> None:
    """Claim mission reward submenu."""
    claimable_missions = engine.get_claimable_missions()
    if not claimable_missions:
        print("No claimable mission rewards.")
        return
    
    print("\nClaimable Missions:")
    for idx, mission in enumerate(claimable_missions, start=1):
        mission_id = mission.get("mission_id", "N/A")
        title = mission.get("title", mission.get("mission_type", "N/A"))
        display = _format_name_with_profile(mission, str(title), True)
        print(f"  {idx}) {mission_id}: {display}")
    
    try:
        raw = input("\nSelect mission index to claim [0 cancel]: ").strip()
        if raw == "0":
            return
        selected = int(raw)
        if selected < 1 or selected > len(claimable_missions):
            print("Invalid selection.")
            return
        mission = claimable_missions[selected - 1]
        mission_id = mission.get("mission_id")
        if not mission_id:
            print("Invalid mission ID.")
            return
        
        result = engine.execute({"type": "claim_mission", "mission_id": mission_id})
        if _is_game_over_result(result):
            _print_game_over(result)
            _game_over_loop(engine, result)
            return
        if result.get("ok"):
            print(f"Mission {mission_id} reward claimed.")
        else:
            error = result.get("error", "unknown_error")
            print(f"Failed to claim mission reward: {error}")
    except ValueError:
        print("Invalid input.")


def _dismiss_crew_menu(engine: GameEngine) -> None:
    """Handle crew dismissal from Player / Ship Info menu."""
    # Get player profile to access crew list
    result = engine.execute({"type": "get_player_profile"})
    detail = _extract_detail_from_stage(step_result=result, stage="player_profile")
    if not isinstance(detail, dict):
        print("Error: Could not retrieve player profile.")
        return
    
    ship_info = detail.get("ship")
    if not ship_info:
        print("Error: No active ship.")
        return
    
    crew_list = ship_info.get("crew", [])
    if not crew_list:
        print("No crew members to dismiss.")
        return
    
    print("CREW DISMISSAL")
    for index, crew_member in enumerate(crew_list, start=1):
        npc_id = crew_member.get('npc_id', 'N/A')
        daily_wage = crew_member.get('daily_wage', 0)
        npc_name = _get_npc_name(engine, npc_id)
        npc = None
        try:
            npc_registry = getattr(engine, "_npc_registry", None)
            if npc_registry:
                npc = npc_registry.get_npc(npc_id)
        except Exception:  # noqa: BLE001
            pass
        display = _format_name_with_profile(npc, npc_name, True) if npc is not None else npc_name
        print(f"  {index}) {display} (wage: {daily_wage})")
    
    raw_selection = input("Dismiss crew member index [0 cancel]: ").strip()
    if raw_selection == "0":
        return
    
    try:
        selected = int(raw_selection)
    except ValueError:
        print("Invalid crew member index.")
        return
    
    if selected < 1 or selected > len(crew_list):
        print("Invalid crew member index.")
        return
    
    npc_id = crew_list[selected - 1].get("npc_id")
    if not isinstance(npc_id, str) or not npc_id:
        print("Invalid crew member ID.")
        return
    
    result = engine.execute({"type": "dismiss_crew", "npc_id": npc_id})
    if _is_game_over_result(result):
        _print_game_over(result)
        _game_over_loop(engine, result)
        return
    detail = _extract_detail_from_stage(step_result=result, stage="crew_dismissal")
    if isinstance(detail, dict):
        result_detail = detail.get("result", {})
        if result_detail.get("ok"):
            relocated = result_detail.get("relocated_to", {})
            print(f"Crew member {npc_id} dismissed and relocated to:")
            print(f"  System: {relocated.get('system_id')}")
            print(f"  Destination: {relocated.get('destination_id')}")
            print(f"  Location: {relocated.get('location_id')}")
        else:
            reason = result_detail.get("reason", "unknown_error")
            print(f"Dismissal failed: {reason}")
    else:
        _format_result(result, "location_action")


def _show_system_info(engine: GameEngine) -> None:
    result = engine.execute({"type": "get_system_profile"})
    if _is_game_over_result(result):
        _print_game_over(result)
        _game_over_loop(engine, result)
        return
    detail = _extract_detail_from_stage(step_result=result, stage="system_profile")
    if not isinstance(detail, dict):
        _format_result(result, "location_action")
        return
    coords = detail.get("coordinates", {})
    system_id = str(detail.get("system_id", "") or "")
    system_visited = system_id in _visited_system_ids(engine)
    system_obj = engine.sector.get_system(system_id) if system_id else None
    system_name = detail.get("name", system_id) or system_id
    system_display = _format_name_with_profile(
        system_obj or SimpleNamespace(emoji_id=None, tier=None, tags=[]),
        system_name,
        system_visited,
    )
    print("SYSTEM INFO")
    print(f"  Name: {system_display}")
    print(f"  ID: {system_id}")
    if system_visited:
        print(f"  Government: {detail.get('government_id')}")
        print(f"  Population: {detail.get('population')}")
    else:
        print("  Government: Unknown")
        print("  Population: Unknown")
    print(f"  Coordinates: ({coords.get('x')}, {coords.get('y')})")
    if system_visited:
        print(f"  Active situations: {detail.get('active_system_situations')}")
        system = engine.sector.get_system(system_id)
        if system is None:
            print("  Destinations: none")
        else:
            dest_displays = []
            for destination in sorted(system.destinations, key=lambda d: d.destination_id):
                visible = destination.destination_id in _visited_destination_ids(engine)
                dest_displays.append(_format_name_with_profile(destination, destination.display_name, visible))
            print(f"  Destinations: {', '.join(dest_displays) if dest_displays else 'none'}")
    else:
        print("  Active situations: Unknown")
        print("  Destinations: Unknown")
    print(f"  Active flags: {detail.get('active_system_flags')}")
    print("  Reachable systems:")
    for row in detail.get("reachable_systems", []):
        system_id_reachable = row.get('system_id', '')
        system_name_reachable = row.get('name', system_id_reachable)
        distance = row.get('distance_ly', 0.0)
        in_range = row.get('in_range', False)
        system_obj = engine.sector.get_system(system_id_reachable) if system_id_reachable else None
        visited = system_id_reachable in _visited_system_ids(engine)
        display = _format_name_with_profile(
            system_obj or SimpleNamespace(emoji_id=None, tier=None, tags=[]),
            system_name_reachable,
            visited,
        )
        print(f"    {display} distance_ly={distance:.3f} in_range={in_range}")
    # Part 4: Map removed from System Info - only shown in Travel menu


def _show_destination_info(engine: GameEngine) -> None:
    result = engine.execute({"type": "get_destination_profile"})
    if _is_game_over_result(result):
        _print_game_over(result)
        _game_over_loop(engine, result)
        return
    detail = _extract_detail_from_stage(step_result=result, stage="destination_profile")
    if not isinstance(detail, dict):
        _format_result(result, "location_action")
        return
    destination_id = str(detail.get("destination_id", "") or "")
    destination_visited = destination_id in _visited_destination_ids(engine)
    # Part 1: Display destination name instead of ID
    destination_name = _get_destination_name(engine, destination_id)
    destination_object = _get_destination_object(engine, destination_id)
    display_name = _format_name_with_profile(
        destination_object or SimpleNamespace(emoji_id=None, tier=None, tags=[]),
        destination_name,
        destination_visited,
    )
    print("DESTINATION INFO")
    print(f"  Name: {display_name}")
    print(f"  Population: {detail.get('population')}")
    if destination_visited:
        print(f"  Primary economy: {detail.get('primary_economy')}")
    else:
        print("  Primary economy: Unknown")
    print(f"  Market attached: {detail.get('market_attached')}")
    if destination_visited:
        print(f"  Active destination situations: {detail.get('active_destination_situations')}")
    else:
        print("  Active destination situations: Unknown")
    print("  Locations:")
    if not destination_visited:
        print("    Unknown")
    else:
        locations = detail.get("locations", [])
        if not locations:
            print("    none")
        for row in locations:
            location_type = str(row.get("location_type") or "")
            location_id = str(row.get("location_id") or "")
            name = location_id or location_type or "Unknown"
            location_entity = SimpleNamespace(
                emoji_id=f"location_{location_type}" if location_type else None,
                tier=None,
                tags=[],
            )
            display = _format_name_with_profile(location_entity, name, True)
            print(f"    {display}")


def _faction_label_for_subtype(subtype_id: str | None) -> str:
    """Return a short faction label for display; safe if subtype_id is missing."""
    if not subtype_id:
        return ""
    _map = {
        "pirate_raider": "pirates",
        "blood_raider": "raiders",
        "customs_patrol": "authority",
        "bounty_hunter": "authority",
        "civilian_trader_ship": "civilian",
        "derelict_ship": "derelict",
        "derelict_station": "derelict",
        "distress_call": "civilian",
        "asteroid_field": "environment",
        "comet_passage": "environment",
        "debris_storm": "environment",
        "ion_storm": "environment",
        "spatial_rift": "anomaly",
        "ancient_beacon": "anomaly",
        "quantum_echo": "anomaly",
        "wormhole_anomaly": "anomaly",
    }
    return _map.get(str(subtype_id), "")


def _extract_encounter_resolution_data(
    result: Dict[str, Any],
    engine: Optional[GameEngine] = None,
) -> Dict[str, Any]:
    """
    Extract encounter resolution data from engine result (and optional engine for pending loot).
    Uses only already-returned data; safe access for missing fields.
    """
    events = result.get("events") or []
    data = {
        "encounter_type": "",
        "subtype": "",
        "faction": "",
        "player_action": "",
        "resolver": "none",
        "combat_outcome": "",
        "npc_destroyed": False,
        "salvage_modules": [],
        "cargo_sku": None,
        "cargo_quantity": 0,
        "credits_awarded": 0,
    }
    for event in events:
        if not isinstance(event, dict):
            continue
        detail = event.get("detail") or {}
        if not isinstance(detail, dict):
            continue
        stage = event.get("stage")
        if stage == "interaction_dispatch":
            data["player_action"] = str(detail.get("action_id", "") or "")
            data["encounter_type"] = str(detail.get("encounter_category", "") or "").replace("environmental_", "environmental ") or "npc_encounter"
            subtype_id = detail.get("subtype_id") or ""
            if subtype_id:
                data["subtype"] = str(subtype_id)
                data["faction"] = _faction_label_for_subtype(subtype_id)
        elif stage == "resolver":
            ro = detail.get("resolver_outcome") or {}
            data["resolver"] = str(ro.get("resolver", "none") or "none")
            outcome = ro.get("outcome")
            if outcome is not None:
                data["combat_outcome"] = str(outcome)
            winner = ro.get("winner")
            if winner is not None:
                data["npc_destroyed"] = str(winner) == "player"
                if data["combat_outcome"] == "" and winner:
                    data["combat_outcome"] = "victory" if winner == "player" else "defeat"
        elif stage == "post_combat" and detail.get("subsystem") == "reward_handler":
            data["credits_awarded"] = int(detail.get("credits_applied_immediately", 0) or 0)
            data["cargo_sku"] = detail.get("cargo_sku")
            data["cargo_quantity"] = int(detail.get("cargo_quantity", 0) or 0)
            data["salvage_count"] = int(detail.get("salvage_count", 0) or 0)
        elif stage == "conditional_rewards" and detail.get("subsystem") == "reward_applicator":
            applied = detail.get("applied") or {}
            if isinstance(applied, dict):
                data["credits_awarded"] = data["credits_awarded"] or int(applied.get("credits", 0) or 0)
                data["cargo_sku"] = data["cargo_sku"] or applied.get("cargo")
                data["cargo_quantity"] = data["cargo_quantity"] or int(applied.get("quantity", 0) or 0)
        elif stage == "combat" and detail.get("subsystem") == "combat_action":
            if detail.get("outcome"):
                data["combat_outcome"] = str(detail.get("outcome", ""))
    # Pending loot (from result or engine) for salvage module list
    pending = result.get("pending_loot") or {}
    salvage_count = data.get("salvage_count", 0) or int(pending.get("salvage_count", 0) or 0)
    if engine and result.get("hard_stop_reason") == "pending_loot_decision":
        engine_loot = engine.get_pending_loot() or {}
        modules = engine_loot.get("salvage_modules") or []
        if modules:
            for m in modules:
                if isinstance(m, dict):
                    mid = m.get("module_id", "?")
                    data["salvage_modules"].append((mid, 1))
        elif salvage_count and not data["salvage_modules"]:
            data["salvage_modules"] = [("(see pending loot)", salvage_count)]
    return data


def _print_encounter_resolution_block(
    result: Dict[str, Any],
    player_action: Optional[str] = None,
    encounter_description: Optional[str] = None,
    engine: Optional[GameEngine] = None,
) -> None:
    """
    Print a structured encounter resolution block for debugging/visibility.
    Uses only data already returned by the engine; no gameplay logic changes.
    """
    data = _extract_encounter_resolution_data(result, engine=engine)
    if player_action:
        data["player_action"] = data["player_action"] or player_action
    resolver = data.get("resolver") or "none"
    print("\n--------------------------------------------------")
    print("Encounter Resolution")
    print("--------------------------------------------------")
    print(f"Encounter Type: {data.get('encounter_type') or 'npc_encounter'}")
    if data.get("subtype"):
        print(f"Subtype: {data.get('subtype')}")
    if data.get("faction"):
        print(f"Faction: {data.get('faction')}")
    print()
    print(f"Player Action: {data.get('player_action') or '—'}")
    print(f"Resolver: {resolver}")
    if data.get("combat_outcome"):
        print()
        print(f"Combat Outcome: {data.get('combat_outcome')}")
        if data.get("npc_destroyed") is not False:
            print(f"NPC Destroyed: {str(data.get('npc_destroyed')).lower()}")
    if data.get("salvage_modules"):
        print()
        print("Salvage Modules:")
        for mid, qty in data["salvage_modules"]:
            print(f"  {mid} x{qty}")
    cargo_sku = data.get("cargo_sku")
    cargo_qty = data.get("cargo_quantity", 0)
    if cargo_sku and cargo_qty:
        print()
        print("Cargo Rewards:")
        print(f"  {cargo_sku} x{cargo_qty}")
    credits = data.get("credits_awarded", 0)
    if credits is not None and int(credits) > 0:
        print()
        print(f"Credits Awarded: {int(credits)}")
    print("--------------------------------------------------\n")


def _show_encounter_result(
    result: Dict[str, Any],
    encounter_description: str | None,
    npc_display_name: str | None = None,
) -> None:
    """
    Display player-friendly encounter result.
    
    Shows what the NPC is doing: hailing, demanding inspection, ignoring, etc.
    npc_display_name: optional name + emoji profile for attack/response messages.
    """
    # Extract resolver outcome from events
    events = result.get("events", [])
    resolver_outcome = None
    for event in events:
        if isinstance(event, dict) and event.get("stage") == "resolver":
            detail = event.get("detail", {})
            resolver_outcome = detail.get("resolver_outcome", {})
            break
    
    if resolver_outcome:
        resolver = resolver_outcome.get("resolver", "none")
        outcome = resolver_outcome.get("outcome")
        
        if resolver == "reaction":
            # NPC reaction outcome
            if outcome == "hail":
                print("The ship hails you.")
            elif outcome == "warn":
                print("The ship issues a warning.")
            elif outcome == "ignore":
                print("The ship ignores you and continues on its way.")
            elif outcome == "attack":
                if npc_display_name:
                    print(f"{npc_display_name} attacks!")
                else:
                    print("The ship attacks!")
            elif outcome == "pursue":
                print("The ship begins pursuit!")
            elif outcome == "accept":
                print("The ship accepts your communication.")
            else:
                # Unknown outcome - show generic message
                print(f"The encounter resolves: {outcome}")
        elif resolver == "law":
            # Law enforcement outcome
            print("Border patrol demands inspection.")
        elif resolver == "combat":
            # Combat initiated
            print("Combat begins!")
        elif resolver == "pursuit":
            # Pursuit outcome
            escaped = resolver_outcome.get("escaped", False)
            if escaped:
                print("You escape the pursuit.")
            else:
                print("Pursuit continues...")
        elif resolver == "exploration":
            # Exploration / environmental encounter outcomes (Phase 7.12).
            # First, surface any mining-blocked messaging for environmental mining subtypes.
            events = result.get("events", [])
            mining_blocked = None
            hazard_event = None
            mining_detail_event = None
            for ev in events:
                if not isinstance(ev, dict):
                    continue
                stage = ev.get("stage")
                detail = ev.get("detail", {}) or {}
                if stage == "mining_blocked" and mining_blocked is None:
                    mining_blocked = detail
                elif stage == "environmental_hazard" and hazard_event is None:
                    hazard_event = detail
                elif stage == "encounter_mining" and mining_detail_event is None:
                    mining_detail_event = detail

            subtype_id = None
            if mining_blocked and isinstance(mining_blocked, dict):
                subtype_id = mining_blocked.get("subtype_id")
            if (subtype_id is None) and hazard_event and isinstance(hazard_event, dict):
                subtype_id = hazard_event.get("subtype_id")
            if (subtype_id is None) and mining_detail_event and isinstance(mining_detail_event, dict):
                subtype_id = mining_detail_event.get("subtype_id")

            env_subtypes = {"asteroid_field", "comet_passage", "debris_storm"}

            if mining_blocked and subtype_id in env_subtypes:
                print("Deposits detected, but you lack mining equipment.")
            elif outcome == "mined" and subtype_id in env_subtypes:
                # Generic mined-result messaging; detailed quantities are visible via logs.
                print("Your crews conduct quick mining operations and recover materials.")

            # Always show hazard outcome for environmental mining subtypes.
            if hazard_event and subtype_id in env_subtypes:
                damage = int(hazard_event.get("damage", 0) or 0)
                hull_before = hazard_event.get("hull_before")
                hull_after = hazard_event.get("hull_after")
                if damage > 0:
                    if isinstance(hull_before, int) and isinstance(hull_after, int):
                        print(
                            f"Environmental hazards damage your hull for {damage} HP "
                            f"(hull {hull_before} → {hull_after})."
                        )
                    else:
                        print(f"Environmental hazards damage your hull for {damage} HP.")
                else:
                    print("You avoid serious damage from environmental hazards.")
            elif outcome not in {None, ""}:
                # Non-environmental exploration outcome (e.g., anomalies).
                print(f"The encounter resolves: {outcome}")
    else:
        # No resolver outcome - encounter ended normally
        if not result.get("hard_stop"):
            print("The encounter ends.")


def _resolve_pending_encounter(engine: GameEngine) -> None:
    """
    Handle a pending encounter decision. Forces player to resolve the encounter
    before returning. This function loops until the encounter is resolved.
    """
    while engine.has_pending_encounter():
        pending_info = engine.get_pending_encounter_info()
        if not pending_info:
            break
        
        print("\n--- ENCOUNTER ---")
        
        # Display encounter description
        encounter_description = pending_info.get("encounter_description")
        if encounter_description:
            print(f"Encounter: {encounter_description}")
        
        encounter_id = pending_info.get("encounter_id")
        if encounter_id:
            print(f"Encounter ID: {encounter_id}")
        
        # Display NPC ship info if available (hull name only for encounters)
        npc_ship_info = pending_info.get("npc_ship_info")
        npc_display_name = None
        if npc_ship_info:
            hull_name = npc_ship_info.get("hull_name", "Unknown")
            npc_display_name = _format_name_with_profile(npc_ship_info, hull_name, True)
            print(f"NPC Ship: {npc_display_name}")
        
        print()  # Blank line before options
        
        options = pending_info.get("options", [])
        if not options:
            print("No encounter options available.")
            break
        
        # Display numbered options
        for idx, opt in enumerate(options, start=1):
            label = opt.get("label", "Unknown")
            print(f"{idx}) {label}")
        
        choice = input("Select option: ").strip()
        decision_id = None
        
        # Try to match by number first
        try:
            choice_num = int(choice)
            if 1 <= choice_num <= len(options):
                decision_id = options[choice_num - 1].get("id")
        except ValueError:
            # Try to match by id or label
            for opt in options:
                if str(opt.get("id", "")) == choice or str(opt.get("label", "")).lower() == choice.lower():
                    decision_id = opt.get("id")
                    break
        
        if decision_id:
            result = engine.execute({
                "type": "encounter_decision",
                "encounter_id": pending_info.get("encounter_id"),
                "decision_id": decision_id,
            })
            
            # Check for game over
            if _is_game_over_result(result):
                _print_game_over(result)
                _game_over_loop(engine, result)
                return
            
            # Show NPC response in player-friendly format
            _show_encounter_result(result, encounter_description, npc_display_name=npc_display_name)
            _print_encounter_resolution_block(result, player_action=decision_id, encounter_description=encounter_description, engine=engine)
            
            # Immediate loot handling: if loot is pending, handle it before continuing
            if result.get("hard_stop") is True and result.get("hard_stop_reason") == "pending_loot_decision":
                pending_loot = engine.get_pending_loot()
                if pending_loot:
                    _handle_pending_loot(engine, pending_loot)
                    # After loot is resolved, check if we should continue to next encounter
                    # The engine will have set up the next encounter if any remain
                    continue
            
            # Check if result has another hard_stop (e.g., combat initiated)
            if result.get("hard_stop") is True:
                hard_stop_reason = result.get("hard_stop_reason")
                if hard_stop_reason == "pending_combat_action":
                    # Combat was initiated, resolve it
                    _resolve_pending_combat(engine)
                # Continue loop to check for next encounter
                continue
        else:
            print("Invalid selection. Please try again.")
            # Continue loop to force player to resolve encounter
            continue


def _resolve_pending_combat(engine: GameEngine) -> None:
    """
    Handle a pending combat action. Forces player to resolve combat
    before returning. This function loops until combat is resolved.
    """
    current_combat_seed_printed = False
    last_combat_seed = None
    
    while engine.has_pending_combat():
        pending_info = engine.get_pending_combat_info()
        if not pending_info:
            break
        
        # Safety check: detect invalid combat state
        invalid_state = pending_info.get("invalid_state", False)
        if invalid_state:
            error_msg = pending_info.get("error", "Unknown error")
            player_hull_max = pending_info.get("player_hull_max", 0)
            enemy_hull_max = pending_info.get("enemy_hull_max", 0)
            print("\n=== FATAL: INVALID COMBAT STATE ===")
            print(f"Error: {error_msg}")
            print(f"Player hull_max: {player_hull_max}")
            print(f"Enemy hull_max: {enemy_hull_max}")
            print("Combat cannot proceed. Breaking out of combat loop.")
            break
        
        # Safety check: detect 0% hull at round 1 (indicates initialization failure)
        round_number = pending_info.get("round_number", 1)
        if round_number < 1:
            round_number = 1
        player_hull_pct = pending_info.get("player_hull_pct", 0)
        enemy_hull_pct = pending_info.get("enemy_hull_pct", 0)
        if round_number == 1 and player_hull_pct == 0 and enemy_hull_pct == 0:
            player_hull_max = pending_info.get("player_hull_max", 0)
            enemy_hull_max = pending_info.get("enemy_hull_max", 0)
            print("\n=== FATAL: COMBAT INITIALIZATION FAILURE ===")
            print("Both player and enemy hull are at 0% at round 1.")
            print(f"Player hull_max: {player_hull_max}")
            print(f"Enemy hull_max: {enemy_hull_max}")
            print("This indicates invalid hull_id or assembly failure.")
            print("Combat cannot proceed. Breaking out of combat loop.")
            break
        
        allowed_actions = pending_info.get("allowed_actions", [])
        if not allowed_actions:
            print("No combat actions available.")
            break
        
        # Check for combat_rng_seed in pending_info or result (combat start detection)
        combat_seed = pending_info.get("combat_rng_seed")
        if combat_seed is not None and not current_combat_seed_printed:
            print("\n=== COMBAT START ===")
            print(f"combat_rng_seed: {combat_seed}")
            current_combat_seed_printed = True
            last_combat_seed = combat_seed
        
        # Extract labels from engine-provided allowed_actions (contract-correct)
        action_labels = [opt.get("label", "") for opt in allowed_actions]
        action_ids = [opt.get("id", "") for opt in allowed_actions]
        
        # Display menu using engine-provided labels (no hardcoding)
        action_label = _combat_action_menu(
            round_number=round_number,
            player_hull_pct=pending_info.get("player_hull_pct", 0),
            enemy_hull_pct=pending_info.get("enemy_hull_pct", 0),
            allowed_actions=action_labels,
            encounter_description=pending_info.get("encounter_description"),
            enemy_ship_info=pending_info.get("enemy_ship_info"),
        )
        
        # Map selected label back to action_id from engine payload
        action_id = None
        for idx, label in enumerate(action_labels):
            if label == action_label:
                action_id = action_ids[idx] if idx < len(action_ids) else None
                break
        
        if action_id:
            result = engine.execute({
                "type": "combat_action",
                "action": action_id,
                "encounter_id": pending_info.get("encounter_id"),
            })
            
            # Check for game over
            if _is_game_over_result(result):
                _print_game_over(result)
                _game_over_loop(engine, result)
                return
            
            # Check for engine errors and surface them
            if result.get("ok") is False:
                error_msg = result.get("error", "Unknown error")
                print(f"\n=== ERROR: Combat action failed ===")
                print(f"Error: {error_msg}")
                print("Breaking out of combat loop.")
                break
            
            # Immediate loot handling: if loot is pending, handle it before continuing
            if result.get("hard_stop") is True and result.get("hard_stop_reason") == "pending_loot_decision":
                pending_loot = engine.get_pending_loot()
                if pending_loot:
                    _handle_pending_loot(engine, pending_loot)
                    # After loot is resolved, check if combat continues or if we should break
                    # The engine will have set up the next encounter if any remain
                    if not engine.has_pending_combat():
                        # Combat ended and loot resolved - break out of combat loop
                        current_combat_seed_printed = False
                        break
                    # Combat may continue (shouldn't happen after loot, but handle gracefully)
                    continue
            
            # Safety check: detect if round_number did not advance (infinite loop prevention)
            if result.get("hard_stop") is True:
                next_pending = result.get("pending_combat")
                if next_pending:
                    next_round = next_pending.get("round_number", 0)
                    if next_round == round_number:
                        print("\n=== WARNING: COMBAT ROUND NOT ADVANCING ===")
                        print(f"Round number did not advance after action. Current: {round_number}, Next: {next_round}")
                        print("This may indicate an infinite loop. Breaking out of combat loop.")
                        print(f"Pending combat payload: {json.dumps(next_pending, sort_keys=True)}")
                        break
            
            # Check for combat_rng_seed in result (alternative detection path)
            result_seed = result.get("combat_rng_seed")
            if result_seed is not None and not current_combat_seed_printed:
                print("\n=== COMBAT START ===")
                print(f"combat_rng_seed: {result_seed}")
                current_combat_seed_printed = True
                last_combat_seed = result_seed
            
            # Check if combat ended
            if result.get("combat_ended") is True:
                # Combat ended - reset flags and break
                current_combat_seed_printed = False
                
                # Display combat result summary if available
                combat_result = result.get("combat_result")
                if combat_result:
                    outcome = combat_result.get("outcome", "unknown")
                    winner = combat_result.get("winner", "none")
                    rounds = combat_result.get("rounds", 0)
                    combat_rng_seed_final = combat_result.get("combat_rng_seed")
                    
                    print(f"\n--- COMBAT ENDED ---")
                    print(f"Outcome: {outcome}")
                    if winner != "none":
                        print(f"Winner: {winner}")
                    print(f"Rounds: {rounds}")
                    if combat_rng_seed_final is not None:
                        print(f"combat_rng_seed: {combat_rng_seed_final}")
                    
                    # Update last_combat_seed if available
                    if combat_rng_seed_final is not None:
                        last_combat_seed = combat_rng_seed_final
                
                # Offer replay
                if last_combat_seed is not None:
                    replay_choice = input("\nType R to replay last combat, or press Enter to continue: ").strip()
                    if replay_choice.upper() == "R":
                        # Replay: Note that full replay requires engine support for combat_rng_seed injection
                        # Since we cannot modify engine, we inform user of the seed for manual replay
                        print(f"Replay seed: {last_combat_seed}")
                        print("Note: Full replay requires engine support for combat_rng_seed injection.")
                        print("Combat inputs were not stored (engine-managed).")
                
                # Check if encounter decision needed
                if result.get("hard_stop") is True:
                    hard_stop_reason = result.get("hard_stop_reason")
                    if hard_stop_reason == "pending_encounter_decision":
                        _resolve_pending_encounter(engine)
                break
            
            # Check if result has another hard_stop (combat continues)
            if result.get("hard_stop") is True:
                hard_stop_reason = result.get("hard_stop_reason")
                if hard_stop_reason == "pending_encounter_decision":
                    # Combat ended, but encounter decision needed
                    _resolve_pending_encounter(engine)
                # Continue loop to check for next combat round
                continue
        else:
            print("Invalid action selection. Please try again.")
            # Continue loop to force player to resolve combat
            continue


def _handle_pending_loot(engine: GameEngine, loot_bundle: dict) -> None:
    """
    Handle pending loot prompt and application.
    
    Prompts player to accept or decline loot, then calls resolve_pending_loot.
    """
    # Get ship info for capacity display
    ship_info_result = engine.execute({"type": "get_player_profile"})
    if _is_game_over_result(ship_info_result):
        return
    ship_detail = _extract_detail_from_stage(step_result=ship_info_result, stage="player_profile")
    if not isinstance(ship_detail, dict):
        return
    
    physical_capacity = ship_detail.get("effective_physical_cargo_capacity", 0)
    data_capacity = ship_detail.get("effective_data_cargo_capacity", 0)
    current_cargo = ship_detail.get("cargo_manifest", {})
    
    # Calculate current cargo usage
    current_physical = 0
    current_data = 0
    for sku, qty in current_cargo.items():
        # Simple heuristic: check if SKU name suggests data (minimal, can be improved)
        # For now, assume all cargo is physical unless we have catalog access
        current_physical += int(qty)
    
    # Extract loot details (coerce None to 0/[] so comparisons never see None)
    credits = loot_bundle.get("credits") or 0
    cargo_sku = loot_bundle.get("cargo_sku")
    cargo_quantity = loot_bundle.get("cargo_quantity") or 0
    salvage_modules = loot_bundle.get("salvage_modules") or []
    salvage_count = len(salvage_modules)
    
    # Check if there's actually loot to offer
    has_loot = credits > 0 or (cargo_sku and cargo_quantity > 0) or salvage_count > 0
    
    if not has_loot:
        # No loot, clear and return
        engine.clear_pending_loot()
        return
    
    print("\n=== LOOT RECOVERED ===")
    if credits > 0:
        print(f"Credits: {credits}")
    if cargo_sku and cargo_quantity > 0:
        cargo_display = _get_good_display_name(engine, cargo_sku)
        print(f"Cargo: {cargo_display} x{cargo_quantity}")
    if salvage_count > 0:
        print(f"Salvage modules: {salvage_count}")
    print("----------------------")
    print("1) Take All")
    print("2) Leave Everything")
    
    choice = input("Select: ").strip()
    
    if choice == "1":
        # Accept all loot
        result = engine.resolve_pending_loot(take_all=True)
        if result.get("ok"):
            print("\nLoot applied successfully.")
            # Check if encounters should resume
            if result.get("resume_encounters"):
                # Engine will have pending encounter, CLI loop will handle it
                return
        else:
            error = result.get("error", "unknown")
            print(f"\nWARNING: Could not apply loot: {error}")
    else:
        # Decline all loot
        result = engine.resolve_pending_loot(take_all=False)
        if result.get("ok"):
            print("\nLoot declined.")
            # Check if encounters should resume
            if result.get("resume_encounters"):
                # Engine will have pending encounter, CLI loop will handle it
                return
        else:
            error = result.get("error", "unknown")
            print(f"\nWARNING: Could not clear loot: {error}")


def _travel_menu(engine: GameEngine) -> None:
    current_system_id = engine.player_state.current_system_id
    current_system = engine.sector.get_system(current_system_id)
    if current_system is None:
        print(json.dumps({"ok": False, "error": "current_system_not_found"}, sort_keys=True))
        return
    active_ship = engine.fleet_by_id.get(engine.player_state.active_ship_id)
    current_fuel = int(getattr(active_ship, "current_fuel", 0) or 0)

    while True:
        # Get current destination info
        current_destination = engine._current_destination()
        current_destination_id = engine.player_state.current_destination_id
        current_destination_name = current_destination.display_name if current_destination else "Unknown"
        display_name = _format_name_with_profile(
            current_destination or SimpleNamespace(emoji_id=None, tier=None, tags=[]),
            current_destination_name,
            True,
        )
        # Part 1: Display names instead of IDs
        system_name = _get_system_name(engine, current_system.system_id)
        print(f"Current system: {system_name}")
        print(f"Current destination: {display_name}")
        print("\n0) Back")
        print("1) Inter-system warp")
        print("2) Intra-system destination travel")
        mode = input("Travel mode: ").strip()

        if mode == "0":
            return
        elif mode == "1":
            # Part 4: Display map only when selecting Inter-system travel
            print("\n" + "="*60)
            print("GALAXY MAP")
            print("="*60)
            _render_galaxy_map(engine.sector, engine=engine)
            print("="*60 + "\n")
            
            reachable = _reachable_systems(engine=engine, current_system=current_system, fuel_limit=current_fuel)
            options = [row["system"] for row in reachable]
            if not options:
                print("No inter-system targets in range.")
                continue
            for index, row in enumerate(reachable, start=1):
                system_id = str(row["system_id"])
                system = row["system"]
                system_name_reachable = _get_system_name(engine, system_id)
                visited = system_id in _visited_system_ids(engine)
                display_name = _format_name_with_profile(system, system_name_reachable, visited)
                distance = row['distance_ly']
                in_range = distance <= float(current_fuel)
                # Part 1: Display system name instead of ID
                base = f"{index}) {display_name} (distance: {distance:.3f} ly, {'in range' if in_range else 'out of range'})"
                if not visited:
                    print(base)
                    continue
                live_situations = _active_system_situations(engine=engine, system_id=system_id)
                # Part 1: Show destination names with emoji profiles
                dest_displays = []
                for d in sorted(system.destinations, key=lambda x: x.destination_id):
                    vis = d.destination_id in _visited_destination_ids(engine)
                    dest_displays.append(_format_name_with_profile(d, d.display_name, vis))
                destinations_str = ", ".join(dest_displays) if dest_displays else "none"
                print(
                    f"{base}\n"
                    f"    Government: {getattr(system, 'government_id', 'Unknown')}, "
                    f"Population: {getattr(system, 'population', 'Unknown')}, "
                    f"Destinations: {destinations_str}"
                )
            raw_index = input("Select target system index: ").strip()
            try:
                selected = int(raw_index)
            except ValueError:
                print("Invalid system index.")
                continue
            if selected < 1 or selected > len(options):
                print("Invalid system index.")
                continue
            target_system = options[selected - 1]
            destinations = sorted(target_system.destinations, key=lambda entry: entry.destination_id)
            target_destination_id = destinations[0].destination_id if destinations else None
            payload: dict[str, object] = {
                "type": "travel_to_destination",
                "target_system_id": target_system.system_id,
            }
            if target_destination_id is not None:
                payload["target_destination_id"] = target_destination_id
            
            # Show travel start message
            target_name = target_system.name if hasattr(target_system, "name") else target_system.system_id
            target_visible = target_system.system_id in _visited_system_ids(engine)
            target_display = _format_name_with_profile(target_system, target_name, target_visible)
            print(f"\nTraveling to {target_system.system_id} ({target_display})...")
            
            result = engine.execute(payload)
            
            # Check for game over
            if _is_game_over_result(result):
                _print_game_over(result)
                _game_over_loop(engine, result)
                return
            
            # Show travel completion if no hard stops
            if not result.get("hard_stop"):
                print(f"Arrived at {target_system.system_id} ({target_display})")
            
            # Handle hard_stop responses (pending encounters or combat)
            # Per interaction_layer_contract.md: all encounters must be resolved before travel continues
            hard_stop_iterations = 0
            while result.get("hard_stop") is True:
                hard_stop_iterations += 1
                if hard_stop_iterations > 100:
                    print("ERROR: Hard stop loop exceeded safe iteration limit.")
                    break
                
                # Check if combat ended - show result and break
                if result.get("combat_ended") is True:
                    combat_result = result.get("combat_result", {})
                    if combat_result:
                        winner = combat_result.get("winner", "unknown")
                        if winner == "player":
                            print("You win the combat!")
                        elif winner == "enemy":
                            print("You lost the combat.")
                        else:
                            print("Combat ended.")
                    break
                
                hard_stop_reason = result.get("hard_stop_reason")
                
                # Handle pending encounter decision - MUST resolve before continuing
                if hard_stop_reason == "pending_encounter_decision":
                    pending_encounter = result.get("pending_encounter")
                    if pending_encounter:
                        print("\n--- ENCOUNTER ---")
                        options = pending_encounter.get("options", [])
                        if not options:
                            print("No encounter options available.")
                            break
                        # Display numbered options
                        for idx, opt in enumerate(options, start=1):
                            label = opt.get("label", "Unknown")
                            print(f"{idx}) {label}")
                        choice = input("Select option: ").strip()
                        decision_id = None
                        # Try to match by number first
                        try:
                            choice_num = int(choice)
                            if 1 <= choice_num <= len(options):
                                decision_id = options[choice_num - 1].get("id")
                        except ValueError:
                            # Try to match by id or label
                            for opt in options:
                                if str(opt.get("id", "")) == choice or str(opt.get("label", "")).lower() == choice.lower():
                                    decision_id = opt.get("id")
                                    break
                        if decision_id:
                            result = engine.execute({
                                "type": "encounter_decision",
                                "encounter_id": pending_encounter.get("encounter_id"),
                                "decision_id": decision_id,
                            })
                            
                            # Show NPC response
                            enc_desc = pending_encounter.get("encounter_description", "Unknown")
                            _show_encounter_result(result, enc_desc)
                            _print_encounter_resolution_block(result, player_action=decision_id, encounter_description=enc_desc, engine=engine)
                            
                            # Continue loop to check for next hard_stop (may be another encounter or combat)
                            continue
                        else:
                            print("Invalid selection. Please try again.")
                            # Don't return - force player to resolve encounter
                            continue
                    else:
                        # No pending_encounter payload - break to avoid infinite loop
                        break
                
                # Handle pending combat action - MUST resolve before continuing
                elif hard_stop_reason == "pending_combat_action":
                    # Defensive guard: do not prompt if combat already ended
                    if result.get("combat_ended") is True:
                        break
                    
                    pending_combat = result.get("pending_combat")
                    if pending_combat:
                        allowed_actions = pending_combat.get("allowed_actions", [])
                        if not allowed_actions:
                            print("No combat actions available.")
                            break
                        
                        # Get round number (enforce 1-indexed, no round 0)
                        round_number = pending_combat.get("round_number", 1)
                        if round_number < 1:
                            round_number = 1
                        
                        # Extract labels from engine-provided allowed_actions (contract-correct)
                        action_labels = [opt.get("label", "") for opt in allowed_actions]
                        action_ids = [opt.get("id", "") for opt in allowed_actions]
                        
                        # Display menu using engine-provided labels (no hardcoding)
                        action_label = _combat_action_menu(
                            round_number=round_number,
                            player_hull_pct=pending_combat.get("player_hull_pct", 0),
                            enemy_hull_pct=pending_combat.get("enemy_hull_pct", 0),
                            allowed_actions=action_labels,
                        )
                        
                        # Map selected label back to action_id from engine payload
                        action_id = None
                        for idx, label in enumerate(action_labels):
                            if label == action_label:
                                action_id = action_ids[idx] if idx < len(action_ids) else None
                                break
                        
                        if action_id:
                            result = engine.execute({
                                "type": "combat_action",
                                "action": action_id,
                                "encounter_id": pending_combat.get("encounter_id"),
                            })
                            
                            # Check for game over
                            if _is_game_over_result(result):
                                _print_game_over(result)
                                _game_over_loop(engine, result)
                                return
                            
                            # Check for engine errors and surface them
                            if result.get("ok") is False:
                                error_msg = result.get("error", "Unknown error")
                                print(f"\n=== ERROR: Combat action failed ===")
                                print(f"Error: {error_msg}")
                                print("Breaking out of combat loop.")
                                break
                            
                            # Check if combat ended - break immediately
                            if result.get("combat_ended") is True:
                                break
                            
                            # Continue loop to check for next hard_stop (combat may continue or end)
                            continue
                        else:
                            print("Invalid action selection. Please try again.")
                            # Don't return - force player to resolve combat
                            continue
                    else:
                        # No pending_combat payload - break to avoid infinite loop
                        break
                else:
                    # Unknown hard_stop_reason - break to avoid infinite loop
                    break
            
            _format_result(result, "location_action")
            if result.get("ok") is True and result.get("player", {}).get("system_id") == target_system.system_id:
                sys_visible = target_system.system_id in _visited_system_ids(engine)
                system_display = _format_name_with_profile(target_system, target_system.name, sys_visible)
                print(f"You have arrived in {system_display}.")
                _print_current_system_destinations(engine)
            return
        elif mode == "2":
            destinations = sorted(current_system.destinations, key=lambda entry: entry.destination_id)
            if not destinations:
                print("No intra-system destinations available.")
                continue
            for index, destination in enumerate(destinations, start=1):
                visible = destination.destination_id in _visited_destination_ids(engine)
                display_name = _format_name_with_profile(
                    destination,
                    destination.display_name,
                    visible,
                )
                print(f"{index}) {destination.destination_id} {display_name} ({destination.destination_type})")
            raw_index = input("Select destination index: ").strip()
            try:
                selected = int(raw_index)
            except ValueError:
                print("Invalid destination index.")
                continue
            if selected < 1 or selected > len(destinations):
                print("Invalid destination index.")
                continue
            payload = {
                "type": "travel_to_destination",
                "target_system_id": current_system.system_id,
                "target_destination_id": destinations[selected - 1].destination_id,
            }
            result = engine.execute(payload)
            
            # Check for game over
            if _is_game_over_result(result):
                _print_game_over(result)
                _game_over_loop(engine, result)
                return
            
            # Handle hard_stop responses (pending encounters or combat)
            # Per interaction_layer_contract.md: all encounters must be resolved before travel continues
            hard_stop_iterations = 0
            while result.get("hard_stop") is True:
                hard_stop_iterations += 1
                if hard_stop_iterations > 100:
                    print("ERROR: Hard stop loop exceeded safe iteration limit.")
                    break
                
                # Check if combat ended - show result and break
                if result.get("combat_ended") is True:
                    combat_result = result.get("combat_result", {})
                    if combat_result:
                        winner = combat_result.get("winner", "unknown")
                        if winner == "player":
                            print("You win the combat!")
                        elif winner == "enemy":
                            print("You lost the combat.")
                        else:
                            print("Combat ended.")
                    break
                
                hard_stop_reason = result.get("hard_stop_reason")
                
                # Handle pending encounter decision - MUST resolve before continuing
                if hard_stop_reason == "pending_encounter_decision":
                    pending_encounter = result.get("pending_encounter")
                    if pending_encounter:
                        print("\n--- ENCOUNTER ---")
                        options = pending_encounter.get("options", [])
                        if not options:
                            print("No encounter options available.")
                            break
                        # Display numbered options
                        for idx, opt in enumerate(options, start=1):
                            label = opt.get("label", "Unknown")
                            print(f"{idx}) {label}")
                        choice = input("Select option: ").strip()
                        decision_id = None
                        # Try to match by number first
                        try:
                            choice_num = int(choice)
                            if 1 <= choice_num <= len(options):
                                decision_id = options[choice_num - 1].get("id")
                        except ValueError:
                            # Try to match by id or label
                            for opt in options:
                                if str(opt.get("id", "")) == choice or str(opt.get("label", "")).lower() == choice.lower():
                                    decision_id = opt.get("id")
                                    break
                        if decision_id:
                            result = engine.execute({
                                "type": "encounter_decision",
                                "encounter_id": pending_encounter.get("encounter_id"),
                                "decision_id": decision_id,
                            })
                            # Check for game over
                            if _is_game_over_result(result):
                                _print_game_over(result)
                                _game_over_loop(engine, result)
                                return
                            # Continue loop to check for next hard_stop (may be another encounter or combat)
                            continue
                        else:
                            print("Invalid selection. Please try again.")
                            # Don't return - force player to resolve encounter
                            continue
                    else:
                        # No pending_encounter payload - break to avoid infinite loop
                        break
                
                # Handle pending combat action - MUST resolve before continuing
                elif hard_stop_reason == "pending_combat_action":
                    # Defensive guard: do not prompt if combat already ended
                    if result.get("combat_ended") is True:
                        break
                    
                    pending_combat = result.get("pending_combat")
                    if pending_combat:
                        allowed_actions = pending_combat.get("allowed_actions", [])
                        if not allowed_actions:
                            print("No combat actions available.")
                            break
                        
                        # Get round number (enforce 1-indexed, no round 0)
                        round_number = pending_combat.get("round_number", 1)
                        if round_number < 1:
                            round_number = 1
                        
                        # Extract labels from engine-provided allowed_actions (contract-correct)
                        action_labels = [opt.get("label", "") for opt in allowed_actions]
                        action_ids = [opt.get("id", "") for opt in allowed_actions]
                        
                        # Display menu using engine-provided labels (no hardcoding)
                        action_label = _combat_action_menu(
                            round_number=round_number,
                            player_hull_pct=pending_combat.get("player_hull_pct", 0),
                            enemy_hull_pct=pending_combat.get("enemy_hull_pct", 0),
                            allowed_actions=action_labels,
                        )
                        
                        # Map selected label back to action_id from engine payload
                        action_id = None
                        for idx, label in enumerate(action_labels):
                            if label == action_label:
                                action_id = action_ids[idx] if idx < len(action_ids) else None
                                break
                        
                        if action_id:
                            result = engine.execute({
                                "type": "combat_action",
                                "action": action_id,
                                "encounter_id": pending_combat.get("encounter_id"),
                            })
                            
                            # Check for game over
                            if _is_game_over_result(result):
                                _print_game_over(result)
                                _game_over_loop(engine, result)
                                return
                            
                            # Check for engine errors and surface them
                            if result.get("ok") is False:
                                error_msg = result.get("error", "Unknown error")
                                print(f"\n=== ERROR: Combat action failed ===")
                                print(f"Error: {error_msg}")
                                print("Breaking out of combat loop.")
                                break
                            
                            # Check if combat ended - break immediately
                            if result.get("combat_ended") is True:
                                break
                            
                            # Continue loop to check for next hard_stop (combat may continue or end)
                            continue
                        else:
                            print("Invalid action selection. Please try again.")
                            # Don't return - force player to resolve combat
                            continue
                    else:
                        # No pending_combat payload - break to avoid infinite loop
                        break
                else:
                    # Unknown hard_stop_reason - break to avoid infinite loop
                    break
            
            _format_result(result, "location_action")
            return
        else:
            print("Invalid selection.")
            continue


def _wait_menu(engine: GameEngine) -> None:
    raw = input("Days to wait (1..10): ").strip()
    try:
        days = int(raw)
    except ValueError:
        days = 1
    result = engine.execute({"type": "wait", "days": days})
    if _is_game_over_result(result):
        _print_game_over(result)
        _game_over_loop(engine, result)
        return
    _format_result(result, "location_action")


def _location_entry_menu(engine: GameEngine) -> None:
    while True:
        destination = _current_destination_object(engine)
        if destination is None:
            print("No locations available.")
            return
        locations = list(getattr(destination, "locations", []) or [])
        if not locations:
            print("No locations available.")
            return

        print("0) Back")
        location_by_index: dict[int, object] = {}
        for index, location in enumerate(locations, start=1):
            location_by_index[index] = location
            loc_type = str(getattr(location, "location_type", "") or "")
            loc_id = str(getattr(location, "location_id", "") or "")
            name = loc_id or loc_type or "Unknown"
            location_entity = SimpleNamespace(
                emoji_id=f"location_{loc_type}" if loc_type else None,
                tier=None,
                tags=[],
            )
            display = _format_name_with_profile(location_entity, name, True)
            print(f"{index}) {display}")
        raw_index = input("Select location index: ").strip()
        if raw_index == "0":
            return
        try:
            selected = int(raw_index)
        except ValueError:
            print("Invalid location index.")
            continue
        if selected < 1 or selected > len(locations):
            print("Invalid location index.")
            continue
        selected_location = location_by_index[selected]
        result = engine.execute({"type": "enter_location", "location_index": selected})
        if _is_game_over_result(result):
            _print_game_over(result)
            _game_over_loop(engine, result)
            return
        if result.get("ok") is False:
            print("Unable to enter location.")
            continue
        print(f"Entered location: {engine.player_state.current_location_id}")

        location_type = str(getattr(selected_location, "location_type", "") or "")
        if location_type == "market":
            _market_location_menu(engine)
            return
        if location_type == "datanet":
            _datanet_location_menu(engine)
            return
        if location_type == "warehouse":
            _warehouse_location_menu(engine)
            return
        if location_type in {"bar", "administration"}:
            _npc_first_location_menu(engine)
            return
        _location_actions_menu(engine)
        return


def _location_actions_menu(engine: GameEngine) -> None:
    # Check if this is a shipdock location
    list_result = engine.execute({"type": "list_location_actions"})
    actions = _extract_actions_from_step_result(list_result)
    is_shipdock = any(
        action.get("action_id") in {"buy_hull", "buy_module", "sell_hull", "sell_module", "repair_ship"}
        for action in actions
    )
    
    if is_shipdock:
        _shipdock_menu(engine)
        return
    
    # Non-shipdock location actions (original flow)
    while True:
        list_result = engine.execute({"type": "list_location_actions"})
        actions = _extract_actions_from_step_result(list_result)
        print(f"LOCATION: {engine.player_state.current_location_id}")
        if not actions:
            print("No actions available at this location.")
            print("1) Return to Destination")
            if input("Select action index: ").strip() == "1":
                _return_to_destination(engine)
                print(f"Returned to destination: {engine.player_state.current_location_id}")
                return
            print("Invalid action index.")
            continue
        for index, action in enumerate(actions, start=1):
            display = _format_name_with_profile(action, str(action.get("display_name", "") or ""), True)
            print(f"{index}) {display}")
        return_index = len(actions) + 1
        print(f"{return_index}) Return to Destination")

        raw_action = input("Select action index: ").strip()
        try:
            selected = int(raw_action)
        except ValueError:
            print("Invalid action index.")
            continue
        if selected == return_index:
            _return_to_destination(engine)
            print(f"Returned to destination: {engine.player_state.current_location_id}")
            return
        if selected < 1 or selected > len(actions):
            print("Invalid action index.")
            continue
        selected_action = actions[selected - 1]
        
        # Collect parameters if action has them
        action_kwargs = {}
        if selected_action.get("parameters"):
            action_kwargs = _prompt_action_kwargs(selected_action)
        
        # Handle confirmation if required
        confirmed = True
        if selected_action.get("requires_confirm"):
            confirmed = input("Confirm action? (y/n): ").strip().lower() == "y"
            if not confirmed:
                print("Action cancelled.")
                continue
        
        payload = {
            "type": "location_action",
            "action_id": selected_action["action_id"],
            "kwargs": action_kwargs,
            "confirm": confirmed,
        }
        result = engine.execute(payload)
        _format_result(result, "location_action")


def _current_location_type(engine: GameEngine) -> str | None:
    """Get the location_type of the current location."""
    destination = _current_destination_object(engine)
    if destination is None:
        return None
    location_id = engine.player_state.current_location_id
    if not location_id:
        return None
    locations = list(getattr(destination, "locations", []) or [])
    for location in locations:
        if getattr(location, "location_id", None) == location_id:
            return str(getattr(location, "location_type", "") or "")
    return None


def _npc_first_location_menu(engine: GameEngine) -> None:
    while True:
        list_result = engine.execute({"type": "list_location_npcs"})
        detail = _extract_detail_from_stage(step_result=list_result, stage="location_npcs") or {}
        npcs = detail.get("npcs", [])
        if not isinstance(npcs, list):
            npcs = []
        
        location_type = _current_location_type(engine)
        is_administration = location_type == "administration"
        
        print(f"LOCATION: {engine.player_state.current_location_id}")
        
        # Get location actions for administration (filtered to admin_mission_board only)
        location_actions: list[dict[str, object]] = []
        if is_administration:
            list_actions_result = engine.execute({"type": "list_location_actions"})
            all_actions = _extract_actions_from_step_result(list_actions_result)
            location_actions = [a for a in all_actions if isinstance(a, dict) and str(a.get("action_id", "")) == "admin_mission_board"]
        
        if not npcs and not location_actions:
            print("No NPCs or actions present.")
            print("0) Return to destination")
            if input("Select option: ").strip() == "0":
                _return_to_destination(engine)
                print(f"Returned to destination: {engine.player_state.current_location_id}")
                return
            print("Invalid selection.")
            continue
        
        # Display NPCs
        npc_count = 0
        if npcs:
            print("NPCs:")
            for index, row in enumerate(npcs, start=1):
                if not isinstance(row, dict):
                    continue
                name = str(row.get("display_name", "Unknown"))
                display = _format_name_with_profile(row, name, True)
                role = str(row.get("role", "unknown"))
                print(f"  {index}) {display} ({role})")
                npc_count = index
        
        # Display Location Actions (administration only, filtered to admin_mission_board)
        action_start_index = npc_count + 1
        if location_actions:
            print("Location Actions:")
            for action in location_actions:
                if not isinstance(action, dict):
                    continue
                action_id = str(action.get("action_id", ""))
                display_name = str(action.get("display_name", action_id))
                display = _format_name_with_profile(action, display_name, True)
                print(f"  {action_start_index}) {display}")
                action_start_index += 1
        
        print("0) Return to destination")
        raw_choice = input("Select option: ").strip()
        if raw_choice == "0":
            _return_to_destination(engine)
            print(f"Returned to destination: {engine.player_state.current_location_id}")
            return
        try:
            selected = int(raw_choice)
        except ValueError:
            print("Invalid selection.")
            continue
        
        # Handle NPC selection
        if 1 <= selected <= npc_count:
            row = npcs[selected - 1]
            if not isinstance(row, dict):
                print("Invalid NPC selection.")
                continue
            npc_id = row.get("npc_id")
            if not isinstance(npc_id, str) or not npc_id:
                print("Invalid NPC selection.")
                continue
            _npc_interactions_menu(engine, npc_id=npc_id)
            continue
        
        # Handle Location Action selection (administration only)
        action_index = selected - npc_count - 1
        if 0 <= action_index < len(location_actions):
            action = location_actions[action_index]
            if not isinstance(action, dict):
                print("Invalid action selection.")
                continue
            action_id = str(action.get("action_id", ""))
            if not action_id:
                print("Invalid action selection.")
                continue
            # Execute location action
            if action_id == "admin_mission_board":
                # Special handling for mission board: allow direct mission acceptance
                action_kwargs = {}
                if action.get("parameters"):
                    action_kwargs = _prompt_action_kwargs(action)
                confirmed = True
                if action.get("requires_confirm"):
                    confirmed = input("Confirm action? (y/n): ").strip().lower() == "y"
                    if not confirmed:
                        print("Action cancelled.")
                        continue
                payload = {"type": "location_action", "action_id": action_id, "kwargs": action_kwargs, "confirm": confirmed}
                result = engine.execute(payload)
                if result.get("ok"):
                    # Extract missions from result["detail"]["missions"] or from events
                    missions = []
                    # First try result["detail"]["missions"]
                    detail = result.get("detail", {})
                    if isinstance(detail, dict):
                        missions_raw = detail.get("missions")
                        if isinstance(missions_raw, list):
                            missions = missions_raw
                    # If not found, try extracting from events
                    if not missions:
                        event_detail = _extract_detail_from_stage(step_result=result, stage="location_action")
                        if event_detail and isinstance(event_detail, dict):
                            missions_raw = event_detail.get("missions")
                            if isinstance(missions_raw, list):
                                missions = missions_raw
                    # Only print "No missions available" if missions list is empty
                    if len(missions) == 0:
                        print("No missions available on the board.")
                        continue
                    # Display numbered list
                    print("MISSION BOARD")
                    for index, mission in enumerate(missions, start=1):
                        mission_type = mission.get("mission_type", "Unknown")
                        mission_tier = mission.get("mission_tier", 0)
                        # Use reward_summary_lines from mission_core.list_offered
                        reward_lines = mission.get("reward_summary_lines", [])
                        if reward_lines:
                            reward_text = ", ".join(reward_lines)
                        else:
                            reward_text = "No rewards"
                        print(f"  {index}) {mission_type} (Tier {mission_tier}) – {reward_text}")
                    print()
                    # Prompt for selection
                    raw_choice = input("Select mission index to discuss (0 to cancel): ").strip()
                    if raw_choice == "0":
                        continue
                    try:
                        selected = int(raw_choice)
                    except ValueError:
                        print("Invalid selection.")
                        continue
                    if selected < 1 or selected > len(missions):
                        print("Invalid selection.")
                        continue
                    # Get mission_id from selected mission
                    selected_mission = missions[selected - 1]
                    mission_id = selected_mission.get("mission_id")
                    if not isinstance(mission_id, str) or not mission_id:
                        print("Invalid mission selection.")
                        continue
                    # Call MissionCore.get_details via engine command
                    discuss_result = engine.execute({"type": "mission_discuss", "mission_id": mission_id})
                    if not discuss_result.get("ok"):
                        print(f"Failed to discuss mission: {discuss_result.get('error', 'unknown error')}")
                        continue
                    # Extract mission details from discuss result
                    discuss_detail = _extract_detail_from_stage(step_result=discuss_result, stage="mission")
                    if discuss_detail and isinstance(discuss_detail, dict):
                        result_data = discuss_detail.get("result", {})
                        if isinstance(result_data, dict):
                            # Get the actual mission entity to access objectives and full details - NO RECALCULATION
                            mission_id_from_result = result_data.get("mission_id")
                            if mission_id_from_result:
                                try:
                                    # Get full mission entity from manager - use existing data only
                                    mission_manager = engine._mission_manager
                                    mission_entity = mission_manager.missions.get(mission_id_from_result)
                                    
                                    if mission_entity:
                                        # Convert to dict for formatting functions - use existing data
                                        mission_dict = mission_entity.to_dict()
                                        # Use reward_summary_lines from get_details result (already calculated)
                                        mission_dict["reward_summary_lines"] = result_data.get("reward_summary_lines", [])
                                    else:
                                        mission_dict = result_data
                                except Exception:  # noqa: BLE001
                                    mission_dict = result_data
                            else:
                                mission_dict = result_data
                            
                            # Mission Title
                            title = mission_dict.get("name") or mission_dict.get("mission_type", "Mission")
                            print(f"\n{'='*60}")
                            print(f"MISSION: {title}")
                            print(f"{'='*60}")
                            
                            # Provider Name (Part 2) with emoji profile
                            provider_npc_id = mission_dict.get("mission_giver_npc_id")
                            if provider_npc_id:
                                provider_name = _get_npc_name(engine, provider_npc_id)
                                provider_npc = None
                                try:
                                    nr = getattr(engine, "_npc_registry", None)
                                    if nr:
                                        provider_npc = nr.get_npc(provider_npc_id)
                                except Exception:  # noqa: BLE001
                                    pass
                                provider_display = _format_name_with_profile(provider_npc, provider_name, True) if provider_npc is not None else provider_name
                                print(f"Provider: {provider_display}")
                            
                            # Mission Description (Part 2 & 5)
                            description = mission_dict.get("description") or mission_dict.get("text", "")
                            if description:
                                print(f"\n{description}\n")
                            
                            # Mission Type and Tier
                            mission_type = mission_dict.get("mission_type", "Unknown")
                            mission_tier = mission_dict.get("mission_tier", 0)
                            print(f"Type: {mission_type} (Tier {mission_tier})")
                            
                            # Destination Name (Part 1) with emoji profiles
                            target_destination_id = mission_dict.get("target_destination_id")
                            target_system_id = mission_dict.get("target_system_id")
                            if target_destination_id:
                                dest_name = _get_destination_name(engine, target_destination_id)
                                dest_obj = _get_destination_object(engine, target_destination_id)
                                dest_visible = target_destination_id in _visited_destination_ids(engine)
                                dest_display = _format_name_with_profile(
                                    dest_obj or SimpleNamespace(emoji_id=None, tier=None, tags=[]),
                                    dest_name,
                                    dest_visible,
                                )
                                if target_system_id:
                                    system_name = _get_system_name(engine, target_system_id)
                                    system_obj = engine.sector.get_system(target_system_id)
                                    sys_visible = target_system_id in _visited_system_ids(engine)
                                    system_display = _format_name_with_profile(
                                        system_obj or SimpleNamespace(emoji_id=None, tier=None, tags=[]),
                                        system_name,
                                        sys_visible,
                                    )
                                    print(f"Destination: {dest_display} ({system_display})")
                                else:
                                    print(f"Destination: {dest_display}")
                            elif target_system_id:
                                system_name = _get_system_name(engine, target_system_id)
                                system_obj = engine.sector.get_system(target_system_id)
                                sys_visible = target_system_id in _visited_system_ids(engine)
                                system_display = _format_name_with_profile(
                                    system_obj or SimpleNamespace(emoji_id=None, tier=None, tags=[]),
                                    system_name,
                                    sys_visible,
                                )
                                print(f"Target System: {system_display}")
                            
                            # Objectives (Part 2 & 3) - from mission entity, NO RECALCULATION
                            objective_lines = _format_mission_objectives(engine, mission_dict)
                            if objective_lines:
                                print(f"\nObjectives:")
                                for obj_line in objective_lines:
                                    print(f"  • {obj_line}")
                            
                            # Rewards (Part 2) - use reward_summary_lines from get_details (already calculated)
                            reward_lines = _format_mission_rewards(engine, mission_dict)
                            if reward_lines:
                                print(f"\nRewards:")
                                for reward_line in reward_lines:
                                    print(f"  • {reward_line}")
                            
                            # Status
                            status = mission_dict.get("status")
                            offer_only = result_data.get("offer_only", False)
                            if status:
                                print(f"\nStatus: {status}")
                            
                            print(f"\n{'='*60}\n")
                            
                            # Only prompt for acceptance if offer_only is True
                            if offer_only:
                                confirm = input("Accept this mission? (y/n): ").strip().lower()
                                if confirm == "y":
                                    # Call MissionCore.accept via engine command
                                    accept_result = engine.execute({"type": "mission_accept", "mission_id": mission_id})
                                    if accept_result.get("ok"):
                                        accept_detail = _extract_detail_from_stage(step_result=accept_result, stage="mission")
                                        if accept_detail and isinstance(accept_detail, dict):
                                            if accept_detail.get("accepted"):
                                                print(f"Mission accepted: {mission_id}")
                                            else:
                                                print(f"Mission accept result: {json.dumps(accept_detail, sort_keys=True)}")
                                        else:
                                            print(f"Mission accepted: {mission_id}")
                                    else:
                                        error = accept_result.get('error', 'unknown error')
                                        if error == "mission_accept_failed_total_cap":
                                            print("Cannot accept: total mission limit reached.")
                                        elif error == "mission_accept_failed_tier_cap":
                                            print("Cannot accept: tier limit reached.")
                                        else:
                                            print(f"Failed to accept mission: {error}")
                                else:
                                    print("Mission discussion cancelled.")
                            else:
                                # Mission is not in OFFERED state, cannot accept
                                print("This mission cannot be accepted at this time.")
                    else:
                        print("Failed to retrieve mission details.")
                else:
                    print(f"Action failed: {result.get('error', 'unknown error')}")
            else:
                action_kwargs = {}
                if action.get("parameters"):
                    action_kwargs = _prompt_action_kwargs(action)
                confirmed = True
                if action.get("requires_confirm"):
                    confirmed = input("Confirm action? (y/n): ").strip().lower() == "y"
                    if not confirmed:
                        print("Action cancelled.")
                        continue
                payload = {"type": "location_action", "action_id": action_id, "kwargs": action_kwargs, "confirm": confirmed}
                result = engine.execute(payload)
                if result.get("ok"):
                    detail = _extract_detail_from_stage(step_result=result, stage="location_action")
                    if detail and detail.get("missions"):
                        missions = detail.get("missions", [])
                        print("Available Missions:")
                        for mission in missions:
                            if isinstance(mission, dict):
                                print(f"  Mission ID: {mission.get('mission_id')}")
                                print(f"  Type: {mission.get('mission_type')}")
                                print(f"  Tier: {mission.get('mission_tier')}")
                                print(f"  Rewards: {mission.get('rewards')}")
                                print()
                else:
                    print(f"Action failed: {result.get('error', 'unknown error')}")
            continue
        
        print("Invalid selection.")


def _npc_interactions_menu(engine: GameEngine, *, npc_id: str) -> None:
    while True:
        list_result = engine.execute({"type": "list_npc_interactions", "npc_id": npc_id})
        detail = _extract_detail_from_stage(step_result=list_result, stage="npc_interactions") or {}
        interactions = detail.get("interactions", [])
        if not isinstance(interactions, list):
            interactions = []
        # Part 1: Display NPC name with profile
        npc_name = _get_npc_name(engine, npc_id)
        npc = None
        try:
            npc_registry = getattr(engine, "_npc_registry", None)
            if npc_registry:
                npc = npc_registry.get_npc(npc_id)
        except Exception:  # noqa: BLE001
            pass
        npc_display = _format_name_with_profile(npc, npc_name, True) if npc is not None else npc_name
        print(f"NPC: {npc_display}")
        for index, row in enumerate(interactions, start=1):
            if not isinstance(row, dict):
                continue
            display = _format_name_with_profile(row, str(row.get("display_name", "") or ""), True)
            print(f"{index}) {display}")
        print("0) Back")
        raw_choice = input("Select interaction index: ").strip()
        if raw_choice == "0":
            return
        try:
            selected = int(raw_choice)
        except ValueError:
            print("Invalid interaction index.")
            continue
        if selected < 1 or selected > len(interactions):
            print("Invalid interaction index.")
            continue
        action = interactions[selected - 1]
        if not isinstance(action, dict):
            print("Invalid interaction index.")
            continue
        interaction_id = action.get("action_id")
        if not isinstance(interaction_id, str) or not interaction_id:
            print("Invalid interaction selection.")
            continue
        result = engine.execute({"type": "npc_interact", "npc_id": npc_id, "interaction_id": interaction_id})
        detail_out = _extract_detail_from_stage(step_result=result, stage="npc_interaction") or {}
        interaction_result = detail_out.get("result")
        if isinstance(interaction_result, dict):
            if isinstance(interaction_result.get("rumor_type"), str):
                print(f"Rumor type: {interaction_result.get('rumor_type')}")
                print(f"Rumor: {interaction_result.get('rumor_text')}")
                hint = interaction_result.get("hint")
                if isinstance(hint, dict):
                    system_id = hint.get("system_id")
                    destination_id = hint.get("destination_id")
                    if isinstance(system_id, str) and system_id:
                        if isinstance(destination_id, str) and destination_id:
                            print(f"Hint: system={system_id} destination={destination_id}")
                        else:
                            print(f"Hint: system={system_id}")
            elif interaction_result.get("offer_only") is True:
                # Mission offer - show full details like mission board - NO RECALCULATION
                mission_id = interaction_result.get("mission_id")
                if mission_id:
                    # Get full mission details via mission_discuss (uses existing calculated data)
                    discuss_result = engine.execute({"type": "mission_discuss", "mission_id": mission_id})
                    if discuss_result.get("ok"):
                        discuss_detail = _extract_detail_from_stage(step_result=discuss_result, stage="mission")
                        if discuss_detail and isinstance(discuss_detail, dict):
                            result_data = discuss_detail.get("result", {})
                            if isinstance(result_data, dict):
                                # Get the actual mission entity - use existing data only
                                try:
                                    mission_manager = engine._mission_manager
                                    mission_entity = mission_manager.missions.get(mission_id)
                                    
                                    if mission_entity:
                                        mission_dict = mission_entity.to_dict()
                                        # Use reward_summary_lines from get_details (already calculated)
                                        mission_dict["reward_summary_lines"] = result_data.get("reward_summary_lines", [])
                                    else:
                                        mission_dict = result_data
                                except Exception:  # noqa: BLE001
                                    mission_dict = result_data
                                
                                # Display mission details with proper formatting
                                title = mission_dict.get("name") or mission_dict.get("mission_type", "Mission")
                                print(f"\n{'='*60}")
                                print(f"MISSION: {title}")
                                print(f"{'='*60}")
                                
                                provider_npc_id = mission_dict.get("mission_giver_npc_id")
                                if provider_npc_id:
                                    provider_name = _get_npc_name(engine, provider_npc_id)
                                    provider_npc = None
                                    try:
                                        nr = getattr(engine, "_npc_registry", None)
                                        if nr:
                                            provider_npc = nr.get_npc(provider_npc_id)
                                    except Exception:  # noqa: BLE001
                                        pass
                                    provider_display = _format_name_with_profile(provider_npc, provider_name, True) if provider_npc is not None else provider_name
                                    print(f"Provider: {provider_display}")
                                
                                description = mission_dict.get("description") or mission_dict.get("text", "")
                                if description:
                                    print(f"\n{description}\n")
                                
                                mission_type = mission_dict.get("mission_type", "Unknown")
                                mission_tier = mission_dict.get("mission_tier", 0)
                                print(f"Type: {mission_type} (Tier {mission_tier})")
                                
                                target_destination_id = mission_dict.get("target_destination_id")
                                target_system_id = mission_dict.get("target_system_id")
                                if target_destination_id:
                                    dest_name = _get_destination_name(engine, target_destination_id)
                                    dest_obj = _get_destination_object(engine, target_destination_id)
                                    dest_visible = target_destination_id in _visited_destination_ids(engine)
                                    dest_display = _format_name_with_profile(
                                        dest_obj or SimpleNamespace(emoji_id=None, tier=None, tags=[]),
                                        dest_name,
                                        dest_visible,
                                    )
                                    if target_system_id:
                                        system_name = _get_system_name(engine, target_system_id)
                                        system_obj = engine.sector.get_system(target_system_id)
                                        sys_visible = target_system_id in _visited_system_ids(engine)
                                        system_display = _format_name_with_profile(
                                            system_obj or SimpleNamespace(emoji_id=None, tier=None, tags=[]),
                                            system_name,
                                            sys_visible,
                                        )
                                        print(f"Destination: {dest_display} ({system_display})")
                                    else:
                                        print(f"Destination: {dest_display}")
                                elif target_system_id:
                                    system_name = _get_system_name(engine, target_system_id)
                                    system_obj = engine.sector.get_system(target_system_id)
                                    sys_visible = target_system_id in _visited_system_ids(engine)
                                    system_display = _format_name_with_profile(
                                        system_obj or SimpleNamespace(emoji_id=None, tier=None, tags=[]),
                                        system_name,
                                        sys_visible,
                                    )
                                    print(f"Target System: {system_display}")
                                
                                # Objectives from mission entity - NO RECALCULATION
                                objective_lines = _format_mission_objectives(engine, mission_dict)
                                if objective_lines:
                                    print(f"\nObjectives:")
                                    for obj_line in objective_lines:
                                        print(f"  • {obj_line}")
                                
                                # Rewards from reward_summary_lines (already calculated) - NO RECALCULATION
                                reward_lines = _format_mission_rewards(engine, mission_dict)
                                if reward_lines:
                                    print(f"\nRewards:")
                                    for reward_line in reward_lines:
                                        print(f"  • {reward_line}")
                                
                                print(f"\n{'='*60}\n")
                
                confirm = input("Accept this mission? (y/n): ").strip().lower()
                if confirm == "y":
                    # Call MissionCore.accept via engine command
                    accept_result = engine.execute({"type": "mission_accept", "mission_id": mission_id})
                    if accept_result.get("ok"):
                        accept_detail = _extract_detail_from_stage(step_result=accept_result, stage="mission")
                        if accept_detail and isinstance(accept_detail, dict):
                            if accept_detail.get("accepted"):
                                print(f"Mission accepted: {mission_id}")
                            else:
                                print(f"Mission accept result: {json.dumps(accept_detail, sort_keys=True)}")
                        else:
                            print(f"Mission accepted: {mission_id}")
                    else:
                        error = accept_result.get('error', 'unknown error')
                        if error == "mission_accept_failed_total_cap":
                            print("Cannot accept: total mission limit reached.")
                        elif error == "mission_accept_failed_tier_cap":
                            print("Cannot accept: tier limit reached.")
                        else:
                            print(f"Failed to accept mission: {error}")
                else:
                    print("Mission offer declined.")
            elif isinstance(interaction_result.get("missions"), list):
                missions = interaction_result.get("missions", [])
                print("Available Missions:")
                for mission in missions:
                    if isinstance(mission, dict):
                        print(f"  Mission ID: {mission.get('mission_id')}")
                        print(f"  Type: {mission.get('mission_type')}")
                        print(f"  Tier: {mission.get('mission_tier')}")
                        reward_text = _format_reward_summary(mission.get("reward_summary", []))
                        print(f"  Rewards: {reward_text}")
                        print()
            elif interaction_result.get("status") == "active" and isinstance(interaction_result.get("text"), str):
                # Active mission status message
                print(str(interaction_result.get("text")))
            elif isinstance(interaction_result.get("text"), str):
                # Generic text response (e.g., resolved mission placeholder)
                print(str(interaction_result.get("text")))
            elif interaction_result.get("paid") is not None:
                print(f"Fines paid: {interaction_result.get('paid')}")
            elif interaction_result.get("cleared_warrants") is not None:
                print(f"Warrants cleared: {interaction_result.get('cleared_warrants')}")
            elif interaction_result.get("accepted"):
                print(f"Mission accepted: {interaction_result.get('mission_id')}")
            else:
                print(json.dumps(interaction_result, sort_keys=True))
        else:
            _format_result(result, "location_action")


def _market_location_menu(engine: GameEngine) -> None:
    while True:
        _print_market_profile(engine)
        _print_market_sku_overlay(engine)
        print("LOCATION: market")
        print("1) Buy")
        print("2) Sell")
        print("3) Return to Destination")
        raw_action = input("Select action index: ").strip()
        if raw_action == "1":
            _market_buy_menu(engine)
            continue
        if raw_action == "2":
            _market_sell_menu(engine)
            continue
        if raw_action == "3":
            _return_to_destination(engine)
            print(f"Returned to destination: {engine.player_state.current_location_id}")
            return
        print("Invalid action index.")


def _datanet_location_menu(engine: GameEngine) -> None:
    while True:
        profile = _build_datanet_profile(engine)
        _print_datanet_profile(profile)
        print("LOCATION: datanet")
        print("1) Refresh")
        if profile.get("has_mission_accept_action"):
            print("2) Accept mission")
        else:
            print("2) Accept mission (unavailable)")
        print("3) Return to Destination")
        raw_action = input("Select action index: ").strip()
        if raw_action == "1":
            # Refresh: clear DataNet offers for this location only
            current_location_id = engine.player_state.current_location_id
            if isinstance(current_location_id, str) and current_location_id:
                engine._mission_manager.clear_datanet_offers(location_id=current_location_id)
            continue
        if raw_action == "2":
            if not profile.get("has_mission_accept_action"):
                print("No missions available.")
                continue
            _accept_mission_from_datanet(engine, profile)
            continue
        if raw_action == "3":
            _return_to_destination(engine)
            print(f"Returned to destination: {engine.player_state.current_location_id}")
            return
        print("Invalid action index.")


def _warehouse_location_menu(engine: GameEngine) -> None:
    while True:
        profile = _build_warehouse_profile(engine)
        _print_warehouse_profile(profile)
        location_entity = SimpleNamespace(emoji_id="location_warehouse", tier=None, tags=[])
        location_display = _format_name_with_profile(location_entity, "Warehouse", True)
        print(f"LOCATION: {location_display}")
        print("1) Rent space")
        print("2) Deposit cargo")
        print("3) Withdraw cargo")
        print("4) Return to Destination")
        raw_action = input("Select action index: ").strip()
        if raw_action == "1":
            raw_units = input("Units to rent: ").strip()
            try:
                units = int(raw_units)
            except ValueError:
                print("Invalid units.")
                continue
            payload = {
                "type": "location_action",
                "action_id": "warehouse_rent",
                "kwargs": {"units": units},
                "confirm": True,
            }
            result = engine.execute(payload)
            _format_result(result, "location_action")
            continue
        if raw_action == "2":
            player_profile = _extract_detail_from_stage(
                step_result=engine.execute({"type": "get_player_profile"}),
                stage="player_profile",
            )
            cargo_manifest = {}
            if isinstance(player_profile, dict):
                cargo_manifest = _compact_manifest(player_profile.get("cargo_manifest", {}))
            if not cargo_manifest:
                print("No cargo available to deposit.")
                continue
            cargo_skus = sorted(cargo_manifest.keys())
            for index, sku_id in enumerate(cargo_skus, start=1):
                display_name = _get_good_display_name(engine, sku_id)
                print(f"{index}) {display_name} units={cargo_manifest.get(sku_id)}")
            raw_index = input("Select cargo SKU index: ").strip()
            try:
                selected_index = int(raw_index)
            except ValueError:
                print("Invalid cargo SKU index.")
                continue
            if selected_index < 1 or selected_index > len(cargo_skus):
                print("Invalid cargo SKU index.")
                continue
            selected_sku_id = cargo_skus[selected_index - 1]
            raw_qty = input("Quantity: ").strip()
            try:
                quantity = int(raw_qty)
            except ValueError:
                print("Invalid quantity.")
                continue
            payload = {
                "type": "location_action",
                "action_id": "warehouse_deposit",
                "kwargs": {"sku_id": selected_sku_id, "quantity": quantity},
                "confirm": True,
            }
            result = engine.execute(payload)
            _format_result(result, "location_action")
            continue
        if raw_action == "3":
            raw_sku_id = input("SKU ID: ").strip()
            raw_qty = input("Quantity: ").strip()
            try:
                quantity = int(raw_qty)
            except ValueError:
                print("Invalid quantity.")
                continue
            payload = {
                "type": "location_action",
                "action_id": "warehouse_withdraw",
                "kwargs": {"sku_id": raw_sku_id, "quantity": quantity},
                "confirm": True,
            }
            result = engine.execute(payload)
            _format_result(result, "location_action")
            continue
        if raw_action == "4":
            _return_to_destination(engine)
            print(f"Returned to destination: {engine.player_state.current_location_id}")
            return
        print("Invalid action index.")


def main() -> None:
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="EmojiSpace CLI - Player-facing playtest tool")
    parser.add_argument("--seed", type=int, help="World seed (default: prompt)")
    parser.add_argument("--verbose", action="store_true", help="Show structured logs inline")
    args = parser.parse_args()
    
    # Get seed
    if args.seed is not None:
        seed = args.seed
    else:
        seed = _prompt_seed()
    
    starting_ship_override = _prompt_admin_override()
    
    # Create engine
    engine = GameEngine(world_seed=seed, config={"system_count": 50}, starting_ship_override=starting_ship_override)
    
    # Set up logging - create PlaytestLogger wrapper
    from logger import Logger
    base_logger = Logger(version="0.5.x")
    playtest_logger = PlaytestLogger(base_logger, verbose=args.verbose)
    
    # Configure file logging (preserves existing behavior)
    log_path = str((Path(__file__).resolve().parents[1] / "logs" / f"gameplay_seed_{seed}.log"))
    base_logger.configure_file_logging(enabled=True, log_path=log_path, truncate=True)
    _ = engine.execute({"type": "set_logging", "enabled": True, "log_path": log_path, "truncate": True})

    # Aevum-complete telemetry (JSON Lines) for engine debugging
    try:
        from playtest_telemetry import start_telemetry
        telemetry_path = str((Path(__file__).resolve().parents[1] / "logs" / f"gameplay_seed_{seed}_telemetry.jsonl"))
        start_telemetry(telemetry_path)
    except Exception:
        pass

    # Prepare output path for Markdown and debug telemetry (Stage 2)
    output_dir = Path(__file__).resolve().parents[1] / "tests" / "output"
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    markdown_path = output_dir / f"playtest_seed_{seed}_{timestamp}.md"
    debug_path = output_dir / f"playtest_seed_{seed}_{timestamp}.debug.jsonl"
    try:
        from playtest_telemetry import start_debug_telemetry
        start_debug_telemetry(str(debug_path))
    except Exception:
        pass

    _configure_cli_test_fuel(engine)
    
    # Set global context for helper functions
    global _playtest_context
    _playtest_context = {
        "playtest_logger": playtest_logger,
        "verbose": args.verbose,
    }
    
    # Clean player-facing output
    print("\n" + "=" * 60)
    print("EMOJISPACE")
    print("=" * 60)
    print(f"Seed: {seed}")
    print("=" * 60 + "\n")
    
    # Suppress logger console output (structured logs go to file/Markdown only)
    with _suppress_logger_console():
        # Display galaxy map at game start
        _render_galaxy_map(engine.sector, engine=engine)
        while True:
            # CRITICAL: Enforce hard-stop contract - check for pending encounters/combat BEFORE rendering menu
            # Per interaction_layer_contract.md and combat_resolution_contract.md, all encounters and combat
            # must be resolved before allowing menu navigation or travel.
            if engine.has_pending_encounter():
                _resolve_pending_encounter(engine)
                # After resolving encounter, continue loop (don't render menu yet in case combat was initiated)
                continue
            
            if engine.has_pending_combat():
                _resolve_pending_combat(engine)
                # After resolving combat, continue loop (don't render menu yet in case another encounter is pending)
                continue
            
            # Check for pending loot decision (after combat ends)
            pending_loot = engine.get_pending_loot()
            if pending_loot:
                _handle_pending_loot(engine, pending_loot)
                # After resolving loot, continue loop (don't render menu yet in case another encounter is pending)
                continue
            
            # Only render main menu if no pending encounters or combat
            # Display destination context block
            _print_destination_context(engine)
            print("1) Player / Ship Info")
            print("2) System Info")
            print("3) Travel")
            print("4) Destination Actions")
            print("5) Locations")
            print("6) Galaxy Summary")
            print("7) Quit")
            choice = input("Select: ").strip()
            if choice == "1":
                _show_player_info(engine)
            elif choice == "2":
                _show_system_info(engine)
            elif choice == "3":
                _travel_menu(engine)
            elif choice == "4":
                _destination_actions_menu(engine)
            elif choice == "5":
                _location_entry_menu(engine)
            elif choice == "6":
                _galaxy_summary(engine)
            elif choice == "7":
                result = engine.execute({"type": "quit"})
                _format_result(result, "quit")
                break
            else:
                print("Invalid menu choice.")
    
    # Stop telemetry (flush and close JSON Lines log)
    try:
        from playtest_telemetry import stop_telemetry
        stop_telemetry()
    except Exception:
        pass
    try:
        from playtest_telemetry import stop_debug_telemetry
        stop_debug_telemetry()
    except Exception:
        pass

    # Write Markdown playtest log at end of session
    try:
        playtest_logger.write_markdown(
            markdown_path,
            seed=seed,
            version=playtest_logger.version,
            log_file_path=Path(log_path),
        )
    except Exception as e:
        print(f"\nWarning: Failed to write playtest log: {e}")


def _reachable_systems(*, engine: GameEngine, current_system, fuel_limit: int) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for system in sorted(engine.sector.systems, key=lambda entry: entry.system_id):
        if system.system_id == current_system.system_id:
            continue
        dx = float(system.x) - float(current_system.x)
        dy = float(system.y) - float(current_system.y)
        distance = math.sqrt((dx * dx) + (dy * dy))
        if distance <= float(fuel_limit):
            rows.append(
                {
                    "system": system,
                    "system_id": system.system_id,
                    "name": system.name,
                    "distance_ly": float(distance),
                }
            )
    return rows


def _render_galaxy_map(sector, width: int = 80, height: int = 30, engine: Optional[GameEngine] = None) -> None:
    """Render ASCII grid map of galaxy systems."""
    if not sector.systems:
        print("No systems to display.")
        return
    
    # Sort systems by system_id to assign stable indices
    sorted_systems = sorted(sector.systems, key=lambda s: s.system_id)
    
    # Find coordinate bounds
    min_x = min(s.x for s in sorted_systems)
    max_x = max(s.x for s in sorted_systems)
    min_y = min(s.y for s in sorted_systems)
    max_y = max(s.y for s in sorted_systems)
    
    # Add small padding to avoid edge issues
    x_range = max_x - min_x
    y_range = max_y - min_y
    if x_range < 1e-6:
        x_range = 1.0
        min_x -= 0.5
        max_x += 0.5
    if y_range < 1e-6:
        y_range = 1.0
        min_y -= 0.5
        max_y += 0.5
    
    # Create grid
    grid: List[List[str | None]] = [[None for _ in range(width)] for _ in range(height)]
    collisions: List[tuple[int, int, List[tuple[int, str, str]]]] = []  # (row, col, [(index, system_id, name)])
    
    # Map systems to grid cells
    for index, system in enumerate(sorted_systems, start=1):
        # Normalize coordinates to [0, 1]
        norm_x = (system.x - min_x) / x_range
        norm_y = (system.y - min_y) / y_range
        
        # Map to grid coordinates (flip y for display: top is max_y)
        col = int(norm_x * (width - 1))
        row = int((1.0 - norm_y) * (height - 1))
        
        # Clamp to grid bounds
        col = max(0, min(width - 1, col))
        row = max(0, min(height - 1, row))
        
        # Format label (2-3 digits)
        if index <= 99:
            label = f"{index:02d}"
        else:
            label = f"{index:03d}"
        
        # Handle collisions
        if grid[row][col] is not None:
            # Find or create collision entry
            collision_entry = None
            for i, (r, c, systems_list) in enumerate(collisions):
                if r == row and c == col:
                    collision_entry = i
                    break
            if collision_entry is None:
                # First collision at this cell - mark existing system
                existing_label = grid[row][col]
                existing_index = int(existing_label) if existing_label and existing_label.isdigit() else 0
                if existing_index > 0:
                    existing_sys = sorted_systems[existing_index - 1]
                    collisions.append((row, col, [(existing_index, existing_sys.system_id, existing_sys.name)]))
                    collision_entry = len(collisions) - 1
                else:
                    collisions.append((row, col, []))
                    collision_entry = len(collisions) - 1
            collisions[collision_entry][2].append((index, system.system_id, system.name))
            grid[row][col] = "*"
        else:
            grid[row][col] = label
    
    # Print grid
    print("\nGALAXY MAP")
    print("=" * width)
    for row in grid:
        line = ""
        for cell in row:
            if cell is None:
                line += " "
            else:
                line += str(cell)
        print(line)
    print("=" * width)
    
    # Print legend
    print("\nLEGEND:")
    for index, system in enumerate(sorted_systems, start=1):
        label = f"{index:02d}" if index <= 99 else f"{index:03d}"
        visible = engine is not None and system.system_id in _visited_system_ids(engine)
        display_name = _format_name_with_profile(system, system.name, visible)
        print(f"  {label} {system.system_id} {display_name} (x={system.x:.3f}, y={system.y:.3f})")
    
    # Print collisions if any
    if collisions:
        print("\nCOLLISIONS (multiple systems in same cell):")
        for row, col, systems_list in collisions:
            print(f"  Cell ({row}, {col}):")
            for idx, sys_id, sys_name in systems_list:
                label = f"{idx:02d}" if idx <= 99 else f"{idx:03d}"
                system = next((s for s in sector.systems if s.system_id == sys_id), None)
                visible = engine is not None and sys_id in _visited_system_ids(engine)
                display_name = _format_name_with_profile(
                    system or SimpleNamespace(emoji_id=None, tier=None, tags=[]),
                    sys_name,
                    visible,
                )
                print(f"    {label} {sys_id} {display_name}")
    print()


def _emoji_glyph_for_id(emoji_id: str) -> str:
    """Resolve emoji_id to glyph via data/emoji.json. Returns empty string if not found."""
    if not emoji_id:
        return ""
    try:
        path = _src_dir.parent / "data" / "emoji.json"
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return ""
    if not isinstance(data, list):
        return ""
    for entry in data:
        if isinstance(entry, dict) and entry.get("emoji_id") == emoji_id:
            glyph = entry.get("glyph", "")
            return str(glyph) if glyph else ""
    return ""


def _print_current_system_destinations(engine: GameEngine) -> None:
    system = engine.sector.get_system(engine.player_state.current_system_id)
    if system is None:
        return
    destinations = sorted(system.destinations, key=lambda destination: destination.destination_id)
    print("Intra-system destinations:")
    for index, destination in enumerate(destinations, start=1):
        visible = destination.destination_id in _visited_destination_ids(engine)
        display_name = _format_name_with_profile(
            destination,
            destination.display_name,
            visible,
        )
        print(f"  {index}) {destination.destination_id} {display_name} ({destination.destination_type})")


def _configure_cli_test_fuel(engine: GameEngine) -> None:
    active_ship = engine.fleet_by_id.get(engine.player_state.active_ship_id)
    if active_ship is None:
        return
    # Set fuel to capacity for testing (no hardcoded value)
    if active_ship.fuel_capacity > 0:
        active_ship.current_fuel = active_ship.fuel_capacity


def _current_destination_object(engine: GameEngine) -> object | None:
    current_system = engine.sector.get_system(engine.player_state.current_system_id)
    if current_system is None:
        return None
    destination_id = engine.player_state.current_destination_id
    for destination in list(getattr(current_system, "destinations", []) or []):
        if getattr(destination, "destination_id", None) == destination_id:
            return destination
    return None


def _enter_location_by_index(engine: GameEngine, selection_text: str) -> dict[str, object]:
    try:
        selected = int(selection_text)
    except ValueError:
        return {"ok": False, "error": "invalid_location_index"}
    return engine.execute({"type": "enter_location", "location_index": selected})


def _return_to_destination(engine: GameEngine) -> None:
    _ = engine.execute({"type": "return_to_destination"})


def _print_destination_context(engine: GameEngine) -> None:
    """Print standardized destination context block."""
    ctx = engine.get_current_destination_context()
    
    system_visited = ctx.get('system_government', '') != '' or ctx.get('primary_economy') is not None
    
    print("-" * 40)
    dest_id = ctx.get("destination_id")
    system_id = ctx.get("system_id")
    dest_obj = _get_destination_object(engine, dest_id) if dest_id else None
    system_obj = engine.sector.get_system(system_id) if system_id else None
    dest_visible = dest_id in _visited_destination_ids(engine) if dest_id else False
    sys_visible = system_id in _visited_system_ids(engine) if system_id else False
    dest_display = _format_name_with_profile(
        dest_obj or SimpleNamespace(emoji_id=None, tier=None, tags=[]),
        ctx.get('destination_name', 'Unknown'),
        dest_visible,
    )
    system_display = _format_name_with_profile(
        system_obj or SimpleNamespace(emoji_id=None, tier=None, tags=[]),
        ctx.get('system_name', 'Unknown'),
        sys_visible,
    )
    print(f"Destination: {dest_display} ({ctx.get('destination_type', 'unknown')})")
    print(f"System: {system_display}", end="")
    
    system_government = ctx.get('system_government', '')
    if system_government:
        print(f" ({system_government})")
    else:
        print()
    
    # Only show sensitive data if system is visited
    if system_visited:
        population = ctx.get('population', 0)
        if population > 0:
            print(f"Population: {population}")
        
        primary_economy = ctx.get('primary_economy')
        secondary_economies = ctx.get('secondary_economies', [])
        
        if primary_economy:
            economy_str = primary_economy
            if secondary_economies:
                economy_str += f" ({', '.join(secondary_economies)})"
            print(f"Economy: {economy_str}")
        
        # Separate system and destination situations
        system_id = ctx.get('system_id', '')
        destination_id = engine.player_state.current_destination_id
        
        # Get situation rows and separate by scope
        situation_rows = engine._active_situation_rows_for_system(system_id=system_id) if system_id else []
        system_situations = []
        destination_situations = []
        
        for row in situation_rows:
            situation_id = row.get('situation_id')
            scope = row.get('scope')
            target_id = row.get('target_id')
            
            if isinstance(situation_id, str) and situation_id:
                if scope == 'system':
                    system_situations.append(situation_id)
                elif scope == 'destination' and target_id == destination_id:
                    destination_situations.append(situation_id)
        
        system_situations = sorted(set(system_situations))
        destination_situations = sorted(set(destination_situations))
        
        if system_situations:
            print(f"System situations: {', '.join(system_situations)}")
        else:
            print("System situations: None")
        
        if destination_situations:
            print(f"Destination situations: {', '.join(destination_situations)}")
        else:
            print("Destination situations: None")
    
    print("-" * 40)


def _galaxy_summary(engine: GameEngine) -> None:
    """Print galaxy summary for debug visibility."""
    sector = engine.sector
    systems = sorted(sector.systems, key=lambda s: s.system_id)
    
    print("\n" + "=" * 60)
    print("GALAXY SUMMARY")
    print("=" * 60)
    print(f"Total systems: {len(systems)}\n")
    
    for system in systems:
        government = engine.government_registry.get_government(system.government_id)
        government_name = government.name if government else system.government_id
        visible = system.system_id in _visited_system_ids(engine)
        display_name = _format_name_with_profile(system, system.name, visible)
        print(f"System: {system.system_id} - {display_name}")
        print(f"  Government: {government_name}")
        print(f"  Population: {system.population}")
        print(f"  Destinations:")
        
        destinations = sorted(system.destinations, key=lambda d: d.destination_id)
        for dest in destinations:
            secondary_str = ", ".join(dest.secondary_economy_ids) if dest.secondary_economy_ids else "-"
            primary_str = dest.primary_economy_id if dest.primary_economy_id else "None"
            visible = dest.destination_id in _visited_destination_ids(engine)
            dest_display = _format_name_with_profile(dest, dest.display_name, visible)
            print(f"    {dest.destination_id} - {dest_display} ({dest.destination_type})")
            print(f"      Population: {dest.population}")
            print(f"      Primary Economy: {primary_str}")
            print(f"      Secondary Economies: {secondary_str}")
        print()
    
    print("=" * 60 + "\n")


def _print_exploration_result(engine: GameEngine, result: Dict[str, Any]) -> None:
    """After Explore action: print SUCCESS/FAIL and exploration progress at this site."""
    if not result.get("ok"):
        return
    events = result.get("events", [])
    success = None
    stage_after = None
    for ev in events:
        if isinstance(ev, dict) and ev.get("stage") == "exploration":
            detail = ev.get("detail", {})
            if isinstance(detail, dict):
                success = detail.get("success")
                stage_after = detail.get("stage_after")
                break
    if success is True:
        print("Exploration result: SUCCESS")
    elif success is False:
        print("Exploration result: FAIL")
    dest_id = result.get("player", {}).get("destination_id") or ""
    progress = int(stage_after) if stage_after is not None else int(getattr(engine.player_state, "exploration_progress", {}).get(dest_id, 0))
    print(f"Exploration progress at this site: {progress}")


def _destination_actions_menu(engine: GameEngine) -> None:
    # Display destination context before menu
    _print_destination_context(engine)
    
    while True:
        list_result = engine.execute({"type": "list_destination_actions"})
        actions = _extract_actions_from_stage(step_result=list_result, stage="destination_actions")
        if not actions:
            print("No destination actions available.")
            return
        print("0) Back")
        for index, action in enumerate(actions, start=1):
            display = _format_name_with_profile(action, str(action.get("display_name", "") or action.get("action_id", "")), True)
            print(f"{index}) {action['action_id']} {display}")

        raw_index = input("Select destination action index: ").strip()
        try:
            selected = int(raw_index)
        except ValueError:
            print("Invalid destination action index.")
            continue
        if selected == 0:
            return
        if selected < 1 or selected > len(actions):
            print("Invalid destination action index.")
            continue
        action = actions[selected - 1]
        kwargs = _prompt_action_kwargs(action)
        result = engine.execute(
            {
                "type": "destination_action",
                "action_id": action["action_id"],
                "action_kwargs": kwargs,
            }
        )
        _format_result(result, "location_action")
        if action["action_id"] == "explore":
            _print_exploration_result(engine, result)
        if action["action_id"] in ("explore", "mine") and result.get("ok"):
            print("Local activity may attract attention...")
            if result.get("hard_stop") and result.get("hard_stop_reason") == "pending_encounter_decision":
                _resolve_pending_encounter(engine)
            else:
                print("No ships respond to your activity.")


def _print_market_profile(engine: GameEngine) -> None:
    result = engine.execute({"type": "get_market_profile"})
    if result.get("ok") is False:
        _format_result(result, "location_action")
        return
    events = result.get("events", [])
    detail = {}
    for event in events:
        if isinstance(event, dict) and event.get("stage") == "market_profile":
            detail = event.get("detail", {})
            break
    if not isinstance(detail, dict):
        print("Market profile unavailable.")
        return
    print("MARKET PROFILE")
    print(f"  System: {detail.get('system_id')}")
    print(f"  Destination: {detail.get('destination_id')}")
    print(f"  Primary economy: {detail.get('primary_economy_id')}")
    situations = detail.get("active_situations", [])
    print(f"  Active situations: {situations if situations else 'none'}")
    categories = detail.get("categories", {})
    if not isinstance(categories, dict):
        return
    for category_id in sorted(categories):
        row = categories[category_id]
        print(
            f"  {category_id}: produced={row.get('produced', [])} "
            f"consumed={row.get('consumed', [])} neutral={row.get('neutral', [])}"
        )


def _market_buy_menu(engine: GameEngine) -> None:
    result = engine.execute({"type": "market_buy_list"})
    rows = _extract_rows_from_stage(step_result=result, stage="market_buy_list")
    if not rows:
        print("No market buy offers.")
        return
    for index, row in enumerate(rows, start=1):
        sku_id = row.get("sku_id", "")
        display_name = _get_good_display_name(engine, sku_id) if sku_id else row.get("display_name", "Unknown")
        print(
            f"{index}) {display_name} "
            f"price={row.get('unit_price')} legality={row.get('legality')} risk={row.get('risk_tier')}"
        )
    raw_index = input("Select buy sku index: ").strip()
    raw_qty = input("Quantity: ").strip()
    try:
        selected = int(raw_index)
        quantity = int(raw_qty)
    except ValueError:
        print("Invalid buy input.")
        return
    if selected < 1 or selected > len(rows):
        print("Invalid buy index.")
        return
    sku_id = rows[selected - 1]["sku_id"]
    result = engine.execute({"type": "market_buy", "sku_id": sku_id, "quantity": quantity})
    _format_result(result, "market_buy")


def _market_sell_menu(engine: GameEngine) -> None:
    result = engine.execute({"type": "market_sell_list"})
    rows = _extract_rows_from_stage(step_result=result, stage="market_sell_list")
    if not rows:
        print("No market sell offers.")
        return
    for index, row in enumerate(rows, start=1):
        sku_id = row.get("sku_id", "")
        display_name = _get_good_display_name(engine, sku_id) if sku_id else row.get("display_name", "Unknown")
        print(
            f"{index}) {display_name} units={row.get('player_has_units')} "
            f"price={row.get('unit_price')} legality={row.get('legality')} risk={row.get('risk_tier')}"
        )
    raw_index = input("Select sell sku index: ").strip()
    raw_qty = input("Quantity: ").strip()
    try:
        selected = int(raw_index)
        quantity = int(raw_qty)
    except ValueError:
        print("Invalid sell input.")
        return
    if selected < 1 or selected > len(rows):
        print("Invalid sell index.")
        return
    sku_id = rows[selected - 1]["sku_id"]
    result = engine.execute({"type": "market_sell", "sku_id": sku_id, "quantity": quantity})
    _format_result(result, "market_sell")


def _shipdock_menu(engine: GameEngine) -> None:
    """Shipdock location menu with numbered lists for all actions."""
    while True:
        print(f"SHIPDOCK: {engine.player_state.current_location_id}")
        print("1) Buy Hull")
        print("2) Buy Module")
        print("3) Sell Hull")
        print("4) Sell Module")
        print("5) Repair Ship")
        print("6) Return to Destination")
        
        raw_choice = input("Select action: ").strip()
        if raw_choice == "6":
            _return_to_destination(engine)
            print(f"Returned to destination: {engine.player_state.current_location_id}")
            return
        elif raw_choice == "1":
            _shipdock_buy_hull(engine)
        elif raw_choice == "2":
            _shipdock_buy_module(engine)
        elif raw_choice == "3":
            _shipdock_sell_hull(engine)
        elif raw_choice == "4":
            _shipdock_sell_module(engine)
        elif raw_choice == "5":
            _shipdock_repair_ship(engine)
        else:
            print("Invalid selection.")


def _shipdock_buy_hull(engine: GameEngine) -> None:
    """Buy hull from shipdock - shows numbered list."""
    result = engine.execute({"type": "shipdock_hull_list"})
    rows = _extract_rows_from_stage(step_result=result, stage="shipdock_hull_list")
    if not rows:
        print("No hulls available at this shipdock.")
        return
    
    print("AVAILABLE HULLS:")
    for index, row in enumerate(rows, start=1):
        display_name = row.get("display_name", row.get("hull_id", "Unknown"))
        display = _format_name_with_profile(row, str(display_name), True)
        print(f"{index}) {display} (Tier {row.get('tier', 0)}) - {row.get('price', 0)} credits")
    
    raw_index = input("Select hull index (0 to cancel): ").strip()
    if raw_index == "0":
        return
    try:
        selected = int(raw_index)
    except ValueError:
        print("Invalid index.")
        return
    if selected < 1 or selected > len(rows):
        print("Invalid index.")
        return
    
    hull_id = rows[selected - 1]["hull_id"]
    # Auto-select active ship
    ship_id = engine.player_state.active_ship_id
    if not ship_id:
        print("No active ship available.")
        return
    
    # Handle confirmation
    confirmed = True
    row_sel = rows[selected - 1]
    confirm_display = _format_name_with_profile(row_sel, str(row_sel.get("display_name", hull_id)), True)
    print(f"Purchase {confirm_display} for {row_sel.get('price', 0)} credits?")
    confirmed = input("Confirm? (y/n): ").strip().lower() == "y"
    if not confirmed:
        print("Purchase cancelled.")
        return
    
    payload = {
        "type": "location_action",
        "action_id": "buy_hull",
        "kwargs": {"hull_id": hull_id, "ship_id": ship_id},
        "confirm": confirmed,
    }
    result = engine.execute(payload)
    _format_result(result, "location_action")


def _shipdock_buy_module(engine: GameEngine) -> None:
    """Buy module from shipdock - shows numbered list."""
    result = engine.execute({"type": "shipdock_module_list"})
    rows = _extract_rows_from_stage(step_result=result, stage="shipdock_module_list")
    if not rows:
        print("No modules available at this shipdock.")
        return
    
    print("AVAILABLE MODULES:")
    for index, row in enumerate(rows, start=1):
        display_name = row.get("display_name", row.get("module_id", "Unknown"))
        display = _format_name_with_profile(row, str(display_name), True)
        print(f"{index}) {display} ({row.get('slot_type', 'unknown')}) - {row.get('price', 0)} credits")
    
    raw_index = input("Select module index (0 to cancel): ").strip()
    if raw_index == "0":
        return
    try:
        selected = int(raw_index)
    except ValueError:
        print("Invalid index.")
        return
    if selected < 1 or selected > len(rows):
        print("Invalid index.")
        return
    
    module_id = rows[selected - 1]["module_id"]
    # Auto-select active ship
    ship_id = engine.player_state.active_ship_id
    if not ship_id:
        print("No active ship available.")
        return
    
    payload = {
        "type": "location_action",
        "action_id": "buy_module",
        "kwargs": {"module_id": module_id, "ship_id": ship_id},
        "confirm": True,
    }
    result = engine.execute(payload)
    _format_result(result, "location_action")


def _shipdock_sell_hull(engine: GameEngine) -> None:
    """Sell hull at shipdock - shows numbered list of owned ships."""
    result = engine.execute({"type": "shipdock_ship_list"})
    rows = _extract_rows_from_stage(step_result=result, stage="shipdock_ship_list")
    if not rows:
        print("No ships available to sell at this destination.")
        return
    
    print("OWNED SHIPS (eligible to sell):")
    for index, row in enumerate(rows, start=1):
        display_name = row.get("display_name", row.get("ship_id", "Unknown"))
        display = _format_name_with_profile(row, str(display_name), True)
        print(f"{index}) {display} (Tier {row.get('tier', 0)}) - {row.get('price', 0)} credits")
    
    raw_index = input("Select ship index to sell (0 to cancel): ").strip()
    if raw_index == "0":
        return
    try:
        selected = int(raw_index)
    except ValueError:
        print("Invalid index.")
        return
    if selected < 1 or selected > len(rows):
        print("Invalid index.")
        return
    
    ship_id = rows[selected - 1]["ship_id"]
    row_sel = rows[selected - 1]
    sell_display = _format_name_with_profile(row_sel, str(row_sel.get("display_name", ship_id)), True)
    # Handle confirmation
    print(f"Sell {sell_display} for {row_sel.get('price', 0)} credits?")
    confirmed = input("Confirm? (y/n): ").strip().lower() == "y"
    if not confirmed:
        print("Sale cancelled.")
        return
    
    payload = {
        "type": "location_action",
        "action_id": "sell_hull",
        "kwargs": {"ship_id": ship_id},
        "confirm": confirmed,
    }
    result = engine.execute(payload)
    _format_result(result, "location_action")


def _shipdock_sell_module(engine: GameEngine) -> None:
    """Sell module at shipdock - shows numbered list of installed modules."""
    # Default to active ship
    ship_id = engine.player_state.active_ship_id
    if not ship_id:
        print("No active ship available.")
        return
    
    result = engine.execute({"type": "shipdock_installed_modules_list", "ship_id": ship_id})
    rows = _extract_rows_from_stage(step_result=result, stage="shipdock_installed_modules_list")
    if not rows:
        print("No modules installed on active ship.")
        return
    
    print("INSTALLED MODULES:")
    for index, row in enumerate(rows, start=1):
        display_name = row.get("display_name", row.get("module_id", "Unknown"))
        display = _format_name_with_profile(row, str(display_name), True)
        print(f"{index}) {display} ({row.get('slot_type', 'unknown')}) - {row.get('price', 0)} credits")
    
    raw_index = input("Select module index to sell (0 to cancel): ").strip()
    if raw_index == "0":
        return
    try:
        selected = int(raw_index)
    except ValueError:
        print("Invalid index.")
        return
    if selected < 1 or selected > len(rows):
        print("Invalid index.")
        return
    
    module_id = rows[selected - 1]["module_id"]
    
    payload = {
        "type": "location_action",
        "action_id": "sell_module",
        "kwargs": {"module_id": module_id, "ship_id": ship_id},
        "confirm": True,
    }
    result = engine.execute(payload)
    _format_result(result, "location_action")


def _shipdock_repair_ship(engine: GameEngine) -> None:
    """Repair ship - single step action."""
    # Default to active ship
    ship_id = engine.player_state.active_ship_id
    if not ship_id:
        print("No active ship available.")
        return
    
    payload = {
        "type": "location_action",
        "action_id": "repair_ship",
        "kwargs": {"ship_id": ship_id},
        "confirm": True,
    }
    result = engine.execute(payload)
    _format_result(result, "location_action")


def _print_market_sku_overlay(engine: GameEngine) -> None:
    buy_rows = _extract_rows_from_stage(step_result=engine.execute({"type": "market_buy_list"}), stage="market_buy_list")
    sell_rows = _extract_rows_from_stage(step_result=engine.execute({"type": "market_sell_list"}), stage="market_sell_list")
    player_profile = _extract_detail_from_stage(
        step_result=engine.execute({"type": "get_player_profile"}),
        stage="player_profile",
    )
    cargo_manifest = _compact_manifest((player_profile or {}).get("cargo_manifest", {}))
    sell_price_by_sku: dict[str, object] = {}
    sell_display_by_sku: dict[str, object] = {}
    sell_legality_by_sku: dict[str, object] = {}
    sell_risk_by_sku: dict[str, object] = {}
    for row in sell_rows:
        sku_id = str(row.get("sku_id", "") or "")
        if not sku_id:
            continue
        sell_price_by_sku[sku_id] = row.get("unit_price")
        sell_display_by_sku[sku_id] = row.get("display_name")
        sell_legality_by_sku[sku_id] = row.get("legality")
        sell_risk_by_sku[sku_id] = row.get("risk_tier")

    buy_by_sku: dict[str, dict[str, object]] = {}
    for row in buy_rows:
        sku_id = str(row.get("sku_id", "") or "")
        if sku_id:
            buy_by_sku[sku_id] = row

    all_skus = sorted(set(buy_by_sku.keys()) | set(cargo_manifest.keys()) | set(sell_price_by_sku.keys()))
    if not all_skus:
        print("No market SKUs available.")
        return

    print("MARKET SKUS")
    for sku_id in all_skus:
        buy_row = buy_by_sku.get(sku_id, {})
        display_name = _get_good_display_name(engine, sku_id)
        buy_price = buy_row.get("unit_price", "--")
        cargo_units = int(cargo_manifest.get(sku_id, 0) or 0)
        if cargo_units > 0:
            sell_price = sell_price_by_sku.get(sku_id, "--")
        else:
            sell_price = "--"
        legality = buy_row.get("legality", sell_legality_by_sku.get(sku_id, "--"))
        risk = buy_row.get("risk_tier", sell_risk_by_sku.get(sku_id, "--"))
        print(
            f"  {sku_id} | {display_name} | buy={buy_price} | sell={sell_price} "
            f"| cargo={cargo_units} | legality={legality} | risk={risk}"
        )


def _build_datanet_profile(engine: GameEngine) -> dict[str, object]:
    # Build base profile from system/destination for context only
    system_detail = _extract_detail_from_stage(
        step_result=engine.execute({"type": "get_system_profile"}),
        stage="system_profile",
    )
    destination_detail = _extract_detail_from_stage(
        step_result=engine.execute({"type": "get_destination_profile"}),
        stage="destination_profile",
    )
    # DataNet missions must be isolated from bar/admin missions.
    # Use a dedicated DataNet mission pool maintained by the engine/mission_manager.
    current_location_id = engine.player_state.current_location_id
    datanet_missions = []
    if isinstance(current_location_id, str) and current_location_id:
        datanet_missions = engine._datanet_mission_rows_for_location(location_id=current_location_id)
    system_situations = []
    system_notices = []
    destination_situations = []
    if isinstance(system_detail, dict):
        system_situations = list(system_detail.get("active_system_situations", []))
        system_notices = list(system_detail.get("active_system_flags", []))
    if isinstance(destination_detail, dict):
        destination_situations = list(destination_detail.get("active_destination_situations", []))
    return {
        "system_situations": system_situations,
        "destination_situations": destination_situations,
        "available_missions": datanet_missions,
        "system_notices": system_notices,
        "mission_actions": [],  # DataNet uses its own accept flow
        "has_mission_accept_action": bool(datanet_missions),
    }


def _print_datanet_profile(profile: dict[str, object]) -> None:
    print("DATANET PROFILE")
    print(f"  System situations: {profile.get('system_situations')}")
    print(f"  Destination situations: {profile.get('destination_situations')}")
    missions = profile.get("available_missions", [])
    if missions:
        print(f"  Available missions: {missions}")
    else:
        print("  Available missions: []")
        print("No missions available.")
    notices = profile.get("system_notices", [])
    if notices:
        print(f"  System notices: {notices}")
    else:
        print("  System notices: none")


def _accept_mission_from_datanet(engine: GameEngine, profile: dict[str, object]) -> None:
    actions = [row for row in profile.get("mission_actions", []) if isinstance(row, dict)]
    if not actions:
        print("No missions available.")
        return
    action = actions[0]
    kwargs = _prompt_action_kwargs(action)
    result = engine.execute(
        {
            "type": "destination_action",
            "action_id": action.get("action_id"),
            "action_kwargs": kwargs,
        }
    )
    _format_result(result, "location_action")


def _build_warehouse_profile(engine: GameEngine) -> dict[str, object]:
    destination_id = str(engine.player_state.current_destination_id or "")
    warehouse = getattr(engine.player_state, "warehouses", {}).get(destination_id, {})
    player_profile = _extract_detail_from_stage(
        step_result=engine.execute({"type": "get_player_profile"}),
        stage="player_profile",
    )
    profile_row: dict[str, object] = {}
    if isinstance(player_profile, dict):
        for row in player_profile.get("warehouses", []):
            if isinstance(row, dict) and row.get("destination_id") == destination_id:
                profile_row = row
                break
    stored_goods: dict[str, int] = {}
    if isinstance(warehouse, dict):
        goods_raw = warehouse.get("goods", {})
        if isinstance(goods_raw, dict):
            stored_goods = {
                str(sku_id): int(quantity)
                for sku_id, quantity in goods_raw.items()
                if isinstance(quantity, int) and int(quantity) > 0
            }
    rented_capacity = int((warehouse or {}).get("capacity", 0) or 0)
    used_storage = int(sum(int(value) for value in stored_goods.values()))
    available_storage = max(0, int(rented_capacity - used_storage))
    rental_cost = int(profile_row.get("cost_per_turn", 0) or 0)
    return {
        "rented_capacity": rented_capacity,
        "used_storage": used_storage,
        "available_storage": available_storage,
        "rental_cost_per_turn": rental_cost,
        "stored_goods": stored_goods,
    }


def _print_warehouse_profile(profile: dict[str, object]) -> None:
    print("WAREHOUSE PROFILE")
    print(f"  Rented capacity: {profile.get('rented_capacity')}")
    print(f"  Used storage: {profile.get('used_storage')}")
    print(f"  Available storage: {profile.get('available_storage')}")
    print(f"  Rental cost per turn: {profile.get('rental_cost_per_turn')}")
    stored_goods = profile.get("stored_goods", {})
    print("  Stored goods list:")
    if isinstance(stored_goods, dict) and stored_goods:
        for sku_id in sorted(stored_goods):
            print(f"    {sku_id}: {stored_goods[sku_id]}")
    else:
        print("    none")


def _visited_system_ids(engine: GameEngine) -> set[str]:
    raw = getattr(engine.player_state, "visited_system_ids", set())
    if isinstance(raw, set):
        return {entry for entry in raw if isinstance(entry, str)}
    if isinstance(raw, list):
        return {entry for entry in raw if isinstance(entry, str)}
    return set()


def _visited_destination_ids(engine: GameEngine) -> set[str]:
    raw = getattr(engine.player_state, "visited_destination_ids", set())
    if isinstance(raw, set):
        return {entry for entry in raw if isinstance(entry, str)}
    if isinstance(raw, list):
        return {entry for entry in raw if isinstance(entry, str)}
    return set()


def _active_system_situations(*, engine: GameEngine, system_id: str) -> list[str]:
    helper = getattr(engine, "_active_situation_rows_for_system", None)
    if not callable(helper):
        return []
    rows = helper(system_id=system_id)
    if not isinstance(rows, list):
        return []
    return sorted(
        [
            str(row.get("situation_id"))
            for row in rows
            if isinstance(row, dict) and isinstance(row.get("situation_id"), str)
        ]
    )


def _compact_manifest(manifest: object) -> dict[str, int]:
    if not isinstance(manifest, dict):
        return {}
    compact: dict[str, int] = {}
    for sku_id, quantity in manifest.items():
        if not isinstance(quantity, int):
            continue
        if int(quantity) <= 0:
            continue
        compact[str(sku_id)] = int(quantity)
    return compact


def _sum_numeric_fields(*, rows: object, candidate_keys: tuple[str, ...]) -> int:
    if not isinstance(rows, list):
        return 0
    total = 0
    for row in rows:
        if not isinstance(row, dict):
            continue
        value = None
        for key in candidate_keys:
            if key in row:
                value = row.get(key)
                break
        if isinstance(value, int):
            total += int(value)
        elif isinstance(value, float):
            total += int(value)
    return int(total)


def _extract_actions_from_step_result(step_result: dict[str, object]) -> list[dict[str, object]]:
    return _extract_actions_from_stage(step_result=step_result, stage="location_actions")


def _extract_actions_from_stage(*, step_result: dict[str, object], stage: str) -> list[dict[str, object]]:
    events = step_result.get("events", [])
    if not isinstance(events, list):
        return []
    for event in events:
        if not isinstance(event, dict):
            continue
        if event.get("stage") != stage:
            continue
        detail = event.get("detail", {})
        if not isinstance(detail, dict):
            continue
        actions = detail.get("actions", [])
        if isinstance(actions, list):
            return [entry for entry in actions if isinstance(entry, dict)]
    return []


def _extract_rows_from_stage(*, step_result: dict[str, object], stage: str) -> list[dict[str, object]]:
    events = step_result.get("events", [])
    if not isinstance(events, list):
        return []
    for event in events:
        if not isinstance(event, dict):
            continue
        if event.get("stage") != stage:
            continue
        detail = event.get("detail", {})
        if not isinstance(detail, dict):
            continue
        rows = detail.get("rows", [])
        if isinstance(rows, list):
            return [row for row in rows if isinstance(row, dict)]
    return []


def _extract_detail_from_stage(*, step_result: dict[str, object], stage: str) -> dict[str, object] | None:
    events = step_result.get("events", [])
    if not isinstance(events, list):
        return None
    for event in events:
        if not isinstance(event, dict):
            continue
        if event.get("stage") != stage:
            continue
        detail = event.get("detail", {})
        if isinstance(detail, dict):
            return detail
    return None


def _prompt_action_kwargs(action: dict[str, object]) -> dict[str, object]:
    params = action.get("parameters", [])
    if not isinstance(params, list) or not params:
        return {}
    kwargs: dict[str, object] = {}
    for param in params:
        # Handle dict parameters (new format: {"name": "...", "type": "...", "prompt": "..."})
        if isinstance(param, dict):
            param_name = param.get("name", "")
            param_prompt = param.get("prompt", param_name)
            param_type = param.get("type", "str")
            if not param_name:
                continue
            raw = input(f"{param_prompt}: ").strip()
            if param_type == "int":
                try:
                    kwargs[param_name] = int(raw)
                except ValueError:
                    kwargs[param_name] = raw
            elif param_type == "bool":
                kwargs[param_name] = raw.lower() in {"1", "true", "yes", "y"}
            else:
                kwargs[param_name] = raw
        # Handle string parameters (legacy format for backward compatibility)
        elif isinstance(param, str):
            raw = input(f"{param}: ").strip()
            if param in {"quantity", "requested_units", "location_index"}:
                try:
                    kwargs[param] = int(raw)
                except ValueError:
                    kwargs[param] = raw
            elif param == "allow_repeat":
                kwargs[param] = raw.lower() in {"1", "true", "yes", "y"}
            else:
                kwargs[param] = raw
    return kwargs


def _combat_action_menu(
    round_number: int,
    player_hull_pct: int,
    enemy_hull_pct: int,
    allowed_actions: list[str],
    encounter_description: str | None = None,
    enemy_ship_info: dict[str, Any] | None = None,
) -> str:
    """
    Prompt player for combat action selection.
    
    Per combat_resolution_contract.md Section 3: "CORE ACTIONS"
    Always available: Focus Fire, Reinforce Shields, Evasive Maneuvers, Attempt Escape, Surrender
    
    Args:
        round_number: Current combat round (1-indexed, no round 0)
        player_hull_pct: Player hull percentage (0-100)
        enemy_hull_pct: Enemy hull percentage (0-100)
        allowed_actions: List of allowed combat action labels (from engine's pending_combat.allowed_actions)
        encounter_description: Optional encounter description (e.g., "Pirate Raider", "Border Patrol")
        enemy_ship_info: Optional enemy ship information dict
        
    Returns:
        Selected action label (must be in allowed_actions)
    """
    # Enforce round numbering: no round 0
    if round_number < 1:
        round_number = 1
    
    # Display encounter description and enemy ship info
    print(f"\n--- COMBAT - Round {round_number} ---")
    
    if encounter_description:
        print(f"Encounter: {encounter_description}")
    
    if enemy_ship_info:
        hull_name = enemy_ship_info.get("hull_name", "Unknown")
        hull_id = enemy_ship_info.get("hull_id", "unknown")
        display_name = _format_name_with_profile(enemy_ship_info, hull_name, True)
        module_count = enemy_ship_info.get("module_count", 0)
        weapon_modules = enemy_ship_info.get("weapon_modules", 0)
        defense_modules = enemy_ship_info.get("defense_modules", 0)
        utility_modules = enemy_ship_info.get("utility_modules", 0)
        print(f"Enemy Ship: {display_name} ({hull_id})")
        if module_count > 0:
            module_parts = []
            if weapon_modules > 0:
                module_parts.append(f"{weapon_modules} weapon")
            if defense_modules > 0:
                module_parts.append(f"{defense_modules} defense")
            if utility_modules > 0:
                module_parts.append(f"{utility_modules} utility")
            if module_parts:
                print(f"  Modules: {', '.join(module_parts)}")
    
    # Concise round summary
    print(f"\nPlayer hull: {player_hull_pct}%")
    print(f"Enemy hull: {enemy_hull_pct}%")
    print("\nAvailable Actions:")
    
    # Build numbered menu using labels directly from engine (contract-correct)
    # Do NOT hardcode action names - use what the engine provides
    options = {}
    for idx, action_label in enumerate(allowed_actions, start=1):
        print(f"{idx}) {action_label}")
        options[idx] = action_label
    
    # Get player selection
    while True:
        raw_choice = input("Select action: ").strip()
        try:
            selected = int(raw_choice)
            if selected in options:
                return options[selected]
            else:
                print(f"Invalid selection. Please choose 1-{len(options)}")
        except ValueError:
            print("Invalid input. Please enter a number.")


if __name__ == "__main__":
    main()
