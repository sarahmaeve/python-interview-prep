# Exercise 29: Async Retry Client

An async HTTP fetcher with retry-on-transient, per-attempt timeout, and attempt tracking. The implementation has **3 bugs** — all are classic async mistakes that also happen to cause the concurrent test case to misbehave subtly.

## How to run the tests

```bash
cd exercises/29_async_retry
python3 -m unittest test_async_fetcher
```

Your goal is to edit `async_fetcher.py` until all tests pass. Do **not** modify the test file.

## Semantics

- On `TransientError`, retry up to `max_attempts` total attempts with a linear backoff between attempts.
- On `PermanentError`, raise immediately (no retry).
- On per-attempt timeout, treat as a `TransientError`.
- `attempt_count` increments on every attempt.

## Hints

<details>
<summary>Hint 1 (gentle)</summary>

Three of the most common async bugs:
1. Forgetting to `await` a coroutine (it returns the coroutine object itself).
2. Off-by-one in the retry loop — think carefully about `range(1, max_attempts)` vs `range(1, max_attempts + 1)`.
3. Using `time.sleep()` inside an async function — that blocks the event loop.

One of the tests specifically measures concurrent wall time to catch the `time.sleep` bug.

</details>

<details>
<summary>Hint 2 (moderate)</summary>

1. `fetch` has `return self.client.get(url)` — but `client.get` is async. That expression is a coroutine, not the value.
2. `for attempt in range(1, self.max_attempts):` — with `max_attempts=3` this iterates twice, not three times.
3. `time.sleep(self.backoff_seconds)` blocks everything else on the event loop during the wait.

</details>

<details>
<summary>Hint 3 (specific)</summary>

1. `return await self.client.get(url)`
2. `for attempt in range(1, self.max_attempts + 1):`
3. `await asyncio.sleep(self.backoff_seconds)`

</details>

## Why the concurrent test matters

The `test_concurrent_fetches_run_in_parallel` test would pass if bug 3 were only about correctness, because a single fetch with `time.sleep` still returns the right value. But two fetches running under `asyncio.gather` with `time.sleep` in their backoff can't actually run in parallel — `time.sleep` blocks the *entire event loop*, so the second fetch's backoff is serialised behind the first. This is the exact bug pattern that caused a half-hour incident at `$real_company` because a 30-request batch was taking 30× the expected time.

## Relevant reading

- `guides/12_async_and_testing.py` — the whole guide
- `guides/05_mocking_and_external_deps.py` — Section 10b (AsyncMock)
