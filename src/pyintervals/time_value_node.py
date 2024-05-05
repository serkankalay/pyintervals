from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from itertools import filterfalse
from typing import Sequence

from sortedcontainers import SortedList

from pyintervals import Interval
from pyintervals.constants import TIME_ZERO
from pyintervals.interval import contains_point


@dataclass(frozen=True)
class TimeValueNode:
    time_point: datetime
    __intervals: SortedList[Interval] = field(default_factory=SortedList)
    __starting_intervals: SortedList[Interval] = field(
        default_factory=SortedList
    )
    __ending_intervals: SortedList[Interval] = field(
        default_factory=SortedList
    )

    @property
    def intervals(self) -> list[Interval]:
        return list(self.__intervals)

    @property
    def starting_intervals(self) -> list[Interval]:
        return list(self.__starting_intervals)

    @property
    def ending_intervals(self) -> list[Interval]:
        return list(self.__ending_intervals)

    @property
    def value(self) -> float:
        return sum(i.value for i in self.__intervals if not i.is_degenerate())

    def is_redundant(self) -> bool:
        return (
            self.time_point > TIME_ZERO
            and not self.__starting_intervals
            and not self.__ending_intervals
        )

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
        if interval.end == self.time_point:
            self.__ending_intervals.add(interval)
            if interval.is_degenerate():
                self.__intervals.add(interval)
        elif not interval.is_degenerate():
            self.__intervals.add(interval)

        if interval.start == self.time_point:
            self.__starting_intervals.add(interval)

    def _remove_interval(self, interval: Interval) -> None:
        if contains_point(interval, self.time_point):
            self.__intervals.remove(interval)
        if interval.start == self.time_point:
            self.__starting_intervals.remove(interval)
        if interval.end == self.time_point:
            self.__ending_intervals.remove(interval)

    @staticmethod
    def clone(
        given: TimeValueNode, to_time: datetime | None = None
    ) -> TimeValueNode:
        return (
            TimeValueNode(given.time_point, SortedList(given.__intervals))
            if not to_time
            else TimeValueNode(
                to_time,
                SortedList(
                    filterfalse(
                        lambda x: x.is_degenerate(),
                        given.__intervals,
                    )
                ),
            )
        )


def _simplify(nodes: Sequence[TimeValueNode]) -> list[TimeValueNode]:
    return list(filterfalse(lambda n: n.is_redundant(), nodes))
