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

    return TimeValueNode.copy(active_node, time_point) if active_node.time_point < time_point else None


def _active_node_at_time(nodes: SortedList[TimeValueNode], when: datetime) -> TimeValueNode:
    if node := weak_predecessor(nodes, TimeValueNode(when)):
        return node
    else:
        raise RuntimeError("Could not find active node at time.")


def _make_range(nodes: SortedList[TimeValueNode], new_interval: Interval) -> None:
    for t in {new_interval.start, new_interval.end}:
        if new_node := _to_new_node(
            active_node=_active_node_at_time(nodes, t),
            time_point=t,
        ):
            nodes.add(new_node)


def _operate(
    a: IntervalHandler,
    b: IntervalHandler,
    operand: Callable[[float, float], float],
) -> IntervalHandler:
    """Only call this function through the methods bound to `IntervalHandler`."""
    if not isinstance(b, IntervalHandler):
        raise TypeError(f"unsupported operand type(s) for {operand.__name__}: " f"'{type(a)}' and '{type(b)}'")
    change_times = set(n.time_point for n in itertools.chain(a.projection_graph, b.projection_graph))

    return IntervalHandler(
        intervals=[
            Interval(
                start=start,
                end=end,
                value=operand(a.value_at_time(start), b.value_at_time(start)),
            )
            for start, end in more_itertools.pairwise(sorted(change_times))
        ],
        tz=a._tz,
    )


def _relevant_nodes(
    nodes: SortedList[TimeValueNode],
    interval: Interval,
) -> list[TimeValueNode]:
    if interval.is_degenerate:
        return [_active_node_at_time(nodes, interval.start)]
    else:
        return [
            n
            for n in nodes.islice(start=nodes.index(_active_node_at_time(nodes, interval.start)))
            if n.time_point <= interval.end
        ]


def _area_during_interval(handler: IntervalHandler, during: Interval) -> timedelta:
    first_node_in_interval = handler.node_at_time(during.start).copy(during.start)
    last_node_in_interval = handler.node_at_time(during.end).copy(during.end)

    relevant_nodes = itertools.chain(
        [first_node_in_interval],
        # ↓ Everything except the first node, since it's not ↓
        # ↓ necessarily part of the interval ↓
        _relevant_nodes(handler.projection_graph, during)[1:],
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
    __first_negative: TimeValueNode | None = None

    def __init__(
        self,
        intervals: Iterable[Interval] = [],
        tz: ZoneInfo | timezone | None = None,
    ):
        self._initialize(tz)
        self.add(intervals)

    def _initialize(self, tz: ZoneInfo | timezone | None) -> None:
        self.__intervals = list()
        self.__projection_graph = SortedList([TimeValueNode(time_point=TIME_ZERO.replace(tzinfo=tz))])
        self._tz = tz

    @property
    def intervals(self) -> list[Interval]:
        return list(self.__intervals)

    def __add__(self, other: IntervalHandler) -> IntervalHandler:
        return _operate(self, other, operand=operator.add)

    def __iadd__(self, other: IntervalHandler) -> None:
        simplified = _operate(self, other, operand=operator.add)
        self._initialize(tz=self._tz)
        self.add(intervals=simplified.intervals)
        return None

    def __sub__(self, other: IntervalHandler) -> IntervalHandler:
        return _operate(self, other, operand=operator.sub)

    def __isub__(self, other: IntervalHandler) -> None:
        simplified = _operate(self, other, operand=operator.sub)
        self._initialize(tz=self._tz)
        self.add(intervals=simplified.intervals)
        return None

    def __mul__(self, other: IntervalHandler) -> IntervalHandler:
        return _operate(self, other, operand=operator.mul)

    def __imul__(self, other: IntervalHandler) -> None:
        simplified = _operate(self, other, operand=operator.mul)
        self._initialize(tz=self._tz)
        self.add(intervals=simplified.intervals)
        return None

    def __truediv__(self, other: IntervalHandler) -> IntervalHandler:
        return _operate(self, other, operand=operator.truediv)

    def __itruediv__(self, other: IntervalHandler) -> None:
        simplified = _operate(self, other, operand=operator.truediv)
        self._initialize(tz=self._tz)
        self.add(intervals=simplified.intervals)
        return None

    def add(self, intervals: Iterable[Interval]) -> None:
        """Adds without simplifying the intervals."""
        self.__intervals.extend(intervals)
        for interval in intervals:
            _make_range(self.__projection_graph, interval)
            for node in _relevant_nodes(self.__projection_graph, interval):
                node._add_interval(interval)
                self._try_refresh_first_negative_point(node)

    def remove(self, intervals: Collection[Interval]) -> None:
        """Removes without simplifying the intervals."""
        self.__intervals = [i for i in self.__intervals if i not in intervals]

        for interval in intervals:
            for node in _relevant_nodes(self.__projection_graph, interval):
                node._remove_interval(interval)
                self._try_refresh_first_negative_point(node)

        self.__projection_graph = SortedList(_simplify(self.__projection_graph))
        if self.__first_negative is None:
            self.__first_negative = next((n for n in self.__projection_graph if n.value < 0), None)

    def clone(self) -> IntervalHandler:
        cloned = IntervalHandler(tz=self._tz)
        cloned.__intervals = list(self.__intervals)
        cloned.__projection_graph = SortedList(TimeValueNode.clone(given=node) for node in self.__projection_graph)
        cloned.__first_negative = (
            None
            if self.__first_negative is None
            else cloned.__projection_graph[self.__projection_graph.index(self.__first_negative)]
        )
        return cloned

    def _try_refresh_first_negative_point(self, node: TimeValueNode) -> None:
        if node.value < 0:
            if self.__first_negative is None or node.time_point < self.__first_negative.time_point:
                self.__first_negative = node

        if self.__first_negative and self.__first_negative.value >= 0:
            self.__first_negative = None

    @property
    def projection_graph(self) -> SortedList[TimeValueNode]:
        return SortedList(self.__projection_graph)

    def node_at_time(self, when: datetime) -> TimeValueNode:
        return _active_node_at_time(self.__projection_graph, when)

    def value_at_time(self, when: datetime) -> float:
        return _active_node_at_time(self.__projection_graph, when).value

    def get_area(self, during: Interval) -> timedelta:
        return _area_during_interval(self, during)

    @property
    def first_negative_point(self) -> TimeValueNode | None:
        return self.__first_negative
