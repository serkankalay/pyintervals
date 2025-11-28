from __future__ import annotations

from datetime import datetime

import pytest

from pyintervals import Interval
from pyintervals.interval import intersection


@pytest.mark.parametrize(
    "s1, e1, s2, e2, s_expected, e_expected",
    [
        # A single test using datetimes rather than dates to show
        # that this function works using
        # datetimes and not dates.
        (
            "2020-01-01T00:00:00+00:00",
            "2020-03-01T00:00:00+00:00",
            "2020-02-01T00:00:00+00:00",
            "2020-04-01T00:00:00+00:00",
            "2020-02-01T00:00:00+00:00",
            "2020-03-01T00:00:00+00:00",
        ),
        # In the rest of the tests, we'll simply use dates
        # because they're a bit easier to read
        # and you can cover just as many test cases with them.
        # interval is modeled as closed-open, i.e. [start, end),
        # hence the expected outcomes
        (
            "2020-01-01",
            "2020-03-01",
            "2020-02-01",
            "2020-04-01",
            "2020-02-01",
            "2020-03-01",
        ),
        (
            "2020-02-01",
            "2020-04-01",
            "2020-01-01",
            "2020-03-01",
            "2020-02-01",
            "2020-03-01",
        ),
        (
            "2020-03-01",
            "2020-05-01",
            "2020-01-01",
            "2020-07-01",
            "2020-03-01",
            "2020-05-01",
        ),
        (
            "2020-01-01",
            "2020-07-01",
            "2020-03-01",
            "2020-05-01",
            "2020-03-01",
            "2020-05-01",
        ),
        ("2020-01-01", "2020-03-01", "2020-05-01", "2020-07-01", None, None),
        ("2020-05-01", "2020-07-01", "2020-01-01", "2020-03-01", None, None),
        ("2020-01-01", "2020-03-01", "2020-03-01", "2020-05-01", None, None),
        ("2020-03-01", "2020-05-01", "2020-01-01", "2020-03-01", None, None),
        (
            "2020-01-01",
            "2020-01-01",
            "2020-01-01",
            "2020-01-01",
            "2020-01-01",
            "2020-01-01",
        ),
        (
            "2020-01-01",
            "2020-07-01",
            "2020-01-01",
            "2020-01-01",
            "2020-01-01",
            "2020-01-01",
        ),
        ("2020-01-01", "2020-07-01", "2020-07-01", "2020-07-01", None, None),
        (
            "2020-01-01",
            "2020-01-01",
            "2020-01-01",
            "2020-07-01",
            "2020-01-01",
            "2020-01-01",
        ),
        ("2020-07-01", "2020-07-01", "2020-01-01", "2020-07-01", None, None),
        ("2020-07-01", "2020-07-02", "2020-07-02", "2020-07-03", None, None),
    ],
)
def test_intersection(
    s1: str,
    e1: str,
    s2: str,
    e2: str,
    s_expected: str | None,
    e_expected: str | None,
) -> None:
    interval1 = Interval(
        datetime.fromisoformat(s1), datetime.fromisoformat(e1)
    )
    interval2 = Interval(
        datetime.fromisoformat(s2), datetime.fromisoformat(e2)
    )

    if s_expected is None or e_expected is None:
        assert intersection(interval1, interval2) is None
    else:
        expected_intersection = Interval(
            datetime.fromisoformat(s_expected),
            datetime.fromisoformat(e_expected),
        )
        assert intersection(interval1, interval2) == expected_intersection
