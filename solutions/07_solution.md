# Solution: Exercise 07 — Exception Handling (Config Parser)

## Bugs Found

1. **`load_config`** — A bare `except: pass` catches every exception, including `KeyboardInterrupt` and `SystemExit`. The test `test_load_config_does_not_swallow_keyboard_interrupt` uses a `BadDict` whose `items()` raises `KeyboardInterrupt` and expects it to propagate.

2. **`get_int`** — Catches `ValueError` but re-raises it as a generic `Exception("")` with an empty message. The test expects a `ValueError` whose message contains both the key name and the bad value.

3. **`validate`** — Catches `TypeError` (from iterating `None`) and silently returns. The test `test_validate_raises_type_error_for_none` expects `TypeError` to propagate.

## Diagnosis Process

- For bug 1: The test creates a `BadDict` that raises `KeyboardInterrupt` from `items()`. The bare `except` in `load_config` catches it and calls `pass`. The fix is to catch only `Exception` (or better, only `AttributeError`), since `KeyboardInterrupt` and `SystemExit` derive from `BaseException`, not `Exception`.
- For bug 2: The test uses `assertRaisesRegex(ValueError, r"port")` and `assertRaisesRegex(ValueError, r"not_a_number")`. The current code raises `Exception("")` — wrong type and empty message.
- For bug 3: The test calls `cp.validate(None)` and expects `TypeError`. The current code catches and swallows it.

## The Fix

### Bug 1 — Bare except in `load_config`
```python
# Before
try:
    for key, value in config_dict.items():
        self._config[key] = value
except:
    pass

# After
try:
    for key, value in config_dict.items():
        self._config[key] = value
except Exception:
    pass
```

### Bug 2 — Wrong exception type and empty message in `get_int`
```python
# Before
try:
    return int(value)
except ValueError:
    raise Exception("")

# After
try:
    return int(value)
except ValueError:
    raise ValueError(
        f"Cannot convert key '{key}' value '{value}' to int"
    )
```

### Bug 3 — Swallowed TypeError in `validate`
```python
# Before
try:
    missing = [k for k in required_keys if k not in self._config]
except TypeError:
    return

# After
missing = [k for k in required_keys if k not in self._config]
```

## Why This Bug Matters

- **Bare `except`** is almost always wrong. It catches `KeyboardInterrupt`, `SystemExit`, and `GeneratorExit`, making programs impossible to interrupt or shut down cleanly. Use `except Exception` at minimum.
- **Re-raising as a different type** loses context. Callers catching `ValueError` will miss a generic `Exception`. Always preserve or narrow the exception type, and include a descriptive message.
- **Silently swallowing exceptions** hides bugs. If a caller passes `None` where a list is expected, that is a programming error that should be surfaced immediately, not hidden behind a silent return.

## Discussion

- For bug 1, `except Exception: pass` still silences things like `AttributeError` if `config_dict` has no `items()`. A stricter approach would remove the try/except entirely and let all errors propagate. The choice depends on whether `load_config` should be lenient or strict.
- For bug 2, using `raise ValueError(...) from e` preserves the original traceback, which is helpful for debugging. This is a Python best practice when converting exceptions.
- For bug 3, simply removing the try/except is the cleanest fix. The `TypeError` from iterating `None` is already descriptive. Adding a try/except only makes sense if you want to customize the message.
