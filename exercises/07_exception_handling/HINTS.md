# Hints: Exercise 07 — Exception Handling

## Hint 1

For each `except`, ask which exception is expected and what recovery the handler
actually performs.

## Hint 2

Look for a handler that is broader than its operation, a conversion error that
loses its public contract, and validation that suppresses invalid input.

## Hint 3

Narrow the loading handler, preserve `ValueError` with a descriptive message
when integer conversion fails, and allow the `TypeError` from non-iterable
required keys to propagate.

The complete walkthrough is in
[solutions/07_solution.md](../../solutions/07_solution.md).
