## Module Emoji Profile Runtime Audit

**Date:** 2026-03-11  
**Scope:** Audit only – no code or data changes in this pass  
**Files inspected:**
- `src/emojispace_cli_v1.py`
- `src/emoji_profile_builder.py`
- `data/modules.json`
- `data/tags.json`
- `data/emoji.json`
- `tests/output/playtest_seed_12345_20260308_115429.md` (for observed runtime state)

---

### 1. Problem Statement

Installed modules are currently displayed with *clean text names only* (e.g.:

- `Energy Weapon Mk I`
- `Shield Defense Mk I`
- `Combat Utility Repair Mk I`

), but **no Emoji Profiles** are rendered, despite:

- `modules.json` defining combat and ship-utility modules with `primary_tag` values such as:
  - `combat:weapon_energy`
  - `combat:defense_shielded`
  - `combat:utility_repair_system`
  - `ship:utility_mining_equipment`
- `tags.json` mapping these tags to emoji ids (e.g. `combat:weapon_energy` → `combat_weapon_energy`)
- `emoji.json` providing glyphs for those emoji ids (e.g. `combat_weapon_energy` → `⚡`).

Goal of audit: determine **why module Emoji Profiles are not rendered** at runtime in the two proof screens:

1. **Player / Ship Info**
2. **Ships And Modules**

---

### 2. Functions Involved in Module Display

**Primary CLI file:** `emojispace_cli_v1.py`

Core helpers for Emoji Profiles:

- `__normalize_entity_for_display(entity)`
- `format_entity_name(entity, name)`
- `_entity_display(entity, name, visible)`
- `_format_name_with_profile(entity, name, visible)`  
  → these ultimately call `build_emoji_profile_parts` in `emoji_profile_builder.py`.

Ship/module helpers:

- `_get_ship_headline(engine, ship_info)`
- `_build_module_catalog()`
- `_get_ship_modules_display_lines(engine, ship_info)`

Proof screens:

- `_show_player_info(engine)`
  - Ship headline:
    - `ship_headline = _get_ship_headline(engine, ship_info)`
  - Installed modules:
    - `module_lines = _get_ship_modules_display_lines(engine, ship_info)`
- `_show_ships_and_modules(engine)`
  - ACTIVE SHIP headline:
    - `ship_display = _get_ship_headline(engine, active_ship)`
  - Installed modules:
    - `module_lines = _get_ship_modules_display_lines(engine, active_ship)`

Both proof screens **do** use the shared helpers for ship and module display.

---

### 3. Runtime Display Path for Installed Modules

#### 3.1. From Screens to Helper

**Player / Ship Info**:

- `ship_info` comes from `get_player_profile` (`detail["ship"]`).
- Installed modules section:

```python
module_lines = _get_ship_modules_display_lines(engine, ship_info)
if module_lines:
    print("  Installed modules:")
    for line in module_lines:
        print(f"    {line}")
else:
    print("  Installed modules: None")
```

**Ships And Modules**:

- `active_ship = engine.get_active_ship()`
- Installed modules section:

```python
module_lines = _get_ship_modules_display_lines(engine, active_ship)
if module_lines:
    print("  Installed Modules:")
    for line in module_lines:
        print(f"    {line}")
else:
    print("  Installed Modules: None")
```

In both cases, `ship_info` / `active_ship` is a dict that includes:

- `ship_id`
- `hull_id`
- `installed_modules`: e.g.
  - `"weapon_energy_mk1"`
  - `"weapon_energy_mk2"`
  - `"defense_shielded_mk1"`
  - `"ship_utility_mining_equipment"`
  - etc.

(These module ids are visible in `tests/output/playtest_seed_12345_20260308_115429.md`.)

#### 3.2. `_get_ship_modules_display_lines`

Key logic (simplified):

```python
def _build_module_catalog() -> Dict[str, Dict[str, Any]]:
    catalog = {}
    from data_loader import load_modules
    modules_data = load_modules()
    for m in modules_data.get("modules", []):
        if isinstance(m, dict):
            mid = m.get("module_id")
            if mid:
                catalog[str(mid)] = m
    return catalog


def _get_ship_modules_display_lines(engine, ship_info) -> List[str]:
    lines: List[str] = []
    module_catalog = _build_module_catalog()
    ship_id = ship_info.get("ship_id") if isinstance(ship_info, dict) else None

    # Primary: rich module records from engine.
    modules = []
    if ship_id:
        try:
            modules = engine.get_ship_modules(ship_id) or []
        except Exception:
            modules = []
    if modules:
        for module in modules:
            module_id = module.get("module_id")
            module_def = module_catalog.get(str(module_id)) if module_id else None
            name = module.get("display_name") or (module_def and module_def.get("name")) \
                   or module.get("name") or module_id or "Unknown Module"
            if module_def:
                entity = SimpleNamespace(
                    emoji_id=module_def.get("emoji_id"),
                    tier=module_def.get("tier"),
                    tags=module_def.get("tags") or [],
                )
            else:
                entity = module
            lines.append(_format_name_with_profile(entity, str(name), True))
        return lines

    # Fallback: installed_modules IDs → module_catalog
    installed_ids = []
    if isinstance(ship_info, dict):
        raw_installed = ship_info.get("installed_modules") or []
        if isinstance(raw_installed, list):
            installed_ids = list(raw_installed)
    if not installed_ids:
        return lines

    for raw_id in installed_ids:
        module_id = str(raw_id)
        module_def = module_catalog.get(module_id)
        if module_def:
            name = module_def.get("name") or module_id
            entity = SimpleNamespace(
                emoji_id=module_def.get("emoji_id"),
                tier=module_def.get("tier"),
                tags=module_def.get("tags") or [],
            )
            lines.append(_format_name_with_profile(entity, name, True))
        else:
            lines.append(module_id)
    return lines
```

Observations:

- When a `module_def` from `modules.json` is available, the helper constructs:

  ```python
  entity = SimpleNamespace(
      emoji_id=module_def.get("emoji_id"),
      tier=module_def.get("tier"),
      tags=module_def.get("tags") or [],
  )
  ```

- It then calls `_format_name_with_profile(entity, name, True)`, which runs:

  ```python
  obj = _normalize_entity_for_display(entity)
  primary, tier, secondary = build_emoji_profile_parts(obj)
  ```

So module Emoji Profiles depend entirely on what `emoji_id`, `tier`, and `tags` exist on `module_def` or `module`.

---

### 4. Module Definitions vs. Formatter Input

#### 4.1. Example module definitions (`data/modules.json`)

Examples (abridged):

```json
{
  "module_id": "weapon_energy_mk1",
  "name": "Energy Weapon Mk I",
  "slot_type": "weapon",
  "primary_tag": "combat:weapon_energy",
  ...
}
```

```json
{
  "module_id": "weapon_energy_mk2",
  "name": "Energy Weapon Mk II",
  "slot_type": "weapon",
  "primary_tag": "combat:weapon_energy",
  ...
}
```

```json
{
  "module_id": "defense_shielded_mk1",
  "name": "Shield Defense Mk I",
  "slot_type": "defense",
  "primary_tag": "combat:defense_shielded",
  ...
}
```

```json
{
  "module_id": "combat_utility_repair_system_mk1",
  "name": "Combat Utility Repair Mk I",
  "slot_type": "utility",
  "primary_tag": "combat:utility_repair_system",
  ...
}
```

```json
{
  "module_id": "ship_utility_mining_equipment",
  "name": "Ship Utility Mining Equipment",
  "slot_type": "utility",
  "primary_tag": "ship:utility_mining_equipment",
  ...
}
```

Common pattern:

- **Present:** `module_id`, `name`, `display_names`, `slot_type`, `primary_tag`, numeric bonuses, rarity/etc.
- **Absent:** `emoji_id`, `tier`, `tags` (there is no `tags` array for modules in `modules.json`).

#### 4.2. Tag and emoji mappings

From `data/tags.json`:

- `combat:weapon_energy` → `emoji_id: "combat_weapon_energy"`
- `combat:defense_shielded` → `emoji_id: "combat_defense_shielded"`
- `combat:utility_repair_system` → `emoji_id: "combat_utility_repair_system"`
- `ship:utility_mining_equipment` → `emoji_id: "ship_utility_mining_equipment"`

From `data/emoji.json`:

- `combat_weapon_energy` → `⚡`
- `combat_defense_shielded` → `🛡`
- `combat_utility_repair_system` → `🔧`
- `ship_utility_mining_equipment` → `⛏`

So **data-side emoji coverage is complete** for the tested modules.

#### 4.3. Actual formatter input entity vs. definition

When `_get_ship_modules_display_lines` resolves a `module_def` from `modules.json`, it builds:

```python
entity = SimpleNamespace(
    emoji_id=module_def.get("emoji_id"),  # → None
    tier=module_def.get("tier"),          # → None
    tags=module_def.get("tags") or [],    # → []
)
```

Because `modules.json` has:

- no `emoji_id` key
- no `tier` key
- no `tags` key

the resulting entity is always:

```python
SimpleNamespace(emoji_id=None, tier=None, tags=[])
```

This entity is then passed into `build_emoji_profile_parts`, which has **no emoji-bearing data to work with**.

---

### 5. Builder Capabilities vs. Actual Inputs

In `emoji_profile_builder.py`:

- Modules are treated as generic entities by `_normalize_entity`:

```python
def _normalize_entity(entity):
    ...
    category = _safe_get(entity, "category")
    if category is not None:
        return _normalize_goods(entity)
    return _normalize_ship_or_generic(entity)
```

- For ships/generic:

```python
def _normalize_ship_or_generic(entity):
    primary = _safe_get(entity, "emoji_id")
    ...
    t = _safe_get(entity, "tier")
    ...
    secondaries = []
    for tag in _safe_list(entity, "tags"):
        if tag is not None and str(tag).strip():
            secondaries.append(str(tag).strip())
    return (primary, tier, secondaries)
```

- `_resolve_secondary`:

```python
for sid in secondary_ids:
    sid = str(sid).strip()
    eid = tag_map.get(sid) or sid
    if eid and eid in registry:
        out.append(registry[eid])
```

This means:

- If we provide an entity with `tags` like `["combat:weapon_energy"]`, the builder will:
  - Look up `combat:weapon_energy` in `tags.json` → `combat_weapon_energy`.
  - Map `combat_weapon_energy` through `emoji.json` → `⚡`.
  - Emit `⚡` as a secondary emoji in the profile.

Conclusion: **the builder fully supports module Emoji Profiles via module tags**.  
The missing link is that the CLI never exposes `primary_tag` as `tags` to the builder.

---

### 6. Direct Answers to Audit Questions

**1. What object is passed into the formatter for modules?**

- Both proof screens call `_get_ship_modules_display_lines`, which constructs `entity` as:
  - For resolved definitions: `SimpleNamespace(emoji_id=None, tier=None, tags=[])`
  - For engine-returned module dicts (if any): the raw `module` dict, which also does not expose `primary_tag` under `tags` or `emoji_id`.

**2. Does that object contain `emoji_id`, `tags`, `tier` the builder needs?**

- **No.**
  - `emoji_id` is always `None`.
  - `tier` is always `None` for modules.
  - `tags` is always `[]` for modules, because `modules.json` has no `tags` field and `_get_ship_modules_display_lines` does not derive tags from `primary_tag`.

**3. Is the runtime helper just resolving a clean name and printing it?**

- It *does* pass the entity through `_format_name_with_profile`, which calls the builder.
- However, since the entity has no emoji-bearing data, `build_emoji_profile_parts` returns `(None, None, [])`, so `format_entity_name` ends up outputting only the **plain name**.

**4. Are module definition fields mapped correctly into builder-usable fields?**

- The key semantic field in `modules.json` is `primary_tag` (e.g. `combat:weapon_energy`).
- This field is **never mapped into `tags` or `emoji_id`** on the entity passed to the builder.
- Therefore, the emoji-relevant metadata from `modules.json` is effectively dropped before formatting.

**5. Is `_format_name_with_profile(...)` called on an emoji-bearing entity?**

- No. For modules, `_format_name_with_profile` is called on:

```python
SimpleNamespace(emoji_id=None, tier=None, tags=[])
```

or a raw module dict with the same effective emoji content (`primary_tag` present, but **not** under `tags`).

The builder is not failing; it is simply never given module tags.

---

### 7. Is the Builder the Blocker?

- **No.**
  - The builder’s generic path via `tags` → `tags.json` → `emoji.json` is entirely capable of rendering module Emoji Profiles.
  - Data coverage for tested modules and tags is complete and consistent.

The failure occurs **before** the builder: the CLI helpers do not normalize modules into a module-shaped entity the builder understands (i.e., they never include `primary_tag` in `tags`).

---

### 8. Root Cause and Fix Location

**Classification:**

- **Not** a module definition data gap:
  - `modules.json` includes `primary_tag` for all relevant modules.
  - `tags.json` and `emoji.json` cover those tags with valid emoji glyphs.
- **Not** a builder limitation:
  - `emoji_profile_builder` already supports generic entities with `tags` driving secondary emojis.

**True fault:**

- **Module-to-builder normalization gap / formatter using the wrong entity shape.**
  - `_get_ship_modules_display_lines` constructs entities with `emoji_id`, `tier`, and `tags`, but all are `None`/empty because it reads from non-existent fields (`emoji_id`, `tier`, `tags`) on the module definitions.
  - It completely ignores `primary_tag`, which is the authoritative module classification key that should drive module Emoji Profiles.

**Correct fix location:**

- The **CLI normalization layer** in `src/emojispace_cli_v1.py`, specifically:
  - `_get_ship_modules_display_lines` (and optionally `_normalize_entity_for_display` if a generic module adapter is desired).
- Required adjustment (conceptual):
  - For resolved modules, build module entities like:

    ```python
    SimpleNamespace(
        emoji_id=None,
        tier=None,  # or a numeric tier if later introduced
        tags=[module_def["primary_tag"], ...],
    )
    ```

  - so the builder can resolve module Emoji Profiles via `tags.json` and `emoji.json`.

No changes are required to:

- `modules.json`
- `tags.json`
- `emoji.json`
- `emoji_profile_builder.py`

for this specific runtime issue.

---

### 9. Summary

- The proof screens correctly route module display through `_get_ship_modules_display_lines` and `_format_name_with_profile`.
- `modules.json`, `tags.json`, and `emoji.json` together provide sufficient semantic tags and emoji glyphs for module Emoji Profiles.
- The **missing link** is that the CLI never passes `primary_tag` (or any tag) as `tags` to the Emoji Profile builder.
- As a result, the builder receives entities with no emoji-bearing data and produces name-only output.

**Action item for implementation pass (future work):**

- Update the CLI helper(s) to normalize modules into entities that expose `primary_tag` (and future secondary tags) through the `tags` field before calling `build_emoji_profile_parts`.

