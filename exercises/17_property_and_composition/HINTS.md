# Hints: Exercise 17 — Properties and Composition

## Hint 1

Compare how the tests access each value—attribute lookup, assignment, or method
call—with how the class defines it.

## Hint 2

One computed method needs property access, one conversion method must be the
property setter, and the station must retain sensor objects rather than labels.

## Hint 3

Add `@property` to `average`; define the unit conversion with `@unit.setter`
and the same method name; store `sensor` as the dictionary value; exclude
`None` averages before summing.

The complete walkthrough is in
[solutions/17_solution.md](../../solutions/17_solution.md).
