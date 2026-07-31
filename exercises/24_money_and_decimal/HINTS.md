# Hints: Exercise 24 — Money and Decimal

## Hint 1

Inspect the type of every operand and write each percentage in words before
checking its formula.

## Hint 2

The accumulator begins in the wrong numeric domain, a whole-number percentage
is treated as a ratio, and the rounding operation does not name the required
business mode.

## Hint 3

Start the subtotal with `Decimal("0")`, divide the discount percentage by 100,
and quantize to `Decimal("0.01")` with `ROUND_HALF_UP`.

The complete walkthrough is in
[solutions/24_solution.md](../../solutions/24_solution.md).
