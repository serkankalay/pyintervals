from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Iterable

from pyintervals import Interval


@dataclass(frozen=True)
class TimeValueNode:
    time_point: datetime
    __intervals: list[Interval] = field(default_factory=list)

    @property
    def intervals(self) -> list[Interval]:
        return list(self.__intervals)

    def __eq__(self, other: TimeValueNode) -> bool:
        return (
            self.time_point == other.time_point
            and self.__intervals == other.__intervals
        )

    def __ne__(self, other: TimeValueNode) -> bool:
        return not (self == other)

    def __lt__(self, other: TimeValueNode) -> bool:
        return self.time_point < other.time_point

    def __le__(self, other: TimeValueNode) -> bool:
        return self.time_point <= other.time_point

    def __gt__(self, other: TimeValueNode) -> bool:
        return self.time_point > other.time_point

    def __ge__(self, other: TimeValueNode) -> bool:
        return self.time_point >= other.time_point

    def _add_intervals(self, intervals: Iterable[Interval]) -> None:
        self.__intervals.extend(intervals)

    @staticmethod
    def clone(
        given: TimeValueNode, to_time: datetime | None = None
    ) -> TimeValueNode:
        return (
            TimeValueNode(given.time_point, given.__intervals)
            if not to_time
            else TimeValueNode(to_time, given.__intervals)
        )
