# Exercise 24: Money and Decimal

An invoice calculator that handles line items, discounts, and tax. The implementation has **3 bugs** — all relating to float/Decimal handling and rounding.

## How to run the tests

```bash
cd exercises/24_money_and_decimal
python3 -m unittest test_invoice
```

Your goal is to edit `invoice.py` until all tests pass. Do **not** modify the test file.

## Functions under test

- `subtotal(items)` — sum of all line items' totals.
- `apply_discount(amount, percent)` — subtract a percentage discount.
- `apply_tax(amount, rate)` — add tax at a decimal rate (e.g. `0.0725`).
- `quantize_cents(amount)` — round to two decimals using commercial rules.
- `calculate_total(items, discount_percent, tax_rate)` — top-level pipeline.

## Hints

<details>
<summary>Hint 1 (gentle)</summary>

All inputs and outputs should be `Decimal`. Anywhere that a `float` sneaks into the arithmetic will either crash (Python 3.11 raises `TypeError` on `float + Decimal`) or quietly introduce imprecision.

Also: Python's built-in `round()` on `Decimal` uses *banker's rounding* (ROUND_HALF_EVEN), which is not what finance expects.

</details>

<details>
<summary>Hint 2 (moderate)</summary>

1. In `subtotal`, check what type the accumulator starts as. The first `+=` with a `Decimal` will reveal the type mismatch.
2. `apply_discount` uses `percent` directly as a multiplier ratio — but `percent` is a whole number like `10`, not a decimal fraction like `0.10`. The math doesn't agree with the docstring.
3. `quantize_cents` uses `round()`. For commercial rounding you need `Decimal.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)`.

</details>

<details>
<summary>Hint 3 (specific)</summary>

1. `subtotal`: `total = 0.0` is a float. Change to `total = Decimal("0")`.
2. `apply_discount`: `multiplier = 1 - percent` is wrong. It should be `1 - percent / 100`.
3. `quantize_cents`:
    ```python
    from decimal import ROUND_HALF_UP, Decimal
    return amount.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    ```

</details>

## Why this matters

- A single penny off on an invoice is a customer-service ticket. A systematic penny-off is a regulatory issue.
- Python 3.11 made `Decimal + float` raise `TypeError` (it used to succeed with silent precision loss). That's a good thing — you want the crash at test time, not a year from now in production.
- The built-in `round()` function on `Decimal` uses banker's rounding because the decimal module's *context* defaults to ROUND_HALF_EVEN. Commercial rounding has to be explicit.

## Relevant reading

- `guides/09_modern_data_types.py` — Section 5 (Decimal for money)
