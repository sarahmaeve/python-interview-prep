"""
Guide 05: Mocking and External Dependencies
=============================================

When your code talks to the outside world -- APIs, databases, the filesystem,
the clock -- your tests become slow, flaky, and non-deterministic.  Mocking
lets you replace those external touch-points with controlled stand-ins so you
can test YOUR logic in isolation.

Run this file:
    python guides/05_mocking_and_external_deps.py

Every section prints a header, runs its examples, and explains what happened.
"""

import datetime
import io
import json
import time
from unittest.mock import MagicMock, patch, call, mock_open

# ---------------------------------------------------------------------------
# Section 1: Why We Mock
# ---------------------------------------------------------------------------
# Real network calls in tests are:
#   - Slow (hundreds of milliseconds each)
#   - Flaky (server could be down, rate-limited, or return different data)
#   - Non-deterministic (timestamps, IDs change every run)
#
# Mocking replaces a real object with a fake that YOU control, so tests are
# fast, reliable, and repeatable.

# ---------------------------------------------------------------------------
# Section 2: Hard-to-test code vs. testable code
# ---------------------------------------------------------------------------
# HARD TO TEST -- the HTTP call is buried inside the function.

import urllib.request


def get_user_email_hard(user_id):
    """Fetch a user's email from a remote API.  Hard to test because
    urllib.request.urlopen is called directly with no seam for injection."""
    url = f"https://api.example.com/users/{user_id}"
    response = urllib.request.urlopen(url)          # <-- real network call
    data = json.loads(response.read().decode())
    return data["email"]


# TESTABLE VERSION -- accept an HTTP client as a parameter (dependency
# injection).  In production you pass a real client; in tests, a mock.

def get_user_email(user_id, http_client=None):
    """Fetch a user's email.  *http_client* must have a .get(url) method
    that returns an object with a .json() method (like requests.Response)."""
    if http_client is None:
        # Default to a real HTTP library in production.  We import here so
        # the module still loads even if requests is not installed.
        import urllib.request as _client
        http_client = _client
    url = f"https://api.example.com/users/{user_id}"
    response = http_client.get(url)
    return response.json()["email"]


def demo_dependency_injection():
    print("=" * 60)
    print("SECTION 2: Dependency injection + MagicMock")
    print("=" * 60)

    # Build a fake HTTP client with MagicMock.
    mock_client = MagicMock()
    # .get(url) returns a response whose .json() returns our canned data.
    mock_client.get.return_value.json.return_value = {
        "email": "ada@example.com",
        "id": 42,
    }

    result = get_user_email(42, http_client=mock_client)
    assert result == "ada@example.com", f"Expected ada@example.com, got {result}"

    # We can also verify HOW the mock was called:
    mock_client.get.assert_called_once_with("https://api.example.com/users/42")
    print("  PASS: get_user_email returned mocked email")
    print("  PASS: mock verified the URL that was called\n")


# ---------------------------------------------------------------------------
# Section 3: patch -- patching the right location
# ---------------------------------------------------------------------------
# Key rule: patch WHERE THE NAME IS LOOKED UP, not where it is defined.
#
# If module_a.py does `from os.path import exists` and you want to mock it,
# you patch "module_a.exists", NOT "os.path.exists", because module_a already
# has its own reference to the function.

# Suppose this module-level name simulates an import like:
#     from some_service import send_notification
_notification_log = []


def send_notification(user, message):
    """Pretend this is an imported third-party function."""
    _notification_log.append((user, message))


def register_user(username):
    """Business logic that we want to test WITHOUT actually sending
    notifications."""
    if len(username) < 3:
        raise ValueError("Username too short")
    # In real code this might be: some_service.send_notification(...)
    send_notification(username, "Welcome!")
    return {"username": username, "active": True}


def demo_patch_location():
    print("=" * 60)
    print("SECTION 3: patch -- patching the right location")
    print("=" * 60)

    # We patch THIS module's reference to send_notification.
    # __name__ resolves to "__main__" when run directly.
    with patch(f"{__name__}.send_notification") as mock_send:
        result = register_user("ada")
        assert result == {"username": "ada", "active": True}
        mock_send.assert_called_once_with("ada", "Welcome!")

    print("  PASS: register_user works, notification was mocked out")
    print("  (send_notification was never really called)\n")


# ---------------------------------------------------------------------------
# Section 4: side_effect -- errors and sequences
# ---------------------------------------------------------------------------
# side_effect can be:
#   - An exception class/instance  ->  the mock raises it when called
#   - A list                       ->  successive calls return successive items
#   - A function                   ->  the mock delegates to that function

def fetch_price(symbol, http_client):
    """Fetch a stock price.  Returns None on transient errors."""
    try:
        resp = http_client.get(f"https://api.prices.io/{symbol}")
        resp.raise_for_status()
        return resp.json()["price"]
    except Exception:
        return None


def demo_side_effect():
    print("=" * 60)
    print("SECTION 4: side_effect for errors and sequences")
    print("=" * 60)

    mock_client = MagicMock()

    # 4a: Simulate a network error on the first call.
    mock_client.get.side_effect = ConnectionError("DNS failure")
    result = fetch_price("AAPL", mock_client)
    assert result is None, "Should return None on error"
    print("  PASS: ConnectionError -> returned None")

    # 4b: Simulate a sequence of responses (first fails, second succeeds).
    good_response = MagicMock()
    good_response.json.return_value = {"price": 150.0}
    good_response.raise_for_status.return_value = None

    mock_client.get.side_effect = [
        ConnectionError("timeout"),          # first call fails
        good_response,                       # second call succeeds
    ]

    r1 = fetch_price("AAPL", mock_client)
    r2 = fetch_price("AAPL", mock_client)
    assert r1 is None and r2 == 150.0
    print("  PASS: sequence [error, success] behaved correctly\n")


# ---------------------------------------------------------------------------
# Section 5: Testing retry logic
# ---------------------------------------------------------------------------

def fetch_with_retry(url, http_client, max_retries=3, delay=1.0):
    """Try up to *max_retries* times, sleeping *delay* seconds between
    attempts.  Returns the response on success, raises on final failure."""
    last_exc = None
    for attempt in range(max_retries):
        try:
            resp = http_client.get(url)
            resp.raise_for_status()
            return resp
        except Exception as exc:
            last_exc = exc
            if attempt < max_retries - 1:
                time.sleep(delay)           # we will mock this out
    raise last_exc


def demo_retry_logic():
    print("=" * 60)
    print("SECTION 5: Testing retry logic")
    print("=" * 60)

    mock_client = MagicMock()
    ok_response = MagicMock()
    ok_response.raise_for_status.return_value = None

    # Fail twice, then succeed on the third attempt.
    mock_client.get.side_effect = [
        ConnectionError("try 1"),
        ConnectionError("try 2"),
        ok_response,
    ]

    # Patch time.sleep so the test does not actually wait.
    with patch("time.sleep") as mock_sleep:
        result = fetch_with_retry("https://api.example.com/data", mock_client)

    assert result is ok_response
    # Verify sleep was called twice (between attempt 0-1 and 1-2).
    assert mock_sleep.call_count == 2
    # Verify the delay value passed to sleep.
    mock_sleep.assert_has_calls([call(1.0), call(1.0)])
    print("  PASS: retried 3 times, slept twice, returned on third try\n")


# ---------------------------------------------------------------------------
# Section 6: Mocking datetime.now() and time.time()
# ---------------------------------------------------------------------------
# Datetime is notoriously tricky to mock because it is a C extension.
# Strategy: wrap the call in a small helper, then mock the helper.

def utcnow():
    """Thin wrapper so tests can patch THIS function instead of
    datetime.datetime.now directly."""
    return datetime.datetime.now(datetime.timezone.utc)


def is_business_hours():
    """Return True if current UTC hour is between 9 and 17 (exclusive)."""
    now = utcnow()
    return 9 <= now.hour < 17


def demo_mock_datetime():
    print("=" * 60)
    print("SECTION 6: Mocking datetime.now()")
    print("=" * 60)

    # 6a: During business hours.
    fake_morning = datetime.datetime(2026, 3, 25, 10, 30, 0,
                                     tzinfo=datetime.timezone.utc)
    with patch(f"{__name__}.utcnow", return_value=fake_morning):
        assert is_business_hours() is True
    print("  PASS: 10:30 UTC -> business hours")

    # 6b: Outside business hours.
    fake_night = datetime.datetime(2026, 3, 25, 22, 0, 0,
                                   tzinfo=datetime.timezone.utc)
    with patch(f"{__name__}.utcnow", return_value=fake_night):
        assert is_business_hours() is False
    print("  PASS: 22:00 UTC -> NOT business hours\n")


# ---------------------------------------------------------------------------
# Section 7: Testing timeout handling
# ---------------------------------------------------------------------------

def fetch_with_timeout(url, http_client, timeout=5.0):
    """Fetch *url* with a timeout.  Returns response text or an error
    string."""
    try:
        resp = http_client.get(url, timeout=timeout)
        return resp.text
    except TimeoutError:
        return "ERROR: request timed out"


def demo_timeout_handling():
    print("=" * 60)
    print("SECTION 7: Testing timeout handling")
    print("=" * 60)

    mock_client = MagicMock()

    # Simulate a timeout by raising TimeoutError.
    mock_client.get.side_effect = TimeoutError("timed out")
    result = fetch_with_timeout("https://slow.api/data", mock_client)
    assert result == "ERROR: request timed out"
    print("  PASS: timeout produced a friendly error string")

    # Verify the timeout kwarg was passed through.
    mock_client.get.assert_called_with("https://slow.api/data", timeout=5.0)
    print("  PASS: timeout value was forwarded to the client\n")


# ---------------------------------------------------------------------------
# Section 8: spec and spec_set -- constraining your mocks
# ---------------------------------------------------------------------------
# A plain MagicMock will happily accept ANY attribute or method call:
#
#     m = MagicMock()
#     m.nonexistent_method()   # no error -- returns another MagicMock
#     m.typo_attr              # no error -- also a MagicMock
#
# This is dangerous: if you misspell a method name in your test, the mock
# silently succeeds, and your test passes even though the code is wrong.
#
# FIX: pass spec= (or spec_set=) to restrict the mock to the real object's
# interface.

class RealEmailClient:
    """A stand-in for a real email client with known methods."""

    def send(self, to, subject, body):
        """Send an email."""
        ...  # pragma: no cover

    def connect(self):
        """Open a connection."""
        ...  # pragma: no cover


def demo_spec():
    print("=" * 60)
    print("SECTION 8: spec and spec_set -- constraining mocks")
    print("=" * 60)

    # --- Without spec: typos silently pass ---
    loose_mock = MagicMock()
    loose_mock.sned("a@b.com", "Hi", "Body")   # typo: "sned" not "send"
    # No error!  This is a false-positive test.

    print("  Without spec: loose_mock.sned() silently succeeds (BAD)")

    # --- With spec: typos raise AttributeError ---
    strict_mock = MagicMock(spec=RealEmailClient)
    try:
        strict_mock.sned("a@b.com", "Hi", "Body")   # typo
        print("  This line should not be reached")
    except AttributeError as e:
        print(f"  With spec:    strict_mock.sned() raises AttributeError: {e}")

    # The correctly-spelled method works fine:
    strict_mock.send("a@b.com", "Hi", "Body")
    strict_mock.send.assert_called_once_with("a@b.com", "Hi", "Body")
    print("  With spec:    strict_mock.send() works as expected")

    # --- spec_set is even stricter: prevents setting new attributes too ---
    locked_mock = MagicMock(spec_set=RealEmailClient)
    try:
        locked_mock.new_attribute = True  # not on the real class
    except AttributeError:
        print("  With spec_set: setting unknown attributes raises AttributeError")
    print()


# ---------------------------------------------------------------------------
# Section 9: Inspecting calls -- call_args, call_args_list, assert_not_called
# ---------------------------------------------------------------------------
# Beyond assert_called_once_with, mocks record rich call history:
#
#   mock.call_args        -> the (args, kwargs) of the MOST RECENT call
#   mock.call_args_list   -> list of ALL calls, each as a call() object
#   mock.call_count       -> integer count
#   mock.assert_not_called()           -> fails if mock WAS called
#   mock.assert_called()               -> fails if mock was NEVER called
#   mock.assert_called_once()          -> fails if not exactly one call

def process_order(order, email_client, sms_client):
    """Send email confirmation.  Only send SMS for orders over $100."""
    email_client.send(order["email"], "Order confirmed", f"Order #{order['id']}")
    if order["total"] > 100:
        sms_client.send_sms(order["phone"], f"Order #{order['id']} confirmed")


def demo_call_inspection():
    print("=" * 60)
    print("SECTION 9: Inspecting calls -- call_args, assert_not_called")
    print("=" * 60)

    mock_email = MagicMock()
    mock_sms = MagicMock()

    # Small order -- should NOT trigger SMS.
    small_order = {"id": 1, "email": "a@b.com", "phone": "555-0100", "total": 50}
    process_order(small_order, mock_email, mock_sms)

    # 9a: Verify email WAS sent.
    mock_email.send.assert_called_once()
    print("  PASS: email was sent for small order")

    # 9b: Verify SMS was NOT sent (order under $100).
    mock_sms.send_sms.assert_not_called()
    print("  PASS: SMS was correctly skipped for small order")

    # 9c: Inspect the exact arguments of the email call.
    args, kwargs = mock_email.send.call_args
    assert args[0] == "a@b.com", "First arg should be the email address"
    assert "Order #1" in args[2], "Body should contain the order ID"
    print(f"  PASS: email call_args -> to={args[0]!r}, subject={args[1]!r}")

    # Reset mocks for the next scenario.
    mock_email.reset_mock()
    mock_sms.reset_mock()

    # Large order -- SHOULD trigger SMS.
    large_order = {"id": 2, "email": "b@c.com", "phone": "555-0200", "total": 250}
    process_order(large_order, mock_email, mock_sms)

    mock_sms.send_sms.assert_called_once()
    print("  PASS: SMS was sent for large order")

    # 9d: call_args_list records every call (useful when a mock is called
    # multiple times).
    mock_email.reset_mock()
    for i in range(3):
        mock_email.send(f"user{i}@test.com", "Hi", "Body")

    assert mock_email.send.call_count == 3
    all_recipients = [c.args[0] for c in mock_email.send.call_args_list]
    assert all_recipients == ["user0@test.com", "user1@test.com", "user2@test.com"]
    print(f"  PASS: call_args_list captured 3 calls: {all_recipients}\n")


# ---------------------------------------------------------------------------
# Section 10: mock_open -- mocking file I/O
# ---------------------------------------------------------------------------
# When code reads or writes files, you don't want tests touching the real
# filesystem.  mock_open() creates a mock that behaves like a file handle:
#
#   - Supports iteration (for line in f)
#   - Supports .read(), .readlines(), .write()
#   - Works as a context manager (with open(...) as f)
#
# Usage:   @patch("builtins.open", new_callable=mock_open, read_data="...")
#    or:   with patch("builtins.open", mock_open(read_data="...")):

def count_lines(filepath):
    """Count non-empty lines in a file."""
    with open(filepath) as f:
        return sum(1 for line in f if line.strip())


def write_report(filepath, data):
    """Write a simple key=value report."""
    with open(filepath, "w") as f:
        for key, value in data.items():
            f.write(f"{key}={value}\n")


def parse_csv_simple(filepath):
    """Parse a CSV into a list of dicts (header row + data rows)."""
    with open(filepath) as f:
        lines = f.read().strip().split("\n")
    if len(lines) < 2:
        return []
    headers = lines[0].split(",")
    return [
        dict(zip(headers, row.split(",")))
        for row in lines[1:]
    ]


def demo_mock_open():
    print("=" * 60)
    print("SECTION 10: mock_open -- mocking file I/O")
    print("=" * 60)

    # 10a: Mocking a file read with read_data.
    fake_content = "line one\nline two\n\nline four\n"
    with patch("builtins.open", mock_open(read_data=fake_content)):
        result = count_lines("fake/path.txt")
    assert result == 3, f"Expected 3 non-empty lines, got {result}"
    print("  PASS: count_lines read mocked content (3 non-empty lines)")

    # 10b: Verifying what was WRITTEN to a file.
    m = mock_open()
    with patch("builtins.open", m):
        write_report("output.txt", {"name": "Alice", "score": "95"})

    # The mock records every write() call.  Collect them:
    handle = m()
    written = "".join(c.args[0] for c in handle.write.call_args_list)
    assert "name=Alice" in written
    assert "score=95" in written
    print(f"  PASS: write_report wrote expected content")

    # 10c: Mocking CSV parsing -- read_data supplies the full text.
    csv_text = "name,age\nAlice,30\nBob,25\n"
    with patch("builtins.open", mock_open(read_data=csv_text)):
        records = parse_csv_simple("data.csv")
    assert records == [{"name": "Alice", "age": "30"}, {"name": "Bob", "age": "25"}]
    print("  PASS: parse_csv_simple parsed mocked CSV data")

    # 10d: Routing multiple files with side_effect.
    # When code opens different files, use a side_effect function:
    file_a = "header\nrow1\n"
    file_b = "col1,col2\na,b\n"

    def open_router(path, *args, **kwargs):
        if path == "a.txt":
            return io.StringIO(file_a)
        elif path == "b.csv":
            return io.StringIO(file_b)
        raise FileNotFoundError(path)

    with patch("builtins.open", side_effect=open_router):
        assert count_lines("a.txt") == 2
        records = parse_csv_simple("b.csv")
        assert records == [{"col1": "a", "col2": "b"}]
    print("  PASS: side_effect routed different file paths to different content\n")


# ---------------------------------------------------------------------------
# Section 11: The tradeoff -- mocking too much vs. too little
# ---------------------------------------------------------------------------

def demo_mocking_tradeoffs():
    print("=" * 60)
    print("SECTION 11: Mocking tradeoffs")
    print("=" * 60)
    print("""
  TOO MUCH mocking:
    - Tests pass even when real integration is broken.
    - You are testing your mocks, not your code.
    - Refactoring internals breaks tests even though behavior is the same.

  TOO LITTLE mocking:
    - Tests are slow (real network, real disk).
    - Tests are flaky (depend on external state).
    - Hard to simulate edge cases (rate limits, outages).

  GUIDELINES:
    1. Mock at the boundary (HTTP client, DB connection, clock).
    2. Do NOT mock your own internal classes unless you have a good reason.
    3. Keep the mocked surface small -- if you need 20 mocks for one test,
       the code probably needs refactoring, not more mocks.
    4. Combine mock-based unit tests with a few integration tests that hit
       real services (run them less frequently, e.g., nightly).
    5. When in doubt, prefer dependency injection over monkey-patching.
       It makes the seam explicit and the test easier to read.
""")


# ---------------------------------------------------------------------------
# Run all demos
# ---------------------------------------------------------------------------

def main():
    print()
    print("GUIDE 05: Mocking and External Dependencies")
    print("=" * 60)
    print()
    demo_dependency_injection()
    demo_patch_location()
    demo_side_effect()
    demo_retry_logic()
    demo_mock_datetime()
    demo_timeout_handling()
    demo_spec()
    demo_call_inspection()
    demo_mock_open()
    demo_mocking_tradeoffs()
    print("All sections passed.")


if __name__ == "__main__":
    main()
