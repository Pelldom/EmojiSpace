# Emoji Profile Consistency Pass Report

**Scope:** `src/emojispace_cli_v1.py` only.  
**Excluded:** `knowledge_state.py`, `game_engine.py`, `run_game_engine_cli.py`, `emoji_profile_builder.py`, data files, galaxy summary, debug suppression, prose layer.

---

## 1. Functions / areas changed

### New helper
- **`_format_cargo_for_display(engine, manifest)`** – Formats a cargo dict as a single player-facing line (e.g. `"Water 10, Food 5"` or `"none"`) using `_get_good_display_name` and `_compact_manifest`. Used everywhere cargo is shown outside the market.

### Player / Ship Info
- Replaced raw `cargo_manifest` dict print with `_format_cargo_for_display(engine, detail.get("cargo_manifest", {}))`.

### Ships And Modules
- Active ship cargo: now `Cargo: {_format_cargo_for_display(engine, cargo)}` (was `_compact_manifest` dict).
- Inactive ships cargo: same; "None" normalized to "none".

### Warehouse
- Warehouse list line: `goods={goods}` replaced with `goods={_format_cargo_for_display(engine, goods)}`.
- Warehouse profile / deposit / withdraw already used `_get_good_display_name` for each line; no change.

### System Info (`_show_system_info`)
- **Government:** Now uses `engine.government_registry.get_government(gov_id)` and prints `.name` (player-facing label) instead of raw `government_id`.
- **Active situations:** Formatted as `", ".join(situations)` when list; no raw Python list repr.
- **Active flags:** Same – comma-separated string when list.

### Destination Info (`_show_destination_info`)
- **System line:** Replaced incorrect `format_entity_name(..., system_name, sys_visible)` (3 args) with `_format_name_with_profile(system_obj, system_name, sys_visible)` so system name is profile-based and visibility is respected.
- **Active destination situations:** Comma-separated string when list; no raw repr.

### Crew dismissal
- Message changed from `Crew member {npc_id} dismissed...` to `Crew member {npc_name} dismissed...` using `_get_npc_name(engine, npc_id)`.
- System line in relocation: `format_entity_name(..., system_name, True)` (invalid 3-arg call) fixed to `_format_name_with_profile(..., system_name, True)`.

### Missions (outside Administration Mission Board)
- **Mission accepted (admin board flow):** All "Mission accepted: {mission_id}" now use title: `selected_mission.get("name") or selected_mission.get("mission_type") or mission_id`.
- **Mission accepted (NPC interaction flow):** Uses `mission_obj` from interaction result when present; fallback to `mission_id` when mission list not in result.
- **Available Missions (location_action / NPC):** Removed "Mission ID: ..." line; list shows `{type_display} (Tier N)` and Rewards only (player-facing).

### Cargo rewards (encounter resolution)
- **Cargo Rewards** in `_print_encounter_resolution_block`: `cargo_sku` replaced with `_get_good_display_name(engine, cargo_sku)` when `engine` is provided.

---

## 2. Summary by area

| Area | Changes |
|------|--------|
| **Ships** | Cargo under Ships And Modules now uses `_format_cargo_for_display`; ship names were already using `_entity_display` / `format_entity_name` (no change). |
| **Cargo / goods** | Player/Ship Info, Ships And Modules (active + inactive), Warehouse list, encounter resolution cargo rewards now use display names; no raw dict/sku in those screens. |
| **NPCs** | Crew dismissal message uses NPC display name instead of `npc_id`. Bar/administration NPC lists already used `_format_name_with_profile` and `display_name`. |
| **Missions** | Non-admin mission lists no longer show raw Mission ID; "Mission accepted" uses title/type where available. Admin board mission IDs unchanged. |
| **System info** | Government from registry name; situations and flags as comma-separated strings; no raw internal field repr. |
| **Destination info** | System line uses `_format_name_with_profile`; active destination situations as comma-separated string. |
| **Location text** | No structural change; headers already used `_format_current_location_display` and title-case. |

---

## 3. Validation

- **Ship displays:** Consistent use of `_entity_display` / hull-based entity and `_format_cargo_for_display` for cargo.
- **Cargo/goods:** No raw dict or sku_id in Player Info, Ships And Modules, Warehouse list, or encounter cargo rewards.
- **NPCs:** No raw `npc_id` in crew-dismissal message; lists already profile-based.
- **Missions:** Raw mission IDs removed from non-admin "Available Missions"; accept message uses title/type.
- **System/Destination info:** Government and situations/flags are player-facing; system line uses profile formatter.
- **Excluded areas:** No edits to galaxy summary, Admin Board mission IDs, debug suppression, prose, knowledge_state, game_engine, emoji_profile_builder, or data files.

---

## 4. File touched

- **`src/emojispace_cli_v1.py`** – All changes confined to this file.
