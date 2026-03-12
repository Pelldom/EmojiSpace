# Phase 7.14B – Entity emoji_id Coverage Audit

**Objective:** Map all in-game entity types to the Emoji Profile Builder contract (emoji_id, optional tier, optional tags) and identify where emoji_id is missing so Phase 7.14C can add it without affecting gameplay.

**Rules:** Emoji Profiles are presentation-only. Builder expects entity.emoji_id (string), entity.tier (optional int), entity.tags (optional list of tag_id). Resolution is via data/emoji.json and data/tags.json only; no hardcoded glyphs in engine logic.

---

## SECTION 1 – ENTITY TYPES DISCOVERED

| Entity Type | Source File | Creation Function | emoji_id Present | tags Present | tier Present |
|-------------|-------------|-------------------|-------------------|--------------|--------------|
| System | world_generator.py | WorldGenerator.generate() → _generate_system / system construction in generate() | No | No | No |
| Destination (planet/station) | world_generator.py | _generate_destinations_for_system() | No | Yes (field exists, often empty) | No |
| Destination (exploration_site) | world_generator.py | _generate_destinations_for_system() | Yes | Yes | No |
| Destination (resource_field) | world_generator.py | _generate_destinations_for_system() | Yes | Yes | No |
| Location | world_generator.py | _add_location_if_missing() | No | No | No |
| EncounterSpec / encounter | encounter_generator.py | generate_encounter() | No (has .emoji glyph placeholder only) | No (encounter_type has default_flags, not tags) | No |
| NPC ship (dict) | npc_ship_generator.py | generate_npc_ship() | No | No (module_instances have secondary_tags per module) | No on dict (tier in hull data) |
| Ship info (CLI dict) | game_engine.py | _format_ship_info_frame_only(), _format_ship_info() | No | No | Yes (frame_only has tier) |
| Player ship (ShipEntity) | game_engine.py, interaction_resolvers.py | _build_default_fleet(), _build_override_fleet(), execute_buy_hull ship creation | No | Yes | No (tier in hull/persistent_state) |
| Good (catalog) | data_catalog.py | _load_goods() from data/goods.json | No | Yes | No |
| Ship module (instance dict) | various | module_instances entries (game_engine, npc_ship_generator, reward_service) | No | Yes (secondary_tags) | No |
| Crew NPC (NPCEntity) | game_engine.py, npc_placement.py | _ensure_mission_contact_npc(), _ensure_structural_npcs(), crew_npc in bar, npc_placement | No | Yes (role_tags, crew_tags) | No (persistence_tier exists) |
| Crew pool entry (dict) | crew_generator.py | generate_hireable_crew() | No | No | No |
| Mission (MissionEntity) | mission_factory.py, game_engine.py | create_mission(), create_delivery_mission(), create_bounty_mission(), etc. | No | Yes | Yes (mission_tier) |
| Hull (data) | data/hulls.json | Loaded by data_loader | No | No (has frame, tier) | Yes (in data) |
| Module (data) | data/modules.json | Loaded by data_loader | No | No | No |

---

## SECTION 2 – ENTITIES MISSING emoji_id

1. **System** – `src/world_generator.py`: System dataclass and construction in `WorldGenerator.generate()` (systems list built from _generate_system or equivalent loop). No emoji_id field on System.

2. **Destination (planet)** – `src/world_generator.py`: `_generate_destinations_for_system()` lines ~574–585. `Destination()` built without `emoji_id` (and without `tags`). Only exploration_site and resource_field pass `emoji_id` via `_default_emoji_id_for_destination_type()`.

3. **Destination (station)** – `src/world_generator.py`: `_generate_destinations_for_system()` lines ~631–634. Same as planet: no `emoji_id` passed.

4. **Location** – `src/world_generator.py`: `Location` dataclass has no emoji_id. Instances created in `_add_location_if_missing()` (location_id, destination_id, location_type, enabled, notes).

5. **EncounterSpec / encounter** – `src/encounter_generator.py`: `generate_encounter()` builds `EncounterSpec(..., emoji=subtype["emoji"], ...)`. Encounter types use "emoji" (glyph placeholder from data), not emoji_id. No tags on spec.

6. **NPC ship dict** – `src/npc_ship_generator.py`: `generate_npc_ship()` returns dict with hull_id, module_instances, degradation_state, current_hull_integrity, current_fuel. No emoji_id, no top-level tags (module_instances have secondary_tags).

7. **Ship info dict (CLI)** – `src/game_engine.py`: `_format_ship_info_frame_only()` (lines 6581–6604) and `_format_ship_info()` (6606–6648) return dicts with hull_id, hull_name, frame, tier (frame_only) or module counts. Neither includes emoji_id or tags.

8. **Player ship (ShipEntity)** – `src/game_engine.py`: `_build_default_fleet()` (6338), `_build_override_fleet()` (6528); `src/interaction_resolvers.py`: `execute_buy_hull` (271). ShipEntity has `emoji` (glyph), `tags`; no `emoji_id`. No tier on entity (tier in hull / persistent_state).

9. **Good (catalog)** – `src/data_catalog.py`: `Good` dataclass (sku, name, category, base_price, tags, possible_tag, harvestable). No emoji_id. Created in `_load_goods()` from data/goods.json.

10. **Crew pool entry** – `src/crew_generator.py`: `generate_hireable_crew()` returns list of dicts with role_id, hire_cost, daily_wage. No emoji_id, no tags.

11. **Crew NPC (NPCEntity)** – `src/game_engine.py`: `_ensure_mission_contact_npc()` (2237), `_ensure_structural_npcs()` required_npc (7370), crew_npc in bar (7601); `src/npc_placement.py` (23). NPCEntity has `emoji`, `tags`, `role_tags`, `crew_tags`; no `emoji_id`.

12. **Mission (MissionEntity)** – `src/mission_factory.py`: `MissionEntity()` in `create_mission()` (37), `create_delivery_mission()` (330), `create_bounty_mission()` (482), and other create_*_mission functions. MissionEntity has `emoji`, `tags`, `mission_tier`; no `emoji_id`.

13. **Hull (data)** – `data/hulls.json`: hull entries have hull_id, tier, frame, etc.; no emoji_id.

14. **Module (data)** – `data/modules.json`: module entries have module_id, slot_type, etc.; no emoji_id.

---

## SECTION 3 – TAGS AVAILABLE FOR DERIVATION

| Entity Type | Tags / identifiers typically present | Map via tags.json to emoji_id? |
|-------------|--------------------------------------|--------------------------------|
| Destination (planet/station) | destination_type ("planet", "station") | No tag_id for type; emoji.json has location_planet, location_station (could be used for display). |
| Encounter | subtype_id (e.g. pirate_raider, civilian_trader_ship, asteroid_field) | subtype_id can map to encounter_* in emoji.json (e.g. encounter_pirate, encounter_trader, encounter_asteroid_field). Not in tags.json; 1:1 mapping in code or data. |
| NPC ship | encounter_subtype, hull frame (CIV/MIL/FRG/XA), module_instances[].secondary_tags | secondary:* tags map in tags.json to secondary_* emoji_id. Frame → ship_trait_civilian, ship_trait_military, ship_trait_freighter, ship_trait_experimental. Subtype → encounter_* for primary. |
| Player ship | model_id (hull_id), persistent_state.module_instances[].secondary_tags | Same as NPC: hull frame from hulls data → ship_trait_*; secondary_tags → tags.json. |
| Good | good.tags (e.g. luxury, agricultural), category | tags map in tags.json (e.g. luxury → goods_luxury). Category could map to goods_category_* in emoji.json. |
| Crew pool entry | role_id (pilot, gunner, etc.) | No tag_id; role_id maps to crew_role_pilot, crew_role_gunner, etc. in emoji.json. |
| Crew NPC | role_tags, crew_tags | crew:* tags map in tags.json to crew_* emoji_id. role_tags (e.g. pilot) → crew_role_pilot. |
| Mission | mission_type (delivery, bounty, patrol, etc.), tags | mission_type → mission_delivery, mission_bounty, etc. in emoji.json. mission_tags may map via tags if extended. |
| Location | location_type (bar, market, shipdock, etc.) | location_type → location_bar, location_market, location_shipdock, etc. in emoji.json. |
| System | government_id, name | No current tag; no system_* in emoji.json. Could add system generic or leave name-only. |
| Module instance | module_id, secondary_tags | module slot/type maps to combat_* or ship_utility_*; secondary_tags map in tags.json. |

---

## SECTION 4 – PRIMARY EMOJI RECOMMENDATIONS

| Entity Type | Recommended emoji_id | emoji.json status |
|-------------|----------------------|--------------------|
| Destination (planet) | destination_planet or location_planet | location_planet exists; destination_planet does not. |
| Destination (station) | destination_station or location_station | location_station exists; destination_station does not. |
| System | (optional) system_generic or omit | No system_* in registry; could add or leave profile to name only. |
| Location | location_{location_type} | location_bar, location_market, location_shipdock, location_administration, location_datanet, location_planet, location_station, location_unknown exist. |
| Encounter (NPC) | encounter_{subtype_id normalized} | encounter_pirate, encounter_trader, encounter_raider, encounter_authority, encounter_bounty_hunter, encounter_derelict_ship, encounter_derelict_station, encounter_distress exist. Subtype_id civilian_trader_ship → encounter_trader; pirate_raider → encounter_pirate; customs_patrol → encounter_authority; blood_raider → encounter_raider; etc. |
| Encounter (environmental) | encounter_asteroid_field, encounter_ion_storm, etc. | encounter_asteroid_field, encounter_comet, encounter_debris_storm, encounter_ion_storm, encounter_spatial_rift, encounter_ancient_beacon, encounter_quantum_echo, encounter_wormhole exist. |
| NPC ship | ship_trait_* from hull frame, or encounter_* from encounter_subtype | Prefer storing emoji_id from encounter_subtype (e.g. encounter_pirate) for primary; tier from hull; tags from module_instances secondary_tags. ship_trait_civilian, ship_trait_freighter, ship_trait_military, ship_trait_experimental exist. |
| Player ship | ship_trait_* from hull frame (CIV→civilian, FRG→freighter, MIL→military, XA→experimental) | Same ship_trait_* as above. |
| Good | goods_luxury, goods_agricultural, etc. from first tag or goods_category_* from category | goods_* and goods_category_* exist; prefer primary from tag (e.g. luxury → goods_luxury) or category. |
| Crew NPC / pool | crew_role_pilot, crew_role_gunner, etc. from role_id | crew_role_* exist for pilot, gunner, tactician, engineer, mechanic, navigator, broker, quartermaster, lawyer, science. |
| Mission | mission_delivery, mission_bounty, mission_patrol, mission_exploration, etc. from mission_type | mission_delivery, mission_bounty, mission_transport, mission_salvage, mission_exploration, mission_illegal, mission_active, mission_completed, mission_failed exist. |
| Hull (data) | (display only if needed) ship_trait_* from frame | As above. |
| Module (data) | combat_* or ship_utility_* from module_id/slot | combat_weapon_energy, ship_utility_probe_array, etc. exist. |

---

## SECTION 5 – INTEGRATION POINTS

Exact functions/locations where emoji_id (and where relevant tier/tags) should be set so the builder can show profiles:

1. **world_generator.py**
   - **Destination (planet):** In `_generate_destinations_for_system()`, when building the first `Destination()` for planet (the one appended to `destinations`), add `emoji_id=...` (e.g. `"location_planet"` or new `"destination_planet"`). Same for **station**: add `emoji_id=...` (e.g. `"location_station"` or `"destination_station"`). Optional: set `tags` if any (e.g. from economy).
   - **Location:** If locations are ever passed to the profile builder, add emoji_id when creating `Location` in `_add_location_if_missing()` (e.g. from location_type → `f"location_{location_type}"`). Alternatively, resolve only at display time from location_type.

2. **encounter_generator.py**
   - **EncounterSpec:** In `generate_encounter()`, when building `EncounterSpec`, add a field `emoji_id` derived from `subtype["subtype_id"]` (e.g. mapping subtype_id to encounter_pirate, encounter_trader, encounter_asteroid_field, etc.). Do not store glyph; store emoji_id only. If CLI/display uses the spec, expose emoji_id there.

3. **npc_ship_generator.py**
   - **NPC ship dict:** In `generate_npc_ship()`, after building the return dict, add `"emoji_id"` (from encounter_subtype → encounter_* mapping) and `"tier"` (from hull["tier"]), and `"tags"` (aggregate list of all secondary_tags from module_instances). Alternatively, add emoji_id/tier/tags in game_engine when formatting for CLI.

4. **game_engine.py**
   - **Ship info dict (CLI):** In `_format_ship_info_frame_only()` and/or `_format_ship_info()`, add `"emoji_id"` (from hull frame → ship_trait_* or from encounter context if available), `"tier"` (already in frame_only), and `"tags"` (from ship_dict["module_instances"] secondary_tags aggregated). This is the object passed to CLI for `_format_name_with_profile(enemy_ship_info, ...)`.
   - **get_current_destination_context:** Already passes through destination emoji_id; no change if destinations get emoji_id at creation.
   - **Player ShipEntity:** When building ShipEntity in `_build_default_fleet()` and `_build_override_fleet()`, set `emoji_id` on the entity from hull data (frame → ship_trait_*). Optionally set `tags` from module_instances secondary_tags. Tier can be read from hull or persistent_state when building profile.

5. **interaction_resolvers.py**
   - **ShipEntity (buy hull):** In `execute_buy_hull`, when constructing `ShipEntity(...)`, set `emoji_id` from hull_data frame → ship_trait_*.

6. **data_catalog.py**
   - **Good:** When building `Good` in `_load_goods()`, add an `emoji_id` field (e.g. from first tag → goods_* via tags.json, or category → goods_category_*). Requires Good dataclass to gain optional emoji_id.

7. **crew_generator.py**
   - **Crew pool entry:** In `generate_hireable_crew()`, for each dict appended to `pool`, add `"emoji_id"` from role_id (e.g. pilot → crew_role_pilot). Optionally add `"tags"` (e.g. from role or empty list).

8. **game_engine.py (NPC/crew)**
   - **NPCEntity:** When creating NPCEntity in `_ensure_mission_contact_npc()`, `_ensure_structural_npcs()`, and bar crew creation, set `emoji_id` from role (e.g. mission_giver → generic NPC emoji if exists, or crew_role_* from role_tags). role_tags/crew_tags already present for secondary.

9. **mission_factory.py**
   - **MissionEntity:** When creating MissionEntity in `create_mission()` and all `create_*_mission()` functions, set `emoji_id` from mission_type (e.g. delivery → mission_delivery, bounty → mission_bounty). mission_tier and tags already on entity.

10. **run_game_engine_cli.py (visibility layer)**
    - Confirmed: destination lists and destination info use engine’s destination object (from sector); system lists use engine’s system object; encounter/combat use npc_ship_info/enemy_ship_info dicts from game_engine. So injecting emoji_id (and tier/tags) at creation or in _format_ship_info_* ensures the same structures the CLI receives have the fields the builder needs. No need to strip or duplicate; add at source.

---

## SECTION 6 – EMOJI REGISTRY READINESS (data/emoji.json)

**Coverage check (read-only):**

- **Systems:** No `system_*` entry. Could add `system_generic` or omit primary for systems.
- **Stations / outposts / planets:** `location_station`, `location_planet` exist. No `destination_station` or `destination_planet`; can reuse location_* or add destination_*.
- **Ships:** `ship_trait_civilian`, `ship_trait_freighter`, `ship_trait_military`, `ship_trait_experimental`, `ship_trait_alien` exist.
- **Pirates / traders / raiders / authorities:** `encounter_pirate`, `encounter_trader`, `encounter_raider`, `encounter_authority`, `encounter_bounty_hunter` exist.
- **Asteroid fields / storms / derelicts:** `encounter_asteroid_field`, `encounter_ion_storm`, `encounter_debris_storm`, `encounter_comet`, `encounter_derelict_ship`, `encounter_derelict_station`, `encounter_distress` exist.
- **Goods:** `goods_*` and `goods_category_*` (ore, food, luxury, etc.) exist.
- **Crew:** `crew_role_*` (pilot, gunner, engineer, etc.) and `crew_*` traits (wanted, alien, etc.) exist.
- **Missions:** `mission_delivery`, `mission_bounty`, `mission_transport`, `mission_salvage`, `mission_exploration`, `mission_illegal`, `mission_active`, `mission_completed`, `mission_failed` exist.
- **Locations:** `location_bar`, `location_market`, `location_shipdock`, `location_administration`, `location_datanet`, `location_planet`, `location_station`, `location_unknown` exist.
- **Environments/anomalies:** `encounter_spatial_rift`, `encounter_ancient_beacon`, `encounter_quantum_echo`, `encounter_wormhole` exist.

Registry is sufficient for the recommended emoji_ids; only optional additions would be `destination_planet` / `destination_station` and `system_generic` if desired.

---

*End of Phase 7.14B audit. No source or data files were modified.*
