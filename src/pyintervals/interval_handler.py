from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Collection, Iterable, Sequence
from zoneinfo import ZoneInfo

from sortedcontainers import SortedList

from .constants import TIME_ZERO
from .interval import Interval, intersection
from .search import weak_predecessor
from .time_value_node import TimeValueNode, _simplify


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


def _relevant_nodes(
    nodes: SortedList[TimeValueNode],
    interval: Interval,
) -> list[TimeValueNode]:
    return [
        n
        for n in nodes.islice(
            start=nodes.index(_active_node_at_time(nodes, interval.start))
        )
        if n.time_point < interval.end
    ]


def _area_during_interval(
    handler: IntervalHandler,
    during: Interval,
) -> timedelta:
    return sum(
        (
            interval.value * during.value * overlap.duration()
            for interval in handler.intervals
            if (overlap := intersection(during, interval))
        ),
        start=timedelta(0),
    )


@dataclass
class IntervalHandler:
    __intervals: list[Interval]
    __projection_graph: SortedList[TimeValueNode]

    def __init__(
        self, intervals: Iterable[Interval] = [], tz: ZoneInfo | None = None
    ):
        self._initialize(tz)
        self.add(intervals)

    def _initialize(self, tz: ZoneInfo | None) -> None:
        self.__intervals = list()
        self.__projection_graph = SortedList(
            [TimeValueNode(time_point=TIME_ZERO.replace(tzinfo=tz))]
        )

    @property
    def intervals(self) -> list[Interval]:
        return list(self.__intervals)

    def add(self, intervals: Iterable[Interval]) -> None:
        self.__intervals.extend(intervals)
        for interval in intervals:
            _make_range(self.__projection_graph, interval)
            for node in _relevant_nodes(self.__projection_graph, interval):
                node._add_interval(interval)

    def remove(self, intervals: Collection[Interval]) -> None:
        self.__intervals = [i for i in self.__intervals if i not in intervals]

        for interval in intervals:
            for node in _relevant_nodes(self.__projection_graph, interval):
                node._remove_interval(interval)

        self.__projection_graph = SortedList(
            _simplify(self.__projection_graph)
        )

    def projection_graph(self) -> Sequence[TimeValueNode]:
        return list(self.__projection_graph)

    def node_at_time(self, when: datetime) -> TimeValueNode:
        return _active_node_at_time(self.__projection_graph, when)

    def value_at_time(self, when: datetime) -> float:
        return _active_node_at_time(self.__projection_graph, when).value

    def get_area(self, during: Interval) -> timedelta:
        return _area_during_interval(self, during)
