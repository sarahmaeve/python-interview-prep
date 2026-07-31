# Hints: Exercise 04 — Shapes Hierarchy

## Hint 1

Trace initialization through the inheritance chain and inspect values used in
each formula.

## Hint 2

One subclass updates its own dimension name but not the dimensions used by its
inherited method. Another method uses the wrong geometric formula, and string
conversion refers to a method without calling it.

## Hint 3

When resizing a square, update the width and height used by inherited
`Rectangle.area`; compute circle area rather than circumference; call `area()`
in the string representation.

The complete walkthrough is in
[solutions/04_solution.md](../../solutions/04_solution.md).
