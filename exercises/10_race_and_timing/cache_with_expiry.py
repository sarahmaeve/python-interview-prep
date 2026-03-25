"""
TimedCache -- a key-value cache where entries expire after a TTL.

This module contains 3 bugs. Run the tests to find them:

    python3 -m unittest test_cache_with_expiry

Fix the bugs until all tests pass. Do not modify the test file.
"""

import time


class TimedCache:
    def __init__(self):
        self._cache = {}  # key -> (value, expiry_timestamp)

    def set(self, key, value, ttl=60):
        """Store *value* under *key*, expiring after *ttl* seconds."""
        self._cache[key] = (value, time.time() + ttl)

    def get(self, key):
        """Return the value for *key* if it exists and has not expired."""
        if key not in self._cache:
            raise KeyError(key)
        value, expiry = self._cache[key]
        # BUG 1: should be `>` not `>=` -- at exactly expiry time the entry
        # should still be accessible.
        if time.time() >= expiry:
            del self._cache[key]
            raise KeyError(key)
        return value

    def cleanup(self):
        """Remove all expired entries from the cache."""
        now = time.time()
        # BUG 2: modifying dict while iterating over .keys() raises RuntimeError
        # in Python 3.  Should use list(self._cache.keys()).
        for key in self._cache.keys():
            if now > self._cache[key][1]:
                del self._cache[key]

    def size(self):
        """Return the number of non-expired entries."""
        # BUG 3: counts expired-but-not-cleaned entries.  Should filter by
        # expiry time.
        return len(self._cache)
