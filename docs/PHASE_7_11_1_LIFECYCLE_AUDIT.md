# Phase 7.11.1 — Lifecycle Audit & Legacy Removal Verification

## Audit Results

### 1. Canonical Mission Storage

**Single Source of Truth: CONFIRMED ✓**

- **MissionManager.missions** (`Dict[str, MissionEntity]`) is the authoritative storage
  - Location: `src/mission_manager.py:16`
  - All mission objects are stored here
  - MissionManager owns all mission objects

- **PlayerState** stores only mission IDs (references, not objects):
  - `active_missions: List[str]` - mission IDs only
  - `completed_missions: List[str]` - mission IDs only
  - `failed_missions: List[str]` - mission IDs only
  - Location: `src/player_state.py:55-57`

**No Duplication:**
- Mission objects are NOT duplicated between MissionManager and PlayerState
- PlayerState only maintains lists of mission IDs for tracking active/completed/failed states
- All mission object access goes through `mission_manager.missions.get(mission_id)`

**Architecture:**
```
MissionManager.missions (Dict[str, MissionEntity])  ← Single source of truth
         ↓
PlayerState.active_missions (List[str])              ← References only
PlayerState.completed_missions (List[str])          ← References only
PlayerState.failed_missions (List[str])             ← References only
```

---

### 2. days_remaining Decrement Logic

**Issue Found: FIXED ✓**

**Problem:**
- `days_remaining` was being decremented on ALL evaluation events (travel_arrival AND turn_tick)
- This violated the requirement: "days_remaining is decremented ONLY when event_context['event'] == 'turn_tick'"

**Fix Applied:**
- Updated `evaluate_active_missions()` in `src/mission_manager.py:259-263`
- Added explicit check: `if days_remaining is not None and event_type == "turn_tick":`
- Now decrements ONLY on `turn_tick` events

**Before:**
```python
days_remaining = mission.persistent_state.get("days_remaining")
if days_remaining is not None:
    days_remaining -= 1  # ❌ Decremented on ALL events
```

**After:**
```python
days_remaining = mission.persistent_state.get("days_remaining")
if days_remaining is not None and event_type == "turn_tick":
    days_remaining -= 1  # ✓ Decremented ONLY on turn_tick
```

**Confirmation:**
- ✓ `days_remaining` decrements ONLY when `event_context["event"] == "turn_tick"`
- ✓ NOT decremented during travel arrival or other evaluation triggers
- ✓ No double-decrement risk exists in the same turn

---

### 3. Centralized Evaluation Authority

**All Evaluation Routes Through `evaluate_active_missions()`: CONFIRMED ✓**

**Central Authority:**
- Location: `src/mission_manager.py:184` - `evaluate_active_missions()`
- All mission evaluation (delivery and other types) goes through this function
- No other evaluation functions are called independently

**Evaluation Call Sites:**
1. **Travel Arrival (Primary):** `src/game_engine.py:763`
   - Event: `{"event": "travel_arrival", ...}`
   - Triggers: After player arrives at destination

2. **Turn Advance (Secondary):** `src/game_engine.py:4511` → `1132`
   - Event: `{"event": "turn_tick"}`
   - Triggers: When time advances

3. **Combat Complete:** `src/game_engine.py:3959` (FIXED - was legacy)
   - Event: `{"event": "combat_complete"}`
   - Triggers: After combat resolution

**No Duplicate Evaluation Paths:**
- ✓ No `_evaluate_single_mission()` calls found
- ✓ No direct `mission.complete()` or `mission.fail()` calls in production code
- ✓ All evaluation goes through `evaluate_active_missions()`

**Helper Functions (Internal Only):**
- `_evaluate_delivery_mission()` - Called ONLY from within `evaluate_active_missions()`
- `mission_manager.complete()` - Called ONLY from within `_evaluate_delivery_mission()`
- `mission_manager.fail()` - Available but not called independently

---

### 4. Legacy Bounty Evaluation

**Issue Found: FIXED ✓**

**Problem:**
- `_evaluate_bounty_missions()` was called in `src/game_engine.py:3959`
- Function did not exist (would cause runtime error)
- This was a legacy evaluation path outside centralized authority

**Fix Applied:**
- Removed call to non-existent `_evaluate_bounty_missions()`
- Replaced with call to `evaluate_active_missions()` with `event_context={"event": "combat_complete"}`
- All mission types now route through centralized authority

**Before:**
```python
# Evaluate active missions after combat (bounty missions only - handled by legacy method)
self._evaluate_bounty_missions(  # ❌ Function doesn't exist
    logger=self._logger if self._logging_enabled else None,
    turn=context.turn_after,
)
```

**After:**
```python
# Evaluate active missions after combat (all mission types through centralized authority)
evaluate_active_missions(  # ✓ Centralized authority
    mission_manager=self._mission_manager,
    player_state=self.player_state,
    current_system_id=self.player_state.current_system_id,
    current_destination_id=self.player_state.current_destination_id,
    event_context={"event": "combat_complete"},
    logger=self._logger if self._logging_enabled else None,
    turn=context.turn_after,
)
```

**Confirmation:**
- ✓ No legacy evaluation functions remain
- ✓ All mission types route through `evaluate_active_missions()`
- ✓ Even if bounty missions are not yet fully implemented, evaluation remains centralized

---

## Summary

### Confirmations

1. **✓ Single Source of Truth:** MissionManager.missions is the authoritative storage
2. **✓ days_remaining Decrement Gated:** Only decrements on `turn_tick` events
3. **✓ No Duplicate Evaluation Paths:** All evaluation goes through `evaluate_active_missions()`
4. **✓ Legacy Functions Removed:** `_evaluate_bounty_missions()` call removed and replaced

### Files Modified

1. **`src/mission_manager.py`**
   - Fixed `days_remaining` decrement to only occur on `turn_tick` events
   - Line 260: Added `and event_type == "turn_tick"` check

2. **`src/game_engine.py`**
   - Removed legacy `_evaluate_bounty_missions()` call
   - Replaced with `evaluate_active_missions()` call
   - Line 3957-3962: Updated to use centralized authority

### Legacy Functions Removed

- **`_evaluate_bounty_missions()`** - Call removed (function never existed)
  - Replaced with: `evaluate_active_missions()` with `event_context={"event": "combat_complete"}`

---

## Architecture Verification

**Mission Storage:**
```
MissionManager.missions (Dict[str, MissionEntity])  ← Single source of truth
         ↓
PlayerState.active_missions (List[str])              ← References only
```

**Evaluation Flow:**
```
Game Events (travel_arrival, turn_tick, combat_complete)
         ↓
evaluate_active_missions()  ← Centralized authority
         ↓
_evaluate_delivery_mission()  ← Helper (internal only)
         ↓
mission_manager.complete()  ← State transition (internal only)
```

**Time Limit Handling:**
```
evaluate_active_missions()
         ↓
if event_type == "turn_tick" and days_remaining is not None:
    days_remaining -= 1  ← Only on turn_tick
```

---

**Phase 7.11.1 — Lifecycle Audit & Legacy Removal: COMPLETE**

All architectural requirements met. Zero legacy evaluation paths remain.
