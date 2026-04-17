"""Tests for the decorators module.

Do NOT modify this file.  Fix the bugs in decorators.py until every
test passes.
"""

import unittest

from decorators import count_calls, log_calls, retry


# ---------------------------------------------------------------------------
# @log_calls — tests introspection survives the wrap.
# ---------------------------------------------------------------------------


class TestLogCallsPreservesIdentity(unittest.TestCase):

    def test_name_is_preserved(self):
        @log_calls
        def greet(name):
            """Say hi."""
            return f"hi {name}"

        self.assertEqual(greet.__name__, "greet")

    def test_docstring_is_preserved(self):
        @log_calls
        def greet(name):
            """Say hi."""
            return f"hi {name}"

        self.assertEqual(greet.__doc__, "Say hi.")

    def test_wrapped_attribute_is_set(self):
        """Decorated functions should expose __wrapped__ so callers
        (mock.patch, inspect.unwrap, …) can reach the original."""

        @log_calls
        def greet(name):
            return name

        self.assertTrue(hasattr(greet, "__wrapped__"))

    def test_function_still_works(self):
        @log_calls
        def add(a, b):
            return a + b

        self.assertEqual(add(2, 3), 5)


# ---------------------------------------------------------------------------
# @retry(n)
# ---------------------------------------------------------------------------


class TestRetry(unittest.TestCase):

    def test_succeeds_eventually(self):
        attempts = {"n": 0}

        @retry(3)
        def flaky():
            attempts["n"] += 1
            if attempts["n"] < 3:
                raise ConnectionError("still warming up")
            return "ok"

        self.assertEqual(flaky(), "ok")
        self.assertEqual(attempts["n"], 3)

    def test_raises_after_exhausting_attempts(self):
        @retry(2)
        def always_fails():
            raise ValueError("nope")

        with self.assertRaises(ValueError):
            always_fails()

    def test_preserves_function_name(self):
        """A function decorated with @retry must keep its own __name__
        and __doc__ — not become 'wrapper'."""

        @retry(3)
        def fetch_user(user_id):
            """Fetch a user record."""
            return {"id": user_id}

        self.assertEqual(fetch_user.__name__, "fetch_user")
        self.assertEqual(fetch_user.__doc__, "Fetch a user record.")


# ---------------------------------------------------------------------------
# @count_calls
# ---------------------------------------------------------------------------


class TestCountCalls(unittest.TestCase):

    def test_counts_a_single_function(self):
        @count_calls
        def hello():
            return "hi"

        for _ in range(4):
            hello()
        self.assertEqual(hello.count, 4)

    def test_each_function_has_its_own_counter(self):
        """Two functions decorated with @count_calls must not share
        state — calling one should not advance the other's count."""

        @count_calls
        def alpha():
            return "a"

        @count_calls
        def beta():
            return "b"

        alpha()
        alpha()
        alpha()
        beta()
        self.assertEqual(alpha.count, 3)
        self.assertEqual(beta.count, 1,
                         "beta's count must be independent of alpha's")


if __name__ == "__main__":
    unittest.main()
