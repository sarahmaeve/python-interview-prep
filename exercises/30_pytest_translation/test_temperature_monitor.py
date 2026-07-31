"""Your pytest translation of test_temperature_monitor_unittest.py.

Run:
    python -m pytest test_temperature_monitor.py -v

The first test is translated for you as an example.  Each remaining test
is a deliberately-failing stub with a TODO comment describing what to use —
the suite starts red and goes green as you translate.  When you're done,
`pytest` should collect 15 tests and all of them should pass.

Translation cheat sheet (see guides/03_unittest_fundamentals.py Section 9):

    self.assertEqual(a, b)              ->  assert a == b
    self.assertIsNone(x)                ->  assert x is None
    self.assertIsInstance(x, T)         ->  assert isinstance(x, T)
    self.assertRaises(E)                ->  with pytest.raises(E):
    self.assertRaisesRegex(E, "...")    ->  with pytest.raises(E, match="..."):
    setUp / tearDown                    ->  @pytest.fixture (yield-based)
    for ... with self.subTest(...)      ->  @pytest.mark.parametrize(...)
"""

import pytest
from temperature_monitor import Reading, TemperatureMonitor

# ---------------------------------------------------------------------------
# CONSTRUCTION
# ---------------------------------------------------------------------------


# Example — this is the fully-translated version of:
#   def test_requires_low_below_high(self):
#       with self.assertRaises(ValueError):
#           TemperatureMonitor(low_threshold=100, high_threshold=0)
def test_requires_low_below_high():
    with pytest.raises(ValueError):
        TemperatureMonitor(low_threshold=100, high_threshold=0)


def test_low_equal_to_high_is_rejected():
    # TODO: use `with pytest.raises(ValueError, match="must be <"):`
    pytest.fail("TODO: translate this test")


def test_default_thresholds():
    # TODO: call TemperatureMonitor() and assert on .low_threshold / .high_threshold
    pytest.fail("TODO: translate this test")


# ---------------------------------------------------------------------------
# FIXTURES — replace unittest's setUp/tearDown
# ---------------------------------------------------------------------------


# TODO: define a `monitor` fixture that yields a fresh
# TemperatureMonitor(low_threshold=0, high_threshold=100) for each test.
# The teardown (`reset`) is handled for free because each test gets a
# fresh instance — there's no shared state to clear.
@pytest.fixture
def monitor() -> TemperatureMonitor:
    ...  # replace with a real fixture body


def test_empty_monitor_has_no_latest(monitor):
    # TODO: assert that monitor.latest() is None
    pytest.fail("TODO: translate this test")


def test_empty_monitor_has_no_average(monitor):
    # TODO
    pytest.fail("TODO: translate this test")


def test_record_returns_a_reading(monitor):
    # TODO: record(21.5), assert the return value is a Reading with celsius == 21.5
    pytest.fail("TODO: translate this test")


def test_latest_returns_most_recent(monitor):
    # TODO: record two readings, assert .latest().celsius equals the second
    pytest.fail("TODO: translate this test")


def test_average_of_readings(monitor):
    # TODO: record 10.0, 20.0, 30.0; assert monitor.average() == 20.0
    pytest.fail("TODO: translate this test")


# ---------------------------------------------------------------------------
# PARAMETRIZE — replaces unittest's subTest table
# ---------------------------------------------------------------------------


# TODO: use @pytest.mark.parametrize to run the same assertion for each
# (celsius, expected) pair below.  The five cases are:
#   (-5.0,   True)
#   ( 0.0,   False)
#   (50.0,   False)
#   (100.0,  False)
#   (100.1,  True)
# The test should construct a Reading with the given celsius and compare
# monitor.is_out_of_range(reading) to expected.
@pytest.mark.parametrize("celsius,expected", [
    # TODO: fill in the table
])
def test_classification(monitor, celsius, expected):
    pytest.fail("TODO: translate this test")


def test_out_of_range_readings_filters_correctly(monitor):
    # TODO: record 50, -1, 101, 99; assert out_of_range_readings()'s
    # celsius values are [-1, 101].
    pytest.fail("TODO: translate this test")


# ---------------------------------------------------------------------------
# A standalone test — no fixture needed
# ---------------------------------------------------------------------------


def test_reset_clears_readings():
    # TODO: make a TemperatureMonitor(), record two readings, reset, and
    # assert that latest() and average() are both None.
    pytest.fail("TODO: translate this test")
