from __future__ import annotations

from datetime import datetime
from functools import partial
from typing import Iterable

import pytest
from sortedcontainers import SortedList

from pyintervals import Interval
from pyintervals.constants import TIME_ZERO
from pyintervals.time_value_node import TimeValueNode, _simplify


def _tvn_with_intervals(
    tvn: TimeValueNode, intervals: Iterable[Interval]
) -> TimeValueNode:
    for interval in intervals:
        tvn._add_interval(interval)
    return tvn


def _to_tvn(
    intervals: Iterable[Interval],
) -> TimeValueNode:
    return _tvn_with_intervals(TimeValueNode(datetime(2014, 9, 12)), intervals)


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
                intervals=[
                    Interval(datetime(1970, 1, 1), datetime(1977, 1, 1)),
                    Interval(datetime(1975, 1, 1), datetime(1977, 1, 1)),
                ],
            ),
            _tvn_with_intervals(
                TimeValueNode(
                    time_point=datetime(1973, 1, 1),
                ),
                intervals=[
                    Interval(datetime(1975, 1, 1), datetime(1977, 1, 1)),
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


@pytest.mark.parametrize(
    "tvn, to_time",
    [
        # Without intervals
        (
            TimeValueNode(datetime(1975, 1, 1)),
            None,
        ),
        # Without intervals, but time
        (
            TimeValueNode(datetime(1975, 1, 1)),
            datetime(2014, 9, 12),
        ),
        # With intervals
        (
            _tvn_with_intervals(
                TimeValueNode(datetime(1975, 1, 1)),
                intervals=[
                    Interval(datetime(1970, 1, 1), datetime(2000, 1, 1))
                ],
            ),
            None,
        ),
        # With degenerate intervals
        (
            _tvn_with_intervals(
                TimeValueNode(datetime(1975, 1, 1)),
                intervals=[
                    Interval(datetime(1975, 1, 1), datetime(1975, 1, 1))
                ],
            ),
            None,
        ),
        # With intervals and time
        (
            _tvn_with_intervals(
                TimeValueNode(datetime(1975, 1, 1)),
                intervals=[
                    Interval(datetime(1970, 1, 1), datetime(2000, 1, 1))
                ],
            ),
            datetime(2014, 9, 12),
        ),
        # With degenerate intervals and time
        (
            _tvn_with_intervals(
                TimeValueNode(datetime(1975, 1, 1)),
                intervals=[
                    Interval(datetime(1975, 1, 1), datetime(1975, 1, 1))
                ],
            ),
            datetime(1976, 1, 1),
        ),
    ],
)
def test_clone_time_value_node(
    tvn: TimeValueNode, to_time: datetime | None
) -> None:
    to_compare = (
        tvn
        if to_time is None
        else _tvn_with_intervals(
            TimeValueNode(to_time),
            [t for t in tvn.intervals if not t.is_degenerate()],
        )
    )
    assert to_compare == TimeValueNode.clone(tvn, to_time)


_normal_interval_with_value = partial(
    Interval,
    start=datetime(2017, 5, 20),
    end=datetime(2023, 10, 6),
)

_degenerate_interval_with_value = partial(
    Interval,
    start=datetime(2014, 9, 12),
    end=datetime(2014, 9, 12),
)


@pytest.mark.parametrize(
    "intervals, expected_value",
    [
        # Empty,
        ([], 0),
        # Single interval with 0 value
        (
            [_normal_interval_with_value(value=0)],
            0,
        ),
        # Single interval with postive value
        (
            [_normal_interval_with_value(value=5)],
            5,
        ),
        # Two intervals with 0 value
        (
            [
                _normal_interval_with_value(value=0),
                _normal_interval_with_value(value=0),
            ],
            0,
        ),
        # Two intervals with positive value
        (
            [
                _normal_interval_with_value(value=2.5),
                _normal_interval_with_value(value=5),
            ],
            7.5,
        ),
        # Degenerate with 0
        (
            [_degenerate_interval_with_value(value=0)],
            0,
        ),
        # Degenerate with positive value
        (
            [_degenerate_interval_with_value(value=5)],
            0,
        ),
        # Two degenerate with positive value
        (
            [
                _degenerate_interval_with_value(value=5),
                _degenerate_interval_with_value(value=7),
            ],
            0,
        ),
        # Combination
        (
            [
                _normal_interval_with_value(value=3.5),
                _degenerate_interval_with_value(value=7),
            ],
            3.5,
        ),
    ],
)
def test_time_value_node_value(
    intervals,
    expected_value: float,
) -> None:
    assert _to_tvn(intervals).value == expected_value
