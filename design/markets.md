# Market Creation — Authoritative Process

**Status:** Authoritative / Binding  
**Applies To:** World Generator, Economy Engine, Testing Harnesses  
**Consumes:**
- `/data/categories.json`
- `/data/goods.json`
- `/data/economies.json`
- Population data (Phase 1.5)

This document defines **how a system market is created at world generation**.  
All implementations must follow this process exactly.

---

## 1. Scope & Timing

Market creation occurs:
- **once**, during world generation
- **before** any simulation steps
- **before** government, NPCs, or situations act

Markets do **not** regenerate during play.  
They may only be modified later by simulation systems.

---

## 2. Required Inputs (Per System)

Each system must provide:

- `population` (integer 1–5)
- `primary_economy` (exactly one)
- `secondary_economies` (zero or more)
- `world_seed`

No other inputs are permitted at creation time.

---

## 3. Economy Aggregation

Collect all economies present:
- primary economy
- all secondary economies

All economies contribute equally.  
There is no priority or weighting between economies at this stage.

---

## 4. Category Role Resolution

For **each canonical category**, determine its role using this order:

1. **Produced**
   - if category appears in `produces` of any economy
2. **Consumed**
   - else if category appears in `consumes` of any economy
3. **Neutral**
   - else if category appears in `neutral_categories` of any economy
   - and the neutral roll succeeds
4. **Absent**
   - otherwise

Rules:
- Produced overrides consumed
- Consumed overrides neutral
- Neutral never overrides produced or consumed
- No caps exist on the number of categories present

---

## 5. Neutral Category Rolls

Neutral categories are resolved as follows:

1. Build a candidate set from all `neutral_categories`
2. De-duplicate the set
3. For each candidate:
   - roll once using a population-scaled chance
   - on success, include the category as `neutral`

Neutral categories:
- add market breadth
- do not imply production or shortage

---

## 6. Population & Market Variety

Population controls **variety**, not identity.

### Core Rule

> **Population = maximum number of distinct goods per category**

| Population | Max Goods per Category |
|-----------|------------------------|
| 1 | 1 |
| 2 | 2 |
| 3 | 3 |
| 4 | 4 |
| 5 | 5 |

This rule applies uniformly to:
- produced categories
- consumed categories
- neutral categories

No exceptions.

---

## 7. Goods Selection (Per Category)

For each category that is present:

1. Collect all goods belonging to that category
2. Apply deterministic weighting:
   - alignment with system economies
   - category role bias (Produced > Neutral > Consumed)
3. Select up to `population` goods
4. Resolve each good’s `possible_tag` (if any)

Once selected:
- goods are fixed
- tags are immutable
- the market definition is complete

---

## 8. Determinism & Logging (Required)

All steps must be:
- seed-driven
- reproducible
- logged in a human-readable way

At minimum, logs must record:
- economies present
- category roles
- neutral roll outcomes
- goods selected per category
- possible tag resolutions

If a result cannot be explained via logs, it is a failure.

---

## 9. Explicit Non-Responsibilities

Market creation does **not**:
- assign prices
- determine legality
- simulate scarcity
- react to situations
- mutate during runtime

Those behaviors belong to downstream systems.

---

## 10. Contract Statement

Any system that:
- creates markets
- reads markets
- modifies markets

**must conform to this document**.

Changes to behavior require updating this document first.

---

## Appendix: Market Creation — Concrete Resolution Rules

This appendix defines the explicit, non-negotiable numeric and procedural rules
required to implement market creation without inferred behavior.

These rules are authoritative and override any implicit assumptions.

---

### 1. Neutral Category Roll Chance

Neutral categories are resolved per category using a population-based lookup table.

#### Neutral Roll Chance by Population

| Population | Neutral Category Chance |
|------------|-------------------------|
| 1          | 20%                     |
| 2          | 30%                     |
| 3          | 40%                     |
| 4          | 55%                     |
| 5          | 70%                     |

#### Application Rules

- Each neutral candidate category is rolled **once**
- Rolls are deterministic using the world seed
- No cap exists on the number of neutral categories
- Neutral categories add market breadth only
- Neutral categories never override produced or consumed categories

---

### 2. Goods Selection Weighting

Goods are selected **per category**, up to the population-based cap.

#### Population Cap

- The maximum number of goods per category equals the system’s population level
max_goods_per_category = population_level

#### Weighting Model

Weighting is applied **per good**, based on the resolved role of the category.

| Category Role | Selection Weight |
|---------------|------------------|
| Produced      | 3.0              |
| Neutral       | 1.5              |
| Consumed      | 1.0              |

#### Selection Rules

- Weighting affects only which goods are selected
- Weighting does not affect prices, production, or consumption
- Selection must be deterministic (seeded)
- If available goods are fewer than or equal to the cap, include all goods

---

### 3. Possible Tag Resolution

Possible tags are resolved **once at market creation**.

#### Base Rules

- A good may have **at most one** possible tag
- Resolution is permanent
- No rerolls or runtime mutation are allowed

#### Base Chance
BASE_POSSIBLE_TAG_CHANCE = 10%


#### Economy Bias Application

- For each economy present:
  - If the economy defines a matching `possible_tag_bias`, add that value
- Biases are **additive**
- The final chance is **capped at 50%**

#### Final Chance Formula
final_chance = min(BASE_POSSIBLE_TAG_CHANCE + sum(economy.possible_tag_bias[tag]),0.50)


#### Resolution Rules

- Roll once per good
- On success, apply the tag permanently
- On failure, the good remains untagged

---

### 4. Economy Assignment Rules

#### Primary Economy

- Every system has **exactly one** primary economy
- The primary economy is selected deterministically using the world seed
- All economy types are equally eligible unless restricted elsewhere

---

#### Secondary Economies

Secondary economies represent additional economic influences on a system.

##### Base Chance

- The base chance for a secondary economy to appear is **33%**
- This chance is applied **per secondary economy slot**

##### Population-Based Slot Limits

| Population | Maximum Secondary Economies |
|------------|-----------------------------|
| 1–2        | 1                           |
| 3          | 2                           |
| 4          | 3                           |
| 5          | 3                           |

Population determines the **maximum number of attempts**, not a guaranteed count.

##### Selection Process

For each system:

1. Determine the maximum number of secondary economy slots based on population
2. For each slot:
   - Roll once against the **33% base chance**
   - On success:
     - Select one economy at random (seeded)
     - The economy must not duplicate the primary or an existing secondary
   - On failure:
     - The slot remains empty
3. Stop when:
   - All slots have been attempted, or
   - No eligible economies remain

##### Additional Rules

- Secondary economies must be **distinct**
- Order of economies is irrelevant
- All economies (primary and secondary) contribute **equally** to market creation
- No dominance, priority, or weighting exists between economies

---

### Contract Statement

With this appendix in place, market creation rules are fully specified.

No system may invent probabilities, formulas, or selection logic.
Any change to market creation behavior requires updating this document first.

---

## Appendix: SKU-Centric Market Resolution

This appendix refines market creation rules to operate at the **SKU (good) level**
rather than assigning a single role to an entire category.

This model is authoritative and replaces any category-level role assumptions.

---

### Core Principles

- **Categories determine eligibility**, not behavior
- **Each SKU has exactly one role** in a market:
  - Produced
  - Consumed
  - Neutral
- Different SKUs within the same category may have different roles
- SKUs are immutable once created

---

### Population Application (Per Role)

Population applies **per role**, not per category.

In a system with population level **N**, for each category:

- Up to **N Produced SKUs**
- Up to **N Consumed SKUs**
- Up to **N Neutral SKUs**

Population limits **depth per role**, not total category size.

---

### SKU Role Assignment Order

For each category present in the market, SKUs are assigned roles in the
following strict order:

1. **Produced**
2. **Consumed**
3. **Neutral**

Each step:
- Has its own population-based cap
- Draws from remaining eligible SKUs only
- Never reuses a SKU already assigned a role
- Does not backfill if insufficient goods exist

If there are fewer eligible SKUs than the cap, all available SKUs are used.

---

### Role Eligibility

For a given SKU:

- **Produced** is allowed if *any* economy (primary or secondary)
  lists the category as produced
- **Consumed** is allowed if *any* economy lists the category as consumed
- **Neutral** is allowed only if the category passed the neutral roll

A SKU may only be assigned **one** role.

---

### Possible Tags and SKU Identity

Possible tags create **new, distinct SKUs**.

- Tagged and untagged goods are **not the same SKU**
- Example:
  - `Spice Wine`
  - `Luxury Spice Wine`
- Both SKUs may coexist in the same market
- Tagged SKUs do **not** replace base SKUs

Tagged SKUs:
- Are created during market generation
- Inherit category and base properties
- Add the resolved tag to their identity
- Are treated independently for role assignment

---

### Selection Pool Rules

- Base SKUs and tagged SKUs coexist in the candidate pool
- Once a SKU is assigned a role, it is removed from further consideration
- Unselected SKUs do not appear in the market

---

### Design Intent

This model allows:
- Fine-grained economic behavior within a category
- Meaningful population scaling
- Organic SKU growth via tags
- Multiple economies influencing the same category without conflict

Any change to SKU role assignment must update this document first.

