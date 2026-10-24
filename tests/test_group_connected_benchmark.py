"""Compares the two `group_connected` engines.

Run with `pytest tests/test_group_connected_benchmark.py --benchmark-enable`.
"""

from __future__ import annotations

import random
from collections.abc import Callable
from datetime import datetime, timedelta

import pytest
from pytest_benchmark.fixture import BenchmarkFixture  # type: ignore[import-untyped]

from pyintervals import Interval, group_connected
from pyintervals.itertools import _sweep

pytestmark = pytest.mark.filterwarnings("ignore::pytest_benchmark.logger.PytestBenchmarkWarning")

BASE = datetime(2024, 1, 1)


def _intervals(starts_and_lengths: list[tuple[int, int]]) -> list[Interval]:
    return [
        Interval(BASE + timedelta(minutes=s), BASE + timedelta(minutes=s + length)) for s, length in starts_and_lengths
    ]


def sparse(n: int, rng: random.Random) -> list[Interval]:
    """Short items spread out so that almost every item is its own group."""
    return _intervals([(i * 100 + rng.randint(0, 20), rng.randint(1, 30)) for i in range(n)])


def realistic(n: int, rng: random.Random) -> list[Interval]:
    """Short items with moderate overlap, giving many groups of a few items each."""
    return _intervals([(i * 10 + rng.randint(0, 15), rng.randint(5, 40)) for i in range(n)])


def one_chain(n: int, rng: random.Random) -> list[Interval]:
    """Short items that each overlap the next, giving a single group of n items."""
    return _intervals([(i * 10, rng.randint(11, 30)) for i in range(n)])


def heavy_overlap(n: int, rng: random.Random) -> list[Interval]:
    """Long items that all span most of the timeline, which is the handler's worst case."""
    return _intervals([(rng.randint(0, n), n * 2 + rng.randint(0, n)) for _ in range(n)])


PATTERNS: dict[str, Callable[[int, random.Random], list[Interval]]] = {
    "sparse": sparse,
    "realistic": realistic,
    "one_chain": one_chain,
    "heavy_overlap": heavy_overlap,
}
SIZES = [1_000, 10_000]


def _data(pattern: str, size: int) -> tuple[list[Interval], list[Interval]]:
    """Returns the same items shuffled and ordered by start."""
    rng = random.Random(42)
    items = PATTERNS[pattern](size, rng)
    shuffled = list(items)
    rng.shuffle(shuffled)
    return shuffled, sorted(shuffled, key=lambda i: i.start)


def _identity(i: Interval) -> Interval:
    return i


@pytest.fixture(autouse=True)
def _only_when_benchmarking(benchmark: BenchmarkFixture) -> None:
    """The heavy patterns take minutes with the handler, so the regular test run skips this module."""
    if benchmark.disabled:
        pytest.skip("pass --benchmark-enable to run the benchmarks")


@pytest.mark.parametrize("size", SIZES)
@pytest.mark.parametrize("pattern", PATTERNS)
class TestEngines:
    def test_handler_on_unsorted(self, benchmark: BenchmarkFixture, pattern: str, size: int) -> None:
        shuffled, _ = _data(pattern, size)
        benchmark.group = f"{pattern}-{size}"
        benchmark(lambda: list(group_connected(shuffled, key=_identity)))

    def test_sort_then_sweep(self, benchmark: BenchmarkFixture, pattern: str, size: int) -> None:
        shuffled, _ = _data(pattern, size)
        benchmark.group = f"{pattern}-{size}"
        benchmark(lambda: list(_sweep(sorted(shuffled, key=lambda i: i.start), _identity)))

    def test_sweep_on_presorted(self, benchmark: BenchmarkFixture, pattern: str, size: int) -> None:
        _, presorted = _data(pattern, size)
        benchmark.group = f"{pattern}-{size}"
        benchmark(lambda: list(group_connected(presorted, key=_identity, assume_sorted=True)))
