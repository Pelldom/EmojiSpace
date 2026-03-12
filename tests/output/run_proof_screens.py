"""Run only the two proof screens and write output to file. UTF-8."""
from __future__ import annotations

import sys
from pathlib import Path

repo = Path(__file__).resolve().parents[2]
src = repo / "src"
if str(src) not in sys.path:
    sys.path.insert(0, str(src))

from game_engine import GameEngine
from io import StringIO

# Create engine (no override)
engine = GameEngine(world_seed=12345, config={"system_count": 50}, starting_ship_override=None)

# Get profile and ship_info (same extraction as CLI)
from emojispace_cli_v1 import _extract_detail_from_stage
result = engine.execute({"type": "get_player_profile"})
detail = _extract_detail_from_stage(step_result=result, stage="player_profile")
if not detail:
    Path(repo / "tests" / "output" / "proof_screens_output.txt").write_text(
        "Error: could not get player profile\n", encoding="utf-8"
    )
    sys.exit(1)

ship_info = detail.get("ship")
if not ship_info:
    Path(repo / "tests" / "output" / "proof_screens_output.txt").write_text(
        "Error: no ship in profile\n", encoding="utf-8"
    )
    sys.exit(1)

# Ensure the active ship has at least one installed module so we can verify module emoji display
active_ship_entity = engine.get_active_ship()
if active_ship_entity:
    ship_id = active_ship_entity.get("ship_id")
    if ship_id:
        ship_entity = engine.fleet_by_id.get(ship_id) if getattr(engine, "fleet_by_id", None) else None
        if ship_entity and hasattr(ship_entity, "persistent_state"):
            mods = list(ship_entity.persistent_state.get("module_instances", []))
            if not mods:
                # Add one module so proof screens show module line with emoji
                mods.append({"module_id": "weapon_energy_mk1", "secondary_tags": []})
                ship_entity.persistent_state["module_instances"] = mods
            # Refresh ship_info so detail ship also has installed_modules for fallback path
            ship_info = detail.get("ship", {})
            if isinstance(ship_info, dict) and ship_info.get("ship_id") == ship_id:
                ship_info["installed_modules"] = [m.get("module_id") for m in mods if m.get("module_id")]

# Build module lines using the same helper as the two proof screens
from emojispace_cli_v1 import _get_ship_modules_display_lines, _get_ship_headline

buf = StringIO()
# Player / Ship Info block (minimal)
buf.write("=== PLAYER / SHIP INFO ===\n")
buf.write("Credits: %s\n" % detail.get("credits", 0))
ship_headline = _get_ship_headline(engine, ship_info)
buf.write("SHIP: %s\n" % ship_headline)
module_lines = _get_ship_modules_display_lines(engine, ship_info)
if module_lines:
    buf.write("Installed modules:\n")
    for line in module_lines:
        buf.write("  %s\n" % line)
else:
    buf.write("Installed modules: None\n")
player_block = buf.getvalue()

# Ships And Modules block
buf.truncate(0)
buf.seek(0)
active_ship = engine.get_active_ship()
buf.write("=== SHIPS AND MODULES ===\n")
if active_ship:
    buf.write("ACTIVE SHIP: %s\n" % _get_ship_headline(engine, active_ship))
    module_lines2 = _get_ship_modules_display_lines(engine, active_ship)
    if module_lines2:
        buf.write("Installed Modules:\n")
        for line in module_lines2:
            buf.write("  %s\n" % line)
    else:
        buf.write("Installed Modules: None\n")
else:
    buf.write("ACTIVE SHIP: None\n")
ships_block = buf.getvalue()

out_path = repo / "tests" / "output" / "proof_screens_output.txt"
out_path.write_text(
    "=== CAPTURED PLAYER / SHIP INFO ===\n" + player_block + "\n"
    "=== CAPTURED SHIPS AND MODULES ===\n" + ships_block,
    encoding="utf-8",
)
print("Written to", str(out_path))
