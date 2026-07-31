# Hints: Exercise 21 — Observability and Logging

## Hint 1

Follow one invalid record and one transform failure through logs, error
tracking, and processed counts.

## Hint 2

Check swallowed exceptions, the visibility threshold of validation messages,
and when a record enters the success collection.

## Hint 3

Record and warn about transform failures, emit validation failures at warning
level, and append to `processed` only after transformation succeeds.

The complete walkthrough is in
[solutions/21_solution.md](../../solutions/21_solution.md).
