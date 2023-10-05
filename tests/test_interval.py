from __future__ import annotations

from datetime import timedelta

import pytest

from pyintervals.interval import Interval
from tests.helpers import FUTURE_DATE, NOT_SO_IMPORTANT_LATER_DATE, THE_DATE


@pytest.fixture
def regular_interval() -> Interval:
    return Interval(
        start=THE_DATE,
        end=FUTURE_DATE,
    )


@pytest.fixture
def degenerate_interval() -> Interval:
    return Interval(
        start=THE_DATE,
        end=THE_DATE,
    )


def test_invalid_interval():
    with pytest.raises(RuntimeError):
        Interval(
            start=NOT_SO_IMPORTANT_LATER_DATE,
            end=THE_DATE,
        )


def test_valid_interval(regular_interval):
    assert regular_interval


def test_degenerate_interval(degenerate_interval, regular_interval):
    assert degenerate_interval.is_degenerate()
    assert not regular_interval.is_degenerate()


@pytest.fixture
def interval_of_1_day() -> Interval:
    start = THE_DATE
    return Interval(
        start=start,
        end=start + timedelta(days=1),
    )


@pytest.fixture
def interval_of_1_hour() -> Interval:
    start = THE_DATE
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
