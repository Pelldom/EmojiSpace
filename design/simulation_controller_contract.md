# EmojiSpace - Simulation Controller Contract

Status: DRAFT (pending lock)
Phase: 4.11.2 - Structural Consolidation
Target Version: 0.8.2
File: /design/simulation_controller_contract.md

----------------------------------------------------------------
1. Purpose
----------------------------------------------------------------

This contract defines the single authoritative orchestration controller for
EmojiSpace simulation flow.

This controller exists to prevent duplicated turn-loop logic across:
- main.py
- cli_playable.py
- ad-hoc harness scripts
- integration scripts

Once implemented, all player-facing runners (CLI, future UI) MUST call the
SimulationController as the sole execution authority for turn progression.

This contract defines ORCHESTRATION ONLY.
It does NOT define new mechanics, new outcomes, or new systems.

----------------------------------------------------------------
2. Authority
----------------------------------------------------------------

2.1 Single Orchestration Authority
- There MUST be exactly one canonical simulation orchestrator:
  src/simulation_controller.py

- No other module may coordinate the full turn flow described in Section 4.
- Other modules may coordinate their own local resolution subflows only.

2.2 System Responsibilities Remain Unchanged
SimulationController must CALL existing systems; it must not re-implement them.
Examples:
- Travel resolution remains in travel_resolution.py
- Encounter generation remains in encounter_generator.py
- Reaction evaluation remains in reaction_engine.py
- Pursuit remains in pursuit_resolver.py
- Combat remains in combat_resolver.py
- Reward materialization remains in reward_materializer.py
- Reward mutation remains in reward_applicator.py
- Enforcement remains in law_enforcement.py
- Time tick order remains in time_engine.py
- Interactions remain dispatched via interaction_layer.py (dispatch-only)

----------------------------------------------------------------
3. Inputs and Outputs
----------------------------------------------------------------

3.1 Inputs
SimulationController MUST accept:
- world_seed (int)
- world_state (object; authoritative state container)
- player_id (string) or a direct PlayerEntity reference

3.2 Player Command Model
SimulationController must accept a command structure:

Command fields (minimal required):
- action_type (string enum)
- payload (object)

Required action_type values (Phase 4.11.2 scope):
- "travel_to_destination"
- "enter_location" (optional if travel implies arrival context)
- "location_action" (buy/sell/repair/refuel/etc via interaction_layer dispatch)
- "encounter_action" (submit/flee/bribe/attack/etc routed to reaction/pursuit/combat)
- "end_turn" (if needed by the flow; may be implicit)

No other commands may be invented in Phase 4.11.2.

3.3 Outputs
SimulationController MUST return a TurnResult object:

TurnResult fields (mandatory):
- ok (bool)
- error (string or null)
- events (list of event objects)
- hard_stop (bool)
- hard_stop_reason (string or null)

Events MUST be structured dictionaries suitable for logging and UI.

----------------------------------------------------------------
4. Canonical Turn Flow
----------------------------------------------------------------

The SimulationController MUST implement the following canonical flow for a
single command execution:

4.1 Pre-checks
- Validate command shape and required fields.
- Validate player state required for the action (ship present, fuel, etc).

4.2 Execute Action
Depending on action_type:
- travel_to_destination:
  - call travel_resolution to compute travel + fuel consumption
  - update player location/system/destination via existing state mutation APIs
  - advance time according to time_engine rules for travel
  - AFTER travel resolution, trigger post-travel encounter generation
  - route encounter into interaction dispatch (reaction/pursuit/combat)
  - apply rewards (materialize then apply via reward_applicator)
  - persist any NPC effects via npc systems if invoked by encounter
  - run enforcement checkpoints as required by contract triggers
- location_action:
  - dispatch through interaction_layer (dispatch-only)
  - interaction_resolvers performs mutation
  - if action implies enforcement trigger (eg market entry customs),
    enforcement MUST be invoked through law_enforcement only
  - time advancement for location actions must follow time_engine contract

4.3 Hard Stop Conditions
SimulationController MUST hard-stop when:
- player is dead
- Tier 2 detention occurs
- run_end is triggered by end game evaluator (if invoked in this flow)

Hard stop must be reflected in TurnResult.

4.4 Logging and Determinism
- SimulationController MUST not use global randomness.
- Any randomness must be inside called systems that already comply with
  deterministic RNG requirements.
- SimulationController must append structured events for each major step.

----------------------------------------------------------------
5. Prohibited Behavior
----------------------------------------------------------------

SimulationController MUST NOT:
- compute prices
- compute legality/risk (beyond calling government and consuming results)
- compute combat math
- compute ship stats
- mutate player credits/cargo directly (must delegate to reward_applicator or resolvers)
- implement narrative arcs or situations (Phase 5)

----------------------------------------------------------------
6. Harness Policy
----------------------------------------------------------------

- All existing ad-hoc harness scripts (including main.py and cli_playable.py)
  are considered non-authoritative and may be deleted or reduced to thin
  wrappers calling SimulationController.
- There MUST be exactly one CLI entry point retained post-Phase 4.11.2:
  src/cli_run.py (name is fixed by this contract)

cli_run.py responsibilities:
- parse seed and simple commands
- call SimulationController
- print TurnResult events
- no direct mechanics

----------------------------------------------------------------
7. Testing Requirements
----------------------------------------------------------------

7.1 End-to-End Deterministic Integration Test
A new test MUST exist:
- Runs a deterministic multi-step scenario using SimulationController
- Covers (in one run):
  - travel
  - enforcement checkpoint (border or customs)
  - encounter generation
  - pursuit or combat resolution path
  - reward materialization + application
  - time advancement
- Asserts deterministic event sequence shape and key fields.

7.2 No Duplicate Orchestration Tests
Tests must not call deleted harness scripts.
All orchestration tests must call SimulationController.

----------------------------------------------------------------
8. Versioning
----------------------------------------------------------------

This phase is a structural consolidation patch.
Target version: 0.8.2
No new mechanics permitted.
