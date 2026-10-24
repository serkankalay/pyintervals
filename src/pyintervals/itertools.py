from __future__ import annotations

from collections.abc import Callable, Iterable, Iterator
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Protocol, cast, overload
from zoneinfo import ZoneInfo

from .interval import Interval
from .interval_handler import IntervalHandler


class HasInterval(Protocol):
    @property
    def interval(self) -> Interval: ...


def _by_interval_attribute(item: HasInterval) -> Interval:
    return item.interval


def _sweep[T](items: Iterable[T], key: Callable[[T], Interval]) -> Iterator[list[T]]:
    """Streams groups of connected items out of ``items``, which must be ordered by ``start``."""
    group: list[T] = []
    group_end: datetime | None = None
    previous_start: datetime | None = None

    for item in items:
        interval = key(item)
        if interval.is_degenerate:
            continue

        if previous_start is not None and interval.start < previous_start:
            raise ValueError("Items must be ordered by start when `assume_sorted=True`.")
        previous_start = interval.start

        if group_end is not None and interval.start > group_end:
            yield group
            group = []
            group_end = None

        group.append(item)
        group_end = interval.end if group_end is None else max(group_end, interval.end)

    if group:
        yield group


@dataclass(frozen=True, order=True)
class _OwnedInterval[T](Interval):
    """An interval that remembers the item it was made for, so the handler's nodes lead back to the items."""

    owner: T = field(kw_only=True, compare=False, repr=False)


def _via_handler[T](items: Iterable[T], key: Callable[[T], Interval]) -> Iterator[list[T]]:
    """Groups connected items out of ``items`` in any order, by walking an ``IntervalHandler``'s graph."""
    intervals: list[_OwnedInterval[T]] = []
    for item in items:
        interval = key(item)
        if not interval.is_degenerate:
            # The handler sums values, so a value of 1 makes a node's value the number of active items.
            intervals.append(_OwnedInterval(interval.start, interval.end, value=1, owner=item))

    if not intervals:
        return

    handler = IntervalHandler(tz=cast("ZoneInfo | timezone | None", intervals[0].start.tzinfo))
    handler.add(intervals)

    group: list[T] = []
    for node in handler.projection_graph:
        if node.value > 0:
            # `starting_intervals` has one entry per item starting here, in input order.
            group.extend(cast("_OwnedInterval[T]", i).owner for i in node.starting_intervals)
        elif group:
            yield group
            group = []

    if group:
        yield group


@overload
def group_connected[T: HasInterval](of: Iterable[T], *, assume_sorted: bool = False) -> Iterator[list[T]]: ...


@overload
def group_connected[
    T
](of: Iterable[T], *, key: Callable[[T], Interval], assume_sorted: bool = False) -> Iterator[list[T]]: ...


def group_connected[
    T
](of: Iterable[T], *, key: Callable[[T], Interval] | None = None, assume_sorted: bool = False,) -> Iterator[list[T]]:
    """Groups connected items together, yielding each group as a list of the original items.

    Items are connected when their intervals overlap *or touch*: ``[a, b)`` and ``[b, c)``
    belong to the same group, while a gap of any positive length separates groups. Groups are
    yielded in start order, and items within a group are ordered by ``start`` with ties kept
    in input order.

    Degenerate intervals (``start == end``) carry no timespan, so they are dropped and never yielded.

    Args:
        of: The items to group.
        key: Returns the interval of an item. Defaults to reading the item's ``interval`` attribute.
        assume_sorted: Declares that ``of`` is ordered by ``start``, which lets groups be streamed
            lazily. A violation raises ``ValueError`` once it is encountered.
    """
    # Without `key`, the overloads guarantee `T` has an `interval` attribute.
    resolved_key = key if key is not None else cast(Callable[[T], Interval], _by_interval_attribute)

    return _sweep(of, resolved_key) if assume_sorted else _via_handler(of, resolved_key)
