from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Collection

from .interval import Interval


@dataclass()
class IntervalHandler:
    __intervals: list[Interval]

    def __init__(self, intervals: Iterable[Interval] = []):
        self.__intervals = list(intervals)

    @property
    def intervals(self) -> list[Interval]:
        return list(self.__intervals)

    def add(self, intervals: Iterable[Interval]) -> None:
        self.__intervals.extend(intervals)
        
    def remove(self, intervals: Collection[Interval]) -> None:
        self.__intervals = [i for i in self.__intervals if i not in intervals]
