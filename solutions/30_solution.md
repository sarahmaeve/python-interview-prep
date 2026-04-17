# Solution: Exercise 30 — Pytest Translation

## Goal

Produce `test_temperature_monitor.py` as an idiomatic pytest translation of the unittest reference in `test_temperature_monitor_unittest.py`. The production code is correct; the exercise is purely about internalising the pytest idioms.

## Full translation

```python
import pytest

from temperature_monitor import Reading, TemperatureMonitor


# ---------------------------------------------------------------------------
# CONSTRUCTION
# ---------------------------------------------------------------------------


def test_requires_low_below_high():
    with pytest.raises(ValueError):
        TemperatureMonitor(low_threshold=100, high_threshold=0)


def test_low_equal_to_high_is_rejected():
    with pytest.raises(ValueError, match="must be <"):
        TemperatureMonitor(low_threshold=50, high_threshold=50)


def test_default_thresholds():
    m = TemperatureMonitor()
    assert m.low_threshold == 0.0
    assert m.high_threshold == 100.0


# ---------------------------------------------------------------------------
# FIXTURES
# ---------------------------------------------------------------------------


@pytest.fixture
def monitor() -> TemperatureMonitor:
    return TemperatureMonitor(low_threshold=0, high_threshold=30)


def test_empty_monitor_has_no_latest(monitor):
    assert monitor.latest() is None


def test_empty_monitor_has_no_average(monitor):
    assert monitor.average() is None


def test_record_returns_a_reading(monitor):
    r = monitor.record(21.5)
    assert isinstance(r, Reading)
    assert r.celsius == 21.5


def test_latest_returns_most_recent(monitor):
    monitor.record(18.0)
    monitor.record(22.0)
    assert monitor.latest().celsius == 22.0


def test_average_of_readings(monitor):
    for c in (10.0, 20.0, 30.0):
        monitor.record(c)
    assert monitor.average() == 20.0


# ---------------------------------------------------------------------------
# PARAMETRIZE
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("celsius,expected", [
    (-5.0, True),
    (0.0, False),
    (50.0, False),
    (100.0, False),
    (100.1, True),
])
def test_classification(monitor, celsius, expected):
    # NOTE: the unittest version uses a monitor with range [0,100] for
    # this subTest block; the fixture's [0,30] range doesn't match.
    # Construct a wider monitor here, or parameterise the monitor.
    m = TemperatureMonitor(low_threshold=0, high_threshold=100)
    assert m.is_out_of_range(Reading(celsius=celsius)) is expected


def test_out_of_range_readings_filters_correctly():
    m = TemperatureMonitor(low_threshold=0, high_threshold=100)
    m.record(50)
    m.record(-1)
    m.record(101)
    m.record(99)
    flagged = m.out_of_range_readings()
    assert [r.celsius for r in flagged] == [-1, 101]


# ---------------------------------------------------------------------------
# STANDALONE
# ---------------------------------------------------------------------------


def test_reset_clears_readings():
    m = TemperatureMonitor()
    m.record(10)
    m.record(20)
    m.reset()
    assert m.latest() is None
    assert m.average() is None
```

## Key translations, explained

| unittest | pytest | Why |
|---|---|---|
| `class TestX(TestCase)` | plain `def test_*()` | Pytest doesn't require classes. Group with module-level organisation or `class TestX:` (no inheritance). |
| `self.assertEqual(a, b)` | `assert a == b` | Pytest rewrites `assert` to produce detailed failure messages. You get the same diagnostics without the method-style API. |
| `self.assertRaises(E)` | `pytest.raises(E)` | A context manager returns the captured exception in `.value`. |
| `self.assertRaisesRegex(E, msg)` | `pytest.raises(E, match=msg)` | `match` takes a regex; use `re.escape` if you mean literal text. |
| `setUp / tearDown` | `@pytest.fixture` that yields | Yield-based fixtures: code before `yield` is setup, code after is teardown. |
| `for ... with self.subTest(x=...)` | `@pytest.mark.parametrize` | Each row becomes an individual test case in the report. |

## Why bother learning both?

- Most real-world 2025 Python teams use pytest. You'll encounter it nearly everywhere.
- The stdlib's `unittest` is in every Python install, so you'll still meet it in library code that wants zero dependencies.
- `unittest.TestCase` subclasses run under pytest without modification — you can migrate gradually.

## Discussion

- **`class TestX:`** — pytest collects test methods in a plain class (no inheritance needed) as long as it starts with `Test`. Useful for grouping.
- **Fixtures compose** — one fixture can consume another. `@pytest.fixture def hot_monitor(monitor): ...` layers on top of `monitor`.
- **Fixture scopes** — `scope="module"` or `scope="session"` makes expensive setup run once, shared across tests. Mirrors `setUpClass` but composes better.
- **Markers** — `@pytest.mark.slow`, `@pytest.mark.integration`, etc. Filter with `pytest -m "not slow"` to skip in fast runs.
- **`caplog`** — the pytest equivalent of `assertLogs`. A single fixture, no boilerplate.
- **`tmp_path`** — a `Path` fixture pointing to a per-test temp directory. Zero boilerplate compared to `tempfile.TemporaryDirectory`.
