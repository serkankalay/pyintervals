from __future__ import annotations

from datetime import datetime

import pytest

from pyintervals.interval import Interval


def test_invalid_interval():
    with pytest.raises(RuntimeError):
        Interval(
            start=datetime(2023, 1, 1, 9, 5),
            end=datetime(2022, 1, 1, 9, 5),
        )


def test_valid_interval():
    assert Interval(
        start=datetime(2023, 1, 1, 9, 5),
        end=datetime(2024, 1, 1, 9, 5),
    )


def test_degenerate_interval():
    assert Interval(
        start=datetime(2023, 1, 1, 9, 5),
        end=datetime(2023, 1, 1, 9, 5),
    ).is_degenerate()
    assert not Interval(
        start=datetime(2023, 1, 1, 9, 5),
        end=datetime(2023, 1, 1, 9, 6),
    ).is_degenerate()
