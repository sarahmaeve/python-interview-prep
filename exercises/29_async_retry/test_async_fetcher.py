"""Tests for the async fetcher.

Do NOT modify this file.  Fix the bugs in async_fetcher.py until every
test passes.
"""

import asyncio
import time
import unittest
from unittest.mock import AsyncMock, patch

from async_fetcher import (
    AsyncFetcher,
    PermanentError,
    TransientError,
    fetch_all,
)


class TestAsyncFetcher(unittest.IsolatedAsyncioTestCase):

    async def test_success_on_first_attempt(self):
        client = AsyncMock()
        client.get.return_value = {"ok": True}
        fetcher = AsyncFetcher(client)

        result = await fetcher.fetch("https://example.com/a")

        self.assertEqual(
            result, {"ok": True},
            "fetch() must return the awaited value — not a coroutine. "
            "If you see `<coroutine object ...>` here, the implementation "
            "forgot to `await` the client call.",
        )
        self.assertEqual(fetcher.attempt_count, 1)
        client.get.assert_awaited_once_with("https://example.com/a")

    async def test_retries_on_transient_then_succeeds(self):
        client = AsyncMock()
        # First two calls fail transiently, third succeeds.
        client.get.side_effect = [
            TransientError("temporary glitch"),
            TransientError("still glitching"),
            {"ok": True},
        ]
        fetcher = AsyncFetcher(client, max_attempts=3, backoff_seconds=0.001)

        result = await fetcher.fetch("/retry")

        self.assertEqual(result, {"ok": True})
        self.assertEqual(
            fetcher.attempt_count, 3,
            "with max_attempts=3 and two transient failures, the fetcher "
            "must make all 3 attempts — check the retry loop's range() call",
        )
        self.assertEqual(client.get.await_count, 3)

    async def test_exhausts_all_attempts_then_raises_last_transient(self):
        client = AsyncMock()
        err1 = TransientError("first")
        err2 = TransientError("second")
        err3 = TransientError("third")
        client.get.side_effect = [err1, err2, err3]
        fetcher = AsyncFetcher(client, max_attempts=3, backoff_seconds=0.001)

        with self.assertRaises(TransientError) as ctx:
            await fetcher.fetch("/always-fails")

        self.assertIs(ctx.exception, err3,
                      "the LAST transient exception must propagate")
        self.assertEqual(fetcher.attempt_count, 3)

    async def test_permanent_error_is_not_retried(self):
        client = AsyncMock()
        client.get.side_effect = PermanentError("400 Bad Request")
        fetcher = AsyncFetcher(client, max_attempts=5)

        with self.assertRaises(PermanentError):
            await fetcher.fetch("/bad")

        self.assertEqual(fetcher.attempt_count, 1,
                         "PermanentError must raise immediately, no retries")
        self.assertEqual(client.get.await_count, 1)

    async def test_timeout_is_treated_as_transient(self):
        """If a single attempt exceeds per_attempt_timeout, we should
        treat it as transient and retry."""

        async def slow_then_fast(url):
            # First call hangs past the timeout; the asyncio.timeout
            # context wakes up with TimeoutError.
            if slow_then_fast.calls == 0:
                slow_then_fast.calls += 1
                await asyncio.sleep(1.0)  # will be cancelled by timeout
                return {"unreachable": True}
            slow_then_fast.calls += 1
            return {"ok": True}

        slow_then_fast.calls = 0
        client = AsyncMock()
        client.get.side_effect = slow_then_fast

        fetcher = AsyncFetcher(client, max_attempts=2,
                               per_attempt_timeout=0.02,
                               backoff_seconds=0.001)

        result = await fetcher.fetch("/slow")
        self.assertEqual(result, {"ok": True})
        self.assertEqual(fetcher.attempt_count, 2)


class TestBackoffUsesAsyncSleep(unittest.IsolatedAsyncioTestCase):
    """The backoff must not block the event loop.

    time.sleep() BLOCKS the loop — other concurrent tasks cannot run
    during the sleep.  asyncio.sleep() yields to the loop instead.
    """

    async def test_concurrent_fetches_run_in_parallel(self):
        """If two fetches run concurrently and both take one retry, the
        total wall time should be close to `backoff` — not 2*backoff —
        because asyncio.sleep() lets the other task proceed during the
        wait.  With time.sleep(), each sleep blocks serially.
        """
        call_count = {"a": 0, "b": 0}

        async def flaky_get(url):
            key = url.strip("/")
            call_count[key] += 1
            if call_count[key] == 1:
                raise TransientError(f"fail {url}")
            return {"url": url}

        client = AsyncMock()
        client.get.side_effect = flaky_get

        fetcher_a = AsyncFetcher(client, max_attempts=2, backoff_seconds=0.10)
        fetcher_b = AsyncFetcher(client, max_attempts=2, backoff_seconds=0.10)

        start = time.perf_counter()
        await asyncio.gather(fetcher_a.fetch("/a"), fetcher_b.fetch("/b"))
        elapsed = time.perf_counter() - start

        # If backoff used time.sleep, elapsed ~= 0.20s (serialised).
        # With asyncio.sleep it's ~= 0.10s (concurrent).
        # Pick 0.17 as a generous upper bound — asyncio's overhead
        # shouldn't push a 0.10 sleep above that.
        self.assertLess(
            elapsed, 0.17,
            f"concurrent fetches with retries took {elapsed:.3f}s; "
            "likely the backoff uses time.sleep() (blocking) instead of "
            "await asyncio.sleep() (non-blocking).",
        )


class TestFetchAll(unittest.IsolatedAsyncioTestCase):
    async def test_results_in_input_order(self):
        client = AsyncMock()
        client.get.side_effect = lambda url: {"url": url}
        fetcher = AsyncFetcher(client)

        urls = ["/a", "/b", "/c"]
        results = await fetch_all(fetcher, urls)
        self.assertEqual([r["url"] for r in results], urls)


if __name__ == "__main__":
    unittest.main()
