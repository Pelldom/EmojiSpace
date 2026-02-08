class PlayerState:
    def __init__(self, start_system_id: str) -> None:
        self._location_system_id = start_system_id
        self._holdings: dict[str, int] = {}
        self._reputation: int = 0
        self._credits: int = 0
        self._has_ship: bool = True
        self._progression_tracks: dict[str, int] = {
            "trust": 0,
            "notoriety": 0,
            "entrepreneur": 0,
            "criminal": 0,
            "law": 0,
            "outlaw": 0,
        }
        self.victory_eligible: bool = False
        self.victory_track: str | None = None
        self.victory_mission_active: bool = False
        self.victory_mission_completed: bool = False
        self.run_ended: bool = False
        self.run_end_reason: str | None = None
        self._reputation_by_system: dict[str, int] = {}
        self._heat_by_system: dict[str, int] = {}
        self._licenses_by_system: dict[str, dict[str, bool]] = {}
        self._warrants_by_system: dict[str, bool] = {}
        self._fines_by_system: dict[str, int] = {}

    @property
    def location_system_id(self) -> str:
        return self._location_system_id

    def move_to(self, system_id: str) -> str:
        previous = self._location_system_id
        self._location_system_id = system_id
        return previous

    def buy(self, sku: str) -> None:
        self._holdings[sku] = self._holdings.get(sku, 0) + 1

    def can_sell(self, sku: str) -> bool:
        return self._holdings.get(sku, 0) > 0

    def sell(self, sku: str) -> bool:
        if not self.can_sell(sku):
            return False
        self._holdings[sku] = self._holdings.get(sku, 0) - 1
        return True

    def holdings_snapshot(self) -> dict[str, int]:
        return dict(self._holdings)

    def credits(self) -> int:
        return self._credits

    def set_credits(self, value: int, logger=None, turn: int = 0, system_id: str | None = None) -> None:
        self._credits = max(0, value)
        self._check_bankruptcy(logger=logger, turn=turn, system_id=system_id)

    def has_ship(self) -> bool:
        return self._has_ship

    def remove_ship(self, logger=None, turn: int = 0, system_id: str | None = None) -> None:
        self._has_ship = False
        self._check_bankruptcy(logger=logger, turn=turn, system_id=system_id)

    def progression_snapshot(self) -> dict[str, int]:
        return dict(self._progression_tracks)

    def get_progression_track(self, track: str) -> int:
        return self._progression_tracks[track]

    def set_progression_track(
        self,
        track: str,
        value: int,
        logger=None,
        turn: int = 0,
        system_id: str | None = None,
    ) -> None:
        if track not in self._progression_tracks:
            raise ValueError(f"Unknown progression track: {track}")
        old_value = self._progression_tracks[track]
        new_value = max(0, min(100, value))
        if new_value == old_value:
            return
        self._progression_tracks[track] = new_value
        self._on_progression_change(
            track=track,
            old_value=old_value,
            new_value=new_value,
            logger=logger,
            turn=turn,
            system_id=system_id,
        )

    def adjust_progression_track(
        self,
        track: str,
        delta: int,
        logger=None,
        turn: int = 0,
        system_id: str | None = None,
    ) -> None:
        self.set_progression_track(
            track=track,
            value=self.get_progression_track(track) + delta,
            logger=logger,
            turn=turn,
            system_id=system_id,
        )

    def finalize_victory_if_ready(self, logger=None, turn: int = 0, system_id: str | None = None) -> None:
        if not self.victory_eligible or self.victory_mission_active:
            return
        if not self.victory_mission_completed:
            return
        self.run_ended = True
        self.run_end_reason = f"victory:{self.victory_track}"
        if logger is not None:
            logger.log(
                turn=turn,
                action="victory_finalized",
                state_change=f"track={self.victory_track} system_id={system_id}",
            )

    def end_run(self, reason: str, logger=None, turn: int = 0, system_id: str | None = None) -> None:
        if self.run_ended:
            return
        self.run_ended = True
        self.run_end_reason = reason
        if logger is not None:
            logger.log(
                turn=turn,
                action="run_ended",
                state_change=f"reason={reason} system_id={system_id}",
            )

    def _check_bankruptcy(self, logger=None, turn: int = 0, system_id: str | None = None) -> None:
        if self.run_ended:
            return
        if _bankruptcy_detected(self._credits, self._has_ship, self._holdings):
            self.run_ended = True
            self.run_end_reason = "bankruptcy"
            _log_run_ended(logger, turn, self.run_end_reason, system_id)

    def _on_progression_change(
        self,
        track: str,
        old_value: int,
        new_value: int,
        logger=None,
        turn: int = 0,
        system_id: str | None = None,
    ) -> None:
        opposing = _opposing_track(track)
        opposing_value = self._progression_tracks[opposing]
        eligible = new_value == 100 and opposing_value <= 50 and not self.run_ended
        if eligible:
            self.victory_eligible = True
            self.victory_track = track
            _log_victory_eligible(logger, turn, track, opposing_value, self._progression_tracks, system_id)
        if self.victory_eligible:
            active_track = self.victory_track
            if active_track is not None:
                active_opposing = _opposing_track(active_track)
                active_value = self._progression_tracks[active_track]
                active_opposing_value = self._progression_tracks[active_opposing]
                if active_value < 100 or active_opposing_value > 50:
                    reason = _track_dropped_reason(active_value, active_opposing_value)
                    self.victory_eligible = False
                    self.victory_track = None
                    _log_victory_revoked(
                        logger,
                        turn,
                        active_track,
                        active_opposing_value,
                        self._progression_tracks,
                        reason,
                        system_id,
                    )

    def confiscate(self, sku: str, amount: int | None) -> int:
        if sku not in self._holdings or self._holdings[sku] <= 0:
            return 0
        if amount is None or amount < 0:
            confiscated = self._holdings[sku]
            self._holdings[sku] = 0
            return confiscated
        confiscated = min(self._holdings[sku], amount)
        self._holdings[sku] -= confiscated
        return confiscated

    def reputation(self) -> int:
        return self._reputation

    def adjust_reputation(self, delta: int) -> None:
        self._reputation += delta

    def get_reputation(self, system_id: str) -> int:
        return self._reputation_by_system.get(system_id, 50)

    def set_reputation(self, system_id: str, value: int) -> None:
        self._reputation_by_system[system_id] = max(1, min(100, value))

    def get_heat(self, system_id: str) -> int:
        return self._heat_by_system.get(system_id, 0)

    def set_heat(self, system_id: str, value: int) -> None:
        self._heat_by_system[system_id] = max(0, min(100, value))

    def has_warrant(self, system_id: str) -> bool:
        return self._warrants_by_system.get(system_id, False)

    def set_warrant(self, system_id: str, value: bool) -> None:
        self._warrants_by_system[system_id] = value

    def get_fines(self, system_id: str) -> int:
        return self._fines_by_system.get(system_id, 0)

    def add_fines(self, system_id: str, amount: int) -> None:
        if amount < 0:
            raise ValueError("Fines amount must be >= 0.")
        self._fines_by_system[system_id] = self.get_fines(system_id) + amount

    def pay_fines(self, system_id: str, amount: int) -> None:
        if amount < 0:
            raise ValueError("Payment amount must be >= 0.")
        remaining = max(0, self.get_fines(system_id) - amount)
        self._fines_by_system[system_id] = remaining

    def has_license(self, system_id: str, sku_or_category: str) -> bool:
        return self._licenses_by_system.get(system_id, {}).get(sku_or_category, False)

    def can_purchase_license(self, system_id: str) -> bool:
        reputation = self.get_reputation(system_id)
        return 81 <= reputation <= 100

    def license_summary_count(self, system_id: str) -> int:
        return len(self._licenses_by_system.get(system_id, {}))

    def profile_view(self) -> list[str]:
        lines: list[str] = []
        systems = set(self._reputation_by_system) | set(self._heat_by_system) | set(self._warrants_by_system)
        systems |= set(self._fines_by_system) | set(self._licenses_by_system)
        for system_id in sorted(systems):
            rep = self.get_reputation(system_id)
            heat = self.get_heat(system_id)
            warrant = self.has_warrant(system_id)
            fines = self.get_fines(system_id)
            licenses = self.license_summary_count(system_id)
            rep_band = _band_label(rep)
            heat_band = _band_label(max(1, heat))
            lines.append(
                f"{system_id} rep={rep}({rep_band}) heat={heat}({heat_band}) "
                f"warrant={warrant} fines={fines} licenses={licenses}"
            )
        return lines


def _band_label(value: int) -> str:
    if value <= 20:
        return "Very Low"
    if value <= 40:
        return "Low"
    if value <= 60:
        return "Neutral"
    if value <= 80:
        return "High"
    return "Very High"


def _opposing_track(track: str) -> str:
    pairs = {
        "trust": "notoriety",
        "notoriety": "trust",
        "entrepreneur": "criminal",
        "criminal": "entrepreneur",
        "law": "outlaw",
        "outlaw": "law",
    }
    return pairs[track]


def _tracks_snapshot_text(tracks: dict[str, int]) -> str:
    return ",".join(f"{key}={tracks[key]}" for key in sorted(tracks))


def _track_dropped_reason(new_value: int, opposing_value: int) -> str:
    if new_value < 100:
        return "track_dropped"
    return "opposing_track_exceeded" if opposing_value > 50 else "track_dropped"


def _bankruptcy_detected(credits: int, has_ship: bool, holdings: dict[str, int]) -> bool:
    if credits > 0:
        return False
    if has_ship:
        return False
    if any(count > 0 for count in holdings.values()):
        return False
    return True


def _log_victory_event(
    logger,
    turn: int,
    action: str,
    track: str,
    opposing_value: int,
    tracks: dict[str, int],
    reason: str | None = None,
    system_id: str | None = None,
) -> None:
    if logger is None:
        return
    if reason is None:
        state_change = (
            f"track={track} opposing_track_value={opposing_value} "
            f"tracks={_tracks_snapshot_text(tracks)} system_id={system_id}"
        )
    else:
        state_change = (
            f"track={track} opposing_track_value={opposing_value} reason={reason} "
            f"tracks={_tracks_snapshot_text(tracks)} system_id={system_id}"
        )
    logger.log(turn=turn, action=action, state_change=state_change)


def _log_victory_revoked(
    logger,
    turn: int,
    track: str,
    opposing_value: int,
    tracks: dict[str, int],
    reason: str,
    system_id: str | None = None,
) -> None:
    _log_victory_event(
        logger=logger,
        turn=turn,
        action="victory_eligibility_revoked",
        track=track,
        opposing_value=opposing_value,
        tracks=tracks,
        reason=reason,
        system_id=system_id,
    )


def _log_victory_eligible(
    logger,
    turn: int,
    track: str,
    opposing_value: int,
    tracks: dict[str, int],
    system_id: str | None = None,
) -> None:
    _log_victory_event(
        logger=logger,
        turn=turn,
        action="victory_eligible",
        track=track,
        opposing_value=opposing_value,
        tracks=tracks,
        reason=None,
        system_id=system_id,
    )


def _log_run_ended(logger, turn: int, reason: str, system_id: str | None = None) -> None:
    if logger is None:
        return
    logger.log(turn=turn, action="run_ended", state_change=f"reason={reason} system_id={system_id}")
