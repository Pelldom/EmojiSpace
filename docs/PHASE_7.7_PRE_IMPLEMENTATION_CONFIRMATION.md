# Phase 7.7 - Pre-Implementation Confirmation Report

**Date:** 2024-12-19  
**Status:** Inspection-Only (No Code Modifications)  
**Purpose:** Confirm architecture safety for mission-NPC binding implementation

---

## 1. Mission Persistence

### 1.1 MissionEntity Serialization

**Answer:** ✅ **YES - Fully Implemented**

**File:** `src/mission_entity.py`

**Implementation:**
- `MissionEntity.to_dict()` exists (lines 84-119)
  - Serializes all fields including `mission_giver_npc_id` and `target_npc_id` (lines 106-107)
  - Uses `_enum_to_str()` helper for enum fields
  - Handles all field types: strings, lists, dicts, enums, optional values

- `MissionEntity.from_dict()` exists (lines 76-82)
  - Uses `setattr()` loop: `for key, value in payload.items(): if hasattr(state, key): setattr(state, key, value)`
  - **This pattern automatically handles new fields** - if a new field exists on the class, it will be set from payload
  - **Backward compatible** - missing fields in payload are ignored (no error)

**Lines:** 76-82 (`from_dict`), 84-119 (`to_dict`)

---

### 1.2 MissionManager Serialization

**Answer:** ✅ **YES - Fully Implemented**

**File:** `src/mission_manager.py`

**Implementation:**
- `MissionManager.to_dict()` exists (lines 91-95)
  - Serializes: `{"missions": {mission_id: mission.to_dict() for ...}, "offered": list(self.offered)}`
  - Calls `mission.to_dict()` for each mission entity

- `MissionManager.from_dict()` exists (lines 97-106)
  - Creates new `MissionManager()` instance
  - Deserializes missions: `MissionEntity.from_dict(data)` for each mission
  - Sets `mission.mission_id = mission_id` after deserialization (line 103)
  - Restores `offered` list

**Lines:** 91-95 (`to_dict`), 97-106 (`from_dict`)

---

### 1.3 GameEngine Save/Load Integration

**Answer:** ⚠️ **NOT FOUND - No Save/Load Methods Exist**

**Evidence:**
- Searched `src/game_engine.py` for: `save`, `load`, `to_dict`, `from_dict`, `serialize`, `persist`
- **No save/load methods found in GameEngine class**
- `MissionManager` is stored as `self._mission_manager` (line 157) but no serialization hook exists

**Implication:**
- Mission persistence infrastructure exists (`MissionManager.to_dict/from_dict`)
- **GameEngine does not currently expose save/load**
- Adding new fields to `MissionEntity` is safe (will serialize/deserialize correctly)
- **Future save/load implementation will need to call `self._mission_manager.to_dict()`**

**Files:**
- `src/game_engine.py:157` (MissionManager instance)
- No save/load methods found

---

### 1.4 Safe Field Addition

**Answer:** ✅ **YES - Safe to Add New Fields**

**Reasoning:**
- `MissionEntity.from_dict()` uses `setattr()` with `hasattr()` check
- New fields added to `MissionEntity` will:
  - Be serialized by `to_dict()` (explicit field listing in lines 85-119)
  - Be deserialized by `from_dict()` if present in payload (setattr will set them)
  - Be ignored if missing in old payloads (backward compatible)

**Caveat:**
- If adding new **required** fields, must ensure default values in dataclass field definition
- Optional fields (e.g., `str | None`) are safe with `None` default

**File:** `src/mission_entity.py:76-82` (`from_dict` implementation)

---

### 1.5 Serialization Logic File Locations

**Exact File References:**
- `src/mission_entity.py:76-82` - `MissionEntity.from_dict()`
- `src/mission_entity.py:84-119` - `MissionEntity.to_dict()`
- `src/mission_manager.py:91-95` - `MissionManager.to_dict()`
- `src/mission_manager.py:97-106` - `MissionManager.from_dict()`

**GameEngine Integration:**
- `src/game_engine.py:157` - `self._mission_manager = MissionManager()` (storage location)
- **No GameEngine save/load methods found**

---

## 2. NPC Elevation Safety

### 2.1 Runtime Tier 2 NPC Creation API

**Answer:** ✅ **YES - API Exists**

**File:** `src/npc_registry.py`

**Implementation:**
- `NPCRegistry.add(npc: NPCEntity, logger=None, turn: int = 0)` exists (lines 12-20)
  - Accepts `NPCEntity` with any persistence tier
  - **Filters out Tier 1** (line 13-14: `if npc.persistence_tier == NPCPersistenceTier.TIER_1: return`)
  - **Accepts Tier 2 and Tier 3** (stored in `self._by_id` and `self._by_location`)
  - Logs registry change

**Usage Pattern:**
```python
npc = NPCEntity(
    npc_id=npc_id,
    persistence_tier=NPCPersistenceTier.TIER_2,  # Tier 2 creation
    display_name="...",
    current_location_id=location_id,
    current_system_id=system_id,
)
registry.add(npc, logger=logger, turn=turn)
```

**File:** `src/npc_registry.py:12-20`

---

### 2.2 NPC Tier Mutation Safety

**Answer:** ✅ **YES - Tier Can Be Mutated**

**Evidence:**
- `NPCEntity` is `@dataclass` (not `@dataclass(frozen=True)`) (line 14 in `npc_entity.py`)
- `persistence_tier: NPCPersistenceTier = NPCPersistenceTier.TIER_1` is a regular field (line 33)
- **Direct assignment is allowed**: `npc.persistence_tier = NPCPersistenceTier.TIER_2`

**File:** `src/npc_entity.py:14, 33`

---

### 2.3 New NPCEntity Creation vs Mutation

**Answer:** ✅ **EITHER APPROACH IS SAFE**

**Option A - Direct Mutation:**
```python
existing_npc = registry.get(npc_id)
if existing_npc:
    existing_npc.persistence_tier = NPCPersistenceTier.TIER_2
    registry.update(existing_npc, logger=logger, turn=turn)
```

**Option B - Create New:**
```python
npc = NPCEntity(
    npc_id=npc_id,
    persistence_tier=NPCPersistenceTier.TIER_2,
    # ... other fields
)
registry.add(npc, logger=logger, turn=turn)
```

**Recommendation:**
- **Option B (Create New)** is safer because:
  - Ensures all fields are explicitly set
  - Avoids partial state from existing NPC
  - Matches existing pattern in `npc_placement.py` (lines 23-31)

**File:** `src/npc_registry.py:31-35` (`update()` method exists for mutation path)

---

### 2.4 NPC Registry Insertion File Locations

**Exact File References:**
- `src/npc_registry.py:12-20` - `NPCRegistry.add()` method
- `src/npc_registry.py:31-35` - `NPCRegistry.update()` method (for mutation path)
- `src/npc_entity.py:14-50` - `NPCEntity` dataclass definition
- `src/npc_entity.py:33` - `persistence_tier` field definition

**Example Usage:**
- `src/npc_placement.py:23-31` - Creates Tier 3 NPC and calls `registry.add()`

---

## 3. Correct Elevation Hook

### 3.1 Mission Accept Call Stack

**Call Stack Trace:**

1. **Entry Point:** `GameEngine.execute(command)` (line 162)
   - Parses command, creates `EngineContext`

2. **Command Routing:** `execute()` -> `_execute_location_action()` (line 192)
   - File: `src/game_engine.py:748`
   - Extracts `action_id` and `kwargs` from payload

3. **Action Dispatch:** `_execute_location_action()` -> `_execute_mission_accept()` (line 796-797)
   - File: `src/game_engine.py:796-797`
   - Condition: `if action_id == "mission_accept"`

4. **Mission Acceptance:** `_execute_mission_accept()` -> `_mission_manager.accept()` (line 666-671)
   - File: `src/game_engine.py:655-679`
   - Validates location, mission_id, offered status
   - Calls `self._mission_manager.accept(...)` (line 666)
   - Checks return value (line 672)

5. **Event Emission:** `_execute_mission_accept()` -> `self._event()` (line 674-679)
   - File: `src/game_engine.py:674-679`
   - Emits success event after acceptance

**Complete Call Stack:**
```
GameEngine.execute()
  -> _execute_location_action() [line 192, 748]
    -> _execute_mission_accept() [line 796-797, 655]
      -> _mission_manager.accept() [line 666]
      -> self._event() [line 674]  # AFTER acceptance
```

---

### 3.2 Safest Hook Point

**Answer:** ✅ **In `_execute_mission_accept()` after successful `accept()` but before `_event()`**

**Exact Location:**
- **File:** `src/game_engine.py`
- **Function:** `_execute_mission_accept()`
- **Line Range:** After line 672, before line 674

**Current Code Structure:**
```python
def _execute_mission_accept(self, context: EngineContext, kwargs: dict[str, Any]) -> None:
    # ... validation (lines 656-665)
    accepted = self._mission_manager.accept(...)  # Line 666-671
    if not accepted:  # Line 672
        raise ValueError("mission_accept_failed")
    # ✅ HOOK POINT HERE (after line 672, before line 674)
    self._event(...)  # Line 674-679
```

**Why This Location:**
- ✅ Mission is already accepted (state changed to ACTIVE)
- ✅ Mission entity is accessible via `self._mission_manager.missions.get(mission_id)`
- ✅ Location context is available (`location_id`, `location_type`, `system_id`)
- ✅ NPC registry is accessible (`self._npc_registry`)
- ✅ Logger is available (`self._logger if self._logging_enabled else None`)
- ✅ Turn is available (`int(get_current_turn())`)
- ✅ Before event emission (can include NPC creation in event detail if needed)

**File:** `src/game_engine.py:655-679`

---

### 3.3 Required Context Available at Hook Point

**Available Variables:**
- `location_id: str` - from line 659
- `mission_id: str` - from line 660
- `location` - from line 656 (`_current_location()`)
- `location_type: str` - from `getattr(location, "location_type", "")`
- `system_id: str` - from `self.player_state.current_system_id`
- `mission: MissionEntity` - from `self._mission_manager.missions.get(mission_id)`
- `self._npc_registry: NPCRegistry` - available
- `self._logger` - available
- `turn: int` - from `int(get_current_turn())`

**File:** `src/game_engine.py:655-679`

---

## Summary

### Mission Persistence: ✅ SAFE
- `MissionEntity` fully serializes/deserializes
- `MissionManager` fully serializes/deserializes
- New fields can be added safely (backward compatible)
- **GameEngine save/load not yet implemented** (infrastructure exists)

### NPC Elevation: ✅ SAFE
- Runtime Tier 2 NPC creation API exists (`NPCRegistry.add()`)
- NPC tier can be mutated directly (not frozen dataclass)
- Both mutation and creation approaches are valid
- **Recommendation: Create new NPCEntity** (cleaner, matches existing patterns)

### Hook Point: ✅ CONFIRMED
- **Location:** `src/game_engine.py:672-674` (after successful accept, before event)
- **Function:** `_execute_mission_accept()`
- **All required context available** (location, mission, registry, logger, turn)

---

## File Reference Summary

**Mission Persistence:**
- `src/mission_entity.py:76-82` - `from_dict()`
- `src/mission_entity.py:84-119` - `to_dict()`
- `src/mission_manager.py:91-95` - `to_dict()`
- `src/mission_manager.py:97-106` - `from_dict()`
- `src/game_engine.py:157` - MissionManager storage

**NPC Elevation:**
- `src/npc_registry.py:12-20` - `add()` method
- `src/npc_registry.py:31-35` - `update()` method
- `src/npc_entity.py:14, 33` - NPCEntity definition and tier field
- `src/npc_placement.py:23-31` - Example Tier 3 creation pattern

**Hook Point:**
- `src/game_engine.py:655-679` - `_execute_mission_accept()` function
- `src/game_engine.py:672-674` - **Exact hook insertion point**

---

**End of Confirmation Report**
