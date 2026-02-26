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

BASE quantity � encounter_TR_band

Example:

If BASE resolves to 3 units and encounter TR = 4,
final quantity = 3 � 4 = 12 units.

----------------------------------------------------------------

### 4.5 credit_range (required if credits or mixed)

Structure:

{
  "min": integer,
  "max": integer
}

Represents TR1 baseline range.

Effective credit range MUST be:

BASE credit range � encounter_TR_band

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
2. Multiply BASE quantity by encounter TR band (1�5)
3. Resolve BASE credit range
4. Multiply BASE credit range by encounter TR band (1�5)
5. Use deterministic RNG:
   seed = world_seed + encounter_id + reward_profile_id
6. Select SKUs from system market pool deterministically
7. Apply stolen_behavior deterministically
8. Log all steps

TR multiplier rule:

Effective reward = BASE � encounter_TR

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

----------------------------------------------------------------

## 10. Mission Reward Profiles

Mission reward profiles are identified by reward_profile_id beginning with:
    "mission_"

Mission reward profiles are evaluated exclusively by the mission system.
They are not processed by reward_materializer.

All mission reward profiles MUST contain:
    reward_profile_id
    reward_type

All mission reward profiles MUST incorporate mission tier behavior.

Distance scaling is OPTIONAL and only valid for reward types:
    credits
    goods

Define required fields by reward_type:

1) reward_type: "credits"

Required:
    base_credits (int)
    tier_multiplier (dict or list)
    distance_multiplier_per_ly (float)

Formula:
    reward = base_credits
             * tier_multiplier_for_mission_tier
             * (1 + distance_ly * distance_multiplier_per_ly)

2) reward_type: "goods"

Required:
    base_quantity (int)
    tier_multiplier (dict or list)

Optional:
    distance_multiplier_per_ly (float)

Selector rules:
    selector may include:
        sku_id
        include_tags
        exclude_tags

Only one SKU is deterministically selected.

Quantity is:
    base_quantity
    * tier_multiplier_for_mission_tier
    * (1 + distance_ly * distance_multiplier_per_ly if present)

3) reward_type: "module"

Required:
    selector
    tier_multiplier (dict or list)

Distance scaling NOT allowed.

Quantity always equals 1.

Selector may include:
    module_id
    slot_type
    include_tags
    exclude_tags

4) reward_type: "hull_voucher"

Required:
    selector
    tier_multiplier (dict or list)

Distance scaling NOT allowed.

Selector may include:
    hull_id
    frame
    include_tags
    exclude_tags

Mission reward profiles MUST NOT contain:
    reward_kind
    quantity_band
    credit_range
    stolen_behavior

Those are encounter-only fields.

----------------------------------------------------------------

## 11. Mission Reward Profile Types (Extension: Goods, Modules, Hull Vouchers)

This section extends the reward profile schema to support mission-specific
reward types beyond credits. Mission rewards operate under different
constraints than encounter rewards and require distinct schema definitions.

### 10.1 Core Structural Rules

A. Each mission MUST reference exactly one reward_profile_id.

B. Each reward profile MUST declare exactly one reward_type.

C. Reward profiles MUST NOT declare multiple reward types in a single profile.

D. Reward profiles MUST NOT use arrays of rewards or weighted pools.

E. Mission reward selection and quantity MUST be deterministic per mission.

### 10.2 Allowed reward_type Values

Mission reward profiles MUST use one of the following reward_type values:

- credits (existing, unchanged)
- goods (new)
- module (new)
- hull_voucher (new)

### 10.3 Credits Reward Type (Unchanged)

The credits reward type for missions remains unchanged from the current
implementation. The mission system uses mission tier and distance_ly as
multipliers in the reward calculation formula.

This contract does not redefine the credits calculation logic, which is
authoritative as currently implemented in the mission reward system.

### 10.4 Goods Reward Type (New)

#### 10.4.1 Schema Fields

A goods reward profile MUST contain:

- reward_type: "goods" (required)
- selector: object (required)
  - sku_id: string (optional)
  - include_tags: array of strings (optional)
  - exclude_tags: array of strings (optional)
- quantity: object (required)
  - type: "fixed" | "range" (required)
  - min: integer (required if type is "range", optional if type is "fixed")
  - max: integer (required if type is "range", required if type is "fixed")

#### 10.4.2 Selection Rules

A. If selector.sku_id is present:
   - The exact SKU specified by sku_id MUST be selected.
   - include_tags and exclude_tags MUST be ignored.

B. If selector.sku_id is absent:
   - Selection MUST be from goods.json filtered by include_tags and exclude_tags.
   - include_tags: SKU MUST have all specified tags.
   - exclude_tags: SKU MUST NOT have any specified tags.
   - Selection MUST be deterministic.
   - Exactly one SKU MUST be selected.

C. If selection yields zero candidates, reward redemption MUST fail.

#### 10.4.3 Quantity Resolution

A. If quantity.type is "fixed":
   - The exact quantity specified by quantity.max MUST be granted.

B. If quantity.type is "range":
   - Quantity MUST be deterministically selected between quantity.min and quantity.max (inclusive).
   - The selection MUST use the mission_reward_quantity RNG stream.

#### 10.4.4 Storage and Redemption Rules

A. Goods are stored as physical or data cargo depending on SKU tags.

B. Cargo capacity MUST be enforced at redemption time.

C. If insufficient cargo capacity exists for the full quantity:
   - Reward redemption MUST fail.
   - No partial grant is permitted.
   - No automatic warehouse fallback is permitted.

D. Goods are subject to normal enforcement rules.
   - Illegal or contraband goods MAY be granted.
   - Enforcement consequences apply normally.

### 10.5 Module Reward Type (New)

#### 10.5.1 Schema Fields

A module reward profile MUST contain:

- reward_type: "module" (required)
- selector: object (required)
  - module_id: string (optional)
  - slot_type: string (optional)
  - tier: integer 1-5 (optional)
  - include_tags: array of strings (optional)
  - exclude_tags: array of strings (optional)
  - dynamic_source: "npc_tags" | "mission_tags" | "none" (required)

#### 10.5.2 Quantity

A. Module rewards MUST always grant exactly one module.

B. No quantity field is required or permitted.

#### 10.5.3 Selection Rules

A. If selector.module_id is present:
   - The exact module specified by module_id MUST be selected.
   - All other selector fields MUST be ignored.

B. If selector.module_id is absent:
   - Selection MUST be from modules.json filtered by selector constraints.
   - slot_type: Module MUST be compatible with the specified slot type.
   - tier: If omitted, defaults to mission.mission_tier (1-5).
   - include_tags: Module MUST have all specified tags.
   - exclude_tags: Module MUST NOT have any specified tags.
   - Selection MUST be deterministic.
   - Exactly one module MUST be selected.

C. If selection yields zero candidates, reward redemption MUST fail.

#### 10.5.4 Secondary Tags

A. Module rewards MAY include secondary tags.

B. Secondary tag selection MUST be deterministic.

C. Secondary tags MUST use the mission_reward_secondary RNG stream.

D. dynamic_source behavior:
   - npc_tags: MAY inject tags sourced from mission giver NPC tags.
   - mission_tags: MAY inject tags sourced from mission tag list (if present).
   - none: No tag injection permitted.

E. Tag injection constraints:
   - Only tags that exist in tags.json MAY be injected.
   - Only tags valid for module context MAY be injected.
   - Tags of incompatible types MUST NOT be injected (no cross-type injection).

F. include_tags and exclude_tags apply to tags generally (primary and secondary).

#### 10.5.5 Storage Rules

A. Mission-granted modules MUST be stored as uninstalled modules.

B. Storage MUST use the existing salvage-style storage concept (player.salvage_modules).

C. Modules MUST NOT be stored as cargo.

D. Installation MUST occur later via shipdock/module install flow.

E. This contract does not define installation behavior.

### 10.6 Hull Voucher Reward Type (New)

#### 10.6.1 Schema Fields

A hull voucher reward profile MUST contain:

- reward_type: "hull_voucher" (required)
- selector: object (required)
  - hull_id: string (optional)
  - frame: string (optional)
  - tier: integer 1-5 (optional)
  - include_tags: array of strings (optional)
  - exclude_tags: array of strings (optional)
  - dynamic_source: "npc_tags" | "mission_tags" | "none" (required)

#### 10.6.2 Selection Rules

A. If selector.hull_id is present:
   - The exact hull specified by hull_id MUST be selected.
   - All other selector fields MUST be ignored.

B. If selector.hull_id is absent:
   - Selection MUST be from hulls.json filtered by selector constraints.
   - frame: Hull MUST match the specified frame type.
   - tier: If omitted, defaults to mission.mission_tier (1-5).
   - include_tags: Hull MUST have all specified tags.
   - exclude_tags: Hull MUST NOT have any specified tags.
   - Selection MUST be deterministic.
   - Exactly one hull MUST be selected.

C. If selection yields zero candidates, reward redemption MUST fail.

#### 10.6.3 Dynamic Source Constraints

A. dynamic_source constraints are identical to module rewards (Section 10.5.4.E).

B. Only tags in tags.json MAY be injected.

C. Only tags valid for hull context MAY be injected.

D. Cross-type tag injection MUST NOT occur.

#### 10.6.4 Voucher Representation

A. A hull voucher MUST be represented as a synthetic SKU stored as data cargo.

B. The voucher SKU MUST have the "data" tag.

C. The voucher SKU MUST consume data cargo capacity.

D. SKU id format: "hull_voucher_<hull_id>"

E. Vouchers MUST NOT be sellable.

F. Markets MUST NOT list voucher SKUs.

G. No trade system interaction is assumed for vouchers.

#### 10.6.5 Redemption Rules

A. Vouchers are redeemable ONLY at shipdock locations.

B. At grant time, sufficient data cargo capacity MUST exist to hold the voucher.

C. If insufficient data cargo capacity exists:
   - Reward redemption MUST fail.
   - No partial grant is permitted.

D. Redemption MUST remove the voucher SKU from cargo.

E. Redemption MUST grant the hull via the existing hull acquisition flow.

F. Redemption MUST NOT require payment.

G. This contract does not define redemption implementation details.

### 10.7 Determinism Requirements for New Reward Types

A. Selection and quantity MUST be deterministic per mission.

B. Three new RNG stream names MUST be used for mission reward resolution:
   - mission_reward_select: For SKU/module/hull selection
   - mission_reward_quantity: For quantity selection (goods only)
   - mission_reward_secondary: For secondary tag selection (modules only)

C. These streams MUST NOT reuse salvage or encounter reward streams.

D. RNG seed format MUST be:
   - mission_reward_select: world_seed + mission_id + reward_profile_id + "select"
   - mission_reward_quantity: world_seed + mission_id + reward_profile_id + "quantity"
   - mission_reward_secondary: world_seed + mission_id + reward_profile_id + "secondary"

### 10.8 Failure Behavior

A. If selection yields no candidates:
   - Reward redemption MUST fail.
   - No partial reward application is permitted.

B. If cargo capacity is insufficient for goods or voucher:
   - Reward redemption MUST fail.
   - No partial reward application is permitted.
   - No automatic warehouse fallback is permitted.

C. Failure MUST be logged with clear reason.

D. Mission state MUST reflect the failure appropriately.

### 10.9 Scope Boundaries

A. This contract defines schema and behavioral rules only.

B. This contract does NOT redefine ship/module/hull schema from their authoritative sources.

C. This contract does NOT define implementation details for redemption flows.

D. This contract does NOT define installation behavior for modules.

E. This contract does NOT define ship creation behavior for hull vouchers.

-------------------------------
