# Exercise 24: Rate-Limited API Client

## Prerequisites

Read guide `05` (Mocking and External Dependencies) before starting. Understanding dependency injection and `unittest.mock` is essential.

## Problem

Build an `ApiClient` that enforces a rate limit and retries transient failures.

This exercise practices: **dependency injection, mocking, rate limiting, retry logic**.

**Target time: ~15 minutes.**

## Your Task

1. Read every docstring in `api_client.py` carefully — they define the contract.
2. Implement `ApiClient.__init__`, `request`, and `requests_remaining` in `api_client.py`.
3. Open `test_api_client.py` and implement each of the 7 test stubs. The comment inside each stub tells you exactly what to set up and assert.
4. Run the tests:

```bash
python3 -m unittest test_api_client -v
```

All tests pass trivially (all `pass`) before you begin — that is intentional. They should pass for real once both files are fully implemented.

## Design Notes

**Dependency injection** is the key pattern here. `ApiClient` never calls `time.time()` directly — it receives a `clock` callable in `__init__`. This makes the clock controllable in tests: you can freeze time or jump forward by 61 seconds without actually waiting.

The same applies to the `transport`: rather than making real HTTP calls, tests pass a `MagicMock` whose `.request()` return value and side effects you control completely.

## Constraints

- Never call `time.time()` or `time.sleep()` directly inside `ApiClient`
- Rate limit uses a fixed window: track the timestamp of the first request in the current window
- Retry on any exception raised by the transport; do not sleep between retries
- No external libraries

## Hints (try without these first)

<details>
<summary>Hint — rate limit window</summary>
Store the timestamp when the current window started. In <code>request</code>, check whether <code>clock() - window_start >= window_seconds</code>; if so, reset the window and the request count. If the count is already at <code>max_requests</code>, raise <code>RateLimitExceeded</code>.
</details>

<details>
<summary>Hint — retry loop</summary>
Use a loop that runs at most <code>1 + max_retries</code> times. Catch exceptions from <code>transport.request</code>. On the last attempt, re-raise. On earlier attempts, continue the loop.
</details>
