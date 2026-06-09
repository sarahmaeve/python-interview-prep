# Solution: Exercise 21 — Observability & Logging

## Bugs Found

### Bug 1 — Validation logs at DEBUG (invisible)

**Location:** `data_processor.py`, `_validate()` method — all three `logger.debug()` calls

```python
# Before (invisible at default WARNING threshold)
logger.debug("Skipping non-dict record: %r", record)

# After
logger.warning("Skipping non-dict record: %r", record)
```

All three validation failure paths need the same change: `debug` → `warning`.

**Why it matters:** The tests use `assertLogs("data_processor", level="WARNING")`. At the WARNING threshold, DEBUG messages are silently filtered — so the tests fail because no log output is captured. This mirrors a real production problem: if you log important events at too low a level, your monitoring can't see them.

### Bug 2 — `_transform()` silently swallows errors

**Location:** `data_processor.py`, `_transform()` method

```python
# Before (errors vanish silently)
except Exception:
    pass

# After (errors are logged and tracked)
except Exception as e:
    logger.warning("Transform failed for record %s: %s", record.get("id"), e)
    self.errors.append(record)
```

**Why it matters:** A bare `except: pass` is the worst anti-pattern for observability. When a record fails to transform, nothing is logged, nothing is tracked, and the record stays in `self.processed` in a half-transformed state. The fix logs the failure AND adds the record to the error list so the summary is accurate.

### Bug 3 — Record appended before transform

**Location:** `data_processor.py`, `process_records()` method

```python
# Before (appends BEFORE transform — failed records inflate count)
self.processed.append(record)
self._transform(record)

# After (appends only after successful transform)
self._transform(record)
if record not in self.errors:
    self.processed.append(record)
```

Alternatively, you can restructure `_transform()` to return success/failure and use that:

```python
self._transform(record)
if record not in self.errors:
    self.processed.append(record)
```

**Why it matters:** The original code appends the record to `self.processed` before attempting the transform. If the transform fails (and now properly adds the record to `self.errors`), the record is in both lists, inflating `processed_count`. Moving the append to after the transform ensures only successfully transformed records are counted.

## Diagnosis Process

The `assertLogs` failures point at two different problems, even though the
error text is identical:

```
AssertionError: no logs of level WARNING or higher triggered on data_processor
```

For the validation tests (`test_logs_warning_for_missing_keys` and friends),
the code IS logging — just at DEBUG, below the captured threshold. Check
`_validate` for `logger.debug()` calls that should be `logger.warning()`.
For `test_logs_warning_when_transform_fails`, nothing is logged at all:
the `except Exception: pass` in `_transform` swallows the failure.

`test_transform_failure_is_tracked_as_error` fails because `self.errors`
is never appended to, so `error_count` stays 0. And
`test_transform_failure_not_counted_as_processed` fails because the record
is appended to `self.processed` BEFORE the transform runs — a record that
then fails transformation is still counted as processed.

Note how the tests trigger the failure path: a `str` subclass whose
`.upper()` raises. It sails through `_validate` (it really is a str) and
detonates mid-transform — the same shape as real-world data corruption
that only surfaces partway through a pipeline.
