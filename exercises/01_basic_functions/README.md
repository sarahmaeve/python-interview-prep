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

## Hints

<details>
<summary>Hint 1 (gentle)</summary>
Pay attention to the data types flowing through each function. Are the inputs what the code expects?
</details>

<details>
<summary>Hint 2 (moderate)</summary>
One function has an arithmetic error involving how percentages are represented. Another has an off-by-one iteration error.
</details>

<details>
<summary>Hint 3 (specific)</summary>

1. `calculate_total`: The `"price"` values in each item dict are strings, not numbers. The function needs to convert them.
2. `apply_discount`: The `percent` parameter is a whole number (e.g. 10), but the code uses it as if it were already a decimal (0.10).
3. `format_receipt`: The loop range excludes the last item.

</details>
