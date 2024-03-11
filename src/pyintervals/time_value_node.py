from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from itertools import filterfalse
from typing import Sequence

from more_itertools import batched
from sortedcontainers import SortedList

from pyintervals import Interval
from pyintervals.constants import TIME_ZERO


@dataclass(frozen=True)
class TimeValueNode:
    time_point: datetime
    __intervals: SortedList = field(default_factory=SortedList)

    @property
    def intervals(self) -> list[Interval]:
        return list(self.__intervals)

    @property
    def value(self) -> float:
        return sum(i.value for i in self.__intervals if not i.is_degenerate())

    def is_redundant(self) -> bool:
        return self.time_point > TIME_ZERO and not self.__intervals

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
        self.__intervals.add(interval)

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
    search_batch = list(filter(lambda n: not n.is_redundant(), nodes))

    while len(search_batch) > 1:
        remaining, redundant = [], []
        for first, second in batched(
            sorted(filter(lambda n: not n.is_redundant(), search_batch)), 2
        ):
            if first == second:
                remaining.append(first)
                redundant.append(second)
            else:
                remaining.extend([first, second])

        search_batch = remaining

        if not redundant:
            break

    return search_batch
