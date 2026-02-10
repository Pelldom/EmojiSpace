from dataclasses import dataclass


_current_turn = 0
_player_action_context = False
_hard_stop_player_dead = False
_hard_stop_tier2_detention = False


@dataclass(frozen=True)
class TimeAdvanceResult:
    starting_turn: int
    days_requested: int
    days_completed: int
    current_turn: int
    hard_stop_reason: str | None


def get_current_turn() -> int:
    return _current_turn


def get_current_date() -> str:
    year_offset = _current_turn // 100
    day_of_year = _current_turn % 100
    month = day_of_year // 10
    day = day_of_year % 10
    return f"{2200 + year_offset}.{month}.{day}"


def advance_time(days: int, reason: str) -> TimeAdvanceResult:
    _validate_advance_request(days)
    _require_player_action_context()
    starting_turn = _current_turn
    _log_time_event(
        "time_advance_requested",
        f"start_turn={starting_turn} days={days} reason={reason}",
    )
    days_completed = 0
    hard_stop_reason = None
    for _ in range(days):
        hard_stop_reason = _check_hard_stop()
        if hard_stop_reason is not None:
            _log_time_event("time_advance_hard_stop", f"turn={_current_turn} reason={hard_stop_reason}")
            break
        completed = _process_single_day()
        if not completed:
            hard_stop_reason = _check_hard_stop()
            _log_time_event("time_advance_hard_stop", f"turn={_current_turn} reason={hard_stop_reason}")
            break
        days_completed += 1
    return TimeAdvanceResult(
        starting_turn=starting_turn,
        days_requested=days,
        days_completed=days_completed,
        current_turn=_current_turn,
        hard_stop_reason=hard_stop_reason,
    )


def galaxy_tick(day: int) -> None:
    _log_time_event("galaxy_tick", f"day={day}")


def system_tick(day: int) -> None:
    _log_time_event("system_tick", f"day={day}")


def planet_station_tick(day: int) -> None:
    _log_time_event("planet_station_tick", f"day={day}")


def location_tick(day: int) -> None:
    _log_time_event("location_tick", f"day={day}")


def npc_tick(day: int) -> None:
    _log_time_event("npc_tick", f"day={day}")


def end_of_day_log(day: int) -> None:
    _log_time_event("end_of_day_log", f"day={day}")


def _process_single_day() -> bool:
    next_turn = _current_turn + 1
    for tick in (
        galaxy_tick,
        system_tick,
        planet_station_tick,
        location_tick,
        npc_tick,
        end_of_day_log,
    ):
        tick(next_turn)
        if _check_hard_stop() is not None:
            return False
    _set_current_turn(next_turn)
    _log_time_event("time_advance_day_completed", f"turn={_current_turn} hard_stop=None")
    return True


def _check_hard_stop() -> str | None:
    if _hard_stop_player_dead:
        return "player_death"
    if _hard_stop_tier2_detention:
        return "tier2_detention"
    return None


def _validate_advance_request(days: int) -> None:
    if not isinstance(days, int):
        raise ValueError("Time advance days must be an integer.")
    if days < 1 or days > 10:
        raise ValueError("Time advance days must be between 1 and 10.")


def _require_player_action_context() -> None:
    if not _player_action_context:
        raise RuntimeError("Time advancement must be called from player action resolution.")


def _log_time_event(action: str, state_change: str) -> None:
    print(f"[time_engine] action={action} change={state_change}")


def _set_current_turn(turn: int) -> None:
    global _current_turn
    _current_turn = turn


def _set_player_action_context(active: bool) -> None:
    global _player_action_context
    _player_action_context = active


def _set_hard_stop_state(*, player_dead: bool = False, tier2_detention: bool = False) -> None:
    global _hard_stop_player_dead, _hard_stop_tier2_detention
    _hard_stop_player_dead = player_dead
    _hard_stop_tier2_detention = tier2_detention


def _reset_time_state_for_test() -> None:
    global _current_turn, _player_action_context, _hard_stop_player_dead, _hard_stop_tier2_detention
    _current_turn = 0
    _player_action_context = False
    _hard_stop_player_dead = False
    _hard_stop_tier2_detention = False


class TimeEngine:
    def __init__(self) -> None:
        pass

    @property
    def current_turn(self) -> int:
        return get_current_turn()

    def advance(self) -> int:
        _set_player_action_context(True)
        try:
            result = advance_time(days=1, reason="legacy_action")
        finally:
            _set_player_action_context(False)
        return result.current_turn
