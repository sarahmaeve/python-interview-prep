"""Temperature monitor — production code (already working and tested).

This module has NO bugs.  Your job is to translate the existing unittest
test file into idiomatic pytest.

See README.md for the task, and guides/03_unittest_fundamentals.py
Section 9 for the pytest translation cheat sheet.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass(frozen=True)
class Reading:
    """A single temperature reading."""
    celsius: float
    at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class TemperatureMonitor:
    """Tracks temperature readings and flags when they exceed a threshold."""

    def __init__(self, *, high_threshold: float = 100.0,
                 low_threshold: float = 0.0) -> None:
        if low_threshold >= high_threshold:
            raise ValueError(
                f"low_threshold ({low_threshold}) must be < "
                f"high_threshold ({high_threshold})"
            )
        self.high_threshold = high_threshold
        self.low_threshold = low_threshold
        self._readings: list[Reading] = []

    def record(self, celsius: float) -> Reading:
        """Record a reading, return it, and return it."""
        reading = Reading(celsius=celsius)
        self._readings.append(reading)
        return reading

    def latest(self) -> Reading | None:
        """The most recent reading, or None if empty."""
        return self._readings[-1] if self._readings else None

    def average(self) -> float | None:
        """Arithmetic mean of all readings' celsius values, or None if empty."""
        if not self._readings:
            return None
        return sum(r.celsius for r in self._readings) / len(self._readings)

    def is_out_of_range(self, reading: Reading) -> bool:
        """True if *reading* is outside [low_threshold, high_threshold]."""
        return (reading.celsius < self.low_threshold
                or reading.celsius > self.high_threshold)

    def out_of_range_readings(self) -> list[Reading]:
        """All recorded readings outside the configured thresholds."""
        return [r for r in self._readings if self.is_out_of_range(r)]

    def reset(self) -> None:
        """Clear every recorded reading."""
        self._readings.clear()
