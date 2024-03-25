from __future__ import annotations

from .interval import Interval, contains, overlaps
from .interval_handler import IntervalHandler
from .time_value_node import TimeValueNode

__version__ = __import__("importlib.metadata").metadata.version(__name__)

__all__ = [
    # document & pages
    "Interval",
    "overlaps",
    "contains",
    "IntervalHandler",
    "TimeValueNode",
]
