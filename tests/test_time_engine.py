import pytest

import time_engine as te


def setup_function() -> None:
    te._reset_time_state_for_test()


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
