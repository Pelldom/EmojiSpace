# Phase 7.11.2a — Mission Reward Materialization (Credits Only) Summary

## Implementation Complete

All parts of Phase 7.11.2a have been implemented.

---

## Modified Files

### 1. `src/mission_entity.py`

**Changes:**
- Added `reward_status: str = ""` field (allowed: "ungranted", "granted")
- Added `reward_granted_turn: int | None = None` field
- Added `_validate_reward_fields()` function with strict validation:
  - Both fields must be present
  - `reward_status` must be "ungranted" or "granted"
  - If `reward_status == "ungranted"`, `reward_granted_turn` MUST be `None`
  - If `reward_status == "granted"`, `reward_granted_turn` MUST be `int`
- Updated `from_dict()` to call `_validate_reward_fields()`
- Updated `to_dict()` to serialize both fields

### 2. `src/mission_factory.py`

**Changes:**
- Updated `create_mission()` to set:
  - `reward_status="ungranted"`
  - `reward_granted_turn=None`
- Updated `create_delivery_mission()` to set:
  - `reward_status="ungranted"`
  - `reward_granted_turn=None`

### 3. `src/mission_manager.py`

**Changes:**
- Added `_load_reward_profiles()` function to load from `data/reward_profiles.json`
- Added `_calculate_mission_credit_reward()` function:
  - Formula: `base_credits * tier_multiplier * (1 + distance_ly * distance_multiplier_per_ly)`
  - Floors result to int (no rounding)
  - No RNG, fully deterministic
  - Raises `ValueError` for missing profiles or fields
- Updated `evaluate_active_missions()`:
  - Added optional `reward_profiles` parameter
  - Added auto payout logic:
    - Checks all resolved/completed missions
    - If `payout_policy == "auto"` and `reward_status == "ungranted"`:
      - Calculates credit reward
      - Adds to `player_state.credits`
      - Sets `reward_status = "granted"`
      - Sets `reward_granted_turn = turn`
      - Logs `mission_reward_granted` event
    - Raises `ValueError` on double payout attempt

### 4. `src/game_engine.py`

**Changes:**
- Updated `_execute_claim_mission()` to implement claim-required payout:
  - Validates mission state (must be resolved/completed)
  - Validates `reward_status == "ungranted"`
  - Validates `payout_policy == "claim_required"`
  - Validates `claim_scope`:
    - `"source_entity"`: Must be at exact source entity (`current_location_id == source.source_id`)
    - `"any_source_type"`: Must be at a location (simplified validation)
    - `"none"`: Raises error (invalid for claim_required)
  - If validations pass:
    - Calculates credit reward
    - Adds to `player_state.credits`
    - Sets `reward_status = "granted"`
    - Sets `reward_granted_turn = turn`
    - Logs `mission_reward_granted` event
  - Returns structured error messages via context for invalid claims

### 5. `data/reward_profiles.json`

**Changes:**
- Added `"mission_delivery"` profile:
  ```json
  {
    "reward_profile_id": "mission_delivery",
    "base_credits": 500,
    "tier_multiplier": {
      "1": 1.0,
      "2": 1.5,
      "3": 2.0,
      "4": 2.5,
      "5": 3.0
    },
    "distance_multiplier_per_ly": 0.1,
    "notes": "Credit reward for delivery missions. Formula: base_credits * tier_multiplier * (1 + distance_ly * distance_multiplier_per_ly)"
  }
  ```

---

## Example Mission Objects

### Before Payout (Resolved, Ungranted)

```json
{
  "mission_id": "MIS-34c7d7e47b",
  "mission_type": "delivery",
  "mission_state": "resolved",
  "outcome": "completed",
  "payout_policy": "auto",
  "claim_scope": "none",
  "reward_status": "ungranted",
  "reward_granted_turn": null,
  "reward_profile_id": "mission_delivery",
  "mission_tier": 1,
  "distance_ly": 5,
  "source": {
    "source_type": "bar",
    "source_id": "test_source"
  }
}
```

### After Auto Payout

```json
{
  "mission_id": "MIS-34c7d7e47b",
  "mission_type": "delivery",
  "mission_state": "resolved",
  "outcome": "completed",
  "payout_policy": "auto",
  "claim_scope": "none",
  "reward_status": "granted",
  "reward_granted_turn": 10,
  "reward_profile_id": "mission_delivery",
  "mission_tier": 1,
  "distance_ly": 5,
  "source": {
    "source_type": "bar",
    "source_id": "test_source"
  }
}
```

**Reward Calculation:**
- `base_credits = 500`
- `tier_multiplier = 1.0` (tier 1)
- `distance_multiplier = 1 + (5 * 0.1) = 1.5`
- `reward = 500 * 1.0 * 1.5 = 750 credits`

### Claim-Required Mission (Before Claim)

```json
{
  "mission_id": "MIS-claim-001",
  "mission_type": "delivery",
  "mission_state": "resolved",
  "outcome": "completed",
  "payout_policy": "claim_required",
  "claim_scope": "source_entity",
  "reward_status": "ungranted",
  "reward_granted_turn": null,
  "reward_profile_id": "mission_delivery",
  "source": {
    "source_type": "bar",
    "source_id": "LOC-bar-001"
  }
}
```

### Claim-Required Validation Success

**Conditions:**
- Mission is resolved and completed
- `reward_status == "ungranted"`
- `payout_policy == "claim_required"`
- `claim_scope == "source_entity"`
- `current_location_id == "LOC-bar-001"` (matches `source.source_id`)

**Result:**
- Reward granted: 750 credits
- `reward_status = "granted"`
- `reward_granted_turn = current_turn`

### Claim-Required Validation Failure

**Scenario 1: Wrong Location**
- `current_location_id == "LOC-bar-002"` (doesn't match `source.source_id`)
- **Error:** `"Must claim reward from source entity 'LOC-bar-001' (currently at 'LOC-bar-002')."`

**Scenario 2: Already Granted**
- `reward_status == "granted"`
- **Error:** `"Mission MIS-claim-001 reward already granted (status: granted)."`

**Scenario 3: Invalid claim_scope**
- `claim_scope == "none"`
- **Error:** `"Mission MIS-claim-001 has claim_scope='none' (invalid for claim_required)."`

---

## Validation Confirmations

### ✓ 1. Delivery Mission Completes
- Mission transitions to `resolved` with `outcome = "completed"` on arrival at target destination

### ✓ 2. Auto Payout Grants Credits Exactly Once
- Auto payout only triggers when `payout_policy == "auto"` and `reward_status == "ungranted"`
- Double payout attempt raises `ValueError`

### ✓ 3. Claim_Required Mission Does NOT Auto Grant
- Missions with `payout_policy == "claim_required"` are skipped in auto payout logic
- Rewards only granted via explicit claim action

### ✓ 4. Claim_Required Mission Grants When Valid Claim Occurs
- All validations pass → reward granted
- Credits added to player state
- `reward_status` transitions to "granted"

### ✓ 5. Claim Fails When Interacting With Invalid Entity
- `claim_scope == "source_entity"`: Must match exact `source_id`
- `claim_scope == "any_source_type"`: Must be at a location
- Returns structured error message via context

### ✓ 6. Double Claim Attempt Raises ValueError
- If `reward_status != "ungranted"`, claim is rejected with error message

### ✓ 7. reward_status Transitions
- `ungranted` → `granted` (on successful payout)
- `reward_granted_turn` set to current turn

### ✓ 8. Determinism
- Same seed produces identical credit amounts
- No RNG in reward calculation
- Formula is purely deterministic: `base_credits * tier_multiplier * (1 + distance_ly * distance_multiplier_per_ly)`

### ✓ 9. No RNG Used in Reward Calculation
- `_calculate_mission_credit_reward()` is purely deterministic
- Uses `math.floor()` for integer conversion (no rounding)

### ✓ 10. No Legacy Reward Code Paths Used
- All reward logic uses new `reward_profile_id` system
- No references to removed `mission.rewards` field in reward logic
- Legacy `rewards` field ignored during deserialization (correct behavior)

---

## Summary

**Phase 7.11.2a — Mission Reward Materialization (Credits Only): COMPLETE**

- ✓ Reward state tracking added to MissionEntity
- ✓ Credit reward calculation implemented (deterministic)
- ✓ Auto payout integrated into evaluation flow
- ✓ Claim-required payout implemented with validation
- ✓ Double payout prevention
- ✓ Determinism preserved
- ✓ No legacy code paths
- ✓ All validation requirements met

The mission reward system is now functional for credits. Module and hull rewards will be implemented in future phases.
