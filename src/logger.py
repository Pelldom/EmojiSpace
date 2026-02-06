from dataclasses import dataclass


@dataclass(frozen=True)
class LogEntry:
    turn: int
    version: str
    action: str
    state_change: str

    def format_line(self) -> str:
        return f"[v{self.version}][turn {self.turn}] action={self.action} change={self.state_change}"


class Logger:
    def __init__(self, version: str) -> None:
        self._version = version

    @property
    def version(self) -> str:
        return self._version

    def log(self, turn: int, action: str, state_change: str) -> None:
        entry = LogEntry(
            turn=turn,
            version=self._version,
            action=action,
            state_change=state_change,
        )
        print(entry.format_line())
