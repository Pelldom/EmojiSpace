class TimeEngine:
    def __init__(self) -> None:
        self._turn = 0

    @property
    def current_turn(self) -> int:
        return self._turn

    def advance(self) -> int:
        self._turn += 1
        return self._turn
