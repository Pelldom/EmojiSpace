# Contract Alignment Summary - Interactive Combat

## Changes Made

### 1. Removed Hardcoded Combat Action Labels in CLI
**File**: `src/run_game_engine_cli.py`
**Function**: `_combat_action_menu()`

**Issue**: Function had a hardcoded `action_labels` dictionary that was redundant and could drift from contract.

**Fix**: Removed hardcoded mapping. Function now uses labels directly from `allowed_actions` parameter, which comes from engine's `pending_combat.allowed_actions` list (contract-correct).

**Why**: Per requirement #3 - CLI/UI must NOT hardcode combat action names. It must render from engine's `pending_combat.allowed_actions`.

### 2. Fixed Encounter Hard-Stop Flow
**File**: `src/run_game_engine_cli.py`
**Function**: `_travel_menu()`

**Issue**: Encounter decisions could be skipped (return on invalid selection), allowing travel to continue without resolution.

**Fix**: 
- Changed invalid selection handling to `continue` instead of `return`
- Added numbered option display (1, 2, 3...) for better UX
- Added check in `main()` loop to block menu navigation while encounters/combat are pending

**Why**: Per requirement #5 and `interaction_layer_contract.md` - all encounters must go through Interaction Layer and be resolved before travel continues.

### 3. Ensured Engine Uses Contract Labels
**File**: `src/game_engine.py`
**Function**: `_build_step_result()`

**Verification**: Engine already uses `available_actions()` from `combat_resolver.py`, which returns exact contract labels:
- "Focus Fire"
- "Reinforce Shields"
- "Evasive Maneuvers"
- "Attempt Escape"
- "Surrender"

**Why**: Per requirement #1 - Combat round choice labels MUST be exactly as specified in `combat_resolution_contract.md` Section 3.

### 4. Action ID Mapping
**File**: `src/game_engine.py`
**Function**: `_execute_combat_action()`

**Verification**: Action mapping already correct:
- `focus_fire` <-> "Focus Fire"
- `reinforce_shields` <-> "Reinforce Shields"
- `evasive_maneuvers` <-> "Evasive Maneuvers"
- `attempt_escape` <-> "Attempt Escape"
- `surrender` <-> "Surrender"

**Why**: Per requirement #2 - Internal IDs MAY be snake_case, but mapping must be strict and deterministic.

### 5. Added Tests
**File**: `tests/test_interactive_combat.py`

**New Tests**:
- `test_combat_actions_use_contract_labels()`: Verifies `pending_combat.allowed_actions` contains exact contract labels and no incorrect labels like "Focus Weapons"
- `test_encounter_decision_blocks_travel()`: Verifies that `pending_encounter_decision` hard_stop blocks travel until resolved

**Why**: Per requirement - tests proving contract-accurate labels and that pending_encounter_decision blocks travel until resolved.

## Contract Compliance

✅ **Requirement #1**: Combat round choice labels are exactly as specified in contract
✅ **Requirement #2**: Internal IDs use snake_case with strict mapping to contract names
✅ **Requirement #3**: CLI does not hardcode combat action names - uses engine's `pending_combat.allowed_actions`
✅ **Requirement #4**: No band-level phrases like "Focus Weapons" in UI
✅ **Requirement #5**: Encounter hard-stop flow blocks travel until resolved

## Files Changed

1. **src/run_game_engine_cli.py**
   - Removed hardcoded `action_labels` dict from `_combat_action_menu()`
   - Updated `_travel_menu()` to force encounter/combat resolution (no early returns)
   - Added numbered option display for encounters
   - Added check in `main()` to block menu navigation while encounters/combat pending

2. **tests/test_interactive_combat.py**
   - Added `test_combat_actions_use_contract_labels()` to verify contract labels
   - Added `test_encounter_decision_blocks_travel()` to verify encounter blocking

3. **docs/contract_alignment_summary.md** (this file)
   - Documentation of changes

## No Changes Required

- `src/game_engine.py`: Already uses contract-correct labels from `combat_resolver.available_actions()`
- `src/combat_resolver.py`: Already returns exact contract labels per Section 3
- Action ID mapping: Already correct and deterministic
