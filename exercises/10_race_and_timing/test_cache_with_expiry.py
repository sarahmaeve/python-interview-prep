"""
Correct tests for TimedCache.

These tests mock time.time() so every assertion is deterministic.
Study how the mock clock is advanced to simulate the passage of time.
"""

import unittest
from unittest.mock import patch

from cache_with_expiry import TimedCache


class TestTimedCacheSet(unittest.TestCase):
    """Tests for basic set / get behaviour."""

    @patch("cache_with_expiry.time")
    def test_set_and_get_basic(self, mock_time):
        mock_time.time.return_value = 1000.0
        cache = TimedCache()
        cache.set("color", "blue", ttl=60)
        mock_time.time.return_value = 1030.0  # 30 s later, well within TTL
        self.assertEqual(cache.get("color"), "blue")

    @patch("cache_with_expiry.time")
    def test_get_missing_key_raises(self, mock_time):
        mock_time.time.return_value = 1000.0
        cache = TimedCache()
        with self.assertRaises(KeyError):
            cache.get("nonexistent")

    @patch("cache_with_expiry.time")
    def test_get_expired_key_raises(self, mock_time):
        mock_time.time.return_value = 1000.0
        cache = TimedCache()
        cache.set("token", "abc", ttl=10)
        mock_time.time.return_value = 1011.0  # 11 s later, past TTL
        with self.assertRaises(KeyError):
            cache.get("token")


class TestTimedCacheBoundary(unittest.TestCase):
    """Edge-case test for the exact expiry moment."""

    @patch("cache_with_expiry.time")
    def test_get_at_exact_expiry_time_returns_value(self, mock_time):
        """An entry with TTL=10 set at t=1000 expires AFTER t=1010, not AT t=1010.

        At t=1010 the entry should still be accessible.
        """
        mock_time.time.return_value = 1000.0
        cache = TimedCache()
        cache.set("session", "xyz", ttl=10)
        mock_time.time.return_value = 1010.0  # exactly at expiry boundary
        self.assertEqual(cache.get("session"), "xyz")


class TestTimedCacheCleanup(unittest.TestCase):
    """Tests for cleanup()."""

    @patch("cache_with_expiry.time")
    def test_cleanup_removes_expired_entries(self, mock_time):
        mock_time.time.return_value = 1000.0
        cache = TimedCache()
        cache.set("a", 1, ttl=5)
        cache.set("b", 2, ttl=20)
        mock_time.time.return_value = 1006.0  # "a" expired, "b" alive
        cache.cleanup()
        with self.assertRaises(KeyError):
            cache.get("a")
        self.assertEqual(cache.get("b"), 2)

    @patch("cache_with_expiry.time")
    def test_cleanup_does_not_raise_on_multiple_expired(self, mock_time):
        """Cleaning up several expired entries must not raise RuntimeError."""
        mock_time.time.return_value = 1000.0
        cache = TimedCache()
        for i in range(10):
            cache.set(f"key_{i}", i, ttl=5)
        mock_time.time.return_value = 1006.0  # all expired
        # This must not raise (e.g. RuntimeError from dict mutation during iteration)
        cache.cleanup()

    @patch("cache_with_expiry.time")
    def test_cleanup_on_empty_cache(self, mock_time):
        mock_time.time.return_value = 1000.0
        cache = TimedCache()
        cache.cleanup()  # should not raise


class TestTimedCacheSize(unittest.TestCase):
    """Tests for size()."""

    @patch("cache_with_expiry.time")
    def test_size_counts_only_live_entries(self, mock_time):
        mock_time.time.return_value = 1000.0
        cache = TimedCache()
        cache.set("a", 1, ttl=5)
        cache.set("b", 2, ttl=20)
        cache.set("c", 3, ttl=20)
        mock_time.time.return_value = 1006.0  # "a" expired
        self.assertEqual(cache.size(), 2)

    @patch("cache_with_expiry.time")
    def test_size_is_zero_when_all_expired(self, mock_time):
        mock_time.time.return_value = 1000.0
        cache = TimedCache()
        cache.set("x", 1, ttl=5)
        cache.set("y", 2, ttl=5)
        mock_time.time.return_value = 1006.0
        self.assertEqual(cache.size(), 0)

    @patch("cache_with_expiry.time")
    def test_size_of_empty_cache(self, mock_time):
        mock_time.time.return_value = 1000.0
        cache = TimedCache()
        self.assertEqual(cache.size(), 0)


if __name__ == "__main__":
    unittest.main()
