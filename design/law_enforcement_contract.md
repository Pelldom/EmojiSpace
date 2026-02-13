# law_enforcement_contract.md

Status: Authoritative / Binding
Phase: 2.7 - Law Enforcement and Consequence Resolution
Applies To: Government and Law Engine, Player State System, Testing Harnesses

Consumes:
- Government policy result (legality_state, risk_tier)
- Player state (reputation/system, heat/system, licenses/system, warrants/system, fines/system)
- Government fields from governments.json
- World seed
- Active enforcement trigger

----------------------------------------------------------------

## 1. Purpose

This document defines the complete and exclusive rules governing law enforcement
in EmojiSpace for Phase 2.7.

It specifies:
- When inspections may occur
- How enforcement events are triggered
- What player options are available
- How outcomes are resolved
- How numeric government and player fields are used

Any behavior not explicitly allowed here is forbidden.

----------------------------------------------------------------

## 2. Scope and Authority

This contract governs:
- Border patrol inspections
- Customs inspections
- Enforcement encounters
- Consequence resolution
- Player legal status tracking

This contract does NOT govern:
- Pricing
- Market composition
- NPC behavior
- Situations
- Narrative outcomes
- Combat mechanics (stubbed only)

----------------------------------------------------------------

## 3. Numeric Conventions (Global)

All enforcement-related numeric values operate on a 1–100 scale.

### 3.1 Universal Band Thresholds

| Range  | Band Index | Label       |
|--------|------------|-------------|
| 1–20   | -2         | Very Low    |
| 21–40  | -1         | Low         |
| 41–60  | 0          | Neutral     |
| 61–80  | +1         | High        |
| 81–100 | +2         | Very High   |

Band indices are used for enforcement math only.
Players see labels, not indices.

----------------------------------------------------------------

## 4. Player Enforcement State (Per System)

All enforcement state is stored on the player entity.
All values are tracked per system.

### 4.1 Reputation

Reputation represents long-term standing with a system government.

| Score | Band | Meaning |
|-------|------|--------|
| 1–20  | -2   | Notorious |
| 21–40 | -1   | Disliked |
| 41–60 | 0    | Neutral |
| 61–80 | +1   | Respected |
| 81–100| +2   | Esteemed |

Rules:
- Reputation never blocks enforcement
- Reputation may adjust consequence severity by at most one band
- Negative reputation may worsen severity by one band
- Reputation band +2 unlocks eligibility to purchase licenses for restricted goods

### 4.2 Heat

Heat represents short-term enforcement attention.

- Numeric range: 0–100
- Displayed as bands using the universal thresholds

Effects:
- Heat affects inspection probability only
- Heat does not affect legality, pricing, or severity directly

Heat decay:
- -10 per turn while in system
- -20 per turn while outside system

### 4.3 Licensing

- Licenses are per system
- Licenses apply to restricted categories or SKUs
- Licenses allow legal trade of restricted goods
- Licenses are only offered at reputation band +2
- License acquisition is a supported future expansion

### 4.4 Warrants

Warrants represent unresolved serious violations.

Rules:
- Warrants are issued only if the player escapes enforcement
- Warrants are per system
- Warrants do NOT affect inspection probability

Effects:
- If inspected while a warrant exists:
  - Automatic arrest occurs
  - Bribery may still be attempted
- Warrants persist until resolved via enforcement or future systems

### 4.5 Fines

Fines represent outstanding monetary penalties.

Rules:
- Fines are per system
- Fines do NOT affect inspection probability
- If inspected while fines exist:
  - Fines are automatically added to any other consequence
- Fines persist until paid

----------------------------------------------------------------

## 5. Enforcement Triggers

Law enforcement may occur only at defined checkpoints.

### 5.1 Border Patrol (Transit)
- Triggered on system entry
- May inspect Illegal goods only
- Restricted goods are ignored
- Inspection is probabilistic

### 5.2 Customs (Market Access)
- Triggered on attempt to access a market
- May inspect:
  - Illegal goods
  - Restricted goods
- Inspection is probabilistic

----------------------------------------------------------------

## 6. Inspection Probability

Inspection probability is evaluated independently at each checkpoint.

### 6.1 Base Score

inspection_score = government.regulation_level

### 6.2 Modifiers

Apply the following modifiers:

Heat band:
- -2: +0
- -1: +5
-  0: +10
- +1: +20
- +2: +35

Reputation band:
- -2: +15
- -1: +5
-  0: 0
- +1: -10
- +2: -20

Situations may add modifiers in later phases.

### 6.3 Resolution

- Clamp inspection_score to 0–100
- Roll 1–100 (deterministic)
- If roll <= inspection_score, inspection occurs
- Warrants and fines do NOT modify inspection chance

----------------------------------------------------------------

## 7. Enforcement Event

An Enforcement Event is created on a successful inspection roll.

Each event includes:
- Trigger type (Border or Customs)
- System government
- Legality state
- Risk tier
- Player enforcement state snapshot
- Cargo snapshot

The event resolves immediately and consumes its inputs.

----------------------------------------------------------------

## 8. Player Options (Mandatory)

When an Enforcement Event occurs, the player must be presented with:

1. Submit to Inspection
2. Attempt to Flee
3. Attack
4. Attempt to Bribe

No other options are permitted in Phase 2.7.

----------------------------------------------------------------

## 9. Risk Mapping (Authoritative)

Risk tiers from Phase 2.6 map to numeric values:

| Risk Tier | Numeric | Band |
|-----------|---------|------|
| None      | 20      | -2 |
| Low       | 40      | -1 |
| Medium    | 60      | 0  |
| High      | 80      | +1 |
| Severe    | 100     | +2 |

Risk is consumed after an enforcement event.

----------------------------------------------------------------

## 10. Consequence Severity Resolution

### 10.1 Base Severity (Legality + Risk)

Restricted goods:
- Risk -2 or -1: Minor
- Risk 0: Moderate
- Risk +1 or +2: Major

Illegal goods:
- Risk -2 or -1: Moderate
- Risk 0: Major
- Risk +1 or +2: Extreme

### 10.2 Enforcement Strength Adjustment

| enforcement_strength | Effect |
|----------------------|--------|
| 1–40  | No change |
| 41–70 | Normal |
| 71–100| +1 severity band (cap at Extreme) |

### 10.3 Reputation Adjustment

| Reputation Band | Effect |
|-----------------|--------|
| -2 | +1 severity band |
| -1 | No change |
| 0  | No change |
| +1 | -1 severity band |
| +2 | -1 severity band |

Caps:
- Minimum severity: Minor
- Maximum severity: Extreme

### 10.4 Warrants and Fines

- Active warrant:
  - Automatic arrest
  - Severity forced to at least Major
- Outstanding fines:
  - Added to any other consequence

----------------------------------------------------------------

## 11. Option Resolution Rules

### 11.1 Submit to Inspection

If no violations:
- Minor reputation increase
- No heat change

Restricted goods without license:
- Player may:
  - Pay fine or licensing fee
  - Attempt bribe
  - Refuse, escalating enforcement

Illegal goods:
- Consequences resolved per severity rules

### 11.2 Attempt to Flee

Resolved via deterministic 50/50 pass/fail.

Border Patrol:
- Success: enter system, heat increase, reputation loss, warrant issued
- Failure: arrest

Customs:
- Success: flee market, market access denied
- Failure: arrest

### 11.3 Attack

Resolved via deterministic 50/50 pass/fail.

Success:
- Escape
- Heat increases sharply
- Warrant issued
- Possible major reputation loss

Failure:
- Arrest or death (game over)
- Major reputation loss

### 11.4 Attempt to Bribe

Bribery success chance:

base = government.bribery_susceptibility

Modifiers:
- Bribe amount tier:
  - Small: +0
  - Medium: +15
  - Large: +30
- Enforcement strength: -(enforcement_strength / 2)
- Post-inspection attempt: -20

Clamp final chance to 0–85.

Rules:
- Bribery may be attempted once per event
- If final chance <= 0, bribery always fails
- If final chance > 0, roll deterministically

Success:
- Pay bribe
- Minimal reputation impact
- Heat may still increase

Failure:
- Fine or arrest
- Reputation loss
- Heat increase

----------------------------------------------------------------

## 12. Logging Requirements

Every enforcement event must log:
- Trigger type
- Inspection roll and score
- Player option selected
- Severity before and after adjustments
- Reputation change
- Heat change
- Warrants issued or cleared
- Fines issued or paid

If an outcome cannot be reconstructed from logs, it is a failure.

----------------------------------------------------------------

## 13. Contract Statement

This document is authoritative.

Any system that triggers enforcement or applies consequences
MUST conform to this contract.

Any deviation requires updating this document first.

----------------------------------------------------------------

Status:
Phase 2.7 law enforcement is fully specified.
Cursor requires no inference.
Future systems may extend but not alter these rules.
