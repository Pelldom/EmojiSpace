# EmojiSpace Time Engine Contract

Version: 1.0
Status: LOCKED (pending final confirmation)
Phase: 3.1 - Time Engine
Location: /design/time_engine_contract.md

---

## 1. Purpose

The Time Engine defines the authoritative rules for how time exists, progresses, and is observed in EmojiSpace.

Time is a foundational system relied upon by:
- Economy
- Government and Law Enforcement
- Missions
- Situations
- NPC persistence

This contract ensures that time progression is deterministic, explicit, and consistent across the entire simulation.

No system may invent, infer, or advance time outside the rules defined here.

---

## 2. Core Principles

1. Time is discrete and turn-based.
2. There is exactly one global simulation clock.
3. Time advances only through explicit player-initiated actions.
4. Time progression is deterministic and replayable.
5. All systems observe time; no system controls it except via approved interfaces.

---

## 3. Canonical Time Representation

### 3.1 Authoritative Time Value

- The sole authoritative time value is `current_turn`.
- `current_turn` is an integer representing total days elapsed since game start.
- Game start:
  - `current_turn = 0`
  - Corresponding calendar date: `2200.0.0`

No other time values are stored or persisted.

---

## 4. Derived Calendar Representation

### 4.1 Calendar Structure

The in-game calendar is a derived, informational projection of `current_turn`.

- Format: YEAR.MONTH.DAY
- Month and day values are zero-based.
- Structure:
  - 1 day = 1 turn
  - 10 days = 1 month
  - 10 months = 1 year
  - 1 year = 100 turns

Example:
- `current_turn = 345`
- Date = `2203.4.5`

### 4.2 Rules

- Calendar values are never stored independently.
- Calendar values may not be mutated.
- All gameplay logic keys exclusively off `current_turn`.
- Month and year boundaries have no inherent mechanical meaning.

---

## 5. What a Day Represents

A day represents the passage of strategic opportunity for the universe to react.

A day is not:
- Continuous simulation time
- Local activity duration
- Physical travel minutiae

A day is consumed only by explicit commitment actions.

---

## 6. Time Advancement Authority

- Only player action resolution may advance time.
- No background system may advance time autonomously.
- No UI, inspection, combat, or dialog action may advance time unless explicitly declared.

---

## 7. Actions That Advance Time

### 7.1 Interstellar Travel

- Cost: 1 day per light-year traveled
- Distance must be an integer
- Time advanced equals distance in days

### 7.2 Intra-System Travel

- Traveling to any destination within a system costs exactly 1 day
- Destination types include (non-exhaustive):
  - Planets
  - Stations
  - Ships
  - Unknown contacts

### 7.3 Wait

- Explicit player action
- Advances time by N days
- Subject to all rules below

---

## 8. Time Advancement Constraints

- Time may only advance in whole days.
- Minimum advance: 1 day
- Maximum advance per action: 10 days
- Fractional, zero, or negative advancement is forbidden.

---

## 9. Multi-Day Advancement Semantics

- Any action advancing N days is internally expanded into N sequential single-day ticks.
- No batching or skipping is permitted.
- Each day is processed fully and in order.
- Multi-day advancement is interruptible.

---

## 10. Daily Processing Order

Each single-day tick is processed in strict top-down order:

1. Galaxy-level processing
2. System-level processing
3. Planet or Station-level processing
4. Location-level processing
5. NPC-level processing
6. End-of-day logging

All layers are invoked even if they are no-ops in early phases.

---

## 11. Interruptibility and Hard Stops

Time advancement halts immediately if a hard stop condition occurs.

Hard stops include:
- Player death
- Tier 2 detention (Game Over)
- Any future forced state requiring immediate player input

Rules:
- All completed days remain processed.
- No rollback occurs.
- Remaining days are discarded.

---

## 12. Encounters and Inspections

- All random encounters occur after travel completes.
- No mid-travel encounters exist in Phase 3.x.
- Encounters are additive, not substitutive.

Example:
- Player travels to a destination.
- Time advances.
- A random encounter may occur.
- After the encounter, the intended destination interaction proceeds.

---

## 13. Local Actions and Time

Local actions at a destination do not advance time by default, including:
- Market transactions
- Conversations
- Inspections
- Encounters
- Combat resolution
- Mission acceptance

Any future action that consumes time must explicitly declare that cost.

---

## 14. Cross-Day Invariants

The following may not change mid-day:
- Player location
- Market composition
- Government type
- Core world state

All such changes occur only at day boundaries.

---

## 15. Save and Load Rules

- Save and load operations are time-neutral.
- Loading a save does not trigger time advancement.
- Only `current_turn` is persisted as time state.

---

## 16. Determinism Requirements

- Given the same initial state, world seed, and player actions, time progression is identical.
- Randomness during daily ticks must be seed-deterministic.
- Calendar representation must never influence logic.

---

## 17. Testing Hooks

- Test-only time advancement hooks are permitted.
- These hooks:
  - Are not exposed to gameplay
  - Obey all Time Engine rules
  - Respect the 1-10 day cap

---

## 18. Logging Requirements

Minimum required logs:
- Each time advancement request:
  - Starting turn
  - Days requested
  - Reason
- Each completed day:
  - Turn number
  - Any hard stop flags

Logs must support full state reconstruction.

---

## 19. Forbidden Behaviors

Explicitly forbidden:
- Autonomous time advancement
- Time advancement during UI browsing, dialog, or combat
- Fractional or negative time
- Mid-day state exposure
- Calendar-based branching logic
- Any system mutating time directly

---

## 20. Contract Authority

This document is authoritative.

All systems that depend on time must conform to this contract.

Changes require:
- Explicit revision
- Version update
- Review prior to any implementation changes

---

End of Time Engine Contract
