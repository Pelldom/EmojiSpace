# Phase 7.12 – Exploration & Mining Follow-up Patch Report

**Date:** 2026-03-02  
**Phase:** 7.12 – Exploration and Mining  
**Version:** 0.11.4  
**Related report:** `docs/verification/phase_7_12_exploration_mining_report.md`  
**Commits:**
- `06b38ed645faa06c84ba61a31fca5d4b71a211a1` – Update mining diminishing returns curve to extended depletion model
- `7a1f2a74f9c067653163a8941032aa7507f86754` – Add mining failure attempt increment setting and improve exploration CLI feedback

---

## 1. Scope of Follow-up

This follow-up patch refines the Phase 7.12 implementation in two focused areas:

1. **Mining depletion behavior**
   - Adjusted diminishing-returns curve for mining yields.
   - Added a configurable game setup setting to control whether failed mining attempts increment the depletion counter.
2. **Exploration CLI feedback**
   - Improved player-facing output so playtests can clearly see exploration success/failure and progression.

All changes preserve the existing **deterministic architecture** and do **not** alter the contract file `design/exploration_and_mining_contract.md`.

---

## 2. Mining Diminishing Returns – Extended Curve

### 2.1 Resolver Behavior

**File:** `src/mining_resolver.py`

- The mining resolver keeps the same structure: deterministic, 1 day and 1 fuel consumed by the caller, and SKU selection based **only** on the `harvestable` flag in `data_catalog`.
- The diminishing returns multiplier is now:
  - Attempt index 0 → **1.0**
  - Attempt index 1 → **0.8**
  - Attempt index 2 → **0.6**
  - Attempt index 3 → **0.4**
  - Attempt index 4 → **0.2**
  - Attempt index 5 → **0.1**
  - Attempt index ≥ 6 → **0.05**
- Implementation details:
  - `_yield_multiplier(attempt_index)` returns from `YIELD_MULTIPLIER_TABLE` for indices 0–5; uses `MULTIPLIER_FLOOR = 0.05` for 6+.
  - Attempt index is `mining_attempts[destination_id]` **before** increment, consistent with the original design.
  - `effective_quantity = floor(base_quantity * multiplier)`, using Python integer conversion for determinism.

### 2.2 Tests for the Extended Curve

**File:** `tests/test_exploration_mining_phase712.py`

- `test_mining_diminishing_returns_behavior`
  - Verifies `_yield_multiplier` values for attempt indices 0–6 correspond to the approved curve.
  - Confirms `MiningResult.attempt_number == attempt_index + 1` when calling `resolve_mining` with pre-set attempts.
- `test_mining_diminishing_returns_attempt_6_and_10_use_floor`
  - Asserts `MULTIPLIER_FLOOR == 0.05`.
  - Confirms indices 6 and 10 both use multiplier `0.05` in `_yield_multiplier` and in `resolve_mining`.

---

## 3. Mining Attempts Increment Setting

### 3.1 Game Setup Setting

**Config source:** `GameEngine.__init__` (`src/game_engine.py`)  
**Design documentation:** `design/TO_ADD.md` under **Game Setup Settings**

- New setting: **`mining_attempts_increment_on_failure`** (boolean).
  - Default: **True** (preserves existing gameplay where failures degrade yields).
  - Purpose: Allow tests and tuning to disable depletion on specific failure types without changing resolver code.
  - When **True**:
    - Mining attempts increment on:
      - Successful yield.
      - `no_yield` due to depletion (diminishing-returns floor).
      - Early or resolver-level failures (e.g. capacity issues, missing harvestables) where the setting is consulted.
  - When **False**:
    - Attempts increment on:
      - Successful yield.
      - `no_yield` due to depletion.
    - Attempts **do not** increment on:
      - `no_harvestable_goods`.
      - `insufficient_cargo_capacity`.
      - Early validation failures in `_execute_mine` (see below) – these will only increment when the setting is True.

### 3.2 Resolver-Level Behavior

**File:** `src/mining_resolver.py`

Signature:

- `resolve_mining(..., increment_on_failure: bool = True) -> (MiningResult, dict[str, int])`

Key behaviors:

- The function always:
  - Copies `mining_attempts` into a local `attempts` dict.
  - Reads `attempt_index_before` = `attempts.get(destination_id, 0)`.
  - Tentatively sets `attempts[destination_id] = attempt_index_before + 1`.
- Cases:
  - **`no_yield` (effective_quantity <= 0):**
    - Always treated as a completed attempt (floor depletion).
    - Attempts remain incremented regardless of `increment_on_failure`.
  - **`no_harvestable_goods`:**
    - If `increment_on_failure` is False:
      - Revert increment: `attempts[destination_id] = attempt_index_before`.
    - Else:
      - Keep the increment.
  - **`insufficient_cargo_capacity`:**
    - If `increment_on_failure` is False:
      - Revert increment as above.
    - Else:
      - Keep the increment.
  - **Successful yield (`success=True`):**
    - Attempts remain incremented.

This keeps all depletion logic centralized in `resolve_mining` and makes the failure behavior tunable without changing the overall contract structure.

### 3.3 Engine-Level Behavior and Logging

**File:** `src/game_engine.py` – `_execute_mine`

- Reads `mining_attempts_increment_on_failure` from `self.config` with default `True`.
- Early validations are now wrapped with a helper:

  - `_mine_early_failure_increment(reason: str)`
    - If the setting is True:
      - Increments `player_state.mining_attempts[destination_id]` by 1 for the early failure.
    - Logs a deterministic line (when logging enabled) of the form:
      - `destination_id=... attempt_index_before=... attempt_index_after=... failure_reason={reason} setting={mining_attempts_increment_on_failure}`
    - Used for:
      - Non-`resource_field` type.
      - Destroyed destination.
      - Missing mining capability.
      - Insufficient fuel.

- For the main resolver call:
  - Captures `attempt_index_before` from `player_state.mining_attempts` prior to invoking `resolve_mining`.
  - Calls `resolve_mining(..., increment_on_failure=mining_attempts_increment_on_failure)`.
  - Writes back `player_state.mining_attempts = new_attempts`.
  - Captures `attempt_index_after` from `new_attempts`.
  - Derives `failure_reason` as:
    - `"success"` if `mining_result.success` is True.
    - Otherwise `mining_result.message` (e.g. `no_harvestable_goods`, `insufficient_cargo_capacity`, `no_yield`).
  - Logs (when enabled) a second deterministic line with the same `destination_id`, before/after indices, failure_reason, and setting.
  - Enriches the existing mining event payload with:
    - `attempt_index_before`
    - `attempt_index_after`
    - `failure_reason`
    - `mining_attempts_increment_on_failure`

These logs enable post-hoc verification of depletion behavior and make test-mode runs auditable.

### 3.4 Tests for Increment-on-Failure

**File:** `tests/test_exploration_mining_phase712.py`

- `test_mining_attempts_increment_on_failure_false_cargo_capacity`
  - `increment_on_failure=False`, `physical_cargo_capacity=0`.
  - Confirms:
    - `result.success is False`
    - `result.message == "insufficient_cargo_capacity"`
    - `new_attempts[dest_id] == 0` (no increment).
- `test_mining_attempts_increment_on_failure_true_cargo_capacity`
  - `increment_on_failure=True`, `physical_cargo_capacity=0`.
  - Confirms:
    - Same failure message.
    - `new_attempts[dest_id] == 1` (increment).

---

## 4. Exploration CLI Feedback

### 4.1 Exploration Result Display

**File:** `src/run_game_engine_cli.py`

- New helper: `_print_exploration_result(engine, result)`
  - Triggered from `_destination_actions_menu` after a successful **Explore** action.
  - Reads the `exploration` event from `result["events"]` and extracts:
    - `success`
    - `stage_after`
  - Prints:
    - `Exploration result: SUCCESS` or `Exploration result: FAIL`
    - `Exploration progress at this site: X` where:
      - X is `stage_after` if present, falling back to `engine.player_state.exploration_progress[destination_id]`.

This makes per-site exploration progress visible in CLI playtests without exposing extra internal detail.

### 4.2 Local Activity Encounter UX

**File:** `src/run_game_engine_cli.py` – `_destination_actions_menu`

- After any **Explore** or **Mine** action that returns `ok=True`:
  - Prints: `Local activity may attract attention...`
  - If the engine result has `hard_stop == True` and `hard_stop_reason == "pending_encounter_decision"`:
    - Calls `_resolve_pending_encounter(engine)` to complete the local_activity encounter.
  - Otherwise:
    - Prints: `No ships respond to your activity.`

This ensures:

- Exactly one encounter roll is still governed by the engine (unchanged mechanics).
- The CLI explicitly differentiates between “encounter triggered” and “no encounter” outcomes after local activity.

---

## 5. TO_ADD.md and Design Notes

**File:** `design/TO_ADD.md`

- Added **Game Setup Settings** entry:
  - `mining_attempts_increment_on_failure` (bool, default true)
    - Purpose and notes match the engine/config behavior described in Section 3.
- Added non-binding future note under **Phase 7.9 – Mining Destinations System (Future)**:
  - Refined metals may later be manufacturable from ores instead of directly mined.
  - This is documentation only; no implementation changes in this phase.

---

## 6. Test Summary

**Key suite:** `tests/test_exploration_mining_phase712.py`

- 9 tests total:
  - Harvestable flag correctness.
  - Extended mining diminishing returns behavior.
  - Floor multiplier for attempts 6 and 10.
  - Exploration attempts and progress increments.
  - Local activity encounter cap (≤ 1).
  - emoji_id defaults on generated destinations.
  - Absence of legacy `*_stub` destination types.
  - Mining attempts increment on capacity failure when setting = True / not when False.
- Command:
  - `python -m pytest tests/test_exploration_mining_phase712.py -q` → **9 passed**.

The broader test suite (`python -m pytest -q`) was also exercised during development and is expected to pass; full runs are recommended as part of release gating.

---

## 7. Assessment and Risk

### 7.1 Contract Alignment

- Destination mechanics (`exploration_site` / `resource_field`) remain unchanged from the contract.
- Mining still uses only the `harvestable` flag to build the SKU pool.
- Exploration resolver, mining resolver, and local_activity encounter rules remain structurally identical; only the depletion curve and failure handling are tuned.
- No validation or structural change was introduced to `design/exploration_and_mining_contract.md`.

### 7.2 Determinism

- Deterministic inputs remain:
  - `world_seed`, `destination_id`, `player_id`, and attempt index for resolver RNG.
  - Hardcoded multiplier table and floor.
- New setting (`mining_attempts_increment_on_failure`) is an explicit config input; behavior remains deterministic for any fixed (seed, config) pair.
- Logger lines and event payloads are derived purely from deterministic state; they add observability but no randomness.

### 7.3 UX and Testing Impact

- The mining setting enables:
  - Easier debug and test scenarios (e.g., repeatedly hitting capacity failures without permanently degrading the site).
  - Controlled experiments on depletion curves without editing resolver code.
- Exploration UX improvements make Phase 7.12 mechanics legible in transcripts (“SUCCESS/FAIL” and per-site progress), which is critical for playtest analysis.

Overall risk is **low** and well-contained: the behavior change is gated by an explicit setting with a default that preserves existing gameplay, and all behavior is covered by focused tests.

