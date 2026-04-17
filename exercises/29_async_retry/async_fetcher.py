"""Async fetcher with retry and timeout — contains 3 async-specific bugs.

An async HTTP client that wraps a lower-level client with:
  - Retry on transient errors
  - Per-attempt timeout
  - Tracking of attempt counts for observability

Your job:
  - Find and fix 3 bugs.
  - All tests must pass without modification.

Relevant reading:
  - guides/12_async_and_testing.py (the whole guide)
  - guides/05_mocking_and_external_deps.py Section 10b (AsyncMock)
"""

from __future__ import annotations

import asyncio
import time
from typing import Any, Protocol


class AsyncHttpClient(Protocol):
    """The shape of the lower-level HTTP client we depend on."""

    async def get(self, url: str) -> dict: ...


class TransientError(Exception):
    """A failure we should retry."""


class PermanentError(Exception):
    """A failure we should NOT retry (4xx-style)."""


class AsyncFetcher:
    """Fetches JSON with retry-on-transient and a per-attempt timeout.

    Semantics:
      - On TransientError, retry up to *max_attempts* total attempts,
        with linear backoff of *backoff_seconds* between attempts.
      - On PermanentError, raise immediately (no retry).
      - On timeout within an attempt, treat it as a TransientError.
      - Each completed attempt increments `attempt_count`.
    """

    def __init__(self, client: AsyncHttpClient, *,
                 max_attempts: int = 3,
                 per_attempt_timeout: float = 5.0,
                 backoff_seconds: float = 0.1) -> None:
        self.client = client
        self.max_attempts = max_attempts
        self.per_attempt_timeout = per_attempt_timeout
        self.backoff_seconds = backoff_seconds
        self.attempt_count = 0

    async def fetch(self, url: str) -> dict:
        last_transient: Exception | None = None

        for attempt in range(1, self.max_attempts):
            self.attempt_count += 1
            try:
                async with asyncio.timeout(self.per_attempt_timeout):
                    return self.client.get(url)
            except PermanentError:
                raise
            except (TransientError, TimeoutError) as exc:
                last_transient = exc
                if attempt < self.max_attempts:
                    time.sleep(self.backoff_seconds)

        assert last_transient is not None
        raise last_transient


async def fetch_all(fetcher: AsyncFetcher, urls: list[str]) -> list[Any]:
    """Fetch every URL concurrently; return results in input order."""
    tasks = [fetcher.fetch(u) for u in urls]
    return await asyncio.gather(*tasks)
