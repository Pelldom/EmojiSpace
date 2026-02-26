Implemented
1) Combat Resolution Structure
CombatResult structure (src/combat_resolver.py, CombatResult dataclass)
Fields present:
outcome: OutcomeName ("destroyed" | "escape" | "surrender" | "max_rounds")
rounds: int
winner: Optional["player" | "enemy" | "none"]
final_state_player: dict
final_state_enemy: dict
log: list[dict] (per-round details incl. actions, attacks, hull, escape/destruction metadata)
tr_player: int, tr_enemy: int
rcp_player: int, rcp_enemy: int
destruction_event: Optional[dict]
Built in resolve_combat when destruction occurs; includes at least:
player_destroyed: bool
enemy_destroyed: bool
requires_external_insurance_resolution: bool (set when player destroyed)
surrendered_by: Optional[SideName]
salvage_modules: list[dict[str, Any]]
combat_rng_seed: int
Not present in CombatResult:
No encounter_id field
No system_id field
No direct destroyed_ship payload; that is passed to resolve_salvage_modules at generation time, not returned.
Where combat is considered “finished” (src/game_engine.py)
Non-interactive combat:
_resolve_encounter_combat(self, spec) calls resolve_combat(...) and receives a CombatResult.
After combat:
Final player hull/degradation are applied back to player_ship.persistent_state using combat.final_state_player.
The method returns the CombatResult.
Combat is “finished” at that return point; no further combat rounds or hard-stops.
Interactive / step-based combat:
_initialize_combat_session(...) sets up self._pending_combat (holds combat_id, encounter_id, ship states, TR/RCP, combat_rng_seed, etc.).
_execute_combat_action(context, payload) calls resolve_combat_round(...).
When round_result["combat_ended"] is True:
A CombatResult is constructed from pending + final CombatStates.
combat_application.apply_combat_result(...) is invoked.
If combat_result.winner == "player" and combat_result.outcome == "destroyed", _apply_post_combat_rewards_and_salvage(...) is called.
_pending_combat is cleared and context.hard_stop = False.
Method returns; at this point the engine considers combat fully resolved.
2) Encounter Subtype Access
Encounter subtype & metadata (src/encounter_generator.py, EncounterSpec, generate_encounter)
EncounterSpec fields:
encounter_id
subtype_id
emoji
posture
initiative
allows_betrayal
threat_rating_tr
participant_templates
default_flags
reward_profile_id (selected via select_reward_profile)
npc_response_profile
selection_log (nested logs for subtype selection, TR assignment, reward profile pick).
Where the engine sees subtype metadata:
generate_encounter(...) returns an EncounterSpec built from data/encounter_types.json:
default_flags and reward_profiles from JSON are validated and embedded.
GameEngine receives this EncounterSpec when an encounter is generated and routed (e.g., in travel/encounter flows), so at encounter start it has access to:
spec.subtype_id
spec.default_flags
spec.reward_profile_id
spec.threat_rating_tr
Subtype metadata preservation:
During encounter lifetime, EncounterSpec is held in the active encounter structures (e.g., _active_encounters / encounter routing) and passed into resolver paths like _resolve_encounter_combat.
selection_log also preserves the raw subtype JSON entry (via IDs and logs) so the mapping from subtype ? reward profiles / flags is traceable.
self._pending_combat does store encounter_id but does not directly embed subtype_id, default_flags, or reward_profile_id; those remain on the original EncounterSpec (reachable via the active encounter registry, not via CombatResult).
3) Reward Trigger Points
Where materialize_reward() is called:
src/game_engine.py
Around line 2517 in _apply_conditional_rewards (name inferred from context):
reward_payload = materialize_reward(spec, system_markets, str(self.world_seed))
applied = apply_materialized_reward(player=self.player_state, reward_payload=reward_payload, context="game_engine")
Event logged under stage "conditional_rewards", subsystem "reward_applicator".
src/simulation_controller.py
Uses materialize_reward(encounter, [_market_payload(...)], str(self._world_seed)), followed by apply_materialized_reward(...).
Trigger timing:
In GameEngine:
Reward materialization is tied to the encounter resolution path, not directly to the combat stepper.
It is invoked in the “conditional reward pipeline” after an encounter decision/resolution, using EncounterSpec (and its reward_profile_id / threat_rating_tr), not CombatResult.
In SimulationController:
Triggered after resolving an encounter in the simulation loop, again based on encounter metadata, not combat output.
Post-combat reward handler:
src/game_engine.py defines and uses:
_apply_post_combat_rewards_and_salvage(context, npc_ship_dict, encounter_id) (function name seen in call).
This is called when:
combat_result.winner == "player" AND combat_result.outcome == "destroyed" in the interactive combat path.
This function is the designated post-combat handler, responsible for post-combat rewards & salvage orchestration on the engine side.
4) Salvage Integration
Where resolve_salvage_modules() is called:
src/combat_resolver.py:
In resolve_combat(...), in the destruction branch:
When enemy_destroyed is True, calls:
resolve_salvage_modules(world_seed=world_seed, system_id=system_id, encounter_id=f"{combat_id}_enemy_destroyed", destroyed_ship=enemy_ship)
Returned modules are stored in:
round_log["salvage_modules"]
CombatResult.salvage_modules.
src/game_engine.py:
In older non-stepper combat path (_process_combat_round / internal combat loop) and in the newer step-based _execute_combat_action:
When outcome == "destroyed" and winner == "player", calls:
resolve_salvage_modules(world_seed=str(self.world_seed), system_id=self.player_state.current_system_id, encounter_id=f"{combat_id}_enemy_destroyed", destroyed_ship=enemy_ship_dict)
The resulting list is then attached to the CombatResult.salvage_modules.
destroyed_ship origin:
In combat_resolver.resolve_combat:
destroyed_ship is the assembled enemy ship (dictionary from assemble_ship) plus module instances.
In GameEngine._execute_combat_action:
destroyed_ship is enemy_ship_dict from self._pending_combat (NPC ship dict with module_instances etc.).
src/salvage_resolver.py expects destroyed_ship as a dict with module_instances; this contract is adhered to in both callers.
5) Player Module Inventory
Where modules live:
Installed ship modules are not on PlayerState directly; they are on ShipEntity / ship records (outside this scope).
PlayerState has:
salvage_modules: List[Dict[str, Any]] — intended as a holding area “from combat (stored until installed via shipdock)” (per field comment).
cargo_by_ship: Dict[str, Dict[str, int]] — for goods, not ship modules.
Salvage modules returned by resolve_salvage_modules are currently only attached to CombatResult.salvage_modules and not persisted into PlayerState.salvage_modules in game_engine.py.
Functions to add module instances to the player (in scoped files):
reward_applicator.apply_materialized_reward(...):
Mutates:
player.credits
player.cargo_by_ship["active"][sku_id] (goods, not modules)
There is no function here that appends to player.salvage_modules or installs modules.
Within the audited files (player_state.py, reward_applicator.py, game_engine.py, combat_resolver.py, salvage_resolver.py), there is no dedicated function that:
Takes a list of salvage module dicts and stores them to PlayerState or to a ship’s installed_modules.
6) Stolen Reward Handling
Stolen computation (src/reward_materializer.py):
RewardResult includes stolen_applied: bool.
_resolve_stolen_applied(profile, seed_string):
Implements:
"always" ? True
"none" ? False
"probabilistic" ? compares a deterministic float against stolen_probability.
RewardResult.log records stolen_roll.
Stolen propagation into player / law system:
apply_materialized_reward(player, reward_payload, ...):
Ignores stolen_applied entirely.
Only:
Adds reward_payload.credits to player.credits.
Adds reward_payload.quantity of reward_payload.sku_id to player.cargo_by_ship["active"].
No field like stolen_goods or flags on cargo are set here.
No connection is visible in these files from stolen_applied to:
PlayerState.heat_by_system
reputation_by_system
Any law/notoriety consequences.
consequences.json is not referenced in the audited modules; any linkage (if present) lies outside this scope.
7) Cargo Capacity
Cargo capacity representation:
PlayerState:
Has cargo_by_ship and warehouses (with per-destination capacity and goods).
Capacity for ships is handled via hull/ship data (assemble_ship) rather than on PlayerState itself.
No method in PlayerState enforces cargo capacity constraints when mutating cargo_by_ship.
Capacity validation during reward application:
apply_materialized_reward(...):
Simply increments cargo counts; no check for:
Max physical/data cargo capacity.
Any overflow or rejection path.
As a result, reward application is capacity-unaware in the current pipeline.
8) Encounter Types & Reward Profiles Alignment
data/encounter_types.json:
Each subtype defines:
default_flags (e.g., "salvage_possible", "piracy_context", "anomaly_discovery_possible", "civilian_target", etc.).
reward_profiles: array of { "reward_profile_id", "weight" }.
encounter_generator.load_encounter_types() validates:
default_flags only contain allowed values (including "salvage_possible").
reward_profiles shape and weights are correct.
data/reward_profiles.json:
Each profile defines:
reward_kind ("cargo", "credits", "mixed", "none").
quantity_band, credit_range (when applicable).
stolen_behavior (and stolen_probability for probabilistic).
load_reward_profiles() validates both structure and semantics.
Alignment:
generate_encounter(...):
Picks reward_profile_id from subtype["reward_profiles"] (if any).
Stores it on the EncounterSpec.
materialize_reward(...):
Uses spec.reward_profile_id to look up the profile in reward_profiles.json.
Uses spec.threat_rating_tr to scale quantity.
Structurally, reward_profiles usage aligns with encounter_types.json and reward_profiles.json schemas.
Partially Implemented
1) Combat ? Reward ? Salvage Pipeline
Combat ? Salvage generation:
Fully implemented:
Destruction produces destruction_event + salvage_modules in CombatResult.
resolve_salvage_modules(...) is wired and deterministic.
Combat ? Post-combat reward & salvage application:
GameEngine has _apply_post_combat_rewards_and_salvage(...) and calls it when:
Player wins and outcome == "destroyed".
However, based on docs/combat_system_audit.md and code in game_engine.py:
CombatResult.salvage_modules are generated but not applied to PlayerState or any ship inventory in the engine.
There appears to be no direct write to player.salvage_modules in the audited files.
Therefore:
Salvage generation is implemented, but salvage application to player state is missing (see also the “Missing” section).
Encounter subtype flags vs. salvage behavior:
encounter_types.json:
Hostile subtypes like "pirate_raider", "blood_raider", "derelict_ship" have default_flags containing "salvage_possible".
Combat/salvage code:
Does not inspect default_flags or salvage_possible directly.
Salvage is triggered purely by combat destruction (enemy destroyed) and the presence of a destroyed ship object, not by subtype flags.
This means:
Salvage flagging in encounter_types.json is validated and stored (on EncounterSpec.default_flags) but not consulted by the salvage pipeline in the audited code.
2) Reward Trigger Semantics
Where rewards are tied to encounters:
Rewards are driven by:
EncounterSpec.reward_profile_id populated at encounter generation.
Conditional reward pipeline (_apply_conditional_rewards) using that EncounterSpec.
Coupling to combat outcome:
There is no direct path in the audited code that:
Looks at CombatResult (e.g., winner, outcome, destruction_event) when choosing whether to call materialize_reward.
Reward qualification logic (if any) seems to be based on encounter outcome / decision semantics, not on CombatResult.
So:
Rewards are structurally integrated, but their dependency on actual combat success/failure is not explicit in the engine modules examined.
3) Stolen Rewards vs. Law/Notoriety
Implemented:
stolen_applied is computed deterministically and logged in RewardResult.
Reward profiles in reward_profiles.json clearly distinguish "always", "none", "probabilistic" stolen behavior and probabilities.
Not fully integrated:
The law/notoriety subsystems (e.g., law_enforcement.enforcement_checkpoint) inspect cargo/heat, but:
In the audited files, there is no linkage from RewardResult.stolen_applied to:
Marking individual cargo items as stolen.
Adjusting PlayerState.heat_by_system or similar fields.
This creates a semantic gap between the reward design (stolen semantics) and legal consequences.
Missing
1) Resolver Router
The requested resolver_router.py file is not present in the workspace (read attempt failed).
Any routing logic between encounter types, resolvers, and post-combat handling must currently live in:
game_engine.py
encounter_generator.py
Possibly other controllers (e.g., cli_playable.py, simulation_controller.py)
There is no dedicated resolver-router module in scope.
2) Salvage Application to Player Inventory
No implementation found (within scoped files) that:
Takes CombatResult.salvage_modules or resolve_salvage_modules(...) output and:
Writes them into PlayerState.salvage_modules or
Installs them on a ship’s module_instances list.
This is corroborated by:
docs/combat_system_audit.md and docs/STRUCTURAL_VERIFICATION_PHASE4_12.md, which explicitly flag salvage as generated but never materialized.
Result:
Salvage is a logged-only artifact at present; the player never actually receives the modules in persistent state.
3) Capacity-Aware Reward Application
apply_materialized_reward(...):
Has no cargo capacity checks:
It will happily increase cargo_by_ship["active"][sku_id] without reference to:
Ship physical/data cargo capacity.
Any per-ship limits defined by hull/module data.
No other audited function performs capacity validation for reward-based cargo addition.
This is an architectural inconsistency with the likely expectation from ship/market contracts that capacity should constrain cargo.
4) Stolen Rewards ? Law/Notoriety Integration
No audited code:
Reads RewardResult.stolen_applied and uses it to:
Mark cargo as “stolen”.
Drive law enforcement behavior or notoriety increases.
reward_profiles.json clearly encodes design intent:
Some profiles (civilian_manifest, raider_loot, derelict_salvage, etc.) are meant to be stolen or risky.
This is an architectural contradiction:
Design encodes nuanced stolen behavior.
Implementation applies rewards as value-neutral cargo/credits without any downstream legal consequence.
5) Explicit Post-Combat Reward Mapping from Reward Profiles
While EncounterSpec.reward_profile_id is set from encounter_types.json and reward_profiles.json, and materialize_reward is used in the generic encounter pipeline:
The audited code does not show:
A dedicated mapping from specific combat outcomes (e.g. "enemy destroyed" in "pirate_raider") to reward profiles in a combat-aware way after interactive combat.
Rewards triggered via _apply_conditional_rewards appear to be encounter-level, not explicitly tied to CombatResult.
6) Player Module Add / Install Functions (Within Scope)
Within the audited modules, there is no function that:
Accepts a list of module instances (e.g., salvage),
Performs validation (e.g., compatibility, capacity, slot types),
And installs them on:
PlayerState.salvage_modules, or
A ShipEntity’s installed modules.
Any such logic likely resides in shipdock / ship management modules (outside this audit’s file list), but it is not part of the combat ? reward ? salvage pipeline as currently wired.
7) Dead or Unreachable Reward/Salvage Paths
Within the audited scope:
Reward materialization calls (materialize_reward) are reachable:
GameEngine and SimulationController both call them in active flows.
Salvage generation calls (resolve_salvage_modules) are reachable:
Combat destruction branches in both resolve_combat and interactive combat.
However:
Application of salvage (i.e., turning CombatResult.salvage_modules into persistent player inventory) is absent, making that conceptual part of the pipeline effectively dead.
Additionally, the reliance on stolen_applied in design without any application logic is a form of dead metadata with respect to law/notoriety.
High-Level Architectural Notes (No Solutions Proposed)
CombatResult is well-structured for downstream consumers (outcome, final states, TR/RCP, destruction, salvage, RNG seed) but does not embed encounter/system identity; those remain in EncounterSpec and engine context.
Encounter subtype metadata (flags and reward profiles) is properly loaded, validated, and embedded in EncounterSpec, but is not consistently consulted by combat/salvage/reward handlers after combat.
Reward profiles and stolen behavior are richly modeled in data (reward_profiles.json) and faithfully materialized in RewardResult, but the mutation path treats all rewards identically (no stolen vs. legitimate distinction, no law consequences).
Salvage generation is robust and deterministic (dedicated RNG streams per destroyed ship), but its integration stops at CombatResult, with no audited code applying salvage to player state.