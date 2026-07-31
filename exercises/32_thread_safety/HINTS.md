# Hints: Exercise 32 — Thread Safety

## Hint 1

List every method that reads or writes shared state, then trace lock ownership
through every return and exception path.

## Hint 2

The sale is a check-then-act sequence, restocking can raise while holding the
lock, and reporting iterates while writers can resize the dictionary.

## Hint 3

Protect the complete sale operation with `with self._lock`, use the same
context-manager form for restocking, and copy the channel dictionary while
holding the lock.

The complete walkthrough is in
[solutions/32_solution.md](../../solutions/32_solution.md).
