from __future__ import annotations

from datetime import datetime
from typing import Iterable, Sequence

import pytest
from _pytest.fixtures import FixtureRequest
from sortedcontainers import SortedList

from pyintervals import Interval
from pyintervals.constants import TIME_ZERO
from pyintervals.interval import contains_point
from pyintervals.interval_handler import IntervalHandler, _make_range
from pyintervals.time_value_node import TimeValueNode


@pytest.mark.parametrize(
    "intervals,n_expected_intervals,n_expected_tvn,expected_tvn_time_points",
    [
        # Empty IH
        ([], 0, 1, [TIME_ZERO]),
        # IH with 1 normal interval
        (
            [Interval(datetime(2023, 10, 6), datetime(2024, 2, 29))],
            1,
            3,
            [
                TIME_ZERO,
                datetime(2023, 10, 6),
                datetime(2024, 2, 29),
            ],
        ),
        # IH with 1 degenerate interval
        (
            [Interval(datetime(2023, 10, 6), datetime(2023, 10, 6))],
            1,
            2,
            [
                TIME_ZERO,
                datetime(2023, 10, 6),
            ],
        ),
        # IH with 1 normal and 1 degenerate interval, irrelevant
        (
            [
                Interval(datetime(2023, 10, 6), datetime(2023, 10, 6)),
                Interval(datetime(2023, 10, 8), datetime(2023, 10, 16)),
            ],
            2,
            4,
            [
                TIME_ZERO,
                datetime(2023, 10, 6),
                datetime(2023, 10, 8),
                datetime(2023, 10, 16),
            ],
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
            [
                TIME_ZERO,
                datetime(2023, 10, 6),
                datetime(2023, 10, 7),
                datetime(2023, 10, 8),
                datetime(2023, 10, 16),
                datetime(2023, 10, 18),
            ],
        ),
        # IH with 2 normal overlapping intervals
        (
            [
                Interval(datetime(2023, 10, 6), datetime(2023, 10, 10)),
                Interval(datetime(2023, 10, 8), datetime(2023, 10, 16)),
            ],
            2,
            5,
            [
                TIME_ZERO,
                datetime(2023, 10, 6),
                datetime(2023, 10, 8),
                datetime(2023, 10, 10),
                datetime(2023, 10, 16),
            ],
        ),
        # IH with 2 end-to-end intervals
        (
            [
                Interval(datetime(2023, 10, 6), datetime(2023, 10, 10)),
                Interval(datetime(2023, 10, 10), datetime(2023, 10, 16)),
            ],
            2,
            4,
            [
                TIME_ZERO,
                datetime(2023, 10, 6),
                datetime(2023, 10, 10),
                datetime(2023, 10, 16),
            ],
        ),
        # IH with 2 exactly same intervals
        (
            [
                Interval(datetime(2023, 10, 6), datetime(2023, 10, 10)),
                Interval(datetime(2023, 10, 6), datetime(2023, 10, 10)),
            ],
            2,
            3,
            [
                TIME_ZERO,
                datetime(2023, 10, 6),
                datetime(2023, 10, 10),
            ],
        ),
        # IH with 2 intervals, one containing the other
        (
            [
                Interval(datetime(2023, 10, 6), datetime(2023, 10, 10)),
                Interval(datetime(2023, 10, 8), datetime(2023, 10, 9)),
            ],
            2,
            5,
            [
                TIME_ZERO,
                datetime(2023, 10, 6),
                datetime(2023, 10, 8),
                datetime(2023, 10, 9),
                datetime(2023, 10, 10),
            ],
        ),
        # IH with 2 intervals, one normal, one degenerate within the normal
        (
            [
                Interval(datetime(2023, 10, 6), datetime(2023, 10, 10)),
                Interval(datetime(2023, 10, 8), datetime(2023, 10, 8)),
            ],
            2,
            4,
            [
                TIME_ZERO,
                datetime(2023, 10, 6),
                datetime(2023, 10, 8),
                datetime(2023, 10, 10),
            ],
        ),
        # IH with 2 intervals, one normal, one degenerate same start
        (
            [
                Interval(datetime(2023, 10, 6), datetime(2023, 10, 10)),
                Interval(datetime(2023, 10, 6), datetime(2023, 10, 6)),
            ],
            2,
            3,
            [
                TIME_ZERO,
                datetime(2023, 10, 6),
                datetime(2023, 10, 10),
            ],
        ),
        # IH with 2 intervals, one normal, one degenerate same end
        (
            [
                Interval(datetime(2023, 10, 6), datetime(2023, 10, 10)),
                Interval(datetime(2023, 10, 10), datetime(2023, 10, 10)),
            ],
            2,
            3,
            [
                TIME_ZERO,
                datetime(2023, 10, 6),
                datetime(2023, 10, 10),
            ],
        ),
    ],
)
def test_interval_handler_with_intervals(
    intervals: Iterable[Interval],
    n_expected_intervals: int,
    n_expected_tvn: int,
    expected_tvn_time_points: list[datetime],
) -> None:
    handler = IntervalHandler(intervals=intervals)
    assert len(handler.intervals) == n_expected_intervals
    assert len(handler.projection_graph()) == n_expected_tvn
    assert [
        tvn.time_point for tvn in handler.projection_graph()
    ] == expected_tvn_time_points
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
                Interval(datetime(2023, 10, 7), datetime(2024, 5, 29)),
                Interval(datetime(2025, 11, 5), datetime(2027, 7, 27)),
            ],
        ),
        (
            "interval_handler_w_2_intervals",
            [
                Interval(datetime(2023, 10, 7), datetime(2023, 10, 7)),
                Interval(datetime(2025, 11, 5), datetime(2025, 11, 5)),
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
    for interval in new_intervals:
        assert (
            interval in handler.node_at_time(interval.start).starting_intervals
        )
        assert interval in handler.node_at_time(interval.end).ending_intervals


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
    assert (
        to_remove
        not in handler.node_at_time(to_remove.start).starting_intervals
    )
    assert (
        to_remove not in handler.node_at_time(to_remove.end).ending_intervals
    )

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
                [
                    TimeValueNode(datetime(1970, 1, 1)),
                    TimeValueNode(datetime(2070, 1, 1)),
                ],
            ),
            Interval(datetime(2060, 1, 1), datetime(2070, 1, 1)),
        ),
        # Empty node graph
        (
            SortedList(
                [
                    TimeValueNode(datetime(1970, 1, 1)),
                ]
            ),
            Interval(datetime(2060, 1, 1), datetime(2070, 1, 1)),
        ),
    ],
)
def test_make_range(nodes: SortedList, new_interval: Interval) -> None:
    _make_range(nodes, new_interval)
    assert {new_interval.start, new_interval.end}.issubset(
        {n.time_point for n in nodes}
    )


def _complex_intervals() -> list[Interval]:
    return [
        Interval(
            start=datetime(2023, 1, 1),
            end=datetime(2023, 1, 15, 17, 0),
            value=1,
        ),
        Interval(
            start=datetime(2023, 1, 19, 5, 0),
            end=datetime(2023, 1, 21, 23, 0),
            value=2,
        ),
        Interval(
            start=datetime(2023, 1, 20, 5, 0),
            end=datetime(2023, 1, 20, 5, 0),
            value=1000,
        ),
        Interval(
            start=datetime(2023, 1, 20, 5, 0),
            end=datetime(2023, 1, 25, 5, 0),
            value=5,
        ),
        Interval(
            start=datetime(2023, 1, 25, 5, 0),
            end=datetime(2023, 1, 25, 5, 0),
            value=9,
        ),
        Interval(
            start=datetime(2023, 2, 1),
            end=datetime(2023, 2, 1),
            value=9,
        ),
        Interval(
            start=datetime(2023, 2, 1),
            end=datetime(2023, 3, 1),
            value=3,
        ),
        Interval(
            start=datetime(2023, 2, 15),
            end=datetime(2023, 2, 15),
            value=2,
        ),
    ]


def _complex_interval_handler() -> IntervalHandler:
    return IntervalHandler(intervals=_complex_intervals())


@pytest.mark.parametrize(
    "time_point, n_expected_intervals, expected_value",
    [
        # Before first interval
        (datetime(2020, 1, 1), 0, 0),
        # At first interval
        (datetime(2023, 1, 1), 1, 1),
        # During first interval
        (datetime(2023, 1, 10), 1, 1),
        # End of first interval
        (datetime(2023, 1, 15, 17), 0, 0),
        # Right before first degenerate
        (datetime(2023, 1, 20, 4, 59), 1, 2),
        # At first degenerate
        (datetime(2023, 1, 20, 5, 0), 3, 7),
        # First time only 2 normal intervals exist
        (datetime(2023, 1, 21, 5, 0), 3, 7),
        # One of the intervals ended
        (datetime(2023, 1, 23, 19, 0), 1, 5),
        # Normal ended but 1 degenerate is there
        (datetime(2023, 1, 25, 5, 0), 1, 0),
        # Nothing is there
        (datetime(2023, 1, 29, 5, 0), 1, 0),
        # Next group starting, no impact degenerate
        (datetime(2023, 2, 1), 2, 3),
        (datetime(2023, 2, 15), 2, 3),
        # End of story
        (datetime(2023, 3, 1), 0, 0),
    ],
)
def test_node_and_value_at_time(
    time_point, n_expected_intervals, expected_value
) -> None:
    handler = _complex_interval_handler()
    assert (
        len(handler.node_at_time(time_point).intervals) == n_expected_intervals
    )
    assert handler.value_at_time(time_point) == expected_value


@pytest.mark.parametrize(
    "intervals, n_expected_tvn_reduction",
    [
        ([_complex_intervals()[0]], 2),
        (_complex_intervals(), 9),
        ([_complex_intervals()[2]], 0),
        ([_complex_intervals()[4]], 0),
        ([_complex_intervals()[7]], 1),
    ],
)
def test_remove_intervals_detailed(
    intervals: list[Interval], n_expected_tvn_reduction
) -> None:
    handler = _complex_interval_handler()
    original_tvn_count = len(handler.projection_graph())
    handler.remove(intervals)
    assert len(handler.projection_graph()) == (
        original_tvn_count - n_expected_tvn_reduction
    )
    assert not any(
        interval in node.intervals
        for node in handler.projection_graph()
        for interval in intervals
    )
