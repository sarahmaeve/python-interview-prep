# Solution: Exercise 28 — Context Manager Leaks

## Bugs Found

1. **`ConnectionPool.__exit__` only closes on clean exit.** The `if exc_type is None:` guard means an exception inside the `with` block leaves the connection open.

2. **`transaction` has no try/except/finally around `yield`.** A raise inside the block skips both `commit` and `rollback`, leaving `open_transactions` off by one.

3. **`run_queries` uses `pool.__enter__()` directly without a matching `__exit__`.** The pool is never cleaned up — the connection leaks for every call.

## Diagnosis Process

- `test_closes_on_exception` fails because `conn.closed` is still `False` after an exception. Reading `__exit__`, the `close()` call is gated on the no-exception path.
- `test_rollback_on_exception` fails with `commits=0, rollbacks=0` — neither path ran because the exception escapes before `db.commit()` and there's no `except` to run `rollback()`.
- `test_uses_the_context_manager_protocol` fails with `pool.conn.closed == False`. `run_queries` calls `__enter__` but never `__exit__`. The fix is to use `with pool as conn:` which handles both ends automatically.

## The Fix

### Bug 1 — `__exit__` must close unconditionally

```python
def __exit__(self, exc_type, exc_val, exc_tb) -> bool:
    if self.conn is not None:
        self.conn.close()
    return False   # propagate any exception
```

Return `False` (or `None`) so the caller still sees the exception; return `True` only if you deliberately want to swallow it.

### Bug 2 — `transaction` needs try/except/else

```python
@contextmanager
def transaction(db: FakeDatabase):
    db.begin()
    try:
        yield db
    except Exception:
        db.rollback()
        raise
    else:
        db.commit()
```

The three branches cover every outcome: `try:yield` for the happy path, `except` for the error path (rollback then re-raise), `else` runs after the happy path only (commit).

### Bug 3 — `run_queries` must use `with`

```python
def run_queries(pool: ConnectionPool, queries: list[str]) -> list[Any]:
    with pool as conn:
        return [conn.execute(q) for q in queries]
```

## Why This Bug Matters

These three bugs are different faces of the same mistake: *cleanup code that runs only on the happy path.* In production:

- **Leaked connections** pile up until the server refuses new ones. Your app looks like it's "slow" but it's really blocked on a saturated pool.
- **Missing rollback** means stuck transactions — row locks held, write-ahead log growing, backend memory filling. The only fix is usually a manual `KILL` on the backend session.
- **No `__exit__` call** means the context manager's entire point — "cleanup runs regardless" — is discarded. If you find yourself calling `__enter__` manually, use `with` or `contextlib.ExitStack`.

## Discussion

- `contextlib.ExitStack` is the right tool for dynamic cases where you can't statically nest `with` blocks (e.g., opening N files at runtime). Guide 11 Section 4 shows the pattern.
- For class-based context managers, remember that `__exit__`'s return value controls exception propagation: `False`/`None` propagates, `True` suppresses. Suppression is almost always wrong — only use it when you legitimately want the context to eat a specific exception type (like `contextlib.suppress`).
- The `@contextmanager` generator form is more concise for stateless cases. The class form is better when the context carries mutable state or has subclass hooks. Choose per situation, not per dogma.
- When testing context managers, run your tests under the *exception path* explicitly. A test suite that only covers happy-path cleanup misses 99% of leak bugs.
