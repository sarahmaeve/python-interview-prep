# Solution: Exercise 24 — Money and Decimal

## Bugs Found

1. **`subtotal` accumulator starts as a `float`.** `total = 0.0` then `total += Decimal(...)` raises `TypeError` in Python 3.11+ (and produced silent precision loss in older versions).

2. **`apply_discount` uses `percent` directly as a fraction.** The docstring says percent is a whole number like `10` for 10%, but the multiplier is `1 - percent`, not `1 - percent / 100`. A 10% discount turns into a `-900%` discount.

3. **`quantize_cents` uses `round()`.** Python's `round()` on `Decimal` uses *banker's rounding* (ROUND_HALF_EVEN). Commercial finance requires ROUND_HALF_UP (round 0.5 away from zero).

## Diagnosis Process

- `test_empty_cart_returns_zero` would pass if the function returned `0` or `0.0`, but `test_return_type_is_decimal` pins it down: the accumulator type matters. First `test_sum_of_line_items` iteration adds `Decimal("3.00")` to `0.0`, which raises `TypeError` on 3.11.
- `test_ten_percent_off_hundred` fails with an obviously-wrong result (`-900`), pointing directly at `apply_discount`'s arithmetic.
- `test_half_up_rounds_away_from_zero` fails with `Decimal('0.12')` instead of `Decimal('0.13')`. This is the diagnostic for banker's vs. commercial rounding.

## The Fix

### Bug 1 — `subtotal` accumulator type

```python
def subtotal(items: list[LineItem]) -> Decimal:
    total = Decimal("0")
    for item in items:
        total += line_total(item)
    return total
```

### Bug 2 — `apply_discount` multiplier

```python
def apply_discount(amount: Decimal, percent: Decimal) -> Decimal:
    multiplier = 1 - percent / 100
    return amount * multiplier
```

### Bug 3 — `quantize_cents` rounding rule

```python
from decimal import ROUND_HALF_UP, Decimal

def quantize_cents(amount: Decimal) -> Decimal:
    return amount.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
```

## Why This Bug Matters

- **Float/Decimal mixing is a correctness bug, not just a style issue.** Python 3.11 made `Decimal + float` raise `TypeError`. That's a *good* thing: the error shows up at test time, not silently in a rounded-down total on a customer invoice. If you're on 3.11+, `TypeError` on an accumulator is the universe telling you the bug exists.
- **Percentages are a modelling choice.** Some APIs take percents as whole numbers (`10` for 10%), others take fractions (`0.10`). Whichever you pick, be consistent and document it in the type — ideally with a small `Percent` NewType or dataclass to make the unit obvious.
- **Banker's vs. commercial rounding.** The decimal module's default context uses `ROUND_HALF_EVEN` (banker's), which minimises bias across large aggregate sums. That's mathematically defensible but differs from what accountants, tax authorities, and end users expect. Commercial software almost always wants `ROUND_HALF_UP`. Know which your domain requires.

## Discussion

- Construct `Decimal` from strings, not floats: `Decimal("0.1")`, not `Decimal(0.1)`. The latter captures the float's binary approximation and defeats the purpose.
- `Decimal.quantize(Decimal("0.01"), rounding=...)` is how you round to a specific number of places. Passing `rounding=ROUND_HALF_UP` makes the rule explicit — don't rely on the module's context setting, which is global and surprisingly mutable.
- For total invoice correctness, the ORDER of operations matters (discount then tax vs. tax then discount), but because both are multiplicative the result is the same under real numbers. The only reason order matters at cents-precision is rounding — consider quantizing ONLY at the end, not after each step.
- If you need *both* rational arithmetic AND unit tracking (e.g., "multiply this price by a 0.0725 tax rate and produce a TaxedAmount"), look at the `decimal` module's context manager (`decimal.localcontext()`) or a library like `py-moneyed`.
