# Hints: Exercise 40 — Retry Idempotency

## Hint 1

Trace one logical submission through two attempts. Write down every key and the
request/result stored under the public operation ID.

## Hint 2

Inspect where the attempt key is created, how cached completion is detected,
and what happens to the recorded payload when an existing operation ID is
submitted with different content.

## Hint 3

- Generate or accept the operation key once, then pass that same key to every
  gateway attempt.
- Test `operation_id in self._results` rather than the cached result's truth
  value.
- Compare an existing payload before writing; raise `IdempotencyConflict` when
  it differs.

The complete walkthrough is in
[solutions/40_solution.md](../../solutions/40_solution.md).
