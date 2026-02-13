###  government_tag_interpretation.md
**Status:** Authoritative / Binding  
**Phase:** 2.6 � Government � Tag Interpretation  
**Applies To:** Economy Engine, Government & Law Engine, Testing Harnesses  
**Consumes:**  
- `governments.json`  
- `tags.json`  
- Market pricing inputs (as defined in `market_pricing_contract.md`)  

---

## 1. Purpose

This document defines how **governments interpret tags** for the purposes of:

- Price bias
- Risk assessment
- Legality defaults

It provides **coarse, bounded numeric rules** suitable for Phase 2.6 implementation.

This document does **not** define:
- Situations
- Culture
- NPC behavior
- Dynamic ideology shifts

Those systems may override outputs later but may not alter rules defined here.

---

## 2. Interpretable Tags

### Possible Tags (Primary Economic Impact)
These tags may affect **price, risk, and legality**:

- luxury
- weaponized
- counterfeit
- stolen
- propaganda
- hazardous
- cybernetic

---

### Fixed Tags (Context Hooks Only)
These tags have **no default economic effect** in Phase 2.6, but may be
interpreted by governments for **risk or legality only**:

Examples include (non-exhaustive):
- medical
- cultural
- essential
- industrial
- technological
- biological
- synthetic
- data
- sentient_adjacent

Fixed tags do **not** apply baseline price changes in Phase 2.6.

---

## 3. Government Fields Used (Exclusive)

Only the following government fields may be consulted:

- regulation_level
- enforcement_strength
- penalty_severity
- tolerance_bias
- bribery_susceptibility
- ideological_modifiers
  - favored_tags
  - restricted_tags
- illegal_goods

No other government data may influence interpretation.

---

## 4. Legality Interpretation (Resolved First)

Legality states are resolved per SKU as follows:

1. If SKU is listed in `illegal_goods` = **Illegal**
2. Else if any SKU tag appears in `restricted_tags` = **Restricted**
3. Else = **Legal**

Definitions:
- **Illegal:** Transaction forbidden
- **Restricted:** Transaction allowed but risky
- **Legal:** No inherent legal risk

Legality resolution occurs **before** pricing.

---

### Consumed Tags (Phase 2.6 Clarification)
When a government rule references a tag (e.g., stolen, counterfeit, weaponized),
that tag is considered **consumed** by Government.

Rules:
- Consumed tags must not be reinterpreted downstream by Pricing.
- Tags not referenced by the government remain eligible for pricing interpretation.

Example:
- SKU tags: [luxury, stolen]
- Government consumes `stolen` → sets legality/risk
- Pricing ignores `stolen` but may still apply `luxury` modifiers

## 5. Risk Tiers (Coarse)

Risk is represented using **four discrete tiers**:

| Tier | Meaning |
|----|--------|
| None | No enforcement attention |
| Low | Minor scrutiny |
| Medium | Noticeable risk |
| High | Serious enforcement risk |
| Severe | Extreme enforcement response |

---

## 6. Base Government Risk Profile

A government�s baseline risk profile is derived as follows:

- High regulation_level = increases risk
- High enforcement_strength = increases risk
- High penalty_severity = increases risk
- High tolerance_bias = decreases risk
- High bribery_susceptibility = decreases risk

Exact numeric conversion is implementation-defined, but output must map
into the risk tiers above.

---

## 7. Possible Tag Interpretation � Default Bands

The following tables define **default Phase 2.6 interpretation**.

These effects are:
- Applied **after** substitute discount
- Bounded
- Additive within caps

---

### 7.1 `luxury`

| Government Trait | Price Bias | Risk |
|------------------|------------|------|
| tolerance_bias > 60 | +20% | Low |
| regulation_level > 70 | -20% | Medium |
| ideological favored | +20% | Low |
| ideological restricted | -20% | Medium |

---

### 7.2 `weaponized`

| Government Type / Trait | Price Bias | Risk |
|-------------------------|------------|------|
| military / fascist / dictatorship | +20% | Medium |
| democracy / collective | -20% | High |
| anarchic | 0% | Low |
| ideological favored | +20% | Medium |
| ideological restricted | -20% | High |

---

### 7.3 `counterfeit`

| Government Trait | Price Bias | Risk |
|------------------|------------|------|
| bribery_susceptibility > 60 | +10% | Medium |
| enforcement_strength > 70 | -30% | High |
| regulation_level > 70 | -20% | High |
| anarchic | 0% | Low |

---

### 7.4 `stolen`

| Government Trait | Price Bias | Risk |
|------------------|------------|------|
| bribery_susceptibility > 60 | +10% | High |
| enforcement_strength > 70 | -30% | Severe |
| tolerance_bias > 70 | 0% | Medium |

---

### 7.5 `propaganda`

| Government Trait | Price Bias | Risk |
|------------------|------------|------|
| ideological aligned | +20% | Low |
| ideological opposed | -20% | High |
| high regulation | -10% | Medium |

---

### 7.6 `hazardous`

| Government Trait | Price Bias | Risk |
|------------------|------------|------|
| regulation_level > 70 | -20% | High |
| enforcement_strength > 70 | -10% | Medium |
| anarchic | 0% | Low |

---

### 7.7 `cybernetic`

| Government Trait | Price Bias | Risk |
|------------------|------------|------|
| technological favored | +20% | Medium |
| conservative / theocratic | -20% | High |
| anarchic | 0% | Low |

---

## 8. Price Bias Caps (Mandatory)

To prevent runaway pricing:

- Total positive tag price bias is capped at **+40%**
- Total negative tag price bias is capped at **-50%**
- Government price bias may not:
  - Override substitute discount
  - Push final price above ideal SKU price

---

## 9. Risk Aggregation Rules

- Risk tiers from tags and government stack upward
- Highest resulting tier is used
- Risk does **not** directly affect price
- Risk resolution occurs in enforcement systems

---

## 10. Fixed Tags in Phase 2.6

Fixed tags:
- Do not alter price by default
- May influence legality or risk only if:
  - Referenced by ideological modifiers
  - Referenced by future systems

They are intentionally inert economically at this phase.

---

## 11. Future Overrides (Explicit)

The following systems may override interpretation outputs later:

- Situation Engine (e.g. plague, war)
- Culture System (e.g. high society, austerity)
- Narrative Triggers

They may:
- Modify price bias
- Modify risk
- Modify legality

They may **not**:
- Add new tags
- Bypass substitute logic
- Reorder pricing steps

---

## 12. Contract Statement

This document is **authoritative**.

Any system that interprets tags for price, risk, or legality must conform
to this document unless explicitly overridden by a later-phase system.

Any deviation requires updating this document first.

---

## Status

With this document and `market_pricing_contract.md` together:

- Phase 2.6 market pricing is fully specified
- Cursor has hard numbers and rules
- No interpretation is required
- Future expansion is clean and non-destructive
