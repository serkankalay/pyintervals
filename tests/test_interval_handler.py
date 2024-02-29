from datetime import datetime
from typing import Iterable, Any, Sequence

import pytest
from _pytest.fixtures import FixtureRequest

from pyintervals import Interval
from pyintervals.interval_handler import IntervalHandler


@pytest.mark.parametrize(
    "intervals, expected_count",
    [
        ([], 0),
        ([Interval(datetime(2023, 10, 6), datetime(2024, 2, 29))], 1),
        (
            [
                Interval(datetime(2023, 10, 6), datetime(2024, 2, 29)),
                Interval(datetime(2023, 10, 6), datetime(2023, 10, 6)),
                Interval(datetime(2024, 12, 4), datetime(2025, 2, 28)),
                Interval(datetime(2025, 11, 4), datetime(2027, 2, 27)),
            ],
            4,
        ),
    ],
)
def test_interval_handler_with_intervals(
    intervals: Iterable[Interval],
    expected_count: int,
) -> None:
    handler = IntervalHandler(intervals=intervals)
    assert len(handler.intervals) == expected_count


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
