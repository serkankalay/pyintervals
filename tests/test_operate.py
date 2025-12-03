from collections.abc import Callable
from datetime import datetime, timedelta

import pytest
import operator

from pyintervals import IntervalHandler, Interval
from pyintervals.constants import TIME_ZERO
from pyintervals.interval_handler import _operate

T_ZERO = datetime(2025, 1, 1)

IN_PLACE_OPERAND_MAPPING = {
    operator.add: operator.iadd,
    operator.sub: operator.isub,
    operator.mul: operator.imul,
    operator.truediv: operator.itruediv,
}

@pytest.mark.parametrize(
    "operand, a, b, expected",
    [
        pytest.param(
            operator.add,
            IntervalHandler(intervals=[Interval(T_ZERO - timedelta(days=3), T_ZERO + timedelta(days=3), value=10)]),
            IntervalHandler(intervals=[Interval(T_ZERO - timedelta(days=3), T_ZERO + timedelta(days=3), value=5)]),
            IntervalHandler(intervals=[
                Interval(TIME_ZERO, T_ZERO - timedelta(days=3), value=0),
                Interval(T_ZERO - timedelta(days=3), T_ZERO + timedelta(days=3), value=15),
            ]),
            id="adding two IntervalHandlers. They both have the exact same domain."
        ),
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
            id="adding two IntervalHandlers. One is contained completely within the other."
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
            id="adding two IntervalHandlers. One overlaps partially with the other."
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
            id="adding two IntervalHandlers. One is adjacent to the other."
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
            id="adding two IntervalHandlers. One is disjoint from the other."
        ),
        pytest.param(
            operator.sub,
            IntervalHandler(intervals=[Interval(T_ZERO - timedelta(days=3), T_ZERO + timedelta(days=3), value=10)]),
            IntervalHandler(intervals=[Interval(T_ZERO - timedelta(days=3), T_ZERO + timedelta(days=3), value=5)]),
            IntervalHandler(intervals=[
                Interval(TIME_ZERO, T_ZERO - timedelta(days=3), value=0),
                Interval(T_ZERO - timedelta(days=3), T_ZERO + timedelta(days=3), value=5),
            ]),
            id="subtracting two IntervalHandlers. They both have the exact same domain."
        ),
        pytest.param(
            operator.sub,
            IntervalHandler(intervals=[Interval(T_ZERO - timedelta(days=3), T_ZERO + timedelta(days=3), value=10)]),
            IntervalHandler(intervals=[Interval(T_ZERO - timedelta(days=1), T_ZERO + timedelta(days=1), value=5)]),
            IntervalHandler(intervals=[
                Interval(TIME_ZERO, T_ZERO - timedelta(days=3), value=0),
                Interval(T_ZERO - timedelta(days=3), T_ZERO - timedelta(days=1), value=10),
                Interval(T_ZERO - timedelta(days=1), T_ZERO + timedelta(days=1), value=5),
                Interval(T_ZERO + timedelta(days=1), T_ZERO + timedelta(days=3), value=10),
            ]),
            id="subtracting two IntervalHandlers. One is contained completely within the other."
        ),
        pytest.param(
            operator.sub,
            IntervalHandler(intervals=[Interval(T_ZERO - timedelta(days=3), T_ZERO + timedelta(days=3), value=10)]),
            IntervalHandler(intervals=[Interval(T_ZERO + timedelta(days=1), T_ZERO + timedelta(days=5), value=5)]),
            IntervalHandler(intervals=[
                Interval(TIME_ZERO, T_ZERO - timedelta(days=3), value=0),
                Interval(T_ZERO - timedelta(days=3), T_ZERO + timedelta(days=1), value=10),
                Interval(T_ZERO + timedelta(days=1), T_ZERO + timedelta(days=3), value=5),
                Interval(T_ZERO + timedelta(days=3), T_ZERO + timedelta(days=5), value=-5),
            ]),
            id="subtracting two IntervalHandlers. One overlaps partially with the other."
        ),
        pytest.param(
            operator.sub,
            IntervalHandler(intervals=[Interval(T_ZERO - timedelta(days=3), T_ZERO + timedelta(days=3), value=10)]),
            IntervalHandler(intervals=[Interval(T_ZERO + timedelta(days=3), T_ZERO + timedelta(days=5), value=5)]),
            IntervalHandler(intervals=[
                Interval(TIME_ZERO, T_ZERO - timedelta(days=3), value=0),
                Interval(T_ZERO - timedelta(days=3), T_ZERO + timedelta(days=3), value=10),
                Interval(T_ZERO + timedelta(days=3), T_ZERO + timedelta(days=5), value=-5),
            ]),
            id="subtracting two IntervalHandlers. One is adjacent to the other."
        ),
        pytest.param(
            operator.sub,
            IntervalHandler(intervals=[Interval(T_ZERO - timedelta(days=3), T_ZERO + timedelta(days=3), value=10)]),
            IntervalHandler(intervals=[Interval(T_ZERO + timedelta(days=5), T_ZERO + timedelta(days=10), value=5)]),
            IntervalHandler(intervals=[
                Interval(TIME_ZERO, T_ZERO - timedelta(days=3), value=0),
                Interval(T_ZERO - timedelta(days=3), T_ZERO + timedelta(days=3), value=10),
                Interval(T_ZERO + timedelta(days=3), T_ZERO + timedelta(days=5), value=0),
                Interval(T_ZERO + timedelta(days=5), T_ZERO + timedelta(days=10), value=-5),
            ]),
            id="subtracting two IntervalHandlers. One is disjoint from the other."
        ),
        pytest.param(
            operator.mul,
            IntervalHandler(intervals=[Interval(T_ZERO - timedelta(days=3), T_ZERO + timedelta(days=3), value=10)]),
            IntervalHandler(intervals=[Interval(T_ZERO - timedelta(days=3), T_ZERO + timedelta(days=3), value=5)]),
            IntervalHandler(intervals=[
                Interval(TIME_ZERO, T_ZERO - timedelta(days=3), value=0),
                Interval(T_ZERO - timedelta(days=3), T_ZERO + timedelta(days=3), value=50),
            ]),
            id="multiplying two IntervalHandlers. They both have the exact same domain."
        ),
        pytest.param(
            operator.mul,
            IntervalHandler(intervals=[Interval(T_ZERO - timedelta(days=3), T_ZERO + timedelta(days=3), value=10)]),
            IntervalHandler(intervals=[Interval(T_ZERO - timedelta(days=1), T_ZERO + timedelta(days=1), value=5)]),
            IntervalHandler(intervals=[
                Interval(TIME_ZERO, T_ZERO - timedelta(days=3), value=0),
                Interval(T_ZERO - timedelta(days=3), T_ZERO - timedelta(days=1), value=0),
                Interval(T_ZERO - timedelta(days=1), T_ZERO + timedelta(days=1), value=50),
                Interval(T_ZERO + timedelta(days=1), T_ZERO + timedelta(days=3), value=0),
            ]),
            id="multiplying two IntervalHandlers. One is contained completely within the other."
        ),
        pytest.param(
            operator.mul,
            IntervalHandler(intervals=[Interval(T_ZERO - timedelta(days=3), T_ZERO + timedelta(days=3), value=10)]),
            IntervalHandler(intervals=[Interval(T_ZERO + timedelta(days=1), T_ZERO + timedelta(days=5), value=5)]),
            IntervalHandler(intervals=[
                Interval(TIME_ZERO, T_ZERO - timedelta(days=3), value=0),
                Interval(T_ZERO - timedelta(days=3), T_ZERO + timedelta(days=1), value=0),
                Interval(T_ZERO + timedelta(days=1), T_ZERO + timedelta(days=3), value=50),
                Interval(T_ZERO + timedelta(days=3), T_ZERO + timedelta(days=5), value=0),
            ]),
            id="multiplying two IntervalHandlers. One overlaps partially with the other."
        ),
        pytest.param(
            operator.mul,
            IntervalHandler(intervals=[Interval(T_ZERO - timedelta(days=3), T_ZERO + timedelta(days=3), value=10)]),
            IntervalHandler(intervals=[Interval(T_ZERO + timedelta(days=3), T_ZERO + timedelta(days=5), value=5)]),
            IntervalHandler(intervals=[
                Interval(TIME_ZERO, T_ZERO - timedelta(days=3), value=0),
                Interval(T_ZERO - timedelta(days=3), T_ZERO + timedelta(days=3), value=0),
                Interval(T_ZERO + timedelta(days=3), T_ZERO + timedelta(days=5), value=0),
            ]),
            id="multiplying two IntervalHandlers. One is adjacent to the other."
        ),
        pytest.param(
            operator.mul,
            IntervalHandler(intervals=[Interval(T_ZERO - timedelta(days=3), T_ZERO + timedelta(days=3), value=10)]),
            IntervalHandler(intervals=[Interval(T_ZERO + timedelta(days=5), T_ZERO + timedelta(days=10), value=5)]),
            IntervalHandler(intervals=[
                Interval(TIME_ZERO, T_ZERO - timedelta(days=3), value=0),
                Interval(T_ZERO - timedelta(days=3), T_ZERO + timedelta(days=3), value=0),
                Interval(T_ZERO + timedelta(days=3), T_ZERO + timedelta(days=5), value=0),
                Interval(T_ZERO + timedelta(days=5), T_ZERO + timedelta(days=10), value=0),
            ]),
            id="multiplying two IntervalHandlers. One is disjoint from the other."
        ),
    ]
)
@pytest.mark.parametrize(
    "is_in_place",
    [
        pytest.param(
            False,
            id="Regular"
        ),
        pytest.param(
            True,
            id="In-place"
        ),
    ]
)
def test_operate(
    operand: Callable[[float, float], float],
    a: IntervalHandler,
    b: IntervalHandler,
    is_in_place: bool,
    expected: IntervalHandler,
) -> None:
    if is_in_place:
        in_place_operand = IN_PLACE_OPERAND_MAPPING[operand]
        method = getattr(a, f"__{in_place_operand.__name__}__")
        method(b)
        assert a == expected
    else:
        method = getattr(a, f"__{operand.__name__}__")
        result = method(b)
        assert result == expected

