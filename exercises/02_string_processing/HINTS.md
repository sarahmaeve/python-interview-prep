# Hints: Exercise 02 — String Processing

## Hint 1

Check index zero, the exact maximum output length, and whitespace at each new
line.

## Hint 2

One loop handles characters after spaces but not the first character. The
ellipsis consumes part of the truncation budget.

## Hint 3

- Capitalize the first character as well as characters following spaces.
- Slice to `max_length - 3` before appending `"..."`.
- Do not carry a leading separator onto a newly wrapped line.

The complete walkthrough is in
[solutions/02_solution.md](../../solutions/02_solution.md).
