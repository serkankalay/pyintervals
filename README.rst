📐 pyintervals
===============================

.. image:: https://img.shields.io/pypi/v/pyintervals.svg?style=flat-square&color=blue
   :target: https://pypi.python.org/pypi/pyintervals

.. image:: https://img.shields.io/pypi/pyversions/pyintervals.svg?style=flat-square
   :target: https://pypi.python.org/pypi/pyintervals

.. image:: https://img.shields.io/pypi/l/pyintervals.svg?style=flat-square&color=blue
   :target: https://pypi.python.org/pypi/pyintervals

.. image:: https://img.shields.io/badge/mypy-strict-forestgreen?style=flat-square
   :target: https://mypy.readthedocs.io/en/stable/command_line.html#cmdoption-mypy-strict

.. image:: https://img.shields.io/badge/coverage-99%25-forestgreen?style=flat-square
   :target: https://github.com/serkankalay/pyintervals

.. image::  https://img.shields.io/github/actions/workflow/status/serkankalay/pyintervals/tests.yml?branch=master&style=flat-square
   :target: https://github.com/serkankalay/pyintervals

**Execute efficient interval operations in Python.**

*(Currently in active development. Leave a* ⭐️ *on GitHub if you're interested how this develops!)*

Why?
--------

Inspired by a discussion and initial implementation in a professional project
and a library I've been using in one of my previous jobs, **pyintervals** is born.

Intervals pop-up frequently in programming, specifically in domains where you
have an activity or a proxy for it.

- Suppose you are implementing a single machine scheduling algorithm.
  In order to schedule an operation, you need to makes sure that the machine is available
  during your desired time of operation.
- Or you are implementing a booking system and need to check
  that the hotel has at least 1 room with desired number of beds for the dates selected.
  For such cases, you need to control some information overlapping with an interval.

As the examples suggest, **pyintervals** defines intervals with date and time.
However, adding support for other comparable types such as ``int``, ``float`` is also possible.

How?
--------

Declare ``Interval`` objects with **pyintervals** and check whether they ``overlap`` with each other or
one ``contains`` the other.

.. code-block:: python

  from pyintervals import Interval, overlaps, contains
  from datetime import datetime

  my_first_interval = Interval(start=datetime(2017,5,20,12,15),end=datetime(2024,10,10,19,0))
  my_second_interval = Interval(start=datetime(2024,10,6,7,21),end=datetime(2024,10,10,19,0))

  overlaps(my_first_interval, my_second_interval)
  >>> True

  my_first_interval.overlaps_with(my_second_interval)
  >>> True

  contains(my_first_interval, my_second_interval)
  >>> True

  my_first_interval.contains(my_second_interval)
  >>> True

  my_third_interval=Interval(start=datetime(1988,5,21,10,45),end=datetime(1989,6,20,1,30))
  overlaps(my_first_interval,my_third_interval)
  >>> False

  contains(my_first_interval,my_third_interval)
  >>> False

**pyintervals** also support `degenerate` intervals, which have their ``start`` equal to their ``end``.

.. code-block:: python

  my_degenerate_interval = Interval(start=datetime(2024,10,10,9,0), end=datetime(2024,10,10,9,0))

  overlaps(my_first_interval, my_degenerate_interval)
  >>> True

  my_same_degenerate_interval = Interval(start=datetime(2024,10,10,9,0), end=datetime(2024,10,10,9,0))

  overlaps(my_degenerate_interval, my_same_degenerate_interval)
  >>> True

What else?
-----------

Interval concept also leads to `aggregate value over time`. Let's dive with an example:

Let there be a beautiful and exclusive patisserie and you heard it from a foodie friend.
She/he suggested you to go there as soon as possible.
You checked your agenda and seems you have an empty spot at your calendar starting at 12:30.
The place is open between 9:00-12:00 and 13:00 - 16:00 daily.

If you want to programatically check whether the shop is open at a given time **T**, then
you need to iterate over `all (in the worst case)` the time intervals the patisserie is open
for the time you are curious about, 12:30 in this case. This will take `O(n)` time.

Linear time is nice but can we not improve it? Well, with **pyintervals**, you can!
What we essentially are curious about is the status of that beautiful store at a given time.
**pintervals** allows you to fetch this value in `O(log n)` time.

.. code-block:: python

  # Add open times with value 1
  mon_interval_1 = Interval(start=datetime(2025,7,21,9,00),end=datetime(2025,7,21,12,0), value=1)
  mon_interval_2 = Interval(start=datetime(2025,7,21,13,00),end=datetime(2025,7,21,16,0), value=1)
  tue_interval_1 = Interval(start=datetime(2025,7,22,9,00),end=datetime(2025,7,22,12,0), value=1)
  tue_interval_2 = Interval(start=datetime(2025,7,22,13,00),end=datetime(2025,7,22,16,0), value=1)

  capacity = IntervalHandler()
  capacity.add(
      [
          mon_interval_1,
          mon_interval_2,
          tue_interval_1,
          tue_interval_2,
      ]
  )

  # Check the capacity, which indicates open when value is positive
  capacity.value_at_time(datetime(2025,7,21,9,30))
  >>> 1  # Open

  capacity.value_at_time(datetime(2025,7,21,12,30))
  >>> 0  # Closed

  capacity.value_at_time(datetime(2025,7,22,13,00))
  >>> 1  # Open

  capacity.value_at_time(datetime(2025,7,22,16,00))
  >>> 0  # Closed

  capacity.value_at_time(datetime(2025,7,22,15,59))
  >>> 1  # Open

See roadmap_ for the list of available and upcoming features.

When?
---------

Start with **pyintervals** right away with

.. code-block:: bash

  pip install pyintervals

.. _roadmap:

Roadmap
---------
**pyintervals** is in active development and not feature complete yet. Please see below
for completed and planned features.

Features:

✅ = implemented, 🚧 = planned, ❌ = not planned

- Fundamentals:
    - ✅ Overlap controls
    - ✅ Contain controls
- Interval Handler:
    - ✅ Own intervals with associated values
    - ✅ Provide value projection graph
    - ✅ Query value over time
    - 🚧 Access intervals overlapping with a specific timespan
- Single-level Pegging:
    - 🚧 Introduce object association to Intervals
    - 🚧 Single level pegging with first-in-first-out
    - 🚧 Enable callback for pegging quantity
    - 🚧 Enable callback for pegging matching
- Support other comparable types
    - 🚧 Define comparable protocol and generics
    - 🚧 Adapt Interval and Interval Handler concepts

Acknowledgements
----------------

Following resources and people have inspired **pyintervals**:

- `Always use [closed, open) intervals <https://fhur.me/posts/always-use-closed-open-intervalshttps://fhur.me/posts/always-use-closed-open-intervals>`_
- `Arie Bovenberg <https://github.com/ariebovenberg>`_
- `pdfje (for initial setup of this project) <https://github.com/ariebovenberg/pdfje>`_
- `Sam de Wringer <https://github.com/samdewr>`_
- Tim Lamballais-Tessensohn
