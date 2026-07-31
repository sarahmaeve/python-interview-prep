# Solution: Exercise 24 — Money and Decimal

## Bugs Found

1. **`subtotal` accumulator starts as a `float`.** `total = 0.0` then
   `total += Decimal(...)` raises `TypeError`; `Decimal` and `float` do not mix
   directly in arithmetic.

2. **`apply_discount` uses `percent` directly as a fraction.** The docstring says percent is a whole number like `10` for 10%, but the multiplier is `1 - percent`, not `1 - percent / 100`. A 10% discount turns into a `-900%` discount.

3. **`quantize_cents` uses `round()`.** Under the default decimal context,
   `round()` uses half-even rounding. This invoice's stated business rule
   requires `ROUND_HALF_UP` (round 0.5 away from zero).

## Diagnosis Process

- `test_empty_cart_returns_zero` would pass if the function returned `0` or
  `0.0`, but `test_return_type_is_decimal` pins it down: the accumulator type
  matters. The first `test_sum_of_line_items` iteration adds `Decimal("3.00")`
  to `0.0`, which raises `TypeError`.
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

- **Float/Decimal mixing is a correctness bug, not just a style issue.**
  Direct mixed arithmetic raises `TypeError`. Constructing `Decimal(0.1)` is
  the subtler failure mode: it preserves the float's binary approximation, so
  convert from strings or integers at the boundary instead.
- **Percentages are a modelling choice.** Some APIs take percents as whole numbers (`10` for 10%), others take fractions (`0.10`). Whichever you pick, be consistent and document it in the type — ideally with a small `Percent` NewType or dataclass to make the unit obvious.
- **Rounding is a domain rule.** The decimal module's default context uses
  `ROUND_HALF_EVEN`, which minimises bias across aggregate sums. This exercise
  specifies `ROUND_HALF_UP`; real accounting and tax rules vary, so encode the
  required policy explicitly.

## Discussion

- Construct `Decimal` from strings, not floats: `Decimal("0.1")`, not `Decimal(0.1)`. The latter captures the float's binary approximation and defeats the purpose.
- `Decimal.quantize(Decimal("0.01"), rounding=...)` is how you round to a specific number of places. Passing `rounding=ROUND_HALF_UP` makes the rule explicit — don't rely on the module's context setting, which is global and surprisingly mutable.
- For total invoice correctness, the ORDER of operations matters (discount then tax vs. tax then discount), but because both are multiplicative the result is the same under real numbers. The only reason order matters at cents-precision is rounding — consider quantizing ONLY at the end, not after each step.
- If you need *both* rational arithmetic AND unit tracking (e.g., "multiply this price by a 0.0725 tax rate and produce a TaxedAmount"), look at the `decimal` module's context manager (`decimal.localcontext()`) or a library like `py-moneyed`.
