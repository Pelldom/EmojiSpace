# Phase 7.5 Pass 1 - Game Engine Orchestration Plan

## Goal
Define the implementation blueprint for a single deterministic `GameEngine` orchestration surface in Pass 2 without changing subsystem mechanics.

## Proposed High-Level Class Structure

```text
GameEngine
  - __init__(world_seed, world_state, player, deps)
  - execute(command) -> StepResult
  - _execute_travel(command, ctx) -> list[event]
  - _execute_location_action(command, ctx) -> list[event]
  - _execute_encounter_action(command, ctx) -> list[event]
  - _run_law_checkpoint(trigger, ctx) -> list[event]
  - _run_encounter_pipeline(ctx) -> list[event]
  - _run_resolver(dispatch, ctx) -> list[event]
  - _maybe_apply_rewards(resolver_outcome, ctx) -> list[event]
  - _check_hard_stop(ctx) -> hard_stop_info
  - _build_step_result(ctx) -> StepResult
```

```text
EngineContext (mutable during one execute call)
  - world_seed
  - turn_before
  - turn_after
  - command
  - player_ref
  - world_state_ref
  - active_system_id
  - active_destination_id
  - active_encounter
  - events[]
  - hard_stop
  - hard_stop_reason
```

## Required Subsystem Call Sequence

### travel_to_destination
1. `travel_resolution.resolve_travel(...)`
2. `time_engine.advance_time(...)` or equivalent authoritative time path
3. `world_state_engine` daily lifecycle (through time engine hook)
4. border `law_enforcement.enforcement_checkpoint(...)` when applicable
5. `encounter_generator.generate_travel_encounters(...)` (or one encounter by policy)
6. `interaction_layer.dispatch_player_action(...)`
7. selected resolver: reaction/pursuit/combat/law
8. `reward_materializer.materialize_reward(...)` only if resolver outcome qualifies
9. `reward_applicator.apply_materialized_reward(...)`
10. hard-stop evaluation and return

### location_action
1. dispatch location action through interaction destination routing
2. run customs checkpoint when action enters market scope
3. apply resulting state changes
4. hard-stop evaluation

### encounter_action
1. validate active encounter
2. dispatch through interaction layer
3. run selected resolver
4. conditional reward pipeline
5. hard-stop evaluation

## Required State Flow Diagram (text)

```text
Command
  -> GameEngine.execute
    -> Precheck + Context init
      -> Action-specific pipeline
        -> Time engine (if action consumes time)
          -> World state lifecycle
        -> Law checkpoint(s)
        -> Encounter generation
        -> Interaction dispatch
        -> Resolver execution
        -> Reward materialize/apply (conditional)
      -> Hard-stop check
      -> StepResult
```

## Proposed StepResult Structure

```text
StepResult
  ok: bool
  error: str | null
  command_type: str
  turn_before: int
  turn_after: int
  hard_stop: bool
  hard_stop_reason: str | null
  state_deltas:
    player: dict
    ship: dict
    world: dict
    npc: dict
  events: list[dict]
  rng_audit:
    streams_used: list[str]
    non_deterministic_calls: list[str]
```

## Determinism Safeguards
- Single orchestration authority for command execution (remove sequencing split)
- No direct use of global `random` in engine
- Require deterministic seed inputs for any subsystem that accepts caller RNG
- Stable ordering for iterable processing before weighted picks
- Explicit RNG stream names in event logs for cross-system reconstruction
- Reset/initialize time-engine global state only at simulation bootstrap, not mid-step

## Hard Stop Handling Strategy
- Evaluate hard stop after each irreversible mutation stage
- Treat these as immediate stop reasons:
  - `player_death`
  - `tier2_detention`
  - explicit run-end outcome from end-game evaluator
- Preserve completed mutations; do not rollback
- Return `StepResult` with `hard_stop=True` and clear reason

## Logging Requirements
- One top-level engine event per stage transition
- Include deterministic context in each stage event:
  - world_seed
  - turn
  - command id/type
  - subsystem name
  - stream id (if RNG used)
- Emit structured payloads for:
  - travel results
  - law checkpoint rolls/outcomes
  - encounter generation logs
  - interaction dispatch selection
  - resolver outcomes
  - reward materialization and application
  - hard-stop decision point

## Pass 2 Implementation Constraints
- Reuse existing subsystem APIs as-is
- Do not alter subsystem mechanics during unification
- Keep old harnesses as wrappers until migration completes
- Add adapter layer only where signatures differ

