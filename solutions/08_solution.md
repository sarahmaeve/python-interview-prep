# Solution: Exercise 08 — Iteration Mutation (Task Manager)

## Bugs Found

1. **`remove_completed`** — Removes elements from `self.tasks` while iterating over it with a `for` loop. When a completed task is removed, the iterator skips the next element, so consecutive completed tasks are not all removed.

2. **`get_overdue`** — Compares date strings in `MM/DD/YYYY` format lexicographically. This fails because month comes first: `"12/01/2025" > "02/01/2027"` lexicographically, even though Dec 2025 is before Feb 2027. Dates must be parsed before comparison.

3. **`bulk_reassign`** — Uses a generator expression, which is consumed on the first pass (`sum(1 for _ in matching)`). The second pass (`for task in matching`) iterates over an already-exhausted generator and does nothing, so tasks are counted but never actually reassigned.

## Diagnosis Process

- For bug 1: `test_remove_consecutive_completed` adds T1 (completed), T2 (completed), T3 (pending). After removing T1 at index 0, T2 shifts to index 0 but the iterator advances to index 1 (now T3), skipping T2.
- For bug 2: `test_overdue_lexicographic_trap` sets up `"12/01/2025"` (overdue) and `"02/01/2027"` (not overdue). Lexicographic `<` of `"12/01/2025" < "03/25/2026"` is `False` (since `"1" < "0"` is `False`), so the truly overdue task is missed.
- For bug 3: `test_bulk_reassign_actually_changes_assignee` checks that after `bulk_reassign`, the assignee field is actually updated. The generator is exhausted by `sum()`, so the subsequent `for` loop is a no-op.

## The Fix

### Bug 1 — Mutating list during iteration
```python
# Before
for task in self.tasks:
    if task["status"] == "completed":
        self.tasks.remove(task)

# After
self.tasks = [task for task in self.tasks if task["status"] != "completed"]
```

### Bug 2 — Lexicographic date comparison
```python
# Before
if task["due_date"] < today:

# After
from datetime import datetime

def get_overdue(self, today):
    today_dt = datetime.strptime(today, "%m/%d/%Y")
    overdue = []
    for task in self.tasks:
        task_dt = datetime.strptime(task["due_date"], "%m/%d/%Y")
        if task_dt < today_dt:
            overdue.append(task)
    return overdue
```

### Bug 3 — Generator exhaustion
```python
# Before
matching = (t for t in self.tasks if t["assignee"] == from_user)
count = sum(1 for _ in matching)
for task in matching:   # generator already exhausted
    task["assignee"] = to_user

# After
matching = [t for t in self.tasks if t["assignee"] == from_user]
count = len(matching)
for task in matching:
    task["assignee"] = to_user
return count
```

## Why This Bug Matters

- **Mutating a list during iteration** is undefined behavior in Python. The iterator uses an internal index that becomes invalid when elements shift. The idiomatic fix is to build a new list with a comprehension or iterate over a copy (`for task in self.tasks[:]`).
- **String comparison of dates** is a recurring bug. Strings sort lexicographically, which only matches chronological order for ISO 8601 format (`YYYY-MM-DD`). For any other format, parse to `datetime` first.
- **Generator exhaustion** is subtle because generators look like lists but can only be iterated once. After the first full pass, they yield nothing. Use a list when you need multiple passes over the data.

## Discussion

- For bug 1, `self.tasks[:] = [t for t in self.tasks if t["status"] != "completed"]` mutates the list in place (preserving any external references). A full reassignment (`self.tasks = ...`) creates a new list, which is fine if nothing else holds a reference.
- For bug 2, if dates were stored as `datetime` objects from the start, comparison would work natively. Storing dates as strings is a code smell — consider converting at input time.
- For bug 3, an alternative is to count and reassign in a single pass: iterate once, reassign each match, and increment a counter. This is more efficient and avoids the two-pass problem entirely.
