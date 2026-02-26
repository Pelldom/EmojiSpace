Verdict
Overall purge status: PASS
All legacy mission types (escort, recovery) have been removed from generation; only structured delivery missions can be generated through the new registry + factory path. One residual defensive fallback (mission_type_id = ... or "delivery") remains in GameEngine._ensure_location_mission_offers(), but it does not reintroduce legacy types and is never exercised under the current registry.
PART 1 — Hardcoded Type Sweep
Search scope: src/
1.1 "escort" matches
Result: No matches in src/
Classification: N/A
Conclusion: Escort is not referenced anywhere in the source tree.
1.2 "recovery" matches
src/world_state_engine.py 169: "recovery_only": bool(entry.get("recovery_only", False)), 933: and not bool(item.get("recovery_only"))
File: src/world_state_engine.py
Context: Situation/event flags (recovery_only) for world state, not mission types.
Classification: D) Harmless string (world state flag, non-mission)
Conclusion: Not a mission type; safe.
1.3 "bounty" matches
src/game_engine.py 4179: # Bounty missions can be evaluated here if needed, but all evaluation goes through evaluate_active_missions() 5082: "bounty_hunter": "Bounty Hunter",src/mission_factory.py 118: # Future types (e.g., bounty) should be added here when their creators exist.src/mission_registry.py 22: # ... (e.g., bounty) can be added... 33: #     mission_type_id="bounty", ...src/mission_manager.py 377: # Other mission types (bounty, etc.) - not implemented yetsrc/integration_test.py 443–466: test code creating a bounty missionsrc/npc_ship_generator.py 26: "bounty_hunter": {"MIL": 80, "CIV": 20},
Classification:
Comments / docs / tests: D) Harmless strings
npc_ship_generator role label "bounty_hunter": independent of mission generation.
Conclusion: Bounty is not part of the active mission generation path; only referenced in comments, tests, and NPC roles.
1.4 _mission_candidates matches
Result: No matches in src/
Conclusion: _mission_candidates() has been removed; it no longer exists.
1.5 create_mission( matches
src/mission_factory.py 10:def create_mission(...)src/cli_test.py, src/integration_test.py 93, 254, 352, 362, 378, 410, 461: test/CLI helper calls
File: src/mission_factory.py
Context: Generic mission creation function (now only used by tests/CLI helpers, not by GameEngine).
Classification: A) Generation logic, but not reached from the runtime mission offering path.
No references in game_engine.py or other runtime generation code.
Conclusion: create_mission() exists, but no production path uses it for mission offering; it cannot generate escort/recovery anymore.
1.6 mission_type = matches
All in src/ are either:
Factory assignment (structured, non-legacy):
  src/mission_factory.py   36: mission_type=mission_type,  256: mission_type="delivery",  267: mission_type="delivery",
Display / logging:
run_game_engine_cli.py reads mission.get("mission_type", ...).
mission_manager.py logs mission.mission_type.
Tests/validators set mission_type="delivery" or "bounty" in test code only.
Classification:
Factory assignments for delivery: A) generation logic (intended, structured).
CLI/tests: B) display logic / D) test-only.
1.7 mission_type_id = matches
src/game_engine.py 1585: mission_type_id = mission_type if isinstance(mission_type, str) and mission_type else "delivery"src/mission_registry.py 26, 33: mission_type_id="delivery" (registry entries only)src/mission_generator.py 42, 66: loop variables inside weighting logic
The key one (generation):
File: src/game_engine.py, _ensure_location_mission_offers()
Line: ~1585
Context:
    mission_type, _ = select_weighted_mission_type(...)    mission_type_id = mission_type if isinstance(mission_type, str) and mission_type else "delivery"
Classification: A) generation logic
Note: This is a defensive fallback to "delivery" if the weighted selector returns None or a falsy value. Given:
implemented_candidates is non-empty
select_weighted_mission_type only returns a type from candidates (or None if all weights 0)
Registry currently only includes "delivery"
this fallback is effectively unused, but it does exist in code.
Others:
In registry + mission_generator: D) internal helper / schema, no hardcoded mission types beyond "delivery" in the registry.
1.8 mission_type == matches
src/mission_manager.py 362: if mission.mission_type == "delivery":
File: src/mission_manager.py
Context: Evaluation logic for mission completion (delivery only).
Classification: Evaluation logic, not generation.
Conclusion: Safe; only checks delivery missions.
1.9 mission_type in [ matches
Result: No matches in src/
Conclusion: No multi-type hardcoded lists remain.
1.10 fallback matches
Mission-related occurrences:
In mission_factory.py:
Comments about target selection fallback:
Fallback to same-system if no reachable systems.
Fallback to inter-system if no alternative destination.
Classification: Deterministic routing for target selection, not mission type selection.
In other files: law, market, reaction, etc.
All non-mission-type related.
Explicit check: No "fallback" around mission_type selection except the mission_type_id = ... or "delivery" assignment already discussed above (which doesn't contain the word fallback).
1.11 default_mission matches
Result: No matches in src/
Conclusion: No default_mission code exists.
1.12 mission_contact_seed matches
src/game_engine.py 1618: mission.mission_contact_seed = f"...|{mission.mission_id}|contact" 1640–1699, 5884–5893, 6208–6235: NPC lookup / elevation logicsrc/mission_core.py 77–82: derive NPC-MSN id for Bar mission giverssrc/mission_entity.py 65, 206: field definition + serialization
Classification: B) Bar NPC presentation logic
Conclusion: Only used to:
Create Tier 1 Bar mission_giver NPCs
Map NPC-MSN IDs back to missions
No mission-type-specific branching (so escort/recovery are not specially handled)
PART 2 — mission_generator.py Integrity Check
File: src/mission_generator.py
Defines its own mission type list?
No. It only operates on eligible_missions passed in from the caller.
Contains hardcoded mission types?
No. The only use of mission_type_id is via _mission_type_id(mission) which reads from the candidate dict in game_engine / registry.
Only performs weighted selection from provided candidates?
Yes. Selection is:
Build base weights from mission["base_weight"]
Apply modifiers
Call _weighted_pick(weighted_items, rng)
Fallback to "delivery" internally?
No. If total weight <= 0, _weighted_pick returns None. No type string constants are used inside the file.
References escort or recovery?
None. Grep finds no mentions.
Conclusion: mission_generator.py is now a pure weighted-selection helper with no embedded mission-type knowledge.
PART 3 — mission_factory.py Authority Check
File: src/mission_factory.py
CREATOR_BY_TYPE exists?
Yes:
    CREATOR_BY_TYPE: Dict[str, Any] = {        "delivery": "create_delivery_mission",  # marker only        # Future types (e.g., bounty) should be added here when their creators exist.    }
Only implemented mission types present?
Yes. Only "delivery" is listed. Comment notes future addition of bounty.
Legacy create_mission() routing for unstructured types?
create_mission() still exists, but no runtime generation path calls it:
All create_mission( call sites are in tests (integration_test.py, cli_test.py) and not in game_engine.py.
GameEngine._ensure_location_mission_offers() routes only to create_delivery_mission() and raises if mission_type_id != "delivery".
Conclusion: No production routing of unstructured legacy types; create_mission() is effectively test-only now.
Any switch/if chain referencing escort or recovery?
No. Grep finds neither in mission_factory.py.
PART 4 — GameEngine._ensure_location_mission_offers() Generation Path
File: src/game_engine.py (excerpt around 1491–1615)
Key points:
Candidates loaded exclusively from mission_registry:
  from mission_registry import mission_type_candidates_for_source  ...  candidates = mission_type_candidates_for_source(source_type=source_type)
Filtering uses CREATOR_BY_TYPE:
  implemented_candidates = []  for row in candidates:      mt_id = str(row.get("mission_type_id", "") or "")      if mt_id in CREATOR_BY_TYPE:          implemented_candidates.append(row)      else:          # log skipped_unimplemented_type  if not implemented_candidates:      raise ValueError(...)
No reference to _mission_candidates():
Confirmed via grep: _mission_candidates does not exist in src/.
No fallback if registry returns empty other than raising ValueError:
If implemented_candidates is empty ? explicit ValueError with clear message.
String comparisons:
Only if mission_type_id == "delivery" to route into create_delivery_mission().
No == "escort" or == "recovery" anywhere in this method.
Defensive fallback assignment:
  mission_type, _ = select_weighted_mission_type(...)  mission_type_id = mission_type if isinstance(mission_type, str) and mission_type else "delivery"
This is a defensive fallback to "delivery" if the weighted selector returns None or non-string.
With the current registry (only "delivery"), mission_type will always be "delivery"; the fallback is not exercised.
However, the assignment is present and should be noted.
PART 5 — NPC Spawn Audit (Bar Only)
Search: "Mission Contact (" and "NPC-MSN"
Files: src/game_engine.py, src/mission_core.py
Usage patterns:
In mission_core.py::list_offered():
   if location_type == "bar" and mission.mission_contact_seed is not None:       npc_hash = hashlib.md5(mission.mission_contact_seed.encode()).hexdigest()[:8]       giver_npc_id = f"NPC-MSN-{npc_hash}"       row["giver_display_name"] = f"Mission Contact ({mission.mission_type})"
Classification: B) Display logic / NPC spawn at Bar
No mission_type branching: Only uses mission.mission_type as part of display name.
In game_engine.py:
When creating missions, for all generated missions:
     mission.location_id = location_id     mission.mission_contact_seed = f"{self.world_seed}|...|{mission.mission_id}|contact"
In NPC resolution / elevation code:
Uses mission_contact_seed and NPC-MSN-{hash} both to create and to find the mission giver NPC.
No mission_type-based conditionals; constraints on types now come exclusively from the registry + CREATOR_BY_TYPE.
Conclusion:
NPC generation happens after mission creation and purely off mission_contact_seed, not mission type.
Because only delivery is generated now, Bar NPC mission_givers can only exist for delivery missions.
No legacy mission-type-based NPC spawn logic remains.
PART 6 — Deterministic Authority Confirmation
1) Is there exactly ONE mission type source of truth?
Yes.
Mission types for generation are defined in src/mission_registry.py via _MISSION_TYPES.
GameEngine._ensure_location_mission_offers() always calls mission_type_candidates_for_source(source_type) and then filters via CREATOR_BY_TYPE.
There is no other candidate list or mission-type table in the generation path.
2) Can escort or recovery be generated anywhere?
No.
escort / recovery do not appear anywhere in src/ except recovery_only world-state flags (non-mission) and are absent from mission_registry.
No generation code references those strings.
create_mission() is only invoked in tests/CLI test helpers, not in production generation paths.
3) Can any mission type be generated without being present in mission_registry AND CREATOR_BY_TYPE?
No.
Candidates come only from mission_registry.mission_type_candidates_for_source.
They are further filtered to mt_id in CREATOR_BY_TYPE.
If filtering yields zero candidates ? ValueError (no fallback).
If select_weighted_mission_type somehow returns an mt_id not in CREATOR_BY_TYPE, another ValueError is raised (has no creator in CREATOR_BY_TYPE).
Thus, a mission type must be present in both mission_registry and CREATOR_BY_TYPE to be creatable.
4) Is there any silent fallback to delivery?
No silent fallback in selection or registry.
The only fallback-like code is:
    mission_type_id = mission_type if isinstance(mission_type, str) and mission_type else "delivery"
This is a defensive default in case select_weighted_mission_type returns None or non-str; combined with:
implemented_candidates being non-empty,
weighted_items built from those candidates,
In practice, this fallback is not exercised. There is:
No hidden or alternative path that silently converts other types into delivery.
All other failure modes raise ValueError, not fallback.
5) Is mission generation deterministic for a fixed seed?
Yes.
RNG for mission generation is GameEngine._mission_rng_for_location(location_id, turn=None), seeded with world_seed, current_system_id, current_destination_id, and location_id.
mission_generator.select_weighted_mission_type() uses that RNG and only deterministic operations.
create_delivery_mission() uses that RNG for target selection and cargo payload deterministically.
Registry content and CREATOR_BY_TYPE mappings are static and not stateful.
Therefore, for a fixed world seed and same player state, mission offerings are deterministic.
Final Verdict — Legacy Mission Purge Completeness
Section-by-section:
Hardcoded type sweep:
No escort or mission-type recovery in generation code.
_mission_candidates() removed.
No static mission type arrays in game_engine.py; the only list of mission types is the new registry in mission_registry.py (by design).
No weighted selection tables contain escort/recovery.
mission_generator.py:
Clean; no hardcoded types, no fallbacks, no escort/recovery.
mission_factory.py:
CREATOR_BY_TYPE exists and only contains "delivery".
create_mission() remains but is not used by runtime generation.
No escort/recovery references.
game_engine generation path:
Uses mission_registry + CREATOR_BY_TYPE exclusively.
No _mission_candidates(), no escort/recovery, no silent type mapping.
NPC spawn (Bar):
Tied to mission_contact_seed and location_type "bar", not mission_type.
With only delivery generated, Bar NPCs present delivery missions only.
Overall Purge Verdict: PASS
Escort and recovery cannot be generated.
Only mission types present in both mission_registry and CREATOR_BY_TYPE are creatable (currently delivery).
No static mission type lists remain in game_engine (replaced by the registry).
No silent legacy fallbacks to escort/recovery or other types; the only fallback to "delivery" is a defensive guard that does not reintroduce legacy behavior.