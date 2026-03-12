# Audit: modules.json primary_tag → tags Normalization

**Scope:** Audit only. No implementation changes.

**Goal:** Determine whether `primary_tag` in `data/modules.json` can be replaced or normalized into the standard `tags` field used by the Emoji Profile pipeline, without breaking existing logic.

**Primary file:** `data/modules.json` (each module has `"primary_tag": "combat:weapon_energy"` etc.)

---

## 1. Exact References to `primary_tag`

### 1.1 Data & loaders

| File | Function / location | Purpose |
|------|--------------------|--------|
| `data/modules.json` | Every module object | Source of truth; each module has one `primary_tag` string. |
| `src/data_loader.py` | `_MODULE_REQUIRED_KEYS` | `"primary_tag"` is a required key. |
| `src/data_loader.py` | `_validate_module()` | `_require_type(module, index, "primary_tag", str, "modules.json")`. |
| `src/data_loader.py` | `_validate_module()` | Calls `_validate_module_primary_tag(module["slot_type"], module["primary_tag"], index)`. |
| `src/data_loader.py` | `_validate_module_primary_tag()` | Validates `primary_tag` vs `slot_type` (weapon/defense/utility allowlists and prefixes). |

**Note:** `_MODULE_ALLOWED_KEYS = _MODULE_REQUIRED_KEYS | _MODULE_OPTIONAL_KEYS` and `_MODULE_OPTIONAL_KEYS = {"numeric_bonus"}`. Any key not in `_MODULE_ALLOWED_KEYS` (e.g. `tags`) is rejected as an unexpected key. So adding `tags` to modules.json **without** adding it to the allowed set would cause load to fail.

### 1.2 Ship assembly & hull/stats

| File | Function | Purpose |
|------|----------|--------|
| `src/ship_assembler.py` | `_validate_primary_tag_vs_slot_type()` | Validates `primary_tag` vs `slot_type` (weapon/defense/utility prefixes). |
| `src/ship_assembler.py` | `compute_hull_max_from_ship_state()` | Uses `module_def["primary_tag"] == "combat:defense_armored"` to add +1 hull per armored defense module. |
| `src/ship_assembler.py` | `assemble_ship()` | Reads `primary_tag = module_def["primary_tag"]`, validates it, and **copies it onto each resolved entry** (`"primary_tag": primary_tag`). |
| `src/ship_assembler.py` | `assemble_ship()` (loop over `resolved`) | Uses `entry["primary_tag"]` for ship utility effects: `ship:utility_extra_cargo`, `ship:utility_data_array`, `ship:utility_interdiction`, `ship:utility_smuggler_hold`, `ship:utility_mining_equipment`, `ship:utility_probe_array`, `ship:utility_extra_fuel`, and `combat:utility_engine_boost` (subsystem_modules). |

So the **assembled** module entry (output of `assemble_ship`) always has `primary_tag` on it; that value comes from the definition.

### 1.3 Combat

| File | Function | Purpose |
|------|----------|--------|
| `src/combat_resolver.py` | `_crew_modifiers_for_ship_state()` | Builds normalized modules from `module_def.get("primary_tag")` and passes to crew modifier logic. |
| `src/combat_resolver.py` | `_primary_weapon_type()` | Uses `module["primary_tag"]` from def to count energy/kinetic/disruptive. |
| `src/combat_resolver.py` | `_primary_defense_type()` | Uses `module["primary_tag"]` from def to count shielded/armored/adaptive. |
| `src/combat_resolver.py` | `_module_is_repair()` | `module_def["primary_tag"] == "combat:utility_repair_system"` to detect repair modules. |
| `src/combat_resolver.py` | `resolve_combat_round()` | Scan action: `module_defs[entry["module_id"]]["primary_tag"] == "ship:utility_probe_array"` (player and enemy). |
| `src/combat_resolver.py` | `_available_actions()` | Same probe check: `module_defs[entry["module_id"]]["primary_tag"] == "ship:utility_probe_array"`. |
| `src/combat_resolver.py` | `_resolve_escape_attempt()` | Cloak: `primary_tag == "combat:utility_cloak"` or `"ship:utility_cloak"`; interdiction: `primary_tag == "ship:utility_interdiction"`. |
| `src/combat_resolver.py` | (second combat path) | Same Scan checks via `module_defs[entry["module_id"]]["primary_tag"] == "ship:utility_probe_array"`. |

### 1.4 Game engine

| File | Function | Purpose |
|------|----------|--------|
| `src/game_engine.py` | Combat flow (Scan) | `module_defs[entry["module_id"]]["primary_tag"] == "ship:utility_probe_array"` for player and enemy. |
| `src/game_engine.py` | TR/RCP calculation | Uses `_module_is_repair(entry)` from combat_resolver (which uses def `primary_tag`). |

### 1.5 Mission / rewards / shipdock / crew / CLI

| File | Function | Purpose |
|------|----------|--------|
| `src/mission_manager.py` | Module selector filtering | `module_tags = set(module.get("tags", [])); primary_tag = module.get("primary_tag"); if primary_tag: module_tags.add(primary_tag)`. Uses both `tags` and `primary_tag` for include/exclude. |
| `src/crew_modifiers.py` | `_count_aligned_alien_elements()` | `module.get("primary_tag")` (on normalized module dict that has `primary_tag`). |
| `src/shipdock_inventory.py` | `_module_tags()` | Builds tag list from `module.get("primary_tag")` plus secondary_policy/secondary_tags. |
| `src/emojispace_cli_v1.py` | `_get_ship_modules_display_lines()` | Uses `module_def.get("tags") or []` for Emoji Profile; does **not** pass `primary_tag` as tags (known gap in module_profile_runtime_audit). |

### 1.6 Design / tests / docs

| File | Purpose |
|------|--------|
| `design/ship_and_module_schema_contract.md` | Documents `primary_tag` as authority: "primary_tag defines all behavior", repair and action unlocking tag-driven. |
| `tests/test_crew_modifiers.py` | Mock module with `"primary_tag": "combat_weapon_alien"`. |
| `tests/test_shipdock_inventory.py` | Mock module defs with `primary_tag`. |
| Various `docs/audits/*.md` | Describe current use of `primary_tag` and recommend feeding it into `tags` for Emoji Profile. |

---

## 2. Is `primary_tag` Display-Only or Used by Gameplay Logic?

**It is used extensively by gameplay logic**, not only for display or profile identity.

- **Slot / loadout validation:** `data_loader` and `ship_assembler` enforce that `primary_tag` matches `slot_type` (weapon/defense/utility and allowed values or prefixes).
- **Hull max:** `ship_assembler.compute_hull_max_from_ship_state()` uses `combat:defense_armored` to add hull.
- **Ship utility effects:** Cargo, data, interdiction, smuggler, mining, probe, fuel, and engine subsystem membership are all driven by `entry["primary_tag"]` in the assembled ship.
- **Combat:** Weapon/defense type (RPS), repair detection, Scan (probe array), escape (cloak/interdiction) all depend on `primary_tag` (from def or from assembled entry).
- **Crew modifiers:** Alien alignment uses `primary_tag` on normalized module.
- **Missions:** Module selector uses `primary_tag` (and optionally `tags`) for filtering.
- **Shipdock / inventory:** `_module_tags()` derives tags from `primary_tag` (and secondaries) for module identity.

So **primary_tag is not display-only**; it is the main behavioral key for modules across load validation, assembly, combat, missions, and inventory.

---

## 3. Do Module Definitions Already Support or Expect `tags`?

- **mission_manager:** Yes. It uses `module.get("tags", [])` and **adds** `primary_tag` into that set for filtering. So it already treats `tags` as a set and merges `primary_tag` in.
- **emojispace_cli_v1:** Yes. It uses `module_def.get("tags") or []` for display/Emoji Profile. Today modules have no `tags` in JSON, so this is always `[]`; the audits note that `primary_tag` is never passed as tags to the profile builder.
- **data_loader:** No. Only keys in `_MODULE_REQUIRED_KEYS` and `_MODULE_OPTIONAL_KEYS` are allowed. `tags` is not in either, so **adding a `tags` key to modules.json without changing the loader would cause validation to fail** (unexpected key).

So: some code paths already **expect** an optional `tags` field (mission_manager, CLI); the data loader currently **forbids** any extra key including `tags`.

---

## 4. If We Add `"tags": ["<primary_tag_value>"]` to Module Definitions

- **With no code changes:** Load would **fail** because `data_loader` rejects unexpected keys. So we must at least add `"tags"` to `_MODULE_OPTIONAL_KEYS` (and thus `_MODULE_ALLOWED_KEYS`) in `src/data_loader.py`. Optionally validate that `tags` is a list of strings.
- **With only that loader change:** All other code continues to use `primary_tag` as today. Mission_manager and CLI would then see `tags` on definitions; mission_manager already merges `primary_tag` into the tag set, so behavior is unchanged. CLI would get non-empty `tags` from the definition and could use them for profiles; keeping `primary_tag` ensures no breakage anywhere else.

So: **Adding `tags` is safe once the loader allows the optional `tags` key.** Keeping `primary_tag` alongside `tags` does not break any existing logic.

---

## 5. If We Later Remove `primary_tag`

The following would break or need explicit migration:

1. **data_loader**
   - `primary_tag` is required and type-checked; `_validate_module_primary_tag(slot_type, primary_tag)` would need to take the primary tag from somewhere else (e.g. first element of `tags` with the same validation rules).
   - Required-keys and allowed-keys would need to be updated (remove `primary_tag`, keep or require `tags` with at least one entry for the “primary” tag).

2. **ship_assembler**
   - Reads `module_def["primary_tag"]` and copies it to each resolved entry. Would need to derive primary from `tags` (e.g. `(module_def.get("tags") or [""])[0]`) and optionally still put it on the entry as a single field for consumers that expect it, or change all consumers to derive primary from `entry.get("tags", [])[0]`.
   - All branches that use `entry["primary_tag"]` (utility effects, engine boost) would need to use that derived value or a shared helper.

3. **combat_resolver**
   - All uses of `module_def["primary_tag"]` or `module["primary_tag"]` would need a single helper, e.g. `_primary_tag(module_def)` returning `module_def.get("primary_tag") or (module_def.get("tags") or [""])[0]`, then later just `(module_def.get("tags") or [""])[0]` after removal.
   - Normalized module dicts built for crew modifiers include `primary_tag`; that would need to be filled from `tags` when `primary_tag` is absent.

4. **game_engine**
   - Scan checks use `module_defs[entry["module_id"]]["primary_tag"]`; same helper as above.

5. **mission_manager**
   - Already supports `tags` and merges `primary_tag`. If definitions only have `tags`, it can use `tags` only (e.g. primary = first tag or full set); no blocker if we standardize on tags.

6. **crew_modifiers**
   - Uses `module.get("primary_tag")` on normalized modules; those would need to carry a primary tag derived from def’s `tags` when `primary_tag` is removed.

7. **shipdock_inventory**
   - `_module_tags(module)` uses `module.get("primary_tag")`; would need to use first tag from `tags` when `primary_tag` is absent.

8. **Design / tests**
   - Contract and tests that reference `primary_tag` would need to be updated to the new convention (e.g. “primary tag” = first element of `tags`).

No other modules (e.g. reward_service, mission_generator) reference `primary_tag` or module defs in a way that would block this migration.

---

## 6. Safe Migration Recommendation

**Choose: A) Safe to add `tags` now and keep `primary_tag` temporarily.**

- **Add `tags`:** Update `src/data_loader.py` so that `tags` is an optional key: add `"tags"` to `_MODULE_OPTIONAL_KEYS` (and ensure it’s in `_MODULE_ALLOWED_KEYS`). Optionally validate that `tags` is a list of strings. Then add to each module in `data/modules.json` a field `"tags": ["<current_primary_tag_value>"]`. No other code change required; all existing logic continues to use `primary_tag`.
- **Keep `primary_tag`:** Do not remove `primary_tag` until a later, dedicated change that introduces a single “primary tag” convention (e.g. `tags[0]`) and migrates all references in data_loader, ship_assembler, combat_resolver, game_engine, crew_modifiers, shipdock_inventory, mission_manager, and tests/docs.

**Not recommended yet:** B) Replace `primary_tag` entirely in one step — too many call sites and two different shapes (definition vs assembled entry); better to do it in two phases (add `tags` + keep `primary_tag`, then remove `primary_tag` with a helper and schema update).

**Not recommended:** C) Adding `tags` to modules.json without changing the loader — load would fail due to unexpected key.

---

## 7. If Not Safe: Exact Blockers

For **adding `tags` only** (keeping `primary_tag`):

- **Blocker:** `src/data_loader.py` rejects any key not in `_MODULE_ALLOWED_KEYS`. So the only blocker is: add `"tags"` to `_MODULE_OPTIONAL_KEYS` (and thus to allowed keys). After that, adding `"tags": ["<primary_tag_value>"]` to modules.json is safe.

For **removing `primary_tag`** (full normalization to `tags`):

- **Blockers:** All call sites listed in sections 1.2–1.5 that read or write `primary_tag` (data_loader, ship_assembler, combat_resolver, game_engine, mission_manager, crew_modifiers, shipdock_inventory, and tests/design). They must be updated to derive the primary tag from `tags` (e.g. `tags[0]`) via a shared helper before `primary_tag` can be removed from the schema and from modules.json.

---

## Summary Table

| Question | Answer |
|----------|--------|
| Where is `primary_tag` referenced? | data_loader, ship_assembler, combat_resolver, game_engine, mission_manager, crew_modifiers, shipdock_inventory, CLI (indirect), design, tests. |
| Display-only or gameplay? | **Gameplay:** validation, hull max, ship utility effects, combat (weapon/defense/repair/scan/escape), crew modifiers, mission filtering, shipdock tags. |
| Do modules already support `tags`? | **Partially:** mission_manager and CLI use `module.get("tags")`; data_loader does **not** allow `tags` (rejects unknown keys). |
| Add `tags` only, keep `primary_tag`? | **Safe** after adding `tags` to optional/allowed keys in data_loader; then add `"tags": ["<primary_tag>"]` in modules.json. |
| Remove `primary_tag`? | **Not safe** without migrating all references above to a `tags`-based primary (e.g. helper + schema change). |
| Recommendation | **A) Safe to add `tags` now and keep `primary_tag` temporarily.** Then, in a follow-up, introduce primary-from-tags and remove `primary_tag`. |
