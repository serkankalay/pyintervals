from __future__ import annotations

from datetime import datetime
from functools import partial
from typing import Iterable

import pytest
from sortedcontainers import SortedList

from pyintervals import Interval
from pyintervals.constants import TIME_ZERO
from pyintervals.interval_handler import _relevant_nodes
from pyintervals.time_value_node import TimeValueNode


def _tvn_with_intervals(tvn: TimeValueNode, intervals: Iterable[Interval]) -> TimeValueNode:
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
                intervals=[Interval(datetime(1970, 1, 1), datetime(2000, 1, 1))],
            ),
            None,
        ),
        # With degenerate intervals
        (
            _tvn_with_intervals(
                TimeValueNode(datetime(1975, 1, 1)),
                intervals=[Interval(datetime(1975, 1, 1), datetime(1975, 1, 1))],
            ),
            None,
        ),
        # With intervals and time
        (
            _tvn_with_intervals(
                TimeValueNode(datetime(1975, 1, 1)),
                intervals=[Interval(datetime(1970, 1, 1), datetime(2000, 1, 1))],
            ),
            datetime(2014, 9, 12),
        ),
        # With degenerate intervals and time
        (
            _tvn_with_intervals(
                TimeValueNode(datetime(1975, 1, 1)),
                intervals=[Interval(datetime(1975, 1, 1), datetime(1975, 1, 1))],
            ),
            datetime(1976, 1, 1),
        ),
    ],
)
def test_copy_time_value_node(tvn: TimeValueNode, to_time: datetime | None) -> None:
    to_compare = (
        tvn
        if to_time is None
        else _tvn_with_intervals(
            TimeValueNode(to_time),
            [t for t in tvn.intervals if not t.is_degenerate],
        )
    )
    assert to_compare == TimeValueNode.copy(tvn, to_time)


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


@pytest.mark.parametrize(
    "nodes, interval, expected_node_count",
    [
        (
            SortedList([TimeValueNode(time_point=TIME_ZERO.replace(tzinfo=None))]),
            _normal_interval_with_value(value=0),
            1,
        ),
        (
            SortedList(
                [
                    TimeValueNode(time_point=TIME_ZERO),
                    TimeValueNode(time_point=datetime(2024, 12, 1)),
                    TimeValueNode(time_point=datetime(2025, 1, 2)),
                    TimeValueNode(time_point=datetime(2025, 1, 4)),
                ]
            ),
            Interval(start=datetime(2025, 1, 1), end=datetime(2025, 1, 5)),
            3,
        ),
        (
            SortedList(
                [
                    TimeValueNode(time_point=TIME_ZERO),
                    TimeValueNode(time_point=datetime(2024, 12, 1)),
                    TimeValueNode(time_point=datetime(2025, 1, 2)),
                    TimeValueNode(time_point=datetime(2025, 1, 4)),
                    TimeValueNode(time_point=datetime(2025, 1, 6)),
                    TimeValueNode(time_point=datetime(2025, 1, 15)),
                ]
            ),
            Interval(start=datetime(2025, 1, 2), end=datetime(2025, 1, 6)),
            3,
        ),
        (
            SortedList(
                [
                    TimeValueNode(time_point=TIME_ZERO),
                    TimeValueNode(time_point=datetime(2024, 12, 1)),
                    TimeValueNode(time_point=datetime(2025, 1, 2)),
                    TimeValueNode(time_point=datetime(2025, 1, 4)),
                ]
            ),
            Interval(start=datetime(2025, 1, 2), end=datetime(2025, 1, 5)),
            2,
        ),
        (
            SortedList(
                [
                    TimeValueNode(time_point=TIME_ZERO),
                    TimeValueNode(time_point=datetime(2024, 12, 1)),
                    TimeValueNode(time_point=datetime(2025, 1, 2)),
                    TimeValueNode(time_point=datetime(2025, 1, 4)),
                ]
            ),
            Interval(start=datetime(2025, 1, 2, 12), end=datetime(2025, 1, 5)),
            2,
        ),
        (
            SortedList(
                [
                    TimeValueNode(time_point=TIME_ZERO),
                    TimeValueNode(time_point=datetime(2024, 12, 1)),
                    TimeValueNode(time_point=datetime(2025, 1, 2)),
                    TimeValueNode(time_point=datetime(2025, 1, 4)),
                ]
            ),
            Interval(start=datetime(2025, 1, 4), end=datetime(2025, 1, 4)),
            1,
        ),
        (
            SortedList(
                [
                    TimeValueNode(time_point=TIME_ZERO),
                    TimeValueNode(time_point=datetime(2024, 12, 1)),
                    TimeValueNode(time_point=datetime(2025, 1, 2)),
                    TimeValueNode(time_point=datetime(2025, 1, 4)),
                ]
            ),
            Interval(start=datetime(2025, 1, 4, 12), end=datetime(2025, 1, 10)),
            1,
        ),
    ],
)
def test_relevant_nodes(
    nodes,
    interval,
    expected_node_count,
) -> None:
    assert len(_relevant_nodes(nodes, interval)) == expected_node_count


@pytest.mark.parametrize(
    "test_id,time_point,intervals",
    [
        (
            "clone_with_starting_interval",
            datetime(2023, 1, 1),
            [Interval(datetime(2023, 1, 1), datetime(2023, 1, 10), value=5)],
        ),
        (
            "clone_with_ending_interval",
            datetime(2023, 1, 10),
            [Interval(datetime(2023, 1, 1), datetime(2023, 1, 10), value=5)],
        ),
        (
            "clone_with_starting_and_ending_interval",
            datetime(2023, 1, 5),
            [
                Interval(datetime(2023, 1, 5), datetime(2023, 1, 10), value=3),
                Interval(datetime(2023, 1, 1), datetime(2023, 1, 5), value=2),
            ],
        ),
        (
            "clone_with_degenerate_at_time_point",
            datetime(2023, 1, 5),
            [Interval(datetime(2023, 1, 5), datetime(2023, 1, 5), value=100)],
        ),
        (
            "clone_with_multiple_starting_intervals",
            datetime(2023, 1, 1),
            [
                Interval(datetime(2023, 1, 1), datetime(2023, 1, 10), value=5),
                Interval(datetime(2023, 1, 1), datetime(2023, 1, 15), value=3),
            ],
        ),
        (
            "clone_with_multiple_ending_intervals",
            datetime(2023, 1, 10),
            [
                Interval(datetime(2023, 1, 1), datetime(2023, 1, 10), value=5),
                Interval(datetime(2023, 1, 5), datetime(2023, 1, 10), value=3),
            ],
        ),
        (
            "clone_with_overlapping_intervals",
            datetime(2023, 1, 5),
            [
                Interval(datetime(2023, 1, 1), datetime(2023, 1, 10), value=5),
                Interval(datetime(2023, 1, 5), datetime(2023, 1, 15), value=3),
            ],
        ),
        (
            "clone_with_interval_containing_time_point",
            datetime(2023, 1, 5),
            [Interval(datetime(2023, 1, 1), datetime(2023, 1, 10), value=5)],
        ),
    ],
    ids=[
        "clone_with_starting_interval",
        "clone_with_ending_interval",
        "clone_with_starting_and_ending_interval",
        "clone_with_degenerate_at_time_point",
        "clone_with_multiple_starting_intervals",
        "clone_with_multiple_ending_intervals",
        "clone_with_overlapping_intervals",
        "clone_with_interval_containing_time_point",
    ],
)
def test_clone_preserves_starting_and_ending_intervals(
    test_id: str, time_point: datetime, intervals: list[Interval]
) -> None:
    """Test that TimeValueNode.clone preserves starting_intervals and ending_intervals."""
    original = TimeValueNode(time_point=time_point)
    for interval in intervals:
        original._add_interval(interval)

    cloned = TimeValueNode.clone(original)

    # Verify intervals are cloned
    assert cloned.intervals == original.intervals, (
        f"Intervals mismatch for {test_id}: " f"original={original.intervals}, cloned={cloned.intervals}"
    )

    # Verify starting_intervals are cloned
    assert cloned.starting_intervals == original.starting_intervals, (
        f"Starting intervals mismatch for {test_id}: "
        f"original={original.starting_intervals}, cloned={cloned.starting_intervals}"
    )

    # Verify ending_intervals are cloned
    assert cloned.ending_intervals == original.ending_intervals, (
        f"Ending intervals mismatch for {test_id}: "
        f"original={original.ending_intervals}, cloned={cloned.ending_intervals}"
    )

    # Verify cloned lists are independent (same objects, but different containers)
    # The intervals themselves should be the same objects, but the lists should be different
    assert (
        cloned.intervals is not original.intervals
    ), f"Cloned intervals list should be a different object for {test_id}"
    assert (
        cloned.starting_intervals is not original.starting_intervals
    ), f"Cloned starting_intervals list should be a different object for {test_id}"
    assert (
        cloned.ending_intervals is not original.ending_intervals
    ), f"Cloned ending_intervals list should be a different object for {test_id}"


@pytest.mark.parametrize(
    "test_id,time_point,intervals,to_time,expected_starting,expected_ending",
    [
        (
            "clone_with_to_time_at_interval_start",
            datetime(2023, 1, 1),
            [Interval(datetime(2023, 1, 1), datetime(2023, 1, 10), value=5)],
            datetime(2023, 1, 1),
            [Interval(datetime(2023, 1, 1), datetime(2023, 1, 10), value=5)],
            [],
        ),
        (
            "clone_with_to_time_at_interval_end",
            datetime(2023, 1, 10),
            [Interval(datetime(2023, 1, 1), datetime(2023, 1, 10), value=5)],
            datetime(2023, 1, 10),
            [],
            [Interval(datetime(2023, 1, 1), datetime(2023, 1, 10), value=5)],
        ),
        (
            "clone_with_to_time_middle_of_interval",
            datetime(2023, 1, 5),
            [Interval(datetime(2023, 1, 1), datetime(2023, 1, 10), value=5)],
            datetime(2023, 1, 5),
            [],
            [],
        ),
        (
            "clone_with_to_time_multiple_intervals",
            datetime(2023, 1, 1),
            [
                Interval(datetime(2023, 1, 1), datetime(2023, 1, 10), value=5),
                Interval(datetime(2023, 1, 5), datetime(2023, 1, 15), value=3),
            ],
            datetime(2023, 1, 5),
            [Interval(datetime(2023, 1, 5), datetime(2023, 1, 15), value=3)],
            [],
        ),
    ],
    ids=[
        "clone_with_to_time_at_interval_start",
        "clone_with_to_time_at_interval_end",
        "clone_with_to_time_middle_of_interval",
        "clone_with_to_time_multiple_intervals",
    ],
)
def test_copy_recalculates_starting_and_ending_intervals(
    test_id: str,
    time_point: datetime,
    intervals: list[Interval],
    to_time: datetime,
    expected_starting: list[Interval],
    expected_ending: list[Interval],
) -> None:
    """Test that TimeValueNode.clone with to_time recalculates starting_intervals and ending_intervals ."""
    original = TimeValueNode(time_point=time_point)
    for interval in intervals:
        original._add_interval(interval)

    cloned = TimeValueNode.copy(original, to=to_time)

    # When cloning with to_time, starting_intervals and ending_intervals should be recalculated
    # based on the new time_point (to_time), not preserved from the original
    assert cloned.starting_intervals == expected_starting, (
        f"Starting intervals mismatch for {test_id}: " f"expected={expected_starting}, got={cloned.starting_intervals}"
    )

    assert cloned.ending_intervals == expected_ending, (
        f"Ending intervals mismatch for {test_id}: " f"expected={expected_ending}, got={cloned.ending_intervals}"
    )
