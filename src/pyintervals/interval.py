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

    def overlaps_with(self, other: Interval) -> bool:
        return overlaps(self, other)


def overlaps(interval: Interval, other: Interval) -> bool:

    # If both are degenerate, then we should check whether they're at the exact same time.
    if interval.is_degenerate() and other.is_degenerate():
        return interval.start == other.start

    # If only 1 is degenerate, then we check that point is included in the other.
    if interval.is_degenerate():
        return other.start <= interval.start < other.end

    if other.is_degenerate():
        return interval.start <= other.start < interval.end

    # We have 2 non-degenerate intervals. We take them in order and check whether they're exclusive.
    if interval.start <= other.start:
        first, second = interval, other
    else:
        first, second = other, interval

    return second.start < first.end
