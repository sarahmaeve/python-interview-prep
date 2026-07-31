# Exercise 10: Cache Expiry and Timing

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

## Principle Primer

Time-based behavior needs an explicit boundary contract: decide whether the
exact deadline is still valid, then apply that rule consistently. Stored state
and observable state may differ when expired entries remain physically present.
When removing dictionary entries, iterate over a stable snapshot rather than a
live view that changes beneath the loop.

If you get stuck, use [HINTS.md](HINTS.md).
