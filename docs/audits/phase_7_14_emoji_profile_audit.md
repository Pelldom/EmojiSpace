# Phase 7.14 – Emoji Profile System Audit

**Date:** 2026-03-08  
**Scope:** Emoji Profile System (design/emoji_profile_contract.md v0.9.1 LOCKED)  
**Type:** Audit only — no implementation, no file changes.

---

## 1. Executive Summary

The repository is **partially ready** for Phase 7.14 formalization. **Biggest blocker:** entity_contract.md and several code/data surfaces still use **`emoji`** (string/glyph) instead of **`emoji_id`** (registry reference). MissionEntity, NPCEntity, ShipEntity, and base Entity all store or serialize `emoji`; the Emoji Profile contract requires exactly one primary emoji stored as **emoji_id** and resolution only via data/emoji.json. **Biggest advantage:** data/emoji.json and data/tags.json exist and are structured correctly; Roman numeral tier emoji (roman_i–roman_x) are present; world_state (situations/events) and destinations already use **emoji_id**; CLI already has a single glyph-resolution path (_emoji_glyph_for_id) that respects the registry. A first implementation slice can build on destinations and world_state as integration footholds while migrating entity/crew/ship/mission/reward/encounter from `emoji` to `emoji_id` and introducing a computed Emoji Profile builder.

---

## 2. Contract Baseline

The following is a precise summary of the locked Emoji Profile contract (design/emoji_profile_contract.md v0.9.1) relevant to implementation:

- **Purpose:** Defines a deterministic composite identity representation (“Emoji Profile”) that is **presentation-layer metadata only** and has **no simulation authority**. All emojis must be defined in **data/emoji.json**; emoji.json is the single source of truth for glyph and description.
- **Primary Emoji:** Exactly one per entity; required by entity_contract; immutable after creation; **stored as emoji_id** referencing emoji.json; must resolve to a valid emoji_id in data/emoji.json.
- **Tier Emoji:** Roman numeral derived from entity tier value; displayed immediately after Primary; **not stored independently**; derived dynamically; Roman numeral glyph must resolve via emoji.json. Tier display is **mandatory** for tiered entities.
- **Secondary Emojis:** Derived from tags, modules, traits, or other secondary identity attributes; stored as emoji_id references; resolved via emoji.json; **multiplicity preserved** (no deduplication unless owning system contract defines it).
- **Emoji Profile construction order:** (1) Primary Emoji, (2) Tier Emoji (if entity has tier), (3) Secondary Emojis sorted by system-defined deterministic rules.
- **Storage rules:** Entities store emoji_id, tier (if applicable), and secondary source identifiers (tag_ids, module_ids, etc.). Entities do **not** store the composite Emoji Profile string, derived composite emoji strings, Roman numeral glyphs directly, or raw emoji glyphs. Profile must always be **computed** from entity.emoji_id, entity.tier, secondary identifiers, and emoji.json.
- **Authority:** Emoji Profile must not affect simulation, branching logic, or behavior; strictly presentation metadata. All references must use emoji_id; systems must not embed raw emoji glyphs.

---

## 3. Data Audit

### 3.1 emoji.json

- **Exists:** Yes. Path: `data/emoji.json`.
- **Structure:** Array of objects. Each object has: `emoji_id` (string), `glyph` (string), `description` (string).
- **Glyph and description:** Present for all inspected entries; contract requirement satisfied.
- **Roman numeral ids:** Present. Exact ids: `roman_i`, `roman_ii`, `roman_iii`, `roman_iv`, `roman_v`, `roman_vi`, `roman_vii`, `roman_viii`, `roman_ix`, `roman_x`.
- **Non-Roman number emoji ids:** None. No decimal-digit or other number symbols found; only Roman numerals for tier.
- **Gaps for Phase 7.14:** None for tier display. Reward and encounter **placeholder** strings used in data (e.g. `cargo_placeholder`, `pirate_placeholder`) do **not** appear in emoji.json; those are data schema placeholders, not current emoji_id entries.

### 3.2 tags.json

- **Exists:** Yes. Path: `data/tags.json`.
- **Structure:** Array of objects. Each object has: `tag_id` (string), `emoji_id` (string), `description` (string). Some entries have optional `category`, `applies_to`.
- **Maps tag_id → emoji_id:** Yes. Every entry provides a tag_id and an emoji_id.
- **Completeness for currently used tags:** All tag_ids referenced in data (goods tags, hull traits, module primary_tag/secondary_tags, crew tag_ids, structural tags destroyed/salvage_site) appear in tags.json with a corresponding emoji_id. All those emoji_ids exist in data/emoji.json.
- **Unmapped tags:** None identified for in-repo entity tags.
- **Mappings to missing emoji ids:** None. All tag_id → emoji_id values in tags.json resolve to existing emoji_id entries in emoji.json.

### 3.3 Other Data Sources

- **Situations:** `data/situations.json` — entries include `emoji_id` (e.g. `situation_trade_boom`, `situation_economic_recession`). Resolve in emoji.json.
- **Events:** `data/events.json` — entries include `emoji_id` (e.g. `event_solar_flare_surge`, `event_war`). Resolve in emoji.json.
- **Destinations:** World generator and Destination dataclass use `emoji_id`; defaults by destination_type (exploration_site → location_unknown, resource_field → goods_category_ore) in `world_generator._default_emoji_id_for_destination_type`.
- **Goods:** `data/goods.json` — has `tags` arrays (e.g. essential, agricultural). Tag-to-emoji path: tag_id → tags.json → emoji_id → emoji.json. No emoji_id on goods themselves; secondary source for profile would be tags.
- **Modules:** `data/modules.json` — have `primary_tag` (e.g. combat:weapon_energy) and optional secondary; no emoji_id field. Module → emoji: primary_tag/secondary tags → tags.json → emoji_id.
- **Hulls:** `data/hulls.json` — have `tier`, `frame`, `traits` (e.g. ship:trait_civilian). No emoji_id; primary from trait (e.g. ship_trait_civilian in emoji.json via tags.json ship:trait_civilian → ship_trait_civilian).
- **Crew roles:** `data/crew_roles.json` — has `role_id` only; no emoji_id. emoji.json has crew_role_* (e.g. crew_role_pilot). Convention: role_id "pilot" → emoji_id "crew_role_pilot". No explicit role_id → emoji_id mapping file; convention is consistent with emoji.json ids.
- **Reward profiles:** `data/reward_profiles.json` — uses field **"emoji"** (not emoji_id) with placeholder values (cargo_placeholder, skull_crate_placeholder, credit_placeholder, etc.). These placeholder ids are **not** in emoji.json.
- **Encounter types:** `data/encounter_types.json` — uses **"emoji"** with placeholder values (trader_placeholder, pirate_placeholder, etc.). Not in emoji.json.

---

## 4. Contract Alignment Audit

### 4.1 entity_contract.md

- **Relevant rule:** Core Entity Fields (Section 3): every entity MUST define `emoji (string)`. Section 5: every entity MUST define exactly one emoji; emoji is immutable after creation; UI consumes, does not assign.
- **Compatible with Emoji Profile contract?** **No.** Emoji Profile requires primary emoji stored as **emoji_id** (reference to emoji.json), not as a string that may be glyph or id. Entity contract uses field name **"emoji"** and does not require resolution via emoji.json.
- **Exact mismatch:** Field name and semantics: entity_contract says "emoji (string)" and "symbolic identifier"; emoji_profile_contract requires "emoji_id" and resolution only through emoji.json. No mention of emoji_id in entity_contract.
- **Implementation impact:** **High.** All entities (base Entity, NPCEntity, ShipEntity, MissionEntity) and any code creating/serializing them must eventually align on emoji_id and registry resolution. Entity contract update required before or as part of Phase 7.14.

### 4.2 crew_contract.md

- **Relevant rule:** Section 6 Emoji Profile: crew emoji profile = primary (role emoji) + secondary (tag emojis); constructed per emoji_profile_contract; ordering: role emoji, then tag emojis in deterministic sorted order. Data dependencies include emoji_profile_contract.md and tags.json.
- **Compatible with Emoji Profile contract?** **Yes.** Crew contract explicitly references emoji_profile_contract and defines primary (role) + secondary (tags) with deterministic ordering. Crew do not store a composite string.
- **Mismatch:** None. Crew_roles.json does not contain emoji_id; convention "crew_role_" + role_id must be documented or centralized (e.g. in a small role→emoji_id map or in crew_roles.json addition) so profile builder has a single source.
- **Implementation impact:** **Medium.** Code must implement profile construction from role_id (→ primary emoji_id) and tag_ids (→ secondary emoji_ids via tags.json); no contract change required if convention is formalized.

### 4.3 ship_entity_contract.md

- **Relevant rule:** Section 8: Ship entity tracks condition_state and **condition_emoji**; emoji representation is thematic and informational.
- **Compatible with Emoji Profile contract?** **Partial.** Contract does not define primary emoji or emoji_id for ship identity. It defines condition_emoji (thematic). Emoji Profile expects ship primary (e.g. from frame/trait) + tier + secondaries (modules/tags). Ship entity contract is DRAFT and does not yet specify emoji_id or profile construction.
- **Exact mismatch:** No emoji_id or primary emoji source; condition_emoji is freeform. Emoji Profile requires primary as emoji_id and tier + secondaries from modules/tags.
- **Implementation impact:** **High.** Ship entity and ship presentation need primary emoji_id (e.g. from hull trait), tier from hull/ship state, and secondary emojis from module primary_tags and secondary_tags via tags.json. Contract update needed to align with Emoji Profile.

### 4.4 world_state_contract.md

- **Relevant rule:** Section 6: All Situations and Events must include **emoji_id (string)** and severity_tier. Emoji does not influence simulation logic. New tags must be synchronized with tags.json and emoji.json per emoji profile contract.
- **Compatible with Emoji Profile contract?** **Yes.** world_state already uses emoji_id; schema (Sections 15–16) shows emoji_id on situation and event objects.
- **Mismatch:** None.
- **Implementation impact:** **Low.** Situations and events are already an integration foothold; no contract change required for Emoji Profile.

### 4.5 ship_system_contract.md

- **Relevant rule:** Defines slot types, frames, tiers (I–V); no emoji or emoji_id fields in the sections reviewed.
- **Compatible with Emoji Profile contract?** **Partial.** No conflict; ship system does not define presentation. Tier and frame/trait feed into ship profile (tier → tier emoji; trait → primary).
- **Implementation impact:** **Low.** Profile builder will consume tier and hull traits; no contract change needed.

### 4.6 world_generation_destinations_contract.md

- **Relevant rule:** Defines destination-scoped fields; no emoji_id in the core schema listed in the contract. production_plan (Phase 7.12) states destination schema has optional emoji_id with defaults.
- **Compatible with Emoji Profile contract?** **Partial.** Implementation (world_generator, Destination) already has emoji_id; contract document does not yet spell out emoji_id. No conflict with Emoji Profile.
- **Implementation impact:** **Low.** Optional contract clarification to add emoji_id to destination-scoped fields.

### 4.7 mission_skeleton_contract.md

- **Relevant rule:** Mission identity includes mission_id, mission_type, mission_tier, etc.; no emoji or emoji_id in the sections reviewed.
- **Compatible with Emoji Profile contract?** **Partial.** Mission has mission_tier (for tier emoji). MissionEntity in code has **emoji** (str | None), not emoji_id; serialization uses "emoji". Contract does not specify emoji field.
- **Exact mismatch:** Code uses "emoji"; Emoji Profile expects emoji_id and computed profile (primary + tier + secondaries if any). Mission type could map to primary emoji_id (e.g. mission_delivery, mission_bounty in emoji.json).
- **Implementation impact:** **Medium.** Mission entity and mission display should migrate to emoji_id and optional profile (primary + tier); mission_skeleton contract could explicitly add emoji_id.

### 4.8 reward_profiles_schema_contract.md

- **Relevant rule:** RewardProfileObject must contain **"emoji": "string"**; placeholder allowed during early development. Example: "emoji": "crate_placeholder".
- **Compatible with Emoji Profile contract?** **No.** Emoji Profile requires all references to use emoji_id and resolve via emoji.json. Reward profile schema uses "emoji" and allows placeholders that are not in emoji.json.
- **Exact mismatch:** Field name "emoji" and placeholder semantics. Contract and data use placeholders that do not resolve in emoji.json. Migration path: rename to emoji_id and either add placeholder entries to emoji.json or define missing-mapping behavior for presentation.
- **Implementation impact:** **Medium.** Reward profiles are used for display/logging; Phase 7.14 can defer or add a migration rule (emoji_id + fallback when missing).

### 4.9 combat_and_ship_tag_contract.md

- **Relevant rule:** Defines tag namespaces (combat:*, ship:trait_*, secondary:*). States: "Emoji representations are presentation-layer only and are not part of this contract."
- **Compatible with Emoji Profile contract?** **Yes.** Tags are identifiers; emoji resolution is via tags.json → emoji.json. No conflict.
- **Implementation impact:** **Low.**

### 4.10 interaction_layer_contract.md

- **Relevant rule:** Governs encounter dispatch and actions; does not govern UI or presentation.
- **Compatible with Emoji Profile contract?** **Yes.** No emoji-specific rules; no conflict.
- **Implementation impact:** **Low.**

### 4.11 prose_contract.md

- **Relevant rule:** Prose is presentation-only; does not decide outcomes.
- **Compatible with Emoji Profile contract?** **Yes.** Emoji Profile is presentation-only; consistent.
- **Implementation impact:** **Low.**

### 4.12 encounter_types_schema_contract.md

- **Relevant rule:** (From grep) emoji: string (placeholder allowed).
- **Compatible with Emoji Profile contract?** **No.** Same as reward_profiles: "emoji" string and placeholders not in emoji.json.
- **Implementation impact:** **Medium.** Encounter types feed encounter display; migration to emoji_id or defined fallback needed for full alignment.

---

## 5. Code Audit

### 5.1 Existing presentation paths

- **CLI destination listing:** `src/run_game_engine_cli.py` — `_print_current_system_destinations`, `_print_travel_destinations`, and related helpers use `getattr(destination, "emoji_id", "")` then `_emoji_glyph_for_id(emoji_id)` to produce a glyph prefix. Destinations only; no composite profile.
- **Travel context / encounter header:** Same file uses `ctx.get("emoji_id", "")` and `_emoji_glyph_for_id` for travel/encounter context display.
- **Game engine profile surfaces:** `src/game_engine.py` — `get_destination_profile` / `get_system_profile` include `"emoji_id"` for destinations in returned dicts (lines 6843–6879). Used by CLI.
- **Logging:** No evidence of a dedicated log formatter that composes emoji strings; logs use structured data. Mission/ship/crew display in CLI use text (e.g. mission_tier, module_id, hull tier) but do not yet build an Emoji Profile string for entities.
- **Mission display:** CLI prints mission_type and mission_tier (e.g. "T3") but does not resolve mission primary emoji or tier emoji from registry.
- **Ship/crew display:** Ship listing shows hull name, tier, frame; crew listing shows role and data; no emoji_id or profile string built from registry.

### 5.2 Existing builder/helper paths

- **Glyph resolution only:** `_emoji_glyph_for_id(emoji_id: str) -> str` in `run_game_engine_cli.py` (lines 3594–3609). Loads data/emoji.json, returns glyph for emoji_id or "". Single point of registry resolution; no profile composition.
- **Destination emoji_id default:** `world_generator._default_emoji_id_for_destination_type(destination_type)` returns default emoji_id for exploration_site and resource_field. No other builder/formatter for composite profile (primary + tier + secondaries).

### 5.3 Hardcoded glyph audit

- **Code (.py):** No raw emoji glyphs found in source. All display uses `_emoji_glyph_for_id(emoji_id)` or equivalent (destination emoji_id). No hardcoded "🟡", "🔴", "⚔", etc. in Python.
- **Data (emoji.json):** Glyphs are stored in data/emoji.json as the registry; this is the required single source of truth and is acceptable.
- **Other data (reward_profiles.json, encounter_types.json):** Use string values like "cargo_placeholder", "pirate_placeholder"; these are identifiers, not glyphs, and they do not resolve in emoji.json — so any code that resolved them would get "". Not hardcoded glyphs but missing mappings.
- **Tests:** `tests/test_encounter_generator.py` uses "emoji": "pirate_placeholder", "authority_placeholder", "a", "b" in test payloads; these are schema/placeholder values, not glyphs.
- **Conclusion:** No problematic hardcoded glyphs in code. Only acceptable registry usage in emoji.json. Placeholder ids in reward_profiles and encounter_types are a data/contract gap, not hardcoding.

### 5.4 Simulation boundary audit

- **Does any emoji-related field affect gameplay logic?** No. Grep for branching on emoji/emoji_id in src shows only: (1) `if not emoji_id` or `if emoji_id` for choosing whether to show a glyph (presentation); (2) lookup in emoji.json for glyph. No combat, economy, enforcement, mission resolution, or RNG branches on emoji or emoji_id. world_state_contract explicitly states "Emoji does not influence simulation logic." **No violation found.**

---

## 6. Entity-Type Readiness Matrix

| Entity type      | Primary emoji source              | Tier source           | Secondary source candidates                    | Current readiness | Blockers |
|------------------|-----------------------------------|------------------------|-----------------------------------------------|------------------|----------|
| Base entities    | entity.emoji (not emoji_id)       | N/A                   | tags                                          | Low              | entity_contract + code use "emoji" not emoji_id |
| Crew             | role_id → convention crew_role_*  | rarity_tier (not numeric tier) | tag_ids → tags.json → emoji_id        | Medium           | No emoji_id on crew; no profile builder; rarity_tier vs tier semantics for tier emoji |
| Ships            | Hull trait (e.g. ship_trait_*)   | Hull/ship tier        | Module primary_tag + secondary_tags           | Low              | Ship has "emoji", condition_emoji; no emoji_id; no profile builder |
| Destinations     | destination.emoji_id              | N/A                   | tags (e.g. destroyed, salvage_site)           | High             | None for primary; secondaries optional |
| Locations        | location_type → location_* in emoji | N/A                 | N/A                                           | Medium           | Entity.emoji string; no emoji_id on location entity |
| Goods            | Category or first tag             | N/A                   | tags from goods.json                          | Medium           | No primary emoji_id on SKU; display uses tags/category |
| Events           | event.emoji_id in data            | severity_tier (internal) | N/A                                        | High             | None |
| Situations       | situation.emoji_id in data        | severity_tier (internal) | N/A                                        | High             | None |
| Missions         | mission_type → mission_* in emoji | mission_tier          | N/A                                           | Low              | MissionEntity.emoji not emoji_id; no profile builder |
| Reward profiles  | profile["emoji"] (placeholder)    | N/A                   | N/A                                           | Low              | Field "emoji" and placeholders not in emoji.json |

---

## 7. Number and Tier Audit

- **Are Roman numeral emoji ids already present in data/emoji.json?** **Yes.** Ids: `roman_i`, `roman_ii`, `roman_iii`, `roman_iv`, `roman_v`, `roman_vi`, `roman_vii`, `roman_viii`, `roman_ix`, `roman_x`.
- **Are there any number emoji ids besides Roman numerals?** **No.** Grep and inspection of emoji.json show no decimal-digit or other number-symbol emoji ids.
- **Does the repo require only Roman numerals for tier display?** **Yes.** Contract and data use Roman numerals for tier; ship_system and mission_skeleton use tiers I–V; no code or contract found that requires decimal digits or other number symbols for tier display.

---

## 8. Deterministic Ordering Audit

- **Tag or module order instability:** Crew tag_ids and ship module lists are stored in lists. Without a defined sort (e.g. by tag_id or by resolved emoji_id alphabetically), iteration order can be insertion-dependent. Emoji Profile contract requires "secondary emojis sorted by system-defined deterministic rules" and "reproducible from entity state." So any profile builder must sort secondary sources (e.g. tag_ids alphabetically, or emoji_id after resolution). No current code builds secondary-emoji list with a defined sort.
- **Sorting by emoji_id alphabetically:** Viable. tags.json and emoji.json provide tag_id → emoji_id; secondary list can be sorted by emoji_id (or by tag_id) for determinism. No conflict identified.
- **System-specific ordering rules:** combat_and_ship_tag_contract and crew_contract do not define display order for tags; emoji_profile_contract leaves "system-defined deterministic rules" to the owning system. So ship system could define e.g. weapon then defense then utility; crew could define tag order by tag_id. No existing system contract mandates an order that would conflict with alphabetical emoji_id sort if chosen.
- **Multiplicity:** Ship modules can repeat (e.g. two weapon_energy). Contract requires multiplicity preserved. Current ship state holds list of modules; multiplicity is storable. No deduplication in profile unless contract says so. Code does not yet build profile, so multiplicity handling is not yet implemented.

---

## 9. Test Coverage Audit

- **Tests that support Emoji Profile implementation:**  
  - `tests/test_exploration_mining_phase712.py`: Asserts destination `emoji_id` presence and defaults (exploration_site → location_unknown, resource_field → goods_category_ore).  
  - Tests that load world or destinations and assert structure (e.g. destination has emoji_id) indirectly support that destinations are profile-ready for primary emoji.
- **Missing tests for Phase 7.14:**  
  - Deterministic ordering: no test that builds a profile from fixed entity state and asserts exact string or exact ordered list of emoji_ids.  
  - Multiplicity preservation: no test that two identical tags or two identical modules produce two identical secondary emojis in profile.  
  - Missing mapping behavior: no test for behavior when emoji_id is missing in emoji.json or tag_id missing in tags.json (e.g. fallback to "" or placeholder).  
  - Registry-only resolution: no test that asserts no code path uses raw glyphs for entity identity; only _emoji_glyph_for_id and emoji.json are used.  
  - Mission/crew/ship entity: no tests that assert emoji_id field or profile construction for these entity types.

---

## 10. Phase 7.14 First-Slice Recommendation

**Smallest safe implementation slice:**

- **Add (new files):**  
  - A single **emoji profile module** (e.g. `src/emoji_profile.py` or under a presentation subpackage) that: (1) loads emoji.json (and optionally tags.json) once or on demand; (2) exposes a function to compute **profile string** or **ordered list of emoji_ids** from: primary emoji_id, optional tier (int), optional list of secondary emoji_ids; (3) uses deterministic sort for secondaries (e.g. by emoji_id); (4) preserves multiplicity; (5) resolves tier to roman_* via tier number; (6) returns glyph string only via emoji.json.  
  - No new data files in first slice.

- **Touch (existing files):**  
  - **run_game_engine_cli.py:** Use the new profile builder **only for destinations** at first: keep current destination emoji_id → glyph prefix; optionally add secondaries (e.g. destination tags) using the same builder so that destination display is "profile-like" without changing entity schema.  
  - **design/entity_contract.md:** In a separate formalization step, add a rule that entity primary emoji is stored as **emoji_id** and must resolve in emoji.json; keep backward compatibility note if "emoji" remains during migration.

- **Do NOT change in first slice:**  
  - Entity, NPCEntity, ShipEntity, MissionEntity field names or serialization (emoji vs emoji_id).  
  - reward_profiles.json or encounter_types.json schema or placeholder values.  
  - Game engine simulation logic or RNG.  
  - Crew/ship/mission display logic beyond what is needed to prove the profile builder (e.g. one destination with tags if available).

- **Entity types in first slice:**  
  - **Include:** Destinations (already have emoji_id); optionally situations/events (already emoji_id) for a second consumer of the same builder.  
  - **Defer:** Crew, ships, missions, reward profiles, encounter types, base entities, goods — until entity/schema migration and contract updates are agreed.

---

## 11. Final Findings

- **GO / NO-GO for formalization:** **GO**, with conditions. The repo has a solid data base (emoji.json, tags.json, Roman numerals, world_state and destinations using emoji_id) and a clear contract. Formalization should: (1) resolve entity_contract “emoji” vs “emoji_id” and define migration; (2) specify role_id → emoji_id for crew primary; (3) specify ship primary (e.g. hull trait → emoji_id); (4) define handling of reward/encounter placeholders (add to emoji.json or define fallback).

- **Required contract updates before implementation:**  
  - **entity_contract.md:** Require primary emoji as **emoji_id** (reference to emoji.json); deprecate or alias "emoji" for backward compatibility.  
  - **ship_entity_contract.md:** Add primary emoji_id (or source: hull trait); align condition_emoji with registry or mark as legacy.  
  - **reward_profiles_schema_contract.md** (and encounter_types if applicable): Prefer **emoji_id** and require resolution in emoji.json or document placeholder/fallback behavior.  
  - **mission_skeleton_contract.md:** Optionally add emoji_id for mission type.

- **Required data additions before implementation:**  
  - **emoji.json:** Add any missing emoji_ids that will be used as primary or secondary (e.g. mission types if mission profile is in scope). For first slice (destinations/situations/events only), no additions required.  
  - **reward_profiles / encounter_types:** Either add placeholder emoji_ids to emoji.json or agree that unresolved ids render as "" or a single "unknown" glyph.

- **Open questions for formalization / implementation prompt:**  
  1. Migration strategy for entity.emoji → entity.emoji_id: big-bang vs dual field (emoji_id optional, fallback to emoji) vs presentation-only builder that accepts either.  
  2. Crew tier: rarity_tier (common/uncommon/rare) vs numeric tier for tier emoji. Contract says "tier value"; crew_contract uses rarity_tier. Clarify whether crew show Roman tier and from what field.  
  3. Ship primary: single source (e.g. first hull trait, or frame-to-trait mapping) and how condition_emoji relates to profile (separate or part of profile).  
  4. Mission primary: mission_type → emoji_id mapping (e.g. delivery → mission_delivery); add to mission_definitions or central map.  
  5. Fallback for missing emoji_id in emoji.json: empty string vs reserved "unknown" emoji_id in registry.

— End of audit —
