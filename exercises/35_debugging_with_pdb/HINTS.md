# Hints: Exercise 35 — Debugging with pdb

## Hint 1

Chase each failure independently and locate the first step where state differs
from the assertion's contract.

## Hint 2

Inspect the row slice in parsing, object identity during merging, and the loop
variables and indentation during adjustment.

## Hint 3

Include the final input row, copy a row before storing it for later mutation,
and perform the quantity update inside the matching branch.

Exact locations and repairs are in
[solutions/35_solution.md](../../solutions/35_solution.md).
