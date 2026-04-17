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

## Hints

<details>
<summary>Hint 1 (gentle)</summary>

Every bug is the same shape: a cleanup path that runs only on the *happy path* but gets skipped when something raises. Walk through each resource's lifecycle under two scenarios (clean exit, raised exception) and note which cleanup actions run in each.

</details>

<details>
<summary>Hint 2 (moderate)</summary>

1. `ConnectionPool.__exit__` only closes the connection when there was no exception. Why?
2. `transaction` calls `commit()` unconditionally — but what about the rollback path?
3. `run_queries` doesn't use `with pool`.

</details>

<details>
<summary>Hint 3 (specific)</summary>

1. In `ConnectionPool.__exit__`, drop the `if exc_type is None:` guard — the connection must close on every exit. Keep `return False` so the exception still propagates.
2. In `transaction`, wrap `yield` in try/except/else:
    ```python
    db.begin()
    try:
        yield db
    except Exception:
        db.rollback()
        raise
    else:
        db.commit()
    ```
3. In `run_queries`, use the pool as a context manager:
    ```python
    with pool as conn:
        return [conn.execute(q) for q in queries]
    ```

</details>

## Why this matters

In production:
- An HTTP connection leak eats file descriptors until the process OOMs or the OS refuses new sockets.
- A DB transaction never committed or rolled back holds row locks and leaks backend memory.
- A connection leased but never returned exhausts the pool and subsequent requests hang waiting for a free slot.

Each of the fixes is a one- or two-line change. The discipline of "wrap yield in try/finally" and "always use `with`" is habit-forming, which is the whole point of this exercise.

## Relevant reading

- `guides/11_context_and_decorators.py` — Sections 1–4 (context manager protocol, `@contextmanager`, `ExitStack`, `suppress`)
