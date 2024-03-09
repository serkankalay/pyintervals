from __future__ import annotations

import pytest
from sortedcontainers import SortedList

from pyintervals.search import weak_predecessor


@pytest.mark.parametrize(
    "sequence, point, expected",
    [
        ([], 0, None),
        ([1, 2, 3, 4], 0, None),
        ([1, 2, 3, 4], 1, 1),
        ([1, 2, 3, 4], 3, 3),
        ([1, 2, 3, 4], 4, 4),
        ([1, 2, 3, 4], 1.5, 1),
        ([1, 2, 3, 4], 4.5, 4),
    ],
)
def test_weak_predecessor(sequence, point, expected) -> None:
    assert weak_predecessor(SortedList(sequence), point) == expected
