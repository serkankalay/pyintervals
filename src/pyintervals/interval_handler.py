from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Iterable, Collection, Sequence

from .interval import Interval
from .time_value_node import TimeValueNode

# Unix epoch
_TIME_ZERO: datetime = datetime(1970, 1, 1)


@dataclass
class IntervalHandler:
    __intervals: list[Interval]
    __projection_graph: list[TimeValueNode]

    def __init__(self, intervals: Iterable[Interval] = []):
        self._initialize()
        self.add(intervals)

    def _initialize(self) -> None:
        self.__intervals = list()
        self.__projection_graph = [TimeValueNode(time_point=_TIME_ZERO)]

    @property
    def intervals(self) -> list[Interval]:
        return list(self.__intervals)

    def add(self, intervals: Iterable[Interval]) -> None:
        self.__intervals.extend(intervals)

    def remove(self, intervals: Collection[Interval]) -> None:
        self.__intervals = [i for i in self.__intervals if i not in intervals]

    def projection_graph(self) -> Sequence[TimeValueNode]:
        return list(self.__projection_graph)
