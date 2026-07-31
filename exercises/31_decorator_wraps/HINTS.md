# Hints: Exercise 31 — Decorator `@wraps` and State

## Hint 1

Inspect each decorated callable's `__name__`, signature, `__wrapped__`, and
state after decorating two different functions.

## Hint 2

Check whether each inner wrapper preserves the function it actually wraps and
whether the call counter belongs to the decorator class or instance.

## Hint 3

Apply `functools.wraps(func)` to each call wrapper, not the configuration
layer, and initialize/increment the counter through `self`.

The complete code is in
[solutions/31_solution.md](../../solutions/31_solution.md).
