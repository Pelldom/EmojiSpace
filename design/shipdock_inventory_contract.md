# Shipdock Inventory Contract
Version: 0.6.5
Phase: 4.7 Deterministic Ship Generation (Shipdock)

---

## Authority and Scope

This contract defines deterministic shipdock inventory generation for:

- Hulls
- Modules

This system:

- Is deterministic.
- Is population-scaled.
- Does not modify combat math.
- Does not modify assembler logic.
- Does not generate secondary tags for sale.
- Does not override legality rules (economy/government remain authoritative).

Shipdock inventory generation is presentation-layer selection only.

---

## Inputs

Shipdock generation requires:

- world_seed (int)
- system_id (string)
- system_population (int 1-5)
- full hull catalog (validated)
- full module catalog (validated)

Population must already be determined by world generation.

---

## Determinism Rules

All shipdock inventory must be deterministic given:

(world_seed, system_id, system_population)

Separate deterministic streams must be used for:

- "shipdock_modules"
- "shipdock_hulls"

The same system with the same seed must always produce the same inventory.

---

## Purchase Bans

The following items must never appear in shipdock inventory:

Modules:
- Any module instance with secondary:prototype
- Any module instance with secondary:alien

Hulls:
- Any hull flagged as experimental (if marked non-purchasable in data)
- Any hull flagged as alien (if marked non-purchasable in data)

Prototype and Alien modules are only obtainable via:
- Missions
- Salvage
- Events
- Exploration

They are never purchasable.

---

## Population Scaling

Population controls inventory breadth.

Values below represent maximum offers.

Zero offers is acceptable.

### Module Offers (Unique Entries)

| Population | Max Modules |
|------------|------------|
| 1          | 0-2        |
| 2          | 0-3        |
| 3          | 0-5        |
| 4          | 0-6        |
| 5          | 0-8        |

### Hull Offers (Unique Entries)

| Population | Max Hulls |
|------------|----------|
| 1          | 0-2      |
| 2          | 0-3      |
| 3          | 0-4      |
| 4          | 0-5      |
| 5          | 0-6      |

The generator must not exceed these limits.

---

## Stock Chance Gate

Inventory presence is probabilistic but deterministic per seed.

### Module Stock Probability

| Population | Probability |
|------------|------------|
| 1          | 50%        |
| 2          | 65%        |
| 3          | 80%        |
| 4          | 90%        |
| 5          | 95%        |

### Hull Stock Probability

| Population | Probability |
|------------|------------|
| 1          | 70%        |
| 2          | 80%        |
| 3          | 90%        |
| 4          | 95%        |
| 5          | 98%        |

If stock roll fails, return empty list for that category.

---

## Rarity Controls (Modules)

Rare modules are defined as:

rarity_tier == "rare"

Rare module caps per population:

| Population | Max Rare Modules |
|------------|------------------|
| 1          | 0                |
| 2          | 0                |
| 3          | 1                |
| 4          | 2                |
| 5          | 3                |

If deterministic selection exceeds cap:

- Replace excess rare modules with common selections deterministically.
- Never exceed cap.

---

## Candidate Pools

### Modules

Eligible pool:
- All modules from catalog
- Exclude any with disallowed availability flags
- Exclude secondary-tagged variants
- Use base archetypes only

Selection:
- Weighted by rarity_weight
- Without replacement
- Respect rarity caps

### Hulls

Eligible pool:
- All purchasable hulls
- Exclude experimental and alien purchase-banned frames

Selection:
- Weighted by rarity_weight if defined
- Without replacement

---

## Output Structure

Shipdock inventory returns:

{
"modules": [
{
"module_id": string,
"base_price_credits": int
},
...
],
"hulls": [
{
"hull_id": string,
"base_price_credits": int
},
...
]
}

Display names for modules are not selected at inventory generation time.
Display naming is applied at instantiation or presentation.

No module secondaries are applied during shipdock generation.

---

## Non-Goals

Shipdock inventory must NOT:

- Assemble ships.
- Modify combat.
- Modify degradation.
- Generate secondary tags.
- Override economy legality.
- Override government restrictions.

Shipdock generation is selection-only.

---

## Versioning

This contract introduces deterministic shipdock inventory rules.

Version bump required when implemented:

0.6.5

No engine behavior outside inventory generation is modified.

---
