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

Observability should preserve the outcome model: a failed record must be
visible somewhere appropriate, log severity should match operational
importance, and success metrics should be updated only after the work succeeds.

There are 3 bugs. If you get stuck, use [HINTS.md](HINTS.md).
