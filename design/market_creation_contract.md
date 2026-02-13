# market_creation_contract.md (UPDATED - DESTINATION SCOPED)

Status: PROPOSED REVISION (Pending Lock)
Applies To: World Generator, Economy Engine, Testing Harnesses
Consumes:
- /data/categories.json
- /data/goods.json
- /data/economies.json
- Destination data (population, primary_economy, secondary_economies)
- world_seed

Produces:
- market definition per destination that has a Market location
- SKU lists per category role (produced/consumed/neutral) within that destination

----------------------------------------------------------------

## 1. Scope & Timing

Market creation occurs:
- once, during world generation
- per destination, not per system
- only for destinations where a Market location exists and is enabled

Markets do not regenerate during play.

----------------------------------------------------------------

## 2. Required Inputs (Per Destination)

Each destination market uses:
- destination.population (integer 1-5)
- destination.primary_economy (exactly one)
- destination.secondary_economies (zero or more)
- world_seed

System population and government do not directly define market composition.
System population only bounds destination.population via the destinations contract.

----------------------------------------------------------------

## 3. Economy Aggregation

Collect all economies present on the destination:
- primary economy
- all secondary economies

All contribute equally.

----------------------------------------------------------------

## 4. Category Eligibility and Role Rules

Apply the existing SKU-centric rules exactly as written, but scoped to the destination.

All references to "system market" become "destination market".

----------------------------------------------------------------

## 5. Determinism & Logging

Logs must include, per destination:
- economies present
- neutral roll outcomes
- SKU pool (base + tagged variants)
- role assignment results per category
- final produced/consumed/neutral SKU lists per category

----------------------------------------------------------------

## 6. Non-Responsibilities

Market creation does not:
- assign prices
- determine legality
- apply government ideology
- create NPCs
- create encounters

----------------------------------------------------------------

## 7. Contract Statement

This revision is authoritative once locked.

Any implementation must conform without inferred behavior.
