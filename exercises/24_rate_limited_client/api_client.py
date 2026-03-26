class RateLimitExceeded(Exception):
    """Raised when the rate limit has been reached."""
    pass


class ApiClient:
    """An API client with rate limiting and retry.

    Args:
        transport: Object with a .request(method, url, **kwargs) method.
                   Returns a response dict. In tests, use a MagicMock.
        clock: Callable returning current time as float (like time.time).
               In tests, use a mock you control.
        max_requests: Maximum requests allowed per window.
        window_seconds: Length of the rate-limit window in seconds.
        max_retries: How many times to retry on transient errors.
    """

    def __init__(self, transport, clock, max_requests=5, window_seconds=60,
                 max_retries=2):
        pass

    def request(self, method, url, **kwargs):
        """Make an API request with rate limiting and retry.

        1. Check rate limit — if exceeded, raise RateLimitExceeded.
        2. Call transport.request(method, url, **kwargs).
        3. On success, return the response.
        4. On failure (transport raises), retry up to max_retries times.
        5. If all retries fail, raise the last exception.

        Returns:
            The response dict from transport.
        Raises:
            RateLimitExceeded: If rate limit is exceeded.
        """
        pass

    @property
    def requests_remaining(self):
        """Number of requests remaining in the current rate window."""
        pass
