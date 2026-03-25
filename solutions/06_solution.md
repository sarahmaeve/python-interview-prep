# Solution: Exercise 06 — Mutable Default Arguments (Event Logger)

## Bugs Found

1. **`Event.__init__`** — The default argument `tags=[]` is a mutable list shared across all instances created without explicit tags. Appending to one event's tags mutates every other default-tags event.

2. **`EventLogger.get_events_by_tag`** — Returns the internal `_tag_index` list directly. Callers who modify the returned list (e.g., `result.clear()`) corrupt the logger's state.

3. **`EventLogger.get_summary`** — Calls `event.tags.sort()`, which sorts the list in place and permanently reorders the event's tags. The test `test_summary_does_not_mutate_event_tag_order` catches this.

## Diagnosis Process

- For bug 1: `test_default_tags_are_independent_between_events` creates two events without tags, appends to one, and asserts the other is still empty. Because `tags=[]` is evaluated once at function definition time, both events share the same list object.
- For bug 2: `test_get_events_by_tag_returns_copy_not_internal_list` calls `result.clear()` and then checks the logger still has the event. If the returned list is the internal one, `clear()` empties it.
- For bug 3: `test_summary_does_not_mutate_event_tag_order` creates an event with `["zebra", "alpha", "middle"]`, calls `get_summary()`, then asserts the original order is preserved.

## The Fix

### Bug 1 — Mutable default argument
```python
# Before
def __init__(self, name, timestamp=None, tags=[]):
    self.tags = tags

# After
def __init__(self, name, timestamp=None, tags=None):
    self.tags = tags if tags is not None else []
```

### Bug 2 — Returning internal list
```python
# Before
return self._tag_index.get(tag, [])

# After
return list(self._tag_index.get(tag, []))
```

### Bug 3 — In-place sort mutates event
```python
# Before
event.tags.sort()

# After
for tag in sorted(event.tags):
```

## Why This Bug Matters

- **Mutable default arguments** are Python's most infamous gotcha. Default values are evaluated once when the function is defined, not each time it is called. Any mutable default (`[]`, `{}`, `set()`) is shared across all calls that use the default.
- **Returning internal references** breaks encapsulation. The caller and the object now share state, leading to action-at-a-distance bugs that are hard to trace.
- **In-place vs. out-of-place operations** — `list.sort()` mutates; `sorted(list)` returns a new list. Know which methods mutate and which return copies.

## Discussion

- The `None`-sentinel pattern (`tags=None` then `tags if tags is not None else []`) is the standard Python idiom. Some codebases use a private sentinel object instead of `None` to allow `None` as a valid argument value.
- For `get_events_by_tag`, returning a copy protects internal state but means the caller works with a snapshot. An alternative is to return a `tuple` or a frozen view to make immutability explicit.
- `sorted()` vs `.sort()` is a general principle: prefer non-mutating operations unless you specifically intend to change the original data. This avoids a whole class of aliasing bugs.
