import unittest
from unittest.mock import MagicMock
from api_client import ApiClient, RateLimitExceeded


class TestBasicRequest(unittest.TestCase):

    def test_successful_request(self):
        """A successful request returns the transport's response."""
        # TODO: Create mock transport and clock. Configure transport.request
        # to return {"status": 200}. Call client.request and verify the response.
        pass

    def test_passes_method_and_url(self):
        """Transport receives the correct method and URL."""
        # TODO: Call client.request("GET", "/data"). Assert transport.request
        # was called with those arguments.
        pass


class TestRateLimiting(unittest.TestCase):

    def test_allows_requests_within_limit(self):
        """Requests within the limit should all succeed."""
        # TODO: Set max_requests=3. Make 3 requests. All should succeed.
        pass

    def test_exceeds_limit_raises(self):
        """The request that exceeds the limit raises RateLimitExceeded."""
        # TODO: Set max_requests=2. Make 3 requests. Third should raise.
        pass

    def test_limit_resets_after_window(self):
        """After the window elapses, the limit resets."""
        # TODO: Set max_requests=1, window_seconds=60. Make 1 request.
        # Advance clock by 61s. Make another — should succeed.
        pass


class TestRetry(unittest.TestCase):

    def test_retries_then_succeeds(self):
        """Transient failures are retried."""
        # TODO: Configure transport to fail once then succeed (side_effect list).
        # Set max_retries=2. Verify the successful response is returned.
        pass

    def test_raises_after_retries_exhausted(self):
        """After max_retries, the exception propagates."""
        # TODO: Configure transport to always fail. Set max_retries=1.
        # Verify the exception is raised and transport was called twice.
        pass


if __name__ == "__main__":
    unittest.main()
