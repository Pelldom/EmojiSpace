Section 1: Mine Action Availability
File: src/game_engine.py
Function: _available_destination_actions(self) -> list[LocationActionModel]
Exact condition (high-level):
Mine is only offered as a destination action when:
There is a current destination.
The destination is not destroyed.
The normalized destination type is "resource_field".
The active ship has the mining capability (ship_has_capability(ship, CAPABILITY_UNLOCK_MINING)).
Concrete code path:
game_engine.py
Lines 6300-6330
def _available_destination_actions(self) -> list[LocationActionModel]:    destination = self._current_destination()    if destination is None:        return []    dest_type = normalize_destination_type(destination.destination_type, getattr(self, "logger", None))    if destination_has_tag(destination, "destroyed"):        dest_type = dest_type  # no explore/mine at destroyed    actions = [        LocationActionModel(            action_id="customs_inspection",            display_name="Customs Inspection",            description="Run a voluntary customs inspection at destination level.",        )    ]    if destination_has_datanet_service(destination):        actions.append(            LocationActionModel(                action_id="refuel",                ...            )        )    if not destination_has_tag(destination, "destroyed"):        ship = self._active_ship()        if ship and dest_type == "exploration_site" and ship_has_capability(ship, CAPABILITY_UNLOCK_PROBE):            actions.append(self._location_action_model("explore"))        if ship and dest_type == "resource_field" and ship_has_capability(ship, CAPABILITY_UNLOCK_MINING):            actions.append(self._location_action_model("mine"))    return sorted(actions, key=lambda entry: entry.action_id)
What data it inspects:
destination.destination_type (normalized via normalize_destination_type)
destination tags via destination_has_tag(destination, "destroyed")
Active ship, via self._active_ship()
Ship capabilities via ship_has_capability(ship, CAPABILITY_UNLOCK_MINING)
File: src/game_engine.py
Function: _location_action_model(self, action_id: str) -> LocationActionModel
Role: Defines the LocationActionModel entry for the Mine action once it has been deemed available.
game_engine.py
Lines 6484-6493
    ...    "mine": LocationActionModel(        action_id="mine",        display_name="Mine",        description="Mine resources. Consumes 1 day, 1 fuel.",        time_cost_days=1,        fuel_cost=1,    ),
File: src/game_engine.py
Function: _execute_destination_action(self, context, payload)
Exact condition:
When the player selects "mine" from the available actions, the engine dispatches directly to _execute_mine:
game_engine.py
Lines 2637-2644
    if action_id == "refuel":        self._execute_destination_refuel(context, kwargs)        return    if action_id == "explore":        self._execute_explore(context)        return    if action_id == "mine":        self._execute_mine(context)        return
File: src/game_engine.py
Function: _execute_mine(self, context: EngineContext) -> None
Exact preconditions (before resolver):
There is a current destination.
Destination is of normalized type "resource_field".
Destination does not have tag "destroyed".
Active ship has mining capability via ship_has_capability(active_ship, CAPABILITY_UNLOCK_MINING).
Active ship has at least 1 fuel.
game_engine.py
Lines 2712-2747
def _execute_mine(self, context: EngineContext) -> None:    """Phase 7.12: Mine at resource_field. 1 day, 1 fuel; then one local_activity encounter roll."""    destination = self._current_destination()    if destination is None:        raise ValueError("No current destination for mine.")    destination_id = destination.destination_id    ...    dest_type = normalize_destination_type(destination.destination_type, getattr(self, "logger", None))    if dest_type != "resource_field":        _mine_early_failure_increment("mine_only_at_resource_field")        raise ValueError("mine_only_at_resource_field")    if destination_has_tag(destination, "destroyed"):        _mine_early_failure_increment("destination_destroyed")        raise ValueError("destination_destroyed")    active_ship = self._active_ship()    if not ship_has_capability(active_ship, CAPABILITY_UNLOCK_MINING):        _mine_early_failure_increment("ship_needs_mining_capability")        raise ValueError("ship_needs_mining_capability")    if int(active_ship.current_fuel) < 1:        _mine_early_failure_increment("insufficient_fuel")        raise ValueError("insufficient_fuel")    # Advance time 1 day, then consume 1 fuel    self._advance_time(days=1, reason="mine")    active_ship.current_fuel = max(0, int(active_ship.current_fuel) - 1)    ...
What data it inspects (execution-time):
Destination type and tags (as above).
Active ship object (model ID, module instances, fuel).
self.config["mining_attempts_increment_on_failure"] (for attempt-index behavior, not for “unlock”).
Section 2: Capability Detection Logic
How mining capability is detected:
Mining capability is derived from installed modules via a ship capability helper, not checked directly by primary_tag at call-sites.
File: src/ship_assembler.py
Function: assemble_ship(hull_id, module_instances, degradation_state) (excerpt)
Primary_tag ? utility effect mapping (where mining is wired):
ship_assembler.py
Lines 268-311
    module_bonus = {"weapon": 0, "defense": 0, "engine": 0}    ship_utility_effects = {        "physical_cargo_bonus": 0,        "data_cargo_bonus": 0,        "interdiction_bonus": 0,        "smuggler_flag": False,        "unlock_mining": False,        "unlock_probe": False,    }    ...    for entry in resolved:        ...        if entry["primary_tag"] == "ship:utility_extra_cargo":            ship_utility_effects["physical_cargo_bonus"] += 5        elif entry["primary_tag"] == "ship:utility_data_array":            ship_utility_effects["data_cargo_bonus"] += 5        elif entry["primary_tag"] == "ship:utility_interdiction":            ship_utility_effects["interdiction_bonus"] += 1        elif entry["primary_tag"] == "ship:utility_smuggler_hold":            ship_utility_effects["smuggler_flag"] = True        elif entry["primary_tag"] == "ship:utility_mining_equipment":            ship_utility_effects["unlock_mining"] = True        elif entry["primary_tag"] == "ship:utility_probe_array":            ship_utility_effects["unlock_probe"] = True        elif entry["primary_tag"] == "ship:utility_extra_fuel":            fuel_bonus += 5
Result:
Any installed module whose primary_tag == "ship:utility_mining_equipment" sets ship_utility_effects["unlock_mining"] = True in the assembled ship state.
File: src/ship_assembler.py
Constants and helper:
ship_assembler.py
Lines 405-432
CAPABILITY_UNLOCK_PROBE = "capability_unlock_probe"CAPABILITY_UNLOCK_MINING = "capability_unlock_mining"def ship_has_capability(ship: Any, capability_id: str) -> bool:    """Return True if the ship has the given capability (Phase 7.12). Uses tag-based gating via ship_utility_effects."""    hull_id = getattr(ship, "model_id", None) or (ship.get("hull_id") if isinstance(ship, dict) else None)    module_instances = (        getattr(ship, "persistent_state", {}).get("module_instances", [])        if not isinstance(ship, dict)        else ship.get("module_instances", [])    )    ...    assembled = assemble_ship(hull_id, module_instances, degradation)    utility = assembled.get("ship_utility_effects") or {}    if capability_id == CAPABILITY_UNLOCK_PROBE:        return bool(utility.get("unlock_probe", False))    if capability_id == CAPABILITY_UNLOCK_MINING:        return bool(utility.get("unlock_mining", False))    return False
Where it is used for Mine availability / execution:
Availability (destination actions):
game_engine.py
Lines 6323-6328
    if not destination_has_tag(destination, "destroyed"):        ship = self._active_ship()        if ship and dest_type == "exploration_site" and ship_has_capability(ship, CAPABILITY_UNLOCK_PROBE):            actions.append(self._location_action_model("explore"))        if ship and dest_type == "resource_field" and ship_has_capability(ship, CAPABILITY_UNLOCK_MINING):            actions.append(self._location_action_model("mine"))
Execution-time guard in _execute_mine:
game_engine.py
Lines 2741-2744
    active_ship = self._active_ship()    if not ship_has_capability(active_ship, CAPABILITY_UNLOCK_MINING):        _mine_early_failure_increment("ship_needs_mining_capability")        raise ValueError("ship_needs_mining_capability")
Whether it uses module tags or derived flags:
Call sites (_available_destination_actions, _execute_mine) rely only on the derived capability flag (ship_has_capability(..., CAPABILITY_UNLOCK_MINING)).
The capability helper internally:
Calls assemble_ship, which interprets module primary_tag and secondary_tags.
Populates ship_utility_effects["unlock_mining"] from primary_tag == "ship:utility_mining_equipment".
So:
Direct checks at call sites are on capability IDs, not on primary_tag.
Primary tag is consumed only inside the ship assembly layer.
Confirming use of primary_tag "ship:utility_mining_equipment":
Module definition (data):
modules.json
Lines 871-888
      "module_id": "ship_utility_mining_equipment",      ...      "primary_tag": "ship:utility_mining_equipment",
Assembler mapping: as shown above (elif entry["primary_tag"] == "ship:utility_mining_equipment": ship_utility_effects["unlock_mining"] = True).
No other code reads "ship:utility_mining_equipment" directly outside the assembly/tag-audit layers.
Section 3: Encounter Integration
Does encounter system also check mining capability?
File: src/encounter_generator.py
No references to "mine", "mining", "mining_equipment", CAPABILITY_UNLOCK_MINING, or ship_has_capability.
Encounter generation deals with travel context, subtype selection, reward profiles, etc., but does not gate or invoke a Mine action.
File: src/interaction_layer.py
This file is focused on interaction handlers; there is no handler for a destination-level Mine action or any mining capability check here.
Combat / encounter-related files (src/combat_resolver.py, etc.):
primary_tag is used for probe array scan actions (ship:utility_probe_array) and various combat utilities, but not mining.
Conclusion for encounter integration:
The Mine action is not part of encounter resolution.
The encounter system does not check mining capability.
Local-activity encounters are triggered after a Mine/Explore action in game_engine._trigger_local_activity_encounter, but capability logic there is absent; capability gating happens only in _available_destination_actions and _execute_mine.
Section 4: Risks / Observations
Duplicated logic:
The unlock condition for mining capability is implemented centrally in:
ship_assembler.assemble_ship (mapping primary_tag to ship_utility_effects["unlock_mining"]).
ship_assembler.ship_has_capability (capability abstraction).
The use of mining capability is duplicated in two places (both using the same helper):
_available_destination_actions (to show/hide the Mine action).
_execute_mine (hard guard before performing the action).
This duplication is intentional and consistent:
UI/UX layer: availability.
Engine authority: execution-time guard.
Inconsistency or surprises:
Mine availability strictly depends on:
Destination type resource_field.
Ship capability derived from installed modules.
Destination not destroyed.
It does not depend on:
Any mission/encounter subtype.
Any direct module checks at the call site (all go through the capability helper).
primary_tag "ship:utility_mining_equipment" is only interpreted in the assembler; there is no inconsistent second path elsewhere.
Risk if standardized to primary_tag at call-sites:
Current design:
Keeps a single source of truth for interpreting module data (assemble_ship + ship_has_capability).
Allows future changes (e.g., multiple modules contributing to mining unlock, crew modifiers, hull traits) to be encapsulated without changing the engine call-sites.
If call-sites started checking primary_tag directly:
It would duplicate interpretation logic already present in assemble_ship.
Risk of capability state diverging from other systems that already rely on ship_utility_effects (e.g., cargo bonuses, probe capability).
As implemented, capability detection is centralized and consistent, with:
One tag ("ship:utility_mining_equipment") ? ship_utility_effects["unlock_mining"] ? ship_has_capability(..., CAPABILITY_UNLOCK_MINING) ? Mine action availability and execution.
In summary, the Mine action is unlocked only at destination level for resource_field destinations when the active ship has a derived mining capability flag, itself computed from installed modules with primary_tag == "ship:utility_mining_equipment". The encounter system does not interact with mining capability beyond the generic local_activity encounter triggered after the Mine action.