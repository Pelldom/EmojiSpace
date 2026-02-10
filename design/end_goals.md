# EmojiSpace - End Goals Contract

Status: LOCKED (Single Source of Truth)
Location: /design/end_goals.md

This document defines the authoritative win and lose conditions for EmojiSpace.

All future systems (economy, combat, missions, UI, NPCs, progression) must conform to this contract.
No system may introduce alternate victory, failure, or progression logic without explicitly updating this document.

---

## 1. Design Intent

EmojiSpace is a systemic sandbox. Players are not assigned classes or roles.

A player's identity emerges from consequences of play, not from time spent or passive accumulation.

The game ends only when:

* The player irreversibly loses agency, or
* The player achieves and secures dominance in one major axis of play

---

## 2. Lose Conditions (Hard Failures)

Lose conditions are immediate and final. There is no recovery once triggered.

### 2.1 Combat Loss - Death

Trigger:

* Player ship is destroyed
* No escape or surrender outcome is available

Result:

* Immediate Game Over

---

### 2.2 Reputation Loss - Tier 2 Arrest

Trigger:

* Player is captured under Tier 2 legal enforcement
* Represents life imprisonment, execution, or permanent removal from play

Result:

* Immediate Game Over

---

### 2.3 Economic Loss - Bankruptcy

Trigger:

* Credits less than or equal to 0
* No sellable assets remain
* No usable ship OR ship seized
* No available loan options

Result:

* Immediate Game Over

---

## 3. Progression Model Summary

Progression is tracked using six additive tracks, grouped into three opposing pairs.

* Each track ranges from 0 to 100
* Thresholds occur every 20 points
* Tracks increase only through qualifying actions
* Tracks do not decay automatically
* Reductions are explicit, intentional, and costly

High progression in one track may block victory in its opposing track.

---

## 4. Progression Axes

### 4.1 Reputation Axis

Tracks:

* Trust: Formal legitimacy and reliability across systems
* Notoriety: Formal recognition as a persistent offender

Primary Drivers:

* Per-system reputation reaching plus or minus 2 thresholds
* Licenses (Trust)
* Warrants (Notoriety)
* Mission outcomes

Key Rules:

* Each system may contribute to Trust or Notoriety once at a time
* Loss of a license or warrant removal immediately removes its contribution

---

### 4.2 Economic Axis

Tracks:

* Entrepreneur: Legitimate, declared economic capacity
* Criminal: Illicit, undeclared economic capacity

Primary Drivers:

* Maintained economic holdings
* Legal market participation (Entrepreneur)
* Illicit goods storage (Criminal)

Key Rules:

* Holdings must exceed a minimum value threshold
* Loss, seizure, or sale immediately removes contribution
* Requires persistent goods storage at locations or idle ships

---

### 4.3 Combat Axis

Tracks:

* Law: Violence against illegitimate targets
* Outlaw: Violence against legitimate targets

Primary Driver:

* Qualifying Defeats, not kills

A Defeat occurs when the player neutralizes a target through:

* Destruction
* Surrender
* Capture

---

## 5. Threat Rating System (Combat Guardrails)

All combat-capable entities have a Threat Rating (TR) from 1 to 5.

Threat Rating Meaning:

* 1: Small, lightly armed
* 2: Standard combat ship
* 3: Heavily armed or elite
* 4: Military grade or group threat
* 5: Extreme danger (task force or capital)

Combat Progression Rules:

* 1 qualifying Defeat equals 1 point
* Defeat counts only if target Threat Rating meets current threshold

Threshold Rules:

* Track score 0 to 19 requires TR 1 or higher
* Track score 20 to 39 requires TR 2 or higher
* Track score 40 to 59 requires TR 3 or higher
* Track score 60 to 79 requires TR 4 or higher
* Track score 80 to 99 requires TR 5

Track Direction:

* Pirate or wanted criminal defeated adds to Law
* Civilian, trader, or authority defeated adds to Outlaw

---

## 6. Win Conditions (Victory Eligibility)

A player becomes eligible for victory when:

* One track reaches 100
* The opposing track in that pair is less than or equal to 50
* The player is not currently in a loss state

Victory is not automatic.

When eligible, the player is offered a Victory Mission tied to that axis.

---

## 7. Victory Missions (Run Finalization)

Victory Missions are:

* One time only
* High risk
* Thematic
* Mandatory to finalize a win

Failure or abandonment does not end the game, but removes victory eligibility until conditions are restored.

Victory missions remain valid once accepted even if tracker values fluctuate. Failure penalties reduce eligibility but do not invalidate the mission system.

### 7.1 Reputation Victories

Trust Victory - Charter of Authority

* Travel to a designated high authority system
* Submit to final review and recognition
* Formalize legitimacy

Notoriety Victory - Escape the DataNet

* Reach a low enforcement system
* Evade final pursuit
* Disappear into legend

---

### 7.2 Economic Victories

Entrepreneur Victory - Retirement Acquisition

* Purchase or claim a major asset (station, moon, planet)
* Requires clean standing and liquidity

Criminal Victory - Secure the Hoard

* Consolidate illicit holdings into a final secure location
* Avoid seizure during transfer

---

### 7.3 Combat Victories

Law Victory - Crown of Order

* Defeat a top tier threat in a destabilized system
* Restore order

Outlaw Victory - Rule Through Fear

* Defeat system defenders
* Force submission through dominance

---

## 8. Titles and Identity Feedback

Each track grants player facing titles at each threshold.

* Titles are informational only
* Titles do not affect NPC behavior
* Titles exist to communicate identity and progress

---

## 9. Finality Rule

A run is won only when:

* A Victory Mission is successfully completed
* The end state is explicitly confirmed

Until then:

* Victory eligibility may be lost
* Tracks continue to update normally

---

## 10. Enforcement

This document is the single source of truth for end game logic.

Any system that:

* Changes win conditions
* Alters loss triggers
* Introduces alternate progression paths

Must update this file explicitly.

No exceptions.
