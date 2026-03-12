## Derived / Tag-Modified Entity Display Audit (Emoji Profiles)

### 1. Derived goods audit

#### 1.1 Data model and derivation

- **Base goods source**: `data_catalog._load_goods` creates `Good` objects with:
  - `sku`, `name`, `category`, `base_price`
  - `tags` (list of tag_ids)
  - `possible_tag` (e.g. `"luxury"`, `"hazardous"`, `"propaganda"`, `"weaponized"`, `"stolen"`, `"cybernetic"`).

- **Market derivation** happens in `market_creation._build_candidates` and `_to_market_good`:

```40:48:src/market_creation.py
def _to_market_good(good: Good, extra_tag: str | None) -> MarketGood:
    tags = list(good.tags)
    sku = good.sku
    name = good.name
    if extra_tag:
        tags.append(extra_tag)
        sku = f"{extra_tag}_{sku}"
        name = f"{extra_tag.title()} {name}"
    return MarketGood(
        sku=sku,
        name=name,
        category=good.category,
        base_price=good.base_price,
        tags=tuple(tags),
    )
```

- For a base good like `experimental_reactors` with `possible_tag="hazardous"`, this produces:
  - `sku = "hazardous_experimental_reactors"`
  - `name = "Hazardous Experimental Reactors"`
  - `tags = [<base_tags>..., "hazardous"]`

- Similarly for:
  - `luxury_fresh_produce`
  - `weaponized_servitor_units`
  - `propaganda_media_packages`
  - `luxury_nutrient_paste`

These **derived SKUs are *not* added to `DataCatalog.goods`**; they exist only in the market layer as `MarketGood` instances and as SKU strings in `market_profile.categories`.

#### 1.2 Display path for derived goods

- **Market profile categories** (what the CLI’s `_format_market_profile_lines` reads) contain raw SKUs:

```100:148:tests/output/playtest_seed_12345_20260309_235353.md
"categories": {
  "ENERGY": { "consumed": [], "neutral": [], "produced": ["high_density_fuel"] },
  "MACHINERY": { "consumed": [], "neutral": [], "produced": ["military_hardware"] },
  "METAL": { "consumed": ["decorative_metals"], "neutral": [], "produced": [] },
  "ORE": { "consumed": ["nickel_ore"], "neutral": [], "produced": [] },
  "PARTS": { "consumed": [], "neutral": [], "produced": ["servitor_units"] }
}
```

and in other runs:

```325:325:tests/output/playtest_seed_12345_20260308_154539.md
\"ENERGY\": {\"consumed\": [\"experimental_reactors\", \"hazardous_experimental_reactors\", \"standard_fuel\"], ...}
\"FOOD\": {\"... neutral\": [\"heritage_cuisine\", \"luxury_fresh_produce\", \"nutrient_paste\"], ...}
\"DATA\": {\"produced\": [\"ai_training_sets\", \"media_packages\", \"propaganda_feeds\"]}
```

- **CLI display helper** for goods (`src/emojispace_cli_v1.py`):

```195:205:src/emojispace_cli_v1.py
def _get_good_display_name(engine: GameEngine, sku_id: str) -> str:
    \"\"\"Resolve sku_id to good display string: [category] Name [tags]. Falls back to plain name on error.\"\"\"
    if not sku_id:
        return \"Unknown Good\"
    try:
        from data_catalog import load_data_catalog
        catalog = load_data_catalog()
        good = catalog.good_by_sku(sku_id)
        return _format_good_name_with_profile(good, good.name, True)
    except (KeyError, Exception):
        return sku_id
```

- **Catalog lookup**:

```49:53:src/data_catalog.py
def good_by_sku(self, sku: str) -> Good:
    for good in self.goods:
        if good.sku == sku:
            return good
    raise KeyError(f\"Unknown SKU: {sku}\")
```

- For **base SKUs** (e.g. `fresh_produce`, `servitor_units`):
  - `good_by_sku` succeeds → we get a `Good` with category, tags, possible_tag.
  - `_format_good_name_with_profile` passes this into `emoji_profile_builder`, which builds the correct Emoji Profile.

- For **derived SKUs** (e.g. `luxury_fresh_produce`, `hazardous_experimental_reactors`, `propaganda_media_packages`):
  - `DataCatalog.good_by_sku(derived_sku)` raises `KeyError` because only the base `Good` exists.
  - `_get_good_display_name` catches the exception and returns the **raw `sku_id` string**.
  - That string is what appears anywhere `_get_good_display_name` is used on those SKUs — notably in the market profile “Produces/Consumes” display.

#### 1.3 Failure point and field status

For derived variants like `hazardous_experimental_reactors`, `luxury_fresh_produce`, `weaponized_servitor_units`, `propaganda_media_packages`:

- **Creation (A)**: `_to_market_good` creates a `MarketGood` with:
  - `sku = extra_tag + "_" + base_sku`
  - `name = extra_tag.title() + " " + base_good.name`
  - `tags = base_tags + [extra_tag]`

  → Creation is correct; the derived entity has a proper name and correct tags.

- **Display-name at source (B)**:
  - `MarketGood.name` is already human-friendly (“Luxury Fresh Produce”, etc.).

- **Category & tags (C)**:
  - `category = good.category` (same as base).
  - `tags` contain both base tags and the extra tag.

- **What the CLI sees (D)**:
  - `market_profile.categories` only contain **SKU strings**, not `MarketGood` objects.
  - `_format_market_profile_lines` iterates those raw SKUs and calls `_get_good_display_name(engine, sku)`.
  - `_get_good_display_name` uses `DataCatalog.good_by_sku`, which only knows base SKUs.

- **Helper resolution (E)**:
  - Base SKUs: resolution succeeds → Emoji Profile is built from a `Good` entity.
  - Derived SKUs: `KeyError` → helper returns `sku_id` string → raw id leak.

- **Builder input (F)**:
  - For base goods: builder receives a `Good` with `category` and `tags` and works correctly.
  - For derived goods: builder is never called; `_get_good_display_name` returns early with a raw string, so there is **no entity object** passed to `emoji_profile_builder`.

**Failure classification for derived goods:**

- **Derived entity never registered in lookup**: `DataCatalog.goods` has only base SKUs.
- **Display-name resolution fails**: `good_by_sku(derived_sku)` raises `KeyError`.
- **Builder never sees derived entity**: the path that would construct an entity with base+extra tags is missing; builder normalization is not exercised for these cases.
- **CLI helper leaks raw ids**: `_get_good_display_name` returns `sku_id` as fallback, bypassing Emoji Profiles.


### 2. Display-name audit

- At the **market layer**, derived goods have correct `name` fields via `_to_market_good`:
  - e.g. `"Hazardous Experimental Reactors"`, `"Luxury Fresh Produce"`.
- Engine `market_buy_list` responses include `display_name` for SKUs shown in buy/sell menus, so those menus display correctly.
- The **only place** where name resolution fails is where the **CLI itself** tries to resolve SKUs using `_get_good_display_name`, which assumes **every SKU exists in `DataCatalog`**.

Result: **display names for derived variants are correct at source (market), but the display helper ignores them and re-resolves via a catalog that doesn’t know about derived SKUs.**


### 3. Emoji-profile audit (builder inputs)

- **Working base goods**:
  - Input to `emoji_profile_builder` is a `Good` with:
    - `category` (e.g. `FOOD`, `ENERGY`)
    - `tags` list (e.g. `["agricultural", "essential"]`)
    - optional `possible_tag`
  - Builder normalizes this “goods entity” and produces:
    - `primary` from `category` → `goods_category_*` emoji.
    - `secondaries` from `tags` → `goods_*` tag emojis.
  - Output matches the spec: `[category] NAME [tag] [tag] ...`.

- **Failing derived goods**:
  - Because `_get_good_display_name` returns the `sku_id` string on `KeyError`, the builder is never called for these SKUs.
  - The builder thus **never receives** an entity that contains the combined base+modifier tags and the derived display name.

Conclusion: **Emoji Profile builder itself is functioning; it simply never receives the derived variants. The fault is upstream in how derived SKUs are resolved for display.**


### 4. Module impact assessment

#### 4.1 Tag-modified modules

- Module tags are assembled in `shipdock_inventory._module_tags`:

```226:242:src/shipdock_inventory.py
def _module_tags(module: dict[str, Any]) -> list[str]:
    tags: list[str] = []
    primary = module.get(\"primary_tag\")
    if isinstance(primary, str):
        tags.append(primary)
    secondary_policy = module.get(\"secondary_policy\")
    if isinstance(secondary_policy, dict):
        default_secondary = secondary_policy.get(\"default_secondary\")
        if isinstance(default_secondary, str):
            tags.append(default_secondary)
    for key in (\"secondary_tags\", \"secondaries\", \"secondary_defaults\"):
        raw = module.get(key)
        if isinstance(raw, list):
            tags.extend(str(entry) for entry in raw)
        elif isinstance(raw, str):
            tags.append(raw)
    return tags
```

- These tags are stored directly on module dicts used in shipdock inventories, combat, etc.

#### 4.2 Display path for modules

- The CLI and `run_game_engine_cli` display modules via helpers that receive the **module dict** (with `tags`) directly and format it through `_format_name_with_profile` / `_entity_display`.
- There is **no derived module SKU** analogous to `luxury_fresh_produce` — modules keep the same `module_id` and accumulate `secondary_tags`.
- Emoji Profiles for modules, when used, see the full module entity including tags.

**Assessment:**  
Modules are **not affected** by the derived-SKU failure mode. They do not create new lookup ids that can miss the catalog; their tags travel with the module objects themselves.


### 5. Hull / ship impact assessment

#### 5.1 Tag-modified hulls / ships

- Hulls have `traits` fields loaded from `hulls.json` and validated via `data_loader`.
- Ships are assembled using `ship_assembler`, which uses hull traits (`traits`) and module `secondary_tags` for behavior but does **not** create new hull ids.

Relevant reads:

```218:223:src/shipdock_inventory.py
def _hull_tags(hull: dict[str, Any]) -> list[str]:
    tags = []
    for value in hull.get(\"traits\", []):
        if isinstance(value, str):
            tags.append(value)
    return tags
```

- Traits are used in systems like `combat_resolver`, `ship_assembler`, etc., but there is no pattern of constructing new `hull_id` values from traits.

#### 5.2 Display path for hulls/ships

- Ship displays rely on:
  - `hull_id` → `get_hull_display_name(hull_id)` → Emoji Profile.
  - Ship/hull dicts that include traits/tags passed into the builder where applicable.
- The CLI **does not** construct derived hull ids like `"alien_midge_i"`; it always uses canonical `hull_id`.

**Assessment:**  
Hulls/ships are **not affected** by the derived-SKU failure mode. There is no new id that can fail a catalog lookup; traits/tags are kept on the hull/ship entity itself and can be consumed by the builder correctly.


### 6. Lookup / catalog registration audit

- `DataCatalog.goods` is built strictly from `data/goods.json` via `_load_goods`.
- Derived SKUs are introduced **only** at the market level as `MarketGood` via `_to_market_good` and are stored inside `Market` instances, not in the catalog.
- `DataCatalog.good_by_sku` only knows the base SKUs from `goods.json`. Any derived SKU string passed here will raise `KeyError`.
- `turn_loop._sku_category` and `_sku_tags` show how logic copes with derived SKUs by stripping the prefix:

```390:405:src/turn_loop.py
def _sku_tags(self, system_id: str, sku: str) -> list[str]:
    market_good = self._market_good(system_id, sku)
    if market_good is not None:
        return list(market_good.tags)
    try:
        return list(self._catalog.good_by_sku(sku).tags)
    except KeyError:
        base_sku = self._strip_possible_tag(sku)
        if base_sku is None:
            return []
        try:
            base_tags = list(self._catalog.good_by_sku(base_sku).tags)
        except KeyError:
            return []
        prefix = sku.split(\"_\", 1)[0]
        return base_tags + [prefix]
```

- Note: **logic paths** (e.g. tag checks for law/price/mission selection) already know how to reconstruct tags for derived SKUs by:
  - Using `MarketGood` when available, or
  - Stripping the `possible_tag` prefix and re-appending it to base tags.

- In contrast, the **display helper** `_get_good_display_name` does **not** use this tag-aware logic; it only calls `DataCatalog.good_by_sku` and returns the `sku_id` on failure.

**Conclusion:**  
Derived SKUs are **not** first-class catalog entries. The catalog + market subsystem is designed such that:

- Logic understands derived SKUs via `MarketGood` and `_strip_possible_tag`.
- Display currently assumes **only base SKUs exist** and treats failure as “fall back to raw id.”


### 7. Root-cause conclusion

**Core issue:**  
Derived goods with extra tags (`luxury_`, `hazardous_`, `weaponized_`, `propaganda_`, etc.) are *not* registered as full `Good` entities in the `DataCatalog`. When the CLI’s `_get_good_display_name(engine, sku_id)` tries to resolve them via `DataCatalog.good_by_sku`, it fails with `KeyError` and falls back to returning the raw `sku_id` string. As a result, the Emoji Profile builder never receives the derived entity (or a reconstructed equivalent), and player-facing screens show raw ids instead of Emoji Profiles for these variants.

**Where the real fix belongs (not implemented yet):**

- The correct fix is **not** a UI workaround in the CLI, but a change in the **display-resolution and catalog/market interface**, e.g.:
  - Make derived SKUs first-class `Good` entries in the catalog, *or*
  - Enhance the display resolution logic (the layer around `_get_good_display_name`) to:
    - Resolve SKUs via `MarketGood` or base+tag reconstruction (similar to `_sku_tags`), and
    - Pass a full entity (with category and combined tags) into `emoji_profile_builder` rather than falling back to raw `sku_id` on `KeyError`.

The Emoji Profile builder itself is behaving correctly when given a proper entity (base goods, modules, hulls). The source of the bug is **how derived SKUs are resolved for display**, not the builder or the CLI formatting layer.

