# Phase 7.10 Encounter System Correction Summary

**Version:** 0.11.16  
**Reference:** PHASE_7_10_ENCOUNTER_SYSTEM_AUDIT_REPORT.md, reaction_engine.py

## Root causes corrected

1. **Single generic resolver chain**  
   All encounters went through one if/elif chain. **Fix:** Branched by handler into NPC path (`_resolve_npc_encounter`) and environmental path (`_resolve_environmental_encounter`). Top-level `_resolve_encounter` dispatches by `HANDLER_EXPLORATION_STUB` vs rest; reward application is in `_resolve_encounter_rewards`.

2. **StepResult.events contamination**  
   Events from multiple encounters in one `execute()` were merged into one list and returned. **Fix:** Before each encounter resolution, `context.events` is cleared. After resolution, only this encounter’s events are appended to `events_so_far` for internal history; `context.events` is left as this step’s events so `_build_step_result` returns per-encounter events only.

3. **Missing environmental resolvers**  
   `derelict_ship`, `derelict_station`, `distress_call`, `ion_storm` fell through to `resolver "none"`. **Fix:** Added explicit branches in `_resolve_exploration_encounter`: environmental opportunity (derelict/distress) uses probe-based success roll and returns `exploration`/`success`|`fail`; ion_storm uses hazard + probe roll and returns `exploration`/`success`|`fail` with optional damage.

4. **Combat rewards fully deferred**  
   Credits and cargo were both in the loot bundle and required acceptance. **Fix:** In `_apply_post_combat_rewards_and_salvage`, credits are applied immediately to the player. Pending loot bundle contains only cargo and salvaged modules (credits set to 0). Loot prompt governs only optional physical loot.

5. **Pending encounter/loot not in StepResult**  
   Engine had pending encounter state but did not expose it in the result. **Fix:** When `hard_stop_reason == "pending_encounter_decision"`, `result["pending_encounter"]` is set from `get_pending_encounter_info()`. When `hard_stop_reason == "pending_loot_decision"`, `result["pending_loot"]` is set with encounter_id, credits (0), cargo_sku, cargo_quantity, salvage_count, stolen_applied.

6. **Pending loot overwrite**  
   A second combat could overwrite `_pending_loot` before the first was resolved. **Fix:** At the start of `_apply_post_combat_rewards_and_salvage`, if `_pending_loot` is already set, we skip creating a new bundle, log `loot_blocked`, and do not set hard_stop for loot. Combat is still resolved; the new loot is not offered until the previous one is resolved.

7. **Salvage storage and capacity**  
   Salvage was capacity-checked but stored in a separate list. **Fix:** Kept behavior that accepted salvage in `resolve_pending_loot` is stored as cargo (1 unit per module by `module_id`) so it occupies cargo space the same as goods. Documented in `salvage_resolver.py` and in-game comment.

8. **resolve_pending_loot context bug**  
   `_event(context, ...)` was called without a valid `context`. **Fix:** A temporary `EngineContext` (`_ctx`) is created inside `resolve_pending_loot` for logging. When `take_all=False`, we log `loot_declined` with `credits_already_applied=True` and only cargo/salvage declined.

## Encounter branching model

- **NPC encounters** (no `encounter_category` or not `environmental_*`):  
  Options from `interaction_layer` (posture-aware). Resolution via `_resolve_npc_encounter`: reaction (reaction_engine), pursuit, combat, law. Posture and response logic remain defined by `reaction_engine.py`.

- **Environmental encounters** (`encounter_category.startswith("environmental_")`):  
  Options: Ignore, Investigate. Resolution via `_resolve_environmental_encounter` → `_resolve_exploration_encounter`, which branches by subtype:
  - **Mining:** asteroid_field, comet_passage, debris_storm → mined / mining_blocked.
  - **Opportunity:** derelict_ship, derelict_station, distress_call → probe-based success/fail.
  - **Hazard:** ion_storm → probe-based success/fail + optional hazard damage.
  - **Anomaly:** spatial_rift, ancient_beacon, quantum_echo, wormhole_anomaly → probe/wormhole logic.

## Event isolation

- For each encounter resolution (whether from `encounter_decision` or from the travel batch loop), `context.events` is cleared before `_resolve_encounter`.
- After resolution, the current step’s events are appended to `_pending_travel["events_so_far"]` for internal/history use only.
- `context.events` is not replaced with the full history; it remains the events for this encounter only.
- `_build_step_result` uses `context.events`, so `result["events"]` contains only the current encounter step’s events.

## Combat reward split

- **Credits:** Applied immediately in `_apply_post_combat_rewards_and_salvage` when combat ends in victory (destroyed enemy or enemy surrender). Not part of the loot prompt.
- **Cargo and salvaged modules:** Placed in `_pending_loot`; player chooses accept/decline via `resolve_pending_loot`. Only optional physical loot is in the prompt; “loot declined” is logged only when the player actually declines (take_all=False).

## Salvage storage and capacity

- Salvaged modules **occupy physical cargo space** (1 unit per module).
- When the player accepts salvage in `resolve_pending_loot`, modules are stored in `cargo_by_ship["active"]` under `module_id` as the SKU, so capacity is enforced and downstream shipdock flows can consume from cargo.
- Design is documented in `salvage_resolver.py` and in the game_engine salvage-application comment.

## Files changed

- `src/game_engine.py`: Event isolation, pending_encounter/pending_loot in StepResult, combat credits immediate + pending loot only cargo/salvage, block pending loot overwrite, NPC vs environmental split, environmental subtypes (derelict/distress/ion_storm), resolve_pending_loot context fix and decline logging, logging (encounter_category, subtype_id, resolver, combat_started).
- `src/salvage_resolver.py`: Module docstring describing salvage-as-cargo and capacity.
- `VERSION`: 0.11.15 → 0.11.16.
- `docs/PHASE_7_10_ENCOUNTER_CORRECTION_SUMMARY.md`: This file.

## Tests

- New: `tests/test_game_engine_phase710.py` with focused tests for event isolation, pending_encounter payload, combat_started pending_combat, environmental resolver outcomes, combat credits immediate, pending loot not overwritten, salvage capacity.

## Commit message suggestion

```
Phase 7.10 encounter system correction (0.11.16)

- Branch NPC vs environmental resolution; add _resolve_npc_encounter,
  _resolve_environmental_encounter, _resolve_encounter_rewards.
- Isolate per-encounter events so StepResult.events has no cross-encounter
  contamination.
- Surface pending_encounter and pending_loot in StepResult for CLI/UI.
- Apply combat credits immediately; keep only cargo/salvage in pending loot.
- Block new pending loot until previous is resolved (no overwrite).
- Add resolvers for derelict_ship, derelict_station, distress_call, ion_storm.
- Fix resolve_pending_loot context bug; log loot_declined only when declined.
- Document salvage as cargo (1 unit per module); capacity enforced.
- Logging: encounter_category, subtype_id, resolver, combat_started.
```
