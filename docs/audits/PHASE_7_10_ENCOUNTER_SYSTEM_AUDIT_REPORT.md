# Phase 7.10 Encounter System Deep Audit Report

**Scope:** Architecture and execution audit of the encounter system. No code was modified.

**Goal:** Identify where encounter execution diverges from design intent and why encounters produce incorrect or missing outcomes.

---

## 1) Encounter Pipeline Diagram

### Design intent (from audit spec)

- **NPC encounters:** Neutral / Authority / Hostile → outcomes: trading, inspection, combat, pursuit, intimidation, ignore.
- **Non-NPC encounters:** Exploration (derelict/abandoned), Mining (asteroids/comets), Anomaly (rifts/wormholes).
- Each category should have its own resolver; NPCs through an NPC interaction system, environmental through exploration/mining/anomaly resolvers.

### Actual pipeline (code flow)

```
generate encounter
  └─ encounter_generator.generate_travel_encounters() / generate_encounter()
       └─ EncounterSpec (subtype_id, posture, initiative, encounter_category, reward_profile_id, …)

player decision
  └─ GameEngine.execute() → _handle_encounter_decision() or travel loop with encounter_action
       └─ interaction_layer.dispatch_player_action(spec, player_action, …)
            └─ next_handler: end | reaction | combat | pursuit_stub | law_stub | exploration_stub

resolver selection (single router in game_engine)
  └─ GameEngine._resolve_encounter(context, spec, player_action)
       ├─ handler == HANDLER_REACTION     → get_npc_outcome() → resolver "reaction"
       ├─ handler == HANDLER_PURSUIT_STUB → resolve_pursuit()  → resolver "pursuit"
       ├─ handler == HANDLER_COMBAT / HANDLER_COMBAT_STUB
       │    ├─ HANDLER_COMBAT → _initialize_combat_session() → hard_stop, resolver "combat" status "combat_started"
       │    └─ HANDLER_COMBAT_STUB → _resolve_encounter_combat() → resolver "combat" (one-shot)
       ├─ handler == HANDLER_LAW_STUB    → _run_law_checkpoint() → resolver "law"
       └─ handler == HANDLER_EXPLORATION_STUB → _resolve_exploration_encounter() → resolver "exploration" or "none"

outcome generation
  └─ Same _resolve_encounter() continues:
       └─ _reward_qualifies() → if not qualifies, return resolver_outcome (no reward)
       └─ If resolver == "combat", return (rewards handled post-combat)
       └─ materialize_reward(spec, system_markets, world_seed)
       └─ apply_materialized_reward(player, reward_payload, …)
       └─ return resolver_outcome

StepResult creation
  └─ GameEngine._build_step_result(context, ok, error)
       └─ result["events"] = list(context.events)
       └─ result["hard_stop"] = context.hard_stop
       └─ result["hard_stop_reason"] = context.hard_stop_reason
       └─ If hard_stop and pending_combat_action: result["pending_combat"] = { … }
       └─ (result["pending_encounter"] is never set)
```

**Where this occurs in code:**

| Phase                 | Location |
|-----------------------|----------|
| Generate encounter    | `encounter_generator.generate_encounter` / `generate_travel_encounters` |
| Player decision       | `interaction_layer.dispatch_player_action`; entry via `game_engine._handle_encounter_decision` or travel with `encounter_action` |
| Resolver selection    | `game_engine._resolve_encounter` (lines ~4081–4172): single if/elif chain on `dispatch.next_handler` |
| Outcome generation    | Same method: `_reward_qualifies`, `materialize_reward`, `apply_materialized_reward` (non-combat) |
| StepResult creation   | `game_engine._build_step_result` (lines ~5901–5968) |

---

## 2) Encounter Type Dispatch

### Branching: NPC vs non-NPC

- **Initial actions** are branched by `encounter_category` in `interaction_layer.allowed_actions_initial()`:
  - `encounter_category.startswith("environmental_")` → `[ACTION_INVESTIGATE, ACTION_IGNORE]`
  - Else NPC (by initiative) → `[ACTION_IGNORE, ACTION_RESPOND, ACTION_ATTACK]` or `[ACTION_IGNORE, ACTION_HAIL, ACTION_ATTACK]`
- **Resolver** is chosen only by **handler** (reaction / pursuit / combat / law / exploration_stub). Handler comes from:
  - Direct action (e.g. attack → combat, flee → pursuit_stub, comply/bribe → law_stub, investigate → exploration_stub), or
  - NPC outcome from `get_npc_outcome()` (e.g. hail/warn → reaction, attack → combat, pursue → pursuit_stub).

So:

- **NPC encounters** (no `environmental_*`): first choice is ignore/respond/attack (or hail/attack). Then either a direct resolver (combat, pursuit, law) or reaction → then possible second step (e.g. combat after reaction). Correct.
- **Environmental encounters** (`environmental_*`): only investigate/ignore. Investigate → `HANDLER_EXPLORATION_STUB` → `_resolve_exploration_encounter()`. So environmental subtypes are forced through the **same** exploration handler; branching inside that method is by **subtype_id**, not by a separate “exploration vs mining vs anomaly” pipeline.

### Where the system merges types

- All encounters go through **one** `_resolve_encounter()` and one if/elif chain on `handler`. There is no separate “NPC interaction system” vs “environmental resolver” entry point; the only split is:
  - `encounter_category.startswith("environmental_")` affects **allowed actions** (investigate/ignore only),
  - then **handler** (exploration_stub vs reaction/combat/etc.) drives the single resolver chain.

So: **branching is by handler, not by a dedicated NPC vs environmental pipeline.** Design says “NPC encounters flow through NPC interaction system” and “environmental through exploration/mining/anomaly resolvers” — in code, both are served by the same `_resolve_encounter()` router; the only real split is exploration_stub vs the rest.

---

## 3) Resolver Mapping Table

| Encounter category / subtype (examples) | Resolver used | Implemented? | Returns valid StepResult? | Notes |
|----------------------------------------|---------------|--------------|----------------------------|--------|
| **NPC – neutral** (e.g. civilian_trader_ship) | reaction / end / combat / pursuit / law | Yes | Yes | reaction_engine.get_npc_outcome; law for comply/bribe (authority). |
| **NPC – authority** (customs_patrol, bounty_hunter) | reaction / combat / pursuit / law | Yes | Yes | Same pipeline. |
| **NPC – hostile** (pirate_raider, blood_raider) | reaction / combat / pursuit | Yes | Yes | Same pipeline. |
| **Environmental – mining** (asteroid_field, comet_passage, debris_storm) | exploration (outcome "mined" or mining_blocked) | Yes | Yes | _resolve_exploration_encounter branches on subtype_id; mining path uses mining_resolver and sets spec.sku_id/quantity. |
| **Environmental – anomaly** (spatial_rift, ancient_beacon, quantum_echo, wormhole_anomaly) | exploration (outcome success/fail, wormhole_reveal/fail) | Yes | Yes | Probe-based success; wormhole has extra path. |
| **Environmental – opportunity (derelict/distress)** (derelict_ship, derelict_station, distress_call) | exploration_stub → **"none"** | **No** | **No outcome** | subtype_id not in `environmental_mining_subtypes` and not in `anomaly_subtypes`; code does `if subtype_id not in anomaly_subtypes: return {"resolver": "none", "outcome": None}`. So **no dedicated resolver**; no outcome, no reward. |
| **Environmental – hazard (ion_storm)** | exploration_stub → **"none"** | **No** | **No outcome** | ion_storm not in mining or anomaly sets; falls through to "none". |

**Missing resolver implementations:**

- **derelict_ship, derelict_station, distress_call** (`environmental_opportunity`): Investigate goes to exploration_stub but returns `resolver "none"`, outcome `None` — no exploration or salvage outcome.
- **ion_storm** (`environmental_hazard`): Same; no hazard/exploration outcome.

---

## 4) Event Contamination Root Cause

### Mechanism

- **context.events** is a single list per `execute()` and is **never cleared** between encounters inside that call.
- When multiple encounters are resolved in **one** command (e.g. travel with explicit `encounter_action`):
  - `_pending_travel["events_so_far"]` is initialized from `context.events` (e.g. around 965, 2996, 3938).
  - After each encounter: `events_so_far = self._pending_travel.get("events_so_far", []); events_so_far.extend(context.events); context.events = list(events_so_far); self._pending_travel["events_so_far"] = list(events_so_far)` (991–994, 3938–3941).
  - So **context.events** is the cumulative list of all events since the start of the command.
- **StepResult** is built from this same list: `result["events"] = list(context.events)` in `_build_step_result` (5910).

So:

- **Root cause:** Events are **accumulated in one list per command**. There is no per-encounter event list; the step result’s `events` array is the full history for that `execute()`.
- **Effect:** When several encounters are processed in one call (batch resolution with `encounter_action`), “events from earlier encounters” appear in the same result as later ones because the result is the entire batch. Any consumer that assumes `result.events` is “events for the current encounter only” will see contamination.
- **events_so_far** is used only to **merge** travel events with the current context and to **persist** them on `_pending_travel`; it does not partition events by encounter.

---

## 5) Combat Trigger Path / “Combat begins” but no combat

### Flow

1. Player chooses attack (or NPC outcome is attack) → `dispatch_player_action` returns `HANDLER_COMBAT`.
2. `_resolve_encounter()` calls `_initialize_combat_session(spec, context)` and sets `context.hard_stop = True`, `context.hard_stop_reason = "pending_combat_action"`, and `resolver_outcome = {"resolver": "combat", "status": "combat_started"}`.
3. An event is emitted with stage `"combat"`, subsystem `"combat_initialization"` (e.g. “combat begins”).
4. **Reward path is skipped** for resolver `"combat"` (early return around 4202–4214), so no immediate reward; combat rewards are deferred to post-combat.
5. Combat **actually** runs only when the client sends a **combat_action** command; the engine then runs `_process_combat_round()` and eventually clears `_pending_combat` and may call `_apply_post_combat_rewards_and_salvage`.

So “combat begins” is correct: it means the **session** has started and the engine is waiting for combat actions. If the client never sends `combat_action`, combat never runs. So:

- **Stale event text:** No — the event is accurate for “combat session started.”
- **Failed resolver dispatch:** No — dispatch to combat and initialization are correct.
- **Lost pending combat state:** Possible. If the client or another code path does not call `combat_action` (or clears/overwrites `_pending_combat`), the session can be lost. `_pending_combat` is only cleared in:
  - `_process_combat_round()` when combat ends (e.g. 5281, 5451),
  - max_rounds forced termination (5281),
  - and in `execute()` when parsing combat_action (5193) if `_pending_combat is None` (raises). So if the next command is not `combat_action`, pending combat remains until the client sends it; if the client sends something else and the engine doesn’t re-check pending combat for that command type, the player could see “combat began” but no way to act (depends on CLI/UI flow).

**Conclusion:** The main risk is **lost or unused pending combat state** (client not sending `combat_action`, or engine not being invoked again with combat_action). The resolver and “combat started” event are consistent with design.

---

## 6) Reward Pipeline and “Loot not in inventory”

### Non-combat (immediate) path

- **materialize_reward(spec, system_markets, world_seed)** (reward_materializer) → `RewardResult` (sku_id, quantity, credits, etc.).
- **apply_materialized_reward(player, reward_payload, …)** (reward_applicator) → credits applied immediately; cargo applied to `player.cargo_by_ship["active"]` (with optional capacity check).

Design: credits applied immediately; cargo can be gated by capacity. In the **non-combat** path in `_resolve_encounter()`, `enforce_capacity=False` is passed (4248), so cargo is always applied and should appear in inventory. So for non-combat encounters, “loot not in inventory” is unlikely unless reward_profile is missing, materialize returns None, or applicator skips (e.g. no sku_id/quantity).

### Combat (deferred) path

- On victory/destroy or enemy surrender, `_apply_post_combat_rewards_and_salvage()`:
  - Uses `materialize_reward(spec, …)` and builds a **loot_bundle** (credits, cargo_sku, cargo_quantity, salvage_modules, etc.).
  - Sets **`self._pending_loot = loot_bundle`** and **`context.hard_stop = True`**, **`context.hard_stop_reason = "pending_loot_decision"`**.
  - Does **not** apply to player yet; design is “player must accept via prompt.”
- Application happens only when the client calls **`resolve_pending_loot(take_all=True/False)`**, which uses `_apply_loot_bundle(..., accepted_items)`.

So:

- **Credits:** Applied only when the player accepts loot (resolve_pending_loot with accepted_items including credits). So “credits applied immediately” is **not** true for combat — they are deferred until loot resolution.
- **Cargo:** Same — requires acceptance; if the client never calls `resolve_pending_loot` or the player declines cargo, it never appears in inventory.
- **Root cause for “generated loot sometimes does not appear”:** Loot is **intentionally** deferred; it appears only after `resolve_pending_loot` with the relevant `accepted_items`. If the CLI/UI skips the loot prompt, or doesn’t call `resolve_pending_loot`, or passes accepted_items that omit cargo/salvage, that loot will not appear. Also, if `_pending_loot` is overwritten by a second combat before the first is resolved, the first loot bundle is lost.

---

## 7) Salvage Modules Handling

### Design requirement

- Salvaged modules should **occupy cargo space the same as goods**.

### Current behavior

- **salvage_resolver.resolve_salvage_modules()** returns a list of module instance dicts (from destroyed ship); it does not touch player state.
- **Post-combat:** Salvage is attached to the **loot_bundle** as `salvage_modules` and stored in **`_pending_loot`**; player is prompted to accept.
- **On accept** (`_apply_loot_bundle` with `accepted_items["salvage_modules"]`):
  - Code checks **physical cargo capacity** (5775–5790): `current_physical_usage + module_count` vs `physical_capacity`.
  - If over capacity → `salvage_capacity_exceeded` error; modules are **not** applied.
  - If under capacity → modules are appended to **`player_state.salvage_modules`** (5791–5814), **not** to `cargo_by_ship`. Comment in code: “Each module consumes 1 physical cargo unit when stored as cargo” and “For now, store in salvage_modules list (player can install later via shipdock).”

So:

- **A) Becomes cargo:** No. Salvage is not added as cargo SKUs; it is stored in a separate **salvage_modules** list.
- **B) Becomes installed modules:** No. They go to `salvage_modules`; installation is a separate shipdock flow.
- **C) Discarded:** Only if the player declines or capacity is exceeded (then not applied).
- **D) Incorrectly handled:** Partially. Capacity is checked against **physical cargo** and counts each module as 1 unit, which is consistent with “occupy cargo space,” but the **storage** is `salvage_modules`, not cargo. So they **do** consume cargo space for the capacity check but **do not** appear as cargo in `cargo_by_ship`; design said “occupy cargo space the same as goods,” which could mean either “count against capacity” (done) or “appear as cargo” (not done).

**Summary:** Salvage is **capacity-checked** like cargo but **stored in a separate list** (`salvage_modules`), not as cargo. So behavior is “C) + D)” relative to the stated design.

---

## 8) Hard Stop Handling

### State and evaluation

- **pending_combat:** `self._pending_combat` (dict or None). Set in `_initialize_combat_session`; cleared when combat ends in `_process_combat_round` or on forced max_rounds.
- **pending_loot:** `self._pending_loot` (loot_bundle or None). Set in `_apply_post_combat_rewards_and_salvage`; cleared in `resolve_pending_loot()` after application.
- **pending_encounter:** No dedicated state name; “next encounter” is represented by `_pending_travel["current_encounter"]` and `_pending_travel["remaining_encounters"]`. `has_pending_encounter()` is true when `_pending_travel is not None and _pending_travel.get("current_encounter") is not None`.

**`_evaluate_hard_stop(context)`** (755–767):

- If `_pending_travel` has a current_encounter or remaining_encounters → `hard_stop = True`, `hard_stop_reason = "pending_encounter_decision"`.
- If `_pending_loot is not None` → `hard_stop = True`, `hard_stop_reason = "pending_loot_decision"`.
- If `_pending_combat is not None` → `hard_stop = True`, `hard_stop_reason = "pending_combat_action"`.

So the **order of checks** can override: e.g. if all three are set, the last one checked wins (pending_combat). In practice, combat sets pending_combat and clears current_encounter when combat starts; after combat, pending_loot may be set. So ordering is important and could cause one reason to hide another if multiple are set.

### Step result and CLI

- **`_build_step_result`** adds **`result["pending_combat"]`** when `hard_stop` and `hard_stop_reason == "pending_combat_action"` and `_pending_combat` is set (5928–5956).
- **`result["pending_encounter"]` is never set** by the engine. The CLI uses `engine.get_pending_encounter_info()` inside `_resolve_pending_encounter(engine)` when it explicitly handles pending encounters; in the generic hard_stop loop it does `pending_encounter = result.get("pending_encounter")`, which is always None, so that path can hit “No pending_encounter payload - break to avoid infinite loop” even when there is a pending encounter (state is in the engine, not in the result).

### Loss or overwrite of hard stop state

- **pending_combat:** Cleared only when combat ends or on error paths; could be lost if the engine is re-initialized or state is reset without sending combat_action.
- **pending_loot:** Set only in `_apply_post_combat_rewards_and_salvage`. If another combat finishes and calls the same function, **`self._pending_loot`** is overwritten; the previous loot bundle is lost.
- **pending_encounter:** Stored in `_pending_travel`; cleared when `remaining_encounters` is empty and there’s no hard_stop. Not overwritten by a single new encounter, but if a new travel is started while `_pending_travel` is still set, the guard in `_execute_travel_to_destination` (754–768) triggers a hard_stop and prevents stacking; so normally not lost unless travel state is cleared elsewhere.

**Summary:** Pending loot can be **overwritten** by a second combat before the first is resolved. Pending encounter is not written into the step result, which can confuse the CLI’s generic hard_stop handling.

---

## 9) Summary Tables

### Resolver mapping (concise)

| Handler              | Resolver name  | Used for                          | Implemented |
|----------------------|----------------|------------------------------------|--------------|
| HANDLER_REACTION     | reaction       | NPC outcome (hail, accept, etc.)   | Yes          |
| HANDLER_PURSUIT_STUB | pursuit        | Flee / pursue                      | Yes          |
| HANDLER_COMBAT       | combat         | Attack / NPC attack                | Yes          |
| HANDLER_LAW_STUB     | law            | Comply / bribe (authority)         | Yes          |
| HANDLER_EXPLORATION_STUB | exploration / none | Investigate (environmental)   | Partial      |
| (subtype mining)      | exploration    | asteroid_field, comet_passage, debris_storm | Yes |
| (subtype anomaly)     | exploration    | spatial_rift, ancient_beacon, quantum_echo, wormhole_anomaly | Yes |
| (subtype derelict/distress/ion_storm) | none   | derelict_ship, derelict_station, distress_call, ion_storm | No  |

### Architectural mismatches

| Design | Implementation |
|--------|-----------------|
| NPC encounters flow through “NPC interaction system”; environmental through “exploration/mining/anomaly resolvers.” | Single `_resolve_encounter()` router; branching only by handler (reaction/combat/pursuit/law/exploration_stub). No separate NPC vs environmental entry points. |
| Each encounter category has its own resolver logic. | One router; exploration_stub branches by subtype_id for mining vs anomaly; derelict/distress/ion_storm get no resolver (return "none"). |
| Salvaged modules occupy cargo space the same as goods. | Capacity is checked (1 unit per module) but modules are stored in `salvage_modules`, not in cargo. |
| Credits applied immediately; cargo requires player acceptance. | Non-combat: credits and cargo applied immediately (enforce_capacity=False). Combat: both credits and cargo deferred to loot prompt; nothing applied until resolve_pending_loot. |

---

## 10) Recommendations (for future fixes; no changes made in this audit)

1. **Resolver coverage:** Add explicit handling in `_resolve_exploration_encounter` for `derelict_ship`, `derelict_station`, `distress_call` (e.g. exploration/salvage outcome), and for `ion_storm` (e.g. hazard/data cache outcome), so they do not return `resolver "none"`.
2. **Events:** Either partition events per encounter (e.g. per-encounter event list and append only that slice to a “current encounter” result) or document that `result.events` is cumulative for the whole command and ensure CLI/UI only shows the relevant slice.
3. **Step result:** When `hard_stop_reason == "pending_encounter_decision"`, set `result["pending_encounter"]` from `get_pending_encounter_info()` so the CLI’s generic hard_stop loop can use it without relying solely on a separate engine call.
4. **Combat rewards:** Align with design: e.g. apply credits immediately on victory and keep only cargo/salvage for the loot prompt; or document that combat rewards are fully deferred.
5. **Salvage:** Either store accepted salvage as cargo (e.g. as a “module_crate” SKU or similar) so it appears in cargo and uses cargo space, or formally define `salvage_modules` as “not cargo but capacity-counted” and document it.
6. **Pending loot overwrite:** When building a new loot bundle after combat, merge or queue with existing `_pending_loot` instead of overwriting, or reject/complete the previous loot before starting the next combat.

---

*End of audit report. No code was modified.*

## Corrections applied (Phase 7.10 correction pass)

A subsequent correction pass (version 0.11.16) addressed the findings above. See **PHASE_7_10_ENCOUNTER_CORRECTION_SUMMARY.md** for root causes corrected, files changed, and behavior documentation (encounter branching, event isolation, combat reward split, salvage capacity).
