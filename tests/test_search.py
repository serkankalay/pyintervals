import pytest

from pyintervals.search import weak_predecessor


@pytest.mark.parametrize(
    "sequence, point, expected",
    [
        ([1, 2, 3, 4], 1, 1),
        ([1, 2, 3, 4], 3, 3),
        ([1, 2, 3, 4], 4, 4),
        ([1, 2, 3, 4], 1.5, 1),
        ([1, 2, 3, 4], 4.5, 4),
    ],
)
def test_weak_predecessor(sequence, point, expected) -> None:
    assert weak_predecessor(sequence, point) == expected
