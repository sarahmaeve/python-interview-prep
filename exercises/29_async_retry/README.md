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

## Principle Primer

Calling an async function produces a coroutine; its result appears only when it
is awaited. Concurrency on one event loop is cooperative, so waiting code must
suspend through an async primitive rather than block the thread. Retry
semantics should state total attempts explicitly and make loop boundaries match
that definition.

If you get stuck, use [HINTS.md](HINTS.md).

## Why the concurrent test matters

The concurrency test checks more than the final value: it proves that one
task's waiting period does not prevent another task from progressing. In a
production batch, blocking the event-loop thread can serialize work that was
intended to overlap.

## Relevant reading

- `guides/12_async_and_testing.py` — the whole guide
- `guides/05_mocking_and_external_deps.py` — Section 10b (AsyncMock)
