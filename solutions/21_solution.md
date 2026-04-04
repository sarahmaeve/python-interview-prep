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

The `assertLogs` tests are the key diagnostic tool here. When you see:

```
AssertionError: no logs of level WARNING or higher triggered on data_processor
```

This tells you the code IS logging, but at the wrong level. Check the `_validate` method for `logger.debug()` calls that should be `logger.warning()`.

The `test_summary_mixed_valid_and_invalid` failure points to the counting bug — it expects `processed_count=2` for 2 valid records out of 4, but the count is wrong because of the append-before-transform issue.
