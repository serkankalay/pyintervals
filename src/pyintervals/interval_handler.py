from __future__ import annotations

import itertools
import operator
from collections.abc import Callable, Collection, Iterable
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

import more_itertools
from sortedcontainers import SortedList

from .constants import TIME_ZERO
from .interval import Interval
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


def _operate(
    a: IntervalHandler,
    b: IntervalHandler,
    operator: Callable[[float, float], float],
) -> IntervalHandler:
    if not isinstance(b, IntervalHandler):
        raise TypeError(
            f"unsupported operand type(s) for {operator.__name__}: "
            f"'{type(a)}' and '{type(b)}'"
        )
    all_nodes = sorted(
        n.time_point
        for n in itertools.chain(a.projection_graph(), b.projection_graph())
    )

    return IntervalHandler(
        intervals=[
            Interval(
                start=start,
                end=end,
                value=operator(a.value_at_time(start), b.value_at_time(start)),
            )
            for start, end in itertools.pairwise(all_nodes)
        ],
        tz=a._tz,
    )


def _relevant_nodes(
    nodes: SortedList[TimeValueNode],
    interval: Interval,
) -> list[TimeValueNode]:
    return list(
        nodes.irange(
            TimeValueNode(interval.start),
            TimeValueNode(interval.end),
            inclusive=(True, True),
        )
    )


def _area_during_interval(
    handler: IntervalHandler, during: Interval
) -> timedelta:
    first_node_in_interval = TimeValueNode.clone(
        handler.node_at_time(during.start), during.start
    )
    last_node_in_interval = TimeValueNode.clone(
        handler.node_at_time(during.end), during.end
    )

    relevant_nodes = itertools.chain(
        [first_node_in_interval],
        _relevant_nodes(handler.projection_graph(), during),
        [last_node_in_interval],
    )

    return sum(
        (
            during.value * start.value * (end.time_point - start.time_point)
            for start, end in more_itertools.pairwise(relevant_nodes)
        ),
        start=timedelta(0),
    )


@dataclass
class IntervalHandler:
    __intervals: list[Interval]
    __projection_graph: SortedList[TimeValueNode]
    _tz: ZoneInfo | timezone | None

    def __init__(
        self,
        intervals: Iterable[Interval] = [],
        tz: ZoneInfo | timezone | None = None,
    ):
        self._initialize(tz)
        self.add(intervals)

    def _initialize(self, tz: ZoneInfo | timezone | None) -> None:
        self.__intervals = list()
        self.__projection_graph = SortedList(
            [TimeValueNode(time_point=TIME_ZERO.replace(tzinfo=tz))]
        )
        self._tz = tz

    @property
    def intervals(self) -> list[Interval]:
        return list(self.__intervals)

    def __add__(self, other: IntervalHandler) -> IntervalHandler:
        return _operate(self, other, operator=operator.add)

    def __iadd__(self, other: IntervalHandler) -> None:
        return self.add(other.intervals)

    def __sub__(self, other: IntervalHandler) -> IntervalHandler:
        return _operate(self, other, operator=operator.sub)

    def __isub__(self, other: IntervalHandler) -> None:
        return self.remove(other.intervals)

    def __mul__(self, other: IntervalHandler) -> IntervalHandler:
        return _operate(self, other, operator=operator.mul)

    def __imul__(self, other: IntervalHandler) -> IntervalHandler:
        raise NotImplementedError(
            f"unsupported operand type(s) for *=: "
            f"'{type(self)}' and '{type(other)}'"
        )

    def __truediv__(self, other: IntervalHandler) -> IntervalHandler:
        return _operate(self, other, operator=operator.truediv)

    def __itruediv__(self, other: IntervalHandler) -> IntervalHandler:
        raise NotImplementedError(
            f"unsupported operand type(s) for /=: "
            f"'{type(self)}' and '{type(other)}'"
        )

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

    def projection_graph(self) -> SortedList[TimeValueNode]:
        return SortedList(self.__projection_graph)

    def node_at_time(self, when: datetime) -> TimeValueNode:
        return _active_node_at_time(self.__projection_graph, when)

    def value_at_time(self, when: datetime) -> float:
        return _active_node_at_time(self.__projection_graph, when).value

    def get_area(self, during: Interval) -> timedelta:
        return _area_during_interval(self, during)
