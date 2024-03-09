from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from itertools import filterfalse

from pyintervals import Interval


@dataclass(frozen=True)
class TimeValueNode:
    time_point: datetime
    __intervals: list[Interval] = field(default_factory=list)

    @property
    def intervals(self) -> list[Interval]:
        return list(self.__intervals)

    @property
    def value(self) -> float:
        return sum(i.value for i in self.__intervals if not i.is_degenerate())

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, TimeValueNode):
            raise NotImplementedError
        return (
            self.time_point == other.time_point
            and self.__intervals == other.__intervals
        )

    def __ne__(self, other: object) -> bool:
        return not (self == other)

    def __lt__(self, other: object) -> bool:
        if not isinstance(other, TimeValueNode):
            raise NotImplementedError
        return self.time_point < other.time_point

    def __le__(self, other: object) -> bool:
        if not isinstance(other, TimeValueNode):
            raise NotImplementedError
        return self.time_point <= other.time_point

    def __gt__(self, other: object) -> bool:
        if not isinstance(other, TimeValueNode):
            raise NotImplementedError
        return self.time_point > other.time_point

    def __ge__(self, other: object) -> bool:
        if not isinstance(other, TimeValueNode):
            raise NotImplementedError
        return self.time_point >= other.time_point

    def _add_interval(self, interval: Interval) -> None:
        self.__intervals.append(interval)

    @staticmethod
    def clone(
        given: TimeValueNode, to_time: datetime | None = None
    ) -> TimeValueNode:
        return (
            TimeValueNode(given.time_point, list(given.__intervals))
            if not to_time
            else TimeValueNode(
                to_time,
                list(
                    filterfalse(
                        lambda x: x.is_degenerate(),
                        given.__intervals,
                    )
                ),
            )
        )
