from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Iterable, Collection

from .interval import Interval


@dataclass(frozen=True)
class TimeValueIntervalNode:
    time_point: datetime
    __intervals: list[Interval] = field(default_factory=list)
    
    @property
    def intervals(self) -> list[Interval]:
        return list(self.__intervals)


@dataclass
class IntervalHandler:
    __intervals: list[Interval]
    __projection_graph: list[TimeValueIntervalNode]

    def __init__(self, intervals: Iterable[Interval] = []):
        self._initialize()
        self.add(intervals)
        
    def _initialize(self) -> None:
        self.__intervals = list()
        self.__projection_graph = list()

    @property
    def intervals(self) -> list[Interval]:
        return list(self.__intervals)

    def add(self, intervals: Iterable[Interval]) -> None:
        self.__intervals.extend(intervals)
        
    def remove(self, intervals: Collection[Interval]) -> None:
        self.__intervals = [i for i in self.__intervals if i not in intervals]
