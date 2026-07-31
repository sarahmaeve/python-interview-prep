# Hints: Exercise 29 — Async Retry

## Hint 1

Inspect every async call, retry-loop endpoint, and waiting primitive.

## Hint 2

One coroutine is returned rather than awaited, the loop provides too few total
attempts, and the backoff blocks the event-loop thread.

## Hint 3

Await `client.get`, include `max_attempts` in the loop range, and await
`asyncio.sleep` for backoff.

The complete walkthrough is in
[solutions/29_solution.md](../../solutions/29_solution.md).
