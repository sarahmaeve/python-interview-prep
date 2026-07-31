# Hints: Exercise 36 — Performance Tuning

## Hint 1

Ask what every operation inside each loop costs as the input grows.

## Hint 2

Look for linear list membership inside a loop, recomputation of every prefix,
and repeated insertion at the front of a list.

## Hint 3

Track membership in a set while preserving output order, carry a running total,
and reverse in one pass rather than repeatedly shifting the list.

The complete implementations and complexity analysis are in
[solutions/36_solution.md](../../solutions/36_solution.md).
