# Hints: Exercise 06 — Event Logger

## Hint 1

Look for state that survives between objects and state that changes merely
because a summary was requested.

## Hint 2

Construct two default-tag events, mutate a list returned by a query, and compare
tag order before and after `get_summary()`.

## Hint 3

Use a `None` sentinel for the mutable default, return a copy from
`get_events_by_tag`, and count tags without sorting each event's list in place.

The complete walkthrough is in
[solutions/06_solution.md](../../solutions/06_solution.md).
