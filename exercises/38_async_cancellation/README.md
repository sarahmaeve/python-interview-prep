# Exercise 38: Async Cancellation and Structured Concurrency

An asynchronous worker module fetches optional data, owns a client lifecycle,
and runs related jobs concurrently. Its success paths look reasonable, but
cancellation and sibling failure violate three lifecycle contracts.

**This exercise practices:** treating cancellation as control flow, guaranteeing
async cleanup, and using structured concurrency so child tasks cannot outlive
the operation that created them.

## How to run the tests

```bash
cd exercises/38_async_cancellation
python3 -m unittest test_async_lifecycle -v
```

Edit `async_lifecycle.py`; do not modify the tests. There are **3 bugs**.

## Cancellation model

Calling `Task.cancel()` requests cancellation. At the next cancellation point,
usually an `await`, the task receives `asyncio.CancelledError`. Cancellation is
not an ordinary business failure: it tells the coroutine to stop because its
owner no longer needs the work.

`CancelledError` directly subclasses `BaseException`, rather than `Exception`.
Broad `BaseException` handlers can therefore intercept cancellation along with
process-control exceptions such as `KeyboardInterrupt` and `SystemExit`.
Normally, cleanup belongs in `finally` and cancellation is allowed to continue
to the caller. Suppressing it deliberately requires considerably more care
than returning a fallback value.

## Cleanup is part of the contract

Any resource acquired before an `await` must be considered live while the task
is suspended. Cancellation can occur at that suspension point, so cleanup
written only after the successful result is not reliable. `try`/`finally` is
the basic ownership structure for both synchronous and asynchronous cleanup;
the `finally` block may itself `await` an async close operation.

## Structured concurrency

Related tasks should have a lexical owner. `asyncio.TaskGroup` is an async
context manager that waits for every child it creates. When one child raises a
non-cancellation exception, the group cancels and awaits its remaining
children, then raises the failures as an `ExceptionGroup`. This prevents
orphaned tasks from continuing after the parent operation has already failed.

By contrast, manually created tasks need explicit ownership on every exit
path. Merely awaiting them one by one does not automatically cancel the rest
when an earlier await raises.

If you get stuck, use [HINTS.md](HINTS.md).

## Official Python documentation

- [Task cancellation](https://docs.python.org/3/library/asyncio-task.html#task-cancellation)
- [`asyncio.TaskGroup`](https://docs.python.org/3/library/asyncio-task.html#task-groups)
- [`ExceptionGroup`](https://docs.python.org/3/library/exceptions.html#ExceptionGroup)
- [Asynchronous context managers](https://docs.python.org/3/reference/datamodel.html#asynchronous-context-managers)
