from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Collection, Iterable, Sequence

from sortedcontainers import SortedList

from .interval import Interval
from .search import weak_predecessor
from .time_value_node import TimeValueNode

# Unix epoch
_TIME_ZERO: datetime = datetime(1970, 1, 1)


def _to_new_node(
    active_node: TimeValueNode | None,
    time_point: datetime,
) -> TimeValueNode | None:
    if active_node is None:
        return TimeValueNode(time_point)

    return (
        TimeValueNode.clone(active_node, time_point)
        if active_node.time_point < time_point
        else None
    )


def _active_node_at_time(
    nodes: SortedList[TimeValueNode], when: datetime
) -> TimeValueNode:
    if node := weak_predecessor(nodes, TimeValueNode(when)):
        return node
    else:
        raise RuntimeError("Could not find active node at time.")


def _make_range(
    nodes: SortedList[TimeValueNode], new_interval: Interval
) -> None:
    for t in {new_interval.start, new_interval.end}:
        if new_node := _to_new_node(
            active_node=_active_node_at_time(nodes, t),
            time_point=t,
        ):
            nodes.add(new_node)


@dataclass
class IntervalHandler:
    __intervals: list[Interval]
    __projection_graph: SortedList[TimeValueNode]

    def __init__(self, intervals: Iterable[Interval] = []):
        self._initialize()
        self.add(intervals)

    def _initialize(self) -> None:
        self.__intervals = list()
        self.__projection_graph = SortedList(
            [TimeValueNode(time_point=_TIME_ZERO)]
        )

    @property
    def intervals(self) -> list[Interval]:
        return list(self.__intervals)

    def add(self, intervals: Iterable[Interval]) -> None:
        self.__intervals.extend(intervals)
        for interval in intervals:
            _make_range(self.__projection_graph, interval)
            for node in self.__projection_graph.irange(
                TimeValueNode(interval.start),
                TimeValueNode(interval.end),
                inclusive=(True, True if interval.is_degenerate() else False),
            ):
                node._add_interval(interval)

    def remove(self, intervals: Collection[Interval]) -> None:
        self.__intervals = [i for i in self.__intervals if i not in intervals]
        # TODO: manage interval handler logic as well.

    def projection_graph(self) -> Sequence[TimeValueNode]:
        return list(self.__projection_graph)

    def node_at_time(self, when: datetime) -> TimeValueNode:
        return _active_node_at_time(self.__projection_graph, when)

    def value_at_time(self, when: datetime) -> float:
        return _active_node_at_time(self.__projection_graph, when).value
