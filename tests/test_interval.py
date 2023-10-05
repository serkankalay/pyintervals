from __future__ import annotations

from datetime import datetime, timedelta

import pytest

from pyintervals.interval import Interval, overlaps

_THE_DATE = datetime(2017, 5, 20, 12, 15)
_NOT_SO_IMPORTANT_LATER_DATE = datetime(2017, 5, 21, 10, 45)
_FUTURE_DATE = datetime(2023, 10, 29, 9, 5)


@pytest.fixture
def regular_interval() -> Interval:
    return Interval(
        start=_THE_DATE,
        end=_FUTURE_DATE,
    )


@pytest.fixture
def degenerate_interval() -> Interval:
    return Interval(
        start=_THE_DATE,
        end=_THE_DATE,
    )


def test_invalid_interval():
    with pytest.raises(RuntimeError):
        Interval(
            start=_NOT_SO_IMPORTANT_LATER_DATE,
            end=_THE_DATE,
        )


def test_valid_interval(regular_interval):
    assert regular_interval


def test_degenerate_interval(degenerate_interval, regular_interval):
    assert degenerate_interval.is_degenerate()
    assert not regular_interval.is_degenerate()


@pytest.fixture
def interval_of_1_day() -> Interval:
    start = _THE_DATE
    return Interval(
        start=start,
        end=start + timedelta(days=1),
    )


@pytest.fixture
def interval_of_1_hour() -> Interval:
    start = _THE_DATE
    return Interval(
        start=start,
        end=start + timedelta(hours=1),
    )


@pytest.mark.parametrize(
    "interval,expected_duration",
    [
        ("interval_of_1_hour", timedelta(hours=1)),
        ("interval_of_1_day", timedelta(days=1)),
        ("degenerate_interval", timedelta()),
    ],
)
def test_interval_duration(request, interval, expected_duration):
    assert request.getfixturevalue(interval).duration() == expected_duration


@pytest.mark.parametrize(
    "first,second,answer",
    [
        # No overlaps
        (
            Interval(start=_THE_DATE, end=_THE_DATE + timedelta(hours=8)),
            Interval(
                start=_THE_DATE + timedelta(days=1),
                end=_THE_DATE + timedelta(days=1, hours=12),
            ),
            False,
        ),
        # Start-to-end
        (
            Interval(start=_THE_DATE, end=_THE_DATE + timedelta(hours=8)),
            Interval(
                start=_THE_DATE + timedelta(hours=8),
                end=_THE_DATE + timedelta(hours=10),
            ),
            False,
        ),
        # Overlapping degenerate at start
        (
            Interval(start=_THE_DATE, end=_THE_DATE + timedelta(hours=8)),
            Interval(start=_THE_DATE, end=_THE_DATE),
            True,
        ),
        # Overlapping degenerate inside
        (
            Interval(start=_THE_DATE, end=_THE_DATE + timedelta(hours=8)),
            Interval(
                start=_THE_DATE + timedelta(hours=4),
                end=_THE_DATE + timedelta(hours=4),
            ),
            True,
        ),
        # Non-overlapping degenerate far later
        (
            Interval(start=_THE_DATE, end=_THE_DATE + timedelta(hours=8)),
            Interval(
                start=_THE_DATE + timedelta(hours=12),
                end=_THE_DATE + timedelta(hours=12),
            ),
            False,
        ),
        # Non-overlapping degenerate far earlier
        (
            Interval(start=_THE_DATE, end=_THE_DATE + timedelta(hours=8)),
            Interval(
                start=_THE_DATE - timedelta(hours=12),
                end=_THE_DATE - timedelta(hours=12),
            ),
            False,
        ),
        # Non-overlapping degenerate at the end
        (
            Interval(start=_THE_DATE, end=_THE_DATE + timedelta(hours=8)),
            Interval(
                start=_THE_DATE + timedelta(hours=8),
                end=_THE_DATE + timedelta(hours=8),
            ),
            False,
        ),
        # Non-overlapping 2 degenerates
        (
            Interval(start=_THE_DATE, end=_THE_DATE),
            Interval(
                start=_NOT_SO_IMPORTANT_LATER_DATE,
                end=_NOT_SO_IMPORTANT_LATER_DATE,
            ),
            False,
        ),
        # Overlapping 2 degenerates
        (
            Interval(start=_THE_DATE, end=_THE_DATE),
            Interval(start=_THE_DATE, end=_THE_DATE),
            True,
        ),
        # Overlapping for 4 hours with other's start
        (
            Interval(start=_THE_DATE, end=_THE_DATE + timedelta(hours=8)),
            Interval(
                start=_THE_DATE + timedelta(hours=4),
                end=_THE_DATE + timedelta(hours=12),
            ),
            True,
        ),
        # Overlapping for 4 hours with other's end
        (
            Interval(start=_THE_DATE, end=_THE_DATE + timedelta(hours=8)),
            Interval(
                start=_THE_DATE - timedelta(hours=4),
                end=_THE_DATE + timedelta(hours=4),
            ),
            True,
        ),
        # Fully contained
        (
            Interval(start=_THE_DATE, end=_THE_DATE + timedelta(hours=8)),
            Interval(
                start=_THE_DATE + timedelta(hours=1),
                end=_THE_DATE + timedelta(hours=2),
            ),
            True,
        ),
        # Exactly the same
        (
            Interval(start=_THE_DATE, end=_THE_DATE + timedelta(hours=8)),
            Interval(start=_THE_DATE, end=_THE_DATE + timedelta(hours=8)),
            True,
        ),
    ],
)
def test_overlaps(first, second, answer):
    assert overlaps(first, second) == answer
    assert overlaps(second, first) == answer
