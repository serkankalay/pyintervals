from datetime import datetime
from typing import Iterable

import pytest

from pyintervals import Interval
from pyintervals.time_value_node import TimeValueNode


def _tvn_with_intervals(
    tvn: TimeValueNode, intervals: Iterable[Interval]
) -> TimeValueNode:
    tvn._add_intervals(intervals)
    return tvn


@pytest.mark.parametrize(
    "tvn, other, is_equal",
    [
        (
            _tvn_with_intervals(
                TimeValueNode(
                    time_point=datetime(1973, 1, 1),
                ),
                intervals=[
                    Interval(datetime(1970, 1, 1), datetime(1977, 1, 1)),
                ],
            ),
            _tvn_with_intervals(
                TimeValueNode(
                    time_point=datetime(1973, 1, 1),
                ),
                intervals=[
                    Interval(datetime(1970, 1, 1), datetime(1977, 1, 1)),
                ],
            ),
            True,
        ),
        (
            _tvn_with_intervals(
                TimeValueNode(
                    time_point=datetime(1973, 1, 1),
                ),
                intervals=[],
            ),
            _tvn_with_intervals(
                TimeValueNode(
                    time_point=datetime(1973, 1, 1),
                ),
                intervals=[
                    Interval(datetime(1971, 1, 1), datetime(1977, 1, 1)),
                ],
            ),
            False,
        ),
        (
            TimeValueNode(time_point=datetime(1973, 1, 1)),
            TimeValueNode(time_point=datetime(1974, 1, 1)),
            False,
        ),
    ],
)
def test_time_value_node_equality(
    tvn: TimeValueNode,
    other: TimeValueNode,
    is_equal: bool,
) -> None:
    assert (tvn == other) == is_equal


@pytest.mark.parametrize(
    "tvn, other, is_lt, is_le, is_gt, is_ge",
    [
        (
            TimeValueNode(datetime(1973, 1, 1)),
            TimeValueNode(datetime(1973, 1, 1)),
            False,  # is_lt
            True,  # is_le
            False,  # is_gt
            True,  # is_ge
        ),
        (
            TimeValueNode(datetime(1973, 1, 1)),
            TimeValueNode(datetime(1974, 1, 1)),
            True,  # is_lt
            True,  # is_le
            False,  # is_gt
            False,  # is_ge
        ),
        (
            TimeValueNode(datetime(1975, 1, 1)),
            TimeValueNode(datetime(1974, 1, 1)),
            False,  # is_lt
            False,  # is_le
            True,  # is_gt
            True,  # is_ge
        ),
    ],
)
def test_time_value_node_comparison(
    tvn: TimeValueNode,
    other: TimeValueNode,
    is_lt: bool,
    is_le: bool,
    is_gt: bool,
    is_ge: bool,
) -> None:
    assert (tvn < other) == is_lt
    assert (tvn > other) == is_gt
    assert (tvn <= other) == is_le
    assert (tvn >= other) == is_ge
