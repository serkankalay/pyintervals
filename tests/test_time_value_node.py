from datetime import datetime

import pytest

from pyintervals.time_value_node import TimeValueNode


@pytest.mark.parametrize(
    "tvn, other, is_equal",
    [
        (
            TimeValueNode(datetime(1973, 1, 1)),
            TimeValueNode(datetime(1973, 1, 1)),
            True,
        ),
        (
            TimeValueNode(datetime(1973, 1, 1)),
            TimeValueNode(datetime(1974, 1, 1)),
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
