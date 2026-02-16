# Game Engine Contract

Status: Authoritative for Phase 7.5 Pass 2
Target Version: 0.10.2

## Responsibilities

- Provide the single authoritative orchestration layer for command execution.
- Enforce stage ordering and hard-stop behavior.
- Route to existing subsystem APIs without adding new mechanics.
- Maintain deterministic execution and structured step logging.
- Return a stable `StepResult` object for every command.

## Exclusions

- No new gameplay mechanics.
- No simulation rule changes inside subsystem resolvers.
- No dependency on legacy orchestrators or harnesses:
  - `src/turn_loop.py`
  - `src/simulation_controller.py`
  - `src/cli_test.py`
  - `src/integration_test.py`
  - `src/cli_run.py`
- No UI ownership beyond a minimal validation CLI.

## Ordering Invariants

For `travel_to_destination`, the engine must execute in this order:

1) travel resolution
2) time advance
3) per-day world ticks (via time engine lifecycle)
4) law checkpoint(s)
5) encounter generation
6) interaction dispatch
7) resolver execution
8) conditional reward materialization and application
9) hard stop evaluation
10) `StepResult` return

Additional invariant:

- Destination interaction can occur only after encounter processing and only if no hard stop is active.
- Local actions do not advance time by default.

## Hard Stop Contract

- Hard stop detection is evaluated after each mutating stage and at step end.
- When hard stop is detected, execution aborts immediately.
- Mutations completed before detection are preserved.
- No rollback is permitted.

## Determinism Rules

- Same seed + same command list must produce identical `StepResult` sequences.
- Engine-level isolated RNG stream name is `engine_orchestration`.
- Engine may create internal RNG instances only from deterministic seed derivation:
  - inputs: `(world_seed, stable_id, stream_name)`
  - hash: SHA-256
- No global `random` usage in the engine.
- Iteration over maps or sets must use stable ordering.

## Reward Gating Rules

- Rewards are not unconditional.
- Reward application is allowed only when resolver outcomes qualify as explicit success.
- If resolver intent is ambiguous, reward must not be granted.

## Required StepResult Fields

`StepResult` is a dict with stable keys:

- `ok` (bool)
- `error` (string or null)
- `command_type` (string)
- `turn_before` (int)
- `turn_after` (int)
- `hard_stop` (bool)
- `hard_stop_reason` (string or null)
- `events` (list of structured dict events)
- `player` (dict snapshot: system, destination, location, credits, arrest_state)
- `active_encounter_count` (int)
- `version` (string)

## Structured Event Requirements

Each event entry in `events` must include:

- `stage`
- `world_seed`
- `turn`
- `command_type`
- `subsystem`
- `detail` (dict)

Event detail must remain ASCII-safe and deterministic.
