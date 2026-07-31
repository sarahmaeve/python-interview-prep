# Hints: Exercise 38 — Async Cancellation

## Hint 1

For every `await`, trace what the function owns and what its caller should
observe if cancellation arrives at that exact point.

## Hint 2

Inspect the breadth of the optional-fetch exception handler, the path from
fetch to close, and what happens to later batch tasks when an earlier await
raises.

## Hint 3

- Catch ordinary `Exception` in `fetch_optional`, not `BaseException`.
- Put `client.close()` in a `finally` block in `fetch_and_close`.
- Create batch tasks through `asyncio.TaskGroup` and read their results only
  after the group exits.

The complete walkthrough is in
[solutions/38_solution.md](../../solutions/38_solution.md).
