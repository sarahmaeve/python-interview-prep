# Solution: Exercise 29 — Async Retry Client

## Bugs Found

1. **`return self.client.get(url)` is missing `await`.** `client.get` is an async method; calling it returns a coroutine, not the awaited value. The function returns the coroutine object itself.

2. **`range(1, self.max_attempts)` is off by one.** With `max_attempts=3`, this iterates through attempts 1 and 2 only — two attempts, not three.

3. **`time.sleep(self.backoff_seconds)` blocks the event loop.** During the sleep, NO other asyncio task can run. Concurrent fetches under `asyncio.gather` serialise instead of running in parallel.

## Diagnosis Process

- `test_success_on_first_attempt` fails because the return value is a `coroutine`, not `{"ok": True}`. The test message specifically calls out the forgotten `await`.
- `test_retries_on_transient_then_succeeds` fails because `attempt_count` is `2`, not `3`. Walking the `range` call by hand: `range(1, 3)` yields `[1, 2]`.
- `test_concurrent_fetches_run_in_parallel` fails with an elapsed time close to 2× the backoff, revealing `time.sleep`. This is the bug pattern I've seen cause a 30× slowdown in production async HTTP clients.

## The Fix

```python
async def fetch(self, url: str) -> dict:
    last_transient: Exception | None = None

    for attempt in range(1, self.max_attempts + 1):
        self.attempt_count += 1
        try:
            async with asyncio.timeout(self.per_attempt_timeout):
                return await self.client.get(url)
        except PermanentError:
            raise
        except (TransientError, TimeoutError) as exc:
            last_transient = exc
            if attempt < self.max_attempts:
                await asyncio.sleep(self.backoff_seconds)

    assert last_transient is not None
    raise last_transient
```

## Why This Bug Matters

### Bug 1 — Forgotten `await`

This is *the* most common async mistake. Without `await`:

- The coroutine is never driven — the function body inside `client.get` never runs.
- Python prints `RuntimeWarning: coroutine '...' was never awaited` when the coroutine is garbage-collected.
- The calling code receives a coroutine object, tries to use it as a dict, and gets `TypeError: 'coroutine' object is not subscriptable` — at which point the cause is several call frames away from the effect.

The fix is a single keyword. Tooling helps: mypy warns when a coroutine is used as if it were the return value; `-W error::RuntimeWarning` turns the runtime warning into a hard error in tests.

### Bug 2 — Off-by-one in the retry loop

`range(1, n)` is a classic off-by-one. For counted retries, write the condition the way it reads in English:

> "For attempts 1 through max_attempts inclusive..."

= `for attempt in range(1, max_attempts + 1):`

Or just iterate by zero-based index and rename:

= `for attempt in range(max_attempts):` and use `attempt + 1` for display.

### Bug 3 — `time.sleep` in async code

`time.sleep(N)` blocks the calling thread for N seconds. In a threaded webserver, it blocks ONE thread. In an async event loop, it blocks *every concurrent task on that loop* — which is catastrophic for a service handling hundreds of requests.

The diagnostic is the concurrency test: two fetches under `asyncio.gather` should parallelise. If they don't, someone's blocking the loop.

Common places this bug sneaks in:
- `time.sleep()` in a helper used across sync and async code.
- Synchronous DB drivers (`psycopg2.connect` etc.) inside `async def` — same issue at a bigger scale.
- CPU-bound work (long loops, JSON parsing of large payloads) — technically not "blocking" but starves the loop just the same. The fix is `asyncio.to_thread(...)`.

## Discussion — asyncio.timeout vs. wait_for

We used `asyncio.timeout(N)` (the context-manager form, 3.11+) instead of the older `asyncio.wait_for(coro, timeout=N)`. They're roughly equivalent, but `timeout` has cleaner semantics in a few cases:

- `timeout` cancels the body and re-raises `TimeoutError`. `wait_for` does the same but has historically had some edge-case issues with cancellation during shutdown.
- `timeout` composes naturally with other `async with` blocks — no need to wrap your code in another function just to pass it to `wait_for`.

For `max_attempts=1` (no retries), the retry loop still runs once. That's intentional: you still get the observability of `attempt_count` and the `try/except` shape. If you want a "retry=off" flag, set `max_attempts=1` and the loop behaves like a single attempt with timeout.

## Interview talking points

- "Why is `asyncio.gather` returning a list of coroutines?" — because someone forgot `await` inside `fetch`. That's bug 1 surfacing at a different layer.
- "Our async service is slow. What do you check first?" — `time.sleep` and synchronous DB calls. Grep for those in the async code paths.
- "How do you test that retries happen the right number of times?" — assert on `AsyncMock.await_count` and the instance's own counter. Mock out `asyncio.sleep` if the backoff delays slow the test suite.
