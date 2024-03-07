from __future__ import annotations

from datetime import datetime
from typing import Iterable, Sequence

import pytest
from _pytest.fixtures import FixtureRequest
from sortedcontainers import SortedList

from pyintervals import Interval
from pyintervals.interval import contains_point
from pyintervals.interval_handler import (
    _TIME_ZERO,
    IntervalHandler,
    _make_range,
)
from pyintervals.time_value_node import TimeValueNode


@pytest.mark.parametrize(
    "intervals,n_expected_intervals,n_expected_tvn,expected_tvn_time_points",
    [
        # Empty IH
        ([], 0, 1, {_TIME_ZERO}),
        # IH with 1 normal interval
        (
            [Interval(datetime(2023, 10, 6), datetime(2024, 2, 29))],
            1,
            3,
            {
                _TIME_ZERO,
                datetime(2023, 10, 6),
                datetime(2024, 2, 29),
            },
        ),
        # IH with 1 degenerate interval
        (
            [Interval(datetime(2023, 10, 6), datetime(2023, 10, 6))],
            1,
            2,
            {
                _TIME_ZERO,
                datetime(2023, 10, 6),
            },
        ),
        # IH with 1 normal and 1 degenerate interval, irrelevant
        (
            [
                Interval(datetime(2023, 10, 6), datetime(2023, 10, 6)),
                Interval(datetime(2023, 10, 8), datetime(2023, 10, 16)),
            ],
            2,
            4,
            {
                _TIME_ZERO,
                datetime(2023, 10, 6),
                datetime(2023, 10, 8),
                datetime(2023, 10, 16),
            },
        ),
        # IH with 2 normal irrelevant and 1 degenerate interval, irrelevant
        (
            [
                Interval(datetime(2023, 10, 6), datetime(2023, 10, 7)),
                Interval(datetime(2023, 10, 8), datetime(2023, 10, 16)),
                Interval(datetime(2023, 10, 18), datetime(2023, 10, 18)),
            ],
            3,
            6,
            {
                _TIME_ZERO,
                datetime(2023, 10, 6),
                datetime(2023, 10, 7),
                datetime(2023, 10, 8),
                datetime(2023, 10, 16),
                datetime(2023, 10, 18),
            },
        ),
        # IH with 2 normal overlapping intervals
        (
            [
                Interval(datetime(2023, 10, 6), datetime(2023, 10, 10)),
                Interval(datetime(2023, 10, 8), datetime(2023, 10, 16)),
            ],
            2,
            5,
            {
                _TIME_ZERO,
                datetime(2023, 10, 6),
                datetime(2023, 10, 8),
                datetime(2023, 10, 10),
                datetime(2023, 10, 16),
            },
        ),
        # IH with 2 end-to-end intervals
        (
            [
                Interval(datetime(2023, 10, 6), datetime(2023, 10, 10)),
                Interval(datetime(2023, 10, 10), datetime(2023, 10, 16)),
            ],
            2,
            4,
            {
                _TIME_ZERO,
                datetime(2023, 10, 6),
                datetime(2023, 10, 10),
                datetime(2023, 10, 16),
            },
        ),
        # IH with 2 exactly same intervals
        (
            [
                Interval(datetime(2023, 10, 6), datetime(2023, 10, 10)),
                Interval(datetime(2023, 10, 6), datetime(2023, 10, 10)),
            ],
            2,
            3,
            {
                _TIME_ZERO,
                datetime(2023, 10, 6),
                datetime(2023, 10, 10),
            },
        ),
        # IH with 2 intervals, one containing the other
        (
            [
                Interval(datetime(2023, 10, 6), datetime(2023, 10, 10)),
                Interval(datetime(2023, 10, 8), datetime(2023, 10, 9)),
            ],
            2,
            5,
            {
                _TIME_ZERO,
                datetime(2023, 10, 6),
                datetime(2023, 10, 8),
                datetime(2023, 10, 9),
                datetime(2023, 10, 10),
            },
        ),
        # IH with 2 intervals, one normal, one degenerate within the normal
        (
            [
                Interval(datetime(2023, 10, 6), datetime(2023, 10, 10)),
                Interval(datetime(2023, 10, 8), datetime(2023, 10, 8)),
            ],
            2,
            4,
            {
                _TIME_ZERO,
                datetime(2023, 10, 6),
                datetime(2023, 10, 8),
                datetime(2023, 10, 10),
            },
        ),
        # IH with 2 intervals, one normal, one degenerate same start
        (
            [
                Interval(datetime(2023, 10, 6), datetime(2023, 10, 10)),
                Interval(datetime(2023, 10, 6), datetime(2023, 10, 6)),
            ],
            2,
            3,
            {
                _TIME_ZERO,
                datetime(2023, 10, 6),
                datetime(2023, 10, 10),
            },
        ),
        # IH with 2 intervals, one normal, one degenerate same end
        (
            [
                Interval(datetime(2023, 10, 6), datetime(2023, 10, 10)),
                Interval(datetime(2023, 10, 10), datetime(2023, 10, 10)),
            ],
            2,
            3,
            {
                _TIME_ZERO,
                datetime(2023, 10, 6),
                datetime(2023, 10, 10),
            },
        ),
    ],
)
def test_interval_handler_with_intervals(
    intervals: Iterable[Interval],
    n_expected_intervals: int,
    n_expected_tvn: int,
    expected_tvn_time_points: set[datetime],
) -> None:
    handler = IntervalHandler(intervals=intervals)
    assert len(handler.intervals) == n_expected_intervals
    assert len(handler.projection_graph()) == n_expected_tvn
    assert (
        set(tvn.time_point for tvn in handler.projection_graph())
        == expected_tvn_time_points
    )
    for interval in intervals:
        for node in handler.projection_graph():
            if contains_point(interval, node.time_point):
                assert interval in node.intervals


@pytest.fixture
def interval_handler_w_2_intervals() -> IntervalHandler:
    return IntervalHandler(
        intervals=[
            Interval(datetime(2023, 10, 6), datetime(2024, 2, 29)),
            Interval(datetime(2025, 11, 4), datetime(2027, 2, 27)),
        ]
    )


@pytest.mark.parametrize(
    "interval_handler,new_intervals",
    [
        ("interval_handler_w_2_intervals", []),
        (
            "interval_handler_w_2_intervals",
            [
                Interval(datetime(2023, 10, 6), datetime(2024, 2, 29)),
                Interval(datetime(2025, 11, 4), datetime(2027, 2, 27)),
            ],
        ),
    ],
)
def test_add_intervals(
    request: FixtureRequest,
    interval_handler: str,
    new_intervals: Sequence[Interval],
) -> None:
    handler = request.getfixturevalue(interval_handler)
    prev_count = len(handler.intervals)
    handler.add(new_intervals)
    assert prev_count + len(new_intervals) == len(handler.intervals)


def test_remove_intervals(
    interval_handler_w_2_intervals: IntervalHandler,
) -> None:
    handler = interval_handler_w_2_intervals
    original_count = len(handler.intervals)

    # Remove no interval
    handler.remove([])
    assert original_count == len(handler.intervals)

    # Remove 1 interval
    to_remove = handler.intervals[0]
    handler.remove([to_remove])
    assert original_count - 1 == len(handler.intervals)

    # Remove all
    handler.remove(handler.intervals)
    assert len(handler.intervals) == 0


@pytest.mark.parametrize(
    "nodes, new_interval",
    [
        # Degenerate same-time
        (
            SortedList([TimeValueNode(datetime(2070, 1, 1))]),
            Interval(datetime(2070, 1, 1), datetime(2070, 1, 1)),
        ),
        # Normal, starting same-time
        (
            SortedList([TimeValueNode(datetime(2070, 1, 1))]),
            Interval(datetime(2070, 1, 1), datetime(2075, 1, 1)),
        ),
        # Normal, starting later
        (
            SortedList([TimeValueNode(datetime(2070, 1, 1))]),
            Interval(datetime(2075, 1, 1), datetime(2076, 1, 1)),
        ),
        # Normal, starting earlier
        # Note, we have an earlier default node (as IntervalHandler will have)
        (
            SortedList(
                [
                    TimeValueNode(datetime(1970, 1, 1)),
                    TimeValueNode(datetime(2070, 1, 1)),
                ]
            ),
            Interval(datetime(2060, 1, 1), datetime(2065, 1, 1)),
        ),
        # Normal, starting earlier, ending-exactly the same time
        # Note, we have an earlier default node (as IntervalHandler will have)
        (
            SortedList(
                [TimeValueNode(datetime(2070, 1, 1))],
            ),
            Interval(datetime(2060, 1, 1), datetime(2070, 1, 1)),
        ),
        # Empty node graph
        (
            SortedList([]),
            Interval(datetime(2060, 1, 1), datetime(2070, 1, 1)),
        ),
    ],
)
def test_make_range(nodes: SortedList, new_interval: Interval) -> None:
    _make_range(nodes, new_interval)
    assert {new_interval.start, new_interval.end}.issubset(
        {n.time_point for n in nodes}
    )
