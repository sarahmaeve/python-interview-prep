# Exercise 25: Receipt Printer Refactor

## Difficulty: Intermediate

## Context

You are given a working receipt printer with a full test suite that passes.
The code is **correct** but violates nearly every clean-code principle: one
massive function, magic numbers, single-letter variable names, deeply nested
conditionals, and copy-pasted formatting logic.

Your job: **refactor the code so it is clean and maintainable while keeping
every test passing**. Do NOT modify the test file.

## What the code does

`print_receipt(items, tax_rate, discount_code, include_header=True)`:

1. Validates the `items` list (each item is a dict with `"name"`, `"price"`, `"quantity"`).
2. Calculates the subtotal.
3. Applies a discount code:
   - `"SAVE10"` — 10% off the subtotal.
   - `"BULK50"` — $5.00 off orders over $50.
   - `"NONE"` or `""` — no discount.
4. Calculates tax (`subtotal_after_discount * tax_rate`).
5. Adds shipping: free when the **original** subtotal is $100 or more, otherwise $5.99.
6. Formats and returns a multi-line receipt string.

## Instructions

1. Run the tests to confirm they all pass before you change anything:
   ```bash
   cd exercises/25_receipt_printer_refactor
   python3 -m unittest test_receipt_printer -v
   ```
2. Refactor `receipt_printer.py` — improve names, extract helpers, eliminate
   duplication, remove magic numbers, etc.
3. After every meaningful change, re-run the tests to make sure nothing broke.
4. Do **not** modify `test_receipt_printer.py`.

## Clean-code smells to find

- Single-letter variable names that reveal nothing about their purpose.
- Numeric literals scattered through the logic with no explanation.
- Duplicated blocks of code that do the same thing in two places.
- A single function that does validation, calculation, **and** formatting all at once.

## Running the tests

```bash
cd exercises/25_receipt_printer_refactor
python3 -m unittest test_receipt_printer -v
```

## Hints (try without these first)

<details>
<summary>Hint 1 — naming</summary>
Rename variables to reflect what they hold:
<code>t</code> → <code>subtotal</code>, <code>d</code> → <code>discount</code>,
<code>x</code> → <code>tax</code>, <code>s</code> → <code>shipping</code>.
</details>

<details>
<summary>Hint 2 — constants</summary>
Define module-level constants for the magic numbers:

```python
SAVE10_RATE = 0.10
BULK50_AMOUNT = 5.00
BULK50_THRESHOLD = 50.00
FREE_SHIPPING_THRESHOLD = 100.00
SHIPPING_COST = 5.99
```
</details>

<details>
<summary>Hint 3 — single responsibility</summary>
Try splitting the work into three functions:
<code>_validate_items</code>, <code>_calculate_totals</code>,
and <code>_format_receipt</code>. Keep <code>print_receipt</code> as a thin
coordinator that calls them in order.
</details>

<details>
<summary>Hint 4 — DRY formatting</summary>
The currency formatting <code>${value:>7.2f}</code> appears many times.
Extract it:

```python
def _fmt_money(value: float) -> str:
    return f"${value:>7.2f}"
```

Then the <code>include_header</code> flag controls only whether the banner
lines are prepended — not a completely different code path.
</details>
