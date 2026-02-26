## TEST PLATFORM ARCHITECTURE
- Deterministic simulation harness (250 turn default)
- Profit + Reputation bias AI
- Invariant enforcement layer
- Structured log output under /test/output/
- Determinism re-run verification pass
- Future extension: multi-seed regression batch runner
- Future extension: economic balance heatmap analyzer
- Future extension: enforcement frequency distribution analysis

## UI / INTERFACE BLUEPRINT ITEMS

### Destination View Improvements
- Credits must always be visible while at a destination.
- Future UI concept: persistent top information bar including:
  - Credits
  - Fuel (current / capacity)
  - Cargo capacity used / total
  - Reputation band
  - Heat
  - Current system / destination
  - Current turn

### Market Interface Requirements
- Entering a market must automatically display:
  - Full market listing (produced / consumed / neutral categories)
  - Prices for all SKUs
  - Legality and risk
  - Player cargo manifest with quantities
- Buy and Sell must not require separate "execute action" layer.
- Sell view must display:
  - All player cargo
  - The price the market will pay for each eligible SKU
- As long as player is inside market location,
  prices should remain visible for planning trade routes.

### Navigation / CLI Improvements
- Location menus must include explicit "Back" option.
- Remove unnecessary multi-step "execute action" layer in CLI.
- On entering a location, immediately display available actions.
- Market location should use direct buy/sell-first interaction flow.

### Phase 7.5.8 - CLI Testing Improvements
- Added `0) back` in destination location selection (no engine call, no state mutation).
- Removed location action indirection so non-market locations show executable actions immediately.
- Kept market as a special direct flow while preserving core simulation behavior.

## UI Blueprint Notes (Captured During CLI Testing)

- Market screen should render in grid/table layout.
- Market should always show full SKU list with buy/sell columns.
- Cargo overlay should appear inline with market list.
- Destination screen should include persistent top info bar showing:
  - Credits
  - Fuel
  - Cargo capacity
  - Turn
  - Ongoing costs
- Warehouse slogan: "Can't sell it? Store it!"
- Risk/legality indicators should use emoji/icons in UI phase.
- Destination root UI should present locations as grid tiles instead of nested menus.
- Add an authoritative warehouse interaction contract section defining rental action IDs, pricing model, and turn-billing behavior.
- UI: Player screen should show total warehouse cost summary
- UI: Warehouse detail screen per destination with grid layout
- UI: Cancel warehouse action from detail screen
- UI: Recurring cost indicator in top info bar

## Loot Resolution – UI Requirements (Future UI Layer)

This section documents how loot interaction must behave when the full UI layer is implemented.

The engine contract remains authoritative.
This section describes UI behavior only.

------------------------------------------------------------
CREDITS
------------------------------------------------------------

- Credits are automatically applied to player total.
- No prompt required.
- No capacity restriction.
- Display gain clearly in UI summary.

------------------------------------------------------------
GOODS (Physical Cargo)
------------------------------------------------------------

UI must:

1) Display:
   - SKU
   - Quantity available
   - Cargo space required
   - Player current cargo usage / max capacity

2) Prompt:
   - Collect none
   - Collect partial amount (enter quantity)
   - Collect all

3) If insufficient cargo space:
   - Display current cargo manifest
   - Allow player to:
        - Jettison existing cargo
        - Reduce collection quantity
        - Cancel collection

4) No cargo overflow permitted.
   Engine must enforce capacity.

------------------------------------------------------------
MODULES (Salvage Modules)
------------------------------------------------------------

UI must:

1) Display module stats and rarity.
2) Prompt:
   - Collect
   - Leave

3) If collecting:
   Prompt:
     - Install immediately (if slot available)
     - Store in cargo (uses 1 physical cargo unit)
     - Cancel

4) If insufficient cargo space:
   - Allow jettison of existing cargo
   - Allow cancellation

5) Installation must respect:
   - Slot type
   - Slot availability
   - Ship tier restrictions

------------------------------------------------------------
GENERAL RULES
------------------------------------------------------------

- Engine remains deterministic.
- UI may not re-roll rewards.
- No cargo overflow allowed.
- No silent loss of loot.
- Player must always confirm destructive actions (jettison).

------------------------------------------------------------
NOTES
------------------------------------------------------------

Current CLI implementation is simplified:
- Credits auto-add after confirmation.
- Goods/modules are not yet interactive.
- Full behavior deferred to UI phase.

This section serves as contract specification for future UI development.

## UI / Exploration Enhancements (Future)

- Searchable "Nearest Known Location" utility: Once visited tracking is implemented, allow players (via UI) to search for the nearest previously visited location type (e.g., Shipdock, Administration, Bar, Warehouse, DataNet). Should operate only on visited systems/destinations. Pure UI query layer - no world mutation.

## Interactive Galaxy Map (UI Phase)

### 1) Interactive Map Layer
- Render the galaxy map visually (UI layer, not CLI).
- Each system will be represented by an emoji-based icon.
- Icons must be selectable (click/tap).
- Selecting a system displays:
    - If visited:
        - system name
        - government
        - primary and secondary economies
        - discovered destinations
    - If not visited:
        - system name only
- No hidden data leakage for unvisited systems.

### 2) Emoji-Based Map Indicators
- The map will use emojis to represent:
    - Stars
    - Wormholes
    - Black holes
    - Special anomalies (future)
    - Player location
- Emoji selection must be centralized in emoji registry (data/emoji.json).
- Emoji usage must not introduce new game logic.
- Icons are presentation-layer only.

### 3) Fog of War Rules
- Unvisited systems show minimal information.
- Discovered systems reveal structural metadata only.
- No economy, legality, or situation data shown unless visited (align with World State contract).

### 4) Future Extension Hooks
- Wormholes (once implemented) must display unique emoji.
- Black holes (once implemented) must display unique emoji.
- Dynamic event overlays (Phase 6 situations) may later appear as temporary map indicators.

Do not implement any of this now.
This is documentation only.

## CUSTOMS / ENFORCEMENT NOTES
- Customs may trigger a MAX of once per destination per turn (anti-spam guard), but is NOT guaranteed.
- Customs trigger is gated by a determination check driven by system enforcement (and any existing rules for destination/market entry).
- Anarchy enforcement implies 0% customs (never triggers).

## PLAYTEST UX NOTES
- Need a consistent market screen: show market list + cargo + prices always visible while in market; actions below.
- CLI friction: list actions should allow direct execute; provide back option.
- Top info bar in UI: always show credits (and later fuel/heat/reputation).
- Warehouse slogan: "Can't sell it? Store it!"

## Bankruptcy Grace Setting
- Add configurable bankruptcy grace period setting.
- Range: 0 (hard mode) to 3 (easy mode).
- Default: 1 full turn.
- Setting to be part of future Game Settings system.

## Travel Cost Preview Before Execution
- Before confirming any travel action, the player must be shown:
  - Travel duration (days)
  - Total recurring cost during travel
  - Estimated fuel usage
- Purpose: Prevent surprise bankruptcies during long travel.

## Bar NPC Emoji Profile Display
- When implementing UI:
  Bar NPC entries must display their Emoji Profile.
  Emoji Profile should visually indicate:
  - Offering work (mission giver)
  - Looking for work (crew candidate)
- This must be driven by role metadata.

## Mission Offer Refresh Indicator
- UI: Display mission offer refresh indicator per location (based on day/turn).
- Purpose: Show when mission offers will regenerate (on next turn when entering location).

## Mission Capacity Expansion (Future)
- Reputation increases total active mission cap.
- Ship upgrades may increase total cap.
- Certain crew roles may increase cap.
- Special traits may remove or increase Tier 1 cap.
- Potential dynamic scaling based on difficulty.

## Phase 7.9 - Galaxy Size Selection (Implemented)
- CLI prompts for galaxy size at new game creation: small (50 systems), normal (100), large (150)
- Galaxy radius scales deterministically with system_count: radius = 10.0 * sqrt(system_count)
- System spacing targets 2-10 LY nearest-neighbor distance
- Deterministic starlane graph construction (MST + k-NN) replaces linear chain
- Curated name lists in data/names.json: systems (200+), planets (400+), stations (400+)
- Destination typing: planets (2-4 per system), stations (1-2 per system), explorable_stub (0-2), mining_stub (0-2)
- Planets and stations use curated names from data/names.json
- Explorable and mining destinations are stubs (no mechanics yet)
- CLI displays destination_type in destination listings
- ASCII grid map display in CLI for galaxy visualization
- All changes preserve determinism from world_seed

## Phase 7.9 - Wormholes (Optional, Deferred)
- Feature: Wormhole connections create long-distance shortcuts between non-neighbor systems
- Placement: Deterministic from world_seed, rare (1-3 per galaxy for N=100)
- Behavior: May reduce travel time/fuel cost for specific routes
- Discovery: May be hidden until visited or always visible
- Implementation: Deferred to future phase (not Phase 7.9)
- Design notes: Wormholes should be bidirectional or one-way, have distinct fuel/time costs, and integrate with awareness radius system

## Phase 7.9 - Explorable Destinations System (Future)
- Feature: Explorable destinations (lost ships, abandoned stations, archaeology sites, anomalies)
- Current: Stub destinations (explorable_stub type) generated deterministically (0-2 per system)
- Future: Add exploration mechanics, discovery rewards, narrative content
- Design notes: Explorable destinations should provide unique interactions, rewards, or story content. May require new interaction types, reward systems, or narrative generation.

## Phase 7.9 - Mining Destinations System (Future)
- Feature: Mining destinations (asteroid belts, planetary rings, comet clusters, gas pockets)
- Current: Stub destinations (mining_stub type) generated deterministically (0-2 per system)
- Future: Add mining mechanics, resource extraction, commodity generation
- Design notes: Mining destinations should provide resource gathering opportunities. May require new interaction types, resource systems, or commodity generation mechanics.

## Phase 7.9 - Planet vs Station Differentiated Behaviors (Future)
- Feature: Distinct behaviors for planets vs stations beyond naming
- Current: Planets and stations are functionally identical (both population centers with markets)
- Future: Add differentiated mechanics (e.g., planets may have surface locations, stations may have different shipdock availability)
- Design notes: Differentiation should be meaningful but not break existing contracts. Consider location types, interaction availability, or economic differences.

## Phase 7.9 - SLM-Based Procedural Naming (Future)
- Feature: Use Small Language Model (SLM) for procedural name generation
- Current: Curated name lists in data/names.json
- Future: Generate names procedurally using SLM, potentially with thematic consistency
- Design notes: SLM naming should be deterministic from world_seed. May require name caching or pre-generation. Consider performance implications.

## Phase 7.9 - Galaxy Size Selection (Future)
- Feature: Galaxy size selection (Small/Normal/Large/Custom) as Game Setup / Settings configuration option
- Current: Default set to 50 systems for production testing
- Future: Add interactive prompt at game creation for galaxy size selection
  - Small: 50 systems
  - Normal: 100 systems
  - Large: 150 systems
  - Custom: User-specified count (with validation)
- Design notes: Should be part of Game Setup / Settings system. Selection should be stored in save game/config. Default currently set to 50 systems for production testing.

## Interactive Galaxy Map (UI Phase)
- Feature: Interactive galaxy map with emoji-based visual representation
- Current: ASCII grid map in CLI (debug visibility only)
- Future: Full UI layer implementation with:
  - **System Selection Behavior:**
    - Visited systems: show full details (name, government, economies, discovered destinations)
    - Unvisited systems: name only (no data leakage)
  - **Map Emoji Markers:**
    - Stars (standard system representation)
    - Wormholes (once implemented)
    - Black holes (once implemented)
    - Special anomalies (future)
    - Player location indicator
  - **Emoji Registry:** Centralized in data/emoji.json (presentation-layer only, no game logic)
  - **Fog of War Rules:** Unvisited systems show minimal info; discovered systems reveal structural metadata only
  - **Future Extension Hooks:** Dynamic event overlays (Phase 6 situations) may appear as temporary map indicators
- Design notes: Map is presentation-layer only. No new game logic. Emoji selection centralized. Icons are visual indicators only.

## Player Profile UI Structure

This section documents the Player Profile UI structure for future UI layer implementation.
The CLI implementation serves as the authoritative reference for UI structure.
All player actions must route through GameEngine authority.

### Structure Overview

The Player Profile UI is organized into a main menu with three submenus:

**Main Menu:**
1. Ships And Modules
2. Financial
3. Missions
4. Back

### Ships And Modules Submenu

**Display:**
- **Active Ship:**
  - Ship ID
  - Hull ID
  - Hull Integrity (current/max, percentage)
  - Fuel (current/capacity)
  - Installed Modules (slot index, slot type, module ID)
  - Cargo Summary
- **Inactive Ships (if any):**
  - For each inactive ship:
    - Ship ID
    - Hull ID
    - Destination ID
    - Hull Integrity
    - Cargo Summary

**Options:**
1. Change Active Ship
2. Install Module
3. Uninstall Module
4. Transfer Cargo
5. Back

**Change Active Ship:**
- Only allowed if more than one owned ship
- Lists inactive ships with index
- Validates: same destination required, no active combat
- Engine method: `engine.execute({"type": "set_active_ship", "ship_id": ship_id})`
- Log event: `action=ship_change_active`

**Install Module:**
- Displays empty slots for active ship
- Displays compatible modules in cargo or local warehouse
- Engine method: `engine.execute({"type": "install_module", "ship_id": ship_id, "module_id": module_id, "slot_index": slot_index})`
- Engine validates slot compatibility
- Log event: `action=module_install`
- Note: Currently requires shipdock location access (stub in CLI)

**Uninstall Module:**
- Lists installed modules by slot
- Engine method: `engine.execute({"type": "uninstall_module", "ship_id": ship_id, "slot_index": slot_index})`
- Module moved to cargo
- Log event: `action=module_uninstall`
- Note: Currently requires shipdock location access (stub in CLI)

**Transfer Cargo:**
- Only if inactive ships present at same destination
- Select target ship
- List cargo SKUs and quantities
- Prompt quantity
- Engine method: `engine.execute({"type": "transfer_cargo", "source_ship_id": source_ship_id, "target_ship_id": target_ship_id, "sku": sku, "quantity": quantity})`
- Engine enforces capacity
- Log event: `action=cargo_transfer`

### Financial Submenu

**Display:**
- **Credits:** Current credit balance
- **Warehouse Rentals (individual entries):**
  - Location ID
  - Capacity
  - Cost per turn
  - Expiration day
- **Insurance:**
  - If none: display "None"
  - No logic required yet (stub)

**Options:**
1. Cancel Warehouse Rental
2. Cancel Insurance (stub, print not implemented)
3. Back

**Cancel Warehouse Rental:**
- Lists individually by index
- Engine method: `engine.execute({"type": "warehouse_cancel", "destination_id": destination_id})`
- Log event: `action=warehouse_cancel`

### Missions Submenu

**Display:**
- **Active Missions:**
  - Mission ID
  - Title (or mission type)
  - Status (Active / Completed)
  - Destination ID

**Options:**
1. Abandon Mission
2. Claim Mission Reward
3. Back

**Abandon Mission:**
- Lists active missions only
- Engine method: `engine.execute({"type": "abandon_mission", "mission_id": mission_id})`
- Log event: `action=mission_abandon`

**Claim Mission Reward:**
- Lists completed but unclaimed missions
- Engine method: `engine.execute({"type": "claim_mission", "mission_id": mission_id})`
- Log event: `action=mission_claim`
- Note: Currently stub (not yet fully implemented)

### Engine Read-Only Accessors

All read-only accessors are pure state reads with no side effects:

- `engine.get_owned_ships()` - Returns list of all owned ships with summary
- `engine.get_active_ship()` - Returns active ship summary or None
- `engine.get_ship_modules(ship_id)` - Returns installed modules for a ship
- `engine.get_ship_cargo(ship_id)` - Returns cargo manifest for a ship
- `engine.get_warehouse_rentals()` - Returns list of warehouse rentals
- `engine.get_active_missions()` - Returns list of active missions
- `engine.get_claimable_missions()` - Returns list of claimable missions (stub)

### Engine Mutating Actions

All mutating actions:
- Validate legality
- Respect combat lock
- Respect destination constraints
- Produce structured logs

**Command Types:**
- `set_active_ship` - Change active ship
- `transfer_cargo` - Transfer cargo between ships
- `abandon_mission` - Abandon an active mission
- `claim_mission` - Claim mission reward (stub)
- `warehouse_cancel` - Cancel warehouse rental (existing)

### UI Requirements

**Player Tab Structure:**
- Ships And Modules
- Financial
- Missions
- Future: Reputation, Factions, Insurance Expansion

**Important Notes:**
- Player actions are NOT location actions
- All actions must route through GameEngine authority
- UI must mirror CLI structure exactly
- No direct state mutation in UI layer
- All validation occurs in engine layer
- Structured logging required for all actions