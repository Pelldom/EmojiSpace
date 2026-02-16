import hashlib
import json
import random
from dataclasses import dataclass, field, replace
from pathlib import Path
from typing import Any, Callable, ClassVar, Optional

from npc_entity import NPCPersistenceTier


@dataclass
class ActiveSituation:
    situation_id: str
    system_id: str
    scope: str  # "system" or "destination"
    target_id: Optional[str]
    remaining_days: int


@dataclass
class ActiveEvent:
    event_id: str
    event_family_id: Optional[str]
    system_id: str
    remaining_days: int
    trigger_day: int = 0


@dataclass
class ScheduledEvent:
    event_id: str
    system_id: str
    trigger_day: int
    insertion_index: int = -1


@dataclass
class ScheduledSituation:
    situation_id: str
    system_id: str
    trigger_day: int
    insertion_index: int = -1


@dataclass
class WorldStateEngine:
    _MODIFIER_CAPS: ClassVar[dict[tuple[str, str], tuple[int | None, int | None]]] = {
        ("goods", "price_bias_percent"): (-50, 40),
        ("goods", "demand_bias_percent"): (-50, 50),
        ("goods", "availability_delta"): (-3, 3),
        ("missions", "spawn_weight_delta"): (-100, 100),
        ("missions", "payout_bias_percent"): (-50, 50),
        ("ships", "availability_delta"): (-3, 3),
        ("ships", "price_bias_percent"): (-40, 40),
        ("modules", "availability_delta"): (-3, 3),
        ("modules", "price_bias_percent"): (-40, 40),
        ("crew", "hire_weight_delta"): (-100, 100),
        ("crew", "wage_bias_percent"): (-50, 50),
        ("travel", "travel_time_delta"): (-2, 2),
        ("travel", "risk_bias_delta"): (-2, 2),
        ("travel", "special_flag"): (0, 1),
    }

    active_situations: dict[str, list[ActiveSituation]] = field(default_factory=dict)
    active_events: dict[str, list[ActiveEvent]] = field(default_factory=dict)
    scheduled_events: list[ScheduledEvent] = field(default_factory=list)
    scheduled_situations: list[ScheduledSituation] = field(default_factory=list)
    situation_catalog: list[dict[str, Any]] = field(default_factory=list)
    event_catalog: list[dict[str, Any]] = field(default_factory=list)
    system_flags: dict[str, set[str]] = field(default_factory=dict)
    pending_structural_mutations: list[dict[str, Any]] = field(default_factory=list)
    active_modifiers_by_system: dict[str, list[dict[str, Any]]] = field(default_factory=dict)
    last_structural_mutation_day_by_system: dict[str, Optional[int]] = field(
        default_factory=dict
    )
    cooldown_until_day_by_system: dict[str, Optional[int]] = field(default_factory=dict)
    _sector_ref: Any = None
    _npc_registry_ref: Any = None
    _valid_government_ids: set[str] = field(default_factory=set)
    _situation_catalog_by_id: dict[str, dict[str, Any]] = field(default_factory=dict)
    _event_catalog_by_id: dict[str, dict[str, Any]] = field(default_factory=dict)
    _scheduled_insertion_counter: int = 0

    def register_system(self, system_id: str) -> None:
        if system_id not in self.active_situations:
            self.active_situations[system_id] = []
        if system_id not in self.active_events:
            self.active_events[system_id] = []
        if system_id not in self.system_flags:
            self.system_flags[system_id] = set()
        if system_id not in self.active_modifiers_by_system:
            self.active_modifiers_by_system[system_id] = []
        if system_id not in self.last_structural_mutation_day_by_system:
            self.last_structural_mutation_day_by_system[system_id] = None
        if system_id not in self.cooldown_until_day_by_system:
            self.cooldown_until_day_by_system[system_id] = None

    def configure_runtime_context(
        self,
        *,
        sector: Any = None,
        npc_registry: Any = None,
        government_ids: Optional[set[str]] = None,
    ) -> None:
        self._sector_ref = sector
        self._npc_registry_ref = npc_registry
        if government_ids is not None:
            self._valid_government_ids = set(government_ids)

    def get_active_situations(self, system_id: str) -> list[ActiveSituation]:
        self.register_system(system_id)
        return list(self.active_situations[system_id])

    def get_active_events(self, system_id: str) -> list[ActiveEvent]:
        self.register_system(system_id)
        return list(self.active_events[system_id])

    def add_situation(self, active_situation: ActiveSituation) -> None:
        self.register_system(active_situation.system_id)
        current = self.active_situations[active_situation.system_id]
        if len(current) >= 3:
            raise ValueError("Maximum 3 active situations per system exceeded.")
        current.append(active_situation)
        print(
            f"Situation added: {active_situation.situation_id} "
            f"system={active_situation.system_id} scope={active_situation.scope}"
        )
        self._add_situation_modifiers(active_situation)

    def add_event(self, active_event: ActiveEvent) -> None:
        self.register_system(active_event.system_id)
        self.active_events[active_event.system_id].append(active_event)
        print(
            f"Event added: {active_event.event_id} "
            f"system={active_event.system_id}"
        )

    def schedule_event(self, scheduled_event: ScheduledEvent) -> None:
        self.register_system(scheduled_event.system_id)
        if scheduled_event.insertion_index < 0:
            scheduled_event.insertion_index = self._scheduled_insertion_counter
            self._scheduled_insertion_counter += 1
        self.scheduled_events.append(scheduled_event)

    def schedule_situation(self, scheduled_situation: ScheduledSituation) -> None:
        self.register_system(scheduled_situation.system_id)
        if scheduled_situation.insertion_index < 0:
            scheduled_situation.insertion_index = self._scheduled_insertion_counter
            self._scheduled_insertion_counter += 1
        self.scheduled_situations.append(scheduled_situation)

    def load_situation_catalog(self, catalog_path: str | Path | None = None) -> None:
        path = Path(catalog_path) if catalog_path is not None else Path(__file__).resolve().parents[1] / "data" / "situations.json"
        with path.open("r", encoding="utf-8") as handle:
            payload = json.load(handle)

        entries = payload.get("situations", []) if isinstance(payload, dict) else payload
        loaded: list[dict[str, Any]] = []
        for entry in entries:
            if not isinstance(entry, dict):
                continue
            loaded.append(
                {
                    "situation_id": entry.get("situation_id"),
                    "severity_tier": entry.get("severity_tier"),
                    "spawn_weight": entry.get("spawn_weight", 1),
                    "random_allowed": bool(entry.get("random_allowed", False)),
                    "event_only": bool(entry.get("event_only", False)),
                    "recovery_only": bool(entry.get("recovery_only", False)),
                    "allowed_scope": entry.get("allowed_scope"),
                    "duration_days": entry.get("duration_days"),
                    "modifiers": entry.get("modifiers", []),
                }
            )
        self.situation_catalog = loaded
        self._situation_catalog_by_id = {
            str(item.get("situation_id")): item
            for item in loaded
            if item.get("situation_id")
        }

    def load_event_catalog(self, catalog_path: str | Path | None = None) -> None:
        path = Path(catalog_path) if catalog_path is not None else Path(__file__).resolve().parents[1] / "data" / "events.json"
        with path.open("r", encoding="utf-8") as handle:
            payload = json.load(handle)

        entries = payload.get("events", []) if isinstance(payload, dict) else payload
        loaded: list[dict[str, Any]] = []
        for entry in entries:
            if not isinstance(entry, dict):
                continue
            loaded.append(dict(entry))
        self.event_catalog = loaded
        self._event_catalog_by_id = {
            str(item.get("event_id")): item
            for item in loaded
            if item.get("event_id")
        }
        if not self._valid_government_ids:
            self._valid_government_ids = _load_valid_government_ids()

    def evaluate_spawn_gate(
        self,
        world_seed: int,
        current_system_id: str,
        neighbor_system_ids: list[str],
        current_day: int,
        event_frequency_percent: int,
    ) -> None:
        # Evaluate only R=0,1 systems: current + direct neighbors provided by caller.
        eligible_systems: list[str] = []
        seen: set[str] = set()
        for system_id in [current_system_id, *neighbor_system_ids]:
            if system_id in seen:
                continue
            seen.add(system_id)
            eligible_systems.append(system_id)
        for system_id in sorted(eligible_systems):
            self.register_system(system_id)

        cooldown_until = self.cooldown_until_day_by_system.get(current_system_id)
        if cooldown_until is not None and current_day <= cooldown_until:
            print(
                "Spawn gate cooldown check: "
                f"system_id={current_system_id} current_day={current_day} "
                f"cooldown_until={cooldown_until} skipped=true reason=cooldown_active"
            )
            return
        print(
            "Spawn gate cooldown check: "
            f"system_id={current_system_id} current_day={current_day} "
            f"cooldown_until={cooldown_until} skipped=false reason=cooldown_clear"
        )

        spawn_probability = max(0.0, min(1.0, float(event_frequency_percent) / 100.0))
        spawn_gate_roll = _rng_u01(
            _deterministic_seed_with_parts(
                world_seed,
                current_system_id,
                current_day,
                "spawn_gate",
            )
        )
        if spawn_gate_roll >= spawn_probability:
            print(
                "Spawn gate cooldown not set: "
                f"system_id={current_system_id} current_day={current_day} "
                f"cooldown_until={self.cooldown_until_day_by_system.get(current_system_id)} "
                f"reason=spawn_gate_roll_failed spawn_gate_roll={spawn_gate_roll}"
            )
            return

        spawn_type_roll = _rng_u01(
            _deterministic_seed_with_parts(
                world_seed,
                current_system_id,
                current_day,
                "spawn_type",
            )
        )
        selected_type = "situation" if spawn_type_roll < 0.70 else "event"
        severity_roll = _rng_u01(
            _deterministic_seed_with_parts(
                world_seed,
                current_system_id,
                current_day,
                "spawn_severity",
            )
        )
        selected_tier = _select_spawn_severity_tier(severity_roll)
        print(
            "Spawn gate type+tier selected: "
            f"system_id={current_system_id} current_day={current_day} "
            f"selected_type={selected_type} selected_tier={selected_tier} "
            f"spawn_type_roll={spawn_type_roll} severity_roll={severity_roll}"
        )

        generated_any = False
        if selected_type == "situation":
            situation_rng = random.Random(
                _deterministic_seed_with_parts(
                    world_seed,
                    current_system_id,
                    current_day,
                    "spawn_select",
                    "situation",
                    selected_tier,
                )
            )
            generated_any = bool(
                self._spawn_random_situation_for_tier(
                    current_system_id,
                    selected_tier,
                    situation_rng,
                )
            )
        else:
            event_rng = random.Random(
                _deterministic_seed_with_parts(
                    world_seed,
                    current_system_id,
                    current_day,
                    "spawn_select",
                    "event",
                    selected_tier,
                )
            )
            active_event = self._spawn_random_event_for_tier(
                current_system_id,
                selected_tier,
                event_rng,
                current_day,
            )
            if active_event is not None:
                generated_any = True
                applied = self.apply_event_effects(
                    world_seed=world_seed,
                    current_day=current_day,
                    target_system_id=current_system_id,
                    event_id=active_event.event_id,
                    rng=event_rng,
                )
                if not applied:
                    self._remove_active_event_instance(
                        system_id=current_system_id,
                        event_id=active_event.event_id,
                        trigger_day=current_day,
                    )

        if generated_any:
            cooldown_until = current_day + 5
            self.cooldown_until_day_by_system[current_system_id] = cooldown_until
            print(
                "Spawn gate cooldown set: "
                f"system_id={current_system_id} current_day={current_day} "
                f"cooldown_until={cooldown_until} generated_any=true reason=spawn_gate_generation"
            )
            return

        print(
            "Spawn gate cooldown not set: "
            f"system_id={current_system_id} current_day={current_day} "
            f"cooldown_until={self.cooldown_until_day_by_system.get(current_system_id)} "
            f"reason=no_generation_created selected_type={selected_type} "
            f"selected_tier={selected_tier} candidates_found=0"
        )

    def apply_event_effects(
        self,
        world_seed: int,
        current_day: int,
        target_system_id: str,
        event_id: str,
        rng: random.Random,
    ) -> bool:
        del world_seed  # Reserved for future deterministic channels.
        self.register_system(target_system_id)
        event_def = self._event_catalog_by_id.get(event_id)
        if event_def is None:
            raise ValueError(f"Event definition not found for event_id={event_id}")

        effects = event_def.get("effects", {})
        if not isinstance(effects, dict):
            effects = {}

        is_structural = _is_structural_event_effects(effects)
        print(
            "Structural detection: "
            f"origin_system_id={target_system_id} event_id={event_id} "
            f"current_day={current_day} is_structural={is_structural}"
        )
        if is_structural:
            last_day = self.last_structural_mutation_day_by_system.get(target_system_id)
            if (
                last_day is not None
                and isinstance(last_day, int)
                and (current_day - last_day) < 10
            ):
                deferred_day = last_day + 10
                if deferred_day <= current_day:
                    deferred_day = current_day + 1
                self.schedule_event(
                    ScheduledEvent(
                        event_id=event_id,
                        system_id=target_system_id,
                        trigger_day=deferred_day,
                    )
                )
                print(
                    "Structural rate-limiter defer: "
                    f"origin_system_id={target_system_id} event_id={event_id} "
                    f"original_day={current_day} deferred_day={deferred_day} "
                    f"last_structural_mutation_day={last_day}"
                )
                return False
            self.last_structural_mutation_day_by_system[target_system_id] = current_day
            print(
                "Structural rate-limiter allow: "
                f"origin_system_id={target_system_id} event_id={event_id} "
                f"current_day={current_day} "
                f"last_structural_mutation_day={current_day}"
            )

        created = effects.get("create_situations", [])
        if isinstance(created, list):
            for item in created:
                if len(self.active_situations[target_system_id]) >= 3:
                    break
                if not isinstance(item, dict):
                    continue
                situation_id = item.get("situation_id")
                if not isinstance(situation_id, str) or not situation_id:
                    continue
                situation_def = self._situation_catalog_by_id.get(situation_id)
                if situation_def is None:
                    raise ValueError(
                        f"Situation definition not found for situation_id={situation_id}"
                    )
                scope = item.get("scope_type")
                if scope not in {"system", "destination"}:
                    scope = str(situation_def.get("allowed_scope") or "system")
                remaining_days = _roll_duration_days(
                    situation_def.get("duration_days"), rng, default_days=3
                )
                self.add_situation(
                    ActiveSituation(
                        situation_id=situation_id,
                        system_id=target_system_id,
                        scope=scope,
                        target_id=None,
                        remaining_days=max(0, remaining_days),
                    )
                )

        flags_add = effects.get("system_flag_add", [])
        if isinstance(flags_add, list):
            for value in flags_add:
                if isinstance(value, str):
                    already_present = value in self.system_flags[target_system_id]
                    self.system_flags[target_system_id].add(value)
                    print(
                        "System flag add: "
                        f"system_id={target_system_id} event_id={event_id} "
                        f"flag={value} already_present={already_present}"
                    )

        flags_remove = effects.get("system_flag_remove", [])
        if isinstance(flags_remove, list):
            for value in flags_remove:
                if isinstance(value, str):
                    was_present = value in self.system_flags[target_system_id]
                    self.system_flags[target_system_id].discard(value)
                    print(
                        "System flag remove: "
                        f"system_id={target_system_id} event_id={event_id} "
                        f"flag={value} was_present={was_present}"
                    )

        npc_mutations = effects.get("npc_mutations", [])
        if isinstance(npc_mutations, list):
            self._apply_npc_mutations(
                target_system_id=target_system_id,
                event_id=event_id,
                npc_mutations=npc_mutations,
            )

        modifiers = effects.get("modifiers", [])
        if isinstance(modifiers, list):
            self._add_modifier_entries(
                system_id=target_system_id,
                source_type="event",
                source_id=event_id,
                modifiers=modifiers,
            )

        structural_payload: dict[str, Any] = {}
        destroy_destination_ids = effects.get("destroy_destination_ids")
        if isinstance(destroy_destination_ids, list) and destroy_destination_ids:
            structural_payload["destroy_destination_ids"] = list(destroy_destination_ids)
            self._apply_destroy_destination_tags(
                target_system_id=target_system_id,
                event_id=event_id,
                destroy_destination_ids=destroy_destination_ids,
            )

        population_delta = effects.get("population_delta")
        if isinstance(population_delta, int) and population_delta != 0:
            structural_payload["population_delta"] = int(population_delta)
            self._apply_population_delta(
                target_system_id=target_system_id,
                event_id=event_id,
                population_delta=int(population_delta),
            )

        government_change = effects.get("government_change")
        if government_change not in (None, "", []):
            structural_payload["government_change"] = government_change
            self._apply_government_change(
                target_system_id=target_system_id,
                event_id=event_id,
                government_change=government_change,
            )

        if structural_payload:
            self.pending_structural_mutations.append(
                {
                    "system_id": target_system_id,
                    "source_event_id": event_id,
                    "mutation_payload": structural_payload,
                    "day_applied": current_day,
                }
            )

        scheduled = effects.get("scheduled_events", [])
        if isinstance(scheduled, list):
            for item in scheduled:
                if not isinstance(item, dict):
                    continue
                scheduled_event_id = item.get("event_id")
                delay_days = item.get("delay_days")
                if not isinstance(scheduled_event_id, str) or not scheduled_event_id:
                    raise ValueError("Scheduled event entry missing event_id.")
                if not isinstance(delay_days, int) or delay_days < 1:
                    raise ValueError("Scheduled event delay_days must be an integer >= 1.")
                self.schedule_event(
                    ScheduledEvent(
                        event_id=scheduled_event_id,
                        system_id=target_system_id,
                        trigger_day=current_day + delay_days,
                    )
                )
        return True

    def process_scheduled_events(self, world_seed: int, current_day: int) -> int:
        due_situations: list[ScheduledSituation] = []
        pending_situations: list[ScheduledSituation] = []
        for row in self.scheduled_situations:
            if row.trigger_day == current_day:
                due_situations.append(row)
            else:
                pending_situations.append(row)

        situation_executed = 0
        due_situations_sorted = sorted(
            due_situations, key=lambda row: (row.system_id, row.insertion_index)
        )
        for row in due_situations_sorted:
            situation_def = self._situation_catalog_by_id.get(row.situation_id)
            if situation_def is None:
                print(
                    "Propagation schedule ignored: "
                    f"system_id={row.system_id} situation_id={row.situation_id} "
                    f"trigger_day={current_day} reason=unknown_situation_id"
                )
                continue
            rng = random.Random(
                _deterministic_seed_with_parts(
                    world_seed,
                    current_day,
                    "scheduled_situation",
                    row.system_id,
                    row.situation_id,
                    row.insertion_index,
                )
            )
            if self._create_propagated_situation(row.system_id, row.situation_id, rng):
                situation_executed += 1

        due: list[ScheduledEvent] = []
        pending: list[ScheduledEvent] = []
        for row in self.scheduled_events:
            if row.trigger_day == current_day:
                due.append(row)
            else:
                pending.append(row)

        executed = 0
        due_sorted = sorted(due, key=lambda row: (row.system_id, row.insertion_index))
        for row in due_sorted:
            event_def = self._event_catalog_by_id.get(row.event_id)
            if event_def is None:
                raise ValueError(f"Event definition not found for event_id={row.event_id}")
            rng = random.Random(
                _deterministic_seed_with_parts(
                    world_seed,
                    current_day,
                    "scheduled_event",
                    row.system_id,
                    row.event_id,
                    row.insertion_index,
                )
            )
            remaining_days = _roll_duration_days(event_def.get("duration_days"), rng, default_days=1)
            self.add_event(
                ActiveEvent(
                    event_id=row.event_id,
                    event_family_id=event_def.get("event_family_id"),
                    system_id=row.system_id,
                    remaining_days=max(0, remaining_days),
                    trigger_day=current_day,
                )
            )
            applied = self.apply_event_effects(
                world_seed=world_seed,
                current_day=current_day,
                target_system_id=row.system_id,
                event_id=row.event_id,
                rng=rng,
            )
            if applied:
                executed += 1
            else:
                self._remove_active_event_instance(
                    system_id=row.system_id,
                    event_id=row.event_id,
                    trigger_day=current_day,
                )

        self.scheduled_situations = pending_situations
        self.scheduled_events = pending
        return executed + situation_executed

    def process_propagation(
        self,
        world_seed: int,
        current_day: int,
        get_neighbors_fn: Callable[[str], list[str]],
    ) -> int:
        executed = 0
        for origin_system_id in sorted(self.active_events.keys()):
            rows_sorted = sorted(
                self.active_events[origin_system_id],
                key=lambda row: (
                    row.event_id,
                    int(getattr(row, "trigger_day", 0)),
                    row.remaining_days,
                ),
            )
            for row in rows_sorted:
                trigger_day = int(getattr(row, "trigger_day", 0))
                if trigger_day <= 0:
                    trigger_day = current_day
                if trigger_day != current_day:
                    continue
                event_id = row.event_id
                event_def = self._event_catalog_by_id.get(event_id)
                if event_def is None:
                    print(
                        "Propagation ignored: "
                        f"origin_system_id={origin_system_id} event_id={event_id} "
                        f"trigger_day={trigger_day} reason=unknown_event_id"
                    )
                    continue
                propagation = event_def.get("propagation", [])
                if not isinstance(propagation, list) or not propagation:
                    continue
                for propagation_index, entry in enumerate(propagation):
                    if not isinstance(entry, dict):
                        print(
                            "Propagation ignored: "
                            f"origin_system_id={origin_system_id} event_id={event_id} "
                            f"trigger_day={trigger_day} propagation_index={propagation_index} "
                            "reason=invalid_entry"
                        )
                        continue
                    situation_id = entry.get("situation_id")
                    if not isinstance(situation_id, str) or not situation_id:
                        print(
                            "Propagation ignored: "
                            f"origin_system_id={origin_system_id} event_id={event_id} "
                            f"trigger_day={trigger_day} propagation_index={propagation_index} "
                            "reason=missing_situation_id"
                        )
                        continue
                    if situation_id not in self._situation_catalog_by_id:
                        print(
                            "Propagation ignored: "
                            f"origin_system_id={origin_system_id} event_id={event_id} "
                            f"trigger_day={trigger_day} propagation_index={propagation_index} "
                            f"situation_id={situation_id} reason=unknown_situation_id"
                        )
                        continue

                    delay_days = _coerce_non_negative_int(entry.get("delay_days", 0), 0)
                    systems_affected = _coerce_non_negative_int(
                        entry.get("systems_affected", 1), 1
                    )
                    candidate_neighbors = sorted(
                        {
                            system_id
                            for system_id in get_neighbors_fn(origin_system_id)
                            if system_id != origin_system_id
                        }
                    )

                    select_seed = _deterministic_seed_with_parts(
                        world_seed,
                        origin_system_id,
                        event_id,
                        trigger_day,
                        propagation_index,
                        "propagation_select",
                    )
                    select_rng = random.Random(select_seed)
                    shuffled = list(candidate_neighbors)
                    select_rng.shuffle(shuffled)
                    selected_neighbors = shuffled[:systems_affected]
                    scheduled_day = trigger_day + delay_days
                    print(
                        "Propagation evaluated: "
                        f"origin_system_id={origin_system_id} event_id={event_id} "
                        f"trigger_day={trigger_day} propagation_index={propagation_index} "
                        f"candidate_neighbors={candidate_neighbors} "
                        f"selected_neighbors={selected_neighbors} "
                        f"situation_id={situation_id} delay_days={delay_days} "
                        f"systems_affected={systems_affected} scheduled_day={scheduled_day}"
                    )
                    for target_system_id in selected_neighbors:
                        if delay_days == 0:
                            duration_rng = random.Random(
                                _deterministic_seed_with_parts(
                                    world_seed,
                                    origin_system_id,
                                    event_id,
                                    trigger_day,
                                    propagation_index,
                                    target_system_id,
                                    "propagation_duration",
                                )
                            )
                            if self._create_propagated_situation(
                                target_system_id, situation_id, duration_rng
                            ):
                                executed += 1
                        else:
                            self.schedule_situation(
                                ScheduledSituation(
                                    situation_id=situation_id,
                                    system_id=target_system_id,
                                    trigger_day=scheduled_day,
                                )
                            )
                            executed += 1
        return executed

    def get_system_flags(self, system_id: str) -> list[str]:
        self.register_system(system_id)
        return sorted(self.system_flags[system_id])

    def drain_structural_mutations(self) -> list[dict]:
        if not self.pending_structural_mutations:
            return []
        drained = sorted(
            list(self.pending_structural_mutations),
            key=lambda row: (
                str(row.get("system_id", "")),
                str(row.get("event_id", row.get("source_event_id", ""))),
                str(row.get("mutation_type", "")),
                int(row.get("insertion_index", 0)),
            ),
        )
        self.pending_structural_mutations = []
        return drained

    def get_active_modifiers(self, system_id: str, domain: Optional[str] = None) -> list[dict[str, Any]]:
        self.register_system(system_id)
        rows = list(self.active_modifiers_by_system[system_id])
        if domain is not None:
            rows = [row for row in rows if str(row.get("domain")) == domain]
        return sorted(
            rows,
            key=lambda row: (
                str(row.get("domain", "")),
                str(row.get("target_type", "")),
                "" if row.get("target_id") is None else str(row.get("target_id")),
                str(row.get("modifier_type", "")),
                str(row.get("source_type", "")),
                str(row.get("source_id", "")),
            ),
        )

    def get_aggregated_modifier_map(self, system_id: str, domain: str) -> dict[tuple[str, str | None, str], int]:
        self.register_system(system_id)
        aggregated: dict[tuple[str, str | None, str], int] = {}
        rows = [
            row
            for row in self.active_modifiers_by_system[system_id]
            if str(row.get("domain", "")) == domain
        ]
        rows_sorted = sorted(
            rows,
            key=lambda row: (
                str(row.get("source_type", "")),
                str(row.get("source_id", "")),
                str(row.get("domain", "")),
                str(row.get("target_type", "")),
                "" if row.get("target_id") is None else str(row.get("target_id")),
                str(row.get("modifier_type", "")),
                int(row.get("modifier_value", 0)),
            ),
        )
        for row in rows_sorted:
            modifier_type = str(row.get("modifier_type", ""))
            if not modifier_type:
                continue
            canonical_target_type = _canonical_target_type(str(row.get("target_type", "")))
            target_id = row.get("target_id")
            if target_id is not None:
                target_id = str(target_id)
            key = (canonical_target_type, target_id, modifier_type)
            aggregated[key] = aggregated.get(key, 0) + int(row.get("modifier_value", 0))
        return aggregated

    def resolve_modifiers_for_entities(
        self,
        system_id: str,
        domain: str,
        entity_views: list[dict[str, Any]],
    ) -> dict[str, Any]:
        aggregated = self.get_aggregated_modifier_map(system_id=system_id, domain=domain)
        resolved: dict[str, dict[str, int]] = {}
        for entity in sorted(entity_views, key=lambda row: str(row.get("entity_id", ""))):
            entity_id = str(entity.get("entity_id", ""))
            if not entity_id:
                continue
            category_id = entity.get("category_id")
            category_id = str(category_id) if category_id is not None else None
            tags_raw = entity.get("tags", [])
            tags = {str(tag) for tag in tags_raw if isinstance(tag, str)}
            totals: dict[str, int] = {}
            for (target_type, target_id, modifier_type), value in aggregated.items():
                applies = False
                if target_type == "ALL":
                    applies = True
                elif target_type == "category" and category_id is not None and target_id == category_id:
                    applies = True
                elif target_type == "tag" and target_id in tags:
                    applies = True
                elif target_type == "id" and target_id == entity_id:
                    applies = True
                elif target_type == "destination_id" and target_id == entity_id:
                    applies = True
                if applies:
                    totals[modifier_type] = totals.get(modifier_type, 0) + int(value)
            capped: dict[str, int] = {}
            for modifier_type, value in sorted(totals.items(), key=lambda row: row[0]):
                clamped = _apply_modifier_cap(domain, modifier_type, value, self._MODIFIER_CAPS)
                if clamped != 0:
                    capped[modifier_type] = clamped
            resolved[entity_id] = capped

        ordered_resolved = {
            entity_id: {
                modifier_type: value
                for modifier_type, value in sorted(mods.items(), key=lambda row: row[0])
            }
            for entity_id, mods in sorted(resolved.items(), key=lambda row: row[0])
        }
        return {
            "domain": domain,
            "system_id": system_id,
            "resolved": ordered_resolved,
        }

    def decrement_durations(self) -> None:
        for system_id in sorted(self.active_situations.keys()):
            for entry in self.active_situations[system_id]:
                entry.remaining_days = max(0, entry.remaining_days - 1)

        for system_id in sorted(self.active_events.keys()):
            for entry in self.active_events[system_id]:
                entry.remaining_days = max(0, entry.remaining_days - 1)

    def resolve_expired(self) -> None:
        for system_id in sorted(self.active_situations.keys()):
            kept: list[ActiveSituation] = []
            for entry in self.active_situations[system_id]:
                if entry.remaining_days <= 0:
                    print(
                        f"Situation expired: {entry.situation_id} "
                        f"system={entry.system_id}"
                    )
                    definition = self._situation_catalog_by_id.get(entry.situation_id, {})
                    count = len(definition.get("modifiers", [])) if isinstance(definition.get("modifiers", []), list) else 0
                    self._remove_modifier_entries(
                        system_id=system_id,
                        source_type="situation",
                        source_id=entry.situation_id,
                        max_count=count,
                    )
                    continue
                kept.append(entry)
            self.active_situations[system_id] = kept

        for system_id in sorted(self.active_events.keys()):
            kept_events: list[ActiveEvent] = []
            for entry in self.active_events[system_id]:
                if entry.remaining_days <= 0:
                    print(
                        f"Event expired: {entry.event_id} "
                        f"system={entry.system_id}"
                    )
                    definition = self._event_catalog_by_id.get(entry.event_id, {})
                    effects = definition.get("effects", {}) if isinstance(definition, dict) else {}
                    modifiers = effects.get("modifiers", []) if isinstance(effects, dict) else []
                    count = len(modifiers) if isinstance(modifiers, list) else 0
                    self._remove_modifier_entries(
                        system_id=system_id,
                        source_type="event",
                        source_id=entry.event_id,
                        max_count=count,
                    )
                    continue
                kept_events.append(entry)
            self.active_events[system_id] = kept_events

    def _spawn_random_situation(self, system_id: str, rng: random.Random) -> bool:
        return self._spawn_random_situation_for_tier(system_id, None, rng)

    def _spawn_random_situation_for_tier(
        self,
        system_id: str,
        selected_tier: Optional[int],
        rng: random.Random,
    ) -> bool:
        if len(self.active_situations[system_id]) >= 3:
            return False
        spawnable = [
            item
            for item in self.situation_catalog
            if bool(item.get("random_allowed"))
            and not bool(item.get("event_only"))
            and not bool(item.get("recovery_only"))
            and (
                selected_tier is None
                or _int_or_default(item.get("severity_tier"), 0) == int(selected_tier)
            )
        ]
        if not spawnable:
            print(
                "Spawn gate candidate filter: "
                f"system_id={system_id} selected_type=situation "
                f"selected_tier={selected_tier} candidates_found=0"
            )
            return False
        print(
            "Spawn gate candidate filter: "
            f"system_id={system_id} selected_type=situation "
            f"selected_tier={selected_tier} candidates_found={len(spawnable)}"
        )
        selected = _weighted_pick_by_spawn_weight(spawnable, rng)
        remaining_days = _roll_duration_days(selected.get("duration_days"), rng, default_days=3)
        active = ActiveSituation(
            situation_id=str(selected.get("situation_id")),
            system_id=system_id,
            scope=str(selected.get("allowed_scope") or "system"),
            target_id=None,
            remaining_days=max(0, remaining_days),
        )
        self.add_situation(active)
        return True

    def _spawn_random_event(
        self, system_id: str, rng: random.Random, current_day: int
    ) -> Optional[ActiveEvent]:
        return self._spawn_random_event_for_tier(system_id, None, rng, current_day)

    def _spawn_random_event_for_tier(
        self,
        system_id: str,
        selected_tier: Optional[int],
        rng: random.Random,
        current_day: int,
    ) -> Optional[ActiveEvent]:
        candidates = [item for item in self.event_catalog if bool(item.get("random_allowed"))]
        if not candidates:
            return None
        tier_events = [
            item
            for item in candidates
            if selected_tier is None
            or _int_or_default(item.get("severity_tier"), 0) == int(selected_tier)
        ]
        if not tier_events:
            print(
                "Spawn gate candidate filter: "
                f"system_id={system_id} selected_type=event "
                f"selected_tier={selected_tier} candidates_found=0"
            )
            return None
        print(
            "Spawn gate candidate filter: "
            f"system_id={system_id} selected_type=event "
            f"selected_tier={selected_tier} candidates_found={len(tier_events)}"
        )
        selected = _weighted_pick_by_spawn_weight(tier_events, rng)
        remaining_days = _roll_duration_days(selected.get("duration_days"), rng, default_days=1)
        active = ActiveEvent(
            event_id=str(selected.get("event_id")),
            event_family_id=selected.get("event_family_id"),
            system_id=system_id,
            remaining_days=max(0, remaining_days),
            trigger_day=current_day,
        )
        self.add_event(active)
        return active

    def _create_propagated_situation(
        self, system_id: str, situation_id: str, rng: random.Random
    ) -> bool:
        self.register_system(system_id)
        if len(self.active_situations[system_id]) >= 3:
            return False
        definition = self._situation_catalog_by_id.get(situation_id)
        if definition is None:
            return False
        scope = str(definition.get("allowed_scope") or "system")
        if scope not in {"system", "destination"}:
            scope = "system"
        remaining_days = _roll_duration_days(
            definition.get("duration_days"), rng, default_days=3
        )
        self.add_situation(
            ActiveSituation(
                situation_id=situation_id,
                system_id=system_id,
                scope=scope,
                target_id=None,
                remaining_days=max(0, remaining_days),
            )
        )
        return True

    def _apply_destroy_destination_tags(
        self,
        *,
        target_system_id: str,
        event_id: str,
        destroy_destination_ids: list[Any],
    ) -> None:
        if self._sector_ref is None:
            for destination_id in destroy_destination_ids:
                print(
                    "Destination destruction skipped: "
                    f"system_id={target_system_id} event_id={event_id} "
                    f"destination_id={destination_id} reason=missing_sector_context"
                )
            return
        system = self._sector_ref.get_system(target_system_id)
        if system is None:
            return
        for destination_id in destroy_destination_ids:
            if not isinstance(destination_id, str) or not destination_id:
                continue
            destination = next(
                (
                    row
                    for row in getattr(system, "destinations", [])
                    if getattr(row, "destination_id", None) == destination_id
                ),
                None,
            )
            if destination is None:
                print(
                    "Destination destruction ignored: "
                    f"system_id={target_system_id} event_id={event_id} "
                    f"destination_id={destination_id} reason=missing_destination"
                )
                continue
            tags = _ensure_destination_tags(destination)
            already_destroyed = "destroyed" in tags
            if not already_destroyed:
                tags.append("destroyed")
            print(
                "Destination destroyed tag update: "
                f"system_id={target_system_id} event_id={event_id} "
                f"destination_id={destination_id} tag_added={not already_destroyed} "
                f"already_destroyed={already_destroyed}"
            )

    def _apply_population_delta(
        self,
        *,
        target_system_id: str,
        event_id: str,
        population_delta: int,
    ) -> None:
        if self._sector_ref is None:
            print(
                "Population mutation skipped: "
                f"system_id={target_system_id} event_id={event_id} "
                f"delta={population_delta} reason=missing_sector_context"
            )
            return
        system = self._sector_ref.get_system(target_system_id)
        if system is None:
            return
        old_pop = int(getattr(system, "population", 0))
        new_pop = max(0, old_pop + int(population_delta))
        if new_pop == old_pop:
            print(
                "Population mutation applied: "
                f"system_id={target_system_id} event_id={event_id} "
                f"old_pop={old_pop} delta={population_delta} new_pop={new_pop}"
            )
            return
        attributes = dict(getattr(system, "attributes", {}) or {})
        attributes["population_level"] = new_pop
        updated = replace(system, population=new_pop, attributes=attributes)
        _replace_system_in_sector(self._sector_ref, updated)
        print(
            "Population mutation applied: "
            f"system_id={target_system_id} event_id={event_id} "
            f"old_pop={old_pop} delta={population_delta} new_pop={new_pop}"
        )

    def _apply_government_change(
        self,
        *,
        target_system_id: str,
        event_id: str,
        government_change: Any,
    ) -> None:
        if not isinstance(government_change, str) or not government_change:
            return
        if self._valid_government_ids and government_change not in self._valid_government_ids:
            print(
                "Government change ignored: "
                f"system_id={target_system_id} event_id={event_id} "
                f"new_government_id={government_change} reason=unknown_government_id"
            )
            return
        if self._sector_ref is None:
            print(
                "Government change skipped: "
                f"system_id={target_system_id} event_id={event_id} "
                f"new_government_id={government_change} reason=missing_sector_context"
            )
            return
        system = self._sector_ref.get_system(target_system_id)
        if system is None:
            return
        old_government_id = str(getattr(system, "government_id", ""))
        attributes = dict(getattr(system, "attributes", {}) or {})
        attributes["government_id"] = government_change
        updated = replace(system, government_id=government_change, attributes=attributes)
        _replace_system_in_sector(self._sector_ref, updated)
        print(
            "Government mutation applied: "
            f"system_id={target_system_id} event_id={event_id} "
            f"old_government_id={old_government_id} new_government_id={government_change}"
        )

    def _apply_npc_mutations(
        self,
        *,
        target_system_id: str,
        event_id: str,
        npc_mutations: list[Any],
    ) -> None:
        registry = self._npc_registry_ref
        if registry is None:
            for row in npc_mutations:
                if isinstance(row, dict):
                    print(
                        "NPC mutation ignored: "
                        f"system_id={target_system_id} event_id={event_id} "
                        f"npc_id={row.get('npc_id')} mutation_type={row.get('mutation_type')} "
                        "applied_or_ignored=ignored reason=missing_npc_registry"
                    )
            return
        for row in npc_mutations:
            if not isinstance(row, dict):
                continue
            npc_id = row.get("npc_id")
            mutation_type = row.get("mutation_type")
            new_value = row.get("new_value")
            if not isinstance(npc_id, str) or not npc_id:
                continue
            if not isinstance(mutation_type, str) or not mutation_type:
                continue
            npc = registry.get(npc_id)
            if npc is None:
                print(
                    "NPC mutation ignored: "
                    f"system_id={target_system_id} event_id={event_id} "
                    f"npc_id={npc_id} mutation_type={mutation_type} "
                    "applied_or_ignored=ignored reason=npc_not_found"
                )
                continue

            if mutation_type == "remove":
                if npc.persistence_tier == NPCPersistenceTier.TIER_3:
                    print(
                        "NPC mutation ignored: "
                        f"system_id={target_system_id} event_id={event_id} "
                        f"npc_id={npc_id} mutation_type={mutation_type} "
                        "applied_or_ignored=ignored reason=persistence_tier_locked"
                    )
                    continue
                registry.remove(npc_id)
                print(
                    "NPC mutation applied: "
                    f"system_id={target_system_id} event_id={event_id} "
                    f"npc_id={npc_id} mutation_type={mutation_type} "
                    "applied_or_ignored=applied reason=ok"
                )
                continue

            updated_npc = npc
            if mutation_type == "faction_change":
                if not isinstance(new_value, str) or not new_value:
                    print(
                        "NPC mutation ignored: "
                        f"system_id={target_system_id} event_id={event_id} "
                        f"npc_id={npc_id} mutation_type={mutation_type} "
                        "applied_or_ignored=ignored reason=invalid_new_value"
                    )
                    continue
                updated_npc = _clone_npc(npc)
                updated_npc.affiliation_ids = [new_value]
            elif mutation_type == "hostility_flag":
                updated_npc = _clone_npc(npc)
                updated_npc.memory_flags = dict(updated_npc.memory_flags)
                updated_npc.memory_flags["hostile"] = bool(new_value)
            else:
                print(
                    "NPC mutation ignored: "
                    f"system_id={target_system_id} event_id={event_id} "
                    f"npc_id={npc_id} mutation_type={mutation_type} "
                    "applied_or_ignored=ignored reason=unsupported_mutation_type"
                )
                continue

            registry.update(updated_npc)
            print(
                "NPC mutation applied: "
                f"system_id={target_system_id} event_id={event_id} "
                f"npc_id={npc_id} mutation_type={mutation_type} "
                "applied_or_ignored=applied reason=ok"
            )

    def _remove_active_event_instance(
        self,
        *,
        system_id: str,
        event_id: str,
        trigger_day: int,
    ) -> None:
        rows = self.active_events.get(system_id, [])
        for index in range(len(rows) - 1, -1, -1):
            row = rows[index]
            if (
                row.event_id == event_id
                and int(getattr(row, "trigger_day", 0)) == trigger_day
            ):
                rows.pop(index)
                return

    def _add_situation_modifiers(self, active_situation: ActiveSituation) -> None:
        definition = self._situation_catalog_by_id.get(active_situation.situation_id)
        if definition is None:
            return
        modifiers = definition.get("modifiers", [])
        if isinstance(modifiers, list):
            self._add_modifier_entries(
                system_id=active_situation.system_id,
                source_type="situation",
                source_id=active_situation.situation_id,
                modifiers=modifiers,
            )

    def _add_modifier_entries(
        self,
        system_id: str,
        source_type: str,
        source_id: str,
        modifiers: list[Any],
    ) -> None:
        self.register_system(system_id)
        for modifier in modifiers:
            if not isinstance(modifier, dict):
                continue
            row = dict(modifier)
            row["source_type"] = source_type
            row["source_id"] = source_id
            self.active_modifiers_by_system[system_id].append(row)

    def _remove_modifier_entries(
        self,
        system_id: str,
        source_type: str,
        source_id: str,
        max_count: Optional[int] = None,
    ) -> None:
        self.register_system(system_id)
        kept: list[dict[str, Any]] = []
        removed = 0
        for row in self.active_modifiers_by_system[system_id]:
            if row.get("source_type") == source_type and row.get("source_id") == source_id:
                if max_count is None or removed < max_count:
                    removed += 1
                    continue
            kept.append(row)
        self.active_modifiers_by_system[system_id] = kept


def _deterministic_seed(world_seed: int, current_day: int, channel: str) -> int:
    packed = f"{world_seed}|{current_day}|{channel}".encode("utf-8")
    return int(hashlib.sha256(packed).hexdigest(), 16)


def _rng_u01(seed: int) -> float:
    return random.Random(seed).random()


def _deterministic_seed_with_parts(*parts: Any) -> int:
    packed = "|".join(str(part) for part in parts).encode("utf-8")
    return int(hashlib.sha256(packed).hexdigest(), 16)


def _coerce_non_negative_int(value: Any, default: int) -> int:
    try:
        if isinstance(value, bool):
            return default
        number = int(value)
    except (TypeError, ValueError):
        return default
    if number < 0:
        return default
    return number


def _int_or_default(value: Any, default: int) -> int:
    try:
        if isinstance(value, bool):
            return default
        return int(value)
    except (TypeError, ValueError):
        return default


def _load_valid_government_ids() -> set[str]:
    path = Path(__file__).resolve().parents[1] / "data" / "governments.json"
    try:
        with path.open("r", encoding="utf-8") as handle:
            payload = json.load(handle)
    except (OSError, json.JSONDecodeError):
        return set()
    entries = payload.get("governments", []) if isinstance(payload, dict) else []
    result: set[str] = set()
    for row in entries:
        if isinstance(row, dict):
            government_id = row.get("id")
            if isinstance(government_id, str) and government_id:
                result.add(government_id)
    return result


def _replace_system_in_sector(sector: Any, updated_system: Any) -> None:
    systems = getattr(sector, "systems", None)
    if not isinstance(systems, list):
        return
    for index, row in enumerate(systems):
        if getattr(row, "system_id", None) == getattr(updated_system, "system_id", None):
            systems[index] = updated_system
            return


def _ensure_destination_tags(destination: Any) -> list[str]:
    if isinstance(destination, dict):
        tags = destination.get("tags")
        if not isinstance(tags, list):
            destination["tags"] = []
            tags = destination["tags"]
        return tags
    tags = getattr(destination, "tags", None)
    if isinstance(tags, list):
        return tags
    try:
        object.__setattr__(destination, "tags", [])
        return getattr(destination, "tags")
    except Exception:  # noqa: BLE001
        return []


def _clone_npc(npc: Any) -> Any:
    if hasattr(npc, "to_dict") and callable(npc.to_dict) and hasattr(type(npc), "from_dict"):
        return type(npc).from_dict(npc.to_dict())
    return npc


def _is_structural_event_effects(effects: dict[str, Any]) -> bool:
    population_delta = effects.get("population_delta")
    if isinstance(population_delta, int) and population_delta != 0:
        return True
    government_change = effects.get("government_change")
    if government_change not in (None, "", []):
        return True
    destroy_destination_ids = effects.get("destroy_destination_ids")
    if isinstance(destroy_destination_ids, list) and len(destroy_destination_ids) > 0:
        return True
    return False


def _roll_duration_days(duration_spec: Any, rng: random.Random, default_days: int) -> int:
    if isinstance(duration_spec, dict):
        minimum = duration_spec.get("min")
        maximum = duration_spec.get("max")
        if isinstance(minimum, int) and isinstance(maximum, int):
            low = min(minimum, maximum)
            high = max(minimum, maximum)
            return rng.randint(low, high)
    if isinstance(duration_spec, int):
        return duration_spec
    return default_days


def _select_spawn_severity_tier(roll: float) -> int:
    if roll < 0.30:
        return 1
    if roll < 0.65:
        return 2
    if roll < 0.85:
        return 3
    if roll < 0.95:
        return 4
    return 5


def _weighted_pick_by_spawn_weight(
    candidates: list[dict[str, Any]], rng: random.Random
) -> dict[str, Any]:
    if not candidates:
        raise ValueError("weighted pick requires at least one candidate")
    weights = [max(0, int(item.get("spawn_weight", 1) or 1)) for item in candidates]
    total = sum(weights)
    if total <= 0:
        return candidates[rng.randrange(len(candidates))]
    pick = rng.uniform(0, total)
    running = 0.0
    for index, weight in enumerate(weights):
        running += weight
        if pick <= running:
            return candidates[index]
    return candidates[-1]


def _select_weighted_tier(candidates: list[dict[str, Any]], tier_weights: dict[int, int], rng: random.Random) -> Optional[int]:
    available_tiers = sorted({int(item.get("severity_tier", 0)) for item in candidates if int(item.get("severity_tier", 0)) in tier_weights})
    if not available_tiers:
        return None
    total = sum(tier_weights[tier] for tier in available_tiers)
    pick = rng.uniform(0, total)
    running = 0.0
    for tier in available_tiers:
        running += tier_weights[tier]
        if pick <= running:
            return tier
    return available_tiers[-1]


def _canonical_target_type(target_type: str) -> str:
    token = target_type.strip()
    if token == "ALL":
        return "ALL"
    if token in {"category", "tag", "id", "destination_id"}:
        return token
    if token in {"sku", "hull_id", "module_type", "crew_role", "mission_type", "route_id", "system_id", "special"}:
        return "id"
    return token or "id"


def _apply_modifier_cap(
    domain: str,
    modifier_type: str,
    value: int,
    caps: dict[tuple[str, str], tuple[int | None, int | None]],
) -> int:
    bounds = caps.get((domain, modifier_type))
    if bounds is None:
        return value
    lower, upper = bounds
    clamped = value
    if lower is not None:
        clamped = max(lower, clamped)
    if upper is not None:
        clamped = min(upper, clamped)
    return clamped
