📐 pyintervals
===============================

**Execute efficient interval operations in Python.**

*(Currently in active development. Leave a* ⭐️ *on GitHub if you're interested how this develops!)*

Why?
--------

Inspired by a discussion and initial implementation in a professional project
and a library I've been using in one of my previous jobs, **pyintervals** is born.

Intervals pop-up frequently in programming, specifically in domains where you
have an activity or a proxy for it. Suppose you are implementing a single machine scheduling algorithm.
In order to schedule an operation, you need to makes sure that the machine is available
during your desired time of operation. Or you are implementing a booking system and need to check
that the hotel has at least 1 room with desired number of beds for the dates selected.
For such cases, you need to control some information overlapping with an interval.

Acknowledgements
----------------

Following resources and people have inspired **pyintervals**:

- `Always use [closed, open) intervals <https://fhur.me/posts/always-use-closed-open-intervalshttps://fhur.me/posts/always-use-closed-open-intervals>`_
- `Arie Bovenberg <https://github.com/ariebovenberg>`_
- `pdfje (for initial setup of this project) <https://github.com/ariebovenberg/pdfje>`_
- Sam de Wringer
- Tim Lamballais-Tessensohn
