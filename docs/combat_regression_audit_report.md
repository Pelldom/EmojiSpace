# Combat Regression Audit Report

**Date:** 2024-12-19  
**Issue:** Combat state shows 0% hull for both ships and round stuck at 0 in CLI  
**Mode:** Audit Only - No Fixes Implemented

---

## 1) Reproduction Path

### Minimal Steps to Reproduce

1. Start CLI with seed 12345:
   ```bash
   python src/run_game_engine_cli.py
   # Enter seed: 12345
   ```

2. Navigate to Travel menu (option 3)

3. Select inter-system warp (option 1)

4. Choose any reachable system

5. If an encounter occurs, select "Attack" option

6. Combat menu should appear

### Observed Symptom

```
--- COMBAT ROUND 0 ---
Player Hull: 0% | Enemy Hull: 0%
Available Actions:
1) Focus Fire
2) Reinforce Shields
3) Evasive Maneuvers
4) Attempt Escape
5) Surrender
```

**Problem:** 
- Round number shows 0 (should be 1 for first round)
- Player hull shows 0% (should show actual hull percentage)
- Enemy hull shows 0% (should show actual hull percentage)
- Menu repeats forever with same values

---

## 2) Git/Change Forensics

### Git Status
```
On branch main
Your branch is ahead of 'origin/main' by 12 commits.

Changes not staged for commit:
  modified:   src/combat_resolver.py
  modified:   src/game_engine.py
  modified:   src/run_game_engine_cli.py
  ... (other files)
```

### Recent Commits
```
0cf1526 Docs: Lock World Generation and World State. Add Phase 7.10 Combat Unification.
6db1f5e World gen: Add destination population structural anchor (max-pop guarantee)
e07f97e CLI: set default galaxy size to 50, add travel header improvements
...
```

### Key Finding
The `_pending_combat` state was introduced in recent commits as part of Phase 7.10 Combat Unification. The regression likely occurred when `get_pending_combat_info()` was added to expose combat state to CLI.

**Commit Analysis:**
- `_initialize_combat_session()` correctly initializes `round_number: 0` (line 2637)
- `_process_combat_round()` correctly increments `round_number` (line 2702-2703)
- `get_pending_combat_info()` was added to provide CLI display data (line 366)

---

## 3) Data Provenance Trace

### 3.1 Round Number

**Source Assignment:**
- **File:** `src/game_engine.py`
- **Line:** 2637
- **Code:** `"round_number": 0,  # 0 = not started, will be 1+ when first round processes`
- **Context:** `_initialize_combat_session()` stores initial state

**Storage Location:**
- **File:** `src/game_engine.py`
- **Line:** 2630-2647
- **Structure:** `self._pending_combat["round_number"]`

**Mutation Each Round:**
- **File:** `src/game_engine.py`
- **Line:** 2702-2703
- **Code:**
  ```python
  round_number = pending["round_number"] + 1
  pending["round_number"] = round_number
  ```
- **Context:** `_process_combat_round()` increments before processing

**Read for Display:**
- **File:** `src/game_engine.py`
- **Line:** 408
- **Code:** `"round_number": pending.get("round_number", 1),`
- **Context:** `get_pending_combat_info()` returns value for CLI
- **ISSUE:** Returns 0 if `_process_combat_round()` hasn't been called yet

**Alternative Read (in `_build_step_result`):**
- **File:** `src/game_engine.py`
- **Line:** 3305
- **Code:** `round_number = pending.get("round_number", 0) + 1  # Next round`
- **Context:** Calculates next round number for display
- **NOTE:** This correctly shows next round, but CLI uses `get_pending_combat_info()` which shows current round

### 3.2 Player Hull Percentage

**Source Assignment:**
- **File:** `src/game_engine.py`
- **Line:** 2605-2606
- **Code:**
  ```python
  if player_ship_state.get("current_hull_integrity", 0) > 0:
      player_state.hull_current = min(player_ship_state["current_hull_integrity"], player_state.hull_max)
  ```
- **Context:** `_initialize_combat_session()` sets initial hull from persistent state
- **Storage:** `pending["player_state"].hull_current` (CombatState object)

**Storage Location:**
- **File:** `src/game_engine.py`
- **Line:** 2638
- **Structure:** `self._pending_combat["player_state"]` (CombatState object with `.hull_current` and `.hull_max` attributes)

**Mutation Each Round:**
- **File:** `src/combat_resolver.py` (via `_apply_damage_and_degradation`)
- **Context:** Called from `_process_combat_round()` to apply damage

**Read for Display (WRONG SOURCE):**
- **File:** `src/game_engine.py`
- **Line:** 394-398
- **Code:**
  ```python
  player_state = pending.get("player_ship_state", {})
  hull_current = player_state.get("hull_current", 0)  # BUG: player_ship_state dict doesn't have hull_current
  hull_max = player_state.get("hull_max", 1)         # BUG: player_ship_state dict doesn't have hull_max
  if hull_max > 0:
      player_hull_pct = int((hull_current / hull_max) * 100)
  ```
- **Context:** `get_pending_combat_info()` tries to read from wrong dict
- **ROOT CAUSE:** `player_ship_state` is a dict with keys: `hull_id`, `module_instances`, `degradation_state`, `current_hull_integrity` - it does NOT have `hull_current` or `hull_max`

**Correct Source (should be):**
- **File:** `src/game_engine.py`
- **Line:** 2638
- **Structure:** `pending["player_state"]` (CombatState object)
- **Attributes:** `.hull_current` and `.hull_max`

**Reference Implementation (correct):**
- **File:** `src/game_engine.py`
- **Line:** 3306
- **Code:** `player_hull_pct = hull_percent(player_state.hull_current, player_state.hull_max)`
- **Context:** `_build_step_result()` correctly reads from `player_state` CombatState object

### 3.3 Enemy Hull Percentage

**Source Assignment:**
- **File:** `src/npc_ship_generator.py` (via `generate_npc_ship()`)
- **Context:** Enemy ship generated with initial hull values
- **Storage:** `pending["enemy_state"].hull_current` (CombatState object)

**Storage Location:**
- **File:** `src/game_engine.py`
- **Line:** 2639
- **Structure:** `self._pending_combat["enemy_state"]` (CombatState object with `.hull_current` and `.hull_max` attributes)

**Mutation Each Round:**
- **File:** `src/combat_resolver.py` (via `_apply_damage_and_degradation`)
- **Context:** Called from `_process_combat_round()` to apply damage

**Read for Display (WRONG SOURCE):**
- **File:** `src/game_engine.py`
- **Line:** 400-403
- **Code:**
  ```python
  enemy_ship = pending.get("enemy_ship_dict", {})
  hull_current = enemy_ship.get("hull_current", 0)  # BUG: enemy_ship_dict may not have hull_current
  hull_max = enemy_ship.get("hull_max", 1)             # BUG: enemy_ship_dict may not have hull_max
  if hull_max > 0:
      enemy_hull_pct = int((hull_current / hull_max) * 100)
  ```
- **Context:** `get_pending_combat_info()` tries to read from wrong dict
- **ROOT CAUSE:** `enemy_ship_dict` structure may vary, but hull values are in `enemy_state` CombatState object

**Correct Source (should be):**
- **File:** `src/game_engine.py`
- **Line:** 2639
- **Structure:** `pending["enemy_state"]` (CombatState object)
- **Attributes:** `.hull_current` and `.hull_max`

**Reference Implementation (correct):**
- **File:** `src/game_engine.py`
- **Line:** 3307
- **Code:** `enemy_hull_pct = hull_percent(enemy_state.hull_current, enemy_state.hull_max)`
- **Context:** `_build_step_result()` correctly reads from `enemy_state` CombatState object

---

## 4) Instrumentation (Temporary Debug Logging)

### Debug Flag
```python
# Add at top of game_engine.py
DEBUG_COMBAT_AUDIT = True
```

### Logging Points Added

#### 4.1 Combat Initialization
**File:** `src/game_engine.py`  
**Location:** After line 2647 (end of `_initialize_combat_session`)

```python
if DEBUG_COMBAT_AUDIT:
    print("=== COMBAT INIT DEBUG ===")
    print(f"round_number: {self._pending_combat['round_number']}")
    print(f"player_state.hull_current: {self._pending_combat['player_state'].hull_current}")
    print(f"player_state.hull_max: {self._pending_combat['player_state'].hull_max}")
    print(f"enemy_state.hull_current: {self._pending_combat['enemy_state'].hull_current}")
    print(f"enemy_state.hull_max: {self._pending_combat['enemy_state'].hull_max}")
    print(f"player_ship_state keys: {list(self._pending_combat['player_ship_state'].keys())}")
    print(f"enemy_ship_dict keys: {list(self._pending_combat['enemy_ship_dict'].keys())}")
    print("========================")
```

#### 4.2 Before CLI Display
**File:** `src/game_engine.py`  
**Location:** Inside `get_pending_combat_info()` before return (after line 411)

```python
if DEBUG_COMBAT_AUDIT:
    print("=== CLI DISPLAY DEBUG ===")
    print(f"round_number from pending: {pending.get('round_number')}")
    print(f"player_ship_state type: {type(pending.get('player_ship_state'))}")
    print(f"player_ship_state keys: {list(pending.get('player_ship_state', {}).keys())}")
    print(f"player_state type: {type(pending.get('player_state'))}")
    if pending.get('player_state'):
        print(f"player_state.hull_current: {pending['player_state'].hull_current}")
        print(f"player_state.hull_max: {pending['player_state'].hull_max}")
    print(f"Calculated player_hull_pct: {player_hull_pct}")
    print(f"Calculated enemy_hull_pct: {enemy_hull_pct}")
    print("=========================")
```

#### 4.3 Combat Action Submitted
**File:** `src/game_engine.py`  
**Location:** Inside `_execute_combat_action()` before `_process_combat_round()` (after line 3063)

```python
if DEBUG_COMBAT_AUDIT:
    print("=== COMBAT ACTION DEBUG ===")
    print(f"Action received: {player_action}")
    print(f"Pre-state round_number: {self._pending_combat['round_number']}")
    print(f"Pre-state player_state.hull_current: {self._pending_combat['player_state'].hull_current}")
    print(f"Pre-state enemy_state.hull_current: {self._pending_combat['enemy_state'].hull_current}")
```

**Location:** Inside `_execute_combat_action()` after `_process_combat_round()` (after line 3064)

```python
if DEBUG_COMBAT_AUDIT:
    print(f"Post-state round_number: {round_result['round_number']}")
    print(f"Post-state player_hull_pct: {round_result['player_hull_pct']}")
    print(f"Post-state enemy_hull_pct: {round_result['enemy_hull_pct']}")
    print(f"Pending combat round_number: {self._pending_combat['round_number']}")
    print("===========================")
```

---

## 5) Engine Round Processing Execution

### Analysis

**Question:** Is `_process_combat_round()` being called?

**Evidence:**
- **File:** `src/game_engine.py`
- **Line:** 3064
- **Code:** `round_result = self._process_combat_round(player_action)`
- **Context:** `_execute_combat_action()` calls it when combat action command is received

**Conclusion:** `_process_combat_round()` IS being called (assuming combat action command is sent).

**Question:** Does it mutate state correctly?

**Evidence:**
- **File:** `src/game_engine.py`
- **Line:** 2702-2703
- **Code:** 
  ```python
  round_number = pending["round_number"] + 1
  pending["round_number"] = round_number
  ```
- **Context:** Round number is incremented and stored in pending combat dict

**Conclusion:** Round number IS mutated correctly in `_process_combat_round()`.

**Question:** Is state read correctly for display?

**Evidence:**
- **File:** `src/game_engine.py`
- **Line:** 394-398 (player) and 400-403 (enemy)
- **Issue:** Reading from wrong source (`player_ship_state` dict instead of `player_state` CombatState object)

**Conclusion:** State is NOT read correctly for display in `get_pending_combat_info()`.

### Proof of Execution Path

**Scenario A:** `_process_combat_round()` is NOT being called
- **Evidence:** If round stays at 0, this would indicate `_process_combat_round()` is never called
- **Likelihood:** LOW - CLI sends combat_action command, which should trigger it

**Scenario B:** It is called but returns without mutating state
- **Evidence:** Round number increment code exists and should execute
- **Likelihood:** LOW - Code path is straightforward

**Scenario C:** It mutates state but state is overwritten/reset afterward
- **Evidence:** No code found that resets `_pending_combat["round_number"]` after increment
- **Likelihood:** LOW

**Scenario D:** It mutates state but CLI reads from wrong object
- **Evidence:** `get_pending_combat_info()` reads from `player_ship_state` dict (wrong) instead of `player_state` CombatState object (correct)
- **Likelihood:** **HIGH** - This is the root cause

---

## 6) Identify the Exact Fault

### Root Cause

**Single Sentence:**  
`get_pending_combat_info()` reads hull values from `player_ship_state` dict (which doesn't contain `hull_current`/`hull_max`) instead of `player_state` CombatState object (which does), and returns `round_number` as-is (0) instead of showing the current active round.

### Fault Location

**File:** `src/game_engine.py`  
**Lines:** 366-412 (entire `get_pending_combat_info()` method)

**Specific Issues:**

1. **Line 394:** `player_state = pending.get("player_ship_state", {})`
   - **Problem:** Variable name `player_state` shadows the actual `player_state` CombatState object
   - **Should be:** Read from `pending.get("player_state")` (CombatState object)

2. **Line 395-396:** `hull_current = player_state.get("hull_current", 0)` and `hull_max = player_state.get("hull_max", 1)`
   - **Problem:** `player_ship_state` dict doesn't have these keys
   - **Should be:** `hull_current = pending["player_state"].hull_current` and `hull_max = pending["player_state"].hull_max`

3. **Line 400-401:** `hull_current = enemy_ship.get("hull_current", 0)` and `hull_max = enemy_ship.get("hull_max", 1)`
   - **Problem:** `enemy_ship_dict` may not have these keys in expected format
   - **Should be:** `hull_current = pending["enemy_state"].hull_current` and `hull_max = pending["enemy_state"].hull_max`

4. **Line 408:** `"round_number": pending.get("round_number", 1)`
   - **Problem:** Returns 0 if combat hasn't started (round_number initialized to 0)
   - **Note:** This is actually correct behavior - round 0 means "not started". However, if `_process_combat_round()` has been called, it should show the incremented value. The issue is that the method is called BEFORE the first round is processed, so it shows 0.

### Why It Produces 0%/Round 0

1. **Round 0:** 
   - `round_number` is initialized to 0 in `_initialize_combat_session()` (line 2637)
   - `get_pending_combat_info()` returns this value directly (line 408)
   - If called before first combat action, it correctly shows 0
   - **However:** If `_process_combat_round()` has been called, `round_number` should be incremented. If it still shows 0, either:
     - `_process_combat_round()` is not being called, OR
     - The increment is happening but `get_pending_combat_info()` is reading a stale value (unlikely)

2. **0% Hull:**
   - `player_ship_state` dict has keys: `hull_id`, `module_instances`, `degradation_state`, `current_hull_integrity`
   - It does NOT have `hull_current` or `hull_max` keys
   - `player_state.get("hull_current", 0)` returns 0 (default) because key doesn't exist
   - `player_state.get("hull_max", 1)` returns 1 (default) because key doesn't exist
   - Calculation: `0 / 1 * 100 = 0%`
   - Same issue for enemy hull

### Minimal Fix Strategy

**DO NOT IMPLEMENT - DESCRIBE ONLY:**

1. **Fix hull percentage calculation in `get_pending_combat_info()`:**
   - Change line 394 to: `player_state_obj = pending.get("player_state")` (rename to avoid shadowing)
   - Change lines 395-398 to read from `player_state_obj.hull_current` and `player_state_obj.hull_max`
   - Change lines 400-403 to read from `pending.get("enemy_state")` CombatState object

2. **Fix round number display:**
   - If `round_number` is 0 and combat has started, it should show 1 (first round)
   - However, if `_process_combat_round()` increments it correctly, this may not be an issue
   - Consider: `"round_number": max(1, pending.get("round_number", 0))` to ensure minimum of 1 for display

3. **Reference correct implementation:**
   - `_build_step_result()` at lines 3305-3307 correctly reads from CombatState objects
   - Use same pattern in `get_pending_combat_info()`

---

## 7) Safety Rails

### Competing Causes (Ranked)

1. **PRIMARY: Wrong data source in `get_pending_combat_info()`**
   - **Evidence:** Lines 394-403 read from wrong dicts
   - **Confidence:** HIGH
   - **Impact:** 0% hull display

2. **SECONDARY: Round number initialization/display**
   - **Evidence:** Round starts at 0, may not increment if `_process_combat_round()` not called
   - **Confidence:** MEDIUM
   - **Impact:** Round stuck at 0

3. **TERTIARY: Combat action command not reaching engine**
   - **Evidence:** None found - CLI appears to send commands correctly
   - **Confidence:** LOW
   - **Impact:** Round never increments

### Evidence Summary

- **File:** `src/game_engine.py`
- **Method:** `get_pending_combat_info()` (lines 366-412)
- **Bug:** Reads hull from `player_ship_state` dict (wrong) instead of `player_state` CombatState object (correct)
- **Reference:** `_build_step_result()` (lines 3305-3307) shows correct implementation pattern

---

## Appendix: Data Structure Reference

### `player_ship_state` Dict Structure
```python
{
    "hull_id": str,
    "module_instances": list,
    "degradation_state": dict,
    "current_hull_integrity": int  # NOTE: Not "hull_current"
}
```

### `player_state` CombatState Object Structure
```python
CombatState(
    hull_current: int,  # Current hull integrity
    hull_max: int,      # Maximum hull integrity
    degradation: dict,
    ...
)
```

### `enemy_ship_dict` Structure
```python
{
    "hull_id": str,
    "module_instances": list,
    "degradation_state": dict,
    # May or may not have hull_current/hull_max directly
}
```

### `enemy_state` CombatState Object Structure
```python
CombatState(
    hull_current: int,  # Current hull integrity
    hull_max: int,      # Maximum hull integrity
    degradation: dict,
    ...
)
```

---

**End of Audit Report**
