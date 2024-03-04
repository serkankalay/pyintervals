import bisect
from typing import TypeVar, Sequence

T = TypeVar("T")


def weak_predecessor(sorted_sequence: Sequence[T], point: T) -> T:
    insertion_point = bisect.bisect_left(sorted_sequence, point)
    if insertion_point == len(sorted_sequence):
        # Then, we need to insert to the end of the collection.
        # Hence, the weak predecessor is the last element in the list.
        return sorted_sequence[insertion_point - 1]

    if (current := sorted_sequence[insertion_point]) and current > point:
        # Then, we found a point which is the successor of our reference.
        # Hence, return the predecessor.
        return sorted_sequence[insertion_point - 1]

    # Otherwise, we found the correct point
    return current
