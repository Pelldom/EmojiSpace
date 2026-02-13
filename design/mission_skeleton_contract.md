# EmojiSpace - Mission Skeleton Contract

Status: DRAFT (Evolving)
Phase: 3
Applies To: Mission structure only

This document defines the structural model for missions in EmojiSpace.
Missions are stateful references that track objectives and outcomes.
Missions do not resolve gameplay logic.

----------------------------------------------------------------

## 1. Core Definition

A Mission is a persistent state object that:
- references existing entities
- tracks progress toward declared objectives
- records resolution outcomes

Missions may reference NPCs, locations, ships, data, and the Player Entity.

Missions do NOT:
- resolve combat
- grant rewards
- calculate legality
- apply enforcement
- advance time
- determine narrative consequences

----------------------------------------------------------------

## 2. Mission Identity

Each mission MUST have:

- mission_id (unique identifier)
- mission_type (e.g. delivery, bounty, exploration, smuggling)
- mission_tier (integer 1 through 5)
- persistence_scope (ephemeral | persistent | systemic)
- mission_state

Mission state values:
- offered
- accepted
- active
- resolved

----------------------------------------------------------------

## 3. Mission Tiers

Mission tiers range from 1 (lowest) to 5 (highest).

Tier meanings:

- Tier 1:
  Entry-level missions with minimal risk and limited consequences.
  Intended for early gameplay and system onboarding.

- Tier 2:
  Standard missions with moderate risk and recoverable consequences.

- Tier 3:
  Advanced missions with high risk, enforcement exposure,
  and meaningful failure consequences.

- Tier 4:
  Expert-level missions with severe risk, strong faction or
  government involvement, and major penalties on failure.

- Tier 5:
  Extreme or endgame missions with system-wide or multi-system impact.
  Failure may permanently alter progression or world state.

Rules:
- Mission tier signals expected difficulty and consequence scope
- Mission tier does NOT calculate rewards or penalties
- Mission tier may be used by other systems to:
  - gate mission availability
  - gate mission acceptance
  - scale consequences
  - unlock progression

Mission entities do not enforce tier restrictions.

----------------------------------------------------------------

## 4. Mission Lifecycle

Standard lifecycle:
1. Offered
2. Accepted
3. Active
4. Resolved

Terminal outcomes:
- completed
- failed
- abandoned

Rules:
- Abandonment is voluntary failure initiated by the player
- Abandonment immediately resolves the mission
- All terminal outcomes release mission slots
- Missions record outcome and failure reason if applicable

----------------------------------------------------------------

## 5. Mission Capacity and Slots

Rules:
- Missions consume Player Entity mission slots while ACTIVE
- Mission acceptance requires available mission slots
- Mission slot enforcement is handled by the Player Entity
- Missions do not manage slot availability

At game start:
- Player has one mission slot

Mission slots may expand via progression, but expansion logic
is not defined in this contract.

----------------------------------------------------------------

## 6. Mission References

A mission may reference the following entities.

NPC references:
- mission_giver_npc_id (Tier 2 or Tier 3 NPC only)
- target_npc_id (optional)

Location references:
- origin_location_id
- destination_location_id
- system_scope (optional)

Ship references:
- target_ship_id (optional)
- player_ship_id (resolved at runtime)

Data references:
- related_sku_ids
- related_event_ids (future)
- DataNet hooks (news, mail, intel)

----------------------------------------------------------------

## 7. Objectives

Objectives are declarative conditions that must become true.

Examples:
- cargo_delivered
- npc_contacted
- ship_destroyed
- system_visited
- data_acquired

Rules:
- Missions define objectives declaratively
- Other systems evaluate objective completion
- Missions do not execute objective logic

----------------------------------------------------------------

## 8. Progress Tracking

Missions may track:
- objective completion flags
- progress counters (optional)

Rules:
- Missions do not infer progress
- Progress is updated externally by other systems

----------------------------------------------------------------

## 9. Outcomes

Mission outcomes may declare:
- NPC flag updates
- Player Entity flag updates
- Reputation deltas (references only)
- Unlocking follow-up missions
- Triggering future events (reference only)

Rules:
- Missions declare outcomes
- Other systems apply effects
- Missions do not grant rewards directly

----------------------------------------------------------------

## 10. Failure and Abandonment

Failure:
- Triggered by system conditions
- Examples:
  - time_expired
  - target_destroyed
  - cargo_lost
  - player_arrested

Abandonment:
- Triggered explicitly by the player
- Treated as voluntary failure
- Immediately resolves the mission
- Frees the mission slot

Rules:
- Missions record failure or abandonment reason
- Missions do not apply penalties

----------------------------------------------------------------

## 11. Promotion and Escalation Hooks

Missions may expose hooks to:
- promote NPC persistence tier
- unlock additional missions
- escalate mission chains
- trigger world events (future)

Hooks do not perform logic directly.

----------------------------------------------------------------

## 12. Explicit Non-Responsibilities

Missions do NOT:
- grant credits
- grant items
- calculate experience
- determine legality
- resolve combat
- enforce consequences
- manage Player Entity progression

Missions track state only.

----------------------------------------------------------------

## 13. Evolution Notes

This contract is intentionally incomplete.

Future phases may add:
- branching mission chains
- dynamic objectives
- mission reputation weighting
- endgame mission structures

All additions MUST preserve the principle that
missions track state but do not resolve outcomes.


----------------------------------------------------------------
## Mission Generation Notes (Advisory)

This section provides non-binding guidance for how missions
may be generated and surfaced. These notes describe intent
and desired feel, not hard rules.

Mission generation is intentionally flexible and may evolve.

----------------------------------------------------------------

### 1. Discovery Philosophy

Mission discovery is meant to feel:
- opportunistic
- uneven
- contextual
- occasionally surprising

Missions should not feel like a static job board or checklist.
Empty locations are acceptable and intentional.

----------------------------------------------------------------

### 2. Source Density (General Guidance)

Typical expectations by source:

- Bars:
  - Primary source of informal missions
  - Often 1 to several missions available
  - Variability is encouraged

- Administration:
  - More structured and predictable
  - Often fewer missions available at once
  - May remain stable over time

- Ship-to-ship encounters:
  - Missions arise contextually
  - Often time-sensitive or immediate
  - Not guaranteed to occur

- DataNet:
  - Rare
  - Often zero missions available
  - When present, missions are significant

These are tendencies, not constraints.

----------------------------------------------------------------

### 3. Mission Tier Distribution (Advisory)

Mission tiers may skew by source:

- Bars:
  - Commonly Tier 1 to Tier 3
  - Higher tiers possible via special NPCs

- Administration:
  - Commonly Tier 2 to Tier 4
  - Tier 5 reserved for major crises

- Ship-to-ship encounters:
  - Any tier, driven by context

- DataNet:
  - Commonly Tier 3 to Tier 5
  - Often systemic or world-affecting

Mission tier is informational and should not be treated
as a gating mechanism.

----------------------------------------------------------------

### 4. Repeatability and Refresh

- Repeatable missions may reappear over time
- Unique missions should not reappear once resolved
- Mission availability may refresh based on:
  - time passage
  - mission completion
  - leaving and re-entering a system
  - world state changes

Refresh behavior is intentionally undefined at this phase.

----------------------------------------------------------------

### 5. World State Sensitivity

Mission generation may consider world conditions such as:
- plagues
- shortages
- piracy levels
- faction presence
- recent major events

World state may increase likelihood of certain missions
but should not guarantee them.

----------------------------------------------------------------

### 6. DataNet Missions (Special Handling)

DataNet missions represent major events or opportunities.

Guiding principles:
- DataNet missions are rare
- DataNet missions bypass player mission filters
- DataNet missions often have substantial or unique outcomes
- Examples include:
  - donation drives
  - crisis response
  - system-wide state changes
  - progression unlocks (e.g. additional mission slots)

DataNet missions are events, not routine jobs.

----------------------------------------------------------------

### 7. Non-Goals

Mission generation rules do NOT aim to:
- ensure constant mission availability
- guarantee balanced mission offerings
- prevent players from attempting high-risk missions
- enforce progression

Discovery and unevenness are intentional.

----------------------------------------------------------------

## 14. Contract Authority

This document is authoritative for mission structure.

Changes require:
- explicit revision
- version update
- review before Cursor implementation
