# Hints: Exercise 27 — match/case Dispatch

## Hint 1

Compare every handler argument with the names bound by its mapping pattern.

## Hint 2

The keypress branch loses modifiers, the resize branch does not capture
dimensions, and the wildcard silently returns.

## Hint 3

Bind `modifiers`, `width`, and `height` in their respective patterns and raise
`ValueError` from the unknown-event branch.

The exact patterns are in
[solutions/27_solution.md](../../solutions/27_solution.md).
