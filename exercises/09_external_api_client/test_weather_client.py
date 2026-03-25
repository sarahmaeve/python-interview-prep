"""
Correct tests for WeatherClient.

These tests mock urllib.request.urlopen so no real HTTP calls are made.
Study the mock setup -- this pattern is essential for testing code that
talks to external services.
"""

import json
import unittest
from io import BytesIO
from unittest.mock import patch, MagicMock
from urllib.error import URLError

from weather_client import WeatherClient


def _mock_response(data):
    """Create a mock HTTP response whose .read() returns JSON bytes."""
    body = json.dumps(data).encode("utf-8")
    response = MagicMock()
    response.read.return_value = body
    response.__enter__ = lambda s: s
    response.__exit__ = MagicMock(return_value=False)
    return response


class TestGetTemperature(unittest.TestCase):
    """Tests for WeatherClient.get_temperature."""

    @patch("weather_client.urlopen")
    def test_returns_temperature_as_float(self, mock_urlopen):
        mock_urlopen.return_value = _mock_response(
            {"main": {"temp": 22.5}}
        )
        client = WeatherClient()
        result = client.get_temperature("London")
        self.assertIsInstance(result, float)
        self.assertAlmostEqual(result, 22.5)

    @patch("weather_client.urlopen")
    def test_calls_correct_url(self, mock_urlopen):
        mock_urlopen.return_value = _mock_response(
            {"main": {"temp": 10.0}}
        )
        client = WeatherClient("http://example.com")
        client.get_temperature("Berlin")
        called_url = mock_urlopen.call_args[0][0]
        self.assertEqual(called_url, "http://example.com/temperature?city=Berlin")

    @patch("weather_client.urlopen")
    def test_handles_negative_temperature(self, mock_urlopen):
        mock_urlopen.return_value = _mock_response(
            {"main": {"temp": -15.0}}
        )
        client = WeatherClient()
        result = client.get_temperature("Moscow")
        self.assertAlmostEqual(result, -15.0)


class TestGetForecast(unittest.TestCase):
    """Tests for WeatherClient.get_forecast."""

    @patch("weather_client.urlopen")
    def test_returns_list_of_temperatures(self, mock_urlopen):
        mock_urlopen.return_value = _mock_response(
            {"forecast": [{"temp": 20.0}, {"temp": 21.0}, {"temp": 19.5}]}
        )
        client = WeatherClient()
        result = client.get_forecast("Paris", days=3)
        self.assertEqual(result, [20.0, 21.0, 19.5])

    @patch("weather_client.urlopen")
    def test_default_days_is_five(self, mock_urlopen):
        mock_urlopen.return_value = _mock_response(
            {"forecast": [{"temp": i} for i in range(5)]}
        )
        client = WeatherClient("http://example.com")
        client.get_forecast("Tokyo")
        called_url = mock_urlopen.call_args[0][0]
        self.assertIn("days=5", called_url)

    @patch("weather_client.urlopen")
    def test_url_encodes_city_name(self, mock_urlopen):
        """Cities with spaces must be percent-encoded in the URL."""
        mock_urlopen.return_value = _mock_response(
            {"forecast": [{"temp": 25.0}]}
        )
        client = WeatherClient("http://example.com")
        client.get_forecast("New York", days=1)
        called_url = mock_urlopen.call_args[0][0]
        # "New York" must become "New%20York" (or "New+York") -- no raw space
        self.assertNotIn(" ", called_url)
        self.assertIn("New%20York", called_url)

    @patch("weather_client.urlopen")
    def test_forecast_with_single_day(self, mock_urlopen):
        mock_urlopen.return_value = _mock_response(
            {"forecast": [{"temp": 30.0}]}
        )
        client = WeatherClient()
        result = client.get_forecast("Cairo", days=1)
        self.assertEqual(result, [30.0])


class TestGetTemperatureWithRetry(unittest.TestCase):
    """Tests for WeatherClient.get_temperature_with_retry."""

    @patch("weather_client.urlopen")
    def test_returns_temperature_on_first_success(self, mock_urlopen):
        mock_urlopen.return_value = _mock_response(
            {"main": {"temp": 18.0}}
        )
        client = WeatherClient()
        result = client.get_temperature_with_retry("Dublin")
        self.assertAlmostEqual(result, 18.0)

    @patch("weather_client.urlopen")
    def test_retries_on_network_error_then_succeeds(self, mock_urlopen):
        """Fail twice, then succeed on the third (final) attempt."""
        mock_urlopen.side_effect = [
            URLError("connection refused"),
            URLError("timeout"),
            _mock_response({"main": {"temp": 12.0}}),
        ]
        client = WeatherClient()
        result = client.get_temperature_with_retry("Oslo", retries=3)
        self.assertAlmostEqual(result, 12.0)
        self.assertEqual(mock_urlopen.call_count, 3)

    @patch("weather_client.urlopen")
    def test_raises_after_all_retries_exhausted(self, mock_urlopen):
        mock_urlopen.side_effect = URLError("down")
        client = WeatherClient()
        with self.assertRaises(URLError):
            client.get_temperature_with_retry("Atlantis", retries=2)
        self.assertEqual(mock_urlopen.call_count, 2)


if __name__ == "__main__":
    unittest.main()
