"""
Guide 08 — Observability & Systems Thinking
=============================================

This guide covers making code behavior visible (logging, instrumentation)
and understanding how code interacts with its deployment environment
(configuration, timeouts, retries, CI/CD).

Run this file:
    python guides/08_observability_and_systems.py

TABLE OF CONTENTS
  1. Python logging basics              (line ~40)
  2. Log levels and when to use them    (line ~100)
  3. Handlers, formatters, hierarchy    (line ~170)
  4. Instrumenting code for debugging   (line ~250)
  5. assertLogs in unittest             (line ~320)
  6. Environment-aware configuration    (line ~380)
  7. Timeout and retry patterns         (line ~420)
  8. CI/CD considerations for tests     (line ~480)
"""

import io
import json
import logging
import os
import time
import unittest
from unittest.mock import patch
from urllib.error import URLError


# ============================================================================
# 1. PYTHON LOGGING BASICS
# ============================================================================
#
# Why not just use print()?
#
# print() is fine for quick one-off debugging, but it has real limitations:
#   - No severity levels: you can't distinguish "informational" from "error"
#   - No off switch: you must manually delete/comment out every print()
#   - No routing: output always goes to stdout
#   - No standard format: every developer formats differently
#
# Python's logging module solves all of these. It's in the standard library,
# so there's nothing to install.

def demo_logging_basics():
    """Basic logging usage."""
    print("\n" + "=" * 60)
    print("1. LOGGING BASICS")
    print("=" * 60)

    # The fundamental pattern: get a named logger, then call methods on it.
    # By convention, use __name__ so the logger name matches the module.
    logger = logging.getLogger("demo.basics")

    # Log at different severity levels:
    logger.debug("This is a debug message — detailed diagnostic info")
    logger.info("This is an info message — confirmation things work")
    logger.warning("This is a warning — something unexpected happened")
    logger.error("This is an error — something failed")
    logger.critical("This is critical — the program may not continue")

    # By default, only WARNING and above are shown. That's why debug and
    # info messages above won't appear unless you configure the logger.

    # To see all levels, you can set the level on the root logger:
    logging.basicConfig(level=logging.DEBUG, force=True)
    # force=True reconfigures even if basicConfig was already called.

    logger.debug("Now this debug message IS visible")
    logger.info("And so is this info message")

    print("\n  Key takeaway: logging.getLogger(__name__) + logger.warning()")
    print("  is the standard pattern. You'll see it everywhere in production code.")


# ============================================================================
# 2. LOG LEVELS AND WHEN TO USE THEM
# ============================================================================
#
# Level        Value   When to use
# ─────────    ─────   ──────────────────────────────────────────────────
# DEBUG        10      Detailed diagnostic info. Useful during development.
#                      Example: "Processing record id=42, fields=['a','b']"
#
# INFO         20      Confirmation that things are working as expected.
#                      Example: "Connected to database", "Processed 100 records"
#
# WARNING      30      Something unexpected that the code handled.
#                      Example: "Retrying request (attempt 2 of 3)"
#                      Example: "Invalid record skipped: missing 'id' field"
#
# ERROR        40      Something failed — a specific operation could not complete.
#                      Example: "Failed to fetch URL: timeout after 30s"
#
# CRITICAL     50      The program itself may not be able to continue.
#                      Example: "Database connection pool exhausted"
#
# Rule of thumb:
#   - WARNING = "something unexpected that the code handled gracefully"
#   - ERROR   = "something the code could NOT handle"
#   - DEBUG   = "details only a developer debugging this specific code needs"

def demo_log_levels():
    """Show how log level filtering works."""
    print("\n" + "=" * 60)
    print("2. LOG LEVELS")
    print("=" * 60)

    logger = logging.getLogger("demo.levels")

    # Set the logger to only show WARNING and above:
    logger.setLevel(logging.WARNING)

    messages = [
        (logging.DEBUG, "detailed record processing info"),
        (logging.INFO, "successfully processed batch"),
        (logging.WARNING, "skipped invalid record id=99"),
        (logging.ERROR, "failed to write output file"),
    ]

    print("\n  With level=WARNING, which messages get through?")
    for level, msg in messages:
        level_name = logging.getLevelName(level)
        passes = level >= logging.WARNING
        symbol = "VISIBLE" if passes else "filtered out"
        print(f"    {level_name:8s}: {msg!r:45s} -> {symbol}")

    # Reset for later demos
    logger.setLevel(logging.DEBUG)

    print("\n  Key takeaway: set the threshold, and everything below it")
    print("  is silently filtered. No code changes needed to silence debug output.")


# ============================================================================
# 3. HANDLERS, FORMATTERS, AND LOGGER HIERARCHY
# ============================================================================
#
# A logger by itself doesn't decide WHERE or HOW to write messages.
# That's the job of handlers and formatters:
#
#   Logger  --->  Handler  --->  Formatter  --->  output
#                 (where)        (how)
#
# Common handlers:
#   StreamHandler   — writes to sys.stderr (or any stream)
#   FileHandler     — writes to a file
#
# You can attach multiple handlers to one logger (e.g., warnings to stderr,
# errors to a file).
#
# Logger hierarchy:
#   Loggers form a tree based on their dotted names.
#   "app" is parent of "app.db" which is parent of "app.db.queries".
#   By default, messages propagate UP the tree — a warning logged to
#   "app.db.queries" will also be handled by "app.db" and "app".

def demo_handlers_and_formatters():
    """Show handler and formatter configuration."""
    print("\n" + "=" * 60)
    print("3. HANDLERS, FORMATTERS, HIERARCHY")
    print("=" * 60)

    # Create a logger with a custom handler and formatter.
    # We use a StringIO stream so we can capture the output for display.
    stream = io.StringIO()
    handler = logging.StreamHandler(stream)

    # Formatters control the output format:
    formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%H:%M:%S"
    )
    handler.setFormatter(formatter)

    logger = logging.getLogger("demo.formatted")
    # Remove any existing handlers to avoid duplicate output
    logger.handlers.clear()
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)
    # Prevent propagation to root logger for this demo
    logger.propagate = False

    logger.info("Server started on port 8080")
    logger.warning("Request took 2.3s (threshold: 1.0s)")
    logger.error("Connection refused: database unreachable")

    output = stream.getvalue()
    print("\n  Formatted output:")
    for line in output.strip().split("\n"):
        print(f"    {line}")

    # --- Logger hierarchy demo ---
    print("\n  Logger hierarchy:")
    print("    'app' is parent of 'app.db' is parent of 'app.db.queries'")

    parent_stream = io.StringIO()
    parent_handler = logging.StreamHandler(parent_stream)
    parent_handler.setFormatter(logging.Formatter("  [%(name)s] %(message)s"))

    parent_logger = logging.getLogger("demo.app")
    parent_logger.handlers.clear()
    parent_logger.addHandler(parent_handler)
    parent_logger.setLevel(logging.DEBUG)
    parent_logger.propagate = False

    child_logger = logging.getLogger("demo.app.database")
    child_logger.handlers.clear()
    # No handler on child — it propagates to parent
    child_logger.setLevel(logging.DEBUG)

    child_logger.warning("slow query detected")

    parent_output = parent_stream.getvalue()
    print(f"\n    Child logger 'demo.app.database' logged a warning.")
    print(f"    Parent logger 'demo.app' received it via propagation:")
    print(f"      {parent_output.strip()}")

    # Clean up
    logger.handlers.clear()
    parent_logger.handlers.clear()

    print("\n  Key takeaway: handler = where (stream, file), formatter = how (format).")
    print("  Child loggers propagate to parents. Configure at the top, log anywhere.")


# ============================================================================
# 4. INSTRUMENTING CODE FOR DEBUGGING
# ============================================================================
#
# When a function produces unexpected results, you need to see WHAT it's
# doing at each step. This is the same systematic approach as Guide 04's
# debugging workflow, but using logging instead of print statements.
#
# Instrument at three points:
#   1. Entry:    log the arguments (DEBUG level)
#   2. Decision: log which branch was taken (DEBUG or INFO)
#   3. Exit:     log the return value (DEBUG level)

def demo_instrumenting_code():
    """Show before/after of adding logging to a function."""
    print("\n" + "=" * 60)
    print("4. INSTRUMENTING CODE FOR DEBUGGING")
    print("=" * 60)

    # --- BEFORE: a function that silently returns wrong results ---
    print("\n  BEFORE (no logging — wrong results are invisible):")
    print("""
    def calculate_discount(price, customer_type, quantity):
        if customer_type == "wholesale":
            discount = 0.20
        elif customer_type == "preferred":
            discount = 0.10
        else:
            discount = 0
        if quantity > 100:
            discount += 0.05
        return price * discount  # BUG: should be price * (1 - discount)
    """)

    # --- AFTER: instrumented with logging ---
    logger = logging.getLogger("demo.discount")
    logger.handlers.clear()
    stream = io.StringIO()
    handler = logging.StreamHandler(stream)
    handler.setFormatter(logging.Formatter("    %(levelname)s: %(message)s"))
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)
    logger.propagate = False

    def calculate_discount(price, customer_type, quantity):
        logger.debug(
            "calculate_discount(price=%s, customer_type=%r, quantity=%s)",
            price, customer_type, quantity
        )

        if customer_type == "wholesale":
            discount = 0.20
            logger.debug("wholesale discount: %.0f%%", discount * 100)
        elif customer_type == "preferred":
            discount = 0.10
            logger.debug("preferred discount: %.0f%%", discount * 100)
        else:
            discount = 0
            logger.debug("no customer discount")

        if quantity > 100:
            discount += 0.05
            logger.debug("quantity bonus applied, total discount: %.0f%%", discount * 100)

        result = price * discount  # BUG: should be price * (1 - discount)
        logger.debug("returning %s", result)
        return result

    result = calculate_discount(100.0, "wholesale", 150)
    output = stream.getvalue()
    print("  AFTER (with logging):")
    print(output)
    print(f"    Result: {result}")
    print(f"    Expected: 75.0 (100 - 25% discount)")
    print(f"    Actual:   {result} <- the log shows price * discount, not price * (1-discount)")

    logger.handlers.clear()

    print("\n  Key takeaway: logging at entry/decision/exit points makes the")
    print("  exact moment where behavior diverges from expectation visible.")


# ============================================================================
# 5. assertLogs IN UNITTEST
# ============================================================================
#
# When your code SHOULD log warnings or errors, you can test for it.
# unittest provides assertLogs as a context manager:
#
#   with self.assertLogs("logger_name", level="WARNING") as cm:
#       do_something_that_should_warn()
#   self.assertIn("expected message", cm.output[0])
#
# cm.output is a list of strings like "WARNING:logger_name:the message"
#
# If no log messages are emitted at the specified level or above,
# assertLogs raises AssertionError — meaning the test fails.

def demo_assert_logs():
    """Show how to test logging output with assertLogs."""
    print("\n" + "=" * 60)
    print("5. assertLogs IN UNITTEST")
    print("=" * 60)

    # A function that logs a warning for invalid input:
    proc_logger = logging.getLogger("processor")

    def process_value(value):
        if not isinstance(value, (int, float)):
            proc_logger.warning("Invalid value type: %s", type(value).__name__)
            return None
        return value * 2

    # A test class that verifies the warning is emitted:
    class TestProcessValue(unittest.TestCase):
        def test_warns_on_invalid_type(self):
            """Verify that a WARNING is logged for non-numeric input."""
            with self.assertLogs("processor", level="WARNING") as cm:
                result = process_value("not a number")

            self.assertIsNone(result)
            # cm.output contains formatted strings like:
            # ["WARNING:processor:Invalid value type: str"]
            self.assertIn("Invalid value type: str", cm.output[0])

        def test_no_warning_on_valid_input(self):
            """Verify that valid input does NOT produce a warning.

            assertNoLogs is available in Python 3.10+.
            For earlier versions, verify assertLogs raises AssertionError.
            """
            # Python 3.10+ approach:
            # with self.assertNoLogs("processor", level="WARNING"):
            #     process_value(42)

            # Compatible approach for Python 3.8+:
            with self.assertRaises(AssertionError):
                with self.assertLogs("processor", level="WARNING"):
                    process_value(42)

    # Run the tests programmatically for the demo
    suite = unittest.TestLoader().loadTestsFromTestCase(TestProcessValue)
    runner = unittest.TextTestRunner(verbosity=0, stream=io.StringIO())
    result = runner.run(suite)

    print(f"\n  Ran {result.testsRun} tests: ", end="")
    if result.wasSuccessful():
        print("all passed")
    else:
        print(f"{len(result.failures)} failures")

    print("""
  Usage pattern:

    with self.assertLogs("logger_name", level="WARNING") as cm:
        function_that_should_warn()

    self.assertIn("expected text", cm.output[0])

  cm.output format: ["LEVEL:logger_name:message", ...]

  Key takeaway: assertLogs lets you verify that your code emits the right
  log messages at the right level. The test FAILS if no logs are emitted.""")


# ============================================================================
# 6. ENVIRONMENT-AWARE CONFIGURATION
# ============================================================================
#
# Production code often reads configuration from environment variables.
# The standard pattern:
#
#   base_url = os.environ.get("API_BASE_URL", "http://localhost:8080")
#
# There's a subtle trap with default arguments:

def demo_environment_config():
    """Show the import-time evaluation trap with default arguments."""
    print("\n" + "=" * 60)
    print("6. ENVIRONMENT-AWARE CONFIGURATION")
    print("=" * 60)

    # --- THE TRAP ---
    # If get_config() is a default argument, it's evaluated ONCE at import
    # time. If the environment changes later (common in tests), the config
    # is stale.

    print("\n  THE TRAP — default argument evaluated at import time:")
    print("""
    def get_config():
        return {"url": os.environ.get("API_URL", "http://localhost")}

    class Client:
        def __init__(self, config=get_config()):  # <-- evaluated ONCE
            self.config = config
    """)
    print("  If a test sets os.environ['API_URL'] = 'http://test-server',")
    print("  Client() still gets the old value from import time!")

    # --- THE FIX ---
    print("\n  THE FIX — use None sentinel, call inside the method body:")
    print("""
    class Client:
        def __init__(self, config=None):
            self.config = config if config is not None else get_config()
    """)
    print("  Now get_config() runs at call time, picking up current env vars.")
    print("  Tests can also inject config directly: Client(config={...})")

    # Demonstrate the difference
    os.environ["DEMO_URL"] = "http://original"

    def get_config_eager():
        return {"url": os.environ.get("DEMO_URL", "default")}

    captured_config = get_config_eager()  # captured NOW

    os.environ["DEMO_URL"] = "http://changed"

    fresh_config = get_config_eager()  # called NOW, sees the change

    print(f"\n  Captured at import time: {captured_config['url']}")
    print(f"  Called fresh:            {fresh_config['url']}")

    # Clean up
    del os.environ["DEMO_URL"]

    print("\n  Key takeaway: never use a function call as a default argument")
    print("  if the function reads external state (env vars, files, time).")


# ============================================================================
# 7. TIMEOUT AND RETRY PATTERNS
# ============================================================================
#
# When code makes network requests, two things can go wrong:
#   1. The request hangs forever (no timeout set)
#   2. A transient error occurs (network blip, server restart)
#
# Always set timeouts. Consider retries for transient failures.

def demo_retry_with_logging():
    """Show a retry loop with logging at each attempt."""
    print("\n" + "=" * 60)
    print("7. TIMEOUT AND RETRY PATTERNS")
    print("=" * 60)

    print("""
  Always pass a timeout to urlopen:

    from urllib.request import urlopen
    response = urlopen(url, timeout=10)   # seconds

  Without timeout=, the request can hang indefinitely. This is especially
  dangerous in CI, where a stuck request can cause the entire build to
  time out with no useful error message.
    """)

    logger = logging.getLogger("demo.retry")
    logger.handlers.clear()
    stream = io.StringIO()
    handler = logging.StreamHandler(stream)
    handler.setFormatter(logging.Formatter("    %(levelname)s: %(message)s"))
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)
    logger.propagate = False

    def fetch_with_retry(url, max_retries=3, timeout=10):
        """Fetch a URL with retries and exponential backoff."""
        for attempt in range(1, max_retries + 1):
            try:
                logger.info("Attempt %d/%d: %s", attempt, max_retries, url)
                # In real code: urlopen(url, timeout=timeout)
                # For this demo, we simulate failure then success:
                if attempt < 3:
                    raise URLError("Connection refused")
                return {"status": "ok"}
            except URLError as e:
                logger.warning(
                    "Attempt %d failed: %s", attempt, e.reason
                )
                if attempt == max_retries:
                    logger.error(
                        "All %d attempts failed for %s", max_retries, url
                    )
                    raise
                # Exponential backoff: 1s, 2s, 4s, ...
                wait = 2 ** (attempt - 1)
                logger.debug("Waiting %ds before retry", wait)
                # time.sleep(wait)  # would actually sleep in real code

    result = fetch_with_retry("http://example.com/api/data")

    output = stream.getvalue()
    print("  Retry loop with logging:")
    print(output)
    print(f"  Final result: {result}")

    logger.handlers.clear()

    print("""
  When to retry vs. when NOT to retry:

    RETRY:        transient errors — connection refused, timeout, 503
    DON'T RETRY:  client errors — 400 Bad Request, 401 Unauthorized, 404
                  (these won't succeed on retry)

  In tests, mock time.sleep so your tests run fast:

    @patch("my_module.time.sleep")
    def test_retry(self, mock_sleep):
        ...  # test runs instantly, no actual sleeping
    """)


# ============================================================================
# 8. CI/CD CONSIDERATIONS FOR TESTS
# ============================================================================
#
# This section is discussion material — no runnable code.
# These are the kinds of questions that come up in systems-level interviews.

def print_ci_considerations():
    """Print discussion points about CI/CD and test behavior."""
    print("\n" + "=" * 60)
    print("8. CI/CD CONSIDERATIONS FOR TESTS")
    print("=" * 60)
    print("""
  Tests that pass locally but fail in CI (or vice versa) are a common
  source of frustration. Here are the main causes and how to prevent them.

  ENVIRONMENT DIFFERENCES
  ───────────────────────
  - Environment variables may differ (API_URL, DATABASE_HOST, CI=true)
  - Filesystem paths may differ (/home/user vs /runner/workspace)
  - Network access may be restricted (no outbound HTTP in CI)
  - Timezone and locale may differ

  Prevention: never hard-code paths or URLs. Read from config. Use
  dependency injection so tests can provide their own values.

  TEST ISOLATION
  ──────────────
  - Tests that modify global state (os.environ, module-level variables,
    class attributes) can affect other tests when run in a different order.
  - CI may run tests in parallel or in a different order than your local run.

  Prevention: use setUp/tearDown to save and restore global state.
  Use unittest.mock.patch as a context manager — it auto-restores.

  TIMING AND FLAKINESS
  ────────────────────
  - Tests that depend on real time (time.time(), sleep, timeouts) may
    be flaky if the CI machine is slower or busier.
  - Tests that depend on network calls may fail if the service is down.

  Prevention: mock time-dependent functions. Mock network calls.
  Use dependency injection for clocks and HTTP clients.

  THE 'CI' ENVIRONMENT VARIABLE
  ─────────────────────────────
  Many CI systems (GitHub Actions, GitLab CI, Travis, Jenkins) set
  CI=true in the environment. Code can check for this:

    is_ci = os.environ.get("CI", "").lower() in ("true", "1")

  Use cases:
  - Skip tests that require network access in CI
  - Use shorter timeouts in CI
  - Disable interactive prompts

  But be cautious: if your code behaves DIFFERENTLY in CI, you're no
  longer testing the same code path that runs in production.

  DISCUSSION QUESTIONS (for interview practice)
  ──────────────────────────────────────────────
  1. A test passes locally but fails in CI. What are the first three
     things you would check?

  2. Your test suite takes 10 minutes in CI. What strategies can you
     use to speed it up without reducing coverage?

  3. A flaky test fails about 10% of the time. How do you diagnose
     whether it's a timing issue, ordering issue, or real bug?

  4. Your code retries failed HTTP requests 3 times with 2-second
     backoff. The CI build has a 5-minute timeout. What could go wrong?

  5. A colleague suggests mocking all external calls in tests. Another
     suggests running integration tests against a real service. What
     are the trade-offs of each approach?
    """)


# ============================================================================
# MAIN
# ============================================================================

def main():
    demo_logging_basics()
    demo_log_levels()
    demo_handlers_and_formatters()
    demo_instrumenting_code()
    demo_assert_logs()
    demo_environment_config()
    demo_retry_with_logging()
    print_ci_considerations()

    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print("""
  Core patterns covered:
    1. logging.getLogger(__name__)  — the standard way to log
    2. WARNING for "handled it", ERROR for "couldn't handle it"
    3. Handler + Formatter = where + how
    4. Instrument at entry, decision, exit
    5. assertLogs("name", level="WARNING") — test your logging
    6. config=None sentinel — avoid import-time evaluation
    7. Always pass timeout= to network calls
    8. Think about what differs between local and CI

  Next: Try Exercise 21 (Observability & Logging) to practice
  instrumenting code and testing log output with assertLogs.
    """)


if __name__ == "__main__":
    main()
