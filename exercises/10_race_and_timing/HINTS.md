# Hints: Exercise 10 — Cache Expiry and Timing

## Hint 1

Write down the expected result immediately before, exactly at, and immediately
after the expiry timestamp.

## Hint 2

Inspect whether cleanup traverses a live dictionary view and whether `size()`
reports stored entries or currently valid entries.

## Hint 3

The tested boundary expires entries only after the deadline, cleanup should
iterate over a stable copy of the keys, and `size()` must evaluate liveness
rather than returning the raw dictionary length.

The complete walkthrough is in
[solutions/10_solution.md](../../solutions/10_solution.md).
