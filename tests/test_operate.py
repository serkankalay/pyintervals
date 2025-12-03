from collections.abc import Callable
from datetime import datetime, timedelta

import pytest
import operator

from pyintervals import IntervalHandler, Interval
from pyintervals.constants import TIME_ZERO
from pyintervals.interval_handler import _operate

T_ZERO = datetime(2025, 1, 1)

@pytest.mark.parametrize(
    "operand, a, b, expected",
    [
        pytest.param(
            operator.add,
            IntervalHandler(intervals=[Interval(T_ZERO - timedelta(days=3), T_ZERO + timedelta(days=3), value=10)]),
            IntervalHandler(intervals=[Interval(T_ZERO - timedelta(days=1), T_ZERO + timedelta(days=1), value=5)]),
            IntervalHandler(intervals=[
                Interval(TIME_ZERO, T_ZERO - timedelta(days=3), value=0),
                Interval(T_ZERO - timedelta(days=3), T_ZERO - timedelta(days=1), value=10),
                Interval(T_ZERO - timedelta(days=1), T_ZERO + timedelta(days=1), value=15),
                Interval(T_ZERO + timedelta(days=1), T_ZERO + timedelta(days=3), value=10),
            ]),
            id="Adding two IntervalHandlers. One is contained completely within the other."
        ),
        pytest.param(
            operator.add,
            IntervalHandler(intervals=[Interval(T_ZERO - timedelta(days=3), T_ZERO + timedelta(days=3), value=10)]),
            IntervalHandler(intervals=[Interval(T_ZERO + timedelta(days=1), T_ZERO + timedelta(days=5), value=5)]),
            IntervalHandler(intervals=[
                Interval(TIME_ZERO, T_ZERO - timedelta(days=3), value=0),
                Interval(T_ZERO - timedelta(days=3), T_ZERO + timedelta(days=1), value=10),
                Interval(T_ZERO + timedelta(days=1), T_ZERO + timedelta(days=3), value=15),
                Interval(T_ZERO + timedelta(days=3), T_ZERO + timedelta(days=5), value=5),
            ]),
            id="Adding two IntervalHandlers. One overlaps partially with the other."
        ),
        pytest.param(
            operator.add,
            IntervalHandler(intervals=[Interval(T_ZERO - timedelta(days=3), T_ZERO + timedelta(days=3), value=10)]),
            IntervalHandler(intervals=[Interval(T_ZERO + timedelta(days=3), T_ZERO + timedelta(days=5), value=5)]),
            IntervalHandler(intervals=[
                Interval(TIME_ZERO, T_ZERO - timedelta(days=3), value=0),
                Interval(T_ZERO - timedelta(days=3), T_ZERO + timedelta(days=3), value=10),
                Interval(T_ZERO + timedelta(days=3), T_ZERO + timedelta(days=5), value=5),
            ]),
            id="Adding two IntervalHandlers. One is adjacent to the other."
        ),
        pytest.param(
            operator.add,
            IntervalHandler(intervals=[Interval(T_ZERO - timedelta(days=3), T_ZERO + timedelta(days=3), value=10)]),
            IntervalHandler(intervals=[Interval(T_ZERO + timedelta(days=5), T_ZERO + timedelta(days=10), value=5)]),
            IntervalHandler(intervals=[
                Interval(TIME_ZERO, T_ZERO - timedelta(days=3), value=0),
                Interval(T_ZERO - timedelta(days=3), T_ZERO + timedelta(days=3), value=10),
                Interval(T_ZERO + timedelta(days=3), T_ZERO + timedelta(days=5), value=0),
                Interval(T_ZERO + timedelta(days=5), T_ZERO + timedelta(days=10), value=5),
            ]),
            id="Adding two IntervalHandlers. One is disjoint from the other."
        ),
    ]
)
def test_operate(
    operand: Callable[[float, float], float],
    a: IntervalHandler,
    b: IntervalHandler,
    expected: IntervalHandler,
) -> None:
    result = _operate(a, b, operand)
    assert result == expected
