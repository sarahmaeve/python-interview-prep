# Hints: Exercise 23 — Dataclass Refactor

## Hint 1

Compare words such as “immutable,” “new,” and “identity” in the docstrings with
the generated dataclass behavior.

## Hint 2

Look at `frozen`, `default_factory`, field comparison options, and
`dataclasses.replace`.

## Hint 3

Freeze `UserProfile`; give timestamps per-instance factories; exclude the audit
timestamp from comparison; replace the profile when granting a role rather
than mutating it.

The complete code is in
[solutions/23_solution.md](../../solutions/23_solution.md).
