from __future__ import annotations

import random
from collections.abc import Iterable, Iterator
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone, tzinfo
from typing import TYPE_CHECKING, Any
from zoneinfo import ZoneInfo

import pytest

from pyintervals import Interval, group_connected
from tests.helpers import THE_DATE

if TYPE_CHECKING:
    from _pytest.mark import ParameterSet

UTC = timezone.utc
AMSTERDAM = ZoneInfo("Europe/Amsterdam")

Names = list[list[str]]


@dataclass(frozen=True)
class Task:
    name: str
    interval: Interval


def at(hours: int, tz: tzinfo | None = None) -> datetime:
    return (THE_DATE + timedelta(hours=hours)).replace(tzinfo=tz)


def task(name: str, start: int, end: int, tz: tzinfo | None = None) -> Task:
    return Task(name, Interval(at(start, tz), at(end, tz)))


def names(groups: Iterable[list[Task]]) -> Names:
    return [[t.name for t in group] for group in groups]


def case(id: str, items: list[Task], grouped: Names, separated: Names | None = None) -> list[ParameterSet]:
    """Expands one input into a case per ``group_touching`` value.

    ``grouped`` is expected when touching items are grouped. ``separated`` is expected when they
    are not, and is only given when the input has touching items that nothing else bridges.
    """
    return [
        pytest.param(items, True, grouped, id=f"{id}/touching-grouped"),
        pytest.param(items, False, grouped if separated is None else separated, id=f"{id}/touching-separated"),
    ]


@pytest.fixture(params=[True, False], ids=["sweep", "handler"])
def assume_sorted(request: pytest.FixtureRequest) -> bool:
    """Runs a test once per engine. Every input used with this fixture is already ordered by start."""
    return bool(request.param)


@pytest.fixture(params=[True, False], ids=["touching-grouped", "touching-separated"])
def group_touching(request: pytest.FixtureRequest) -> bool:
    """Runs a test once per ``group_touching`` value. Only for inputs whose outcome does not depend on it."""
    return bool(request.param)


# Inputs ordered by start, so both engines must produce the same groups.
SORTED_CASES = [
    *case("empty", [], []),
    *case("single", [task("a", 0, 1)], [["a"]]),
    *case("overlapping", [task("a", 0, 5), task("b", 3, 8)], [["a", "b"]]),
    *case("gap", [task("a", 0, 5), task("b", 6, 8)], [["a"], ["b"]]),
    *case("chain-of-overlaps", [task("a", 0, 3), task("b", 2, 5), task("c", 4, 7)], [["a", "b", "c"]]),
    # `b` ends before `a`, so `c` must still connect through `a`'s end.
    *case("nested-does-not-shrink-group-end", [task("a", 0, 10), task("b", 1, 2), task("c", 9, 12)], [["a", "b", "c"]]),
    *case(
        "identical-intervals-keep-input-order",
        [task("a", 0, 5), task("b", 0, 5), task("c", 0, 5)],
        [["a", "b", "c"]],
    ),
    *case("ordered-by-start-only-not-end", [task("a", 0, 10), task("b", 0, 2), task("c", 1, 3)], [["a", "b", "c"]]),
    *case(
        "multiple-groups-in-start-order",
        [task("a", 0, 2), task("b", 1, 3), task("c", 10, 12), task("d", 20, 25), task("e", 24, 26)],
        [["a", "b"], ["c"], ["d", "e"]],
    ),
    *case("degenerate-inside-dropped", [task("a", 0, 5), task("point", 2, 2), task("b", 3, 8)], [["a", "b"]]),
    *case("degenerate-isolated-dropped", [task("a", 0, 2), task("point", 4, 4), task("b", 6, 8)], [["a"], ["b"]]),
    *case("only-degenerate", [task("p", 1, 1), task("q", 1, 1)], []),
    *case("touching", [task("a", 0, 5), task("b", 5, 8)], [["a", "b"]], [["a"], ["b"]]),
    *case(
        "touching-chain",
        [task("a", 0, 3), task("b", 3, 6), task("c", 6, 9)],
        [["a", "b", "c"]],
        [["a"], ["b"], ["c"]],
    ),
    *case(
        "touching-with-several-starting-at-the-boundary",
        [task("a", 0, 5), task("b", 5, 8), task("c", 5, 9)],
        [["a", "b", "c"]],
        [["a"], ["b", "c"]],
    ),
    *case(
        "touching-with-several-ending-at-the-boundary",
        [task("a", 0, 5), task("b", 2, 5), task("c", 5, 8)],
        [["a", "b", "c"]],
        [["a", "b"], ["c"]],
    ),
    # `b` overlaps both `a` and `c`, so the boundary between those two does not split the group.
    *case("touching-bridged-by-overlap", [task("a", 0, 5), task("b", 3, 6), task("c", 5, 8)], [["a", "b", "c"]]),
    # `a` spans the boundary between `b` and `c`.
    *case("touching-bridged-by-enclosing", [task("a", 0, 10), task("b", 2, 5), task("c", 5, 8)], [["a", "b", "c"]]),
    *case(
        "touching-with-degenerate-at-the-boundary",
        [task("a", 0, 5), task("point", 5, 5), task("b", 5, 8)],
        [["a", "b"]],
        [["a"], ["b"]],
    ),
    *case(
        "touching-timezone-aware",
        [task("a", 0, 5, UTC), task("b", 5, 8, UTC)],
        [["a", "b"]],
        [["a"], ["b"]],
    ),
]

# Inputs not ordered by start, which only the handler engine accepts.
UNSORTED_CASES = [
    *case(
        "groups-in-start-order",
        [task("d", 20, 25), task("b", 1, 3), task("c", 10, 12), task("e", 24, 26), task("a", 0, 2)],
        [["a", "b"], ["c"], ["d", "e"]],
    ),
    *case("ties-keep-input-order", [task("b", 1, 6), task("a", 0, 5), task("c", 1, 3)], [["a", "b", "c"]]),
    *case(
        "touching",
        [task("z", 5, 9), task("a", 0, 5), task("b", 0, 5), task("c", 0, 3)],
        [["a", "b", "c", "z"]],
        [["a", "b", "c"], ["z"]],
    ),
    *case(
        "touching-chain",
        [task("c", 6, 9), task("a", 0, 3), task("b", 3, 6)],
        [["a", "b", "c"]],
        [["a"], ["b"], ["c"]],
    ),
    *case("touching-bridged-by-overlap", [task("c", 5, 8), task("b", 3, 6), task("a", 0, 5)], [["a", "b", "c"]]),
    *case(
        "touching-timezone-inferred-from-items",
        [task("a", 5, 8, AMSTERDAM), task("b", 0, 5, AMSTERDAM)],
        [["b", "a"]],
        [["b"], ["a"]],
    ),
]

ERROR_CASES = [
    pytest.param(
        [task("a", 5, 8), task("b", 0, 2)], {"assume_sorted": True}, ValueError, id="unsorted-declared-sorted"
    ),
    pytest.param([task("naive", 0, 5), task("aware", 5, 8, UTC)], {}, TypeError, id="mixed-naive-and-aware"),
]

# What the first group is, and how much input had to be read to know that it is complete.
LAZY_CASES = [
    pytest.param(True, ["a", "b"], ["a", "b", "c"], id="touching-grouped"),
    pytest.param(False, ["a"], ["a", "b"], id="touching-separated"),
]


@pytest.mark.parametrize("items,group_touching,expected", SORTED_CASES)
def test_groups_sorted_input(items: list[Task], group_touching: bool, expected: Names, assume_sorted: bool) -> None:
    groups = group_connected(items, assume_sorted=assume_sorted, group_touching=group_touching)
    assert names(groups) == expected


@pytest.mark.parametrize("items,group_touching,expected", UNSORTED_CASES)
def test_handler_groups_unsorted_input(items: list[Task], group_touching: bool, expected: Names) -> None:
    assert names(group_connected(items, group_touching=group_touching)) == expected


def test_touching_items_are_grouped_by_default(assume_sorted: bool) -> None:
    items = [task("a", 0, 5), task("b", 5, 8)]
    assert names(group_connected(items, assume_sorted=assume_sorted)) == [["a", "b"]]


@pytest.mark.parametrize("items,kwargs,error", ERROR_CASES)
def test_invalid_input_raises(
    items: list[Task], kwargs: dict[str, Any], error: type[Exception], group_touching: bool
) -> None:
    with pytest.raises(error):
        list(group_connected(items, group_touching=group_touching, **kwargs))


def test_key_function_is_used_for_arbitrary_shapes(assume_sorted: bool, group_touching: bool) -> None:
    items = [("a", at(0), at(5)), ("b", at(3), at(8)), ("c", at(20), at(21))]
    groups = group_connected(
        items, key=lambda i: Interval(i[1], i[2]), assume_sorted=assume_sorted, group_touching=group_touching
    )
    assert [[i[0] for i in g] for g in groups] == [["a", "b"], ["c"]]


def test_original_objects_are_yielded(assume_sorted: bool, group_touching: bool) -> None:
    a, b = task("a", 0, 5), task("b", 3, 8)
    (group,) = group_connected([a, b], assume_sorted=assume_sorted, group_touching=group_touching)
    assert group[0] is a
    assert group[1] is b


@pytest.mark.parametrize("group_touching,first_group,expected_consumed", LAZY_CASES)
def test_is_lazy_when_sorted(group_touching: bool, first_group: list[str], expected_consumed: list[str]) -> None:
    consumed: list[str] = []

    def source() -> Iterator[Task]:
        for t in [task("a", 0, 5), task("b", 5, 8), task("c", 10, 11)]:
            consumed.append(t.name)
            yield t

    groups = group_connected(source(), assume_sorted=True, group_touching=group_touching)
    assert names([next(groups)]) == [first_group]
    # Only enough input to know that the first group is complete has been read.
    assert consumed == expected_consumed


@pytest.mark.parametrize("seed", range(25))
def test_engines_agree_on_random_input(seed: int, group_touching: bool) -> None:
    rng = random.Random(seed)
    items = []
    for n in range(rng.randint(0, 60)):
        start = rng.randint(0, 40)
        items.append(task(f"t{n}", start, start + rng.randint(0, 6)))
    rng.shuffle(items)

    presorted = sorted(items, key=lambda t: t.interval.start)  # stable, so ties keep their shuffled order

    via_handler = group_connected(items, group_touching=group_touching)
    via_sweep = group_connected(presorted, assume_sorted=True, group_touching=group_touching)
    assert names(via_handler) == names(via_sweep)
