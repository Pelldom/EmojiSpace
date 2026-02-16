## market_pricing_contract.md
**Status:** Authoritative / Binding  
**Phase:** 2.6 � Market Pricing  
**Applies To:** Economy Engine, Government & Law Engine (read-only), Testing Harnesses  
**Consumes:**  
- Market definition (from Market Creation)  
- Goods catalog (`goods.json`)  
- Categories (`categories.json`)  
- Tags (`tags.json`)  
- Government data (`governments.json`)  

---

## 1. Purpose

This document defines the **complete and exclusive rules** governing market pricing in EmojiSpace for Phase 2.6.

It establishes:
- What inputs pricing may consume
- The fixed order of operations
- How buying and selling prices are derived
- How tags and governments influence pricing
- What pricing **must not** do

Any behavior not explicitly allowed here is forbidden.

---

## 2. Scope & Authority

This contract governs:
- Buy prices
- Sell prices
- Substitute valuation
- Tag-based interpretation
- Government price bias

This contract does **not** govern:
- Situations (war, plague, unrest)
- Culture
- NPC behavior
- Dynamic demand curves
- Price volatility over time

Future systems may **override outputs**, but may not alter rules defined here.

---

## 3. Core Principles (Non-Negotiable)

1. Pricing must be deterministic  
2. Pricing must be explainable post-hoc  
3. No system may apply the same reason twice  
4. Eligibility, price, and risk are separate concepts  
5. Tags have no intrinsic meaning; systems interpret them  
6. Governments modify interpretation, not base economics  

---

## 4. Inputs to Pricing (Exclusive List)

Pricing may consume **only** the following inputs:

- SKU base price
- Category role (produced / neutral / consumed)
- Market scarcity
- System population
- System government
- SKU tags (fixed + possible)
- Deterministic world seed
- Government policy result:
  - legality_state
  - risk_tier
  - consumed_tags

No other inputs are permitted.

---

## 5. Buying vs Selling (Hard Rule)

### Buying
- Buying is **SKU-specific**
- A player may only buy SKUs explicitly present in the system market
- Buy price represents the market�s asking price

### Selling
- Selling is **category-based**
- A player may sell **any SKU** whose category is present in the market
- SKU presence determines preference, not eligibility

---

## 6. Ideal vs Substitute Goods

### Ideal Goods
A good is **ideal** if:
- Its SKU is present in the system market

Ideal goods:
- Receive **no substitute discount**

---

### Substitute Goods
A good is a **substitute** if:
- Its category is present
- Its SKU is **not** present

Substitutes are accepted, but discounted.

There are **no other substitute tiers**.

---
Substitute goods inherit the category role (produced / neutral / consumed)
of their category in the system market. Substitutes differ only by the
application of the substitute discount.


## 7. Substitute Discount (Authoritative)

### Discount Band
- All substitute goods receive a base discount between:  
  **-40% and -55%**

### Deterministic Resolution
- The exact discount value is resolved **once per system � SKU**
- Resolution uses:
  - World seed
  - System identifier
  - SKU identifier
- The resolved value is:
  - Deterministic
  - Stable across all transactions
  - Logged

No per-transaction randomness is permitted.

---

## 8. Order of Price Calculation (Fixed)

Pricing must be resolved in **exactly** this order:

1. Start from SKU `base_price`
2. Apply category pressure (produced / neutral / consumed)
3. Apply scarcity modifier
4. If selling and SKU is a substitute:
   - Apply substitute discount
5. Apply tag-based price interpretation
6. Apply government price bias
7. Clamp final price to non-negative only (no upper clamp)
   - final_multiplier = max(0, final_multiplier)

Reordering is forbidden.

Note:
- Pricing MUST NOT apply an upper clamp to final price multipliers.
- WorldState deltas are already capped per world_state_contract.md Section 13.
- Pricing enforces only a non-negative floor to prevent negative prices.

### Category Pressure Multipliers (Phase 2.6)

Category pressure is applied as a coarse multiplier:

- Produced: 0.80
- Neutral: 1.00
- Consumed: 1.20

These multipliers apply to both buy and sell pricing and are applied
before substitute discounts.

---

## 9. Tags � Pricing Rules

### Tag Vocabulary
- The tag list is **fixed and final**
- No new tags may be introduced
- All interpretation uses existing tags only

---

### Tag Meaning
Tags have **no intrinsic economic meaning**.

Tags are interpreted by:
- Government (Phase 2.6)
- Situations (future)
- Culture (future)

---

### Fixed Tags
Examples:
- medical
- cultural
- essential
- industrial
- technological
- biological
- synthetic
- data
- sentient_adjacent

Rules:
- Do not apply baseline price changes
- May be referenced by interpreters
- Have **no default economic effect** in Phase 2.6

---

### Possible Tags
Examples:
- luxury
- weaponized
- counterfeit
- stolen
- propaganda
- hazardous
- cybernetic

Rules:
- May influence price, risk, and legality
- Interpretation is contextual
- No possible tag has unconditional effects

### Government Policy Inputs (Phase 2.6 Clarification)
Pricing consumes a **Government policy result** that includes:
- `legality_state`
- `risk_tier`
- `consumed_tags`

Rules:
- Pricing MUST ignore any tag listed in `consumed_tags`.
- Pricing MAY interpret tags not listed in `consumed_tags`.
- Pricing reacts to `legality_state` and `risk_tier`, but does not redefine them.
- Pricing must not reinterpret `consumed_tags` for price, legality, or risk.

---

## 10. Government Price Bias

Governments:
- Do not set prices
- Do not override economy
- May apply **bounded price bias** when interpreting tags

Government price bias:
- Is coarse (banded)
- Is directional, not granular
- Is capped
- Is applied **after** substitute discount

Numeric values are defined in `government_tag_interpretation.md`.

---

## 11. Price Caps & Safety Rails

To prevent runaway values:

- Total positive tag bias is capped
- Total negative tag bias is capped
- Final sell price may not exceed the ideal SKU price
- Final price may not drop below a minimum salvage value (defined elsewhere)

Exact caps are implementation-defined but must exist.

---
### Salvage Floor

Final prices may not fall below a salvage floor defined as:

SALVAGE_FLOOR = max(1, round(base_price * 0.10))


## 12. Logging Requirements (Mandatory)

Every pricing calculation must be reconstructible from logs.

At minimum, logs must include:
- SKU
- Base price
- Category role
- Substitute status
- Substitute discount value
- Tags considered
- Government applied
- Final price

If a price cannot be explained from logs, it is a failure.

---

## 13. Explicit Non-Responsibilities

Pricing does **not**:
- Change market composition
- Determine legality outcomes
- Apply enforcement consequences
- React to situations
- Model NPC demand
- Advance time

Those behaviors belong to other systems.

---

## 14. Contract Statement

This document is **authoritative**.

Any system that:
- Calculates prices
- Displays prices
- Modifies prices

**must conform to this contract**.

Any deviation requires updating this document first.

---

## Status

With this contract in place:
- Phase 2.6 pricing behavior is fully specified
- Cursor can implement without inference
- Future systems can override cleanly
