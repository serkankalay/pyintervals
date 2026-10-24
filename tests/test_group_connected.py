from __future__ import annotations

import random
from collections.abc import Iterator
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

import pytest

from pyintervals import Interval, group_connected
from tests.helpers import THE_DATE


@dataclass(frozen=True)
class Task:
    name: str
    interval: Interval


@pytest.fixture(params=[True, False], ids=["sweep", "handler"])
def assume_sorted(request: pytest.FixtureRequest) -> bool:
    """Runs a test once per engine. Every input used with this fixture is already ordered by start."""
    return bool(request.param)


def at(hours: int) -> datetime:
    return THE_DATE + timedelta(hours=hours)


def task(name: str, start: int, end: int) -> Task:
    return Task(name, Interval(at(start), at(end)))


def names(groups: Iterator[list[Task]]) -> list[list[str]]:
    return [[t.name for t in group] for group in groups]


def test_empty_input_yields_nothing(assume_sorted: bool) -> None:
    assert list(group_connected([], assume_sorted=assume_sorted)) == []


def test_single_item_is_its_own_group(assume_sorted: bool) -> None:
    a = task("a", 0, 1)
    assert list(group_connected([a], assume_sorted=assume_sorted)) == [[a]]


def test_overlapping_items_are_grouped(assume_sorted: bool) -> None:
    items = [task("a", 0, 5), task("b", 3, 8)]
    assert names(group_connected(items, assume_sorted=assume_sorted)) == [["a", "b"]]


def test_touching_items_are_grouped(assume_sorted: bool) -> None:
    items = [task("a", 0, 5), task("b", 5, 8)]
    assert names(group_connected(items, assume_sorted=assume_sorted)) == [["a", "b"]]


def test_gap_separates_groups(assume_sorted: bool) -> None:
    items = [task("a", 0, 5), task("b", 6, 8)]
    assert names(group_connected(items, assume_sorted=assume_sorted)) == [["a"], ["b"]]


def test_chain_of_overlaps_is_one_group(assume_sorted: bool) -> None:
    items = [task("a", 0, 3), task("b", 2, 5), task("c", 4, 7)]
    assert names(group_connected(items, assume_sorted=assume_sorted)) == [["a", "b", "c"]]


def test_nested_item_does_not_shrink_group_end(assume_sorted: bool) -> None:
    # `b` ends before `a`, so `c` must still connect through `a`'s end.
    items = [task("a", 0, 10), task("b", 1, 2), task("c", 9, 12)]
    assert names(group_connected(items, assume_sorted=assume_sorted)) == [["a", "b", "c"]]


def test_identical_intervals_on_distinct_objects_are_kept_in_input_order(assume_sorted: bool) -> None:
    items = [task("a", 0, 5), task("b", 0, 5), task("c", 0, 5)]
    assert names(group_connected(items, assume_sorted=assume_sorted)) == [["a", "b", "c"]]


def test_multiple_groups_come_out_in_start_order(assume_sorted: bool) -> None:
    items = [task("a", 0, 2), task("b", 1, 3), task("c", 10, 12), task("d", 20, 25), task("e", 24, 26)]
    assert names(group_connected(items, assume_sorted=assume_sorted)) == [["a", "b"], ["c"], ["d", "e"]]


def test_degenerate_items_are_dropped(assume_sorted: bool) -> None:
    items = [task("a", 0, 5), task("point-inside", 2, 2), task("point-touching", 5, 5), task("b", 5, 8)]
    assert names(group_connected(items, assume_sorted=assume_sorted)) == [["a", "b"]]


def test_isolated_degenerate_item_is_dropped(assume_sorted: bool) -> None:
    items = [task("a", 0, 2), task("point", 4, 4), task("b", 6, 8)]
    assert names(group_connected(items, assume_sorted=assume_sorted)) == [["a"], ["b"]]


def test_only_degenerate_items_yield_nothing(assume_sorted: bool) -> None:
    items = [task("p", 1, 1), task("q", 1, 1)]
    assert list(group_connected(items, assume_sorted=assume_sorted)) == []


def test_key_function_is_used_for_arbitrary_shapes(assume_sorted: bool) -> None:
    items = [("a", at(0), at(5)), ("b", at(5), at(8)), ("c", at(20), at(21))]
    groups = group_connected(items, key=lambda i: Interval(i[1], i[2]), assume_sorted=assume_sorted)
    assert [[i[0] for i in g] for g in groups] == [["a", "b"], ["c"]]


def test_original_objects_are_yielded(assume_sorted: bool) -> None:
    a, b = task("a", 0, 5), task("b", 5, 8)
    (group,) = group_connected([a, b], assume_sorted=assume_sorted)
    assert group[0] is a and group[1] is b


def test_timezone_aware_items_are_supported(assume_sorted: bool) -> None:
    tz = timezone.utc
    a = Task("a", Interval(at(0).replace(tzinfo=tz), at(5).replace(tzinfo=tz)))
    b = Task("b", Interval(at(5).replace(tzinfo=tz), at(8).replace(tzinfo=tz)))
    assert names(group_connected([a, b], assume_sorted=assume_sorted)) == [["a", "b"]]


def test_is_lazy_when_sorted() -> None:
    consumed: list[str] = []

    def source() -> Iterator[Task]:
        for t in [task("a", 0, 1), task("b", 5, 6), task("c", 10, 11)]:
            consumed.append(t.name)
            yield t

    groups = group_connected(source(), assume_sorted=True)
    assert [t.name for t in next(groups)] == ["a"]
    # Only enough input to know that the first group is complete has been read.
    assert consumed == ["a", "b"]


def test_unsorted_input_raises_when_declared_sorted() -> None:
    items = [task("a", 5, 8), task("b", 0, 2)]
    with pytest.raises(ValueError):
        list(group_connected(items, assume_sorted=True))


def test_sorting_is_by_start_only_not_end() -> None:
    items = [task("a", 0, 10), task("b", 0, 2), task("c", 1, 3)]
    assert names(group_connected(items, assume_sorted=True)) == [["a", "b", "c"]]


def test_handler_groups_unsorted_input_in_start_order() -> None:
    items = [task("d", 20, 25), task("b", 1, 3), task("c", 10, 12), task("e", 24, 26), task("a", 0, 2)]
    assert names(group_connected(items)) == [["a", "b"], ["c"], ["d", "e"]]


def test_handler_keeps_ties_in_input_order() -> None:
    items = [task("z", 5, 9), task("a", 0, 5), task("b", 0, 5), task("c", 0, 3)]
    assert names(group_connected(items)) == [["a", "b", "c", "z"]]


def test_handler_infers_timezone_from_items() -> None:
    tz = ZoneInfo("Europe/Amsterdam")
    a = Task("a", Interval(at(5).replace(tzinfo=tz), at(8).replace(tzinfo=tz)))
    b = Task("b", Interval(at(0).replace(tzinfo=tz), at(5).replace(tzinfo=tz)))
    assert names(group_connected([a, b])) == [["b", "a"]]


def test_mixed_naive_and_aware_items_raise() -> None:
    naive = task("naive", 0, 5)
    aware = Task("aware", Interval(at(5).replace(tzinfo=timezone.utc), at(8).replace(tzinfo=timezone.utc)))
    with pytest.raises(TypeError):
        list(group_connected([naive, aware]))


@pytest.mark.parametrize("seed", range(25))
def test_engines_agree_on_random_input(seed: int) -> None:
    rng = random.Random(seed)
    items = []
    for n in range(rng.randint(0, 60)):
        start = rng.randint(0, 40)
        items.append(task(f"t{n}", start, start + rng.randint(0, 6)))
    rng.shuffle(items)

    presorted = sorted(items, key=lambda t: t.interval.start)  # stable, so ties keep their shuffled order

    assert names(group_connected(items)) == names(group_connected(presorted, assume_sorted=True))
