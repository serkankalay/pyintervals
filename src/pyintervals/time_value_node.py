from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime

from pyintervals import Interval


@dataclass(frozen=True)
class TimeValueNode:
    time_point: datetime
    __intervals: list[Interval] = field(default_factory=list)

    @property
    def intervals(self) -> list[Interval]:
        return list(self.__intervals)

    def __eq__(self, other: TimeValueNode) -> bool:
        return self.time_point == other.time_point

    def __ne__(self, other: TimeValueNode) -> bool:
        return self.time_point != other.time_point

    def __lt__(self, other: TimeValueNode) -> bool:
        return self.time_point < other.time_point

    def __le__(self, other: TimeValueNode) -> bool:
        return self.time_point <= other.time_point

    def __gt__(self, other: TimeValueNode) -> bool:
        return self.time_point > other.time_point

    def __ge__(self, other: TimeValueNode) -> bool:
        return self.time_point >= other.time_point
