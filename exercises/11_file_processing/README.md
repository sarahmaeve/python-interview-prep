# Exercise 11: CSV Sales Report Generator

A simple CSV sales report generator that reads sales data, calculates revenue totals by product, and writes a summary report. The implementation has **3 bugs** for you to find and fix.

This exercise focuses on **file I/O patterns** -- proper resource management, accumulation logic, and error propagation. The tests use `unittest.mock.patch` and `mock_open` to verify file handling without touching the filesystem.

## How to run the tests

```bash
cd exercises/11_file_processing
python3 -m unittest test_csv_report
```

Your goal is to edit `csv_report.py` until all tests pass. Do **not** modify the test file.

## Functions

- `read_sales_data(filepath)` -- reads a CSV file with columns `product,quantity,price` and returns a list of dicts with keys `"product"`, `"quantity"` (int), and `"price"` (float).
- `calculate_totals(sales_data)` -- groups by product and returns a dict mapping product name to total revenue (sum of quantity * price for each row).
- `generate_report(filepath, output_path)` -- reads sales data, calculates totals, and writes a summary report. Should propagate errors from the read step.

## Hints

<details>
<summary>Hint 1 (gentle)</summary>
How does the code manage the file it opens? What happens if an exception occurs before cleanup?
</details>

<details>
<summary>Hint 2 (moderate)</summary>
When a product appears multiple times, does the running total actually accumulate?
</details>

<details>
<summary>Hint 3 (specific)</summary>

1. `read_sales_data` uses `open()` without a `with` statement and never calls `.close()`, leaking the file handle.
2. `calculate_totals` uses `setdefault` to initialize `0` but then assigns (`=`) instead of accumulating (`+=`), so only the last row per product counts.
3. `generate_report` catches `FileNotFoundError` from the read step but still proceeds to write an empty report file. It should let the error propagate.

</details>
