# EmojiSpace - reward_profiles.json Schema Contract

Status: FINAL
Phase: 4f - Reward Profile Data Schema
Target Version: 0.5.x
Location: /data/reward_profiles.json
Authoritative Schema Reference: /design/reward_profiles_schema_contract.md

----------------------------------------------------------------

## 1. Purpose

reward_profiles.json defines declarative reward structures used by
resolvers (combat, exploration, law, etc).

A reward profile defines:

- What kind of reward may be produced
- The BASE quantity band
- The BASE credit range
- Stolen tagging behavior
- Emoji representation

It contains NO logic and does not directly select goods.

Goods are selected from the collective system markets at
materialization time.

----------------------------------------------------------------

## 2. File Structure (Top-Level)

The file MUST be a JSON object:

{
  "version": "0.5.x",
  "reward_profiles": [
    { RewardProfileObject },
    ...
  ]
}

- version is mandatory
- reward_profiles is mandatory
- reward_profile_id must be unique
- Order does not imply priority

----------------------------------------------------------------

## 3. RewardProfileObject (Authoritative Shape)

Each object MUST contain:

{
  "reward_profile_id": "string",
  "emoji": "string",
  "reward_kind": "cargo | credits | mixed | none",
  "quantity_band": "very_low | low | medium | high | very_high",
  "credit_range": { optional object },
  "stolen_behavior": "none | always | probabilistic",
  "stolen_probability": number (0.0 - 1.0, optional),
  "notes": "string (optional)"
}

----------------------------------------------------------------

## 4. Field Definitions

### 4.1 reward_profile_id (required)

- Unique string
- ASCII lowercase with underscores
- Referenced by encounter_types.json

Examples:
- "pirate_standard"
- "civilian_manifest_light"
- "derelict_salvage_low"

----------------------------------------------------------------

### 4.2 emoji (required)

- String field
- Emoji representing this reward type
- Placeholder allowed during early development

Example:
"emoji": "crate_placeholder"

----------------------------------------------------------------

### 4.3 reward_kind (required)

Defines structural type:

- cargo: goods materialization only
- credits: credits only
- mixed: both cargo and credits
- none: no reward

Resolvers must respect this type.

----------------------------------------------------------------

### 4.4 quantity_band (required)

Defines the BASE reward scale at TR1.

Allowed values:

- very_low
- low
- medium
- high
- very_high

Effective quantity MUST be:

BASE quantity × encounter_TR_band

Example:

If BASE resolves to 3 units and encounter TR = 4,
final quantity = 3 × 4 = 12 units.

----------------------------------------------------------------

### 4.5 credit_range (required if credits or mixed)

Structure:

{
  "min": integer,
  "max": integer
}

Represents TR1 baseline range.

Effective credit range MUST be:

BASE credit range × encounter_TR_band

Example:

BASE: { min: 500, max: 1000 }
TR4 encounter:
Effective range = { min: 2000, max: 4000 }

Deterministic RNG selects final value within scaled range.

----------------------------------------------------------------

### 4.6 stolen_behavior (required)

Defines how stolen tag is applied to materialized cargo.

Allowed values:

- none
- always
- probabilistic

Meaning:

none:
- No stolen tag applied

always:
- All materialized cargo is tagged stolen

probabilistic:
- Each materialized SKU evaluated independently
- Probability defined by stolen_probability

----------------------------------------------------------------

### 4.7 stolen_probability (required if probabilistic)

- Float between 0.0 and 1.0
- Used deterministically during materialization

Example:
"stolen_probability": 0.5

Ignored if stolen_behavior != probabilistic

----------------------------------------------------------------

## 5. Goods Selection Rule (Authoritative)

For reward_kind including cargo:

Resolvers MUST construct loot pool as follows:

1. Identify system where encounter occurs.
2. Collect all markets in that system.
3. Collect all SKUs from:
   - produced
   - consumed
   - neutral
4. Combine into a unique SKU set.
5. Sort SKUs in ASCII order.
6. Select SKUs deterministically from this pool.

All SKUs have equal weight regardless of produced/consumed status.

No external loot tables are permitted.

----------------------------------------------------------------

## 6. Determinism Requirements

Resolvers must:

1. Resolve BASE quantity from quantity_band
2. Multiply BASE quantity by encounter TR band (1–5)
3. Resolve BASE credit range
4. Multiply BASE credit range by encounter TR band (1–5)
5. Use deterministic RNG:
   seed = world_seed + encounter_id + reward_profile_id
6. Select SKUs from system market pool deterministically
7. Apply stolen_behavior deterministically
8. Log all steps

TR multiplier rule:

Effective reward = BASE × encounter_TR

Additional deterministic modifiers MAY be introduced in future
versions but MUST default to 1.0 in v0.5.x.

----------------------------------------------------------------

## 7. Prohibited Fields

RewardProfileObject MUST NOT include:

- SKU lists
- Source tables
- Pricing modifiers
- Legality definitions
- Government logic
- TR scaling overrides
- Resolver routing info
- State mutation logic

----------------------------------------------------------------

## 8. Responsibility Boundaries

Encounter Generator:
- Selects reward_profile_id only

Interaction Layer:
- Does not apply rewards

Reaction Evaluation:
- Does not apply rewards

Pursuit Resolver:
- Does not apply rewards

Resolvers (combat, exploration, law):
- Trigger reward materialization

Materialization Logic:
- Applies TR multiplier
- Selects SKUs from system markets
- Applies stolen behavior
- Generates credits
- Logs everything

Government:
- Interprets stolen tag

Pricing:
- Reacts to legality only

----------------------------------------------------------------

## 9. Contract Authority

This schema is authoritative.

All reward profiles must conform.
Changes require version increment and schema revision.

-------------------------------
