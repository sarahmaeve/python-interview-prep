"""Tests for the temperature monitoring system.

All 12 tests are correct. Do NOT modify this file.
Fix the 4 bugs in temp_monitor.py so that every test passes.
"""

import unittest

from temp_monitor import MonitoringStation, TemperatureSensor


# ---------------------------------------------------------------------------
# TemperatureSensor tests
# ---------------------------------------------------------------------------


class TestRecordAndLatest(unittest.TestCase):
    def test_record_and_latest(self):
        """latest returns the most recently recorded value."""
        sensor = TemperatureSensor("kitchen")
        sensor.record(20.5)
        sensor.record(22.0)
        sensor.record(19.3)
        self.assertEqual(sensor.latest, 19.3)


class TestAverage(unittest.TestCase):
    def test_average_as_property(self):
        """average is accessed as a property (no parentheses) and returns a float."""
        sensor = TemperatureSensor("bedroom")
        sensor.record(10.0)
        sensor.record(20.0)
        sensor.record(30.0)
        # Accessed without parentheses -- must be a @property, not a plain method.
        result = sensor.average
        self.assertIsInstance(result, float)
        self.assertAlmostEqual(result, 20.0)

    def test_average_no_readings(self):
        """average returns None when the sensor has no readings."""
        sensor = TemperatureSensor("empty")
        self.assertIsNone(sensor.average)


class TestUnit(unittest.TestCase):
    def test_unit_default_is_celsius(self):
        """A new sensor defaults to Celsius."""
        sensor = TemperatureSensor("hallway")
        self.assertEqual(sensor.unit, "C")

    def test_set_unit_to_fahrenheit_converts_readings(self):
        """Setting unit to 'F' converts stored readings from C to F."""
        sensor = TemperatureSensor("lab")
        sensor.record(0.0)
        sensor.record(100.0)
        # Assignment syntax must work (requires @unit.setter).
        sensor.unit = "F"
        self.assertAlmostEqual(sensor.latest, 212.0)
        self.assertAlmostEqual(sensor.average, 122.0)
        self.assertEqual(sensor.unit, "F")

    def test_set_invalid_unit_raises(self):
        """Setting unit to an unsupported value raises ValueError."""
        sensor = TemperatureSensor("garage")
        with self.assertRaises(ValueError):
            sensor.unit = "K"


class TestReset(unittest.TestCase):
    def test_reset_clears_readings(self):
        """After reset, latest and average are both None."""
        sensor = TemperatureSensor("attic")
        sensor.record(15.0)
        sensor.record(25.0)
        sensor.reset()
        self.assertIsNone(sensor.latest)
        self.assertIsNone(sensor.average)


# ---------------------------------------------------------------------------
# MonitoringStation tests
# ---------------------------------------------------------------------------


class TestAddAndGetSensor(unittest.TestCase):
    def test_add_and_get_sensor(self):
        """get_sensor returns the actual TemperatureSensor object, not a string."""
        station = MonitoringStation()
        sensor = TemperatureSensor("roof")
        station.add_sensor(sensor)
        retrieved = station.get_sensor("roof")
        self.assertIsInstance(retrieved, TemperatureSensor)
        self.assertIs(retrieved, sensor)

    def test_get_sensor_missing(self):
        """get_sensor returns None for an unknown label."""
        station = MonitoringStation()
        self.assertIsNone(station.get_sensor("nonexistent"))


class TestAllAverages(unittest.TestCase):
    def test_all_averages(self):
        """all_averages returns a dict mapping labels to average readings."""
        station = MonitoringStation()

        s1 = TemperatureSensor("north")
        s1.record(10.0)
        s1.record(20.0)

        s2 = TemperatureSensor("south")
        s2.record(30.0)
        s2.record(40.0)

        station.add_sensor(s1)
        station.add_sensor(s2)

        avgs = station.all_averages()
        self.assertAlmostEqual(avgs["north"], 15.0)
        self.assertAlmostEqual(avgs["south"], 35.0)


class TestStationAverage(unittest.TestCase):
    def test_station_average_skips_empty_sensors(self):
        """station_average ignores sensors with no readings."""
        station = MonitoringStation()

        s1 = TemperatureSensor("east")
        s1.record(10.0)
        s1.record(30.0)  # average = 20

        s2 = TemperatureSensor("west")
        s2.record(40.0)  # average = 40

        s3 = TemperatureSensor("center")
        # no readings -- should be skipped

        station.add_sensor(s1)
        station.add_sensor(s2)
        station.add_sensor(s3)

        # Expected: (20 + 40) / 2 = 30, NOT (20 + 40 + None) / 3
        self.assertAlmostEqual(station.station_average(), 30.0)


class TestHighAlert(unittest.TestCase):
    def test_high_alert(self):
        """high_alert returns labels of sensors whose latest reading exceeds the threshold."""
        station = MonitoringStation()

        hot = TemperatureSensor("furnace")
        hot.record(85.0)
        hot.record(102.5)

        warm = TemperatureSensor("office")
        warm.record(24.0)

        cold = TemperatureSensor("freezer")
        cold.record(-18.0)

        station.add_sensor(hot)
        station.add_sensor(warm)
        station.add_sensor(cold)

        alerts = station.high_alert(50.0)
        self.assertEqual(alerts, ["furnace"])


if __name__ == "__main__":
    unittest.main()
