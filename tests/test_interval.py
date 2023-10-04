from __future__ import annotations

from datetime import datetime

import pytest

from pyintervals.interval import Interval


@pytest.fixture
def regular_interval() -> Interval:
    return Interval(
        start=datetime(2023, 1, 1, 9, 5),
        end=datetime(2024, 1, 1, 9, 5),
    )


@pytest.fixture
def degenerate_interval() -> Interval:
    return Interval(
        start=datetime(2023, 1, 1, 9, 5),
        end=datetime(2023, 1, 1, 9, 5),
    )


def test_invalid_interval():
    with pytest.raises(RuntimeError):
        Interval(
            start=datetime(2023, 1, 1, 9, 5),
            end=datetime(2022, 1, 1, 9, 5),
        )


def test_valid_interval(regular_interval):
    assert regular_interval


def test_degenerate_interval(degenerate_interval, regular_interval):
    assert degenerate_interval.is_degenerate()
    assert not regular_interval.is_degenerate()
