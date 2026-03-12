# PHASE 7.12 – EXPLORATION AND NON-COMBAT ENCOUNTER AUDIT

**Read-only structural discovery. No code or architecture changes.**

---

## SECTION 1 – DATA LAYER AUDIT (/data)

### 1.1 Destinations and world generation

**Destination types currently defined (in code, not in a data file):**

- **planet** – `world_generator.py` line 509: `destination_type = "planet"`
- **station** – `world_generator.py` line 565: `destination_type = "station"`
- **explorable_stub** – `world_generator.py` line 621: `destination_type = "explorable_stub"`
- **mining_stub** – `world_generator.py` line 640: `destination_type = "mining_stub"`

**Types that resemble asteroid / anomaly / debris / derelict / abandoned / salvage:**

- **asteroid_field** and **contact** are referenced only as *excluded* types in `world_generator.py` (lines 919, 954): they are used in conditionals to treat certain destinations as non-populated (e.g. zero population, excluded from “populated” lists). They are **not** currently generated; only `planet`, `station`, `explorable_stub`, and `mining_stub` are created.
- **explorable_stub** and **mining_stub** are the only non-inhabited destination types actually generated. They are created with `population=0`, no market, no locations, and default `tags=[]` (no tags set at creation).

**Contract governing destination generation:**

- Destination generation is fully defined in **`src/world_generator.py`**. There is no separate data contract file (e.g. no `data/destinations.json`). Logic lives in:
  - `WorldGenerator.generate()` (lines 92–155), which calls `_generate_destinations()` (lines 469–675).
  - Counts: `planet_count` (2–4), `station_count` (1–2), `explorable_count` (0–2), `mining_count` (0–2) per system (lines 491–492).

**Destination types marked as stubs:**

- **explorable_stub** and **mining_stub** are explicitly named and treated as stubs: zero population, no markets, no locations. They are excluded from “populated” destination logic (e.g. `world_generator.py` lines 919, 954).

---

### 1.2 modules.json

**All modules (by primary_tag / slot_type):**

- **Weapons:** `weapon_energy_mk1`, `weapon_energy_mk2`, `weapon_kinetic_mk1`, `weapon_kinetic_mk2`, `weapon_disruptive_mk1`, `weapon_disruptive_mk2`
- **Defense:** `defense_shielded_mk1`, `defense_shielded_mk2`, `defense_armored_mk1`, `defense_armored_mk2`, `defense_adaptive_mk1`, `defense_adaptive_mk2`
- **Combat utility:** `combat_utility_engine_boost_mk1/mk2`, `combat_utility_targeting_mk1/mk2`, `combat_utility_repair_system_mk1/mk2`, `combat_utility_signal_scrambler_mk1/mk2`, `combat_utility_overcharger_mk1/mk2`
- **Ship utility:** `ship_utility_extra_cargo`, `ship_utility_data_array`, `ship_utility_smuggler_hold`, `ship_utility_mining_equipment`, `ship_utility_probe_array`, `ship_utility_interdiction`, `ship_utility_extra_fuel_mk1`

**Modules with tags related to mining / scanner / survey / salvage / anomaly:**

- **Mining:** `ship_utility_mining_equipment` – `primary_tag`: `"ship:utility_mining_equipment"` (data/modules.json lines 533–562). Description: “Mining effects are applied by ship systems later.”
- **Survey/exploration:** `ship_utility_probe_array` – `primary_tag`: `"ship:utility_probe_array"` (lines 563–592). Description: “Exploration effects are applied by encounter/world systems later.”
- **Salvage:** No module with a tag literally named “salvage”. Modules have `salvage_policy` (e.g. `salvageable`, `mutation_allowed`) for being *salvageable from* combat, not for performing salvage. No module tag “scanner” or “anomaly”.

**All module tags present (primary_tag only):**

- Combat: `combat:weapon_energy`, `combat:weapon_kinetic`, `combat:weapon_disruptive`, `combat:defense_shielded`, `combat:defense_armored`, `combat:defense_adaptive`, `combat:utility_engine_boost`, `combat:utility_targeting`, `combat:utility_repair_system`, `combat:utility_signal_scrambler`, `combat:utility_overcharger`
- Ship utility: `ship:utility_extra_cargo`, `ship:utility_data_array`, `ship:utility_smuggler_hold`, `ship:utility_mining_equipment`, `ship:utility_probe_array`, `ship:utility_interdiction`, `ship:utility_extra_fuel`

**Modules that modify yield, extraction, or scanning:**

- **None.** No module has numeric or effect fields for yield, extraction, or scanning. `ship_utility_mining_equipment` and `ship_utility_probe_array` only set flags in code (`unlock_mining`, `unlock_probe` in `ship_assembler.py` lines 305–307); no yield/extraction/scan values in data.

---

### 1.3 hulls.json

**Hull fields that may influence cargo, data, utility, mining/exploration:**

- **cargo:** `physical_base`, `data_base` – every hull has `cargo: { "physical_base": N, "data_base": M }` (e.g. lines 19–22 for `civ_t1_midge`). Used for capacity.
- **bias:** `weapon`, `defense`, `engine`, `hull` – combat/mobility, not cargo or exploration-specific.
- **traits:** e.g. `ship:trait_civilian`, `ship:trait_freighter`, `ship:trait_military`, `ship:trait_experimental`, `ship:trait_alien` – no mining or exploration trait.
- **fuel_capacity_base** – range/travel.
- **crew_capacity** – no field named “utility bonus” or “mining/exploration potential”. Mining/exploration potential is only implied by slot capacity for utility modules (e.g. equipping mining or probe modules).

---

### 1.4 reward_profiles.json

**Reward profiles that resemble exploration / salvage / derelict / anomaly / civilian_manifest:**

- **civilian_manifest** (lines 5–12) – cargo, medium band, “Cargo taken from civilian ships.”
- **alien_salvage** (lines 34–40) – cargo, medium, “Salvage from alien vessels.”
- **derelict_salvage** (lines 42–49) – cargo, low, “Salvage recovered from derelicts.”
- **cargo_cache** (lines 51–58) – cargo, medium, “Recovered lost cargo.”

**Reward profiles used outside combat:**

- **Yes.** In `game_engine.py` (lines 3789–3811), after encounter resolution, if the resolver is **not** combat and the encounter qualifies for rewards, `materialize_reward()` is called and `apply_materialized_reward()` is applied immediately. This path is used for **reaction** (e.g. accept), **pursuit** (e.g. escape_success), and **law** resolvers. Combat rewards are handled separately in `_apply_post_combat_rewards_and_salvage` (deferred loot prompt). So reward_profiles are consumed both in combat (post-combat) and in non-combat (reaction/pursuit/law) paths.

---

### 1.5 encounter_types.json

**All encounter types (subtype_id):**

1. **civilian_trader_ship** – posture `neutral`, initiative `player`, flags `civilian_target`, `trade_possible`, reward_profile `civilian_manifest`
2. **customs_patrol** – posture `authority`, initiative `npc`, no reward_profiles
3. **bounty_hunter** – posture `authority`, initiative `npc`, reward_profile `bounty_credit`
4. **pirate_raider** – posture `hostile`, initiative `npc`, reward_profile `pirate_loot`, flags include `salvage_possible`
5. **blood_raider** – posture `hostile`, initiative `npc`, reward_profile `raider_loot`, `salvage_possible`
6. **derelict_ship** – posture `opportunity`, initiative `npc`, reward_profile `derelict_salvage`, flags `salvage_possible`, `anomaly_discovery_possible`

**Explicitly non-combat encounter types:**

- **civilian_trader_ship** – neutral, trade_possible; can be resolved without combat (reaction/accept).
- **derelict_ship** – opportunity; allowed action `ACTION_INVESTIGATE` leads to `HANDLER_EXPLORATION_STUB` (interaction_layer.py lines 121–122, 205–207). No combat required for “investigate” path.
- **customs_patrol** – authority; can lead to law_stub, not necessarily combat.

**Classification:**

- By **posture:** `neutral`, `authority`, `hostile`, `opportunity` (encounter_generator.py line 7: `ALLOWED_POSTURES`).
- By **default_flags:** e.g. `civilian_target`, `trade_possible`, `salvage_possible`, `anomaly_discovery_possible`, `authority_actor`, `criminal_actor`, `piracy_context`, `mission_possible` (encounter_generator.py lines 9–17).

---

### 1.6 tags.json

**Tags related to asteroid / mining / salvage / anomaly / destroyed / salvage_site:**

- **destroyed** (lines 266–270): `category`: `"structural"`, `applies_to`: `["destination"]`, description “Destination is destroyed and unavailable for normal interaction.”
- **salvage_site** (lines 272–276): `category`: `"structural"`, `applies_to`: `["destination"]`, description “Location contains salvageable debris or remains.”

**Not present in tags.json:** `asteroid`, `mining`, `anomaly` (as tag_id). No tag_id literally “asteroid” or “mining” or “anomaly”.

---

## SECTION 2 – SOURCE CODE AUDIT (/src)

### 2.1 World generation

- **File responsible for destination creation:** `src/world_generator.py`.
- **Destination creation:** `WorldGenerator.generate()` (lines 92–155) calls `_generate_destinations()` (lines 469–675) per system. That function creates:
  - Planets (2–4 per system), stations (1–2), explorable stubs (0–2), mining stubs (0–2).
- **Non-inhabited types generated at worldgen:** Yes. `explorable_stub` and `mining_stub` are created with population 0, no market, no locations, default empty tags (lines 616–652).
- **World generation references to asteroid/anomaly types:** Only in conditionals. `asteroid_field` and `contact` appear in `_destination_population()` and `_ensure_max_population_destination()` (lines 919, 954) to *exclude* such types from population logic; they are **not** generated. No code path creates destinations with type `asteroid` or `anomaly`.

---

### 2.2 Destination entity schema

- **Class/structure representing a destination:** `world_generator.py` lines 25–36: `Destination` dataclass (frozen).
  - Fields: `destination_id`, `system_id`, `destination_type`, `display_name`, `population`, `primary_economy_id`, `secondary_economy_ids`, `locations`, `market`, `tags` (default `list`).
- **visit_count:** Not present. The Destination type has no `visit_count` field.
- **Custom state fields / arbitrary metadata:** No. Destination is a frozen dataclass with a fixed set of fields; no `state` or `metadata` dict.
- **State persisted per destination:** No. Destination instances are immutable. Visit tracking is on **player**: `player_state.visited_destination_ids` (set of destination_id strings) in `player_state.py` (line 35). No per-destination state (e.g. visit count, discovered, depleted) is stored on the destination entity.

---

### 2.3 Travel resolution

- **File:** `src/travel_resolution.py`. `resolve_travel()` (lines 45–120+) handles fuel cost, wages, travel days, risk/encounter rate modifiers, and optional world_state_engine modifiers. It does **not** define “destination actions” or “exploration” hooks.
- **Player interaction with destination:** In `game_engine.py`: travel is `travel_to_destination` (payload: `target_system_id`, `target_destination_id`). On arrival, `current_destination_id` and `visited_destination_ids` are updated (lines 755–762). Available actions at a destination come from `destination_actions()` in `interaction_resolvers.py` (lines 53–71): refuel (if datanet), buy/sell hull/module, repair_ship (if shipdock). **Destroyed** tag: if destination has tag `destroyed`, `destination_actions()` still returns the same list (only order sorted); no special “exploration” or “salvage” action (interaction_resolvers.py lines 55–57).
- **Non-travel destination actions:** Yes: refuel, buy_hull, sell_hull, buy_module, sell_module, repair_ship, warehouse deposit/withdraw (location-level). No “explore”, “survey”, “mine”, or “salvage” destination action.
- **Exploration hooks:** None in travel_resolution. No hook in travel resolution for “on arrive at explorable_stub” or “on mine”. Exploration appears only as encounter-side: `ACTION_INVESTIGATE` and `HANDLER_EXPLORATION_STUB` in interaction_layer.py; no destination-based exploration flow.

---

### 2.4 Interaction layer

- **File:** `src/interaction_layer.py`. Encounter dispatch: `dispatch_player_action()` (lines 156–233). Branching: by `player_action` and then by `npc_outcome` via `_npc_outcome_to_handler()` (lines 136–153).
- **Resolver types currently supported (next_handler):**
  - **HANDLER_END** – end encounter
  - **HANDLER_REACTION** – further NPC reaction
  - **HANDLER_COMBAT** – combat
  - **HANDLER_COMBAT_STUB** – one-shot combat (simulation)
  - **HANDLER_LAW_STUB** – law/customs
  - **HANDLER_PURSUIT_STUB** – pursuit
  - **HANDLER_EXPLORATION_STUB** – exploration (lines 82, 205–207): when player chooses `ACTION_INVESTIGATE` (e.g. on derelict_ship), next_handler is `HANDLER_EXPLORATION_STUB`.
- **Non-combat resolver path:** Yes. Reaction (e.g. accept), law_stub, pursuit_stub, and exploration_stub are non-combat. In `game_engine.py`, when handler is not combat, `resolver_outcome` is set for **reaction**, **pursuit**, and **law** (lines 3702–3755). There is **no** branch for `HANDLER_EXPLORATION_STUB`; for that handler, `resolver_outcome` remains `{"resolver": "none", "outcome": None}` (line 3700), so no exploration-specific resolution or reward gate runs.

---

### 2.5 Encounter generator

- **File:** `src/encounter_generator.py`. Encounter type selection: loaded from `data/encounter_types.json`; selection is weighted by `base_weight`, filtered by `allowed_TR_range` and other factors (e.g. government_bias, situation_bias). `generate_encounter()` (and related helpers) build an `EncounterSpec` with one `reward_profile_id` selected from the subtype’s `reward_profiles` list (e.g. `select_reward_profile()` around lines 494–520, 552–575).
- **Non-combat types present:** Yes. `civilian_trader_ship`, `customs_patrol`, `derelict_ship` are non-hostile; `derelict_ship` has posture `opportunity` and flags `salvage_possible`, `anomaly_discovery_possible`.

---

### 2.6 Combat resolver

- **File:** `src/combat_resolver.py`. Resolves combat rounds; on enemy destroyed/surrender, returns combat result including `salvage_modules` (from `salvage_resolver.resolve_salvage_modules()`).
- **Reward materialization:** Reward (from encounter `reward_profile_id`) is **not** applied inside combat_resolver. It is applied in `game_engine.py`: post-combat in `_apply_post_combat_rewards_and_salvage()` (materialize_reward + loot bundle), and for non-combat in the block at 3789–3811 (materialize_reward + apply_materialized_reward).
- **Exploration-style rewards:** The same `reward_materializer.materialize_reward()` and reward_profiles (e.g. derelict_salvage, cargo_cache) can in principle be used for non-combat; they are already used for reaction/pursuit. Exploration_stub does not currently trigger that path because no resolver branch sets a qualifying `resolver_outcome` for it.

---

### 2.7 Reward materialization system

- **Where reward_profiles are consumed:**
  - **reward_materializer.py:** `load_reward_profiles()` (from `data/reward_profiles.json`), `materialize_reward(spec, system_market_payloads, world_seed)` (uses `spec.reward_profile_id`).
  - **game_engine.py:** (1) After non-combat resolution (lines 3789–3811): `materialize_reward()` then `apply_materialized_reward()` when resolver is not combat and reward qualifies. (2) Post-combat (lines 4867–4875): `materialize_reward()` then loot bundle stored for deferred application.
  - **mission_manager.py / reward_service.py:** Mission rewards use reward_profile_id and mission-specific reward_profiles (e.g. mission_credits_500, mission_goods_*) for delivery/retrieval missions, not encounter loot.
- **Non-combat invocation:** Yes. Non-combat path in game_engine (3789–3811) is used when `resolver` is reaction, pursuit, or law and `_reward_qualifies()` returns True. Exploration_stub does not set a resolver, so it does not currently invoke reward materialization.

---

### 2.8 Mining or exploration stubs

**Search keywords: mining, explore, survey, salvage**

- **mining:** `world_generator.py`: `mining_stub` destination type, `mining_count`, “Mining Site” (lines 635–652). `ship_assembler.py`: `ship:utility_mining_equipment` sets `unlock_mining`: True (lines 305–306). `modules.json`: `ship_utility_mining_equipment` (data). No mining *gameplay* (no extraction, yield, or mining action at a destination).
- **explore:** `interaction_layer.py`: `HANDLER_EXPLORATION_STUB` (line 82). `playtest_runner.py`: string “explore” in bias descriptions (e.g. “explore local destination”) – AI bias text only. No dedicated “explore” action or system beyond the stub handler.
- **survey:** Not present in codebase.
- **salvage:** `salvage_resolver.py`: `resolve_salvage_modules()` – selects modules from defeated NPC for salvage. `combat_resolver.py`: uses it post-combat. `game_engine.py`: applies salvage modules from loot bundle. Encounter flag `salvage_possible` and reward profiles (e.g. derelict_salvage). No destination-based “salvage site” action or salvage-at-location flow.

**Stubs/placeholders:**

- **HANDLER_EXPLORATION_STUB** – handler returned for ACTION_INVESTIGATE; no resolver implementation in game_engine (no branch, no reward for exploration_stub).
- **explorable_stub / mining_stub** – destination types with no locations or actions beyond travel; no “explore” or “mine” action at those destinations.
- **ship_utility_mining_equipment / ship_utility_probe_array** – module descriptions say effects “are applied by ship systems later” / “by encounter/world systems later” – i.e. data-side placeholders for future systems.

---

### 2.9 Crew modifiers

- **File:** `src/crew_modifiers.py`. `CrewModifiers` (lines 8–38) and `compute_crew_modifiers()` (lines 41–70). Role effects (lines 99–118): pilot (engine), gunner (attack), tactician (defense), engineer/mechanic (repair), navigator (fuel_delta), broker (buy/sell multiplier), quartermaster (cargo_delta), science (data_cargo_delta). Tag effects (lines 121–158): e.g. steady_aim, evasive, fuel_efficient, organized (cargo_delta), data_savvy (data_cargo_delta), etc.
- **Mining / exploration / yield bonuses:** None. No crew role or tag applies a mining bonus, exploration bonus, or yield bonus. Cargo and data capacity deltas exist (quartermaster, organized, science, data_savvy); no “mining yield” or “scan strength” modifier.

---

## SECTION 3 – STRUCTURAL CONSTRAINT ANALYSIS

### 3.1 World state constraints

- **destroyed and salvage_site tags:** Defined in `data/tags.json` with `applies_to: ["destination"]`. In code, **destroyed** is read in `interaction_resolvers.py` (lines 55–57): `destination_has_tag(destination, "destroyed")` – if true, destination_actions still returns the same list (sorted). So destroyed destinations remain travel-reachable but get no extra behavior; no code adds or removes the destroyed tag. **salvage_site** is not referenced in src; it exists only in tags.json. No handler applies or reads `salvage_site` for destinations.
- **Adding new destination types post-worldgen:** World is built once in `WorldGenerator.generate()`; destinations are created inside `_generate_destinations()`. No code path was found that appends new destination types or new destinations to the galaxy after initial generation. Adding a new type would require either changing world_generator logic or introducing a separate system that mutates or extends the world (none found).

---

### 3.2 Persistence boundaries

- **Structural mutation:** Galaxy/System/Destination are produced by world_generator and are typically treated as read-only structural data. Destination is a frozen dataclass; no in-place mutation of Destination fields. “Structural” in tag_policy_engine is used for goods/tag risk (e.g. luxury, weaponized), not for world structure.
- **Destination state mutation without Event:** Per-destination state (e.g. visit count, depleted, discovered) is not stored on the destination entity. The only “destination-related” mutable state is on player_state: `visited_destination_ids`, `current_destination_id`, `warehouses` (keyed by destination_id). Changing a destination’s tags or type would require replacing the Destination in the system’s list (new immutable instance); no code path was found that does that in response to an Event or otherwise.

---

### 3.3 Encounter persistence

- **Encounters creating persistent NPC entities:** Encounters are generated per travel/resolution (e.g. `generate_encounter()`); the result is an `EncounterSpec` and resolution produces combat result, pursuit result, or reaction outcome. NPCs are generated for the encounter (e.g. NPC ship for combat) but are not registered as persistent world entities. Persistent NPCs exist as crew (e.g. on player ship) or in other registries (e.g. `npc_registry`, persistence_tier). Encounter resolution does **not** create new persistent NPC entities in the world; it does not add NPCs to a global world state that persists after the encounter ends.

---

## SECTION 4 – SUMMARY TABLE

| System Area | Exists (Yes/No/Partial) | Relevant Files | Notes |
|-------------|-------------------------|----------------|-------|
| Persistent asteroid destinations | No | `world_generator.py`, `tags.json` | `asteroid_field` only referenced as excluded type; not generated. No destination type “asteroid” created. |
| Persistent anomaly destinations | No | `world_generator.py`, `data/` | No “anomaly” destination type. Encounter flag `anomaly_discovery_possible` exists; no anomaly destination entity. |
| Mining module support | Partial | `data/modules.json`, `ship_assembler.py` | Module `ship_utility_mining_equipment` exists; sets `unlock_mining` only. No yield/extraction logic or mining action. |
| Exploration action system | Partial | `interaction_layer.py`, `game_engine.py` | ACTION_INVESTIGATE → HANDLER_EXPLORATION_STUB; no resolver branch or reward for exploration_stub. No “explore” at destination. |
| Non-combat encounter resolver | Yes | `interaction_layer.py`, `game_engine.py` | Reaction, pursuit, law_stub have resolver branches and (where applicable) reward application. Derelict/trader are non-combat types. |
| Trader encounter type | Yes | `data/encounter_types.json` | `civilian_trader_ship` (neutral, trade_possible, civilian_manifest reward). |
| Destination visit tracking | Partial | `player_state.py`, `game_engine.py` | `visited_destination_ids` (set) on player; no per-destination visit_count or state on Destination. |
| Reward invocation outside combat | Yes | `game_engine.py`, `reward_materializer.py` | materialize_reward + apply_materialized_reward for reaction/pursuit/law when qualifies. Not for HANDLER_EXPLORATION_STUB. |

---

*End of audit. No code or contracts were modified.*
