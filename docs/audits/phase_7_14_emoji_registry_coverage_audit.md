# Phase 7.14 – Emoji Registry Coverage Audit

**Date:** 2026-03-08  
**Type:** Read-only audit. No files modified.  
**Purpose:** Analyze emoji coverage and produce a gap report for Phase 7.14 emoji registry expansion planning.

---

## 1. Executive Summary

The repository has **244 emoji entries** in `data/emoji.json` and **58 tag → emoji_id mappings** in `data/tags.json`. All tag mappings in tags.json reference **existing** emoji_ids (no broken tag→emoji references). Gaps identified: (1) **Six ship:utility_* tags** used by modules and contracts have **no entries in tags.json**, so they have no emoji mapping for secondary ship profile. (2) **Reward profiles** and **encounter types** use placeholder string values (e.g. `cargo_placeholder`, `trader_placeholder`) that are **not** in emoji.json—these are broken references for any resolver that looks up glyphs. (3) **location_warehouse** is a location_type in use but has no emoji_id in the registry. (4) No other number emoji ids exist beyond Roman numerals (roman_i–roman_x). Status-style concepts (destroyed, salvage_site, damaged, wanted) already have coverage. **Recommended expansion:** Add emoji_ids for ship utility tags (or add tag mappings to existing combat/utility-style emojis), add placeholder emoji_ids for reward/encounter display, add location_warehouse, and optionally add ship_utility_* emoji_ids if distinct glyphs are desired for module secondary display.

---

## 2. Emoji Registry Overview

### 2.1 Total emoji entries

- **Source:** `data/emoji.json`
- **Total entries:** 244 (each entry: emoji_id, glyph, description)

### 2.2 List of all emoji_id values (by category cluster)

**roman_** (10)  
roman_i, roman_ii, roman_iii, roman_iv, roman_v, roman_vi, roman_vii, roman_viii, roman_ix, roman_x

**government_** (11)  
government_anarchic, government_democracy, government_dictatorship, government_theocracy, government_fascist, government_corporate_authority, government_free_trade_coalition, government_republic, government_socialist, government_communist, government_collective_commune

**tag_** (3)  
tag_alien, tag_destroyed, tag_salvage_site

**location_** (9)  
location_bar, location_shipdock, location_market, location_contact, location_planet, location_station, location_unknown, location_administration, location_datanet

**reward_** (5)  
reward_credits, reward_goods, reward_reputation, reward_ship, reward_module

**ship_trait_** (4)  
ship_trait_military, ship_trait_civilian, ship_trait_freighter, ship_trait_experimental

**ship_condition_** (3)  
ship_condition_pristine, ship_condition_damaged, ship_condition_critical

**ship_trait_alien** (1)  
ship_trait_alien

**crew_role_** (10)  
crew_role_pilot, crew_role_gunner, crew_role_engineer, crew_role_mechanic, crew_role_tactician, crew_role_broker, crew_role_quartermaster, crew_role_lawyer, crew_role_navigator, crew_role_science

**crew_** (traits / tags) (24)  
crew_steady_aim, crew_evasive, crew_damage_control, crew_trigger_happy, crew_slow_reactions, crew_overconfident, crew_organized, crew_cluttered, crew_data_savvy, crew_fuel_efficient, crew_haggler, crew_bargain_hunter, crew_connected, crew_blacklisted, crew_wanted, crew_awkward, crew_ex_navy, crew_ex_pirate, crew_undercover, crew_loyal, crew_opportunist, crew_wasteful, crew_high_maintenance, crew_alien

**star_** (7)  
star_yellow, star_red, star_blue, star_white, star_binary, star_neutron, star_blackhole

**npc_** (1)  
npc_law

**goods_category_** (11)  
goods_category_food, goods_category_ore, goods_category_metal, goods_category_medicine, goods_category_parts, goods_category_energy, goods_category_data, goods_category_weapons, goods_category_luxury, goods_category_chemicals, goods_category_machinery

**goods_** (attributes) (22)  
goods_energy, goods_industrial, goods_medical, goods_agricultural, goods_technological, goods_luxury, goods_cultural, goods_data, goods_hazardous, goods_weapon, goods_cybernetic, goods_biological, goods_synthetic, goods_sentient, goods_propaganda, goods_counterfeit, goods_stolen, goods_essential, goods_weaponized, goods_sentient_adjacent

**secondary_** (6)  
secondary_compact, secondary_efficient, secondary_enhanced, secondary_prototype, secondary_unstable, secondary_alien

**combat_** (15)  
combat_weapon_energy, combat_weapon_kinetic, combat_weapon_disruptive, combat_defense_shielded, combat_defense_armored, combat_defense_adaptive, combat_utility_engine_boost, combat_utility_cloak, combat_utility_targeting, combat_utility_repair_system, combat_utility_overcharger, combat_utility_signal_scrambler

**encounter_** (6)  
encounter_pirate, encounter_bounty_hunter, encounter_trader, encounter_derelict_ship, encounter_random_event

**pursuit_** (3)  
pursuit_active, pursuit_evaded, pursuit_engaged

**mission_** (10)  
mission_delivery, mission_transport, mission_bounty, mission_exploration, mission_salvage, mission_illegal, mission_active, mission_completed, mission_failed

**reaction_** (3)  
reaction_hostile, reaction_neutral, reaction_friendly

**market_** (2)  
market_surplus, market_shortage

**violation_** (2)  
violation_minor, violation_major

**situation_** (32)  
situation_war, situation_plague, situation_famine, situation_economic_boom, situation_blockade, situation_recession, situation_civil_unrest, situation_trade_embargo, situation_research_breakthrough, situation_resource_shortage, situation_black_market_expansion, situation_border_tensions, situation_cultural_festival, situation_economic_recession, situation_energy_crisis, situation_exploration_craze, situation_food_shortage, situation_industrial_expansion, situation_industrial_parts_shortage, situation_infrastructure_expansion, situation_infrastructure_strain, situation_labor_strike, situation_luxury_goods_demand, situation_medical_shortage, situation_military_mobilization, situation_pirate_surge, situation_population_drain, situation_public_panic, situation_quarantine, situation_reconstruction, situation_refugee_strain, situation_religious_revival, situation_smuggling_crackdown, situation_supply_chain_failure, situation_trade_boom

**event_** (50+)  
event_solar_flare, event_market_crash, event_rebellion, event_pirate_surge, event_discovery, event_assassination, event_scientific_anomaly, event_system_failure, event_refugee_wave, event_trade_summit, event_alien_artifact_discovery, event_alien_bounty_hunters, event_alien_cultural_exchange, event_alien_cultural_exhibition, event_alien_delegation, event_alien_incident, event_alien_science_defector, event_alien_trade_pact, event_corporate_audit, event_corporate_takeover, event_diplomatic_incident, event_economic_collapse, event_economic_crisis, event_economic_shock, event_infrastructure_collapse, event_interstellar_incident, event_major_discovery, event_mass_migration, event_merchant_convoy_arrival, event_micro_singularity_event, event_pirate_warlord_emerges, event_plague_outbreak, event_political_assassination, event_religious_schism, event_resource_discovery, event_scientific_breakthrough, event_smuggler_amnesty, event_solar_flare_surge, event_stellar_instability, event_strategic_blockade, event_trade_treaty_signed, event_war

**victory_** (3)  
victory_trade, victory_reputation, victory_combat

**defeat_** (3)  
defeat_bankruptcy, defeat_arrest, defeat_death

### 2.3 Identity / status / unused

- **Entity identity:** Covered via government_*, location_*, crew_role_*, ship_trait_*, mission_*, encounter_*, etc.
- **Status:** ship_condition_*, mission_active/completed/failed, reaction_*, violation_*, pursuit_*.
- **Roman numerals:** Only number-related emoji_ids; used for tier display.
- **Duplicates:** No duplicate emoji_id values in emoji.json. Some glyphs are reused across emoji_ids (e.g. same glyph for different concepts); that is allowed.

---

## 3. Tag Mapping Coverage

### 3.1 Structure

- **Source:** `data/tags.json`
- **Structure:** Array of objects with `tag_id`, `emoji_id`, `description`. Optional `category`, `applies_to`.
- **Pipeline:** tag_id → emoji_id → (resolve glyph from emoji.json).

### 3.2 Total tag mappings

- **Total mappings:** 58

### 3.3 All emoji_ids referenced by tags.json

agricultural → goods_agricultural  
biological → goods_biological  
combat:defense_adaptive → combat_defense_adaptive  
combat:defense_armored → combat_defense_armored  
combat:defense_shielded → combat_defense_shielded  
combat:utility_cloak → combat_utility_cloak  
combat:utility_engine_boost → combat_utility_engine_boost  
combat:utility_overcharger → combat_utility_overcharger  
combat:utility_repair_system → combat_utility_repair_system  
combat:utility_signal_scrambler → combat_utility_signal_scrambler  
combat:utility_targeting → combat_utility_targeting  
combat:weapon_disruptive → combat_weapon_disruptive  
combat:weapon_energy → combat_weapon_energy  
combat:weapon_kinetic → combat_weapon_kinetic  
counterfeit → goods_counterfeit  
crew:alien → crew_alien  
crew:awkward → crew_awkward  
crew:bargain_hunter → crew_bargain_hunter  
crew:blacklisted → crew_blacklisted  
crew:cluttered → crew_cluttered  
crew:connected → crew_connected  
crew:damage_control → crew_damage_control  
crew:data_savvy → crew_data_savvy  
crew:evasive → crew_evasive  
crew:ex_navy → crew_ex_navy  
crew:ex_pirate → crew_ex_pirate  
crew:fuel_efficient → crew_fuel_efficient  
crew:haggler → crew_haggler  
crew:high_maintenance → crew_high_maintenance  
crew:loyal → crew_loyal  
crew:opportunist → crew_opportunist  
crew:organized → crew_organized  
crew:overconfident → crew_overconfident  
crew:slow_reactions → crew_slow_reactions  
crew:steady_aim → crew_steady_aim  
crew:trigger_happy → crew_trigger_happy  
crew:undercover → crew_undercover  
crew:wanted → crew_wanted  
crew:wasteful → crew_wasteful  
cultural → goods_cultural  
cybernetic → goods_cybernetic  
data → goods_data  
destroyed → tag_destroyed  
energy → goods_energy  
essential → goods_essential  
hazardous → goods_hazardous  
industrial → goods_industrial  
luxury → goods_luxury  
medical → goods_medical  
propaganda → goods_propaganda  
salvage_site → tag_salvage_site  
secondary:alien → secondary_alien  
secondary:compact → secondary_compact  
secondary:efficient → secondary_efficient  
secondary:enhanced → secondary_enhanced  
secondary:prototype → secondary_prototype  
secondary:unstable → secondary_unstable  
sentient_adjacent → goods_sentient_adjacent  
ship:trait_alien → ship_trait_alien  
ship:trait_civilian → ship_trait_civilian  
ship:trait_experimental → ship_trait_experimental  
ship:trait_freighter → ship_trait_freighter  
ship:trait_military → ship_trait_military  
stolen → goods_stolen  
synthetic → goods_synthetic  
technological → goods_technological  
weaponized → goods_weaponized  

### 3.4 Duplicate mappings

- No duplicate tag_id values in tags.json (each tag_id appears once).

### 3.5 Broken mappings (emoji_ids in tags.json that do NOT exist in emoji.json)

- **None.** Every emoji_id listed in tags.json exists in emoji.json.

---

## 4. Missing Tag → Emoji Mappings

### 4.1 Master list of tags used in the repo

**From data/goods.json (tags + possible_tag):**  
essential, agricultural, luxury, synthetic, cultural, industrial, hazardous, medical, technological, biological, stolen, cybernetic, weaponized, sentient_adjacent, energy, data, propaganda, counterfeit

**From data/hulls.json (traits):**  
ship:trait_civilian, ship:trait_freighter, ship:trait_military, ship:trait_experimental, ship:trait_alien

**From data/modules.json (primary_tag):**  
combat:weapon_energy, combat:weapon_kinetic, combat:weapon_disruptive, combat:defense_shielded, combat:defense_armored, combat:defense_adaptive, combat:utility_engine_boost, combat:utility_targeting, combat:utility_repair_system, combat:utility_signal_scrambler, combat:utility_overcharger, ship:utility_extra_cargo, ship:utility_data_array, ship:utility_smuggler_hold, ship:utility_mining_equipment, ship:utility_probe_array, ship:utility_interdiction, ship:utility_extra_fuel

**From data/mission_definitions.json / events (tag references):**  
ship:trait_alien, secondary:alien

**Crew tags (from crew_contract / crew_roles):**  
All crew:* tags used in code/tests map via tags.json (crew:alien, crew:wanted, etc.); all are in tags.json.

### 4.2 Tags present in repo but missing in tags.json

**MISSING TAG MAPPINGS (no emoji mapping yet):**

- ship:utility_extra_cargo  
- ship:utility_data_array  
- ship:utility_smuggler_hold  
- ship:utility_mining_equipment  
- ship:utility_probe_array  
- ship:utility_interdiction  
- ship:utility_extra_fuel  

All goods tags, hull traits (ship:trait_*), and combat tags used in data are present in tags.json. Only the **ship:utility_*** set is missing.

### 4.3 Tags mapped to emoji_ids missing from emoji.json

- **None.** Every tag in tags.json points to an emoji_id that exists in emoji.json.

---

## 5. Broken Emoji References (data referencing emoji_ids not in registry)

These are **not** tag mappings; they are direct **emoji** / **emoji_id** fields in data that reference strings not present in emoji.json.

### 5.1 data/reward_profiles.json (field "emoji")

Values used (placeholders, not in emoji.json):

- cargo_placeholder  
- skull_crate_placeholder  
- raider_crate_placeholder  
- alien_crate_placeholder  
- derelict_crate_placeholder  
- cache_placeholder  
- credit_placeholder  
- crate_placeholder  
- module_placeholder  
- hull_placeholder  
- data_crate_placeholder  
- rare_crate_placeholder  
- mining_crate_placeholder  

### 5.2 data/encounter_types.json (field "emoji")

Values used (placeholders, not in emoji.json):

- trader_placeholder  
- authority_placeholder  
- bounty_placeholder  
- pirate_placeholder  
- raider_placeholder  
- derelict_placeholder  
- derelict_station_placeholder  
- distress_placeholder  
- asteroid_field_placeholder  
- ion_storm_placeholder  
- debris_storm_placeholder  
- comet_passage_placeholder  
- spatial_rift_placeholder  
- ancient_beacon_placeholder  
- quantum_echo_placeholder  
- wormhole_placeholder  

Any code that resolves these via emoji.json will get no glyph until these ids are added (or aliased to existing emoji_ids).

---

## 6. Entity Primary Emoji Coverage

| Entity type   | Primary emoji source / schema              | Status        | Notes |
|---------------|--------------------------------------------|---------------|--------|
| **Ships**     | Hull trait → ship_trait_* (in emoji.json) | **Defined**   | emoji_id from hull; condition_emoji_id for state. All hull traits (civilian, freighter, military, experimental, alien) have emoji_ids. |
| **Crew**      | role_id → crew_role_* (in emoji.json)     | **Defined**   | Convention crew_role_&lt;role_id&gt;; all 10 roles have emoji_ids. |
| **Goods**     | Category / tags → goods_* (in emoji.json)  | **Defined**   | No single primary on SKU; display uses category or tags; all goods tags mapped. |
| **Destinations** | destination.emoji_id; defaults by type  | **Defined**   | world_generator sets emoji_id (e.g. location_unknown, goods_category_ore). |
| **Locations** | location_type → location_*                 | **Partial**   | location_bar, location_market, location_shipdock, location_administration, location_datanet exist. **Missing:** location_warehouse (location_type "warehouse" in location_availability.json). |
| **Missions**  | mission_type → mission_*                   | **Defined**   | mission_delivery, mission_bounty, etc. in emoji.json. Contract requires emoji_id. |
| **Events**    | event.emoji_id in data/events.json          | **Defined**   | All event records carry emoji_id; all listed event_* ids exist in emoji.json. |
| **Situations**| situation.emoji_id in data/situations.json  | **Defined**   | All situation records carry emoji_id; all listed situation_* ids exist in emoji.json. |
| **Reward profiles** | profile["emoji"] placeholder strings   | **Missing**   | Placeholder ids not in emoji.json (see Section 5). |
| **Encounter types** | subtype["emoji"] placeholder strings    | **Missing**   | Placeholder ids not in emoji.json (see Section 5). |

---

## 7. Category Gap Analysis

| Category / prefix     | Count in registry | Tags referencing (from tags.json) | Gaps |
|------------------------|-------------------|------------------------------------|------|
| roman_                 | 10                | 0 (tier from int, not tag)        | None. |
| government_            | 11                | 0 (entity field)                   | None. |
| tag_                   | 3                 | 2 (destroyed, salvage_site)        | None. |
| location_              | 9                 | 0 (entity/destination field)       | **Missing:** location_warehouse. |
| reward_                | 5                 | 0 (reward_profiles use placeholders) | Placeholder ids not in registry. |
| ship_trait_ / ship_condition_ | 8             | 5 ship:trait_* in tags.json        | None for traits. |
| crew_role_             | 10                | 0 (role_id convention)             | None. |
| crew_ (traits)         | 24                | 24 crew:* in tags.json              | None. |
| goods_category_        | 10                | 0 (goods category field)           | None. |
| goods_                 | 22                | 18+ tag_ids in tags.json            | None. |
| secondary_             | 6                 | 6 secondary:* in tags.json          | None. |
| combat_                | 15                | 12 combat:* in tags.json            | **Missing tag mappings:** ship:utility_* (6) not in tags.json; no ship_utility_* emoji_ids. |
| encounter_             | 6                 | 0 (encounter_types use placeholders) | Placeholder ids not in registry. |
| mission_               | 10                | 0 (mission_type)                    | None. |
| situation_             | 32                | 0 (situation_id in data)           | None. |
| event_                 | 50+               | 0 (event_id in data)                | None. |

---

## 8. Unused Emoji Registry Entries

Emoji_ids that exist in emoji.json but are **not** referenced by:

- tags.json  
- entity/destination/event/situation schemas (as primary or in data)  
- contracts (as required identifiers)  
- tests (as expected values)

**Likely unused or only indirectly used:**

- **star_*** (star_yellow, star_red, star_blue, star_white, star_binary, star_neutron, star_blackhole) — Used for system/star display if implemented; may be unused in current CLI.
- **npc_law** — Law enforcement presence; may be used in encounter or NPC display.
- **reaction_hostile / reaction_neutral / reaction_friendly** — Encounter/posture display.
- **market_surplus / market_shortage** — Market state display.
- **violation_minor / violation_major** — Enforcement display.
- **pursuit_active / pursuit_evaded / pursuit_engaged** — Pursuit state display.
- **mission_active / mission_completed / mission_failed** — Mission state display.
- **victory_* / defeat_*** — Endgame display.

These are not “missing”; they are available for current or future presentation. No removal recommended; they support Phase 7.14 and UI.

---

## 9. Numeric Emoji Findings

### 9.1 Roman numeral ids in emoji.json

- **Present:** roman_i, roman_ii, roman_iii, roman_iv, roman_v, roman_vi, roman_vii, roman_viii, roman_ix, roman_x (10 entries).

### 9.2 Decimal digit ids

- **None** in emoji.json.

### 9.3 Other number symbol ids

- **None** in emoji.json.

### 9.4 Systems referencing numeric emoji ids

- **Tier display:** emoji_profile_contract and contracts require tier → Roman numeral (roman_i … roman_x) via emoji.json. Ship tier, mission_tier, severity_tier, etc. use integer 1–10; builder must map to these ids. No code or data references decimal or other number emoji ids.

---

## 10. Status Emoji Needs

Concepts checked for status-style display:

| Concept      | In registry? | emoji_id / tag |
|-------------|-------------|-----------------|
| destroyed   | Yes         | tag_destroyed   |
| salvage     | Yes         | tag_salvage_site |
| damaged     | Yes         | ship_condition_damaged |
| abandoned   | No          | — (no explicit “abandoned” emoji_id or tag) |
| wanted      | Yes         | crew_wanted     |
| inspected   | No          | — (no “inspected” emoji_id) |
| scanned     | No          | — (no “scanned” emoji_id) |
| pristine    | Yes         | ship_condition_pristine |
| critical    | Yes         | ship_condition_critical |

Destroyed, salvage, damaged, wanted, pristine, and critical have coverage. Abandoned, inspected, and scanned have no emoji_id; add only if Phase 7.14 or UI requires them.

---

## 11. Recommended Emoji Registry Expansion

Below are **emoji_ids to add** to emoji.json (identifiers only; no glyphs assigned in this audit).

### 11.1 Missing tag mappings (ship:utility_*)

Add to **tags.json** as tag_id → emoji_id, and ensure the following **emoji_ids** exist in **emoji.json** (add if not present):

- ship_utility_extra_cargo  
- ship_utility_data_array  
- ship_utility_smuggler_hold  
- ship_utility_mining_equipment  
- ship_utility_probe_array  
- ship_utility_interdiction  
- ship_utility_extra_fuel  

(If the contract uses “combat_utility_*” style for ship utilities, these could instead map to existing or new combat_utility_* or a shared utility set; the important part is that each ship:utility_* tag_id has a corresponding emoji_id in emoji.json and a mapping in tags.json.)

### 11.2 Location type

- location_warehouse  

(Used by location_availability.json as location_type "warehouse"; no current location_* emoji_id for it.)

### 11.3 Reward profile placeholders (for reward_profiles.json)

Add so each profile can resolve a glyph:

- cargo_placeholder  
- skull_crate_placeholder  
- raider_crate_placeholder  
- alien_crate_placeholder  
- derelict_crate_placeholder  
- cache_placeholder  
- credit_placeholder  
- crate_placeholder  
- module_placeholder  
- hull_placeholder  
- data_crate_placeholder  
- rare_crate_placeholder  
- mining_crate_placeholder  

### 11.4 Encounter type placeholders (for encounter_types.json)

- trader_placeholder  
- authority_placeholder  
- bounty_placeholder  
- pirate_placeholder  
- raider_placeholder  
- derelict_placeholder  
- derelict_station_placeholder  
- distress_placeholder  
- asteroid_field_placeholder  
- ion_storm_placeholder  
- debris_storm_placeholder  
- comet_passage_placeholder  
- spatial_rift_placeholder  
- ancient_beacon_placeholder  
- quantum_echo_placeholder  
- wormhole_placeholder  

### 11.5 Optional (status / UX)

Only if product needs them:

- status_abandoned  
- status_inspected  
- status_scanned  

---

## 12. Systems Requiring Emoji Coverage in Phase 7.14

| System            | Current coverage | Action for Phase 7.14 |
|-------------------|------------------|------------------------|
| **Crew profile**  | role + tag_ids → tags.json → emoji.json | Complete; no tag gaps for crew. |
| **Ship profile**  | Hull trait + modules (primary_tag, secondary_tags) | Add ship:utility_* → emoji_id (tags.json + emoji.json). |
| **Destination display** | emoji_id on destination | Complete; defaults exist. |
| **Location display**   | location_type → location_* | Add location_warehouse. |
| **Mission display**     | mission_type → mission_* | Complete. |
| **Events / situations** | emoji_id in data | Complete. |
| **Reward profile display** | profile["emoji"] | Add placeholder emoji_ids to emoji.json (or migrate to existing reward_* ids). |
| **Encounter display**   | subtype["emoji"] | Add encounter placeholder emoji_ids to emoji.json (or alias to existing encounter_* ids). |
| **Goods / SKU display** | tags → tags.json | Complete. |
| **Tier display**        | roman_i–roman_x | Complete. |

— End of audit —
