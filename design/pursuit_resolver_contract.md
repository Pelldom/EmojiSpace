# EmojiSpace - Pursuit Resolver Contract

Status: Locked
Phase: 4d - Pursuit Resolution
Target Version: 0.5.x
Location: /design/pursuit_resolver_contract.md

----------------------------------------------------------------

## 1. Purpose

The Pursuit Resolver determines the outcome of an escape attempt.

It is invoked when:
- Player chooses flee
- NPC chooses refuse_flee
- Any resolver explicitly dispatches to pursuit

Pursuit determines whether the fleeing party escapes or is forced
into combat.

Pursuit does NOT simulate space movement or persistent chase states.

----------------------------------------------------------------

## 2. Scope and Authority

This contract governs:

- Deterministic evaluation of escape success or failure
- Inputs allowed for pursuit comparison
- Outcome enum
- Logging requirements

This contract does NOT govern:

- Combat resolution
- Ship damage
- World state mutation beyond escape/combat transition
- Population-based modifiers
- Spatial simulation
- Prose generation

----------------------------------------------------------------

## 3. Core Principles (Non-Negotiable)

1. Pursuit must be deterministic
2. Pursuit must compare ship capability bands, not raw stats
3. Population must NOT influence pursuit outcome
4. Pursuit must not simulate time or movement
5. Pursuit returns a binary structural outcome
6. Pursuit must be fully log-reconstructible

----------------------------------------------------------------

## 4. Inputs (Authoritative)

### 4.1 Encounter Context

- encounter_id
- posture
- subtype_id
- flags (optional)

### 4.2 Fleeing Party

- fleeing_ship_TR_band (1..5)
- fleeing_engine_band (1..5; future)
- fleeing_special_components (set; eg cloak, afterburner)
- fleeing_pilot_skill_band (future; optional)

### 4.3 Pursuing Party

- pursuing_ship_TR_band (1..5)
- pursuing_engine_band (1..5; future)
- pursuing_special_components (set; eg interdiction_device)
- pursuing_pilot_skill_band (future; optional)

### 4.4 Situations (Optional Modifiers)

- active_system_situations (eg war zone)

Population MUST NOT be included.

### 4.5 Determinism

- world_seed
- stable_salt = encounter_id + "pursuit"

----------------------------------------------------------------

## 5. Output (Authoritative Enum)

Pursuit MUST return exactly one of:

- escape_success
- escape_fail

Meaning:

escape_success:
- Encounter ends
- No combat initiated

escape_fail:
- Dispatch to combat resolver

----------------------------------------------------------------

## 6. Evaluation Model

Pursuit uses a deterministic capability comparison model.

Base factors:

- Engine band delta (primary factor)
- TR band delta (secondary factor)
- Special components:
  - cloak increases escape chance
  - interdiction_device reduces escape chance
- Pilot/crew skill band (future extension)

Conceptual model:

escape_score =
    engine_delta_weight
  + TR_delta_weight
  + special_component_modifiers
  + skill_delta_weight
  + situation_modifiers

Where:
engine_delta = fleeing_engine_band - pursuing_engine_band
TR_delta = fleeing_TR_band - pursuing_TR_band

Escape likelihood increases with positive score.

----------------------------------------------------------------

## 7. Deterministic Outcome Selection

Procedure:

1. Compute escape_score
2. Map escape_score to probability distribution
3. Use deterministic RNG:
   seed = world_seed + stable_salt
4. Roll and select outcome
5. Log full breakdown

Tie-breaking must use ASCII ordering.

----------------------------------------------------------------

## 8. Special Component Rules (v0.5.x)

Initial rules:

- cloak:
  + positive modifier to escape_score
- interdiction_device:
  + negative modifier to escape_score

No other special components permitted without contract revision.

----------------------------------------------------------------

## 9. Logging Requirements (Mandatory)

Pursuit Resolver must log:

- encounter_id
- fleeing and pursuing bands
- engine bands
- TR bands
- special component modifiers
- computed escape_score
- probability distribution
- deterministic roll value
- final outcome enum

Failure to reconstruct outcome from logs is a contract violation.

----------------------------------------------------------------

## 10. Explicit Non-Responsibilities

Pursuit MUST NOT:

- Deal damage
- Modify cargo
- Apply legal consequences
- Mutate reputation
- Apply rewards
- Generate prose
- Persist chase states

----------------------------------------------------------------

## 11. Contract Authority

This document becomes authoritative once locked.

All escape logic must conform to this contract.
Changes require explicit revision and version update.

----------------------------------------------------------------
