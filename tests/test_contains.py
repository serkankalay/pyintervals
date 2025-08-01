from __future__ import annotations

from datetime import timedelta

import pytest

from pyintervals import Interval, contains
from tests.helpers import NOT_SO_IMPORTANT_LATER_DATE, THE_DATE


@pytest.mark.parametrize(
    "reference,other,answer",
    [
        # No overlaps
        (
            Interval(start=THE_DATE, end=THE_DATE + timedelta(hours=8)),
            Interval(
                start=THE_DATE + timedelta(days=1),
                end=THE_DATE + timedelta(days=1, hours=12),
            ),
            False,
        ),
        # Start-to-end
        (
            Interval(start=THE_DATE, end=THE_DATE + timedelta(hours=8)),
            Interval(
                start=THE_DATE + timedelta(hours=8),
                end=THE_DATE + timedelta(hours=10),
            ),
            False,
        ),
        # Overlapping degenerate at start
        (
            Interval(start=THE_DATE, end=THE_DATE + timedelta(hours=8)),
            Interval(start=THE_DATE, end=THE_DATE),
            True,
        ),
        # Overlapping degenerate inside
        (
            Interval(start=THE_DATE, end=THE_DATE + timedelta(hours=8)),
            Interval(
                start=THE_DATE + timedelta(hours=4),
                end=THE_DATE + timedelta(hours=4),
            ),
            True,
        ),
        # Non-overlapping degenerate far later
        (
            Interval(start=THE_DATE, end=THE_DATE + timedelta(hours=8)),
            Interval(
                start=THE_DATE + timedelta(hours=12),
                end=THE_DATE + timedelta(hours=12),
            ),
            False,
        ),
        # Non-overlapping degenerate far earlier
        (
            Interval(start=THE_DATE, end=THE_DATE + timedelta(hours=8)),
            Interval(
                start=THE_DATE - timedelta(hours=12),
                end=THE_DATE - timedelta(hours=12),
            ),
            False,
        ),
        # Non-overlapping degenerate at the end
        (
            Interval(start=THE_DATE, end=THE_DATE + timedelta(hours=8)),
            Interval(
                start=THE_DATE + timedelta(hours=8),
                end=THE_DATE + timedelta(hours=8),
            ),
            False,
        ),
        # Non-overlapping 2 degenerates
        (
            Interval(start=THE_DATE, end=THE_DATE),
            Interval(
                start=NOT_SO_IMPORTANT_LATER_DATE,
                end=NOT_SO_IMPORTANT_LATER_DATE,
            ),
            False,
        ),
        # Overlapping 2 degenerates
        (
            Interval(start=THE_DATE, end=THE_DATE),
            Interval(start=THE_DATE, end=THE_DATE),
            True,
        ),
        # Overlapping for 4 hours with other's start
        (
            Interval(start=THE_DATE, end=THE_DATE + timedelta(hours=8)),
            Interval(
                start=THE_DATE + timedelta(hours=4),
                end=THE_DATE + timedelta(hours=12),
            ),
            False,
        ),
        # Overlapping for 4 hours with other's end
        (
            Interval(start=THE_DATE, end=THE_DATE + timedelta(hours=8)),
            Interval(
                start=THE_DATE - timedelta(hours=4),
                end=THE_DATE + timedelta(hours=4),
            ),
            False,
        ),
        # Fully contained
        (
            Interval(start=THE_DATE, end=THE_DATE + timedelta(hours=8)),
            Interval(
                start=THE_DATE + timedelta(hours=1),
                end=THE_DATE + timedelta(hours=2),
            ),
            True,
        ),
        # Exactly the same
        (
            Interval(start=THE_DATE, end=THE_DATE + timedelta(hours=8)),
            Interval(start=THE_DATE, end=THE_DATE + timedelta(hours=8)),
            True,
        ),
        # Reference is contained in the other, so it should return false.
        (
            Interval(start=THE_DATE, end=THE_DATE + timedelta(days=1)),
            Interval(
                start=THE_DATE - timedelta(days=10),
                end=THE_DATE + timedelta(days=10),
            ),
            False,
        ),
        # Overlapping, the reference is degenerate, the other one non-degenerate  # noqa: E501
        (
            Interval(start=THE_DATE, end=THE_DATE),
            Interval(
                start=THE_DATE,
                end=THE_DATE + timedelta(hours=12),
            ),
            False,
        ),
        # Overlapping, the reference is non-degenerate, the other one degenerate  # noqa: E501
        (
            Interval(start=THE_DATE, end=THE_DATE + timedelta(hours=12)),
            Interval(
                start=THE_DATE,
                end=THE_DATE,
            ),
            True,
        ),
        # Non-overlapping, the reference is degenerate, the other one non-degenerate  # noqa: E501
        (
            Interval(start=THE_DATE, end=THE_DATE),
            Interval(
                start=NOT_SO_IMPORTANT_LATER_DATE,
                end=NOT_SO_IMPORTANT_LATER_DATE + timedelta(hours=12),
            ),
            False,
        ),
        # Non-overlapping, the reference is degenerate, the other one non-degenerate  # noqa: E501
        (
            Interval(start=THE_DATE, end=THE_DATE + timedelta(hours=12)),
            Interval(
                start=NOT_SO_IMPORTANT_LATER_DATE,
                end=NOT_SO_IMPORTANT_LATER_DATE,
            ),
            False,
        ),
    ],
)
def test_contains(reference, other, answer):
    assert contains(reference, other) == answer
    assert reference.contains(other) == answer
