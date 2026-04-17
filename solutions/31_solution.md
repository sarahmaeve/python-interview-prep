# Solution: Exercise 31 — Decorator `@wraps` and State

## Bugs Found

1. **`log_calls` forgets `@functools.wraps(func)`** on its `wrapper`. Decorated functions inherit `wrapper`'s identity — `__name__` becomes `"wrapper"`, `__doc__` is gone, `__wrapped__` is missing.

2. **`retry` decorates the wrong target.** `@functools.wraps(max_attempts)` is applied to the outer `decorator` function, with `max_attempts` (an int) as the target. `functools.wraps` silently skips attributes that don't exist on an int — so the net effect is "no wraps was applied, and `retry` itself is confusingly annotated with a numeric `__wrapped__`". Crucially, the *inner* `wrapper` that actually wraps `func` has no `@wraps` at all.

3. **`count_calls` stores `_count` as a class attribute.** Every instance — every decorated function — increments the same counter. "Per-function" counting doesn't happen.

## Diagnosis Process

- `test_name_is_preserved` fails with `greet.__name__ == "wrapper"`. Reading `log_calls`, the inner wrapper is missing `@functools.wraps(func)`.
- `test_preserves_function_name` under `@retry(3)` fails the same way. Looking at `retry`, the `@functools.wraps(max_attempts)` line stands out as applied at the wrong level AND to the wrong object — the inner wrapper needs `@functools.wraps(func)`, not the outer `decorator`.
- `test_each_function_has_its_own_counter` fails because `alpha.count` equals `4` (total for alpha + beta) instead of `3`. The counter is on the class, shared across instances.

## The Fix

### Bug 1 — `@functools.wraps(func)` on the inner wrapper

```python
def log_calls(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        logger.info("calling %s", func.__name__)
        try:
            result = func(*args, **kwargs)
        except Exception as exc:
            logger.info("%s raised %s", func.__name__, type(exc).__name__)
            raise
        logger.info("%s returned", func.__name__)
        return result
    return wrapper
```

### Bug 2 — `@wraps` belongs on the real wrapper

```python
def retry(max_attempts: int):
    def decorator(func):
        @functools.wraps(func)       # <-- correct target, correct level
        def wrapper(*args, **kwargs):
            last_exc: BaseException | None = None
            for _ in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except Exception as exc:
                    last_exc = exc
            assert last_exc is not None
            raise last_exc
        return wrapper
    return decorator
```

### Bug 3 — per-instance counter

```python
class count_calls:
    def __init__(self, func):
        functools.update_wrapper(self, func)
        self._func = func
        self._count = 0

    def __call__(self, *args, **kwargs):
        self._count += 1
        return self._func(*args, **kwargs)

    @property
    def count(self):
        return self._count
```

## Why This Bug Matters

### Bugs 1 and 2 — introspection breakage

`@functools.wraps` is the cheapest one-line fix in Python and the most consequential when it's missing:

- **`unittest.mock.patch`** uses attribute introspection. If your decorated function's `__module__` and `__qualname__` don't match the original, patching can fail silently or patch the wrong target.
- **Logging** messages that include `func.__name__` end up with `"wrapper"` everywhere, making log search useless.
- **Sphinx / pdoc** generate empty documentation because the `__doc__` attribute was replaced.
- **Stack traces** show `wrapper` instead of the real function name — harder to read, and tools like `sentry` group errors differently.

Bug 2 is especially insidious: `@functools.wraps(max_attempts)` doesn't raise. `update_wrapper` does `getattr(target, attr)` inside a try/except for each of `__module__`, `__name__`, `__qualname__`, `__doc__`, `__dict__`. An `int` has `__module__` (it's `"builtins"`) and `__doc__` (type-level), but not `__name__` or `__qualname__` — so the copy is partial. Worse, `__wrapped__` is set unconditionally to the target, so `retry.__wrapped__ == 3` after `retry(3)`. A debugger staring at that attribute would scratch its head.

### Bug 3 — class vs. instance attributes

This is the same family of bug as Guide 02 Section 2 (mutable class attributes). When you write:

```python
class count_calls:
    _count = 0   # class-level
```

Every subclass *and* every instance reads the same `_count` attribute. The first time an instance does `self._count += 1`, that's equivalent to `self._count = self._count + 1` — which CREATES an instance attribute that SHADOWS the class one. So the very first increment silently gives you per-instance state... until you use `type(self)._count +=` or `self.__class__._count += 1`, which is what the buggy code does explicitly.

The bug in this exercise uses `count_calls._count += 1` — the explicit class-level mutation. That's unambiguously shared state.

## Discussion

- **Every decorator should use `@functools.wraps`.** It's a one-line cost and prevents an entire class of bugs. Make it a reflex.
- **Parameterised decorators need three functions deep.** Outer captures the arguments, middle captures `func`, inner is the wrapper. `@wraps` goes on the innermost wrapper.
- **Class-based decorators use `functools.update_wrapper(self, func)`** instead of `@wraps` — same effect, different API.
- **`typing.ParamSpec`** (3.10+) lets you preserve the wrapped function's signature through the decorator, so mypy sees the decorated function with its original type. Worth adding to any production decorator library.
