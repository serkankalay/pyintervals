from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from itertools import chain, filterfalse
from typing import Sequence

from sortedcontainers import SortedList

from pyintervals import Interval
from pyintervals.constants import TIME_ZERO
from pyintervals.interval import contains_point


@dataclass
class TimeValueNode:
    time_point: datetime
    __intervals: SortedList[Interval] = field(default_factory=SortedList)
    __starting_intervals: SortedList[Interval] = field(default_factory=SortedList)
    __ending_intervals: SortedList[Interval] = field(default_factory=SortedList)
    __value: float = 0.0

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
        return self.__value

    def is_redundant(self) -> bool:
        return self.time_point > TIME_ZERO and not self.__starting_intervals and not self.__ending_intervals

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, TimeValueNode):
            raise NotImplementedError
        return self.time_point == other.time_point and self.__intervals == other.__intervals

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

    def __add(self, interval: Interval) -> None:
        self.__intervals.add(interval)
        if not interval.is_degenerate:
            self.__value += interval.value

    def __remove(self, interval: Interval) -> None:
        self.__intervals.remove(interval)
        if not interval.is_degenerate:
            self.__value -= interval.value

    def _add_interval(self, interval: Interval) -> None:
        if interval.end == self.time_point:
            self.__ending_intervals.add(interval)
            if interval.is_degenerate:
                self.__add(interval)
        elif not interval.is_degenerate:
            self.__add(interval)

        if interval.start == self.time_point:
            self.__starting_intervals.add(interval)

    def _remove_interval(self, interval: Interval) -> None:
        if contains_point(interval, self.time_point):
            self.__remove(interval)
        if interval.start == self.time_point:
            self.__starting_intervals.remove(interval)
        if interval.end == self.time_point:
            self.__ending_intervals.remove(interval)

    def copy(self, to: datetime | None) -> TimeValueNode:
        if to is None or to == self.time_point:
            return TimeValueNode.clone(self)
        else:
            return TimeValueNode(
                to,
                SortedList(
                    filterfalse(
                        lambda x: x.is_degenerate,
                        self.__intervals,
                    )
                ),
                SortedList(
                    filter(
                        lambda x: x.start == to,
                        chain(self.__intervals, self.__ending_intervals),
                    )
                ),
                SortedList(
                    filter(
                        lambda x: x.end == to,
                        chain(self.__intervals, self.__ending_intervals),
                    )
                ),
                self.__value,
            )

    @staticmethod
    def clone(given: TimeValueNode) -> TimeValueNode:
        return TimeValueNode(
            given.time_point,
            SortedList(given.__intervals),
            SortedList(given.__starting_intervals),
            SortedList(given.__ending_intervals),
            given.__value,
        )


def _simplify(nodes: Sequence[TimeValueNode]) -> list[TimeValueNode]:
    return list(filterfalse(lambda n: n.is_redundant(), nodes))
