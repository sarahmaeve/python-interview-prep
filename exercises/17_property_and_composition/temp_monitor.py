"""Temperature monitoring system using @property decorators and composition.

This module contains 4 bugs. The test file is correct -- fix this file only.
"""


class TemperatureSensor:
    """A sensor that reads temperatures in Celsius.

    Attributes:
        label: str -- human-readable sensor name.
        _readings: list of float -- raw temperature readings.
        _unit: str -- current unit, "C" or "F".
    """

    def __init__(self, label: str) -> None:
        self.label = label
        self._readings: list[float] = []
        self._unit = "C"

    def record(self, value: float) -> None:
        """Add a temperature reading."""
        self._readings.append(float(value))

    def reset(self) -> None:
        """Clear all readings and reset unit to Celsius."""
        self._readings.clear()
        self._unit = "C"

    # ---- properties --------------------------------------------------------

    @property
    def latest(self) -> float | None:
        """Return the most recent reading, or None if there are none."""
        if not self._readings:
            return None
        return self._readings[-1]

    # BUG 1: missing @property decorator -- callers use sensor.average (no parens)
    def average(self) -> float | None:
        """Return the mean of all readings, or None if there are none."""
        if not self._readings:
            return None
        return sum(self._readings) / len(self._readings)

    @property
    def unit(self) -> str:
        """Return the current temperature unit ('C' or 'F')."""
        return self._unit

    # BUG 2: should be @unit.setter, not a plain method
    def set_unit(self, value: str) -> None:
        """Set the temperature unit, converting existing readings."""
        value = value.upper()
        if value not in ("C", "F"):
            raise ValueError(f"Unsupported unit: {value!r}. Use 'C' or 'F'.")
        if value == self._unit:
            return
        if value == "F":
            self._readings = [r * 9 / 5 + 32 for r in self._readings]
        else:
            self._readings = [(r - 32) * 5 / 9 for r in self._readings]
        self._unit = value


class MonitoringStation:
    """Aggregates multiple TemperatureSensors via composition.

    This class HAS sensors (composition) -- it is NOT a sensor (inheritance).
    """

    def __init__(self) -> None:
        self._sensors: dict[str, TemperatureSensor] = {}

    def add_sensor(self, sensor: TemperatureSensor) -> None:
        """Register a sensor with this station."""
        # BUG 3: stores the label string instead of the sensor object
        self._sensors[sensor.label] = sensor.label

    def get_sensor(self, label: str) -> TemperatureSensor | None:
        """Return the sensor with the given label, or None if not found."""
        return self._sensors.get(label)

    def all_averages(self) -> dict[str, float | None]:
        """Return a dict mapping each sensor label to its average reading."""
        return {label: sensor.average for label, sensor in self._sensors.items()}

    def station_average(self) -> float | None:
        """Return the mean of all sensor averages.

        Sensors with no readings should be excluded from the calculation.
        Returns None if no sensor has any readings.
        """
        # BUG 4: does not filter out None averages before summing
        averages = [sensor.average for sensor in self._sensors.values()]
        if not averages:
            return None
        return sum(averages) / len(averages)

    def high_alert(self, threshold: float) -> list[str]:
        """Return labels of sensors whose latest reading exceeds *threshold*."""
        alerts: list[str] = []
        for label, sensor in self._sensors.items():
            if sensor.latest is not None and sensor.latest > threshold:
                alerts.append(label)
        return alerts
