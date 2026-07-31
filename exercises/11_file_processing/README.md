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

## Principle Primer

Resource lifetime should be structural: a `with` block closes a file on both
success and failure. Aggregation needs an invariant such as “the stored total
equals all rows processed so far,” which distinguishes accumulation from
replacement. Catch an I/O error only when this layer can recover; otherwise,
preserve it for the caller rather than producing a misleading partial result.

If you get stuck, use [HINTS.md](HINTS.md).
