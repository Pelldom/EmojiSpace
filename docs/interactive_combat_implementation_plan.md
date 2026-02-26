# Interactive Combat Implementation Plan

## Current State Analysis

### Problem
- When player selects "Attack" during an encounter, combat resolves instantly via `_resolve_encounter_combat()` → `_run_ship_combat()`
- `_run_ship_combat()` runs all rounds to completion in a single call
- No round-by-round player interaction
- Violates `combat_resolution_contract.md` which requires interactive round-by-round combat

### Current Flow
1. Encounter decision "attack" → `_resolve_encounter()` → `dispatch_player_action()` → `HANDLER_COMBAT`
2. `_resolve_encounter()` handles `HANDLER_COMBAT` → calls `_resolve_encounter_combat()`
3. `_resolve_encounter_combat()` → calls `_run_ship_combat()` with optional `get_player_action` callback
4. `_run_ship_combat()` runs entire combat loop (rounds 1 to max_rounds) in one call
5. Returns `CombatResult` with final outcome

### Required Flow (Per Contract)
1. Encounter decision "attack" → Initialize combat session → Return `hard_stop` with `pending_combat`
2. CLI displays combat menu → Player selects action → Send `combat_action` command
3. Engine processes ONE round → Update state → Check termination
4. If combat continues: Return `hard_stop` with `pending_combat` (repeat from step 2)
5. If combat ends: Apply results → Clear pending combat → Continue normal flow

---

## Implementation Strategy

### Phase 1: Combat Session State Management

#### 1.1 Add Pending Combat State
**File**: `src/game_engine.py`
**Location**: `__init__` method (around line 108)

```python
# Add after _pending_travel initialization
self._pending_combat: dict[str, Any] | None = None
```

**State Structure**:
```python
{
    "combat_id": str,  # e.g., "CMB-{encounter_id}"
    "encounter_id": str,
    "spec": EncounterSpec,  # Original encounter spec
    "player_ship_entity": ShipEntity,
    "enemy_ship_dict": dict,
    "round_number": int,  # Current round (0 = not started, 1+ = in progress)
    "player_state": CombatState,  # From combat_resolver
    "enemy_state": CombatState,
    "player_ship_state": dict,  # Ship state dict
    "tr_player": int,
    "tr_enemy": int,
    "rcp_player": int,
    "rcp_enemy": int,
    "log": list[dict],  # Combat log entries
    "context": EngineContext,  # Original context
}
```

#### 1.2 Import HANDLER_COMBAT
**File**: `src/game_engine.py`
**Location**: Import section (around line 17-26)

```python
from interaction_layer import (
    ACTION_IGNORE,
    HANDLER_COMBAT,  # ADD THIS
    HANDLER_COMBAT_STUB,
    ...
)
```

---

### Phase 2: Combat Initialization

#### 2.1 Create `_initialize_combat_session()` Method
**File**: `src/game_engine.py`
**Location**: After `_get_encounter_options()` (around line 2690)

**Responsibilities**:
- Generate NPC ship (deterministic, using existing `generate_npc_ship()`)
- Get player ship entity
- Initialize combat states using `_create_initial_state_from_ship_state()`
- Calculate TR/RCP values
- Store all state in `self._pending_combat`
- Log "combat_started" event

**Key Points**:
- Use same deterministic seed pattern as existing combat: `world_seed + encounter_id`
- Do NOT process any rounds yet
- Do NOT apply any damage yet

#### 2.2 Modify Combat Handler
**File**: `src/game_engine.py`
**Location**: `_resolve_encounter()` method, `HANDLER_COMBAT` branch (around line 2217)

**Current Code**:
```python
elif handler == HANDLER_COMBAT_STUB:
    combat = self._resolve_encounter_combat(spec)
    resolver_outcome = {...}
```

**New Code**:
```python
elif handler == HANDLER_COMBAT or handler == HANDLER_COMBAT_STUB:
    # Initialize interactive combat session
    self._initialize_combat_session(spec, context)
    
    # Set hard_stop to pause for player combat action
    context.hard_stop = True
    context.hard_stop_reason = "pending_combat_action"
    
    resolver_outcome = {
        "resolver": "combat",
        "status": "combat_started",
    }
```

**Note**: Keep `HANDLER_COMBAT_STUB` for backward compatibility (simulation controller may still use it)

---

### Phase 3: Round-by-Round Processing

#### 3.1 Create `_process_combat_round()` Method
**File**: `src/game_engine.py`
**Location**: After `_initialize_combat_session()`

**Signature**:
```python
def _process_combat_round(self, player_action: str) -> dict[str, Any]:
    """
    Process one round of interactive combat.
    
    Args:
        player_action: Player's chosen combat action (Focus Fire, Reinforce Shields, etc.)
    
    Returns:
        {
            "round_number": int,
            "player_action": str,
            "enemy_action": str,
            "player_hull_current": int,
            "player_hull_max": int,
            "enemy_hull_current": int,
            "enemy_hull_max": int,
            "combat_ended": bool,
            "combat_result": CombatResult | None,  # Only if combat_ended
        }
    """
```

**Implementation Strategy**:
- Extract round processing logic from `_run_ship_combat()` (lines 2815-3150)
- Key steps per round:
  1. Get available actions for player and enemy
  2. Validate player_action
  3. Get enemy action (deterministic, using existing `_deterministic_enemy_selector`)
  4. Check surrender (if either side surrenders, end combat)
  5. Calculate bands (weapon/defense/engine) for both sides
  6. Apply RPS matrix adjustments
  7. Resolve attacks in both directions
  8. Apply damage and degradation
  9. Check for escape attempt (if player chose "Attempt Escape")
  10. Check for destruction (hull <= 0)
  11. Check max rounds
  12. Update stored state in `_pending_combat`
  13. Return round result

**Key Functions to Reuse**:
- `available_actions()` - from combat_resolver
- `_effective_from_assembled()` - band calculation
- `_resolve_attack()` - attack resolution
- `_apply_damage_and_degradation()` - damage application
- `_escape_attempt()` - escape logic (routes to pursuit_resolver)
- `_repair_once()` - repair logic
- `_deterministic_enemy_selector()` - enemy action selection

**State Persistence**:
- After each round, update `self._pending_combat["player_state"]` and `self._pending_combat["enemy_state"]`
- Update `self._pending_combat["round_number"]`
- Append to `self._pending_combat["log"]`

#### 3.2 Create `_execute_combat_action()` Command Handler
**File**: `src/game_engine.py`
**Location**: After `_execute_encounter_decision()` (around line 2400)

**Signature**:
```python
def _execute_combat_action(self, context: EngineContext, payload: dict[str, Any]) -> None:
    """
    Execute player combat action for one round.
    
    Command format:
    {
        "type": "combat_action",
        "action": "Focus Fire" | "Reinforce Shields" | "Evasive Maneuvers" | "Attempt Escape" | "Surrender"
    }
    """
```

**Responsibilities**:
1. Validate `self._pending_combat` exists
2. Extract `action` from payload
3. Call `_process_combat_round(action)`
4. If `combat_ended`:
   - Apply combat result via `apply_combat_result()`
   - Apply post-combat rewards if NPC destroyed
   - Clear `self._pending_combat`
   - Set `context.hard_stop = False`
5. If combat continues:
   - Set `context.hard_stop = True`
   - Set `context.hard_stop_reason = "pending_combat_action"`
   - Log round completed

#### 3.3 Add Command Routing
**File**: `src/game_engine.py`
**Location**: `execute()` method, command dispatcher (around line 323)

```python
elif command_type == "encounter_decision":
    self._execute_encounter_decision(context, payload)
elif command_type == "combat_action":  # ADD THIS
    self._execute_combat_action(context, payload)
```

**Location**: `_parse_command()` method, allowed commands (around line 2457)

```python
allowed.add("encounter_decision")
allowed.add("combat_action")  # ADD THIS
```

---

### Phase 4: Result Payload Updates

#### 4.1 Add `pending_combat` Payload
**File**: `src/game_engine.py`
**Location**: `_build_step_result()` method (around line 2462)

**Add after pending_encounter handling**:
```python
# Add pending_combat payload if hard_stop is due to pending combat action
if context.hard_stop and context.hard_stop_reason == "pending_combat_action" and self._pending_combat:
    from combat_resolver import available_actions
    player_ship_state = self._pending_combat.get("player_ship_state")
    player_state = self._pending_combat.get("player_state")
    enemy_state = self._pending_combat.get("enemy_state")
    
    if player_ship_state and player_state:
        allowed_actions = available_actions(player_ship_state, player_state)
        round_number = self._pending_combat.get("round_number", 0) + 1  # Next round
        player_hull_pct = int((player_state.hull_current * 100) // player_state.hull_max) if player_state.hull_max > 0 else 0
        enemy_hull_pct = int((enemy_state.hull_current * 100) // enemy_state.hull_max) if enemy_state and enemy_state.hull_max > 0 else 0
        
        result["pending_combat"] = {
            "combat_id": self._pending_combat.get("combat_id", ""),
            "encounter_id": self._pending_combat.get("encounter_id", ""),
            "round_number": round_number,
            "player_hull_pct": player_hull_pct,
            "enemy_hull_pct": enemy_hull_pct,
            "allowed_actions": allowed_actions,
        }
```

---

### Phase 5: CLI Integration

#### 5.1 Update `_combat_action_menu()` Function
**File**: `src/run_game_engine_cli.py`
**Location**: Already exists (around line 2081)

**Current**: Function exists but may need updates for action name mapping

**Ensure it uses exact contract names**:
- "Focus Fire"
- "Reinforce Shields"
- "Evasive Maneuvers"
- "Attempt Escape"
- "Surrender"
- Plus any unlocked actions (Scan, Repair Systems)

#### 5.2 Add Pending Combat Handling in Main Loop
**File**: `src/run_game_engine_cli.py`
**Location**: `main()` function or travel menu handler

**After handling `pending_encounter`**:
```python
# Handle pending combat
if result.get("hard_stop") and result.get("hard_stop_reason") == "pending_combat_action":
    pending_combat = result.get("pending_combat")
    if pending_combat:
        # Display combat menu and get player action
        action = _combat_action_menu(
            round_number=pending_combat.get("round_number", 1),
            player_hull_pct=pending_combat.get("player_hull_pct", 0),
            enemy_hull_pct=pending_combat.get("enemy_hull_pct", 0),
            allowed_actions=pending_combat.get("allowed_actions", []),
        )
        
        # Send combat action command
        result = engine.execute({
            "type": "combat_action",
            "action": action,
        })
        
        # Loop until combat ends (hard_stop becomes False)
        continue
```

**Integration Point**: This should be in the main CLI loop, similar to how `pending_encounter` is handled

---

### Phase 6: Escape Attempt Integration

#### 6.1 Ensure Escape Routes to Pursuit Resolver
**File**: `src/game_engine.py`
**Location**: `_process_combat_round()` method

**When player_action == "Attempt Escape"**:
- Call `_escape_attempt()` from combat_resolver
- This should already route to `pursuit_resolver.resolve_pursuit()`
- If escape succeeds: end combat, return escape result
- If escape fails: continue combat (enemy may still attack this round)

**Verify**: `_escape_attempt()` in `combat_resolver.py` already uses `pursuit_resolver` (from previous implementation)

---

### Phase 7: State Persistence and Ship Updates

#### 7.1 Apply Combat Results When Combat Ends
**File**: `src/game_engine.py`
**Location**: `_execute_combat_action()` method

**When `combat_ended == True`**:
```python
from combat_application import apply_combat_result

combat_result = round_result.get("combat_result")
if combat_result:
    apply_combat_result(
        player_state=self.player_state,
        player_ship_entity=self._pending_combat["player_ship_entity"],
        enemy_ship_entity_or_dict=self._pending_combat["enemy_ship_dict"],
        combat_result=combat_result,
        system_id=self.player_state.current_system_id,
        encounter_id=self._pending_combat["encounter_id"],
        world_seed=self.world_seed,
        logger=self._silent_logger,
        turn=int(get_current_turn()),
    )
    
    # Apply post-combat rewards if NPC destroyed
    if combat_result.winner == "player" and combat_result.outcome == "destroyed":
        self._apply_post_combat_rewards_and_salvage(
            context=context,
            npc_ship_dict=self._pending_combat["enemy_ship_dict"],
            encounter_id=self._pending_combat["encounter_id"],
        )
```

---

### Phase 8: Determinism Preservation

#### 8.1 Ensure Deterministic Enemy Actions
**File**: `src/game_engine.py`
**Location**: `_process_combat_round()` method

**Use existing deterministic selector**:
- Same seed pattern: `world_seed + combat_id + round_number`
- Same logic as in `_run_ship_combat()` (lines 2785-2805)

#### 8.2 Ensure Deterministic RNG
**File**: `src/game_engine.py`
**Location**: `_process_combat_round()` method

**Use `CombatRng` with same seed pattern**:
```python
from combat_resolver import CombatRng
rng = CombatRng(world_seed=str(self.world_seed), salt=f"{combat_id}_combat")
```

**Note**: RNG state should be deterministic per round, not cumulative across rounds

---

## Implementation Order

### Step 1: Foundation (Low Risk)
1. Add `_pending_combat` state variable
2. Import `HANDLER_COMBAT`
3. Add `combat_action` to allowed commands
4. Add command routing for `combat_action`

### Step 2: Combat Initialization (Medium Risk)
1. Create `_initialize_combat_session()` method
2. Modify combat handler to call initialization and return `hard_stop`
3. Add `pending_combat` payload to `_build_step_result()`

### Step 3: Round Processing (High Risk - Complex)
1. Extract round logic from `_run_ship_combat()` into `_process_combat_round()`
2. Implement state persistence between rounds
3. Handle all termination conditions (destruction, surrender, escape, max rounds)

### Step 4: Command Handler (Low Risk)
1. Create `_execute_combat_action()` method
2. Wire to command dispatcher
3. Handle combat end vs. continue logic

### Step 5: CLI Integration (Low Risk)
1. Update main loop to handle `pending_combat`
2. Ensure `_combat_action_menu()` uses correct action names
3. Test round-by-round flow

### Step 6: Testing (Critical)
1. Test combat starts and returns `pending_combat`
2. Test each round processes correctly
3. Test all termination conditions
4. Test determinism with same seed + same choices
5. Test escape routing to pursuit resolver

---

## Key Design Decisions

### Decision 1: State Storage
**Choice**: Store full combat state in `_pending_combat` dict
**Rationale**: 
- Keeps state isolated from other systems
- Easy to clear when combat ends
- No need to persist to disk (in-memory only)

### Decision 2: Round Processing Extraction
**Choice**: Extract round logic into separate method rather than refactoring `_run_ship_combat()`
**Rationale**:
- `_run_ship_combat()` still used by simulation controller
- Minimal changes to existing code
- Can reuse existing round logic

### Decision 3: Command Naming
**Choice**: Use `combat_action` (not `encounter_combat_action` or `combat_round`)
**Rationale**:
- Clear and concise
- Matches pattern of `encounter_decision`
- Action-oriented naming

### Decision 4: Backward Compatibility
**Choice**: Keep `HANDLER_COMBAT_STUB` support for simulation controller
**Rationale**:
- Simulation may still need one-shot combat
- Avoids breaking existing tests
- Can deprecate later if needed

---

## Risk Assessment

### High Risk Areas

1. **Round Logic Extraction**
   - **Risk**: Missing edge cases when extracting from `_run_ship_combat()`
   - **Mitigation**: 
     - Copy logic exactly, then adapt for single-round processing
     - Test each termination condition separately
     - Compare results with original `_run_ship_combat()` for same inputs

2. **State Persistence**
   - **Risk**: State corruption between rounds
   - **Mitigation**:
     - Store all necessary state in `_pending_combat`
     - Validate state before each round
     - Add defensive checks for missing state

3. **Determinism**
   - **Risk**: Different results with same seed + choices
   - **Mitigation**:
     - Use exact same seed patterns as existing code
     - Test determinism explicitly
     - Ensure RNG channels are isolated

### Medium Risk Areas

1. **Escape Integration**
   - **Risk**: Escape not routing correctly to pursuit resolver
   - **Mitigation**: Verify `_escape_attempt()` already uses `pursuit_resolver` (from previous work)

2. **Combat End Handling**
   - **Risk**: Results not applied correctly when combat ends
   - **Mitigation**: Reuse existing `apply_combat_result()` and `_apply_post_combat_rewards_and_salvage()`

### Low Risk Areas

1. **CLI Integration**
   - **Risk**: Menu display issues
   - **Mitigation**: Simple menu function, easy to test

2. **Command Routing**
   - **Risk**: Command not recognized
   - **Mitigation**: Follow existing patterns, add to allowed list

---

## Testing Strategy

### Unit Tests

1. **Combat Initialization**
   - Test `_initialize_combat_session()` creates correct state
   - Test NPC ship generation is deterministic
   - Test state structure is complete

2. **Round Processing**
   - Test single round processes correctly
   - Test state updates after round
   - Test each termination condition separately

3. **Command Handler**
   - Test `_execute_combat_action()` validates input
   - Test combat end handling
   - Test combat continue handling

### Integration Tests

1. **Full Combat Flow**
   - Test: Attack → Initialize → Round 1 → Round 2 → ... → End
   - Verify: Each round prompts for action
   - Verify: Combat ends correctly

2. **Determinism Test**
   - Test: Same seed + same choices → same results
   - Test: Different choices → different results (but deterministic)

3. **Escape Test**
   - Test: "Attempt Escape" routes to pursuit resolver
   - Test: Escape success ends combat
   - Test: Escape failure continues combat

### CLI Tests

1. **Menu Display**
   - Test: Correct actions shown
   - Test: Hull percentages displayed
   - Test: Round number displayed

2. **Input Handling**
   - Test: Invalid action rejected
   - Test: Valid action processed

---

## Files to Modify

1. **src/game_engine.py**
   - Add `_pending_combat` state
   - Add `_initialize_combat_session()` method
   - Add `_process_combat_round()` method
   - Add `_execute_combat_action()` method
   - Modify combat handler
   - Update `_build_step_result()` for `pending_combat` payload
   - Add command routing

2. **src/run_game_engine_cli.py**
   - Update main loop to handle `pending_combat`
   - Ensure `_combat_action_menu()` uses correct names

3. **tests/test_interactive_combat.py** (may need updates)
   - Add tests for round-by-round processing
   - Add determinism tests

---

## Estimated Complexity

- **Lines of Code**: ~500-800 new lines (mostly extracted from `_run_ship_combat()`)
- **Files Modified**: 2-3 files
- **Risk Level**: Medium-High (due to round logic extraction)
- **Time Estimate**: 4-6 hours for careful implementation + testing

---

## Questions for Review

1. **State Persistence**: Should combat state survive engine restarts? (Current plan: No, in-memory only)

2. **Simulation Controller**: Should simulation controller continue using one-shot combat, or also use interactive? (Current plan: Keep one-shot for simulation)

3. **Round Logic**: Should we refactor `_run_ship_combat()` to call `_process_combat_round()` internally, or keep them separate? (Current plan: Keep separate for now)

4. **Error Handling**: What should happen if `_pending_combat` is missing when `combat_action` is called? (Current plan: Raise ValueError)

5. **Max Rounds**: Should max rounds be enforced per round, or only checked at end? (Current plan: Check each round)

---

## Next Steps

1. Review this plan
2. Confirm design decisions
3. Answer questions above
4. Proceed with implementation in order (Step 1 → Step 6)
