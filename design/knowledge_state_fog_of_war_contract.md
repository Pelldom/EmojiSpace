## Knowledge State / Fog-of-War Contract

### 1. Purpose

The purpose of this contract is to define a centralized, deterministic fog-of-war and player-knowledge model for EmojiSpace.  
It specifies how the game decides:

- **What the player can currently observe** based on location and range.
- **What the player has previously learned and persists as knowledge.**
- **How stale knowledge behaves when the underlying world changes.**

This contract is UI-agnostic and must be respected by all frontends (CLI, UI, prose systems) and by game logic that exposes information to the player.

---

### 2. Scope

This contract governs:

- Knowledge and visibility for **systems** and **destinations**.
- Handling of **live-only information** (situations).
- The separation of **current observability** vs **stored knowledge**.
- Rules for **snapshot creation, refresh, and staleness**.
- The **authoritative sources** for range and reachability.

Out of scope:

- Detailed implementation, data structures, or code.
- Non-location entities (e.g., ships, modules, missions) except where they reference systems/destinations.
- Game balance and narrative design beyond knowledge visibility.

---

### 3. Terminology

#### 3.1 Knowledge levels — systems

- **`unknown` (system)**  
  The system exists in world state but is not yet known to the player. It does not appear as a normal entry on the galaxy map or in travel menus (may appear in future as a generic “unknown” marker). Reserved for hidden/secret/undiscovered systems.

- **`detected`**  
  The player knows that a system exists and where it is, but only with minimal information (e.g., map blip, identifier, basic emoji/type).

- **`scanned_local`**  
  The system is within the active ship’s authoritative jump/fuel range (or otherwise scanned) and has been locally scanned. The player knows system-level government information in addition to what is known at `detected`.

- **`visited` (system)**  
  The player has physically traveled to and entered the system. Stable system-level facts such as population/tier become persistent stored knowledge.

#### 3.2 Knowledge levels — destinations

- **`unknown` (destination)**  
  The destination exists in world state but is not yet known to the player. It does not appear in destination listings or travel menus, unless explicitly revealed by future intel/secret mechanics.

- **`local_visible`**  
  The player is currently in the same system as the destination. The destination is visible in local system views and its stable facts (name/type/population/economies) are observable while in that system. This is **local visibility only** and does not, by itself, count as fully visited knowledge.

- **`visited` (destination)**  
  The player has actually entered the destination. Stable destination-level facts seen during the visit become persistent stored knowledge and remain visible later outside the system.

#### 3.3 Observability vs stored knowledge

- **Current observability**  
  What the player can see **right now** based solely on:
  - Current system/destination location.
  - Authoritative travel reachability (in-range systems).
  - Local menus and immediate environment.

  Examples:
  - Same-system destination local visibility.
  - In-range system government visibility.
  - Live situations at the current system or destination.

- **Stored knowledge**  
  Information that has been learned and **persisted** beyond the immediate context, surviving travel and time until explicitly refreshed by revisiting or other knowledge updates.

  Examples:
  - Visited system population/tier and government.
  - Visited destination population and economies.
  - Destination details learned via actual visit.

- **Stale knowledge**  
  Stored knowledge that no longer matches the underlying world because the world has changed since it was last refreshed. Until revisited, the player continues to see the **last-known** version of these facts.

#### 3.4 Live-only information

- **Situations**  
  Time-varying events or modifiers affecting systems or destinations. Situations are **purely live observability** and are **not** part of persistent knowledge under this contract, unless explicitly expanded by future design.

---

### 4. System knowledge rules

#### 4.1 System knowledge levels

Every system known to the player is in exactly one of the following knowledge levels:

- `unknown`
- `detected`
- `scanned_local`
- `visited`

Systems not present in the knowledge model are treated as `unknown`.

#### 4.2 System visibility fields

For systems, the following fields are governed by knowledge level:

- **primary**: Primary emoji / type used in emoji profile.
- **name**: Display name of the system.
- **government**: Government emoji/name associated with the system.
- **population/tier**: Stable population or tier marker for the system.
- **situations**: System-scope situations currently active (live-only).

#### 4.3 System visibility matrix

The table below defines what is visible to the player at each system knowledge level:

| Level          | Appears in galaxy map / system lists? | Primary | Name | Government | Population/Tier | Situations (system-scope)           |
|----------------|----------------------------------------|---------|------|------------|------------------|-------------------------------------|
| `unknown`      | No (or generic “unknown” marker only) | No      | No   | No         | No               | No                                  |
| `detected`     | Yes (minimal entry/blip)              | Yes     | Yes  | No         | No               | No                                  |
| `scanned_local`| Yes                                   | Yes     | Yes  | Yes        | No               | No                                  |
| `visited`      | Yes                                   | Yes     | Yes  | Yes        | Yes              | Yes, but **only** while currently in that system (live-only) |

Notes:

- “Appears” means eligible to show up in galaxy map legends, travel target lists, and similar views.
- Government visibility at `scanned_local` and above is considered **current observability** when the system is in range, and may also be persisted as stored knowledge.
- Population/tier is **never** visible below `visited`.
- Situations are never persisted; they are visible only when the player is physically present in the system and must be re-queried from world state each time.

---

### 5. Destination knowledge rules

#### 5.1 Destination knowledge levels

Every destination known to the player is in exactly one of the following knowledge levels:

- `unknown`
- `local_visible`
- `visited`

Destinations not present in the knowledge model are treated as `unknown`.

#### 5.2 Destination visibility fields

For destinations, the following fields are governed by knowledge level:

- **type/primary**: Destination type and primary emoji (e.g., planet/station).
- **name**: Display name of the destination.
- **population/tier**: Destination population or tier marker.
- **economies**: Primary and secondary economies associated with the destination.
- **situations**: Destination-scope situations currently active (live-only).

#### 5.3 Destination visibility matrix

The table below defines what is visible at each destination knowledge level:

| Level           | Appears in in-system lists / menus? | Type/Primary | Name | Population/Tier | Economies        | Situations (dest-scope)                                    |
|-----------------|--------------------------------------|--------------|------|------------------|------------------|------------------------------------------------------------|
| `unknown`       | No (unless revealed by special mechanics) | No           | No   | No               | No               | No                                                         |
| `local_visible` | Yes, but only while in the same system | Yes          | Yes  | Yes              | Yes              | Yes, but **only** while currently at this destination      |
| `visited`       | Yes (globally, outside the system too) | Yes          | Yes  | Yes (snapshot)   | Yes (snapshot)   | Yes, but **only** while currently at this destination (live-only) |

Notes:

- **Local visibility only**:
  - When the player enters a system, all its destinations become `local_visible` for as long as the player is in that system.
  - `local_visible` grants full destination emoji profile (type/name/population/economies) for **current observability**, but this does not, on its own, promote the destination to fully visited/persistent knowledge.
- **Visited destinations**:
  - When the player enters a destination, its knowledge level becomes `visited`.
  - At `visited`, stable destination-level facts become stored knowledge and remain visible later from other systems (e.g., in mission logs, summaries, or UI panels).
- **Situations**:
  - Destination-scope situations are **only** visible in views for the current destination.
  - They are never persisted as part of stored knowledge under this contract.

---

### 6. Live-only information rules

#### 6.1 System-scope situations

- System-scope situations are visible only when the player is currently in that system.
- They must be queried from the authoritative world state each time.
- They are not stored as persistent knowledge and do not appear in snapshots or long-term summaries by default.

#### 6.2 Destination-scope situations

- Destination-scope situations are visible only when the player is currently at that destination.
- They must be queried from authoritative world state each time.
- They are not stored in persistent destination knowledge and do not appear in global views unless the view explicitly represents current context.

#### 6.3 Observability vs knowledge for situations

- Situations are **pure current observability**.
- Under this contract, they are not upgraded to stored knowledge unless explicitly added by a future extension to this specification.

---

### 7. Snapshot / refresh rules

#### 7.1 System snapshots

- When a system is **detected**:
  - The system is added to the knowledge model at level `detected`.
  - Snapshot may record minimal stable fields (e.g., identifier, basic name/type).

- When a system is **scanned locally** (within jump range or via authoritative scan):
  - The system’s knowledge level is upgraded to at least `scanned_local`.
  - Government information becomes visible (current observability) and may be recorded as stored knowledge.

- When a system is **visited**:
  - The system’s knowledge level is upgraded to `visited`.
  - Stable facts are snapshotted as stored knowledge:
    - Name.
    - Primary emoji/type.
    - Government.
    - Population/tier.
    - `last_seen_turn` or equivalent.

#### 7.2 Destination snapshots

- When the player **enters a system**:
  - All destinations in that system become locally visible (`local_visible`) as current observability.
  - While in that system, full destination emoji profiles (type/name/population/economies) may be visible.
  - This **does not** promote destinations to `visited` and **does not, by itself, constitute persistent visited knowledge**.

- When a destination is **visited** (player enters the destination itself):
  - The destination’s knowledge level is upgraded to `visited`.
  - Stable facts are snapshotted as stored knowledge:
    - Name.
    - Destination type.
    - Population/tier.
    - Primary economy.
    - Secondary economies.
    - `last_seen_turn` or equivalent.

#### 7.3 Stale knowledge rule

- Stored knowledge for systems and destinations **does not auto-refresh** when the world changes.
- If world-state system or destination facts change (e.g., government, population, economies):
  - The player continues to see **last-known** values drawn from snapshots.
  - These values are considered **stale knowledge** until explicitly refreshed.
- **Revisiting**:
  - Revisiting a system or destination (entering it again) is the canonical way to refresh stored knowledge snapshots.
  - On revisit, snapshots are updated to reflect current world-state facts as of that visit.

---

### 8. Authoritative source rules

#### 8.1 Travel range and jump distance

- The determination of which systems are “within jump range” must reuse the **authoritative travel reachability logic** already used for actual player travel.
- This logic is based on:
  - The active ship’s capabilities.
  - Current fuel and fuel-limited reach.
  - Existing pathfinding/range calculations used by the engine for travel.
- The fog-of-war / knowledge system:
  - **Must not** implement a separate or duplicate travel-range calculation.
  - **Must defer** to the existing authoritative reachability component when deciding which systems qualify as “in range” for `scanned_local` upgrades and in-range observability.

#### 8.2 World state as truth

- All live information (situations, current government, current population/economies) comes from the authoritative world state components (e.g., world generator, world state engine, time engine).
- Knowledge snapshots do not supersede world state; they represent the player’s last-known view of that state.

---

### 9. Current-phase assumptions

For the current phase of the project, the following assumptions apply:

- **All systems are detected at game start.**
  - At the start of a new game, every system is at least at the `detected` knowledge level.
  - The `unknown` system state remains defined for future hidden/secret systems but is **not** used for normal systems in this phase.

- **Range and reachability use existing travel logic.**
  - Any “in jump range” determination for fog-of-war must use the same logic currently used to compute reachable systems for the active ship based on fuel and capabilities.

These assumptions may be relaxed or extended in future phases, but implementers must respect them for the current project scope.

---

### 10. Future extensibility

The contract is designed to support:

- **Hidden systems and secret destinations**
  - Use `unknown` for systems/destinations that exist in world state but are not yet discoverable.
  - Introduce discovery flows that promote:
    - Systems: `unknown → detected → scanned_local → visited`.
    - Destinations: `unknown → local_visible → visited`.

- **Advanced intel and scanning mechanics**
  - Additional actions (intel reports, probes, quests) can promote knowledge levels or update snapshots without requiring a physical visit.
  - Such mechanics must:
    - Use the same knowledge levels and fields defined here.
    - Clearly distinguish between current observability (one-time report) and stored knowledge (what remains after the report).

- **Extended fields**
  - New fields (e.g., system tags, threat levels, law level, structural flags) can be added to snapshots and views if they follow the same:
    - Level-gated visibility.
    - Snapshot vs live data separation.
    - Staleness and refresh rules.

---

### 11. Integration expectations

All systems that expose system/destination information to the player must:

- Query a **central knowledge handler** for:
  - System and destination knowledge levels.
  - System and destination views (what to show).
- Respect this contract when:
  - Deciding whether to show emoji profiles vs plain names.
  - Deciding which fields (government, population, economies) are visible in each context.
  - Treating situations as live-only observability.

Engine components responsible for:

- Travel,
- World state,
- Time progression,

must:

- Notify the knowledge handler when knowledge-relevant events occur, including:
  - System detected or scanned (e.g., when in range).
  - System visited (arrival).
  - Destination locally visible (in-system listing).
  - Destination visited (arrival).

Frontends (CLI, UI, prose) must:

- Not bypass the knowledge handler by peeking at raw world state for player-facing views.
- Use the provided views/levels to render appropriate fog-of-war–aware information.

---

### 12. Non-goals / exclusions

This contract explicitly does **not** cover:

- The visual or textual style of how information is displayed (e.g., exact emoji, layout, narrative phrasing).
- Non-location knowledge such as:
  - NPC memory,
  - mission history (beyond their references to systems/destinations),
  - economic forecast or price histories.
- Internal debugging and developer-only tools that intentionally bypass fog-of-war (unless they are intended to represent player-facing information).
- Save/load formats beyond requiring that:
  - Stored knowledge (snapshots) is persisted and restored consistently.
  - Current observability is recalculated from world state and location after load.

All such topics may be defined in separate contracts or design documents and must not contradict this fog-of-war and knowledge-state contract.

