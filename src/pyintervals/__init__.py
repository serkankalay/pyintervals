from __future__ import annotations

from .interval import Interval, contains, overlaps

__version__ = __import__("importlib.metadata").metadata.version(__name__)

__all__ = [
    # document & pages
    "Interval",
    "overlaps",
    "contains",
]
