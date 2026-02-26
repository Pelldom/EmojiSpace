# Phase 7.5 Pass 1 - Game Engine Integration Audit

## Scope
- Branch: main
- Pass: preparation only
- Code changes: none in gameplay modules
- Audit basis: src module read-through plus design contracts in `design/`

## Subsystem Inventory

### Travel
- `src/travel_resolution.py`

### Encounter generation
- `src/encounter_generator.py`

### Reaction
- `src/reaction_engine.py`

### Interaction layer
- `src/interaction_layer.py`
- `src/interaction_resolvers.py`

### Combat
- `src/combat_resolver.py`

### Pursuit
- `src/pursuit_resolver.py`

### Reward materialization
- `src/reward_materializer.py`

### Law enforcement
- `src/law_enforcement.py`
- `src/government_law_engine.py`
- `src/tag_policy_engine.py`

### Time engine
- `src/time_engine.py`

### World state
- `src/world_state_engine.py`

### Market systems
- `src/market_creation.py`
- `src/market_pricing.py`
- `src/economy_engine.py`
- `src/market.py`
- `src/economy_data.py`

### NPC systems
- `src/npc_ship_generator.py`
- `src/npc_registry.py`
- `src/npc_entity.py`
- `src/npc_placement.py`

### Ship systems
- `src/ship_assembler.py`
- `src/ship_entity.py`
- `src/shipdock_inventory.py`
- `src/salvage_resolver.py`

### Entities / models
- `src/player_state.py`
- `src/entities.py`
- `src/mission_entity.py`
- `src/warehouse_entity.py`
- `src/datanet_entry.py`
- `src/government_type.py`

### Utilities / data access / glue
- `src/data_catalog.py`
- `src/data_loader.py`
- `src/government_registry.py`
- `src/logger.py`
- `src/prose_generator.py`
- `src/datanet_feed.py`
- `src/end_game_evaluator.py`
- `src/reward_applicator.py`
- `src/mission_factory.py`
- `src/mission_generator.py`
- `src/mission_manager.py`
- `src/simulation_controller.py`
- `src/turn_loop.py`

### Test harnesses and runner shells
- `src/cli_run.py`
- `src/main.py`
- `src/cli_test.py`
- `src/cli_combat_sim.py`
- `src/integration_test.py`

## Authoritative Entry Point Mapping

### Travel
- Entry: `travel_resolution.resolve_travel(...)`
- Params: `ship, inter_system, distance_ly, emergency_transport=False, advance_time=None, player_state=None, world_state_engine=None, current_system_id=None, route_id=None, route_tags=None, rng=None, base_risk=0.0, base_encounter_rate=0.0`
- Returns: `TravelResult`
- Mutation: mutates `ship.current_fuel`; mutates `player_state.credits` when provided
- RNG: none internally unless caller passes `rng` for unstable wormhole branch
- Preconditions: valid ship object and fields; if inter-system, distance non-negative
- Postconditions: success/fail with fuel/wage side effects encoded in returned record
- Authority: this is the mechanical travel resolver in code

### Encounter generation
- Entry: `encounter_generator.generate_travel_encounters(...)`
- Params: `world_seed, travel_id, population, system_government_id, active_situations, travel_context=None, world_state_engine=None, current_system_id=None`
- Returns: `list[EncounterSpec]`
- Mutation: no state mutation; pure generation
- RNG: deterministic hash-derived float and weighted choice helpers
- Preconditions: population >= 0 and data catalogs load
- Postconditions: ordered encounter specs with embedded selection logs
- Authority: for travel loops use `generate_travel_encounters`; `generate_encounter` is lower-level single-spec generator

### Reaction
- Entry: `reaction_engine.get_npc_outcome(...)`
- Params: `spec, player_action, world_seed, ignore_count, reputation_score, notoriety_score, law_score=None, outlaw_score=None`
- Returns: `(outcome_str, log_dict)`
- Mutation: none
- RNG: deterministic weighted choice via `encounter_generator.deterministic_weighted_choice`
- Preconditions: `spec` has response profile and encounter metadata
- Postconditions: deterministic reaction outcome and full modifier log
- Authority: reaction scoring and outcome mapping lives here

### Interaction layer
- Entry: `interaction_layer.dispatch_player_action(...)`
- Params: `spec, player_action, world_seed, ignore_count, reputation_band, notoriety_band`
- Returns: `InteractionResult(next_handler, handler_payload, log)`
- Mutation: no direct world/player mutation for encounter dispatch path
- RNG: none directly; delegates to reaction engine for reaction-required actions
- Preconditions: valid action and phase-allowed action set
- Postconditions: explicit next-handler routing decision
- Additional local-action entry: `interaction_layer.dispatch_destination_action(action_id, **kwargs)`
- Mutation note: destination actions delegate to `interaction_resolvers` and do mutate player/ship/fleet state
- Authority: encounter dispatch routing and destination action routing live here

### Combat
- Entry: `combat_resolver.resolve_combat(...)`
- Params: `world_seed, combat_id, ...` (ship/loadout/action selector forms supported)
- Returns: `CombatResult`
- Mutation: operates on local combat state; returns assembled outcome payload (winner, logs, salvage)
- RNG: `CombatRng` seeded from `world_seed` and combat salt
- Preconditions: valid ship/module payloads
- Postconditions: deterministic combat timeline and outcome payload
- Authority: combat mechanics source of truth

### Pursuit
- Entry: `pursuit_resolver.resolve_pursuit(encounter_id, world_seed, pursuer_ship, pursued_ship)`
- Returns: `PursuitResult`
- Mutation: none
- RNG: deterministic float from seed string
- Preconditions: ships include speed; pilot and band fields validated or derived
- Postconditions: binary `escape_success` or `escape_fail` with audit log
- Authority: pursuit resolution source of truth

### Reward materialization
- Entry: `reward_materializer.materialize_reward(spec, system_markets, world_seed)`
- Returns: `RewardResult | None`
- Mutation: none
- RNG: deterministic SKU pick, quantity roll, stolen roll, credit roll
- Preconditions: valid reward profile id and market SKU pool
- Postconditions: normalized reward payload or empty equivalent
- Authority: reward generation source of truth

### Reward application
- Entry: `reward_applicator.apply_materialized_reward(player, reward_payload, context=None)`
- Returns: `dict` applied summary
- Mutation: mutates player credits and active cargo map
- RNG: none
- Preconditions: valid player object and optional reward payload
- Postconditions: player state adjusted and delta summary returned
- Authority: reward mutation source of truth

### Law enforcement
- Entry: `law_enforcement.enforcement_checkpoint(...)`
- Params: system/government/policy/player/world_seed/turn/cargo_snapshot/logger plus options
- Returns: `EnforcementOutcome | None`
- Mutation: mutates player reputation/heat/warrants/fines/arrest state; may mutate ship crew through lawyer downgrade path
- RNG: seeded `random.Random` streams via `_rng_for(...)`
- Preconditions: policy results and government model available
- Postconditions: deterministic checkpoint outcome and logged consequence state
- Authority: enforcement consequence application in current runtime flow

### Time engine
- Entry: `time_engine.advance_time(days, reason)` and `TimeEngine.advance()`
- Returns: `TimeAdvanceResult` or current turn
- Mutation: mutates module-level turn globals; runs world-state lifecycle callbacks
- RNG: no direct random in time tick, but world-state callbacks consume deterministic RNG
- Preconditions: player-action context enabled; day bounds 1..10
- Postconditions: turn advanced, per-day ticks executed, possible hard-stop early halt
- Authority: global time advancement mechanism

### World state
- Entry: `WorldStateEngine.evaluate_spawn_gate(...)`, `process_scheduled_events(...)`, `process_propagation(...)`, `resolve_modifiers_for_entities(...)`
- Returns: mostly side-effect methods; resolver returns structured modifier map
- Mutation: mutates active events/situations/modifiers/system flags/scheduled queues/structural mutation queue
- RNG: deterministic channel seeds per world seed/day/system/event keys
- Preconditions: catalogs loaded and systems registered
- Postconditions: deterministic world-state progression and modifier views
- Authority: world event/situation lifecycle and modifier aggregation

### Market systems
- Pricing entry: `market_pricing.price_transaction(...)` returns `PricingResult`; no direct mutation
- Economy entry: `EconomyEngine.advance_turn(turn, trade_action=None)` mutates availability/price pressure state
- Market creation entry: `MarketCreator.create_market(...)` returns `Market`
- RNG: deterministic if seeded RNG passed to creator; pricing substitute discount uses stable seeded `random.Random`

### NPC systems
- Ship generation: `npc_ship_generator.generate_npc_ship(...)` returns ship-state dict, no global mutation
- Registry mutation: `NPCRegistry.add/remove/update(...)` mutates NPC index maps
- Placement entry: `npc_placement.resolve_npcs_for_location(...)` returns NPC list and registry side effects as needed

### Ship systems
- Assembly entry: `ship_assembler.assemble_ship(...)` returns assembled ship stats/config dict
- Ship entity mutators: `ShipEntity.set_*`, `add_crew`, `remove_crew`
- Shipdock inventory generation: `shipdock_inventory.generate_shipdock_inventory(...)` returns deterministic inventory bundle
- Salvage entry: `salvage_resolver.resolve_salvage_modules(...)` returns module instances list

### Entities/models/utilities
- `PlayerState` and `ShipEntity` are canonical mutable state carriers
- `DataCatalog` and loaders are read/validate utilities
- `Logger.log(...)` is side-effect print logger used across systems

## State Mutation Map

### Player state mutations
- Direct mutable writes in: `travel_resolution`, `reward_applicator`, `law_enforcement`, `turn_loop`, `interaction_resolvers`, `mission_manager`, `simulation_controller`
- Encapsulation quality: mixed
  - Encapsulated setters exist in `PlayerState`, but many modules write fields directly
- Contract control: partial; some writes follow contracts, others are implementation convenience

### World state mutations
- Primary owner: `world_state_engine.WorldStateEngine`
- Additional world mutations: `world_generator` (initial construction), `simulation_controller` active encounter handling
- Encapsulation quality: mostly encapsulated in engine methods
- Contract control: strong in world-state module, weaker in callers that only partially honor contract order

### Ship state mutations
- Direct writes in: `travel_resolution`, `interaction_resolvers`, `ship_entity`, `simulation_controller`
- Encapsulation quality: mixed
  - `ShipEntity` has setters, but many modules mutate attributes/persistent_state directly
- Contract control: partial

### Time/turn state mutations
- Primary owner: `time_engine` module globals (`_current_turn`, hard-stop flags)
- Called by: `TurnLoop`, potentially other orchestrators
- Encapsulation quality: centralized but global-state based
- Contract control: medium (guarded by player-action context)

### NPC state mutations
- Registry-level mutations in `npc_registry`
- Event-driven NPC mutations in `world_state_engine._apply_npc_mutations`
- Ship crew mutations via `ShipEntity.add_crew/remove_crew` and law-enforcement lawyer removal path

### Integration risk points from mutation model
- Shared mutable references (player, ship, registry, world state) passed across systems without immutable boundaries
- Direct field writes bypass setter logging in several modules
- Multiple orchestrators can mutate same state in overlapping ways (`TurnLoop` and `SimulationController`)

## RNG Audit Summary

### Deterministic isolated streams already present
- `combat_resolver.CombatRng` (seeded by world seed + combat salt)
- `encounter_generator` deterministic hash-based weighted choices
- `reaction_engine` deterministic weighted choice seed from world/encounter/action
- `pursuit_resolver` deterministic float seed
- `law_enforcement` checkpoint/action-specific seeded `random.Random`
- `government_law_engine` stable-seeded random roll
- `market_pricing.resolve_substitute_discount` stable-seeded random stream
- `npc_ship_generator` named per-stream SHA-based RNGs
- `salvage_resolver` named per-stream SHA-based RNGs
- `shipdock_inventory` stream-seeded RNGs
- `world_generator` and destination helpers seeded RNG channels
- `world_state_engine` deterministic seed channels for spawn, schedule, propagation, duration

### Seeded externally (deterministic if caller disciplined)
- `market_creation.MarketCreator` (expects caller-provided RNG)
- `mission_generator.select_weighted_mission_type` (expects caller-provided RNG)
- `travel_resolution.resolve_travel` unstable-wormhole branch (uses caller-provided RNG when provided)

### Determinism risks
- If callers provide unseeded/default RNG to mission/market/travel optional RNG paths, determinism can drift
- Multiple orchestration surfaces (`TurnLoop` and `SimulationController`) can consume RNG in different orders, changing outcomes
- Global module state in `time_engine` can affect reproducibility across concurrent harness runs if not reset

## Ordering Dependency Map (Contract vs Implementation)

### Required by contracts
- Travel -> Time advance -> Encounter generation -> Interaction dispatch
- Hard-stop conditions must halt advancement immediately
- Law checkpoints sequence around border/customs triggers
- Reward application must occur after qualifying resolver outcomes

### Observed implementation behavior
- `SimulationController._execute_travel_to_destination` calls `resolve_travel` then `TurnLoop.execute_move` (time and border checkpoint), then encounter generation and interaction dispatch
- `TurnLoop.execute_move` does: set destination system -> `time_engine.advance()` -> economy advance -> heat decay -> border checkpoint
- `TurnLoop.execute_buy/sell` currently advances time for market actions
- `SimulationController._resolve_encounter` always materializes and applies reward after dispatch branch, regardless of encounter outcome details

### Consistency findings
- Travel->time->encounter->interaction ordering exists in `SimulationController`
- Border enforcement path exists in `TurnLoop`

### Contract alignment risks
1) Time cost mismatch risk
- Inter-system travel distance is accepted by `resolve_travel`, but `TurnLoop.execute_move` advances only one day
- Potential mismatch with time/travel contracts expecting distance-scaled day advancement

2) Reward sequencing risk
- Reward currently applied unconditionally in `SimulationController._resolve_encounter`
- Contract expectation is resolver-qualified reward application

3) Interaction mutation boundary risk
- Interaction contract says dispatch-only for encounter layer; destination action routing in `interaction_layer` delegates to mutating resolvers directly

4) Local action time advancement risk
- Time contract says local actions are non-advancing by default; `TurnLoop.execute_buy/sell` advance time

5) Hard-stop propagation surface split
- `time_engine` has internal hard-stop checks; `SimulationController` computes hard-stop from emitted events and arrest field
- Multiple hard-stop authorities increase orchestration ambiguity

## Integration Risks List
- Dual orchestrators (`TurnLoop` and `SimulationController`) create sequencing divergence risk
- Distance-based travel time not centrally enforced in one place
- Reward application not gated by clear resolver success contract
- Mutable shared state with direct field writes bypasses setter/log hooks
- Determinism depends on call-order discipline across many seeded streams
- Interaction layer responsibilities blur between dispatch and mutation for destination actions

## Recommended Orchestration Order for Phase 7.5
1. Validate command and snapshot deterministic context (seed, turn, player/system ids)
2. Resolve travel mechanics (fuel, wage, route modifiers) without side branching
3. Advance time through authoritative time engine with explicit days
4. Run world-state lifecycle and enforce hard-stop checks after each day
5. Execute mandatory law checkpoints by trigger type (border/customs)
6. Generate encounters (travel context) deterministically
7. Dispatch encounter action through interaction layer
8. Run selected resolver (reaction/pursuit/combat/law/exploration)
9. Materialize reward only when resolver outcome qualifies
10. Apply reward through reward applicator
11. Emit structured step events and return single step result

