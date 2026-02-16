import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"
sys.path.insert(0, str(SRC_ROOT))

import time_engine as te

_DEFAULT_GALAXY_TICK = te.galaxy_tick
_DEFAULT_SYSTEM_TICK = te.system_tick
_DEFAULT_PLANET_STATION_TICK = te.planet_station_tick
_DEFAULT_LOCATION_TICK = te.location_tick
_DEFAULT_NPC_TICK = te.npc_tick
_DEFAULT_END_OF_DAY_LOG = te.end_of_day_log


def setup_function() -> None:
    te._reset_time_state_for_test()
    te.galaxy_tick = _DEFAULT_GALAXY_TICK
    te.system_tick = _DEFAULT_SYSTEM_TICK
    te.planet_station_tick = _DEFAULT_PLANET_STATION_TICK
    te.location_tick = _DEFAULT_LOCATION_TICK
    te.npc_tick = _DEFAULT_NPC_TICK
    te.end_of_day_log = _DEFAULT_END_OF_DAY_LOG


def test_date_derivation_from_turn() -> None:
    te._set_current_turn(345)
    assert te.get_current_date() == "2203.4.5"


def test_day_cap_enforcement() -> None:
    te._set_player_action_context(True)
    try:
        with pytest.raises(ValueError):
            te.advance_time(0, "test")
        with pytest.raises(ValueError):
            te.advance_time(-1, "test")
        with pytest.raises(ValueError):
            te.advance_time(11, "test")
        with pytest.raises(ValueError):
            te.advance_time(1.5, "test")  # type: ignore[arg-type]
        assert te.advance_time(1, "test").current_turn == 1
        assert te.advance_time(10, "test").current_turn == 11
    finally:
        te._set_player_action_context(False)


def test_sequential_tick_execution() -> None:
    calls: list[str] = []

    def make_tick(name: str):
        def _tick(day: int) -> None:
            calls.append(f"{name}:{day}")

        return _tick

    te.galaxy_tick = make_tick("galaxy")
    te.system_tick = make_tick("system")
    te.planet_station_tick = make_tick("planet_station")
    te.location_tick = make_tick("location")
    te.npc_tick = make_tick("npc")
    te.end_of_day_log = make_tick("end_of_day")

    te._set_player_action_context(True)
    try:
        result = te.advance_time(2, "test")
    finally:
        te._set_player_action_context(False)

    assert result.current_turn == 2
    assert result.days_completed == 2
    assert calls == [
        "galaxy:1",
        "system:1",
        "planet_station:1",
        "location:1",
        "npc:1",
        "end_of_day:1",
        "galaxy:2",
        "system:2",
        "planet_station:2",
        "location:2",
        "npc:2",
        "end_of_day:2",
    ]


def test_interruptibility_on_hard_stop() -> None:
    calls: list[str] = []

    def stop_tick(day: int) -> None:
        calls.append("galaxy")
        te._set_hard_stop_state(player_dead=True)

    def system_tick(day: int) -> None:
        calls.append("system")

    te.galaxy_tick = stop_tick
    te.system_tick = system_tick

    te._set_player_action_context(True)
    try:
        result = te.advance_time(3, "test")
    finally:
        te._set_player_action_context(False)

    assert result.current_turn == 0
    assert result.days_completed == 0
    assert result.hard_stop_reason == "player_death"
    assert calls == ["galaxy"]


class _StubSystem:
    def __init__(self, neighbors: list[str]) -> None:
        self.neighbors = neighbors


class _StubSector:
    def __init__(self, adjacency: dict[str, list[str]]) -> None:
        self._adjacency = adjacency

    def get_system(self, system_id: str):
        if system_id not in self._adjacency:
            return None
        return _StubSystem(self._adjacency[system_id])


class _StubPlayer:
    def __init__(self, current_system_id: str) -> None:
        self.current_system_id = current_system_id


class _StubWorldStateEngine:
    def __init__(self) -> None:
        self.order: list[str] = []
        self.spawn_calls = 0
        self.scheduled_calls: list[int] = []
        self.propagation_calls = 0
        self.expired_removed = False
        self._active_event_days: list[int] = []

    def process_scheduled_events(self, world_seed: int, current_day: int) -> int:
        _ = world_seed
        self.order.append("scheduled")
        self.scheduled_calls.append(current_day)
        if current_day == 1:
            self._active_event_days = [1]
            return 1
        return 0

    def evaluate_spawn_gate(
        self,
        world_seed: int,
        current_system_id: str,
        neighbor_system_ids: list[str],
        current_day: int,
        event_frequency_percent: int,
    ) -> None:
        _ = (world_seed, current_system_id, neighbor_system_ids, current_day, event_frequency_percent)
        self.order.append("spawn")
        self.spawn_calls += 1

    def process_propagation(self, world_seed: int, current_day: int, get_neighbors_fn) -> int:
        _ = (world_seed, current_day, get_neighbors_fn)
        self.order.append("propagation")
        self.propagation_calls += 1
        return 0

    def decrement_durations(self) -> None:
        self.order.append("decrement")
        self._active_event_days = [max(0, day - 1) for day in self._active_event_days]

    def resolve_expired(self) -> None:
        self.order.append("resolve")
        if any(day <= 0 for day in self._active_event_days):
            self.expired_removed = True
        self._active_event_days = [day for day in self._active_event_days if day > 0]


def test_advance_day_invokes_spawn_gate_once() -> None:
    stub = _StubWorldStateEngine()
    te._world_state_engine = stub
    te._world_state_seed = 42
    te._world_state_sector = _StubSector({"SYS-1": ["SYS-2"], "SYS-2": ["SYS-1"]})
    te._world_state_player = _StubPlayer("SYS-1")
    te._world_state_event_frequency_percent = 8

    te._set_player_action_context(True)
    try:
        te.advance_time(1, "test")
    finally:
        te._set_player_action_context(False)

    assert stub.spawn_calls == 1


def test_scheduled_events_execute_when_due_in_daily_advance() -> None:
    stub = _StubWorldStateEngine()
    te._world_state_engine = stub
    te._world_state_seed = 7
    te._world_state_sector = _StubSector({"SYS-1": ["SYS-2"], "SYS-2": ["SYS-1"]})
    te._world_state_player = _StubPlayer("SYS-1")
    te._world_state_event_frequency_percent = 8

    te._set_player_action_context(True)
    try:
        te.advance_time(1, "test")
    finally:
        te._set_player_action_context(False)

    assert stub.scheduled_calls == [1]
    assert stub.order[:3] == ["scheduled", "spawn", "propagation"]


def test_expired_events_removed_after_duration_in_daily_lifecycle() -> None:
    stub = _StubWorldStateEngine()
    te._world_state_engine = stub
    te._world_state_seed = 9
    te._world_state_sector = _StubSector({"SYS-1": []})
    te._world_state_player = _StubPlayer("SYS-1")
    te._world_state_event_frequency_percent = 8

    te._set_player_action_context(True)
    try:
        te.advance_time(1, "test")
    finally:
        te._set_player_action_context(False)

    assert stub.expired_removed is True
    assert stub.order == ["scheduled", "spawn", "propagation", "decrement", "resolve"]