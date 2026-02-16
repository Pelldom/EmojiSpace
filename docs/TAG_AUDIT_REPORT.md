=== TAG AUDIT REPORT ===

[File: src/combat_resolver.py]
Line 148: `if entry.startswith("secondary:"):`
Explanation: Prefix-based parsing of secondary tag namespace.

Line 149: `values.add(entry.split("secondary:", 1)[1])`
Explanation: Split-based parsing that assumes `secondary:` format.

Line 155: `return tag in s or f"secondary:{tag}" in s`
Explanation: Exact/prefix hybrid check for normalized vs namespaced secondary tags.

Line 185: `if tag == "combat:weapon_energy":`
Explanation: Exact match assumes combat namespaced tag string.

Line 187: `elif tag == "combat:weapon_kinetic":`
Explanation: Exact match on combat tag.

Line 189: `elif tag == "combat:weapon_disruptive":`
Explanation: Exact match on combat tag.

Line 202: `if tag == "combat:defense_shielded":`
Explanation: Exact match on combat defense tag.

Line 204: `elif tag == "combat:defense_armored":`
Explanation: Exact match on combat defense tag.

Line 206: `elif tag == "combat:defense_adaptive":`
Explanation: Exact match on combat defense tag.

Line 272: `return bool(module and module["primary_tag"] == "combat:utility_repair_system")`
Explanation: Exact match utility tag assumption.

Line 286: `"combat:weapon_energy": "weapon_energy_mk1",`
Explanation: Hardcoded mapping key for tag-to-module translation.

Line 287: `"combat:weapon_kinetic": "weapon_kinetic_mk1",`
Explanation: Hardcoded mapping key.

Line 288: `"combat:weapon_disruptive": "weapon_disruptive_mk1",`
Explanation: Hardcoded mapping key.

Line 289: `"combat:defense_shielded": "defense_shielded_mk1",`
Explanation: Hardcoded mapping key.

Line 290: `"combat:defense_armored": "defense_armored_mk1",`
Explanation: Hardcoded mapping key.

Line 291: `"combat:defense_adaptive": "defense_adaptive_mk1",`
Explanation: Hardcoded mapping key.

Line 292: `"combat:utility_engine_boost": "combat_utility_engine_boost_mk1",`
Explanation: Hardcoded mapping key.

Line 293: `"combat:utility_targeting": "combat_utility_targeting_mk1",`
Explanation: Hardcoded mapping key.

Line 294: `"combat:utility_repair_system": "combat_utility_repair_system_mk1",`
Explanation: Hardcoded mapping key.

Line 295: `"combat:utility_signal_scrambler": "combat_utility_signal_scrambler_mk1",`
Explanation: Hardcoded mapping key.

Line 296: `"combat:utility_overcharger": "combat_utility_overcharger_mk1",`
Explanation: Hardcoded mapping key.

Line 297: `"combat:utility_cloak": "ship_utility_probe_array",`
Explanation: Hardcoded mapping key (possible alias behavior).

Line 298: `"ship:utility_extra_cargo": "ship_utility_extra_cargo",`
Explanation: Hardcoded ship utility tag key.

Line 299: `"ship:utility_data_array": "ship_utility_data_array",`
Explanation: Hardcoded ship utility tag key.

Line 300: `"ship:utility_smuggler_hold": "ship_utility_smuggler_hold",`
Explanation: Hardcoded ship utility tag key.

Line 301: `"ship:utility_mining_equipment": "ship_utility_mining_equipment",`
Explanation: Hardcoded ship utility tag key.

Line 302: `"ship:utility_probe_array": "ship_utility_probe_array",`
Explanation: Hardcoded ship utility tag key.

Line 303: `"ship:utility_interdiction": "ship_utility_interdiction",`
Explanation: Hardcoded ship utility tag key.

Line 437: `if _has_secondary(instance, "alien") and "ship:trait_alien" in hull_traits:`
Explanation: Hybrid check combining normalized secondary token + namespaced trait tag.

Line 517: `if module_defs[entry["module_id"]]["primary_tag"] == "combat:utility_cloak":`
Explanation: Exact match for combat utility tag.

Line 520: `if module_defs[entry["module_id"]]["primary_tag"] == "ship:utility_interdiction":`
Explanation: Exact match for ship utility tag.

Line 740: `...["primary_tag"] == "ship:utility_probe_array"...`
Explanation: Exact ship utility tag check gates scan behavior.

Line 751: `...["primary_tag"] == "ship:utility_probe_array"...`
Explanation: Same exact match logic for enemy side.

---

[File: src/ship_assembler.py]
Line 100: `if entry.startswith("secondary:"):`
Explanation: Prefix-based parsing of secondary namespace.

Line 101: `normalized.add(entry.split("secondary:", 1)[1])`
Explanation: Split-based parsing of namespaced secondary tags.

Line 106: `return name in secondary_tags or f"secondary:{name}" in secondary_tags`
Explanation: Exact/prefix hybrid compatibility logic.

Line 137: `if slot_type == "weapon" and not primary_tag.startswith("combat:weapon_"):`
Explanation: Prefix rule enforces combat weapon tag namespace.

Line 139: `if slot_type == "defense" and not primary_tag.startswith("combat:defense_"):`
Explanation: Prefix rule enforces combat defense namespace.

Line 142: `if not (primary_tag.startswith("combat:utility_") or primary_tag.startswith("ship:utility_")):`
Explanation: Prefix-based validation assumes utility tags in combat/ship namespaces.

Line 151: `is_experimental_hull = "ship:trait_experimental" in hull.get("traits", [])`
Explanation: Exact namespaced trait check.

Line 152: `is_alien_hull = "ship:trait_alien" in hull.get("traits", [])`
Explanation: Exact namespaced trait check.

Line 166: `if module_def["primary_tag"] == "combat:defense_armored":`
Explanation: Exact tag check affects hull max.

Line 297: `if entry["primary_tag"] == "ship:utility_extra_cargo":`
Explanation: Exact ship utility tag behavior mapping.

Line 299: `elif entry["primary_tag"] == "ship:utility_data_array":`
Explanation: Exact ship utility tag mapping.

Line 301: `elif entry["primary_tag"] == "ship:utility_interdiction":`
Explanation: Exact ship utility tag mapping.

Line 303: `elif entry["primary_tag"] == "ship:utility_smuggler_hold":`
Explanation: Exact ship utility tag mapping.

Line 305: `elif entry["primary_tag"] == "ship:utility_mining_equipment":`
Explanation: Exact ship utility tag mapping.

Line 307: `elif entry["primary_tag"] == "ship:utility_probe_array":`
Explanation: Exact ship utility tag mapping.

Line 309: `elif entry["primary_tag"] == "ship:utility_extra_fuel":`
Explanation: Exact ship utility tag mapping.

Line 328: `... entry["primary_tag"] == "combat:utility_engine_boost"`
Explanation: Exact tag check in engine subsystem aggregation.

---

[File: src/salvage_resolver.py]
Line 69: `if entry.startswith("secondary:"):`
Explanation: Prefix-based secondary tag parsing.

Line 70: `values.add(entry.split("secondary:", 1)[1])`
Explanation: Split-based parsing of secondary namespace.

Line 78: `has_alien = "alien" in secondaries or "secondary:alien" in secondaries`
Explanation: Hardcoded hybrid support for normalized and namespaced alien secondary tags.

Line 79: `has_non_alien = any(tag not in {"alien", "secondary:alien"} for tag in secondaries)`
Explanation: Exact-match exclusion logic based on old/new alien token forms.

Line 84: `if "prototype" in secondaries or "secondary:prototype" in secondaries:`
Explanation: Hybrid token handling for prototype modifier.

Line 86: `if "unstable" in secondaries or "secondary:unstable" in secondaries:`
Explanation: Hybrid token handling for unstable modifier.

Line 135: `instance["secondary_tags"] = ["secondary:unstable"]`
Explanation: Hardcoded namespaced tag output.

---

[File: src/npc_ship_generator.py]
Line 150: `return [f"secondary:{first}"]`
Explanation: Emits namespaced secondary tags explicitly.

Line 155: `tags = ["secondary:alien"]`
Explanation: Hardcoded alien secondary tag baseline.

Line 157: `tags.append(f"secondary:{second}")`
Explanation: Namespaced secondary generation assumption.

---

[File: src/shipdock_inventory.py]
Line 70: `if value.startswith("secondary:"):`
Explanation: Prefix-based parsing of secondary namespace.

Line 71: `expanded.add(value.split("secondary:", 1)[1])`
Explanation: Split-based parsing for compatibility.

Line 72: `return "prototype" in expanded or "alien" in expanded or "secondary:prototype" in expanded or "secondary:alien" in expanded`
Explanation: Hybrid old/new token assumptions for risk filtering.

---

[File: src/data_loader.py]
Line 249: `"combat:weapon_energy",`
Explanation: Hardcoded allowed primary tags list.

Line 250: `"combat:weapon_kinetic",`
Explanation: Hardcoded allowed primary tags list.

Line 251: `"combat:weapon_disruptive",`
Explanation: Hardcoded allowed primary tags list.

Line 258: `"combat:defense_shielded",`
Explanation: Hardcoded allowed primary tags list.

Line 259: `"combat:defense_armored",`
Explanation: Hardcoded allowed primary tags list.

Line 260: `"combat:defense_adaptive",`
Explanation: Hardcoded allowed primary tags list.

Line 266: `if primary_tag.startswith("combat:utility_") or primary_tag.startswith("ship:utility_"):`
Explanation: Prefix-based namespace validation for utility tags.

---

[File: src/turn_loop.py]
Line 275: `tags = self._sku_tags(system_id, sku)`
Explanation: Collects tag list used in legality checks.

Line 278: `commodity=Commodity(commodity_id=sku, tags=set(tags)),`
Explanation: Passes tags into law engine policy evaluation.

Line 324: `tags = self._sku_tags(system_id, sku)`
Explanation: Collects tags for pricing policy context.

Line 327: `commodity=Commodity(commodity_id=sku, tags=set(tags)),`
Explanation: Law policy call with tags.

Line 392: `return list(market_good.tags)`
Explanation: Uses tags as loaded from market data.

Line 394: `return list(self._catalog.good_by_sku(sku).tags)`
Explanation: Uses tags as loaded from catalog.

Line 400: `base_tags = list(self._catalog.good_by_sku(base_sku).tags)`
Explanation: Tag carry-forward when stripping possible-tag prefix.

Line 403: `prefix = sku.split("_", 1)[0]`
Explanation: `_` parsing assumption for prefixed SKUs.

Line 408: `possible_tags = {`
Explanation: Hardcoded tag-name set used for SKU prefix logic.

Line 409: `"luxury",`
Explanation: Hardcoded tag name.

Line 410: `"weaponized",`
Explanation: Hardcoded tag name.

Line 411: `"counterfeit",`
Explanation: Hardcoded tag name.

Line 412: `"propaganda",`
Explanation: Hardcoded tag name.

Line 413: `"stolen",`
Explanation: Hardcoded tag name.

Line 414: `"hazardous",`
Explanation: Hardcoded tag name.

Line 415: `"cybernetic",`
Explanation: Hardcoded tag name.

Line 419: `prefix, remainder = sku.split("_", 1)`
Explanation: `_` parsing of SKU prefix into semantic tag + base SKU.

---

[File: src/government_law_engine.py]
Line 73: `restricted_tags = set(government.ideological_modifiers.get("restricted_tags", []))`
Explanation: Tag policy input from government config.

Line 79: `elif tags.intersection(restricted_tags):`
Explanation: Set intersection for legality classification.

Line 82: `consumed_tags.update(tags.intersection(restricted_tags))`
Explanation: Consumes matched tags for policy output.

Line 269: `bias, risk, interpreted = interpret_policy_tags(government, tags)`
Explanation: Delegates tag interpretation to central utility.

---

[File: src/tag_policy_engine.py]
Line 8: `"luxury",`
Explanation: Hardcoded supported tag vocabulary.

Line 9: `"weaponized",`
Explanation: Hardcoded supported tag vocabulary.

Line 10: `"counterfeit",`
Explanation: Hardcoded supported tag vocabulary.

Line 11: `"stolen",`
Explanation: Hardcoded supported tag vocabulary.

Line 12: `"propaganda",`
Explanation: Hardcoded supported tag vocabulary.

Line 13: `"hazardous",`
Explanation: Hardcoded supported tag vocabulary.

Line 14: `"cybernetic",`
Explanation: Hardcoded supported tag vocabulary.

Line 27: `if tag not in POSSIBLE_TAGS:`
Explanation: Exact whitelist gate for tag interpretation.

Line 37: `favored_tags = set(getattr(government, "ideological_modifiers").get("favored_tags", []))`
Explanation: Uses favored tag lists from government profile.

Line 38: `restricted_tags = set(getattr(government, "ideological_modifiers").get("restricted_tags", []))`
Explanation: Uses restricted tag lists from government profile.

Line 48: `if tag == "luxury":`
Explanation: Exact-match branch logic.

Line 61: `elif tag == "weaponized":`
Explanation: Exact-match branch logic.

Line 76: `elif tag == "counterfeit":`
Explanation: Exact-match branch logic.

Line 88: `elif tag == "stolen":`
Explanation: Exact-match branch logic.

Line 97: `elif tag == "propaganda":`
Explanation: Exact-match branch logic.

Line 107: `elif tag == "hazardous":`
Explanation: Exact-match branch logic.

Line 116: `elif tag == "cybernetic":`
Explanation: Exact-match branch logic.

---

[File: src/market_pricing.py]
Line 102: `tags = _resolved_tags(good, market_good)`
Explanation: Pulls tags for price interpretation.

Line 103: `skipped_tags = [tag for tag in tags if tag in policy.consumed_tags]`
Explanation: Exact set membership against consumed tags.

Line 104: `interpreted_tags = [tag for tag in tags if tag not in policy.consumed_tags]`
Explanation: Exclusion-based tag filtering.

Line 183: `bias, risk, _ = interpret_policy_tags(government, tags)`
Explanation: Delegates tag interpretation to central utility.

---

[File: src/law_enforcement.py]
Line 533: `if "piracy" in tags:`
Explanation: Exact string match on consumed tags list.

Line 545: `if "stolen" in tags:`
Explanation: Exact string match on consumed tags list.

Line 547: `if "counterfeit" in tags:`
Explanation: Exact string match on consumed tags list.

Line 699: `if violation_type == "stolen_goods_possession" and "stolen" not in policy.consumed_tags:`
Explanation: Exact tag check in enforcement validation.

Line 701: `if violation_type == "counterfeit_goods_possession" and "counterfeit" not in policy.consumed_tags:`
Explanation: Exact tag check in enforcement validation.

---

[File: src/data_catalog.py]
Line 91: `allowed_possible_tags = {`
Explanation: Hardcoded allowed possible-tag vocabulary for goods data validation.

Line 92: `"luxury",`
Explanation: Hardcoded possible tag.

Line 93: `"weaponized",`
Explanation: Hardcoded possible tag.

Line 94: `"counterfeit",`
Explanation: Hardcoded possible tag.

Line 95: `"propaganda",`
Explanation: Hardcoded possible tag.

Line 96: `"stolen",`
Explanation: Hardcoded possible tag.

Line 97: `"hazardous",`
Explanation: Hardcoded possible tag.

Line 98: `"cybernetic",`
Explanation: Hardcoded possible tag.

Line 104: `for tag in entry.get("tags", []):`
Explanation: Iterates and validates declared tags.

Line 105: `if tag not in tags:`
Explanation: Exact key existence validation against known tag registry.

Line 108: `if possible_tag is not None and possible_tag not in tags:`
Explanation: Exact validation for optional possible_tag.

---

[File: src/interaction_resolvers.py]
Line 340: `if "secondary:prototype" in secondary_tags:`
Explanation: Exact namespaced tag check for resale multiplier.

Line 342: `if "secondary:alien" in secondary_tags:`
Explanation: Exact namespaced tag check for resale multiplier.

---

[File: src/entities.py]
Line 45: `tags=[f"location_type:{location_type}"],`
Explanation: Emits namespaced tag-like string via prefix convention.

---

[File: src/end_game_evaluator.py]
Line 96: `if mission.mission_type.startswith("victory:"):`
Explanation: Prefix-based parsing assumption for mission type namespace.

Line 97: `return mission.mission_type.split("victory:", 1)[1]`
Explanation: Split-based extraction from namespaced mission type.

=== SUMMARY ===
Total locations: 332 (broad pattern hit count across `src/`; includes definitions + logic)
Exact match usage: Present (heavy; many `== "combat:..."`, `in {"luxury", ...}` checks)
Prefix usage: Present (`startswith("secondary:")`, `startswith("combat:...")`, `startswith("victory:")`)
Suffix usage: None found (`endswith(...)` not found)
Parsing usage: Present (`split("secondary:", 1)`, `split("_", 1)`, `split("victory:", 1)`)
Namespace risk level: Medium
Recommendation: Yes, centralizing tag handling into a utility module is recommended (expand beyond current `tag_policy_engine`). Suggested target: shared helpers for namespace parsing, compatibility normalization (`secondary:x` vs `x`), and canonical tag constants to reduce distributed hardcoded assumptions.

