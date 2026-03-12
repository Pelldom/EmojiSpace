EMOJI REGISTRY AUDIT REPORT
1. Registry summary
Total registry entries (data/emoji.json): 298
Verified by loading the file as JSON and counting the top-level array length.
2. Referenced emoji_ids in data files
Data files scanned (direct or indirect emoji sources):

data/governments.json – emoji_id fields (11 governments)
data/economies.json – no emoji_id fields (ids only)
data/crew_roles.json – no emoji_id fields (role_id only)
data/mission_definitions.json – no emoji_id fields (mission_type + tags only)
data/hulls.json – uses traits (e.g. ship:trait_civilian) ? tags.json ? emoji_id
data/modules.json – uses primary_tag (e.g. combat:weapon_energy) ? tags.json ? emoji_id
data/tags.json – emoji_id fields (74 tags)
data/encounter_types.json – no emoji_id fields (legacy emoji placeholders only)
data/situations.json – emoji_id fields (27 situations)
data/events.json – emoji_id fields (38 events)
data/categories.json – emoji_id fields (11 goods categories)
Distinct emoji_id families referenced:

Governments:

government_free_trade_coalition
government_corporate_authority
government_fascist
government_anarchic
government_democracy
government_republic
government_socialist
government_communist
government_collective_commune
government_theocracy
government_dictatorship
Tags (74 entries in tags.json):

Goods traits: goods_agricultural, goods_biological, goods_counterfeit, goods_cultural, goods_cybernetic, goods_data, goods_energy, goods_essential, goods_hazardous, goods_industrial, goods_luxury, goods_medical, goods_propaganda, goods_sentient_adjacent, goods_stolen, goods_synthetic, goods_technological, goods_weaponized, etc.
Combat traits: combat_defense_adaptive, combat_defense_armored, combat_defense_shielded, combat_utility_cloak, combat_utility_engine_boost, combat_utility_overcharger, combat_utility_repair_system, combat_utility_signal_scrambler, combat_utility_targeting, combat_weapon_disruptive, combat_weapon_energy, combat_weapon_kinetic, etc.
Crew traits: crew_alien, crew_awkward, crew_bargain_hunter, crew_blacklisted, crew_cluttered, crew_connected, crew_damage_control, crew_data_savvy, crew_evasive, crew_ex_navy, crew_ex_pirate, crew_fuel_efficient, crew_haggler, crew_high_maintenance, crew_loyal, crew_opportunist, crew_organized, crew_overconfident, crew_slow_reactions, crew_steady_aim, crew_trigger_happy, crew_undercover, crew_wanted, crew_wasteful.
Ship traits/utilities: ship_trait_alien, ship_trait_civilian, ship_trait_experimental, ship_trait_freighter, ship_trait_military, ship_utility_data_array, ship_utility_extra_cargo, ship_utility_extra_fuel, ship_utility_interdiction, ship_utility_mining_equipment, ship_utility_probe_array, ship_utility_smuggler_hold.
Meta: secondary_alien, secondary_compact, secondary_efficient, secondary_enhanced, secondary_prototype, secondary_unstable, tag_destroyed, tag_salvage_site.
These are:

Referenced directly in tags.json, and
Referenced indirectly by hulls.json (traits) and modules.json (primary_tag).
Situations (27 in situations.json):

e.g. situation_trade_boom, situation_economic_recession, situation_pirate_surge, situation_military_mobilization, situation_border_tensions, situation_civil_unrest, situation_labor_strike, situation_industrial_expansion, situation_resource_shortage, situation_energy_crisis, situation_quarantine, situation_cultural_festival, situation_religious_revival, situation_black_market_expansion, situation_smuggling_crackdown, situation_exploration_craze, situation_infrastructure_strain, situation_refugee_strain, situation_reconstruction, situation_public_panic, situation_medical_shortage, situation_food_shortage, situation_industrial_parts_shortage, situation_luxury_goods_demand, situation_supply_chain_failure, situation_population_drain, situation_infrastructure_expansion.
Events (38 in events.json):

e.g. event_solar_flare_surge, event_alien_delegation, event_major_discovery, event_merchant_convoy_arrival, event_smuggler_amnesty, event_war, event_plague_outbreak, event_economic_shock, event_alien_incident, event_corporate_audit, event_pirate_warlord_emerges, event_trade_treaty_signed, event_resource_discovery, event_economic_crisis, event_political_assassination, event_infrastructure_collapse, event_scientific_breakthrough, event_alien_science_defector, etc.
Goods categories (categories.json, 11 entries):

goods_category_food, goods_category_ore, goods_category_metal, goods_category_medicine, goods_category_parts, goods_category_energy, goods_category_data, goods_category_weapons, goods_category_luxury, goods_category_chemicals, goods_category_machinery.
Distinct referenced emoji_ids (from these families):

Governments: 11
Tags: 74
Situations: 27
Events: 38
Categories: 11
Total distinct referenced emoji_ids (union of these disjoint families):
11 + 74 + 27 + 38 + 11 = 161

Note: Hulls and modules do not introduce new emoji_ids; they re-use the tag-based emoji_ids listed above.

3. Missing registry entries (CHECK A)
Definition: emoji_ids referenced by the data layer that do not exist in data/emoji.json.

From the families above:

All **government_*** ids found in governments.jsonare present inemoji.json` (verified via grep).
All tag-based emoji_ids from tags.json are present in emoji.json.
All **situation_*** ids from situations.jsonare present inemoji.json`.
All **event_*** ids from events.jsonare present inemoji.json`.
All **goods_category_*** ids from categories.jsonare present inemoji.json`.
Hulls and modules only reference tag-based IDs already covered above.
Result:

Missing emoji_ids:
(none found)
The registry includes every emoji_id currently referenced in the scanned data files.

4. Orphaned registry entries (CHECK B)
Definition: emoji_ids that exist in data/emoji.json but are not referenced anywhere in the data layer (directly or via traits/tags as modeled above).

Since:

Registry entries: 298
Referenced emoji_ids: 161
Orphaned registry entries: 298 ? 161 = 137
These orphaned IDs fall into several broad categories:

Crew roles (not yet wired in data via emoji_id):

e.g. crew_role_pilot, crew_role_gunner, crew_role_tactician, crew_role_engineer, crew_role_mechanic, crew_role_navigator, crew_role_broker, crew_role_quartermaster, crew_role_lawyer, crew_role_science.
(These exist in emoji.json but crew_roles.json currently has no emoji_id field.)
Economies (prepared for future use):

economy_mining, economy_agricultural, economy_industrial, economy_tech, economy_trade, economy_military, economy_research, economy_tourism, economy_cultural.
(These exist in emoji.json but economies.json has no emoji_id fields yet.)
Mission-level glyphs beyond the core ones used so far:

Already used in data indirectly via UI/logic (status) but not referenced as emoji_id by data files:
mission_active, mission_completed, mission_failed, mission_illegal.
New mission-type emojis recently added but not yet referenced in data:
mission_retrieval, mission_patrol, mission_rescue, mission_scan, mission_assassination, mission_escort, mission_recon, mission_supply, mission_smuggling, mission_blockade.
Encounter emojis (registry entries not wired to data yet):

encounter_trader, encounter_authority, encounter_pirate, encounter_raider, encounter_bounty_hunter, encounter_derelict, encounter_derelict_ship, encounter_derelict_station, encounter_distress, encounter_asteroid_field, encounter_ion_storm, encounter_debris_storm, encounter_comet, encounter_spatial_rift, encounter_ancient_beacon, encounter_quantum_echo, encounter_wormhole, encounter_random_event.
(These exist in emoji.json, but encounter_types.json still uses legacy emoji string placeholders and no emoji_id fields.)
Meta / system / status / crate glyphs that are engine/CLI-only and not referenced via data:

Examples:
Crates & caches: mining_cache, module_crate, npc_law, raider_crate, rare_crate, supply_cache, alien_crate, cargo_crate, etc.
Status and reaction: mission_active, mission_completed, mission_failed, status_abandoned, status_inspected, status_scanned, reaction_friendly, reaction_hostile, reaction_neutral, pursuit_active, pursuit_engaged, pursuit_evaded, etc.
Star/system markers: star_blue, star_neutron, star_red, star_white, star_yellow, and various victory_*, violation_* glyphs.
These orphaned entries are not errors per se; many are intended for UI state, events, or future features that are not yet driven by data-layer emoji_id fields.

5. Compliance summary
Total registry entries (emoji.json): 298
Total distinct emoji_ids referenced via data layer (direct or via tags/traits): 161
Missing registry entries (data ? registry): 0
Orphaned registry entries (registry ? data): 137 (see families above)
Status:

CHECK A – Missing registry entries:
? Pass – Every emoji_id referenced by the scanned data files has a matching entry in emoji.json.

CHECK B – Orphaned registry entries:
? Partial – Large, intentional pool of emoji_ids (economies, crew roles, missions, encounters, and meta/status glyphs) are defined in emoji.json but are not yet referenced by the current data layer.

Overall, the emoji registry is superset-compliant with the data layer: data never references a missing emoji_id, but the registry contains many additional (planned or UI-focused) emoji_ids that are not yet wired into data.