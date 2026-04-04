"""Tests for ServiceClient.

These tests verify correct handling of timeouts, retries, and
environment-aware configuration.
Do NOT modify this file. Fix the bugs in service_client.py.
"""

import json
import unittest
from io import BytesIO
from unittest.mock import patch, MagicMock
from urllib.error import URLError

# We must reload the module in some tests to check import-time behavior,
# so we import the module rather than the class directly.
import service_client


def _mock_response(data):
    """Create a mock HTTP response that returns JSON data."""
    response = MagicMock()
    response.read.return_value = json.dumps(data).encode("utf-8")
    return response


class TestFetch(unittest.TestCase):
    """Tests for the fetch() method."""

    def _make_client(self, **overrides):
        config = {
            "base_url": "http://test-server:8080",
            "timeout": 5,
            "retries": 3,
            "is_ci": False,
        }
        config.update(overrides)
        return service_client.ServiceClient(config=config)

    @patch("service_client.urlopen")
    def test_fetch_returns_json(self, mock_urlopen):
        mock_urlopen.return_value = _mock_response({"status": "ok"})
        client = self._make_client()

        result = client.fetch("/api/data")
        self.assertEqual(result, {"status": "ok"})

    @patch("service_client.urlopen")
    def test_fetch_passes_timeout(self, mock_urlopen):
        """The timeout from config must be passed to urlopen."""
        mock_urlopen.return_value = _mock_response({"status": "ok"})
        client = self._make_client(timeout=7)

        client.fetch("/api/data")

        # urlopen must have been called with timeout=7
        _args, kwargs = mock_urlopen.call_args
        self.assertEqual(kwargs.get("timeout"), 7,
                         "urlopen must be called with timeout from config")

    @patch("service_client.time.sleep")
    @patch("service_client.urlopen")
    def test_fetch_retries_on_error(self, mock_urlopen, mock_sleep):
        """Should retry on URLError, then succeed."""
        mock_urlopen.side_effect = [
            URLError("Connection refused"),
            _mock_response({"status": "ok"}),
        ]
        client = self._make_client(retries=3)

        result = client.fetch("/api/data")
        self.assertEqual(result, {"status": "ok"})
        self.assertEqual(mock_urlopen.call_count, 2)

    @patch("service_client.time.sleep")
    @patch("service_client.urlopen")
    def test_fetch_raises_after_max_retries(self, mock_urlopen, mock_sleep):
        """Should raise URLError after all retries are exhausted."""
        mock_urlopen.side_effect = URLError("Connection refused")
        client = self._make_client(retries=3)

        with self.assertRaises(URLError):
            client.fetch("/api/data")
        self.assertEqual(mock_urlopen.call_count, 3)

    @patch("service_client.time.sleep")
    @patch("service_client.urlopen")
    def test_fetch_sleeps_between_retries(self, mock_urlopen, mock_sleep):
        """Should use exponential backoff between retries."""
        mock_urlopen.side_effect = [
            URLError("fail"),
            URLError("fail"),
            _mock_response({"ok": True}),
        ]
        client = self._make_client(retries=3)

        client.fetch("/api/data")
        # Backoff: 2^0=1s, 2^1=2s
        sleep_calls = [call[0][0] for call in mock_sleep.call_args_list]
        self.assertEqual(sleep_calls, [1, 2])

    @patch("service_client.urlopen")
    def test_fetch_builds_correct_url(self, mock_urlopen):
        mock_urlopen.return_value = _mock_response({})
        client = self._make_client(base_url="http://myserver:9090")

        client.fetch("/api/data")
        called_url = mock_urlopen.call_args[0][0]
        self.assertEqual(called_url, "http://myserver:9090/api/data")


class TestConfig(unittest.TestCase):
    """Tests for configuration behavior."""

    def test_config_uses_injected_values(self):
        """When config is passed explicitly, it should be used as-is."""
        config = {
            "base_url": "http://custom:1234",
            "timeout": 99,
            "retries": 1,
            "is_ci": True,
        }
        client = service_client.ServiceClient(config=config)
        self.assertEqual(client.config["base_url"], "http://custom:1234")
        self.assertEqual(client.config["timeout"], 99)

    @patch.dict("os.environ", {"API_BASE_URL": "http://env-server:5000"})
    def test_config_not_cached_at_import(self):
        """Creating a client without config should read CURRENT env vars,
        not the values captured at import time."""
        # This test will fail if get_config() is a default argument,
        # because the default was evaluated at import time (before
        # API_BASE_URL was set in this test).
        client = service_client.ServiceClient()
        self.assertEqual(client.config["base_url"], "http://env-server:5000")

    def test_default_config_values(self):
        """With no env vars set, defaults should be used."""
        config = service_client.get_config()
        self.assertEqual(config["base_url"], "http://localhost:8080")
        self.assertEqual(config["timeout"], 30)
        self.assertEqual(config["retries"], 3)
        self.assertFalse(config["is_ci"])


class TestHealthCheck(unittest.TestCase):
    """Tests for the health_check() method."""

    def test_health_check_uses_config_ci_flag(self):
        """In CI mode (via config), health_check should return True
        without making a network call."""
        config = {
            "base_url": "http://test:8080",
            "timeout": 5,
            "retries": 1,
            "is_ci": True,
        }
        client = service_client.ServiceClient(config=config)

        # Should return True based on config, not os.environ
        with patch.dict("os.environ", {}, clear=True):
            result = client.health_check()
        self.assertTrue(result)

    @patch("service_client.urlopen")
    def test_health_check_calls_service_when_not_ci(self, mock_urlopen):
        """When not in CI mode, health_check should actually call the service."""
        mock_urlopen.return_value = _mock_response({"status": "healthy"})
        config = {
            "base_url": "http://test:8080",
            "timeout": 5,
            "retries": 1,
            "is_ci": False,
        }
        client = service_client.ServiceClient(config=config)
        result = client.health_check()
        self.assertTrue(result)
        self.assertTrue(mock_urlopen.called)

    @patch("service_client.urlopen")
    def test_health_check_returns_false_on_error(self, mock_urlopen):
        mock_urlopen.side_effect = URLError("Connection refused")
        config = {
            "base_url": "http://test:8080",
            "timeout": 5,
            "retries": 1,
            "is_ci": False,
        }
        client = service_client.ServiceClient(config=config)
        result = client.health_check()
        self.assertFalse(result)


class TestFetchWithFallback(unittest.TestCase):
    """Tests for the fetch_with_fallback() method."""

    def _make_client(self, **overrides):
        config = {
            "base_url": "http://test:8080",
            "timeout": 5,
            "retries": 1,
            "is_ci": False,
        }
        config.update(overrides)
        return service_client.ServiceClient(config=config)

    @patch("service_client.urlopen")
    def test_returns_data_on_success(self, mock_urlopen):
        mock_urlopen.return_value = _mock_response({"key": "value"})
        client = self._make_client()
        result = client.fetch_with_fallback("/api/data", fallback_value={})
        self.assertEqual(result, {"key": "value"})

    @patch("service_client.urlopen")
    def test_returns_fallback_on_error(self, mock_urlopen):
        mock_urlopen.side_effect = URLError("Connection refused")
        client = self._make_client()
        result = client.fetch_with_fallback("/api/data", fallback_value={"default": True})
        self.assertEqual(result, {"default": True})

    @patch("service_client.urlopen")
    def test_request_count_increments(self, mock_urlopen):
        mock_urlopen.return_value = _mock_response({})
        client = self._make_client()
        self.assertEqual(client.request_count, 0)
        client.fetch("/api/a")
        self.assertEqual(client.request_count, 1)
        client.fetch("/api/b")
        self.assertEqual(client.request_count, 2)


if __name__ == "__main__":
    unittest.main()
