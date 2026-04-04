# Exercise 21: Observability & Logging

A data processor that silently drops records and produces incorrect counts. Your job: fix 3 bugs and ensure the code logs meaningful warnings when things go wrong.

**This exercise practices:** Python's `logging` module, `assertLogs` in unittest, and instrumenting code for observability.

## How to run the tests

```bash
cd exercises/21_observability_logging
python -m unittest test_data_processor
```

Your goal: edit `data_processor.py` until all tests pass.

## Key Concept

Some tests use `self.assertLogs("data_processor", level="WARNING")` to verify that your code emits the right log messages at the right level. If you've never seen `assertLogs`, read Guide 08 first or check the [unittest docs](https://docs.python.org/3/library/unittest.html#unittest.TestCase.assertLogs).

The pattern:
```python
with self.assertLogs("logger_name", level="WARNING") as cm:
    do_something_that_should_warn()
# cm.output is a list like ["WARNING:logger_name:the message"]
```

If **no** log messages are emitted at the specified level (or above), `assertLogs` raises `AssertionError` — the test fails.

## Bugs: 3

<details>
<summary>Hint 1 (gentle)</summary>

One method catches exceptions but doesn't tell anyone about them — not the caller, not the log, not the error list. Records just vanish.
</details>

<details>
<summary>Hint 2 (moderate)</summary>

Check which logging **level** is used for invalid records. The tests expect warnings to be visible at the `WARNING` threshold. Are they?

Also: when does a record get added to `self.processed` — before or after the transform? What happens if the transform fails?
</details>

<details>
<summary>Hint 3 (specific)</summary>

1. **`_transform()` swallows errors silently**: The bare `except` catches errors but does nothing. Add `logger.warning(...)` to log the failure and append the record info to `self.errors` so it's tracked.

2. **`_validate()` logs at the wrong level**: All three validation failure paths use `logger.debug(...)`, which is invisible at the default WARNING threshold. Change them to `logger.warning(...)`.

3. **`process_records()` appends too early**: The record is added to `self.processed` *before* `_transform()` is called. If the transform fails, the record is still counted as processed. Move the append to *after* a successful transform.
</details>
