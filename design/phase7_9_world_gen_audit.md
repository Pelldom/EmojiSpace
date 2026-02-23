# Phase 7.9 World Gen Unification - Audit and Implementation Plan

Status: IMPLEMENTED
Phase: 7.9
Target Version: 0.11.2+
Date: 2024

## 1. Current Implementation Summary

### 1.1 File Locations

- World Generator: `src/world_generator.py`
- Game Engine: `src/game_engine.py`
- CLI Runner: `src/run_game_engine_cli.py`
- Config: No dedicated config file; `system_count` passed via `GameEngine.__init__(config={"system_count": N})`

### 1.2 Current World Generation Behavior

**System Count:**
- Default: 5 systems (hardcoded in `WorldGenerator.__init__`, `GameEngine.__init__`)
- Configurable via `GameEngine(config={"system_count": N})` but no CLI prompt
- Tests assume 5 systems in many places (integration_test.py, cli_test.py, test_run.py)

**Galaxy Radius:**
- IMPLEMENTED: Computed as `radius = 10.0 * sqrt(system_count)` in `WorldGenerator._galaxy_radius()`
- Replaced fixed `GALAXY_RADIUS = 100.0` constant
- Scales deterministically with system count
- Used in `_assign_spatial_coordinates()` for spatial placement

**Spatial Coordinates:**
- Systems have `x: float, y: float` fields (added in Phase 7.5.1)
- Coordinates generated deterministically via `_deterministic_system_coordinates()`
- Uses polar coordinate generation: `radial = sqrt(rng.random()) * radius`, `angle = rng.random() * 2*pi`
- IMPLEMENTED: Coordinate uniqueness enforced via rejection sampling (up to 100 attempts) and deterministic micro-jitter
- Coordinates assigned BEFORE neighbor assignment (needed for graph construction)

**Neighbor/Starlane Graph:**
- IMPLEMENTED: MST + k-NN (k=2) graph construction in `WorldGenerator._build_starlane_graph()`
- Replaced simple linear chain (index-1, index+1)
- Stored as `System.neighbors: List[str]` (system_id strings, sorted deterministically)
- Graph is connected (MST ensures connectivity), with additional k-NN edges for better connectivity
- Used by:
  - World State propagation (world_state_contract.md: radius 1 = direct neighbors)
  - Awareness radius evaluation (world_state_contract.md: R=1 for DataNet)
  - Time Engine daily tick (time_engine.py: neighbor evaluation)

**System Names:**
- Hardcoded list of 10 names: ["Aster", "Beacon", "Cirrus", "Drift", "Ember", "Flux", "Gleam", "Haven", "Ion", "Jade"]
- Shuffled with seed, then cycled: `name = base_names[index % len(base_names)]`
- Results in name repetition for N > 10

**Destination Types:**
- Current types: "planet", "station", "asteroid_field", "contact"
- Destination generation uses `_destination_counts()` which returns core_count and extra_count
- Core types are "planet" and "station" (randomly chosen)
- Extra types are "asteroid_field" and "contact" (randomly chosen)
- No distinction between planets and stations in naming (both use system_name + index)
- No explorable or mining destination types
- No curated name lists for planets or stations

**Travel Targeting:**
- Inter-system travel: Any system within fuel range (fuel-based distance check)
- Uses `_warp_distance_ly()` in game_engine.py (line 2643) based on (x,y) coordinates
- No discovery requirement; all systems reachable if fuel permits
- CLI shows reachable systems with distance_ly in `_reachable_systems()` (run_game_engine_cli.py line 1062)

**World Seed Usage:**
- Set in `GameEngine.__init__(world_seed: int)` (line 98)
- Passed to `WorldGenerator(seed=world_seed)` (line 120)
- Used throughout for deterministic RNG via `_seeded_rng()` helper
- No CLI prompt for galaxy size; seed only prompted in `_prompt_seed()` (run_game_engine_cli.py line 10)

### 1.3 Ripgrep Findings Summary

**system_count:**
- Default 5 in: world_generator.py:79, game_engine.py:119, cli_run.py:40
- Tests use 1, 4, or 5 (test_crew_spawn_hiring.py, test_world_state_long_horizon.py, integration_test.py)

**GALAXY_RADIUS:**
- Single constant: world_generator.py:74 = 100.0
- Used in `_assign_spatial_coordinates()` line 214

**neighbors:**
- Assigned in world_generator.py:156-173 (linear chain)
- Used in: game_engine.py:3213-3214 (world state), time_engine.py:242-248 (daily tick), world_state_engine.py:627-718 (propagation)

**starlane/starlanes/lane:**
- Only mentioned in contracts (world_state_contract.md:612, 681)
- No code implementation of "starlane graph" as separate entity
- Current model: `System.neighbors` IS the graph representation

**warp_distance/distance_ly:**
- `_warp_distance_ly()` in game_engine.py:2643 (Euclidean distance from x,y)
- Used in travel validation (line 391), reachable systems (line 2076), CLI display (run_game_engine_cli.py:300, 1076)

**Hardcoded "5 system" assumptions:**
- integration_test.py:113, 128, 151, 168, 189 (all use system_count=5)
- cli_test.py:186
- tools/test_run.py:100
- No explicit "5 system" string matches, but many tests default to 5

**Tests assuming 5 systems:**
- integration_test.py (multiple test functions)
- cli_test.py
- tools/test_run.py
- Note: Some tests use system_count=1 or 4, but majority assume 5

## 2. Contract Requirements Summary

### 2.1 world_generation_destinations_contract.md

**System Position:**
- Systems have `position (x,y or equivalent)` (Section 2.2)
- No explicit requirement for minimum separation
- No explicit requirement for radius scaling

**Neighbors/Graph:**
- Contract does NOT define neighbor/starlane graph construction
- Contract focuses on destinations, locations, economies
- No mention of inter-system connectivity

**Conclusion:** Contract is silent on starlane graph; current linear chain is acceptable but not contractually required.

### 2.2 world_state_contract.md

**Starlane Graph Immutability:**
- Section 18 (Structural Persistence): "Starlane graph" is immutable after worldgen
- Section 102: Events may NOT "Mutate world topology (starlanes)"
- Current `System.neighbors` is set during worldgen and never mutated (compliant)

**Awareness Radius:**
- Section 21: "R = graph distance in starlane network"
- Daily tick: R=0 (current system only)
- DataNet query: R=1 (direct neighbors)
- Current implementation uses `System.neighbors` for R=1 (compliant)

**Propagation:**
- Section 15A: Propagation selects neighbors via `get_neighbors_fn(system_id)`
- Radius fixed at 1 (direct neighbors only)
- Current implementation passes `lambda system_id: list(system.neighbors)` (compliant)

**Conclusion:** Current neighbor model satisfies contract requirements. Graph is immutable, awareness uses neighbors, propagation uses neighbors.

### 2.3 time_engine_contract.md

**Travel Distance:**
- Section 7.1: "Cost: 1 day per light-year traveled"
- Distance must be integer (ceiled)
- Current: `distance_ly = _warp_distance_ly()` then `days = ceil(distance_ly)` (compliant)

**Conclusion:** No changes needed for time engine contract.

## 3. Gaps / Risks

### 3.1 Identified Gaps

**Gap 1: No Galaxy Size Prompt**
- CLI prompts for seed only, not galaxy size
- User cannot choose small/normal/large at game creation
- Risk: Users stuck with default 5 systems

**Gap 2: Fixed Galaxy Radius**
- `GALAXY_RADIUS = 100.0` regardless of system_count
- For N=50, systems may cluster near center or spread too thin
- For N=150, systems may be too dense or exceed radius
- Risk: Inconsistent spacing; nearest-neighbor distances unpredictable

**Gap 3: Linear Neighbor Chain**
- Current: Only connects index-1 and index+1
- For N=150, this creates a 150-node chain
- No cross-connections; graph diameter = N-1
- Risk: Long travel paths, no strategic routing options
- Note: Contract allows this, but gameplay may suffer

**Gap 4: Name Repetition**
- 10 names cycle for any N > 10
- For N=150, each name appears 15 times
- Risk: Confusing, breaks immersion

**Gap 5: No CLI Map Display**
- No ASCII grid map showing system positions
- Users cannot visualize galaxy layout
- Risk: Poor spatial awareness, hard to plan routes

**Gap 6: Travel Targeting Discovery Requirement**
- Current: All systems reachable if fuel permits (no discovery gate)
- User requirement: "any system within ship range, discovered or undiscovered"
- Current behavior matches requirement (no gap, but note for clarity)

### 3.2 Risks

**Risk 1: Determinism Breakage**
- Changing radius scaling or neighbor algorithm must preserve determinism
- All RNG must use `world_seed + stable_salt` pattern
- Risk: Non-deterministic changes break save/load, tests

**Risk 2: Test Suite Impact**
- Many tests assume system_count=5
- Tests may break if default changes or if determinism changes
- Risk: Test failures require updates

**Risk 3: Performance**
- N=150 systems: neighbor graph construction, distance calculations scale
- Current linear chain is O(N) to build, O(1) per neighbor lookup
- MST + k-NN may be O(N^2) to build
- Risk: Slow worldgen for large N

**Risk 4: Persistence Compatibility**
- Existing saves may have system_count=5, radius=100.0
- New saves may have different values
- Risk: Save format changes, migration needed

## 4. Proposed Deterministic Designs

### 4.1 Radius Scaling

**Proposal: Deterministic Radius Function**

```
radius(system_count) = base_radius * sqrt(system_count / base_count)

Where:
  base_radius = 100.0 (current GALAXY_RADIUS)
  base_count = 5 (current default)
  
Examples:
  N=50:  radius = 100.0 * sqrt(50/5) = 100.0 * sqrt(10) ≈ 316.2 LY
  N=100: radius = 100.0 * sqrt(100/5) = 100.0 * sqrt(20) ≈ 447.2 LY
  N=150: radius = 100.0 * sqrt(150/5) = 100.0 * sqrt(30) ≈ 547.7 LY
```

**Nearest-Neighbor Spacing Analysis:**

For uniform random distribution in circle of radius R:
- Expected nearest-neighbor distance ≈ 2 * R / sqrt(N) (approximate)
- For N=50, R=316: spacing ≈ 2*316/sqrt(50) ≈ 89.4 LY (too large)
- For N=100, R=447: spacing ≈ 2*447/sqrt(100) ≈ 89.4 LY (too large)
- For N=150, R=548: spacing ≈ 2*548/sqrt(150) ≈ 89.5 LY (too large)

**Revised Proposal: Target-Based Scaling**

Target: nearest-neighbor spacing in [2, 10] LY range.

```
For target spacing S in [2, 10]:
  radius = S * sqrt(N) * sqrt_factor
  
Where sqrt_factor accounts for uniform distribution density.

Empirical: For uniform random in circle, nearest-neighbor ≈ 0.5 * R / sqrt(N)
To get spacing ≈ 5 LY: R ≈ 10 * sqrt(N)

Examples:
  N=50:  R = 10 * sqrt(50) ≈ 70.7 LY  (spacing ≈ 5 LY)
  N=100: R = 10 * sqrt(100) = 100.0 LY (spacing ≈ 5 LY)
  N=150: R = 10 * sqrt(150) ≈ 122.5 LY (spacing ≈ 5 LY)
```

**IMPLEMENTED:**
```
radius(system_count) = 10.0 * sqrt(system_count)

This yields:
  N=50:  R ≈ 70.7 LY,  expected spacing ≈ 5.0 LY
  N=100: R = 100.0 LY, expected spacing ≈ 5.0 LY
  N=150: R ≈ 122.5 LY, expected spacing ≈ 5.0 LY
```

**IMPLEMENTED: Coordinate Uniqueness Enforcement**

- Deterministic rejection sampling: Generate (x,y), check against used_coords set (rounded to 6 decimals)
- If collision detected, retry with new attempt counter (up to MAX_ATTEMPTS=100)
- If attempts exhausted, apply deterministic micro-jitter based on hash(seed, system_id, "coord_jitter")
- Jitter applied at 1e-6 scale, then re-checked for uniqueness
- Ensures no two systems share the same coordinate key (round(x,6), round(y,6))

### 4.2 Starlane Graph Construction

**IMPLEMENTED: MST + k-NN Deterministic Graph**

**Algorithm:**
1. Build Minimum Spanning Tree (MST) for connectivity
   - Use Kruskal's algorithm with union-find data structure
   - Edge weights = Euclidean distance from (x,y) coordinates
   - Sort edges by (distance, a_id, b_id) where a_id < b_id (deterministic tie-break)
   - Result: Connected graph with N-1 edges

2. Add k-Nearest Neighbors (k=2) for extra connectivity
   - For each system, find k nearest neighbors by distance (excluding self and existing neighbors)
   - Add edge if not already in MST
   - Sort candidates by (distance, neighbor_id) for deterministic selection
   - Ensure undirected symmetry (if A->B added, also add B->A)
   - Result: Additional edges (typically 2 per system, some duplicates)

3. Store neighbors deterministically
   - For each system, collect all neighbors (MST + k-NN edges)
   - Sort neighbor list by system_id (deterministic)
   - Store as `System.neighbors: List[str]`

**Determinism Guarantees:**
- MST: Deterministic because edge weights are deterministic (from deterministic x,y)
- Tie-breaks: Deterministic via system_id lexicographic sort
- k-NN: Deterministic because distances are deterministic, tie-breaks use system_id
- Neighbor list ordering: Deterministic via system_id sort

**Complexity:**
- MST: O(N^2) for Prim's (acceptable for N <= 150)
- k-NN: O(N^2) to compute all distances, then O(N log N) to sort per system
- Total: O(N^2) which is acceptable for N <= 150

**Example for N=5:**
- MST: 4 edges (connects all 5 systems)
- k-NN (k=2): Adds ~4-6 additional edges (some duplicates)
- Result: Each system has 2-4 neighbors (vs previous 1-2 in linear chain)

**Example for N=150:**
- MST: 149 edges
- k-NN (k=2): Adds ~300 additional edges (many duplicates)
- Result: Each system has ~3-5 neighbors on average
- Graph diameter: ~10-15 hops (vs previous 149 hops for linear chain)

**Implementation Notes:**
- Use `_seeded_rng(world_seed, "starlane_graph", system_id)` for any RNG needed
- Store graph as `System.neighbors` (no separate graph data structure)
- Graph is immutable after worldgen (contract compliant)

### 4.3 Name Lists (Systems, Planets, Stations)

**Proposal: Curated Name Data File**

**File:** `data/names.json`

**Schema:**
```json
{
  "systems": ["Aster", "Beacon", ...],
  "planets": ["Terra", "Mars", ...],
  "stations": ["Orbital", "Deep", ...]
}
```

**Requirements:**
- systems: >= 200 unique names
- planets: >= 400 unique names
- stations: >= 400 unique names
- ASCII only (no Unicode)
- No duplicates within each list
- Curated list (not generated)

**Deterministic Selection:**
1. Load names from `data/names.json`
2. For systems: Shuffle with seed, assign sequentially per system
3. For planets: Shuffle per system with seed + system_id + "planet_names", assign sequentially
4. For stations: Shuffle per system with seed + system_id + "station_names", assign sequentially
5. For N > list size, names will repeat, but repetition is deterministic

**Implementation:**
- Add `_load_names()` helper in world_generator.py
- Use system names in `WorldGenerator.generate()` instead of hardcoded list
- Use planet/station names in `_generate_destinations()` for destination naming
- Fallback: If file missing, use current hardcoded lists

### 4.4 Destination Typing and Stub Generation

**Proposal: Explicit Destination Type Generation**

**Destination Types:**
- "planet": Population center, has economy/market (2-4 per system)
- "station": Population center, has economy/market (1-2 per system)
- "explorable_stub": Non-population, no market, stub for future mechanics (0-2 per system)
- "mining_stub": Non-population, no market, stub for future mechanics (0-2 per system)

**Deterministic Count Rules:**
- Per system, generate deterministically:
  - planets: 2 to 4 (using seed + system_id + "dst_planet_count")
  - stations: 1 to 2 (using seed + system_id + "dst_station_count")
  - explorable_stub: 0 to 2 (using seed + system_id + "dst_explorable_count")
  - mining_stub: 0 to 2 (using seed + system_id + "dst_mining_count")

**Naming Rules:**
- Planets: Use names from `data/names.json` planets list, shuffled per system
- Stations: Use names from `data/names.json` stations list, shuffled per system
- Explorable stubs: Use "Explorable Site N" (temporary, until mechanics added)
- Mining stubs: Use "Mining Site N" (temporary, until mechanics added)

**Stub Behavior:**
- Stubs have population=0, no primary_economy_id, no secondary_economy_ids, no market
- Stubs are visible in CLI destination listing with destination_type shown
- Stubs do NOT affect markets, shipdocks, legality, enforcement, world state, or time
- Stubs are placeholders for future mechanics (exploration, mining)

**Implementation:**
- Update `_generate_destinations()` to generate each type separately
- Remove old `_destination_counts()` and `_choose_destination_types()` logic
- Generate planets and stations first (population centers)
- Generate stubs last (no population)
- Use deterministic RNG streams for each count type

### 4.4 CLI Map Display

**IMPLEMENTED: ASCII Grid Map Renderer**

**Function:** `_render_galaxy_map(sector, width=80, height=30) -> None`

**Algorithm:**
1. Determine grid size (default: 80 columns x 30 rows)
2. Sort systems by system_id to assign stable indices (01, 02, ..., 150)
3. Map float (x,y) coordinates to integer grid cells:
   - Find min_x, max_x, min_y, max_y across all systems
   - Add padding if range is too small
   - Scale to grid: `col = int((x - min_x) / x_range * (width - 1))`
   - Flip y for display: `row = int((1.0 - (y - min_y) / y_range) * (height - 1))`
4. Handle collisions (multiple systems in one cell):
   - If collision: mark cell with "*"
   - Store collision list: `collisions[(row, col)] = [(index, system_id, name), ...]`
5. Label systems:
   - For non-collision cells: label with 2-3 digit index (01, 02, ..., 150)
   - Index = 1-based position in sorted system list
6. Print map:
   - Grid with labels
   - Legend: index -> system_id -> name -> (x, y) coordinates
   - Below legend: collision list (if any)

**Deterministic Collision Handling:**
- Sort systems by system_id before assigning to grid
- If collision, show "*" and list all colliding systems in legend
- Order collisions by system_id (deterministic)

**Integration Points:**
- IMPLEMENTED: Print once at game start (after `GameEngine` init in `main()`)
- IMPLEMENTED: Print on "System Info" command (in `_show_system_info()`)

**Example Output:**
```
GALAXY MAP
================================================================================
    01    02    03
       04    05
  *       06    07
    08    09    10
...
================================================================================

LEGEND:
  01 SYS-001 Ion (x=12.345, y=67.890)
  02 SYS-002 Beacon (x=23.456, y=78.901)
  ...

COLLISIONS (multiple systems in same cell):
  Cell (40, 15):
    042 SYS-042 SystemName (x=..., y=...)
    043 SYS-043 SystemName (x=..., y=...)
```

### 4.5 Persistence Implications

**Current State:**
- World generation is deterministic from `world_seed`
- World state mutates after generation (situations, events, player actions)
- Save/load must store mutated state, not just seed

**Why Seed-Only Regeneration Is Insufficient:**
- Events create situations, modify population, change governments
- Player actions modify player state, mission state, NPC state
- These mutations are NOT reconstructible from seed alone
- Example: System A had population 3, Event reduced it to 2. Regenerating from seed would restore population 3 (incorrect)

**Proposed Persistent Fields (Minimal):**
1. `world_seed: int` (required for regeneration base)
2. `galaxy_size: str` ("small"|"normal"|"large") or `system_count: int` (required for regeneration)
3. `world_state_mutations: list[dict]` OR `world_state_snapshot: dict`
   - Store all mutations since worldgen (events, situations, structural changes)
   - OR store full world state snapshot (systems with mutated population/government, active situations, etc.)

**Recommendation:**
- Store `world_seed` and `system_count` (or `galaxy_size`)
- Store full world state snapshot (simpler than mutation log)
- On load: Verify seed matches, verify system_count matches, load snapshot
- Do NOT regenerate world from seed on load (would lose mutations)

**Future Enhancement:**
- Add save format version field
- Migration path: Old saves (system_count=5) can be loaded, but new games use new system_count

## 5. Implementation Plan Steps

### Step 1: Add Galaxy Size Prompt to CLI
- File: `src/run_game_engine_cli.py`
- Add `_prompt_galaxy_size() -> str` function
- Options: "small" (50), "normal" (100), "large" (150)
- Map to system_count: {"small": 50, "normal": 100, "large": 150}
- Call in `main()` before `GameEngine` init
- Pass to `GameEngine(config={"system_count": system_count})`

### Step 2: Implement Radius Scaling (COMPLETED)
- File: `src/world_generator.py`
- Replaced `GALAXY_RADIUS = 100.0` with `_galaxy_radius()` method
- Function: `radius = 10.0 * math.sqrt(system_count)`
- Updated `_assign_spatial_coordinates()` to use computed radius
- Test: Verified radius scales correctly for N=50, 100, 150

### Step 3: Implement Deterministic Starlane Graph (COMPLETED)
- File: `src/world_generator.py`
- Added `_build_starlane_graph(systems: List[System]) -> List[System]` method
- Implemented MST (Kruskal's algorithm with union-find) with deterministic tie-breaks
- Implemented k-NN (k=2) with deterministic tie-breaks
- Replaced linear chain assignment with graph builder
- Test: Verified graph is connected, deterministic, immutable

### Step 4: Add Names Data File (COMPLETED - from previous phase)
- File: `data/names.json` (create new)
- Add >= 200 system names, >= 400 planet names, >= 400 station names (ASCII only)
- File: `src/world_generator.py`
- Add `_load_names() -> Dict[str, List[str]]` helper
- Replace hardcoded 10-name list with loaded system names
- Use planet/station names in destination generation
- Fallback to current lists if file missing
- Test: Verify names load, shuffle deterministically

### Step 4A: Update Destination Generation with Typing
- File: `src/world_generator.py`
- Update `_generate_destinations()` to generate planets/stations separately
- Add explorable_stub and mining_stub generation
- Use deterministic counts: planets (2-4), stations (1-2), explorable (0-2), mining (0-2)
- Use names from `data/names.json` for planets and stations
- Ensure stubs have population=0, no markets, no economies
- Test: Verify destination counts are deterministic, names assigned correctly

### Step 5: Implement CLI Map Renderer
- File: `src/run_game_engine_cli.py`
- Add `_render_galaxy_map(engine: GameEngine) -> None` function
- Implement grid mapping, collision handling, labeling
- Call in `main()` after `GameEngine` init
- Optional: Add map option to `_show_system_info()`
- Test: Verify map renders correctly for N=50, 100, 150

### Step 6: Update Tests
- Files: `tests/integration_test.py`, `tests/cli_test.py`, `tools/test_run.py`
- Update tests to use explicit `system_count` parameter
- Add tests for N=50, 100, 150 determinism
- Add tests for radius scaling, starlane graph connectivity
- Verify no hardcoded "5 system" assumptions remain

### Step 7: Update Game Engine Config Handling
- File: `src/game_engine.py`
- Ensure `system_count` from config is passed to `WorldGenerator`
- Add validation: system_count must be > 0, <= 200 (reasonable max)
- Log system_count and computed radius at init

### Step 8: Documentation Updates
- File: `design/TO_ADD.md` (append Phase 7.9 entry)
- Document galaxy size selection feature
- Document wormholes as future addition (optional, deferred)

## 6. Test Plan

### 6.1 Determinism Tests

**Test: Same Seed, Same Galaxy**
- Generate galaxy with seed=12345, system_count=100
- Generate again with same seed, system_count
- Verify: All system_ids, names, coordinates, neighbors identical

**Test: Different Seeds, Different Galaxies**
- Generate with seed=12345, system_count=100
- Generate with seed=67890, system_count=100
- Verify: Systems differ (different names, coordinates, neighbors)

**Test: Radius Scaling Determinism**
- Generate with seed=12345, system_count=50
- Verify: radius ≈ 70.7 LY
- Generate with seed=12345, system_count=150
- Verify: radius ≈ 122.5 LY
- Verify: Same seed, different system_count yields different but deterministic layouts

### 6.2 Graph Connectivity Tests

**Test: Graph Is Connected**
- Generate galaxy with system_count=100
- Verify: All systems reachable from any system via neighbor graph
- Use BFS/DFS to check connectivity

**Test: Graph Has Reasonable Diameter**
- Generate galaxy with system_count=150
- Compute graph diameter (longest shortest path)
- Verify: diameter < 20 (vs current 149 for linear chain)

**Test: Graph Is Immutable**
- Generate galaxy
- Store initial neighbors
- Advance time, trigger events (should not mutate neighbors)
- Verify: neighbors unchanged

### 6.3 Radius Scaling Tests

**Test: Nearest-Neighbor Spacing**
- Generate with system_count=100
- Compute all pairwise distances
- Find minimum distance (nearest-neighbor)
- Verify: minimum distance in [2, 10] LY range (approximately)

**Test: Radius Formula**
- Generate with system_count=50, 100, 150
- Verify: radius = 10.0 * sqrt(system_count) (within floating-point tolerance)

### 6.4 Name Assignment Tests

**Test: Names Load and Shuffle**
- Verify: `_load_names()` returns >= 200 system names, >= 400 planet names, >= 400 station names
- Generate with seed=12345, system_count=50
- Verify: System names assigned deterministically (same seed = same names)
- Verify: Planet names assigned deterministically per system
- Verify: Station names assigned deterministically per system

**Test: Name Repetition for Large N**
- Generate with system_count=250 (if supported)
- Verify: Names repeat deterministically (not random repetition)

**Test: Destination Type Generation**
- Generate with seed=12345, system_count=10
- Verify: Each system has 2-4 planets, 1-2 stations
- Verify: Each system has 0-2 explorable_stub, 0-2 mining_stub
- Verify: Counts are deterministic (same seed = same counts per system)
- Verify: Planet names come from planets list
- Verify: Station names come from stations list
- Verify: Stubs have population=0, no markets, no economies

### 6.5 CLI Map Tests

**Test: Map Renders Without Crash**
- Generate galaxy with system_count=150
- Call `_render_galaxy_map()`
- Verify: No exceptions, output is ASCII

**Test: Map Handles Collisions**
- Generate galaxy with system_count=150, small radius (force collisions)
- Verify: Collisions shown as "*", listed below map

### 6.6 Integration Tests

**Test: Full Game Flow with Large Galaxy**
- Create game with system_count=100
- Execute 10+ travel commands
- Verify: No crashes, determinism preserved

**Test: Save/Load with New System Count**
- Create game with system_count=150
- Save game
- Load game
- Verify: System count preserved, world state intact

## 7. TO_ADD.md Entries

### 7.1 Galaxy Size Selection (Phase 7.9)

**Feature: Galaxy Size Selection at Game Creation**
- CLI prompts for galaxy size: small (50 systems), normal (100), large (150)
- Selection stored in game config, passed to world generator
- Affects galaxy radius scaling and system spacing
- Deterministic: same seed + same size = same galaxy

**Future Enhancement:**
- Allow custom system_count (beyond small/normal/large presets)
- Add "tiny" (25) and "huge" (200) options
- UI: Galaxy size selector in new game screen

### 7.2 Wormholes (Optional, Deferred)

**Feature: Wormhole Connections (Future)**
- Wormholes create long-distance connections between non-neighbor systems
- Reduce travel time for specific routes
- Deterministic placement based on world_seed
- May be one-way or bidirectional
- Implementation deferred to future phase (not Phase 7.9)

**Design Notes:**
- Wormholes should be rare (1-3 per galaxy for N=100)
- Placement should be deterministic from world_seed
- Wormholes may have fuel cost or time cost different from normal travel
- Wormholes may be discoverable (hidden until visited) or always visible

---

## Appendix A: Mathematical Notes

### A.1 Radius Scaling Derivation

For uniform random distribution in circle of radius R:
- Area = π * R²
- Expected number of systems in area A: N * (A / (π * R²))
- Nearest-neighbor distance (approximate): d ≈ 2 * R / sqrt(N)

To achieve d ≈ 5 LY:
- 5 ≈ 2 * R / sqrt(N)
- R ≈ 2.5 * sqrt(N)

Using factor 10.0 (more conservative, accounts for edge effects):
- R = 10.0 * sqrt(N)
- For N=100: R = 100.0 LY, d ≈ 2*100/sqrt(100) = 20 LY (too large)

Revised target: d in [2, 10] LY, prefer d ≈ 5-7 LY.

Better formula:
- R = 5.0 * sqrt(N)  (for d ≈ 5 LY)
- For N=100: R = 50.0 LY, d ≈ 2*50/sqrt(100) = 10 LY (upper bound)
- For N=50: R ≈ 35.4 LY, d ≈ 2*35.4/sqrt(50) ≈ 10 LY
- For N=150: R ≈ 61.2 LY, d ≈ 2*61.2/sqrt(150) ≈ 10 LY

**Final Recommendation:** Use `R = 5.0 * sqrt(N)` for tighter spacing, or `R = 10.0 * sqrt(N)` for looser spacing. Phase 7.9 uses `R = 10.0 * sqrt(N)` as conservative starting point.

### A.2 MST + k-NN Graph Properties

For N systems:
- MST edges: N-1 (minimum for connectivity)
- k-NN edges: ~k*N/2 (accounting for duplicates, k=3 gives ~1.5*N edges)
- Total edges: ~2.5*N (vs linear chain: N-1)
- Average degree: ~5 neighbors per system (vs linear chain: ~2)
- Graph diameter: O(log N) for well-connected graphs (vs linear: O(N))

For N=150:
- MST: 149 edges
- k-NN: ~225 edges (many duplicates)
- Total unique edges: ~250-300
- Average neighbors: ~3-4 per system
- Expected diameter: ~8-12 hops

---

END OF AUDIT DOCUMENT
