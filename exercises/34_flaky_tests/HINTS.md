# Hints: Exercise 34 — Flaky Tests

## Hint 1

Classify each failure by whether it changes within a process, across processes,
or with test order.

## Hint 2

Inspect uncontrolled random choice, assumptions about set order, dependence on
the real clock, and mutable class-level fixture state.

## Hint 3

Inject a deterministic RNG, compare unordered values without relying on order,
use fixed times through the provided seam, and create a fresh mutable fixture
for each test.

The complete repaired tests are in
[solutions/34_solution.md](../../solutions/34_solution.md).
