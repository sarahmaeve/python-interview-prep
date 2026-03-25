# Solution 13 --- Type Hint Bugs in `grade_processor.py`

## Bugs Found

### Bug 1: `calculate_gpa` returns `None` for empty grades (line 31)

The bare `return` produces `None`, but callers (including `get_honor_roll`) compare the
result with `>=`, which raises `TypeError: '>=' not supported between 'NoneType' and 'float'`.

### Bug 2: `parse_records` stores `student_id` as `int` (line 21)

The raw JSON data supplies `student_id` as an integer (e.g. `1001`). The code stores it
as-is, but `format_transcript` calls `record.student_id.upper()`, which crashes because
`int` has no `.upper()` method.

### Bug 3: `get_honor_roll` returns `None` when nobody qualifies (line 46)

Callers expect an iterable list (e.g. `for name in get_honor_roll(records)`). Returning
`None` instead of `[]` causes a `TypeError` on iteration.

### Bug 4: `merge_records` sets `grades` to a list of tuples (line 58)

`list(dict.items()) + list(dict.items())` yields a `list[tuple]`, but the rest of the
codebase expects `grades` to be a `dict[str, float]`. Calling `.items()` or `.values()`
on the merged record fails with `AttributeError`.

---

## Diagnosis Process

1. **Read the tests first.** `test_empty_grades_returns_zero` asserts the result is a
   `float` equal to `0.0` -- trace into `calculate_gpa` and see the bare `return`.
2. **`test_student_id_is_string`** asserts `isinstance(..., str)` -- trace into
   `parse_records` and see that `raw["student_id"]` (an int) is never converted.
3. **`test_none_qualify_returns_empty_list`** asserts `isinstance(result, list)` -- trace
   into `get_honor_roll` and see the `return None` branch.
4. **`test_merged_grades_is_dict`** asserts `isinstance(merged.grades, dict)` -- trace
   into `merge_records` and see the list concatenation is never wrapped in `dict()`.

---

## The Fix

### Bug 1

```python
# Before
if not record.grades:
    return

# After
if not record.grades:
    return 0.0
```

### Bug 2

```python
# Before
student_id=raw["student_id"],

# After
student_id=str(raw["student_id"]),
```

### Bug 3

```python
# Before
if not honor:
    return None

# After
if not honor:
    return []
```

### Bug 4

```python
# Before
combined_grades = list(existing.grades.items()) + list(new.grades.items())

# After
combined_grades = {**existing.grades, **new.grades}
```

(and pass `combined_grades` directly -- it is already a `dict`.)

---

## How Type Hints Would Have Prevented This

### Bug 1 -- `def calculate_gpa(record: StudentRecord) -> float:`

mypy error: *"Returning `None` from a function declared to return `float`."*
The bare `return` is implicitly `return None`, which violates the `-> float` contract.

### Bug 2 -- `student_id: str` on `StudentRecord.__init__`

mypy error: *"Argument 'student_id' has incompatible type `int`; expected `str`."*
Passing the raw int from the JSON dict would be flagged immediately.

### Bug 3 -- `def get_honor_roll(...) -> list[str]:`

mypy error: *"Returning `None` from a function declared to return `list[str]`."*
The `return None` branch directly contradicts the return type.

### Bug 4 -- `grades: dict[str, float]` on `StudentRecord.__init__`

mypy error: *"Argument 'grades' has incompatible type `list[tuple[str, float]]`; expected `dict[str, float]`."*
The list-of-tuples would be caught at construction time.

---

## Discussion

Every bug in this module is a **type mismatch**: the code produces a value of one type
where a different type is expected. Python's dynamic typing lets these mismatches slip
through silently until a specific code path triggers a crash at runtime.

Type annotations serve as **machine-checked documentation**. They cost almost nothing to
write, but they let tools like mypy catch entire categories of bugs -- `None`-where-a-value-is-expected, wrong container type, int-vs-str confusion -- before any test is run.
The lesson: annotate return types and constructor parameters first; that alone catches
the majority of real-world type bugs.
