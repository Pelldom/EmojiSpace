# Interactive Combat Implementation - Dev Notes

## Overview

Interactive combat has been implemented per `combat_resolution_contract.md` Section 3, requiring round-by-round player decisions instead of instant resolution.

## Contract Alignment

### Player Combat Actions (from combat_resolution_contract.md Section 3)

**Always available:**
- Focus Fire
- Reinforce Shields
- Evasive Maneuvers
- Attempt Escape
- Surrender

**Additional actions may be unlocked by modules:**
- Scan (requires `ship:utility_probe_array`)
- Repair Systems (requires `combat:utility_repair_system` with remaining uses)

## Action ID Convention

Internal action IDs use lower_snake_case derived from contract labels:
- `focus_fire` → "Focus Fire"
- `reinforce_shields` → "Reinforce Shields"
- `evasive_maneuvers` → "Evasive Maneuvers"
- `attempt_escape` → "Attempt Escape"
- `surrender` → "Surrender"

The engine accepts both contract names and lower_snake_case IDs for backward compatibility.

## Hard-Stop Contract for Pending Combat

When combat is initiated (player chooses "Attack" during an encounter), the engine:

1. Initializes a `_pending_combat` session state
2. Returns `hard_stop=true` with `hard_stop_reason="pending_combat_action"`
3. Includes a `pending_combat` payload in the response:

```json
{
  "hard_stop": true,
  "hard_stop_reason": "pending_combat_action",
  "pending_combat": {
    "combat_id": "CMB-{encounter_id}",
    "encounter_id": "{encounter_id}",
    "round_number": 1,
    "player_hull_pct": 100,
    "enemy_hull_pct": 100,
    "allowed_actions": [
      {"id": "focus_fire", "label": "Focus Fire"},
      {"id": "reinforce_shields", "label": "Reinforce Shields"},
      {"id": "evasive_maneuvers", "label": "Evasive Maneuvers"},
      {"id": "attempt_escape", "label": "Attempt Escape"},
      {"id": "surrender", "label": "Surrender"}
    ]
  }
}
```

## Command Format

To process a combat round, send:

```json
{
  "type": "combat_action",
  "action": "focus_fire",  // or "Focus Fire" (both accepted)
  "encounter_id": "{encounter_id}"  // optional, for validation
}
```

## Round Processing

Each `combat_action` command:
1. Processes exactly ONE round
2. Applies player action effects
3. Determines enemy action (deterministic)
4. Resolves attacks in both directions
5. Applies damage and degradation
6. Checks termination conditions (destruction, surrender, escape, max rounds)

If combat continues, returns `hard_stop=true` with `pending_combat` for the next round.
If combat ends, returns normal completion result with combat outcome.

## State Persistence

Combat state is stored in `GameEngine._pending_combat` (in-memory only):
- `combat_id`: Unique combat identifier
- `encounter_id`: Source encounter ID
- `round_number`: Current round (0 = not started, 1+ = in progress)
- `player_state`: `CombatState` for player
- `enemy_state`: `CombatState` for enemy
- `player_ship_state`: Ship state dict
- `enemy_ship_dict`: Enemy ship dict
- `log`: Combat log entries
- `tr_player`, `tr_enemy`: Threat ratings
- `rcp_player`, `rcp_enemy`: Raw combat power

## Determinism

Combat is fully deterministic given:
- `world_seed`
- `encounter_id`
- Player action sequence

Enemy actions are deterministic based on `_default_selector` in `combat_resolver.py`.

## Integration Points

- **Combat Initialization**: `_initialize_combat_session()` in `GameEngine`
- **Round Processing**: `_process_combat_round()` in `GameEngine`
- **Command Handler**: `_execute_combat_action()` in `GameEngine`
- **CLI Integration**: `_travel_menu()` in `run_game_engine_cli.py` handles `pending_combat_action` hard_stop
- **Combat Application**: Uses `apply_combat_result()` from `combat_application.py` when combat ends
- **Post-Combat Rewards**: Uses `_apply_post_combat_rewards_and_salvage()` when NPC is destroyed

## Backward Compatibility

- `HANDLER_COMBAT_STUB` still uses one-shot `resolve_combat()` for simulation controller
- `HANDLER_COMBAT` uses interactive round-by-round processing
- Action names accept both contract format ("Focus Fire") and lower_snake_case ("focus_fire")

## Testing

See `tests/test_interactive_combat.py` for:
- Combat initialization returns `hard_stop` with `pending_combat`
- Round processing increments round number
- Deterministic combat progression with same seed + choices
- Combat termination conditions (destruction, surrender, escape, max rounds)
