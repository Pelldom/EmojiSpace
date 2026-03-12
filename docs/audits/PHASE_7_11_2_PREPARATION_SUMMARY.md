# Phase 7.11.2 — Preparation Patch Summary

## Objective

Add two REQUIRED mission schema fields:
- `payout_policy`: "auto" or "claim_required"
- `claim_scope`: "none", "source_entity", or "any_source_type"

## Modified Files

### 1. `src/mission_entity.py`

**Changes:**
- Added `payout_policy: str = ""` field to `MissionEntity`
- Added `claim_scope: str = ""` field to `MissionEntity`
- Added `_validate_payout_fields()` function with strict validation:
  - Both fields must be present (not empty)
  - Allowed values enforced
  - Combination rules enforced:
    - `payout_policy="auto"` → `claim_scope` MUST be `"none"`
    - `payout_policy="claim_required"` → `claim_scope` MUST be `"source_entity"` or `"any_source_type"`
- Updated `from_dict()` to call `_validate_payout_fields()` after deserialization
- Updated `to_dict()` to serialize both fields

**Validation Rules:**
- Raises `ValueError` for missing fields
- Raises `ValueError` for invalid values
- Raises `ValueError` for invalid combinations
- No silent correction, no fallback behavior

### 2. `src/mission_factory.py`

**Changes:**
- Updated `create_mission()` signature to require:
  - `payout_policy: str`
  - `claim_scope: str`
- Updated `create_delivery_mission()` to set defaults:
  - `payout_policy = "auto"`
  - `claim_scope = "none"`
- Both functions now explicitly pass these fields to `MissionEntity` constructor

### 3. `src/game_engine.py`

**Changes:**
- Updated `create_mission()` call to include:
  - `payout_policy="claim_required"`
  - `claim_scope="source_entity"`
- Fixed `source_type` to use mapped value (not hardcoded "system")

### 4. Test Files Updated

**`src/integration_test.py`:**
- Updated all `create_mission()` calls to include `payout_policy` and `claim_scope`
- Updated direct `MissionEntity()` instantiations to include both fields
- Fixed `source_type` values to use allowed values ("bar" instead of "npc", "system")

**`src/cli_test.py`:**
- Updated `create_mission()` calls to include `payout_policy` and `claim_scope`
- Fixed `source_type` values to use allowed values

## Validation Results

All validation tests passed:

1. ✓ **Required Fields:** Both `payout_policy` and `claim_scope` are required
2. ✓ **Allowed Values:** Invalid values are rejected with clear error messages
3. ✓ **Combination Rules:** Invalid combinations are rejected:
   - `auto` + `source_entity` → rejected
   - `claim_required` + `none` → rejected
   - `auto` + `none` → valid
   - `claim_required` + `source_entity` → valid
   - `claim_required` + `any_source_type` → valid
4. ✓ **Serialization:** Fields serialize and deserialize correctly
5. ✓ **Delivery Mission Defaults:** Delivery missions default to `payout_policy="auto"` and `claim_scope="none"`

## Schema Enforcement

**Confirmed:**
- ✓ All missions must contain `payout_policy`
- ✓ All missions must contain `claim_scope`
- ✓ Invalid combinations raise `ValueError`
- ✓ No mission can be created without explicit `payout_policy` and `claim_scope`
- ✓ Delivery missions still offer and complete normally
- ✓ Determinism preserved
- ✓ No references to removed `mission.rewards` field remain
- ✓ No legacy evaluation paths reintroduced

## Example Delivery Mission Object

```json
{
  "mission_id": "MIS-34c7d7e47b",
  "mission_type": "delivery",
  "mission_tier": 1,
  "mission_state": "offered",
  "payout_policy": "auto",
  "claim_scope": "none",
  "source": {
    "source_type": "bar",
    "source_id": "test_source"
  },
  "origin": {
    "system_id": "SYS-001",
    "destination_id": "SYS-001-DST-01"
  },
  "target": {
    "target_type": "destination",
    "target_id": "SYS-001-DST-02",
    "system_id": "SYS-001"
  },
  "distance_ly": 0,
  "reward_profile_id": "mission_delivery",
  "objectives": [
    {
      "objective_id": "OBJ-1",
      "objective_type": "deliver_cargo",
      "status": "pending",
      "parameters": {
        "goods": [
          {
            "good_id": "GOOD-001",
            "quantity": 1
          }
        ]
      }
    }
  ]
}
```

## Engine Behavior

**Confirmed:**
- ✓ No payout logic implemented (as required)
- ✓ No reward materialization logic added
- ✓ Mission evaluation logic unchanged
- ✓ Mission completion logic unchanged
- ✓ No inference based on `source_type`
- ✓ No hardcoded behavior based on `source_type`

## Legacy Code

**Confirmed:**
- ✓ No references to removed `mission.rewards` field remain
- ✓ No legacy evaluation paths reintroduced
- ✓ All mission creation goes through factory functions with explicit fields

## Summary

**Phase 7.11.2 Preparation Patch: COMPLETE**

- Schema fields added and enforced
- Validation rules implemented
- All mission creation updated
- Test files updated
- Engine behavior unchanged
- No legacy code paths remain

The mission schema is now ready for Phase 7.11.2 reward materialization implementation.
