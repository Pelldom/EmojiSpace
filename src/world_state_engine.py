import hashlib
import json
import random
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, ClassVar, Optional


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


@dataclass
class ScheduledEvent:
    event_id: str
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
    situation_catalog: list[dict[str, Any]] = field(default_factory=list)
    event_catalog: list[dict[str, Any]] = field(default_factory=list)
    system_flags: dict[str, set[str]] = field(default_factory=dict)
    pending_structural_mutations: list[dict[str, Any]] = field(default_factory=list)
    active_modifiers_by_system: dict[str, list[dict[str, Any]]] = field(default_factory=dict)
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

        rng_seed = _deterministic_seed(world_seed, current_day, "spawn_gate")
        rng = random.Random(rng_seed)
        spawn_probability = max(0.0, min(1.0, float(event_frequency_percent) / 100.0))
        if rng.random() >= spawn_probability:
            return

        if rng.random() < 0.70:
            self._spawn_random_situation(current_system_id, rng)
            return
        active_event = self._spawn_random_event(current_system_id, rng)
        if active_event is not None:
            self.apply_event_effects(
                world_seed=world_seed,
                current_day=current_day,
                target_system_id=current_system_id,
                event_id=active_event.event_id,
                rng=rng,
            )

    def apply_event_effects(
        self,
        world_seed: int,
        current_day: int,
        target_system_id: str,
        event_id: str,
        rng: random.Random,
    ) -> None:
        del world_seed  # Reserved for future deterministic channels.
        self.register_system(target_system_id)
        event_def = self._event_catalog_by_id.get(event_id)
        if event_def is None:
            raise ValueError(f"Event definition not found for event_id={event_id}")

        effects = event_def.get("effects", {})
        if not isinstance(effects, dict):
            effects = {}

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
                    raise ValueError(f"Situation definition not found for situation_id={situation_id}")
                scope = item.get("scope_type")
                if scope not in {"system", "destination"}:
                    scope = str(situation_def.get("allowed_scope") or "system")
                remaining_days = _roll_duration_days(situation_def.get("duration_days"), rng, default_days=3)
                self.add_situation(
                    ActiveSituation(
                        situation_id=situation_id,
                        system_id=target_system_id,
                        scope=scope,
                        target_id=None,
                        remaining_days=max(0, remaining_days),
                    )
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

        flags_add = effects.get("system_flag_add", [])
        if isinstance(flags_add, list):
            for value in flags_add:
                if isinstance(value, str):
                    self.system_flags[target_system_id].add(value)

        flags_remove = effects.get("system_flag_remove", [])
        if isinstance(flags_remove, list):
            for value in flags_remove:
                if isinstance(value, str):
                    self.system_flags[target_system_id].discard(value)

        modifiers = effects.get("modifiers", [])
        if isinstance(modifiers, list):
            self._add_modifier_entries(
                system_id=target_system_id,
                source_type="event",
                source_id=event_id,
                modifiers=modifiers,
            )

        structural_keys = [
            "government_change",
            "population_delta",
            "destroy_destination_ids",
            "asset_destruction",
        ]
        structural_payload: dict[str, Any] = {}
        for key in structural_keys:
            value = effects.get(key)
            if key == "population_delta" and isinstance(value, int) and value != 0:
                structural_payload[key] = value
            elif key == "government_change" and value not in (None, "", []):
                structural_payload[key] = value
            elif key == "destroy_destination_ids" and isinstance(value, list) and value:
                structural_payload[key] = list(value)
            elif key == "asset_destruction" and isinstance(value, dict) and value:
                structural_payload[key] = dict(value)
        if structural_payload:
            self.pending_structural_mutations.append(
                {
                    "system_id": target_system_id,
                    "source_event_id": event_id,
                    "mutation_payload": structural_payload,
                    "day_applied": None,
                }
            )

    def process_scheduled_events(self, world_seed: int, current_day: int) -> int:
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
                )
            )
            self.apply_event_effects(
                world_seed=world_seed,
                current_day=current_day,
                target_system_id=row.system_id,
                event_id=row.event_id,
                rng=rng,
            )
            executed += 1

        self.scheduled_events = pending
        return executed

    def process_propagation(
        self,
        world_seed: int,
        current_day: int,
        get_neighbors_fn: Callable[[str], list[str]],
    ) -> int:
        active_event_ids = sorted(
            {
                row.event_id
                for rows in self.active_events.values()
                for row in rows
                if row.event_id in self._event_catalog_by_id
            }
        )
        executed = 0
        for event_id in active_event_ids:
            event_def = self._event_catalog_by_id.get(event_id)
            if event_def is None:
                continue
            if not bool(event_def.get("propagation_allowed")):
                continue
            if int(event_def.get("propagation_radius", 0)) < 1:
                continue

            roll_rng = random.Random(
                _deterministic_seed_with_parts(
                    world_seed,
                    current_day,
                    "propagation",
                    event_id,
                )
            )
            chance_percent = int(event_def.get("propagation_daily_chance_percent", 25))
            chance = max(0.0, min(1.0, float(chance_percent) / 100.0))
            if roll_rng.random() >= chance:
                continue

            sources = sorted(
                [
                    system_id
                    for system_id, rows in self.active_events.items()
                    if any(row.event_id == event_id for row in rows)
                ]
            )
            selected_source: Optional[str] = None
            selected_targets: list[str] = []
            for source in sources:
                neighbors = sorted(set(get_neighbors_fn(source)))
                targets = [
                    neighbor
                    for neighbor in neighbors
                    if neighbor != source
                    and not any(row.event_id == event_id for row in self.get_active_events(neighbor))
                ]
                if targets:
                    selected_source = source
                    selected_targets = targets
                    break
            if selected_source is None:
                continue

            activation_rng = random.Random(
                _deterministic_seed_with_parts(
                    world_seed,
                    current_day,
                    "propagation_target",
                    event_id,
                    selected_source,
                )
            )
            target_system_id = activation_rng.choice(selected_targets)
            self.register_system(target_system_id)
            remaining_days = _roll_duration_days(event_def.get("duration_days"), activation_rng, default_days=1)
            self.add_event(
                ActiveEvent(
                    event_id=event_id,
                    event_family_id=event_def.get("event_family_id"),
                    system_id=target_system_id,
                    remaining_days=max(0, remaining_days),
                )
            )
            self.apply_event_effects(
                world_seed=world_seed,
                current_day=current_day,
                target_system_id=target_system_id,
                event_id=event_id,
                rng=activation_rng,
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
        if len(self.active_situations[system_id]) >= 3:
            return False
        spawnable = [
            item
            for item in self.situation_catalog
            if bool(item.get("random_allowed"))
            and not bool(item.get("event_only"))
            and not bool(item.get("recovery_only"))
        ]
        if not spawnable:
            return False
        selected = rng.choice(spawnable)
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

    def _spawn_random_event(self, system_id: str, rng: random.Random) -> Optional[ActiveEvent]:
        candidates = [item for item in self.event_catalog if bool(item.get("random_allowed"))]
        if not candidates:
            return None
        tier_weights: dict[int, int] = {1: 30, 2: 35, 3: 20, 4: 10, 5: 5}
        selected_tier = _select_weighted_tier(candidates, tier_weights, rng)
        if selected_tier is None:
            return None
        tier_events = [item for item in candidates if int(item.get("severity_tier", 0)) == selected_tier]
        if not tier_events:
            return None
        selected = rng.choice(tier_events)
        remaining_days = _roll_duration_days(selected.get("duration_days"), rng, default_days=1)
        active = ActiveEvent(
            event_id=str(selected.get("event_id")),
            event_family_id=selected.get("event_family_id"),
            system_id=system_id,
            remaining_days=max(0, remaining_days),
        )
        self.add_event(active)
        return active

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


def _deterministic_seed_with_parts(*parts: Any) -> int:
    packed = "|".join(str(part) for part in parts).encode("utf-8")
    return int(hashlib.sha256(packed).hexdigest(), 16)


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
