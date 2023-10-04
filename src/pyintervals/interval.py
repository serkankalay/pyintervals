from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta


@dataclass(frozen=True)
class Interval:
    start: datetime
    end: datetime

    def __post_init__(self) -> None:
        if self.start > self.end:
            raise RuntimeError(
                f"Invalid interval: {self.end=} is earlier than {self.start=}"
            )

    def is_degenerate(self) -> bool:
        return self.start == self.end
    
    def duration(self) -> timedelta:
        return self.end - self.start
