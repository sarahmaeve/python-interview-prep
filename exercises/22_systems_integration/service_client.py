"""ServiceClient — an HTTP client with retries, timeouts, and env-aware config.

This module reads configuration from environment variables and provides
a client for fetching JSON from a remote service.

There are 3 bugs in this file, all related to how the code interacts
with its deployment environment (local vs CI, test vs production).
"""

import json
import os
import time
from urllib.request import urlopen, Request
from urllib.error import URLError


def get_config():
    """Read configuration from environment variables with defaults."""
    return {
        "base_url": os.environ.get("API_BASE_URL", "http://localhost:8080"),
        "timeout": int(os.environ.get("API_TIMEOUT", "30")),
        "retries": int(os.environ.get("API_RETRIES", "3")),
        "is_ci": os.environ.get("CI", "").lower() in ("true", "1"),
    }


class ServiceClient:
    """HTTP client with retry logic and environment-aware configuration."""

    def __init__(self, config=get_config()):
        self.config = config
        self._request_count = 0

    def fetch(self, path):
        """Fetch JSON from the service.

        Retries on URLError up to config["retries"] times.
        Raises URLError if all retries are exhausted.
        """
        url = self.config["base_url"].rstrip("/") + "/" + path.lstrip("/")
        last_error = None

        for attempt in range(1, self.config["retries"] + 1):
            try:
                self._request_count += 1
                response = urlopen(url)
                data = response.read().decode("utf-8")
                return json.loads(data)
            except URLError as e:
                last_error = e
                if attempt < self.config["retries"]:
                    wait = 2 ** (attempt - 1)
                    time.sleep(wait)

        raise last_error

    def fetch_with_fallback(self, path, fallback_value):
        """Like fetch(), but returns fallback_value on failure instead
        of raising."""
        try:
            return self.fetch(path)
        except URLError:
            return fallback_value

    def health_check(self):
        """Return True if the service is reachable, False otherwise.

        In CI mode, skip the actual check and return True (assumes
        the service is mocked or not needed).
        """
        if os.environ.get("CI", "").lower() in ("true", "1"):
            return True

        try:
            self.fetch("/health")
            return True
        except URLError:
            return False

    @property
    def request_count(self):
        """Number of HTTP requests made (for observability)."""
        return self._request_count
