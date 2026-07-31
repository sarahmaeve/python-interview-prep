# Solution: Exercise 38 — Async Cancellation and Structured Concurrency

## Bugs Found

1. `fetch_optional` catches `BaseException`, so it converts task cancellation
   into an ordinary `None` result.
2. `fetch_and_close` closes its client only after a successful fetch;
   cancellation or failure skips cleanup.
3. `run_batch` creates unowned tasks and awaits them sequentially. When one
   raises, siblings remain alive and the caller receives the original exception
   rather than the structured group's `ExceptionGroup`.

## Repairs

Catch only ordinary failures in the optional operation:

```python
async def fetch_optional(client, resource):
    try:
        return await client.fetch(resource)
    except Exception:
        return None
```

`asyncio.CancelledError` inherits directly from `BaseException`, so it passes
through this handler. A production implementation would usually catch a still
narrower tuple of expected client exceptions.

Put cleanup in a `finally` block:

```python
async def fetch_and_close(client, resource):
    try:
        return await client.fetch(resource)
    finally:
        await client.close()
```

The pending cancellation is re-raised after `finally` completes unless the
cleanup itself raises. Real systems should decide how to report a cleanup
failure that competes with an existing exception.

Give the batch a structured lifetime:

```python
async def run_batch(fetcher, resources):
    tasks = []
    async with asyncio.TaskGroup() as group:
        for resource in resources:
            tasks.append(group.create_task(fetcher(resource)))
    return [task.result() for task in tasks]
```

If a child fails, `TaskGroup` cancels and awaits the others. After all children
finish cleanup, it raises an `ExceptionGroup`. When every child succeeds, task
results remain available in creation order.

## Why This Matters

Cancellation is how timeouts, request disconnects, service shutdown, and
structured concurrency reclaim unwanted work. Swallowing it can make a timeout
look successful, leak resources, or prevent a task group from completing.

Manual `create_task()` remains appropriate for genuinely independent
background work, but that work needs an explicit owner, retained references,
error reporting, and a shutdown policy. Related request-scoped tasks belong in
a task group.

## Official documentation

- [Task cancellation](https://docs.python.org/3/library/asyncio-task.html#task-cancellation)
- [`asyncio.TaskGroup`](https://docs.python.org/3/library/asyncio-task.html#task-groups)
- [`ExceptionGroup`](https://docs.python.org/3/library/exceptions.html#ExceptionGroup)
