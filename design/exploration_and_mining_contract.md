# EmojiSpace - Exploration and Mining Resolution Contract

Status: DRAFT
Phase: 7.12 - Persistent Exploration and Mining
Target Version: 1.1.x
File: /design/exploration_and_mining_contract.md

----------------------------------------------------------------
1. Purpose
----------------------------------------------------------------

Defines two deterministic subsystems:

A) Exploration Resolution
B) Mining Resolution

These systems apply ONLY to persistent non-inhabited destinations:

- exploration_site
- resource_field

These destination types are generated at world creation
and may also be introduced via authorized Event mutation.

This contract introduces:

- Destination-based player actions
- Deterministic diminishing returns
- Per-destination player progression tracking
- Harvestable-based mining yield system
- Single post-action encounter check

This contract does NOT:

- Modify world structure
- Delete destinations
- Mutate government
- Modify population
- Override economy pricing rules
- Replace salvage or combat reward systems

----------------------------------------------------------------
2. Destination Types
----------------------------------------------------------------

2.1 exploration_site

Represents a persistent anomaly, signal, structure,
or unknown phenomenon.

Properties:

- population = 0
- no market
- no standard locations
- may produce exploration outcomes
- may schedule Events

2.2 resource_field

Represents a persistent extractable zone.

Properties:

- population = 0
- no market
- no standard locations
- produces mining yield via harvestable goods

----------------------------------------------------------------
3. Goods Schema Extension
----------------------------------------------------------------

goods.json MUST support:

harvestable: true | false

Default if field missing: false

Only goods with harvestable == true
are eligible for mining production.

No other system uses this field.

----------------------------------------------------------------
4. Player State Extension
----------------------------------------------------------------

Player entity MUST store per-destination state:

exploration_progress:
  { destination_id: integer_success_count }

exploration_attempts:
  { destination_id: integer_attempt_count }

mining_attempts:
  { destination_id: integer_attempt_count }

Destination objects remain immutable.
All progression is player-side.

----------------------------------------------------------------
5. Diminishing Returns
----------------------------------------------------------------

Let N = attempt count at this destination.

yield_multiplier:

N = 0: 1.00
N = 1: 0.75
N = 2: 0.50
N = 3: 0.25
N >= 4: 0.10 (floor)

Applied AFTER base quantity calculation.

----------------------------------------------------------------
6. Exploration Resolution
----------------------------------------------------------------

Explore action appears ONLY if:

- destination_type == exploration_site
- destination not tagged destroyed
- player ship has unlock_probe capability

6.1 RNG Stream

Seed:
world_seed + destination_id + player_id + "explore"

6.2 Success Check

Base success probability >= 0.50.

Exploration_progress increments ONLY on success.

exploration_attempts increments every attempt.

6.3 Stage Logic

Stage 0 -> stage 1 outcome
Stage 1 -> stage 2 outcome
Stage >=2 -> repeat diminished outcome

Outcomes MAY:

- Grant credits
- Grant goods via reward_profiles
- Grant data cargo
- Schedule Event via world_state

Exploration MUST NOT directly mutate structure.

----------------------------------------------------------------
7. Mining Resolution
----------------------------------------------------------------

Mine action appears ONLY if:

- destination_type == resource_field
- destination not tagged destroyed
- player ship has unlock_mining capability

7.1 RNG Stream

Seed:
world_seed + destination_id + player_id + "mining"

7.2 Base Quantity

base_quantity =
player_ship_TR_band

7.3 Effective Quantity

effective_quantity =
floor(base_quantity * yield_multiplier)

yield_multiplier defined in Section 5.

mining_attempts increments every attempt.

7.4 SKU Pool Construction

1) Load goods.json
2) Filter goods where harvestable == true
3) Sort ASCII by sku_id
4) Deterministically select SKU(s)

7.5 Storage Rules

Mining goods:

- Stored as physical cargo unless SKU tagged data
- Must obey cargo capacity
- If insufficient capacity:
    action fails
    no partial yield granted

Mining goods are subject to legality and enforcement normally.

----------------------------------------------------------------
8. Time and Fuel Consumption
----------------------------------------------------------------

Each exploration or mining action:

- Advances time by exactly 1 day
- Consumes fuel equivalent to intra-system travel
- Must log both

Time advancement occurs BEFORE encounter roll.

----------------------------------------------------------------
9. Post-Action Encounter Check
----------------------------------------------------------------

After action resolution:

- Trigger encounter_generator
- travel_context.mode = "local_activity"
- Perform exactly ONE encounter roll
- No chaining allowed
- Use standard subtype weighting
- Do NOT modify pirate weight
- Do NOT modify enforcement bonuses
- Do NOT reduce base probability

Encounter resolution is handled by the unified system.

----------------------------------------------------------------
10. Logging Requirements
----------------------------------------------------------------

Must log:

- destination_id
- action_type
- attempt_number
- success (explore)
- stage_before
- stage_after
- base_quantity
- multiplier
- final_quantity
- RNG roll
- time_advance
- fuel_consumed
- encounter_roll_result

Outcome must be fully reconstructible from logs.

----------------------------------------------------------------
END OF CONTRACT