"""REFERENCE: the original unittest test suite.

This file is PROVIDED — do not edit.  Your job is to produce an
equivalent pytest suite in `test_temperature_monitor.py`.

Run this to confirm the source module works:

    python -m unittest test_temperature_monitor_unittest
"""

import unittest

from temperature_monitor import Reading, TemperatureMonitor


class TestTemperatureMonitorConstruction(unittest.TestCase):

    def test_requires_low_below_high(self):
        with self.assertRaises(ValueError):
            TemperatureMonitor(low_threshold=100, high_threshold=0)

    def test_low_equal_to_high_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "must be <"):
            TemperatureMonitor(low_threshold=50, high_threshold=50)

    def test_default_thresholds(self):
        m = TemperatureMonitor()
        self.assertEqual(m.low_threshold, 0.0)
        self.assertEqual(m.high_threshold, 100.0)


class TestRecordAndQuery(unittest.TestCase):

    def setUp(self):
        self.monitor = TemperatureMonitor(low_threshold=0, high_threshold=30)

    def tearDown(self):
        self.monitor.reset()

    def test_empty_monitor_has_no_latest(self):
        self.assertIsNone(self.monitor.latest())

    def test_empty_monitor_has_no_average(self):
        self.assertIsNone(self.monitor.average())

    def test_record_returns_a_reading(self):
        r = self.monitor.record(21.5)
        self.assertIsInstance(r, Reading)
        self.assertEqual(r.celsius, 21.5)

    def test_latest_returns_most_recent(self):
        self.monitor.record(18.0)
        self.monitor.record(22.0)
        latest = self.monitor.latest()
        self.assertEqual(latest.celsius, 22.0)

    def test_average_of_readings(self):
        for c in (10.0, 20.0, 30.0):
            self.monitor.record(c)
        self.assertEqual(self.monitor.average(), 20.0)


class TestOutOfRange(unittest.TestCase):
    """Table-driven via subTest — translate to @pytest.mark.parametrize."""

    def setUp(self):
        self.monitor = TemperatureMonitor(low_threshold=0, high_threshold=100)

    def test_classification(self):
        cases = [
            (-5.0, True),
            (0.0, False),
            (50.0, False),
            (100.0, False),
            (100.1, True),
        ]
        for celsius, expected in cases:
            with self.subTest(celsius=celsius):
                r = Reading(celsius=celsius)
                self.assertEqual(self.monitor.is_out_of_range(r), expected)

    def test_out_of_range_readings_filters_correctly(self):
        self.monitor.record(50)      # in
        self.monitor.record(-1)      # out
        self.monitor.record(101)     # out
        self.monitor.record(99)      # in
        flagged = self.monitor.out_of_range_readings()
        self.assertEqual([r.celsius for r in flagged], [-1, 101])


class TestReset(unittest.TestCase):

    def test_reset_clears_readings(self):
        m = TemperatureMonitor()
        m.record(10)
        m.record(20)
        m.reset()
        self.assertIsNone(m.latest())
        self.assertIsNone(m.average())


if __name__ == "__main__":
    unittest.main()
