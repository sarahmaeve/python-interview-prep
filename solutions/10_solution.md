# Solution: Exercise 10 -- Race Condition and Timing Bugs

## Bugs Found

### Bug 1: Wrong comparison operator in `get`

**Location:** `get`, line 29

The code uses `>=` to check expiry, which means an entry is considered expired at the exact moment it should still be valid.

**Diagnosis:** `test_get_at_exact_expiry_time_returns_value` sets TTL=10 at t=1000, then reads at t=1010. With `>=`, the entry is deleted. The test expects it to still be accessible.

**Before:**
```python
if time.time() >= expiry:
```

**After:**
```python
if time.time() > expiry:
```

**Why it matters:** Boundary conditions in time comparisons are a classic source of flaky behavior. The convention "expires *after* the boundary, not *at* it" should be documented and consistently applied.

---

### Bug 2: Mutating dict during iteration in `cleanup`

**Location:** `cleanup`, line 39

Iterating over `self._cache.keys()` and deleting entries raises `RuntimeError: dictionary changed size during iteration` in Python 3.

**Diagnosis:** `test_cleanup_does_not_raise_on_multiple_expired` inserts 10 entries, expires them all, then calls `cleanup()`. The test expects no exception.

**Before:**
```python
for key in self._cache.keys():
    if now > self._cache[key][1]:
        del self._cache[key]
```

**After:**
```python
for key in list(self._cache.keys()):
    if now > self._cache[key][1]:
        del self._cache[key]
```

**Why it matters:** In Python 3, `dict.keys()` returns a *view*, not a copy. Wrapping with `list()` materializes the keys first so deletion is safe. This is one of the most common Python 3 migration bugs.

---

### Bug 3: `size` counts expired entries

**Location:** `size`, line 47

Returns `len(self._cache)`, which includes entries whose TTL has passed but haven't been cleaned up yet.

**Diagnosis:** `test_size_counts_only_live_entries` sets 3 keys (one with TTL=5, two with TTL=20), advances time past the short TTL, and expects `size()` to return 2.

**Before:**
```python
def size(self):
    return len(self._cache)
```

**After:**
```python
def size(self):
    now = time.time()
    return sum(1 for _, (__, expiry) in self._cache.items() if now <= expiry)
```

**Why it matters:** Lazy expiration (only removing on access) is a valid strategy, but any method reporting cache state must account for it. Otherwise callers get a misleading view of the cache.

---

## Discussion

- **Mocking `time.time`:** The tests patch the entire `time` module at the `cache_with_expiry` level. This makes timing deterministic -- essential for avoiding flaky CI.
- **Eager vs. lazy expiration:** This cache uses lazy expiration (entries removed on `get` or `cleanup`). An alternative is a background thread or `heapq`-based priority queue that expires entries proactively.
- **Thread safety:** The current implementation is not thread-safe. In production, you'd protect `_cache` with a `threading.Lock` or use `cachetools.TTLCache`.
