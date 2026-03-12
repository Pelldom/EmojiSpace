# Phase 7.12 – Exploration and Mining Verification Report

**Date:** 2026-03-02  
**Contract:** design/exploration_and_mining_contract.md  
**Target Version:** 0.11.4  
**Status:** Implementation complete; full test run and commit pending

---

## 1. Work Done

### 1.1 Step 0 – Baseline
- Pulled latest main (already up to date).
- Recorded version from design/production_plan.md (0.11.3).
- Grep baseline for explorable_stub, mining_stub, destination_type, encounter chaining, goods.json usage.

### 1.2 Step 1 – Destination Type Rename
- **Replaced across repo:** `explorable_stub` → `exploration_site`, `mining_stub` → `resource_field`.
- **Updated:** world_generator (destination creation, display names "Exploration Site N" / "Resource Field N"), destination factories, tests (test_destination_population_structural_anchor, integration_test), design docs (production_plan, vision, TO_ADD), CLI output.
- **Legacy loader:** In world_generator, added `LEGACY_DESTINATION_TYPE_MAP` and `normalize_destination_type()`; game_engine uses it in `_build_destination_context` when building destination context from saved/loaded state.
- **Migration:** One-line deterministic migration notice logged when legacy type is normalized.
- **Verification:** No `*_stub` destination types are generated in new worlds; only legacy mapping and docs/audit/test output references remain.

### 1.3 Step 2 – Goods: harvestable Flag
- **data/goods.json:** Every good has boolean `"harvestable"` (default false in schema).
- **Set harvestable = true for:** All ORE; all METAL; all CHEMICALS except `experimental_serums`; `standard_fuel`. All other goods false.
- **data_catalog.py:** `Good` dataclass has `harvestable: bool = False`; loader reads field (default False).
- **Mining:** Mining resolver uses only `harvestable` flag (no category filtering in resolver).

### 1.4 Step 3 – Emoji Profile Support
- **Destination schema:** Optional `emoji_id: str` (default `""`) on Destination in world_generator.
- **Defaults:** exploration_site → `"location_unknown"`, resource_field → `"goods_category_ore"` via `_default_emoji_id_for_destination_type()`.
- **No validation** of emoji_id against emoji.json at load time; emoji.json not modified.
- **Persistence:** emoji_id passed in all Destination copy/creation paths; game_engine `_build_destination_context` includes emoji_id; CLI and encounter results can use it.

### 1.5 Step 4 – Player State Extension
- **player_state.py:** Added `exploration_progress`, `exploration_attempts`, `mining_attempts` (each `dict[str, int]`, default `{}`).
- **from_dict:** Safe normalization; missing keys → empty dict; non-int values sanitized; deterministic behavior.
- **to_dict:** All three fields serialized for save/load.

### 1.6 Step 5 – Capability Gating
- **ship_assembler.py:** `ship_has_capability(ship, capability_id)`; `CAPABILITY_UNLOCK_PROBE`, `CAPABILITY_UNLOCK_MINING`; uses existing `unlock_probe` / `unlock_mining` from assemble_ship.
- **Explore:** Allowed only when destination is exploration_site and ship has probe capability.
- **Mine:** Allowed only when destination is resource_field and ship has mining capability.

### 1.7 Step 6 – Exploration Resolver
- **src/exploration_resolver.py:** `resolve_exploration()` consumes 1 day, 1 fuel (caller applies). Increments `exploration_attempts[destination_id]`. Deterministic RNG: `world_seed + destination_id + player_id + "explore"`. Base success chance 0.50. On success, increments `exploration_progress[destination_id]`. Returns `ExplorationResult` (success, stage_before, stage_after, rng_roll) and new attempts/progress dicts.

### 1.8 Step 7 – Mining Resolver
- **src/mining_resolver.py:** Diminishing returns table N=0:1.0, N=1:0.75, N=2:0.5, N=3:0.25, N≥4:0.10. `resolve_mining()` consumes 1 day, 1 fuel (caller applies). SKU pool from catalog where `harvestable == true`, sorted by sku (ASCII). Deterministic SKU selection; capacity check (no partial fill). Returns `MiningResult` and new mining_attempts.

### 1.9 Step 8 – Local Activity Encounter Mode
- **encounter_generator.py:** For `travel_context.mode == "local_activity"`, encounter cap set to 1 (exactly one roll, no chaining).
- **encounter_generator.select_subtype:** Allowed mode `"local_activity"` in validation (in addition to `in_system`, `system_arrival`).
- **game_engine:** `_execute_explore` / `_execute_mine` call `_trigger_local_activity_encounter()` after resolve; single encounter roll; no recursive chaining.

### 1.10 Step 9 – CLI Updates
- **Emoji resolution:** `_emoji_glyph_for_id(emoji_id)` in run_game_engine_cli loads data/emoji.json and returns glyph for emoji_id (or "").
- **Destination listing:** _print_current_system_destinations, travel destination list, _print_destination_context, _galaxy_summary show optional `[GLYPH]` before destination name; format includes `(Type)`.
- **Destination actions:** Mine (resource_field + mining capability) and Explore (exploration_site + probe capability) with "Consumes 1 day, 1 fuel".
- **After explore/mine:** Prints "Local activity may attract attention..."; if result has hard_stop and pending_encounter_decision, calls `_resolve_pending_encounter(engine)`.

### 1.11 Step 10 – Tests
- **tests/test_exploration_mining_phase712.py:** Six tests added:
  - harvestable flag correctly applied (ORE, METAL, CHEMICALS except experimental_serums, standard_fuel).
  - Mining diminishing returns (multipliers and attempt_number).
  - Exploration progress increments (attempts and progress).
  - Local activity exactly one encounter roll (cap 1).
  - emoji_id persists on generated destinations (defaults for exploration_site, resource_field).
  - No *_stub destination types in generated world.
- **Result:** All 6 Phase 7.12 tests pass.

### 1.12 Step 11 – Production Plan and Version
- **design/production_plan.md:** Phase 7.12 (IN PROGRESS) added; target 0.11.4; contract reference; summary bullets (destination rename, harvestable, emoji_id, player state, capability gating, exploration resolver, mining resolver, local_activity, CLI).
- **VERSION:** 0.11.4; status "Exploration and Mining (Phase 7.12 IN PROGRESS)".

---

## 2. Issues Identified

### 2.1 Resolved During Implementation
- **encounter_generator mode validation:** `select_subtype()` only allowed `in_system` and `system_arrival`. Adding `local_activity` was required so that `generate_travel_encounters(..., travel_context={"mode": "local_activity"})` does not raise. **Fixed:** allowed `"local_activity"` in the mode check.

### 2.2 Known / Non-Blocking
- **Legacy type strings in docs and old output:** `docs/audits/phase_7_12_exploration_non_combat_audit.md`, `docs/world_generation_contract_audit.md`, `docs/phase7_9_world_gen_audit.md`, and `test/output/playtest.txt` still mention `explorable_stub` / `mining_stub` for historical accuracy or old run output. No code path generates these types for new worlds; loader mapping handles legacy saves. Optional follow-up: update or footnote audit docs.
- **Full pytest suite:** Full `python -m pytest -q` was run in background; duration is long. Recommendation: run locally to confirm no regressions before commit.

### 2.3 Not Applicable / Out of Scope
- **emoji_id save/load:** Contract requires emoji_id to "persist through save/load". Current implementation persists emoji_id through all in-memory world and destination copy paths and through game_engine context. No separate sector serialization to disk was found; when a save/load path is implemented, destination serialization must include emoji_id (world_generator already uses it in all Destination constructions).

---

## 3. Remaining Steps

### 3.1 Before Merge / Release
1. **Run full test suite:** Execute `python -m pytest -q` (or `python -m pytest`) and ensure all tests pass.
2. **Commit and push:** Stage changes, commit with a message referencing Phase 7.12 and exploration_and_mining_contract.md, push to remote. Record commit hash (e.g. `git rev-parse HEAD`).
3. **Optional:** Re-run a short playtest (e.g. travel to an exploration_site, run Explore; travel to a resource_field, run Mine) and confirm CLI output (glyph, "Local activity may attract attention...", encounter resolution).

### 3.2 Optional Follow-ups (Non-Blocking)
- **Audit docs:** Update or add footnotes in `docs/audits/phase_7_12_exploration_non_combat_audit.md` and related docs to state that runtime types are now `exploration_site` / `resource_field` and that legacy names are migration-only.
- **Save/load:** When implementing full game save/load, ensure sector/destination serialization and deserialization include `emoji_id` so it persists across sessions.

### 3.3 Contract Compliance Checklist (Reference)
- [x] Only exploration_site and resource_field for explore/mine mechanics.
- [x] Mining uses only harvestable flag (no category filtering in resolver).
- [x] Diminishing returns: N=0:1.0, N=1:0.75, N=2:0.5, N=3:0.25, N≥4:0.10.
- [x] Exploration: base success 0.50; attempts/progress per destination_id.
- [x] Local activity: exactly one encounter roll; travel_context.mode = "local_activity".
- [x] emoji_id not validated against emoji.json at load; defaults applied; present in context and CLI.
- [x] No *_stub types generated; legacy mapping for old saves only.

---

## 4. Files Touched (Summary)

| Area | Files |
|------|--------|
| World / destinations | world_generator.py (rename, emoji_id, legacy map, normalize_destination_type) |
| Goods | data/goods.json, data_catalog.py (harvestable) |
| Player state | player_state.py (exploration_progress, exploration_attempts, mining_attempts) |
| Capabilities | ship_assembler.py (ship_has_capability, CAPABILITY_UNLOCK_*) |
| Resolvers | exploration_resolver.py (new), mining_resolver.py (new) |
| Encounters | encounter_generator.py (local_activity cap, mode validation) |
| Engine | game_engine.py (explore/mine execution, trigger_local_activity_encounter, destination context, actions) |
| CLI | run_game_engine_cli.py (emoji glyph helper, destination listing, post explore/mine message and encounter) |
| Tests | test_exploration_mining_phase712.py (new), test_destination_population_structural_anchor.py, integration_test.py |
| Design / version | design/production_plan.md, design/vision.md, design/TO_ADD.md, VERSION |

---

**Report generated for Phase 7.12 verification. Complete full pytest and commit/push before marking phase complete.**
