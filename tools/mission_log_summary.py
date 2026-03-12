from __future__ import annotations

import argparse
import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Dict, Set


def _load_hull_frames(project_root: Path) -> Dict[str, str]:
    """Load hull_id -> frame mapping from data/hulls.json (best-effort)."""
    hulls_path = project_root / "data" / "hulls.json"
    frames: Dict[str, str] = {}
    if not hulls_path.is_file():
        return frames
    try:
        with hulls_path.open("r", encoding="utf-8") as handle:
            payload = json.load(handle)
    except Exception:
        return frames
    entries = payload.get("hulls", []) if isinstance(payload, dict) else payload
    if not isinstance(entries, list):
        return frames
    for row in entries:
        if not isinstance(row, dict):
            continue
        hull_id = row.get("hull_id")
        frame = row.get("frame")
        if isinstance(hull_id, str) and hull_id and isinstance(frame, str) and frame:
            frames[hull_id] = frame
    return frames


def summarize_mission_log(log_path: Path, project_root: Path) -> Dict[str, Any]:
    """
    Parse a gameplay_seed_*.log file and return a structured JSON summary
    of mission-related activity.

    This does NOT modify any game logic; it is a pure log parser.
    """
    text = log_path.read_text(encoding="utf-8")

    # Regex patterns for key signals
    turn_re = re.compile(r"\[v[^\]]*\]\[turn (\d+)\]")
    world_seed_re = re.compile(r'"world_seed":\s*(\d+)')
    mission_create_re = re.compile(
        r"action=mission_create change=mission_id=(\S+)\s+source_type=(\S+)"
    )
    # mission_core accept event with JSON detail
    mission_accept_detail_re = re.compile(
        r'"action_id":\s*"mission_accept".*?"mission_id":\s*"([^"]+)"'
    )
    # location_action accept safeguard (less detailed, but record mission_id if present)
    mission_accept_location_re = re.compile(
        r"action=mission_manager change=accept .*mission_id=(\S+)"
    )
    # Completion events
    mission_state_transition_re = re.compile(
        r"action=mission_state_transition .*mission_id=(\S+).*outcome=completed"
    )
    mission_eval_completed_re = re.compile(
        r"action=mission_eval:completed .*mission_id=(\S+)\s+mission_type=(\S+)"
    )
    # Reward grants (Phase 7.11.2+ mission rewards)
    mission_reward_re = re.compile(
        r"action=mission_reward_granted .*mission_id=(\S+)\s+.*"
    )
    credits_field_re = re.compile(r"credits=(\d+)")
    goods_field_re = re.compile(r"goods=([a-zA-Z0-9_]+)\s+quantity=(\d+)")
    module_field_re = re.compile(r"module=([a-zA-Z0-9_]+)")
    hull_voucher_field_re = re.compile(r"hull_voucher=([a-zA-Z0-9_]+)")

    max_turn_seen = 0
    seed: int | None = None

    # Mission tracking
    missions_created_by_source: Dict[str, Set[str]] = defaultdict(set)
    missions_accepted: Set[str] = set()
    missions_completed: Set[str] = set()

    # Reward tracking
    credits_total = 0
    goods_rewards: Counter[str] = Counter()
    module_rewards: Counter[str] = Counter()
    hull_vouchers_by_hull: Counter[str] = Counter()

    for line in text.splitlines():
        m_turn = turn_re.search(line)
        if m_turn:
            try:
                t = int(m_turn.group(1))
                if t > max_turn_seen:
                    max_turn_seen = t
            except ValueError:
                pass

        if seed is None:
            m_seed = world_seed_re.search(line)
            if m_seed:
                try:
                    seed = int(m_seed.group(1))
                except ValueError:
                    seed = None

        m = mission_create_re.search(line)
        if m:
            mission_id, source_type = m.groups()
            missions_created_by_source[source_type].add(mission_id)
            continue

        m = mission_accept_detail_re.search(line) or mission_accept_location_re.search(
            line
        )
        if m:
            missions_accepted.add(m.group(1))
            continue

        m = mission_state_transition_re.search(line)
        if m:
            missions_completed.add(m.group(1))
            continue

        m = mission_eval_completed_re.search(line)
        if m:
            missions_completed.add(m.group(1))
            continue

        m = mission_reward_re.search(line)
        if m:
            # Credits
            mc = credits_field_re.search(line)
            if mc:
                try:
                    credits_total += int(mc.group(1))
                except ValueError:
                    pass
            # Goods
            mg = goods_field_re.search(line)
            if mg:
                sku_id, qty = mg.groups()
                try:
                    goods_rewards[sku_id] += int(qty)
                except ValueError:
                    pass
            # Modules
            mm = module_field_re.search(line)
            if mm:
                module_rewards[mm.group(1)] += 1
            # Hull vouchers
            mh = hull_voucher_field_re.search(line)
            if mh:
                hull_vouchers_by_hull[mh.group(1)] += 1

    # Derive hull voucher counts by frame for XA / XB / XC / ALN, if hull catalog is present
    hull_frames = _load_hull_frames(project_root)
    hull_vouchers_by_frame: Counter[str] = Counter()
    for hull_id, count in hull_vouchers_by_hull.items():
        frame = hull_frames.get(hull_id, "UNKNOWN")
        hull_vouchers_by_frame[frame] += count

    return {
        "log_path": str(log_path),
        "seed": seed,
        "max_turn_seen": max_turn_seen,
        "missions": {
            "created_by_source_type": {
                source: sorted(mids) for source, mids in missions_created_by_source.items()
            },
            "accepted_ids": sorted(missions_accepted),
            "completed_ids": sorted(missions_completed),
        },
        "rewards": {
            "credits_total": credits_total,
            "goods_totals": dict(goods_rewards),
            "module_totals": dict(module_rewards),
            "hull_vouchers": {
                "by_hull_id": dict(hull_vouchers_by_hull),
                "by_frame": dict(hull_vouchers_by_frame),
            },
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Summarize mission-related activity from a gameplay_seed_*.log file "
            "and emit a structured JSON document to stdout."
        )
    )
    parser.add_argument(
        "--log",
        dest="log_path",
        default="logs/gameplay_seed_12345.log",
        help="Path to gameplay log file (default: logs/gameplay_seed_12345.log)",
    )
    args = parser.parse_args()

    project_root = Path(__file__).resolve().parents[1]
    log_path = (project_root / args.log_path).resolve() if not Path(args.log_path).is_absolute() else Path(args.log_path)

    if not log_path.is_file():
        raise SystemExit(f"Log file not found: {log_path}")

    summary = summarize_mission_log(log_path=log_path, project_root=project_root)
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

