# Solution: Exercise 01 - Shopping Cart

## Bugs Found

1. **`calculate_total`** -- Concatenates strings instead of summing numbers. The `price` values in each item dict are strings (e.g. `"1.50"`), but the code adds them to a numeric `total` without converting via `float()`.

2. **`apply_discount`** -- Treats `percent` as a decimal fraction instead of a percentage. Passing `10` for 10% computes `total - total * 10`, giving a wildly negative number. Should divide by 100.

3. **`format_receipt`** -- Item lines print the raw string price without a dollar sign or decimal formatting (`Apple: 1.50`), while the total line correctly uses `$` and `.2f` formatting (`Total: $7.00`). The item lines need consistent currency formatting.

## Diagnosis Process

- **Bug 1:** The test passes `{"price": "1.50"}` and expects a float result of `7.00`. Running mentally, `0 + "1.50"` raises `TypeError` because you cannot add `str` to `int`. The fix is clear: cast to `float`.
- **Bug 2:** `apply_discount(100.0, 10)` should return `90.0`. The current code returns `100 - 100*10 = -900`. The percent parameter must be divided by 100.
- **Bug 3:** `test_single_item_receipt` expects `"Apple: $1.50"` but the code produces `"Apple: 1.50"` — no dollar sign and no `.2f` formatting. The item lines use the raw string price while the total line is properly formatted.

## The Fix

### Bug 1 -- `calculate_total`

```python
# Before
total += item["price"]

# After
total += float(item["price"])
```

### Bug 2 -- `apply_discount`

```python
# Before
return total - (total * percent)

# After
return total - (total * percent / 100)
```

### Bug 3 -- `format_receipt`

```python
# Before
lines.append(f"{item['name']}: {item['price']}")

# After
lines.append(f"{item['name']}: ${float(item['price']):.2f}")
```

## Why This Bug Matters

- **Bug 1 (type coercion):** Python does not silently convert strings to numbers. In dynamically typed languages it is critical to validate and convert data at system boundaries (e.g., when reading from JSON or a database).
- **Bug 2 (unit mismatch):** A common source of real-world errors. Always document whether a percentage parameter is `0-100` or `0.0-1.0`, and match the formula to that contract.
- **Bug 3 (inconsistent formatting):** When displaying monetary values, all amounts should use the same format. Mixing raw strings with formatted floats produces a receipt where the items say `1.50` but the total says `$7.00` — confusing and unprofessional.

## Discussion

- `calculate_total` could be a one-liner: `sum(float(item["price"]) for item in items)`.
- Storing prices as strings is common when data comes from JSON; converting early (at parse time) prevents downstream bugs.
- Bug 3 interacts with Bug 1: since prices are strings, you must convert to `float` both for summing (Bug 1) and for formatting (Bug 3). A consistent approach is to convert at parse time.
- `apply_discount` could accept either form if documented, but accepting a human-readable percentage (10 for 10%) is more intuitive for callers.
