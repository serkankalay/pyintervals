from __future__ import annotations

import random
from collections.abc import Iterable, Iterator
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone, tzinfo
from typing import Any
from zoneinfo import ZoneInfo

import pytest

from pyintervals import Interval, group_connected
from tests.helpers import THE_DATE

UTC = timezone.utc
AMSTERDAM = ZoneInfo("Europe/Amsterdam")


@dataclass(frozen=True)
class Task:
    name: str
    interval: Interval


def at(hours: int, tz: tzinfo | None = None) -> datetime:
    return (THE_DATE + timedelta(hours=hours)).replace(tzinfo=tz)


def task(name: str, start: int, end: int, tz: tzinfo | None = None) -> Task:
    return Task(name, Interval(at(start, tz), at(end, tz)))


def names(groups: Iterable[list[Task]]) -> list[list[str]]:
    return [[t.name for t in group] for group in groups]


@pytest.fixture(params=[True, False], ids=["sweep", "handler"])
def assume_sorted(request: pytest.FixtureRequest) -> bool:
    """Runs a test once per engine. Every input used with this fixture is already ordered by start."""
    return bool(request.param)


# Inputs ordered by start, so both engines must produce the same groups.
SORTED_CASES = [
    pytest.param([], [], id="empty"),
    pytest.param([task("a", 0, 1)], [["a"]], id="single"),
    pytest.param([task("a", 0, 5), task("b", 3, 8)], [["a", "b"]], id="overlapping"),
    pytest.param([task("a", 0, 5), task("b", 5, 8)], [["a", "b"]], id="touching"),
    pytest.param([task("a", 0, 5), task("b", 6, 8)], [["a"], ["b"]], id="gap"),
    pytest.param(
        [task("a", 0, 3), task("b", 2, 5), task("c", 4, 7)],
        [["a", "b", "c"]],
        id="chain-of-overlaps",
    ),
    pytest.param(
        # `b` ends before `a`, so `c` must still connect through `a`'s end.
        [task("a", 0, 10), task("b", 1, 2), task("c", 9, 12)],
        [["a", "b", "c"]],
        id="nested-does-not-shrink-group-end",
    ),
    pytest.param(
        [task("a", 0, 5), task("b", 0, 5), task("c", 0, 5)],
        [["a", "b", "c"]],
        id="identical-intervals-keep-input-order",
    ),
    pytest.param(
        [task("a", 0, 10), task("b", 0, 2), task("c", 1, 3)],
        [["a", "b", "c"]],
        id="ordered-by-start-only-not-end",
    ),
    pytest.param(
        [task("a", 0, 2), task("b", 1, 3), task("c", 10, 12), task("d", 20, 25), task("e", 24, 26)],
        [["a", "b"], ["c"], ["d", "e"]],
        id="multiple-groups-in-start-order",
    ),
    pytest.param(
        [task("a", 0, 5), task("point", 2, 2), task("b", 5, 8)],
        [["a", "b"]],
        id="degenerate-inside-dropped",
    ),
    pytest.param(
        [task("a", 0, 5), task("point", 5, 5), task("b", 5, 8)],
        [["a", "b"]],
        id="degenerate-touching-dropped",
    ),
    pytest.param(
        [task("a", 0, 2), task("point", 4, 4), task("b", 6, 8)],
        [["a"], ["b"]],
        id="degenerate-isolated-dropped",
    ),
    pytest.param([task("p", 1, 1), task("q", 1, 1)], [], id="only-degenerate"),
    pytest.param(
        [task("a", 0, 5, UTC), task("b", 5, 8, UTC)],
        [["a", "b"]],
        id="timezone-aware",
    ),
]

# Inputs not ordered by start, which only the handler engine accepts.
UNSORTED_CASES = [
    pytest.param(
        [task("d", 20, 25), task("b", 1, 3), task("c", 10, 12), task("e", 24, 26), task("a", 0, 2)],
        [["a", "b"], ["c"], ["d", "e"]],
        id="groups-in-start-order",
    ),
    pytest.param(
        [task("z", 5, 9), task("a", 0, 5), task("b", 0, 5), task("c", 0, 3)],
        [["a", "b", "c", "z"]],
        id="ties-keep-input-order",
    ),
    pytest.param(
        [task("a", 5, 8, AMSTERDAM), task("b", 0, 5, AMSTERDAM)],
        [["b", "a"]],
        id="timezone-inferred-from-items",
    ),
]

ERROR_CASES = [
    pytest.param(
        [task("a", 5, 8), task("b", 0, 2)],
        {"assume_sorted": True},
        ValueError,
        id="unsorted-declared-sorted",
    ),
    pytest.param(
        [task("naive", 0, 5), task("aware", 5, 8, UTC)],
        {},
        TypeError,
        id="mixed-naive-and-aware",
    ),
]


@pytest.mark.parametrize("items,expected", SORTED_CASES)
def test_groups_sorted_input(items: list[Task], expected: list[list[str]], assume_sorted: bool) -> None:
    assert names(group_connected(items, assume_sorted=assume_sorted)) == expected


@pytest.mark.parametrize("items,expected", UNSORTED_CASES)
def test_handler_groups_unsorted_input(items: list[Task], expected: list[list[str]]) -> None:
    assert names(group_connected(items)) == expected


@pytest.mark.parametrize("items,kwargs,error", ERROR_CASES)
def test_invalid_input_raises(items: list[Task], kwargs: dict[str, Any], error: type[Exception]) -> None:
    with pytest.raises(error):
        list(group_connected(items, **kwargs))


def test_key_function_is_used_for_arbitrary_shapes(assume_sorted: bool) -> None:
    items = [("a", at(0), at(5)), ("b", at(5), at(8)), ("c", at(20), at(21))]
    groups = group_connected(items, key=lambda i: Interval(i[1], i[2]), assume_sorted=assume_sorted)
    assert [[i[0] for i in g] for g in groups] == [["a", "b"], ["c"]]


def test_original_objects_are_yielded(assume_sorted: bool) -> None:
    a, b = task("a", 0, 5), task("b", 5, 8)
    (group,) = group_connected([a, b], assume_sorted=assume_sorted)
    assert group[0] is a
    assert group[1] is b


def test_is_lazy_when_sorted() -> None:
    consumed: list[str] = []

    def source() -> Iterator[Task]:
        for t in [task("a", 0, 1), task("b", 5, 6), task("c", 10, 11)]:
            consumed.append(t.name)
            yield t

    groups = group_connected(source(), assume_sorted=True)
    assert names([next(groups)]) == [["a"]]
    # Only enough input to know that the first group is complete has been read.
    assert consumed == ["a", "b"]


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
