from __future__ import annotations

import operator
from collections.abc import Callable
from datetime import datetime, timedelta
from typing import Union

import pytest

from pyintervals import Interval, IntervalHandler
from pyintervals.constants import TIME_ZERO

T_NOW = datetime(2025, 1, 1)

IN_PLACE_OPERAND_MAPPING = {
    operator.add: operator.iadd,
    operator.sub: operator.isub,
    operator.mul: operator.imul,
    operator.truediv: operator.itruediv,
}


@pytest.mark.parametrize(
    "operand, a, b, expected_error_type, expected",
    [
        pytest.param(
            operator.add,
            IntervalHandler(
                intervals=[
                    Interval(
                        T_NOW - timedelta(days=3),
                        T_NOW + timedelta(days=3),
                        value=10,
                    )
                ]
            ),
            IntervalHandler(
                intervals=[
                    Interval(
                        T_NOW - timedelta(days=3),
                        T_NOW + timedelta(days=3),
                        value=5,
                    )
                ]
            ),
            None,  # No error expected
            IntervalHandler(
                intervals=[
                    Interval(TIME_ZERO, T_NOW - timedelta(days=3), value=0),
                    Interval(
                        T_NOW - timedelta(days=3),
                        T_NOW + timedelta(days=3),
                        value=15,
                    ),
                ]
            ),
            id="adding two IntervalHandlers. They both have the exact same domain.",
        ),
        pytest.param(
            operator.add,
            IntervalHandler(
                intervals=[
                    Interval(
                        T_NOW - timedelta(days=3),
                        T_NOW + timedelta(days=3),
                        value=10,
                    )
                ]
            ),
            IntervalHandler(
                intervals=[
                    Interval(
                        T_NOW - timedelta(days=1),
                        T_NOW + timedelta(days=1),
                        value=5,
                    )
                ]
            ),
            None,  # No error expected
            IntervalHandler(
                intervals=[
                    Interval(TIME_ZERO, T_NOW - timedelta(days=3), value=0),
                    Interval(
                        T_NOW - timedelta(days=3),
                        T_NOW - timedelta(days=1),
                        value=10,
                    ),
                    Interval(
                        T_NOW - timedelta(days=1),
                        T_NOW + timedelta(days=1),
                        value=15,
                    ),
                    Interval(
                        T_NOW + timedelta(days=1),
                        T_NOW + timedelta(days=3),
                        value=10,
                    ),
                ]
            ),
            id="adding two IntervalHandlers. One is contained completely within the other.",
        ),
        pytest.param(
            operator.add,
            IntervalHandler(
                intervals=[
                    Interval(
                        T_NOW - timedelta(days=3),
                        T_NOW + timedelta(days=3),
                        value=10,
                    )
                ]
            ),
            IntervalHandler(
                intervals=[
                    Interval(
                        T_NOW + timedelta(days=1),
                        T_NOW + timedelta(days=5),
                        value=5,
                    )
                ]
            ),
            None,  # No error expected
            IntervalHandler(
                intervals=[
                    Interval(TIME_ZERO, T_NOW - timedelta(days=3), value=0),
                    Interval(
                        T_NOW - timedelta(days=3),
                        T_NOW + timedelta(days=1),
                        value=10,
                    ),
                    Interval(
                        T_NOW + timedelta(days=1),
                        T_NOW + timedelta(days=3),
                        value=15,
                    ),
                    Interval(
                        T_NOW + timedelta(days=3),
                        T_NOW + timedelta(days=5),
                        value=5,
                    ),
                ]
            ),
            id="adding two IntervalHandlers. One overlaps partially with the other.",
        ),
        pytest.param(
            operator.add,
            IntervalHandler(
                intervals=[
                    Interval(
                        T_NOW - timedelta(days=3),
                        T_NOW + timedelta(days=3),
                        value=10,
                    )
                ]
            ),
            IntervalHandler(
                intervals=[
                    Interval(
                        T_NOW + timedelta(days=3),
                        T_NOW + timedelta(days=5),
                        value=5,
                    )
                ]
            ),
            None,  # No error expected
            IntervalHandler(
                intervals=[
                    Interval(TIME_ZERO, T_NOW - timedelta(days=3), value=0),
                    Interval(
                        T_NOW - timedelta(days=3),
                        T_NOW + timedelta(days=3),
                        value=10,
                    ),
                    Interval(
                        T_NOW + timedelta(days=3),
                        T_NOW + timedelta(days=5),
                        value=5,
                    ),
                ]
            ),
            id="adding two IntervalHandlers. One is adjacent to the other.",
        ),
        pytest.param(
            operator.add,
            IntervalHandler(
                intervals=[
                    Interval(
                        T_NOW - timedelta(days=3),
                        T_NOW + timedelta(days=3),
                        value=10,
                    )
                ]
            ),
            IntervalHandler(
                intervals=[
                    Interval(
                        T_NOW + timedelta(days=5),
                        T_NOW + timedelta(days=10),
                        value=5,
                    )
                ]
            ),
            None,  # No error expected
            IntervalHandler(
                intervals=[
                    Interval(TIME_ZERO, T_NOW - timedelta(days=3), value=0),
                    Interval(
                        T_NOW - timedelta(days=3),
                        T_NOW + timedelta(days=3),
                        value=10,
                    ),
                    Interval(
                        T_NOW + timedelta(days=3),
                        T_NOW + timedelta(days=5),
                        value=0,
                    ),
                    Interval(
                        T_NOW + timedelta(days=5),
                        T_NOW + timedelta(days=10),
                        value=5,
                    ),
                ]
            ),
            id="adding two IntervalHandlers. One is disjoint from the other.",
        ),
        pytest.param(
            operator.sub,
            IntervalHandler(
                intervals=[
                    Interval(
                        T_NOW - timedelta(days=3),
                        T_NOW + timedelta(days=3),
                        value=10,
                    )
                ]
            ),
            IntervalHandler(
                intervals=[
                    Interval(
                        T_NOW - timedelta(days=3),
                        T_NOW + timedelta(days=3),
                        value=5,
                    )
                ]
            ),
            None,  # No error expected
            IntervalHandler(
                intervals=[
                    Interval(TIME_ZERO, T_NOW - timedelta(days=3), value=0),
                    Interval(
                        T_NOW - timedelta(days=3),
                        T_NOW + timedelta(days=3),
                        value=5,
                    ),
                ]
            ),
            id="subtracting two IntervalHandlers. They both have the exact same domain.",
        ),
        pytest.param(
            operator.sub,
            IntervalHandler(
                intervals=[
                    Interval(
                        T_NOW - timedelta(days=3),
                        T_NOW + timedelta(days=3),
                        value=10,
                    )
                ]
            ),
            IntervalHandler(
                intervals=[
                    Interval(
                        T_NOW - timedelta(days=1),
                        T_NOW + timedelta(days=1),
                        value=5,
                    )
                ]
            ),
            None,  # No error expected
            IntervalHandler(
                intervals=[
                    Interval(TIME_ZERO, T_NOW - timedelta(days=3), value=0),
                    Interval(
                        T_NOW - timedelta(days=3),
                        T_NOW - timedelta(days=1),
                        value=10,
                    ),
                    Interval(
                        T_NOW - timedelta(days=1),
                        T_NOW + timedelta(days=1),
                        value=5,
                    ),
                    Interval(
                        T_NOW + timedelta(days=1),
                        T_NOW + timedelta(days=3),
                        value=10,
                    ),
                ]
            ),
            id="subtracting two IntervalHandlers. One is contained completely within the other.",
        ),
        pytest.param(
            operator.sub,
            IntervalHandler(
                intervals=[
                    Interval(
                        T_NOW - timedelta(days=3),
                        T_NOW + timedelta(days=3),
                        value=10,
                    )
                ]
            ),
            IntervalHandler(
                intervals=[
                    Interval(
                        T_NOW + timedelta(days=1),
                        T_NOW + timedelta(days=5),
                        value=5,
                    )
                ]
            ),
            None,  # No error expected
            IntervalHandler(
                intervals=[
                    Interval(TIME_ZERO, T_NOW - timedelta(days=3), value=0),
                    Interval(
                        T_NOW - timedelta(days=3),
                        T_NOW + timedelta(days=1),
                        value=10,
                    ),
                    Interval(
                        T_NOW + timedelta(days=1),
                        T_NOW + timedelta(days=3),
                        value=5,
                    ),
                    Interval(
                        T_NOW + timedelta(days=3),
                        T_NOW + timedelta(days=5),
                        value=-5,
                    ),
                ]
            ),
            id="subtracting two IntervalHandlers. One overlaps partially with the other.",
        ),
        pytest.param(
            operator.sub,
            IntervalHandler(
                intervals=[
                    Interval(
                        T_NOW - timedelta(days=3),
                        T_NOW + timedelta(days=3),
                        value=10,
                    )
                ]
            ),
            IntervalHandler(
                intervals=[
                    Interval(
                        T_NOW + timedelta(days=3),
                        T_NOW + timedelta(days=5),
                        value=5,
                    )
                ]
            ),
            None,  # No error expected
            IntervalHandler(
                intervals=[
                    Interval(TIME_ZERO, T_NOW - timedelta(days=3), value=0),
                    Interval(
                        T_NOW - timedelta(days=3),
                        T_NOW + timedelta(days=3),
                        value=10,
                    ),
                    Interval(
                        T_NOW + timedelta(days=3),
                        T_NOW + timedelta(days=5),
                        value=-5,
                    ),
                ]
            ),
            id="subtracting two IntervalHandlers. One is adjacent to the other.",
        ),
        pytest.param(
            operator.sub,
            IntervalHandler(
                intervals=[
                    Interval(
                        T_NOW - timedelta(days=3),
                        T_NOW + timedelta(days=3),
                        value=10,
                    )
                ]
            ),
            IntervalHandler(
                intervals=[
                    Interval(
                        T_NOW + timedelta(days=5),
                        T_NOW + timedelta(days=10),
                        value=5,
                    )
                ]
            ),
            None,  # No error expected
            IntervalHandler(
                intervals=[
                    Interval(TIME_ZERO, T_NOW - timedelta(days=3), value=0),
                    Interval(
                        T_NOW - timedelta(days=3),
                        T_NOW + timedelta(days=3),
                        value=10,
                    ),
                    Interval(
                        T_NOW + timedelta(days=3),
                        T_NOW + timedelta(days=5),
                        value=0,
                    ),
                    Interval(
                        T_NOW + timedelta(days=5),
                        T_NOW + timedelta(days=10),
                        value=-5,
                    ),
                ]
            ),
            id="subtracting two IntervalHandlers. One is disjoint from the other.",
        ),
        pytest.param(
            operator.mul,
            IntervalHandler(
                intervals=[
                    Interval(
                        T_NOW - timedelta(days=3),
                        T_NOW + timedelta(days=3),
                        value=10,
                    )
                ]
            ),
            IntervalHandler(
                intervals=[
                    Interval(
                        T_NOW - timedelta(days=3),
                        T_NOW + timedelta(days=3),
                        value=5,
                    )
                ]
            ),
            None,  # No error expected
            IntervalHandler(
                intervals=[
                    Interval(TIME_ZERO, T_NOW - timedelta(days=3), value=0),
                    Interval(
                        T_NOW - timedelta(days=3),
                        T_NOW + timedelta(days=3),
                        value=50,
                    ),
                ]
            ),
            id="multiplying two IntervalHandlers. They both have the exact same domain.",
        ),
        pytest.param(
            operator.mul,
            IntervalHandler(
                intervals=[
                    Interval(
                        T_NOW - timedelta(days=3),
                        T_NOW + timedelta(days=3),
                        value=10,
                    )
                ]
            ),
            IntervalHandler(
                intervals=[
                    Interval(
                        T_NOW - timedelta(days=1),
                        T_NOW + timedelta(days=1),
                        value=5,
                    )
                ]
            ),
            None,  # No error expected
            IntervalHandler(
                intervals=[
                    Interval(TIME_ZERO, T_NOW - timedelta(days=3), value=0),
                    Interval(
                        T_NOW - timedelta(days=3),
                        T_NOW - timedelta(days=1),
                        value=0,
                    ),
                    Interval(
                        T_NOW - timedelta(days=1),
                        T_NOW + timedelta(days=1),
                        value=50,
                    ),
                    Interval(
                        T_NOW + timedelta(days=1),
                        T_NOW + timedelta(days=3),
                        value=0,
                    ),
                ]
            ),
            id="multiplying two IntervalHandlers. One is contained completely within the other.",
        ),
        pytest.param(
            operator.mul,
            IntervalHandler(
                intervals=[
                    Interval(
                        T_NOW - timedelta(days=3),
                        T_NOW + timedelta(days=3),
                        value=10,
                    )
                ]
            ),
            IntervalHandler(
                intervals=[
                    Interval(
                        T_NOW + timedelta(days=1),
                        T_NOW + timedelta(days=5),
                        value=5,
                    )
                ]
            ),
            None,  # No error expected
            IntervalHandler(
                intervals=[
                    Interval(TIME_ZERO, T_NOW - timedelta(days=3), value=0),
                    Interval(
                        T_NOW - timedelta(days=3),
                        T_NOW + timedelta(days=1),
                        value=0,
                    ),
                    Interval(
                        T_NOW + timedelta(days=1),
                        T_NOW + timedelta(days=3),
                        value=50,
                    ),
                    Interval(
                        T_NOW + timedelta(days=3),
                        T_NOW + timedelta(days=5),
                        value=0,
                    ),
                ]
            ),
            id="multiplying two IntervalHandlers. One overlaps partially with the other.",
        ),
        pytest.param(
            operator.mul,
            IntervalHandler(
                intervals=[
                    Interval(
                        T_NOW - timedelta(days=3),
                        T_NOW + timedelta(days=3),
                        value=10,
                    )
                ]
            ),
            IntervalHandler(
                intervals=[
                    Interval(
                        T_NOW + timedelta(days=3),
                        T_NOW + timedelta(days=5),
                        value=5,
                    )
                ]
            ),
            None,  # No error expected
            IntervalHandler(
                intervals=[
                    Interval(TIME_ZERO, T_NOW - timedelta(days=3), value=0),
                    Interval(
                        T_NOW - timedelta(days=3),
                        T_NOW + timedelta(days=3),
                        value=0,
                    ),
                    Interval(
                        T_NOW + timedelta(days=3),
                        T_NOW + timedelta(days=5),
                        value=0,
                    ),
                ]
            ),
            id="multiplying two IntervalHandlers. One is adjacent to the other.",
        ),
        pytest.param(
            operator.mul,
            IntervalHandler(
                intervals=[
                    Interval(
                        T_NOW - timedelta(days=3),
                        T_NOW + timedelta(days=3),
                        value=10,
                    )
                ]
            ),
            IntervalHandler(
                intervals=[
                    Interval(
                        T_NOW + timedelta(days=5),
                        T_NOW + timedelta(days=10),
                        value=5,
                    )
                ]
            ),
            None,  # No error expected
            IntervalHandler(
                intervals=[
                    Interval(TIME_ZERO, T_NOW - timedelta(days=3), value=0),
                    Interval(
                        T_NOW - timedelta(days=3),
                        T_NOW + timedelta(days=3),
                        value=0,
                    ),
                    Interval(
                        T_NOW + timedelta(days=3),
                        T_NOW + timedelta(days=5),
                        value=0,
                    ),
                    Interval(
                        T_NOW + timedelta(days=5),
                        T_NOW + timedelta(days=10),
                        value=0,
                    ),
                ]
            ),
            id="multiplying two IntervalHandlers. One is disjoint from the other.",
        ),
        pytest.param(
            operator.truediv,
            IntervalHandler(
                intervals=[
                    Interval(
                        T_NOW - timedelta(days=3),
                        T_NOW + timedelta(days=3),
                        value=10,
                    )
                ]
            ),
            IntervalHandler(
                intervals=[
                    Interval(
                        T_NOW - timedelta(days=3),
                        T_NOW + timedelta(days=3),
                        value=5,
                    )
                ]
            ),
            ZeroDivisionError,
            None,
            id="dividing two IntervalHandlers. They both have the exact same domain. "
            "Where the value of the denominator is zero, there will be a zero division error.",
        ),
        pytest.param(
            operator.truediv,
            IntervalHandler(
                intervals=[
                    Interval(
                        T_NOW - timedelta(days=3),
                        T_NOW + timedelta(days=3),
                        value=10,
                    )
                ]
            ),
            IntervalHandler(
                intervals=[
                    Interval(
                        T_NOW - timedelta(days=1),
                        T_NOW + timedelta(days=1),
                        value=5,
                    )
                ]
            ),
            ZeroDivisionError,
            None,
            id="dividing two IntervalHandlers. One is contained completely within the other. "
            "Where the intervals don't overlap and where the value of the denominator is zero, "
            "there will be a zero division error.",
        ),
        pytest.param(
            operator.truediv,
            IntervalHandler(
                intervals=[
                    Interval(
                        T_NOW - timedelta(days=3),
                        T_NOW + timedelta(days=3),
                        value=10,
                    )
                ]
            ),
            IntervalHandler(
                intervals=[
                    Interval(
                        T_NOW + timedelta(days=1),
                        T_NOW + timedelta(days=5),
                        value=5,
                    )
                ]
            ),
            ZeroDivisionError,
            None,
            id="dividing two IntervalHandlers. One is contained completely within the other. "
            "Where the intervals don't overlap and where the value of the denominator is zero, "
            "there will be a zero division error.",
        ),
        pytest.param(
            operator.truediv,
            IntervalHandler(
                intervals=[
                    Interval(
                        T_NOW - timedelta(days=3),
                        T_NOW + timedelta(days=3),
                        value=10,
                    )
                ]
            ),
            IntervalHandler(
                intervals=[
                    Interval(
                        T_NOW + timedelta(days=3),
                        T_NOW + timedelta(days=5),
                        value=5,
                    )
                ]
            ),
            ZeroDivisionError,
            None,
            id="dividing two IntervalHandlers. One is contained completely within the other. "
            "Where the intervals don't overlap and where the value of the denominator is zero, "
            "there will be a zero division error.",
        ),
        pytest.param(
            operator.truediv,
            IntervalHandler(
                intervals=[
                    Interval(
                        T_NOW - timedelta(days=3),
                        T_NOW + timedelta(days=3),
                        value=10,
                    )
                ]
            ),
            IntervalHandler(
                intervals=[
                    Interval(
                        T_NOW + timedelta(days=5),
                        T_NOW + timedelta(days=10),
                        value=5,
                    )
                ]
            ),
            ZeroDivisionError,
            None,
            id="dividing two IntervalHandlers. One is contained completely within the other. "
            "Where the intervals don't overlap and where the value of the denominator is zero, "
            "there will be a zero division error.",
        ),
        pytest.param(
            operator.truediv,
            IntervalHandler(
                intervals=[
                    Interval(
                        T_NOW - timedelta(days=3),
                        T_NOW + timedelta(days=3),
                        value=10,
                    )
                ]
            ),
            IntervalHandler(
                intervals=[
                    Interval(TIME_ZERO, datetime.max, value=1),
                    Interval(
                        T_NOW - timedelta(days=3),
                        T_NOW + timedelta(days=3),
                        value=4,
                    ),
                ]
            ),
            None,  # No error expected,
            IntervalHandler(
                intervals=[
                    Interval(TIME_ZERO, T_NOW - timedelta(days=3), value=0),
                    Interval(
                        T_NOW - timedelta(days=3),
                        T_NOW + timedelta(days=3),
                        value=2,
                    ),
                    Interval(T_NOW + timedelta(days=3), datetime.max, value=0),
                ]
            ),
            id="dividing two IntervalHandlers. They both have the exact same domain. "
            "To prevent `ZeroDivisionError`, a 'baseline' value of 1 "
            "is added to the denominating `IntervalHandler`.",
        ),
        pytest.param(
            operator.truediv,
            IntervalHandler(
                intervals=[
                    Interval(
                        T_NOW - timedelta(days=3),
                        T_NOW + timedelta(days=3),
                        value=10,
                    )
                ]
            ),
            IntervalHandler(
                intervals=[
                    Interval(TIME_ZERO, datetime.max, value=1),
                    Interval(
                        T_NOW - timedelta(days=1),
                        T_NOW + timedelta(days=1),
                        value=4,
                    ),
                ]
            ),
            None,  # No error expected,
            IntervalHandler(
                intervals=[
                    Interval(TIME_ZERO, T_NOW - timedelta(days=3), value=0),
                    Interval(
                        T_NOW - timedelta(days=3),
                        T_NOW - timedelta(days=1),
                        value=10,
                    ),
                    Interval(
                        T_NOW - timedelta(days=1),
                        T_NOW + timedelta(days=1),
                        value=2,
                    ),
                    Interval(
                        T_NOW + timedelta(days=1),
                        T_NOW + timedelta(days=3),
                        value=10,
                    ),
                    Interval(T_NOW + timedelta(days=3), datetime.max, value=0),
                ]
            ),
            id="dividing two IntervalHandlers. They both have the exact same domain. "
            "To prevent `ZeroDivisionError`, a 'baseline' value of 1 "
            "is added to the denominating `IntervalHandler`.",
        ),
        pytest.param(
            operator.truediv,
            IntervalHandler(
                intervals=[
                    Interval(
                        T_NOW - timedelta(days=3),
                        T_NOW + timedelta(days=3),
                        value=10,
                    )
                ]
            ),
            IntervalHandler(
                intervals=[
                    Interval(TIME_ZERO, datetime.max, value=1),
                    Interval(
                        T_NOW + timedelta(days=1),
                        T_NOW + timedelta(days=5),
                        value=4,
                    ),
                ]
            ),
            None,  # No error expected,
            IntervalHandler(
                intervals=[
                    Interval(TIME_ZERO, T_NOW - timedelta(days=3), value=0),
                    Interval(
                        T_NOW - timedelta(days=3),
                        T_NOW + timedelta(days=1),
                        value=10,
                    ),
                    Interval(
                        T_NOW + timedelta(days=1),
                        T_NOW + timedelta(days=3),
                        value=2,
                    ),
                    Interval(
                        T_NOW + timedelta(days=3),
                        T_NOW + timedelta(days=5),
                        value=0,
                    ),
                    Interval(T_NOW + timedelta(days=5), datetime.max, value=0),
                ]
            ),
            id="dividing two IntervalHandlers. They both have the exact same domain. "
            "To prevent `ZeroDivisionError`, a 'baseline' value of 1 "
            "is added to the denominating `IntervalHandler`.",
        ),
        pytest.param(
            operator.truediv,
            IntervalHandler(
                intervals=[
                    Interval(
                        T_NOW - timedelta(days=3),
                        T_NOW + timedelta(days=3),
                        value=10,
                    )
                ]
            ),
            IntervalHandler(
                intervals=[
                    Interval(TIME_ZERO, datetime.max, value=1),
                    Interval(
                        T_NOW + timedelta(days=3),
                        T_NOW + timedelta(days=5),
                        value=4,
                    ),
                ]
            ),
            None,  # No error expected,
            IntervalHandler(
                intervals=[
                    Interval(TIME_ZERO, T_NOW - timedelta(days=3), value=0),
                    Interval(
                        T_NOW - timedelta(days=3),
                        T_NOW + timedelta(days=3),
                        value=10,
                    ),
                    Interval(
                        T_NOW + timedelta(days=3),
                        T_NOW + timedelta(days=5),
                        value=0,
                    ),
                    Interval(T_NOW + timedelta(days=5), datetime.max, value=0),
                ]
            ),
            id="dividing two IntervalHandlers. They both have the exact same domain. "
            "To prevent `ZeroDivisionError`, a 'baseline' value of 1 "
            "is added to the denominating `IntervalHandler`.",
        ),
        pytest.param(
            operator.truediv,
            IntervalHandler(
                intervals=[
                    Interval(
                        T_NOW - timedelta(days=3),
                        T_NOW + timedelta(days=3),
                        value=10,
                    )
                ]
            ),
            IntervalHandler(
                intervals=[
                    Interval(TIME_ZERO, datetime.max, value=1),
                    Interval(
                        T_NOW + timedelta(days=5),
                        T_NOW + timedelta(days=10),
                        value=4,
                    ),
                ]
            ),
            None,  # No error expected,
            IntervalHandler(
                intervals=[
                    Interval(TIME_ZERO, T_NOW - timedelta(days=3), value=0),
                    Interval(
                        T_NOW - timedelta(days=3),
                        T_NOW + timedelta(days=3),
                        value=10,
                    ),
                    Interval(
                        T_NOW + timedelta(days=3),
                        T_NOW + timedelta(days=5),
                        value=0,
                    ),
                    Interval(
                        T_NOW + timedelta(days=5),
                        T_NOW + timedelta(days=10),
                        value=0,
                    ),
                    Interval(T_NOW + timedelta(days=10), datetime.max, value=0),
                ]
            ),
            id="dividing two IntervalHandlers. They both have the exact same domain. "
            "To prevent `ZeroDivisionError`, a 'baseline' value of 1 "
            "is added to the denominating `IntervalHandler`.",
        ),
    ],
)
@pytest.mark.parametrize(
    "is_in_place",
    [
        pytest.param(False, id="Regular"),
        pytest.param(True, id="In-place"),
    ],
)
def test_operate(
    operand: Callable[[float, float], float],
    a: IntervalHandler,
    b: IntervalHandler,
    expected_error_type: Union[type[Exception], None],
    is_in_place: bool,
    expected: Union[IntervalHandler, None],
) -> None:
    if is_in_place:
        in_place_operand = IN_PLACE_OPERAND_MAPPING[operand]
        if expected_error_type is not None:
            with pytest.raises(expected_error_type):
                in_place_operand(a, b)
        else:
            in_place_operand(a, b)
            assert a == expected
    else:
        if expected_error_type is not None:
            with pytest.raises(expected_error_type):
                operand(a, b)
        else:
            result = operand(a, b)
            assert result == expected
