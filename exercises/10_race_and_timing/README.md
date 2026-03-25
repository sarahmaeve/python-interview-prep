# Exercise 10: Race Conditions and Timing

A key-value cache where each entry has a time-to-live (TTL). The implementation has **3 bugs** related to time-dependent behavior for you to find and fix.

The test file uses `unittest.mock.patch("time.time")` to control the clock, making the tests deterministic. This is the standard pattern for testing any code that depends on the current time.

## How to run the tests

```bash
cd exercises/10_race_and_timing
python3 -m unittest test_cache_with_expiry
```

Your goal is to edit `cache_with_expiry.py` until all tests pass. Do **not** modify the test file.

## Class: TimedCache

- `__init__(self)` -- creates an empty cache.
- `set(self, key, value, ttl=60)` -- stores a value that expires after `ttl` seconds.
- `get(self, key)` -- returns the value if the key exists and has not expired; raises `KeyError` otherwise.
- `cleanup(self)` -- removes all expired entries from the cache.
- `size(self)` -- returns the number of non-expired entries currently in the cache.

## Hints

<details>
<summary>Hint 1 (gentle)</summary>
Think about boundary conditions. What happens at the exact moment an entry expires?
</details>

<details>
<summary>Hint 2 (moderate)</summary>
One method modifies a dictionary while iterating over it. Another method takes a shortcut that gives a wrong answer.
</details>

<details>
<summary>Hint 3 (specific)</summary>

1. `get` uses `>=` when checking expiry, so an item fetched at exactly its expiry time is wrongly considered expired. It should use `>`.
2. `cleanup` iterates over `self._cache.keys()` and deletes entries during iteration, which raises a `RuntimeError` in Python 3. Use `list(self._cache.keys())`.
3. `size` returns `len(self._cache)`, which counts expired-but-not-yet-cleaned entries. It should count only entries whose expiry is in the future.

</details>
