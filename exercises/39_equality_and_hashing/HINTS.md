# Hints: Exercise 39 — Equality and Hashing

## Hint 1

Write down the exact state each class uses for equality, then compare that with
the state used for hashing and the state callers may mutate.

## Hint 2

Check normalization in `ProductCode`, assumptions about the other operand in
`Version`, and why `AccountKey` needs `unsafe_hash=True` in its current form.

## Hint 3

- Hash `ProductCode` using the same case-folded representation as equality.
- Return `NotImplemented` when `Version.__eq__` receives an unsupported type.
- Replace `unsafe_hash=True` with `frozen=True` for `AccountKey`.

The complete walkthrough is in
[solutions/39_solution.md](../../solutions/39_solution.md).
