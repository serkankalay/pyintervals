from __future__ import annotations

import bisect
from typing import Sequence, TypeVar

from _typeshed import SupportsRichComparison

T = TypeVar("T", bound=SupportsRichComparison)


def weak_predecessor(sorted_sequence: Sequence[T], point: T) -> T | None:
    # If the passed sequence is empty, then no predecessor.
    if not sorted_sequence:
        return None

    insertion_point = bisect.bisect_left(sorted_sequence, point)
    if insertion_point == len(sorted_sequence):
        # Then, we need to insert to the end of the collection.
        # Hence, the weak predecessor is the last element in the list.
        return sorted_sequence[insertion_point - 1]

    if (
        current := sorted_sequence[insertion_point]
    ) and current > point:  # type: ignore
        # Then, we found a point which is the successor of our reference.
        # Hence, return the predecessor.

        # If the insertion point is found to be 0, then there is no predecessor
        if insertion_point == 0:
            return None
        else:
            return sorted_sequence[insertion_point - 1]

    # Otherwise, we found the correct point
    return current
