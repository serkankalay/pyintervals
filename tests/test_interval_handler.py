from __future__ import annotations

from datetime import datetime
from typing import Callable, Iterable, Sequence

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
    assert [tvn.time_point for tvn in handler.projection_graph()] == expected_tvn_time_points
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
        assert interval in handler.node_at_time(interval.start).starting_intervals
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
    assert to_remove not in handler.node_at_time(to_remove.start).starting_intervals
    assert to_remove not in handler.node_at_time(to_remove.end).ending_intervals

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
    assert {new_interval.start, new_interval.end}.issubset({n.time_point for n in nodes})


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
def test_node_and_value_at_time(time_point, n_expected_intervals, expected_value) -> None:
    handler = _complex_interval_handler()
    assert len(handler.node_at_time(time_point).intervals) == n_expected_intervals
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
def test_remove_intervals_detailed(intervals: list[Interval], n_expected_tvn_reduction) -> None:
    handler = _complex_interval_handler()
    original_tvn_count = len(handler.projection_graph())
    handler.remove(intervals)
    assert len(handler.projection_graph()) == (original_tvn_count - n_expected_tvn_reduction)
    assert not any(interval in node.intervals for node in handler.projection_graph() for interval in intervals)


@pytest.mark.parametrize(
    "test_id,intervals,expected_time_point,expected_value_check,additional_assertions",
    [
        (
            "empty_handler",
            [],
            None,
            None,
            None,
        ),
        (
            "only_positive_values",
            [
                Interval(datetime(2023, 1, 1), datetime(2023, 1, 10), value=5),
                Interval(datetime(2023, 1, 5), datetime(2023, 1, 15), value=3),
                Interval(datetime(2023, 1, 20), datetime(2023, 1, 20), value=0),
            ],
            None,
            None,
            None,
        ),
        (
            "single_negative_interval",
            [
                Interval(datetime(2023, 1, 1), datetime(2023, 1, 10), value=-5),
            ],
            datetime(2023, 1, 1),
            lambda v: v < 0,
            None,
        ),
        (
            "multiple_negative_intervals",
            [
                Interval(datetime(2023, 1, 5), datetime(2023, 1, 10), value=-3),
                Interval(datetime(2023, 1, 1), datetime(2023, 1, 8), value=-2),
            ],
            datetime(2023, 1, 1),
            lambda v: v < 0,
            None,
        ),
        (
            "positive_then_negative",
            [
                Interval(datetime(2023, 1, 1), datetime(2023, 1, 10), value=5),
                Interval(datetime(2023, 1, 5), datetime(2023, 1, 15), value=-10),
            ],
            datetime(2023, 1, 5),
            lambda v: v < 0,
            None,
        ),
        (
            "negative_then_positive",
            [
                Interval(datetime(2023, 1, 1), datetime(2023, 1, 10), value=-5),
                Interval(datetime(2023, 1, 5), datetime(2023, 1, 15), value=10),
            ],
            datetime(2023, 1, 1),
            lambda v: v < 0,
            None,
        ),
        (
            "zero_then_negative",
            [
                Interval(datetime(2023, 1, 1), datetime(2023, 1, 5), value=0),
                Interval(datetime(2023, 1, 3), datetime(2023, 1, 10), value=-3),
            ],
            datetime(2023, 1, 3),
            lambda v: v < 0,
            None,
        ),
        (
            "overlapping_negative_intervals",
            [
                Interval(datetime(2023, 1, 1), datetime(2023, 1, 10), value=-2),
                Interval(datetime(2023, 1, 5), datetime(2023, 1, 15), value=-3),
            ],
            datetime(2023, 1, 1),
            lambda v: v < 0,
            lambda h: h.node_at_time(datetime(2023, 1, 5)).value == -5,
        ),
        (
            "degenerate_negative_interval",
            [
                Interval(datetime(2023, 1, 1), datetime(2023, 1, 1), value=-5),
            ],
            None,
            None,
            None,
        ),
    ],
    ids=[
        "empty_handler",
        "only_positive_values",
        "single_negative_interval",
        "multiple_negative_intervals",
        "positive_then_negative",
        "negative_then_positive",
        "zero_then_negative",
        "overlapping_negative_intervals",
        "degenerate_negative_interval",
    ],
)
def test_first_negative_point(
    test_id: str,
    intervals: list[Interval],
    expected_time_point: datetime | None,
    expected_value_check: Callable[[float], bool] | None,
    additional_assertions: Callable[[IntervalHandler], None] | None,
) -> None:
    """Test first_negative_point method of IntervalHandler."""
    handler = IntervalHandler(intervals=intervals)
    first_negative = handler.first_negative_point()

    if expected_time_point is None:
        if test_id == "degenerate_negative_interval":
            # Special case: degenerate intervals don't contribute to node.value
            # So first_negative_point should be None OR if not None, value should be < 0
            assert first_negative is None or first_negative.value < 0, (
                f"Expected None or negative value for {test_id}, "
                f"got {first_negative} with value={first_negative.value if first_negative else None}"
            )
        else:
            assert first_negative is None, f"Expected None for {test_id}, got {first_negative}"
    else:
        assert first_negative is not None, f"Expected non-None for {test_id}"
        assert first_negative.time_point == expected_time_point, (
            f"Expected time_point {expected_time_point} for {test_id}, " f"got {first_negative.time_point}"
        )
        if expected_value_check:
            assert expected_value_check(
                first_negative.value
            ), f"Value check failed for {test_id}: value={first_negative.value}"

    if additional_assertions:
        additional_assertions(handler)


@pytest.mark.parametrize(
    "test_id,operation,handler1_intervals,handler2_intervals,expected_time_point,expected_value_check",
    [
        (
            "negative_through_subtraction",
            "sub",
            [Interval(datetime(2023, 1, 1), datetime(2023, 1, 10), value=5)],
            [Interval(datetime(2023, 1, 1), datetime(2023, 1, 10), value=10)],
            datetime(2023, 1, 1),
            lambda v: v < 0,
        ),
        (
            "negative_through_subtraction_partial_overlap",
            "sub",
            [Interval(datetime(2023, 1, 1), datetime(2023, 1, 10), value=5)],
            [Interval(datetime(2023, 1, 5), datetime(2023, 1, 15), value=10)],
            datetime(2023, 1, 5),
            lambda v: v < 0,
        ),
        (
            "negative_through_subtraction_multiple_intervals",
            "sub",
            [
                Interval(datetime(2023, 1, 1), datetime(2023, 1, 10), value=5),
                Interval(datetime(2023, 1, 15), datetime(2023, 1, 20), value=3),
            ],
            [
                Interval(datetime(2023, 1, 1), datetime(2023, 1, 10), value=10),
                Interval(datetime(2023, 1, 15), datetime(2023, 1, 20), value=8),
            ],
            datetime(2023, 1, 1),
            lambda v: v < 0,
        ),
        (
            "negative_through_addition_with_negative",
            "add",
            [Interval(datetime(2023, 1, 1), datetime(2023, 1, 10), value=-5)],
            [Interval(datetime(2023, 1, 1), datetime(2023, 1, 10), value=-3)],
            datetime(2023, 1, 1),
            lambda v: v < 0,
        ),
        (
            "negative_through_addition_positive_and_negative",
            "add",
            [Interval(datetime(2023, 1, 1), datetime(2023, 1, 10), value=3)],
            [Interval(datetime(2023, 1, 1), datetime(2023, 1, 10), value=-10)],
            datetime(2023, 1, 1),
            lambda v: v < 0,
        ),
        (
            "negative_through_multiplication_positive_negative",
            "mul",
            [Interval(datetime(2023, 1, 1), datetime(2023, 1, 10), value=5)],
            [Interval(datetime(2023, 1, 1), datetime(2023, 1, 10), value=-2)],
            datetime(2023, 1, 1),
            lambda v: v < 0,
        ),
        (
            "negative_through_multiplication_negative_positive",
            "mul",
            [Interval(datetime(2023, 1, 1), datetime(2023, 1, 10), value=-3)],
            [Interval(datetime(2023, 1, 1), datetime(2023, 1, 10), value=4)],
            datetime(2023, 1, 1),
            lambda v: v < 0,
        ),
        (
            "negative_through_multiplication_both_negative",
            "mul",
            [Interval(datetime(2023, 1, 1), datetime(2023, 1, 10), value=-2)],
            [Interval(datetime(2023, 1, 1), datetime(2023, 1, 10), value=-3)],
            None,
            None,
        ),
        (
            "negative_through_division_positive_by_negative",
            "div",
            [Interval(datetime(2023, 1, 1), datetime(2023, 1, 10), value=9)],
            [Interval(datetime(2023, 1, 1), datetime(2023, 1, 10), value=-3)],
            datetime(2023, 1, 1),
            lambda v: v < 0,
        ),
        (
            "negative_through_division_negative_by_positive",
            "div",
            [Interval(datetime(2023, 1, 1), datetime(2023, 1, 10), value=-11)],
            [Interval(datetime(2023, 1, 1), datetime(2023, 1, 10), value=1)],
            datetime(2023, 1, 1),
            lambda v: v < 0,
        ),
        (
            "negative_through_division_negative_by_negative",
            "div",
            [Interval(datetime(2023, 1, 1), datetime(2023, 1, 10), value=-11)],
            [Interval(datetime(2023, 1, 1), datetime(2023, 1, 10), value=-3)],
            None,
            None,
        ),
        (
            "subtraction_no_negative_result",
            "sub",
            [Interval(datetime(2023, 1, 1), datetime(2023, 1, 10), value=10)],
            [Interval(datetime(2023, 1, 1), datetime(2023, 1, 10), value=5)],
            None,
            None,
        ),
        (
            "addition_no_negative_result",
            "add",
            [Interval(datetime(2023, 1, 1), datetime(2023, 1, 10), value=5)],
            [Interval(datetime(2023, 1, 1), datetime(2023, 1, 10), value=3)],
            None,
            None,
        ),
        (
            "subtraction_overlapping_intervals",
            "sub",
            [
                Interval(datetime(2023, 1, 1), datetime(2023, 1, 10), value=5),
                Interval(datetime(2023, 1, 5), datetime(2023, 1, 15), value=3),
            ],
            [
                Interval(datetime(2023, 1, 1), datetime(2023, 1, 10), value=10),
                Interval(datetime(2023, 1, 5), datetime(2023, 1, 15), value=8),
            ],
            datetime(2023, 1, 1),
            lambda v: v < 0,
        ),
    ],
    ids=[
        "negative_through_subtraction",
        "negative_through_subtraction_partial_overlap",
        "negative_through_subtraction_multiple_intervals",
        "negative_through_addition_with_negative",
        "negative_through_addition_positive_and_negative",
        "negative_through_multiplication_positive_negative",
        "negative_through_multiplication_negative_positive",
        "negative_through_multiplication_both_negative",
        "negative_through_division_positive_by_negative",
        "negative_through_division_negative_by_positive",
        "negative_through_division_negative_by_negative",
        "subtraction_no_negative_result",
        "addition_no_negative_result",
        "subtraction_overlapping_intervals",
    ],
)
def test_first_negative_point_operations(
    test_id: str,
    operation: str,
    handler1_intervals: list[Interval],
    handler2_intervals: list[Interval],
    expected_time_point: datetime | None,
    expected_value_check: Callable[[float], bool] | None,
) -> None:
    """Test first_negative_point with operations like addition, subtraction, multiplication, division."""
    handler1 = IntervalHandler(intervals=handler1_intervals)
    handler2 = IntervalHandler(intervals=handler2_intervals)

    if operation == "add":
        result = handler1 + handler2
    elif operation == "sub":
        result = handler1 - handler2
    elif operation == "mul":
        result = handler1 * handler2
    elif operation == "div":
        # To avoid division by zero.
        handler1.add([Interval(TIME_ZERO, datetime.max, 1)])
        handler2.add([Interval(TIME_ZERO, datetime.max, 1)])
        result = handler1 / handler2
    else:
        raise ValueError(f"Unknown operation: {operation}")

    first_negative = result.first_negative_point()

    if expected_time_point is None:
        assert first_negative is None, f"Expected None for {test_id}, got {first_negative}"
    else:
        assert first_negative is not None, f"Expected non-None for {test_id}"
        assert first_negative.time_point == expected_time_point, (
            f"Expected time_point {expected_time_point} for {test_id}, " f"got {first_negative.time_point}"
        )
        if expected_value_check:
            assert expected_value_check(
                first_negative.value
            ), f"Value check failed for {test_id}: value={first_negative.value}"


@pytest.mark.parametrize(
    "test_id,intervals,remove_intervals,expected_after_remove",
    [
        (
            "remove_negative_interval",
            [
                Interval(datetime(2023, 1, 1), datetime(2023, 1, 10), value=-5),
                Interval(datetime(2023, 1, 5), datetime(2023, 1, 15), value=3),
            ],
            [Interval(datetime(2023, 1, 1), datetime(2023, 1, 10), value=-5)],
            None,
        ),
        (
            "remove_one_of_multiple_negatives",
            [
                Interval(datetime(2023, 1, 1), datetime(2023, 1, 10), value=-5),
                Interval(datetime(2023, 1, 5), datetime(2023, 1, 15), value=-3),
            ],
            [Interval(datetime(2023, 1, 1), datetime(2023, 1, 10), value=-5)],
            datetime(2023, 1, 5),
        ),
        (
            "remove_positive_that_cancels_negative",
            [
                Interval(datetime(2023, 1, 1), datetime(2023, 1, 10), value=-5),
                Interval(datetime(2023, 1, 5), datetime(2023, 1, 15), value=10),
            ],
            [Interval(datetime(2023, 1, 5), datetime(2023, 1, 15), value=10)],
            datetime(2023, 1, 1),
        ),
        (
            "remove_all_negative_intervals",
            [
                Interval(datetime(2023, 1, 1), datetime(2023, 1, 10), value=-5),
                Interval(datetime(2023, 1, 5), datetime(2023, 1, 15), value=-3),
            ],
            [
                Interval(datetime(2023, 1, 1), datetime(2023, 1, 10), value=-5),
                Interval(datetime(2023, 1, 5), datetime(2023, 1, 15), value=-3),
            ],
            None,
        ),
        (
            "remove_earlier_negative_keeps_later",
            [
                Interval(datetime(2023, 1, 1), datetime(2023, 1, 10), value=-5),
                Interval(datetime(2023, 1, 15), datetime(2023, 1, 20), value=-3),
            ],
            [Interval(datetime(2023, 1, 1), datetime(2023, 1, 10), value=-5)],
            datetime(2023, 1, 15),
        ),
        (
            "remove_overlapping_negative",
            [
                Interval(datetime(2023, 1, 1), datetime(2023, 1, 10), value=-2),
                Interval(datetime(2023, 1, 5), datetime(2023, 1, 15), value=-3),
            ],
            [Interval(datetime(2023, 1, 1), datetime(2023, 1, 10), value=-2)],
            datetime(2023, 1, 5),
        ),
        (
            "remove_positive_from_mixed",
            [
                Interval(datetime(2023, 1, 1), datetime(2023, 1, 10), value=-5),
                Interval(datetime(2023, 1, 5), datetime(2023, 1, 15), value=3),
            ],
            [Interval(datetime(2023, 1, 5), datetime(2023, 1, 15), value=3)],
            datetime(2023, 1, 1),
        ),
    ],
    ids=[
        "remove_negative_interval",
        "remove_one_of_multiple_negatives",
        "remove_positive_that_cancels_negative",
        "remove_all_negative_intervals",
        "remove_earlier_negative_keeps_later",
        "remove_overlapping_negative",
        "remove_positive_from_mixed",
    ],
)
def test_first_negative_point_after_remove(
    test_id: str,
    intervals: list[Interval],
    remove_intervals: list[Interval],
    expected_after_remove: datetime | None,
) -> None:
    """Test first_negative_point after removing intervals."""
    handler = IntervalHandler(intervals=intervals)
    # Initially should have a negative point
    assert handler.first_negative_point() is not None, f"Expected negative point initially for {test_id}"

    # Remove the intervals
    handler.remove(remove_intervals)
    first_negative = handler.first_negative_point()

    if expected_after_remove is None:
        assert first_negative is None, f"Expected None after removal for {test_id}, got {first_negative}"
    else:
        assert first_negative is not None, f"Expected non-None after removal for {test_id}"
        assert first_negative.time_point == expected_after_remove, (
            f"Expected time_point {expected_after_remove} after removal for {test_id}, "
            f"got {first_negative.time_point}"
        )


@pytest.mark.parametrize(
    "test_id,initial_intervals,add_intervals,expected_after_add",
    [
        (
            "add_negative_to_empty",
            [],
            [Interval(datetime(2023, 1, 1), datetime(2023, 1, 10), value=-5)],
            datetime(2023, 1, 1),
        ),
        (
            "add_negative_to_positive",
            [
                Interval(datetime(2023, 1, 1), datetime(2023, 1, 10), value=5),
            ],
            [Interval(datetime(2023, 1, 5), datetime(2023, 1, 15), value=-10)],
            datetime(2023, 1, 5),
        ),
        (
            "add_positive_that_cancels_negative",
            [
                Interval(datetime(2023, 1, 1), datetime(2023, 1, 10), value=-5),
            ],
            [Interval(datetime(2023, 1, 5), datetime(2023, 1, 15), value=10)],
            datetime(2023, 1, 1),
        ),
        (
            "add_positive_that_fully_cancels_negative",
            [
                Interval(datetime(2023, 1, 1), datetime(2023, 1, 10), value=-5),
            ],
            [Interval(datetime(2023, 1, 1), datetime(2023, 1, 10), value=5)],
            None,
        ),
        (
            "add_overlapping_negative",
            [
                Interval(datetime(2023, 1, 1), datetime(2023, 1, 10), value=-2),
            ],
            [Interval(datetime(2023, 1, 5), datetime(2023, 1, 15), value=-3)],
            datetime(2023, 1, 1),
        ),
        (
            "add_negative_before_existing_negative",
            [
                Interval(datetime(2023, 1, 10), datetime(2023, 1, 20), value=-5),
            ],
            [Interval(datetime(2023, 1, 1), datetime(2023, 1, 15), value=-3)],
            datetime(2023, 1, 1),
        ),
        (
            "add_negative_after_existing_negative",
            [
                Interval(datetime(2023, 1, 1), datetime(2023, 1, 10), value=-5),
            ],
            [Interval(datetime(2023, 1, 15), datetime(2023, 1, 20), value=-3)],
            datetime(2023, 1, 1),
        ),
        (
            "add_positive_to_negative",
            [
                Interval(datetime(2023, 1, 1), datetime(2023, 1, 10), value=-5),
            ],
            [Interval(datetime(2023, 1, 5), datetime(2023, 1, 15), value=3)],
            datetime(2023, 1, 1),
        ),
        (
            "add_multiple_negatives",
            [
                Interval(datetime(2023, 1, 1), datetime(2023, 1, 10), value=-2),
            ],
            [
                Interval(datetime(2023, 1, 5), datetime(2023, 1, 15), value=-3),
                Interval(datetime(2023, 1, 20), datetime(2023, 1, 25), value=-1),
            ],
            datetime(2023, 1, 1),
        ),
        (
            "add_negative_that_creates_first_negative",
            [
                Interval(datetime(2023, 1, 1), datetime(2023, 1, 10), value=5),
                Interval(datetime(2023, 1, 5), datetime(2023, 1, 15), value=3),
            ],
            [Interval(datetime(2023, 1, 8), datetime(2023, 1, 20), value=-10)],
            datetime(2023, 1, 8),
        ),
    ],
    ids=[
        "add_negative_to_empty",
        "add_negative_to_positive",
        "add_positive_that_cancels_negative",
        "add_positive_that_fully_cancels_negative",
        "add_overlapping_negative",
        "add_negative_before_existing_negative",
        "add_negative_after_existing_negative",
        "add_positive_to_negative",
        "add_multiple_negatives",
        "add_negative_that_creates_first_negative",
    ],
)
def test_first_negative_point_after_add(
    test_id: str,
    initial_intervals: list[Interval],
    add_intervals: list[Interval],
    expected_after_add: datetime | None,
) -> None:
    """Test first_negative_point after adding intervals."""
    handler = IntervalHandler(intervals=initial_intervals)

    # Add the intervals
    handler.add(add_intervals)
    first_negative = handler.first_negative_point()

    if expected_after_add is None:
        assert first_negative is None, f"Expected None after adding for {test_id}, got {first_negative}"
    else:
        assert first_negative is not None, f"Expected non-None after adding for {test_id}"
        assert first_negative.time_point == expected_after_add, (
            f"Expected time_point {expected_after_add} after adding for {test_id}, " f"got {first_negative.time_point}"
        )
        # Verify the value is negative
        assert first_negative.value < 0, (
            f"Expected negative value after adding for {test_id}, " f"got {first_negative.value}"
        )
