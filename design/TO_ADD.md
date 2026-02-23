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