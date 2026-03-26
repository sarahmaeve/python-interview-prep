# Exercise 22: Statistics Module

## Format: Pure TDD

The tests in `test_stats.py` are **complete and correct** — every assertion is already written. Your only job is to implement `stats.py` until all 15 tests pass.

This is how TDD works in practice: the tests define the spec. Read them before you write a single line of implementation.

This exercise practices: **reading tests as a spec, implementing to a contract, edge-case handling**.

**Target time: ~10 minutes.**

## Your Task

1. Read `test_stats.py` thoroughly — the tests tell you exactly what each function must do.
2. Open `stats.py` and implement each function. All five currently contain only `pass`.
3. Run the tests and iterate until everything is green:

```bash
python3 -m unittest test_stats -v
```

All 15 tests should fail before you start (the skeleton returns `None` for everything). Your goal is to get them all passing.

## Constraints

- Use only the standard library — no `statistics` module
- Raise `ValueError` for empty input where noted
- Do not modify the input list inside `median`
- Results must be accurate to reasonable floating-point precision

## Function Summary

| Function | Description |
|----------|-------------|
| `mean(numbers)` | Arithmetic mean; raises `ValueError` for empty input |
| `median(numbers)` | Middle value (or average of two middle values for even length); must not modify input; raises `ValueError` for empty |
| `mode(numbers)` | Most frequent value; ties broken by smallest value; raises `ValueError` for empty |
| `std_dev(numbers)` | Population standard deviation; raises `ValueError` for empty |
| `percentile(numbers, p)` | p-th percentile (0–100) using linear interpolation; raises `ValueError` for empty or invalid `p` |

## Hints (only if you're stuck)

<details>
<summary>Hint — median</summary>
Sort a copy of the list. For even length <code>n</code>, average the elements at indices <code>n//2 - 1</code> and <code>n//2</code>.
</details>

<details>
<summary>Hint — mode with tie-breaking</summary>
Build a frequency dict, find the max frequency, then return <code>min()</code> of all values that share that frequency.
</details>

<details>
<summary>Hint — percentile linear interpolation</summary>
Scale <code>p</code> to an index: <code>index = p / 100 * (n - 1)</code>. Split into integer part <code>i</code> and fractional part <code>f</code>. Result is <code>sorted_data[i] * (1 - f) + sorted_data[i + 1] * f</code> (handle the boundary when <code>i + 1 == n</code>).
</details>
