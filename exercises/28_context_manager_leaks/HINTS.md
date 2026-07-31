# Hints: Exercise 28 — Context Manager Leaks

## Hint 1

Trace cleanup after both a clean body and a body that raises.

## Hint 2

Inspect the exception guard in `__exit__`, the code surrounding the generator's
`yield`, and whether `run_queries()` enters the pool structurally.

## Hint 3

Close on every `__exit__`, use `try`/`except`/`else` around `yield` to roll back
or commit, and execute queries inside `with pool as conn`.

The complete walkthrough is in
[solutions/28_solution.md](../../solutions/28_solution.md).
