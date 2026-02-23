EmojiSpace — Vision (Living Design Document)
High-level premise

EmojiSpace is a procedurally generated, turn-based sci-fi sandbox where an entire sector of space is simulated using a symbolic, emoji-driven visual language. Systems, planets, NPCs, goods, threats, and opportunities are all represented through compact, readable icons that allow complex situations to be understood at a glance.

Each playthrough generates a new sector with its own geography, politics, economies, and conflicts. The world evolves continuously over time, whether or not the player intervenes. Players are not placed on a fixed narrative path; instead, stories emerge naturally from the interaction of systems, NPCs, and player choices.

EmojiSpace prioritizes systems over scripts, cause-and-effect over spectacle, and emergent narrative over authored plotlines.

Core design pillars
Symbolic clarity

Emoji act as a formal visual vocabulary, not decoration.

The player should be able to infer:

danger

legality

opportunity

faction alignment
with minimal text.

When something happens, the player should be able to reasonably answer “why did this occur?”

Systemic depth through simple rules

Complex behavior must arise from small, composable systems.

No mechanic should exist in isolation; economy, politics, NPC behavior, and situations must interact.

The game should feel deep because systems collide, not because rules are dense.

Player-defined identity

There are no fixed classes.

The player’s role (merchant, pirate, miner, bounty hunter, protector, etc.) emerges from:

actions taken

reputations earned

relationships formed

Hybrid identities are expected and encouraged.

A living sector

The sector is persistent for the duration of a run.

The galaxy evolves over time. Events are not static, and opportunities may arise, escalate, or disappear based on the passage of time and player action or inaction. Time in EmojiSpace is discrete and systemic rather than real-time, serving as a foundation for world state changes, consequences, and long-term outcomes.

Missions in EmojiSpace are not scripted quests, but emergent contracts formed from context, relationships, and circumstance. Their meaning comes not from predefined narratives, but from outcomes, consequences, and how they intersect with the wider state of the galaxy.

DataNet represents the underlying information and service infrastructure of the galaxy. It provides access to news, messages, and rare system-level opportunities, but does not replace physical presence, ships, or local interactions. DataNet informs and enables; it does not trivialize distance, risk, or consequence.

Systems experience:

economic shifts

political changes

crises (war, plague, famine, unrest)

Situations resolve over time even if the player ignores them.

The player is influential, not central.

Emergent narrative over scripted story

There is no single “main quest.”

Storylines are optional, procedural, and situational.

NPCs remember past interactions and act accordingly.

Failure, loss, and unintended consequences are valid narrative outcomes.

What the game explicitly is NOT

Not a twitch or real-time action game
All gameplay is turn-based and decision-focused.

Not a heavily scripted narrative RPG
There are no long dialogue trees or fixed campaign arcs as a core requirement.

Not a realism-focused simulation
Accuracy is sacrificed in favor of clarity, legibility, and interesting outcomes.

Not a pure roguelike puzzle game
While replayable and procedural, the game is not about solving fixed challenges.

Not a content treadmill
Replayability comes from systemic variation, not from large quantities of handcrafted content.

Intended player experience

Players should feel:

Informed but uncertain
The world provides readable signals, but never perfect information.

Consequential
Actions matter, often in delayed or indirect ways.

Adaptive
Plans must change as systems react and situations evolve.

Curious
The player is encouraged to explore, observe, and experiment.

Accountable
Mistakes, betrayals, and failures persist and shape future opportunities.

The core loop is:

observe the sector → identify opportunity or risk → act → systems react → adapt or suffer consequences

World structure

The game world is a procedurally generated sector-scale map composed of systems and destinations.

**World Generation (Locked):**
- Default galaxy size: 50 systems (configurable for production)
- Galaxy radius scales deterministically: R = 10.0 * sqrt(system_count)
- Unique spatial coordinates enforced for all systems
- Deterministic starlane graph (MST + k-NN) connects systems
- At least one destination per system matches system population
- Remaining destinations use uniform population distribution
- Primary and secondary economies assigned per destination
- Market blending and situation modifiers functioning correctly

Each system is defined by:

government type

population level (1-5)

spatial coordinates (x, y)

starlane connections (neighbors)

Each destination within a system is defined by:

destination type (planet, station, explorable_stub, mining_stub)

population (0-5, must be <= system population)

primary economy

secondary economies (0-3 based on population)

current situations (system-scoped or destination-scoped)

These factors directly affect:

prices and availability of goods

NPC behavior and professions present

legality of player actions

contracts and story triggers

location availability

Scope boundaries for a first playable version

The first playable version must demonstrate the core simulation loop, not feature completeness.

It must include:

A procedurally generated sector map

A basic but functional economy (supply, demand, scarcity)

At least one government type with distinct legal behavior

At least one dynamic situation (e.g., war or plague)

Persistent NPCs with memory and opinion of the player

Multiple viable playstyles (e.g., trade-focused vs. conflict-focused)

Clear success and failure states defined by player choice, not a fixed win screen

The first playable version explicitly excludes:

Graphical polish beyond symbolic UI

Large numbers of factions or biomes

Deep crafting or base-building systems

Multiplayer or networking

Monetization systems

Long-form authored narrative campaigns

Living document notes

This document defines intent and identity, not implementation.

Any proposed feature must clearly support at least one design pillar.

If complexity increases without improving systemic interaction, it should be reconsidered.

This document should be updated intentionally as understanding improves; drift without revision is a failure.