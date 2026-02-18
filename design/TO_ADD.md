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

## CUSTOMS / ENFORCEMENT NOTES
- Customs may trigger a MAX of once per destination per turn (anti-spam guard), but is NOT guaranteed.
- Customs trigger is gated by a determination check driven by system enforcement (and any existing rules for destination/market entry).
- Anarchy enforcement implies 0% customs (never triggers).

## PLAYTEST UX NOTES
- Need a consistent market screen: show market list + cargo + prices always visible while in market; actions below.
- CLI friction: list actions should allow direct execute; provide back option.
- Top info bar in UI: always show credits (and later fuel/heat/reputation).
- Warehouse slogan: "Can't sell it? Store it!"