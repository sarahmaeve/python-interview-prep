# Solution: Exercise 11 -- File Processing

## Bugs Found

### Bug 1: File handle never closed in `read_sales_data`

**Location:** `read_sales_data`, line 7

The file is opened with `f = open(...)` but there is no `with` statement and no `f.close()`. The test explicitly checks that the context manager protocol is used.

**Diagnosis:** `test_file_is_properly_closed` asserts that `__enter__` and `__exit__` were called on the file handle, which only happens with a `with` statement.

**Before:**
```python
def read_sales_data(filepath):
    f = open(filepath, "r")
    lines = f.read().strip().split("\n")
```

**After:**
```python
def read_sales_data(filepath):
    with open(filepath, "r") as f:
        lines = f.read().strip().split("\n")
```

(The rest of the function body stays the same, now inside the `with` block.)

**Why it matters:** Unclosed file handles can exhaust OS file descriptors under load. The `with` statement guarantees cleanup even if an exception occurs mid-read.

---

### Bug 2: Revenue overwrites instead of accumulates in `calculate_totals`

**Location:** `calculate_totals`, line 33

`totals[product] = revenue` replaces the previous value instead of adding to it.

**Diagnosis:** `test_multiple_rows_same_product_accumulates` passes two Widget rows (10*2.50 + 5*2.50 = 37.50). With `=`, only the last row's revenue (12.50) is stored.

**Before:**
```python
totals[product] = revenue
```

**After:**
```python
totals[product] += revenue
```

**Why it matters:** This is a classic accumulator bug. The `setdefault(product, 0)` on the line above correctly initializes the value, but the assignment on the next line throws that away. Using `+=` is the intended pattern with `setdefault`.

---

### Bug 3: `generate_report` swallows `FileNotFoundError`

**Location:** `generate_report`, lines 41-43

The `try/except` catches `FileNotFoundError` and sets `sales_data = []`, then proceeds to write an empty report. The test expects the error to propagate.

**Diagnosis:** `test_file_not_found_propagates` asserts that `FileNotFoundError` is raised and that the output file is never opened.

**Before:**
```python
try:
    sales_data = read_sales_data(filepath)
except FileNotFoundError:
    sales_data = []
```

**After:**
```python
sales_data = read_sales_data(filepath)
```

Simply remove the try/except and let the exception propagate naturally.

**Why it matters:** Silently swallowing errors and producing empty output is dangerous -- the caller has no way to know something went wrong. Fail loudly so the problem is detected immediately.

---

## Discussion

- **Resource management:** Python's `with` statement is the idiomatic way to manage file handles, database connections, and locks. Always prefer it over manual `open`/`close`.
- **Accumulator patterns:** Alternatives to `setdefault` + `+=` include `collections.defaultdict(float)` or `collections.Counter` for counting use cases.
- **Error handling philosophy:** The original code follows a "defensive" style that hides errors. The corrected version follows "let it crash" -- callers decide how to handle missing files.
