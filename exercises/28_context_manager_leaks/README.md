# Exercise 28: Context Manager Leaks

Three small resource-management utilities, each with a subtle leak. The implementation has **3 bugs**, all of the same family: context-manager discipline.

## How to run the tests

```bash
cd exercises/28_context_manager_leaks
python3 -m unittest test_resource_manager
```

Your goal is to edit `resource_manager.py` until all tests pass. Do **not** modify the test file.

## What's inside

- `ConnectionPool` — class-based context manager; leases a connection.
- `transaction(db)` — `@contextmanager`-decorated generator; commits on success, rolls back on error.
- `run_queries(pool, queries)` — helper that uses a pool to run several queries.

## Principle Primer

A context manager defines paired lifecycle actions across both normal and
exceptional exits. For a class-based manager, `__exit__` receives the exception
state and decides both cleanup and suppression. For a generator-based manager,
an exception from the `with` body is raised at the suspended `yield`, allowing
the manager to roll back and re-raise.

If you get stuck, use [HINTS.md](HINTS.md).

## Why this matters

In production:
- An HTTP connection leak eats file descriptors until the process OOMs or the OS refuses new sockets.
- A DB transaction never committed or rolled back holds row locks and leaks backend memory.
- A connection leased but never returned exhausts the pool and subsequent requests hang waiting for a free slot.

The habit to build is tracing both lifecycle paths—success and failure—before
calling resource management complete.

## Relevant reading

- `guides/11_context_and_decorators.py` — Sections 1–4 (context manager protocol, `@contextmanager`, `ExitStack`, `suppress`)
