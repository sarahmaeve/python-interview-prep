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

## Principle Primer

Keep a monetary calculation in one numeric domain from input through output.
`Decimal` should be constructed from decimal text or integers, not from an
already-approximated binary float. Percentage units must be explicit, and
rounding is a business rule: quantize at the required boundary with the named
rounding mode rather than assuming a default.

If you get stuck, use [HINTS.md](HINTS.md).

## Why this matters

- A single penny off on an invoice is a customer-service ticket. A systematic penny-off is a regulatory issue.
- `Decimal` and `float` have refused to mix in Python arithmetic since long
  before 3.11. The imprecision trap is constructing `Decimal(0.1)`, which
  exactly preserves the already-approximated float.
- Rounding rules are domain decisions. This exercise requires `ROUND_HALF_UP`;
  other accounting or regulatory contexts may require a different rule.

## Relevant reading

- `guides/09_modern_data_types.py` — Section 5 (Decimal for money)
