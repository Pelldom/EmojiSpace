phase_7_12B_encounter_architecture_audit.md
Summary of Current Encounter System
Encounter definition (data):
Ship encounters are defined in encounter_types.json and validated/loaded by encounter_generator.py.
Each entry is a subtype object (subtype_id) with posture, initiative, flags, reward profiles, and an npc_response_profile.
Contracts:
design/encounter_types_schema_contract.md defines required fields and deterministic selection rules.
design/encounter_generator_contract.md specifies enforcement-based weighting and clamping.
Encounter generation:
encounter_generator.generate_encounter builds an EncounterSpec from:
Subtype selection: select_subtype (authority enforcement and situation/world-state biases).
Threat rating selection: assign_tr based on allowed_TR_range.
Reward profile selection: select_reward_profile.
Travel-time generation:
generate_travel_encounters rolls encounters for a travel leg based on population and a deterministic decay curve.
travel_context.mode ("in_system" | "system_arrival" | "local_activity") affects both authority weighting and the number of possible rolls.
Interaction dispatch layer:
interaction_layer.py implements the Interaction Layer described in design/interaction_layer_contract.md.
It:
Provides allowed action sets based on initiative phase (initial vs post-contact) and posture.
Validates player action against this allowed set.
Calls reaction_engine.get_npc_outcome for actions that require NPC reaction.
Maps NPC outcomes to resolver handler types (HANDLER_COMBAT, HANDLER_PURSUIT_STUB, HANDLER_LAW_STUB, etc.).
It does not mutate world state or resolve combat/law outcomes directly.
Reaction evaluation:
reaction_engine.py implements the logic contract in design/reaction_evaluation_contract.md.
For actions like intimidate, bribe, and surrender (plus some other contact actions), it:
Computes banded player/NPC scores and TR deltas.
Applies deterministic modifiers to a response weight table (npc_response_profile).
Selects an outcome deterministically via deterministic_weighted_choice.
Combat and pursuit resolution:
Combat:
Implemented in combat_resolver.py as a multi-round combat engine over banded stats.
Used by:
game_engine.GameEngine._resolve_encounter_combat (and interactive combat session flow).
simulation_controller.SimulationController (one-shot simulation path).
Pursuit:
Implemented in pursuit_resolver.py as a single-roll escape check based on:
Speeds, engine bands, TR bands, pilot skills, cloaking/interdiction, and hull damage.
Called by:
game_engine.GameEngine._resolve_encounter when the interaction layer yields a pursuit handler.
SimulationController._resolve_encounter for the simpler simulation path.
Law enforcement:
Law enforcement encounters are governed by design/law_enforcement_contract.md and implemented in law_enforcement.py.
They are not generated via encounter_generator; rather:
law_enforcement.enforcement_checkpoint determines if an enforcement event is triggered.
resolve_option interprets player options (SUBMIT, FLEE, ATTACK, BRIBE) and can set route_to_handler = "combat" | "pursuit" to signal the main engine to use unified combat/pursuit systems.
Engine dispatch and encounter resolution entry points:
Main game engine (game_engine.py):
Travel:
_execute_travel_to_destination calls generate_travel_encounters to produce a list of EncounterSpec instances.
Encounters are stored in self._pending_travel["remaining_encounters"].
Encounter resolution entry points:
_execute_encounter_action (older “active_encounters” path).
_execute_encounter_decision for the travel-based pending-encounter system.
Both delegate to _resolve_encounter for a specific EncounterSpec and player decision.
_resolve_encounter:
Calls interaction_layer.dispatch_player_action with:
spec (EncounterSpec),
player_action,
world_seed,
banded reputation and notoriety.
Examines dispatch.next_handler and:
For REACTION: calls reaction_engine.get_npc_outcome (again) and logs.
For PURSUIT: calls pursuit_resolver.resolve_pursuit.
For COMBAT / COMBAT_STUB:
Either initializes an interactive combat session (pending combat state) or runs legacy one-shot combat via _resolve_encounter_combat.
For LAW_STUB: runs a customs-style law enforcement checkpoint using _run_law_checkpoint.
After resolver outcome, applies non-combat rewards (if any) using reward_materializer.materialize_reward plus reward_applicator.apply_materialized_reward, gated by _reward_qualifies.
Combat rewards are handled elsewhere (post-combat).
Simulation controller (simulation_controller.py):
Provides a simpler CLI/game-harness entry point:
_execute_travel_to_destination:
Uses resolve_travel.
Immediately generates one system-arrival encounter via generate_encounter.
Immediately calls _resolve_encounter(encounter, action) with a single player action (often "ignore").
_resolve_encounter (simulation variant) has similar shape:
Uses interaction_layer.dispatch_player_action to determine handler.
On HANDLER_PURSUIT_STUB: calls resolve_pursuit with fixed, synthetic ship stats.
On HANDLER_COMBAT_STUB: runs a short combat (resolve_combat) and applies results via combat_application.apply_combat_result.
Then always calls reward_materializer.materialize_reward + reward_applicator.apply_materialized_reward.
Resolver Flow Diagram (Text-Based)
High-Level Encounter Flow (Main Game Engine)
Travel:
GameEngine._execute_travel_to_destination
? travel_resolution.resolve_travel
? encounter_generator.generate_travel_encounters (0..N EncounterSpec)
? store in pending_travel.remaining_encounters.
Per-encounter resolution:
For each EncounterSpec:
_resolve_encounter(context, spec, player_action, player_kwargs):
dispatch = interaction_layer.dispatch_player_action(spec, player_action, world_seed, ignore_count=0, reputation_band, notoriety_band)
handler = dispatch.next_handler determines resolver:
END:
Encounter terminates; no resolver beyond logging.
Reward gating still runs; if qualifies and non-combat, reward is materialized/applied.
COMBAT / COMBAT_STUB:
If interactive:
_initialize_combat_session ? pending combat session (combat actions resolved via separate command).
Else:
combat = _resolve_encounter_combat(spec)
? combat_resolver.resolve_combat ? CombatResult.
Combat rewards/salvage handled later by _apply_post_combat_rewards_and_salvage (not in _resolve_encounter).
PURSUIT_STUB:
(pursuer_ship, pursued_ship) = _pursuit_ships_for_spec(spec)
pursuit = pursuit_resolver.resolve_pursuit(encounter_id, world_seed, pursuer_ship, pursued_ship)
Outcome (escape_success / escape_fail) is logged and used for reward gating and subsequent state transitions.
LAW_STUB:
law_outcome = _run_law_checkpoint(..., trigger_type=CUSTOMS, option_name)
Inside law_enforcement.resolve_option, route_to_handler may be set to "combat" or "pursuit" to delegate to unified resolvers.
REACTION (from interaction layer):
_resolve_encounter currently re-calls reaction_engine.get_npc_outcome for logging and outcome, independent of interaction-layer mapping.
Reward flow (non-combat):
qualifies = _reward_qualifies(dispatch, resolver_outcome, spec)
If qualifies and resolver != "combat":
reward_payload = reward_materializer.materialize_reward(spec, system_market_payloads, world_seed)
apply_materialized_reward(player_state, reward_payload, context="game_engine", enforce_capacity=False).
Simplified Simulation Flow
SimulationController._execute_travel_to_destination:
resolve_travel ? on success:
Generate single arrival encounter: generate_encounter.
_resolve_encounter(encounter, action):
dispatch_player_action (interaction layer) ? handler:
HANDLER_PURSUIT_STUB ? resolve_pursuit (synthetic ships).
HANDLER_COMBAT_STUB ? resolve_combat (short max_rounds) ? combat_application.apply_combat_result.
Always then calls materialize_reward + apply_materialized_reward.
1) Currently Defined Encounter Types and Subtypes
Encounter postures and initiatives (from contracts and data)
Postures (EncounterSpec.posture, authoritative in interaction_layer_contract.md and encounter_types_schema_contract.md):
neutral
authority
hostile
opportunity
Initiative (EncounterSpec.initiative, in encounter_generator.py and schema):
player
npc
Concrete subtypes (from data/encounter_types.json)
Current subtypes (all ship-encounter oriented):
civilian_trader_ship
Posture: neutral
Initiative: player
Flags: ["civilian_target", "trade_possible"]
Reward profiles: ["civilian_manifest"]
Interaction shape: neutral posture with simple intimidate/bribe blocks; no authority or pursuit semantics.
customs_patrol
Posture: authority
Initiative: npc
Flags: ["authority_actor"]
Reward profiles: [] (no encounter reward; consequences go through law system).
Includes a legacy government_bias field despite schema removing it (code still tolerates optional bias maps via _validate_optional_bias_map).
bounty_hunter
Posture: authority
Initiative: npc
Flags: ["authority_actor"]
Reward profiles: ["bounty_credit"]
Emphasizes hail/pursue/attack patterns.
pirate_raider
Posture: hostile
Initiative: npc
Flags: ["criminal_actor", "piracy_context", "salvage_possible"]
Reward profiles: ["pirate_loot"]
allows_betrayal: true enabling accept_and_attack in reaction outcomes.
Has situation_bias for "war".
blood_raider
Posture: hostile
Initiative: npc
Flags: ["criminal_actor", "salvage_possible"]
Reward profiles: ["raider_loot"]
Purely hostile response tables; no acceptance or bribe success.
derelict_ship
Posture: opportunity
Initiative: npc
Flags: ["salvage_possible", "anomaly_discovery_possible"]
Reward profiles: ["derelict_salvage"]
Response profile is effectively passive (ignore/ignore).
No additional encounter types or subtypes are currently defined in encounter_types.json.
2) Existing Resolver Types
From contracts and implementation:
Interaction/dispatch:
interaction_layer.dispatch_player_action:
Core “interaction resolver” / dispatcher for encounter-level actions.
Handler constants:
HANDLER_END
HANDLER_REACTION
HANDLER_COMBAT
HANDLER_COMBAT_STUB
HANDLER_LAW_STUB
HANDLER_PURSUIT_STUB
HANDLER_MARKET_STUB (stub only; not wired in engine flows)
HANDLER_MISSION_STUB (stub only)
HANDLER_EXPLORATION_STUB (stub only; exploration resolver lives in exploration_resolver.py)
Reaction evaluation:
Logical resolver: reaction_engine.get_npc_outcome:
Interprets intimidation, bribe, surrender, ignore/respond/hail.
Produces NPC outcome enums: accept, accept_and_attack, refuse_stand, refuse_flee, refuse_attack, plus some non-contract outcomes (ignore, hail, warn, attack, pursue) mapped back to contract outcomes when needed.
Combat:
combat_resolver.resolve_combat:
Full multi-round combat resolver over CombatState with crew, RPS, degradation, escape attempts.
Integrated via:
game_engine.GameEngine._resolve_encounter_combat.
Interactive session helpers (_initialize_combat_session, _process_combat_round, etc.).
simulation_controller.SimulationController legacy one-shot.
Pursuit:
pursuit_resolver.resolve_pursuit:
Single-roll chase/escape resolver, parameterized by TR/engine bands and modifiers.
Law enforcement:
law_enforcement.resolve_option and enforcement_checkpoint:
Enforcement-specific resolver, with PlayerOption enums and severity/penalty logic.
Has routing hooks (route_to_handler) to unified combat/pursuit systems but does not perform those resolutions itself.
Exploration / mining / salvage:
exploration_resolver.py, mining_resolver.py, salvage_resolver.py:
Resolve non-encounter exploration and salvage (not directly orchestrated by interaction_layer yet).
Salvage is used post-combat for loot (salvage_resolver.resolve_salvage_modules in combat_resolver).
Rewarding/loot:
reward_materializer.materialize_reward:
Pure function mapping an EncounterSpec and market snapshot to RewardResult via reward profiles.
reward_applicator.apply_materialized_reward:
Applies RewardResult to player state/inventory.
Combat salvage:
combat_resolver ? salvage modules via salvage_resolver.
Post-combat application through combat_application.apply_combat_result and game-engine post-combat handling.
3) Interaction Resolver Capabilities
Multiple player choices
Yes:
interaction_layer.allowed_actions_initial(spec) returns 2–3 actions depending on initiative:
NPC-initiative: [ignore, respond, attack].
Player-initiative: [ignore, hail, attack].
allowed_actions_post_contact(spec) returns posture-specific action sets:
Neutral: [end_encounter, intimidate, attack, respond, hail].
Authority: [end_encounter, intimidate, attack, comply, bribe, flee, surrender].
Hostile: [surrender, bribe, flee, attack].
Opportunity: [investigate, end_encounter, attack].
These lists are sorted ASCII before validation and logging, per contract determinism requirements.
Branching behavior
Branching at resolver level:
Player action ? (via dispatch_player_action) branches to:
End encounter.
Combat (or interactive combat session).
Pursuit.
Law enforcement.
(In principle) exploration/market/mission stubs.
For certain actions (ignore, respond, hail, intimidate, bribe, surrender), REACTION_REQUIRED_ACTIONS triggers a Reaction Evaluation step:
NPC outcome then branches to end, combat, or pursuit.
Within-encounter branching / multi-step:
The interaction layer tracks only:
Phase: "initial" vs "post_contact" based on ignore_count == 0.
ignore_count (but callers currently always pass 0).
It does not maintain an explicit interaction graph or node ID per encounter.
The “branching” is limited to:
Choosing from a flat set of available actions in that phase.
Resolver target and NPC reaction possibly returning control to the player with a reduced action set (per Reaction Evaluation contract, e.g. refuse_stand limiting actions to ignore/attack).
The engine (game_engine._resolve_encounter and SimulationController._resolve_encounter) invoke dispatch_player_action once per player command; they do not currently track or increment ignore_count, so ignore-escalation branches implemented in reaction_engine are not used in main flows.
Conclusion for Q3:
Multiple player choices: supported (per posture/phase).
Branching: present at the level of routing to resolvers and NPC reactions, but not a general multi-node interaction tree. The current structure is “single-step dispatch with posture-based allowed actions,” not a full branching dialogue graph.
Single-node only: not strictly single-node (because resolvers and reaction outcomes can change what happens), but there is no explicit multi-node interaction state within the Interaction Layer itself.
4) Escalation Mechanisms (Interaction ? Combat / Pursuit)
Interaction to combat
Direct player escalation:
player_action == "attack":
In interaction_layer.dispatch_player_action, this maps to HANDLER_COMBAT.
The main engine sees this handler and:
Either starts interactive combat (HANDLER_COMBAT) or
Runs legacy one-shot combat (HANDLER_COMBAT_STUB), depending on context.
Via Reaction Evaluation / NPC outcome:
In interaction_layer:
For REACTION_REQUIRED_ACTIONS (ignore/respond/hail/intimidate/bribe/surrender):
get_npc_outcome returns NPC outcome.
_npc_outcome_to_handler maps:
attack or accept_and_attack ? HANDLER_COMBAT.
In game_engine._resolve_encounter:
If handler == HANDLER_COMBAT or HANDLER_COMBAT_STUB, combat is invoked as above.
In law_enforcement:
resolve_option can set route_to_handler = "combat" when the player chooses ATTACK or when outcomes call for escalation; the engine is intended to route this into the unified combat system (outside the encounter layer).
Interaction to pursuit
Direct flee action:
player_action == "flee":
In interaction_layer.dispatch_player_action, maps to HANDLER_PURSUIT_STUB.
In game_engine._resolve_encounter:
handler == HANDLER_PURSUIT_STUB:
pursuer_ship, pursued_ship = _pursuit_ships_for_spec(spec) (engine-specific mapping).
pursuit_resolver.resolve_pursuit(...) is called.
Via Reaction Evaluation:
In interaction_layer:
NPC outcomes mapped to pursuit handler:
Outcome pursue (non-contract, mapped to contract refuse_flee) ? HANDLER_PURSUIT_STUB.
Contract-level refuse_flee also maps to pursuit via _npc_outcome_to_handler.
In law_enforcement:
resolve_option can set route_to_handler = "pursuit" for FLEE; the game engine’s law integration is designed to hand that off to the same pursuit resolver.
Conclusion for Q4:
There are explicit mechanisms for escalation:
Interaction ? combat: direct attack, or NPC outcomes (refuse_attack/accept_and_attack).
Interaction ? pursuit: direct flee, or NPC outcomes (refuse_flee/pursue), and law-enforcement FLEE behavior.
5) Reward Granting Behavior
Reward profiles and materializer
Encounter reward profiles:
Defined in reward_profiles.json with schema contract design/reward_profiles_schema_contract.md.
Each profile includes:
reward_profile_id, emoji, reward_kind, quantity_band, credit_range (if needed), stolen_behavior, stolen_probability.
Encounters:
encounter_generator.generate_encounter selects exactly one reward_profile_id (or None) deterministically from the subtype’s weighted list.
Materialization and application:
reward_materializer.materialize_reward(spec, system_markets, world_seed):
If spec.reward_profile_id is None: returns None (no reward).
If reward_kind == none: returns zero-quantity, zero-credits reward.
If reward_kind includes cargo:
Aggregates SKUs from system markets via aggregate_system_skus (produced/consumed/neutral).
Selects a SKU deterministically from the ASCII-sorted pool.
Resolves base quantity from quantity_band, multiplies by spec.threat_rating_tr.
If reward_kind includes credits:
Scales credits deterministically within the banded range.
Applies stolen_behavior with its own deterministic roll.
Application:
reward_applicator.apply_materialized_reward is called:
Directly in SimulationController._resolve_encounter (always, if reward exists).
In GameEngine._resolve_encounter for non-combat encounters that pass _reward_qualifies.
Direct vs profile-based rewards
Profile-based rewards:
All encounter rewards tied to reward_profile_id use reward_materializer and thus the reward_profiles schema.
Law enforcement, mission, and some exploration flows have separate reward schemas (mission reward profiles, etc.) but those do not flow through reward_materializer.
Direct/other reward flows:
Combat salvage:
combat_resolver uses salvage_resolver.resolve_salvage_modules to produce module drops independently of reward_profiles.
These are applied via combat_application.apply_combat_result and engine post-combat handlers.
Law enforcement:
Applies fines/confiscations as negative outcomes (not rewards).
Missions:
Use mission reward profiles with separate schema inside reward_profiles.json (reward_type: credits | goods | module | hull_voucher) and mission-specific determinism streams.
Conclusion for Q5:
Encounter rewards are primarily profile-based through reward_profiles + reward_materializer.
There is a mixed landscape overall:
Encounter rewards: via reward profiles.
Combat salvage: deterministic but via separate salvage resolver (not reward profiles).
Missions and law: own schemas and flows.
6) Determinism Enforcement
RNG implementation and seeding
Core deterministic RNG:
encounter_generator.deterministic_float(seed_string):
SHA-256 hashing of ASCII seed_string, using first 8 bytes as an integer.
Divides by 
2
64
2 
64
  to get a float in 
[
0
,
1
)
[0,1).
deterministic_weighted_choice(items, weights, seed_string):
Uses deterministic_float and cumulative weights for deterministic selection.
Encounter generator:
Subtype selection:
Seed: seed_string = f"{world_seed}{encounter_id}subtype".
Candidate list sorted ASCII by subtype_id before selection.
Threat rating TR:
Seed: seed_string = f"{world_seed}{encounter_id}tr".
Reward profile selection:
Seed: seed_string = f"{world_seed}{encounter_id}reward".
Profiles sorted ASCII by reward_profile_id.
Travel encounter rolls:
For each index i:
Seed: f"{world_seed}{travel_id}enc_roll_{i}".
Logging:
selection_log includes candidate weights, modifiers, enforcement flags, travel roll details, TR and reward-selection logs.
Reaction Evaluation:
reaction_engine.get_npc_outcome:
Outcome selection seed:
seed_string = f"{world_seed}{spec.encounter_id}{player_action}{ignore_count}".
Logs:
Baseline weights, effective outcomes, weights after modifiers, TR deltas, reputation/notoriety bands, and selected outcome.
Contract (reaction_evaluation_contract.md) also specifies:
Conceptual seed: seed = world_seed + stable_salt where stable_salt = encounter_id + action_type.
Pursuit:
pursuit_resolver.resolve_pursuit:
Seed: seed_string = f"{world_seed}{encounter_id}_pursuit".
Logs:
All deltas, hull-damage penalty, threshold before/after modifiers, roll, distribution.
Rewards:
reward_materializer:
Quantity seed: f"{world_seed}{spec.encounter_id}_qty".
SKU selection seed: f"{world_seed}{spec.encounter_id}_sku".
Stolen behavior seed: f"{world_seed}{spec.encounter_id}{spec.reward_profile_id}_stolen" (via base seed_string and suffix).
Credits seed: f"{world_seed}{spec.encounter_id}{spec.reward_profile_id}_credits".
Logs:
SKU pool size, base quantity, TR multiplier, final quantity, stolen and credit rolls.
Law enforcement:
_rng_for(world_seed, system_id, turn, checkpoint, action):
Derives a 32-bit integer hash from the token string, then uses random.Random(value).
Used for:
Inspection rolls (enforcement_checkpoint).
Bribery and other per-event stochastic checks.
Logging:
Inspection/logging rules explicitly required in law_enforcement_contract.md and implemented in law_enforcement.enforcement_checkpoint.
Combat:
CombatRng:
Uses Python random.Random(combat_rng_seed) with internal counter and per-roll logging.
In resolve_combat:
combat_rng_seed:
If passed explicitly, determinism is preserved across runs.
If not passed, defaults to secrets.randbits(64) ? non-deterministic by design.
The main game engine:
For _resolve_encounter_combat, does not currently pass a deterministic combat_rng_seed (it relies on internal default), so runtime combat is not fully deterministic unless higher-layer code seeds or wraps this.
Logging for reconstructibility
Encounter generator logs:
Candidate weights and modifiers for subtype and TR.
Travel roll inputs and results.
Interaction Layer logs:
Posture, subtype, phase, allowed actions, chosen action, NPC outcome and log, next handler.
Reaction Evaluation logs:
All inputs, banded values, modifier steps, seed and final outcome.
Pursuit resolver logs:
All bands, modifiers, roll, and final outcome.
Reward materializer logs:
SKU selection, quantity, TR multiplier, stolen/credit rolls.
Law enforcement logs:
Inspection and outcome fields sufficient to reconstruct enforcement.
Conclusion for Q6:
Determinism is strongly enforced for:
Encounter generation, travel encounter selection, reward profiles, reaction outcomes, pursuit, law enforcement.
Combat determinism depends on explicit combat_rng_seed usage; in some flows it is non-deterministic by default.
7) Encounter Flags: One-Time, Persistent, Context-Based
One-time-only / persistent flags
EncounterSpec fields (EncounterSpec in encounter_generator.py) include:
encounter_id, subtype_id, emoji, posture, initiative, allows_betrayal, threat_rating_tr, participant_templates, default_flags, reward_profile_id, npc_response_profile, selection_log.
default_flags:
Valid flags currently are:
civilian_target, authority_actor, criminal_actor, piracy_context, salvage_possible, trade_possible, mission_possible, anomaly_discovery_possible.
There are no flags defined or used for:
“one-time only encounter”.
“persistent encounter” (e.g. persistent NPC ship).
Engine-side:
GameEngine and SimulationController treat EncounterSpec as a stateless event; they do not persist a per-encounter identity beyond logging and pending-queue state.
There is no infrastructure to mark that a given encounter subtype or specific encounter_id should not reoccur in future travel legs or sessions.
Context-based encounters (travel vs local activity)
Travel context:
generate_travel_encounters accepts travel_context dict with mode:
"in_system" (default when travel_context is None),
"system_arrival",
"local_activity".
Posture weighting:
For authority postures:
Always add enforcement_strength.
Additional enforcement_strength bonus only when travel_context.mode == "system_arrival".
Encounter roll cap:
cap = population * 2 normally.
For local_activity mode:
Cap is forced to 1 encounter roll (no chaining).
Data-level context:
There are no explicit context or mode fields in encounter_types.json; context is driven by the travel call site, not intrinsic to the subtype definition.
Conclusion for Q7:
One-time only: Not currently supported at encounter