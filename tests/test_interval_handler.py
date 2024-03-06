from datetime import datetime
from typing import Iterable, Any, Sequence

import pytest
from _pytest.fixtures import FixtureRequest

from pyintervals import Interval
from pyintervals.interval_handler import (
    IntervalHandler,
    _TIME_ZERO,
    _make_range,
)
from pyintervals.time_value_node import TimeValueNode


@pytest.mark.parametrize(
    "intervals, expected_interval_count, expected_tvn_count, expected_tvn_time_point_set",
    [
        ([], 0, 1, {_TIME_ZERO}),
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
        # TODO
        # (
        #     [
        #         Interval(datetime(2023, 10, 6), datetime(2024, 2, 29)),
        #         Interval(datetime(2023, 10, 6), datetime(2023, 10, 6)),
        #         Interval(datetime(2024, 12, 4), datetime(2025, 2, 28)),
        #         Interval(datetime(2025, 11, 4), datetime(2027, 2, 27)),
        #     ],
        #     4,
        # ),
    ],
)
def test_interval_handler_with_intervals(
    intervals: Iterable[Interval],
    expected_interval_count: int,
    expected_tvn_count: int,
    expected_tvn_time_point_set: set[datetime],
) -> None:
    handler = IntervalHandler(intervals=intervals)
    assert len(handler.intervals) == expected_interval_count
    assert len(handler.projection_graph()) == expected_tvn_count
    assert (
        set(tvn.time_point for tvn in handler.projection_graph())
        == expected_tvn_time_point_set
    )


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
            [TimeValueNode(datetime(2070, 1, 1))],
            Interval(datetime(2070, 1, 1), datetime(2070, 1, 1)),
        ),
        # Normal, starting same-time
        (
            [TimeValueNode(datetime(2070, 1, 1))],
            Interval(datetime(2070, 1, 1), datetime(2075, 1, 1)),
        ),
        # Normal, starting later
        (
            [TimeValueNode(datetime(2070, 1, 1))],
            Interval(datetime(2075, 1, 1), datetime(2076, 1, 1)),
        ),
        # Normal, starting earlier
        # Note, we have an earlier default node (as IntervalHandler will have)
        (
            [
                TimeValueNode(datetime(1970, 1, 1)),
                TimeValueNode(datetime(2070, 1, 1)),
            ],
            Interval(datetime(2060, 1, 1), datetime(2065, 1, 1)),
        ),
        # Normal, starting earlier, ending-exactly the same time
        # Note, we have an earlier default node (as IntervalHandler will have)
        (
            [
                TimeValueNode(datetime(2070, 1, 1)),
            ],
            Interval(datetime(2060, 1, 1), datetime(2070, 1, 1)),
        ),
        # Empty node graph
        # Note, we have an earlier default node (as IntervalHandler will have)
        (
            [],
            Interval(datetime(2060, 1, 1), datetime(2070, 1, 1)),
        ),
    ],
)
def test_make_range(
    nodes: list[TimeValueNode], new_interval: Interval
) -> None:
    _make_range(nodes, new_interval)
    assert {new_interval.start, new_interval.end}.issubset(
        {n.time_point for n in nodes}
    )
