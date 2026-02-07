
Each good belongs to **exactly one** category.

---

## 4. Goods

### 4.1 Definition

A **Good** is a concrete, tradable commodity identified by a unique SKU.

Goods are immutable after world generation.

Each good has:
- `sku` — machine identifier (snake_case)
- `name` — Proper Case display name
- `category`
- `tags`
- optional `possible_tag`

---

## 5. Tags & Possible Tags

### 5.1 Tags

Tags describe intrinsic properties of goods that other systems react to.

Canonical tags are defined in `/data/tags.json`.

Tags:
- are single-word
- lowercase
- immutable after assignment

### 5.2 Possible Tags

A **possible tag** represents contextual specialization.

Rules:
- A good may have **at most one** possible tag
- Possible tags are resolved **once**, at world generation
- If applied, the tag becomes permanent
- Tags never mutate afterward

Only these tags may appear as possible tags:
luxury
weaponized
counterfeit
propaganda
stolen
hazardous
cybernetic


---

## 6. Economies

### 6.1 Definition

An **Economy** represents a system’s economic role.

Economies:
- bias production, consumption, and neutrality
- do **not** imply population size
- do **not** imply technology level
- do **not** imply legality

Economies are defined in `/data/economies.json`.

---

### 6.2 Multi-Economy Systems

Each system has:
- **1 primary economy**
- **0 or more secondary economies**

All economies present contribute equally.

There is **no “mixed” economy type**.

---

### 6.3 Economy Fields

Each economy defines:

- `produces` — categories with local production
- `consumes` — categories with elevated demand
- `neutral_categories` — categories that may appear without pressure
- `possible_tag_bias` — additive chance to apply valid possible tags
- `description` — explanatory only

Economies add bias only; they never override system rules.

---

## 7. Market Category Resolution

For each category, role is determined **in this exact order**:

1. **Produced**
   - if category ? any economy.produces
2. **Consumed**
   - else if category ? any economy.consumes
3. **Neutral**
   - else if category ? any economy.neutral_categories
   - and the neutral roll succeeds
4. **Absent**
   - otherwise

Produced always overrides consumed.  
Consumed always overrides neutral.

No caps are applied to the number of categories present.

---

## 8. Neutral Category Resolution

Neutral categories are resolved as follows:

1. Build a candidate pool from all economies’ `neutral_categories`
2. De-duplicate the list
3. For each candidate:
   - roll once using a population-scaled chance
   - on success, include the category as `neutral`

Neutral categories:
- add breadth, not depth
- never imply production or shortage

---

## 9. Population & Market Variety

### 9.1 Population Meaning

**Population represents market capacity, not advancement.**

Population controls:
- how much variety a market can support

Population does **not** control:
- technology level
- sophistication
- economic identity

---

### 9.2 Goods-Per-Category Cap (Critical Rule)

> **Population level = maximum number of distinct goods available per category**

| Population | Max Goods per Category |
|-----------|------------------------|
| 1 | 1 |
| 2 | 2 |
| 3 | 3 |
| 4 | 4 |
| 5 | 5 |

This cap applies to:
- produced categories
- consumed categories
- neutral categories

No exceptions.

---

## 10. Goods Selection

For each category present:

1. Build a list of all goods in that category
2. Apply weighting:
   - economy alignment
   - role (produced > neutral > consumed)
3. Select up to `population` goods
4. Resolve possible tags for each selected good

Once selected, goods are immutable.

---

## 11. What This System Does NOT Do

The Goods & Economy System does **not**:

- assign legality
- determine prices
- mutate goods at runtime
- model NPC behavior
- react to wars or events

Those behaviors belong to **government**, **economy simulation**, and **situation** systems that *consume* this data.

---

## 12. Summary

This system provides:

- stable economic identity
- deterministic yet varied markets
- explainable outcomes
- clean interfaces for all downstream systems

All future development must treat this document as **authoritative**.

Any deviation requires updating this document first.

