# Exercise 01: Shopping Cart

A small shopping cart module with three utility functions: calculating totals, applying discounts, and formatting receipts. The implementation has **3 bugs** for you to find and fix.

## How to run the tests

```bash
cd exercises/01_basic_functions
python3 -m unittest test_shopping_cart
```

Your goal is to edit `shopping_cart.py` until all tests pass. Do **not** modify the test file.

## Functions

- `calculate_total(items)` — takes a list of dicts, each with `"name"` and `"price"` keys, and returns the numeric total.
- `apply_discount(total, percent)` — takes a numeric total and a whole-number percentage (e.g. `10` for 10%) and returns the discounted total.
- `format_receipt(items, total)` — returns a newline-separated string listing every item and the final total.

## Principle Primer

Small functions still have contracts. Track the representation of each value
at the boundary: data that looks numeric may arrive as text, a percentage can
mean a whole number or a ratio, and formatted output has an exact public shape.
Convert once at the boundary, perform calculations on numbers, and format only
when producing display text.

If you get stuck, use [HINTS.md](HINTS.md).
