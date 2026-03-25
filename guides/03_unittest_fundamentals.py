"""
Guide 03 — unittest Fundamentals
=================================

This is a runnable test file that teaches unittest concepts through annotated
examples.  Run it directly:

    python guides/03_unittest_fundamentals.py

Or via the test runner:

    python -m unittest guides/03_unittest_fundamentals

Every test here either passes or is marked with @unittest.expectedFailure so
the overall run succeeds with an OK result.

TABLE OF CONTENTS
  1. Anatomy of a TestCase            (line ~35)
  2. Assertion methods deep-dive       (line ~95)
  3. setUp / tearDown and isolation    (line ~165)
  4. setUpClass / tearDownClass        (line ~215)
  5. Reading test output               (line ~250)
  6. Running tests & organization      (line ~285)
"""

import unittest

# ============================================================================
# 1. ANATOMY OF A TEST CASE
# ============================================================================
# A test case is a class that inherits from unittest.TestCase.
# The framework discovers test methods by looking for methods whose names
# start with "test".  Methods that DON'T start with "test" are just helpers.


class TestBasicAnatomy(unittest.TestCase):
    """Demonstrates the minimal structure of a test case."""

    # --- This IS a test (starts with "test") ---
    def test_addition(self):
        result = 1 + 1
        # assertEqual(a, b) fails if a != b.  The optional third argument
        # is a message that appears on failure — use it to save future-you
        # time when debugging.
        self.assertEqual(result, 2, "Basic addition should work")

    def test_string_upper(self):
        self.assertEqual("hello".upper(), "HELLO")

    # --- This is NOT a test (no "test" prefix) ---
    def helper_build_greeting(self, name):
        """Helpers keep tests readable.  The runner ignores this method."""
        return f"Hello, {name}!"

    def test_using_helper(self):
        greeting = self.helper_build_greeting("Ada")
        self.assertEqual(greeting, "Hello, Ada!")


# Naming conventions
# ------------------
# - Test files:    test_<module>.py  (or <module>_test.py)
# - Test classes:  Test<Thing>       (CamelCase, starts with "Test")
# - Test methods:  test_<behavior>   (snake_case, starts with "test")
#
# Good names describe WHAT is being tested and the EXPECTED outcome:
#   test_deposit_increases_balance
#   test_withdraw_raises_on_insufficient_funds
#
# Bad names are vague or implementation-focused:
#   test_1
#   test_method_calls_helper


# ============================================================================
# 2. ASSERTION METHODS DEEP-DIVE
# ============================================================================
# Why use self.assertEqual() instead of a bare `assert`?
#
#   1. Better failure messages — assertEqual tells you what the two values
#      actually were.  A bare `assert` only says "AssertionError".
#   2. The test runner counts assertions properly.
#   3. Specialised assertions (assertIn, assertRaises, ...) express INTENT,
#      making tests easier to read.
#
# Compare these two failure messages:
#   assert result == 42        →  AssertionError
#   self.assertEqual(result, 42) →  AssertionError: 17 != 42
#
# The second one tells you the actual value (17) instantly.


class TestAssertionMethods(unittest.TestCase):
    """Tour of the most common assertion methods."""

    # --- Equality ---
    def test_assert_equal(self):
        self.assertEqual(3 * 4, 12)  # Are they equal?

    def test_assert_not_equal(self):
        self.assertNotEqual(3 * 4, 13)  # Are they different?

    # --- Truthiness ---
    def test_assert_true_and_false(self):
        self.assertTrue(10 > 5)
        self.assertFalse(10 < 5)
        # Use these for boolean expressions.  For comparing two values,
        # assertEqual is better because the failure message shows both values.

    # --- Membership ---
    def test_assert_in(self):
        fruits = ["apple", "banana", "cherry"]
        self.assertIn("banana", fruits)      # Is it in the collection?
        self.assertNotIn("durian", fruits)   # Is it absent?

    # --- Approximate equality (great for floats) ---
    def test_assert_almost_equal(self):
        # Floating-point math is imprecise.  0.1 + 0.2 != 0.3 exactly.
        result = 0.1 + 0.2
        # This would FAIL:  self.assertEqual(result, 0.3)
        # Instead, check that they're close enough (7 decimal places default):
        self.assertAlmostEqual(result, 0.3, places=5)

    # --- Checking for exceptions ---
    def test_assert_raises(self):
        # Use assertRaises as a context manager to verify that specific
        # code raises the expected exception type.
        with self.assertRaises(ZeroDivisionError):
            _ = 1 / 0

        with self.assertRaises(ValueError):
            int("not_a_number")

    def test_assert_raises_with_message(self):
        # You can also inspect the exception message:
        with self.assertRaises(ValueError) as ctx:
            int("xyz")
        self.assertIn("invalid literal", str(ctx.exception))

    # --- Type and identity ---
    def test_assert_is_instance(self):
        self.assertIsInstance(42, int)
        self.assertIsInstance("hi", str)

    def test_assert_is_none(self):
        result = {}.get("missing_key")
        self.assertIsNone(result)           # Preferred over assertEqual(x, None)
        self.assertIsNotNone("something")

    # --- Container comparisons ---
    def test_assert_count_equal(self):
        # Checks that two sequences have the same elements regardless of order.
        # (It does NOT check that counts are equal, despite the name.)
        self.assertCountEqual([3, 1, 2], [1, 2, 3])


# ============================================================================
# 3. setUp / tearDown AND TEST ISOLATION
# ============================================================================
# KEY PRINCIPLE: Each test must be independent.
#
# If test_A modifies a list and test_B reads that list, the result depends on
# execution order — that's a flaky test waiting to happen.
#
# setUp() runs BEFORE every single test method.
# tearDown() runs AFTER every single test method (even if the test fails).
#
# Use them to create a fresh environment for each test.


class TestBankAccount(unittest.TestCase):
    """Demonstrates setUp/tearDown for test isolation."""

    def setUp(self):
        # This runs before EVERY test.  Each test gets its own account.
        # If one test modifies self.account, the next test won't see it
        # because setUp creates a brand-new dict.
        self.account = {"owner": "Alice", "balance": 100.0}

    def tearDown(self):
        # This runs after EVERY test, even if the test raised an exception.
        # Use it for cleanup: closing files, dropping temp database tables,
        # resetting global state, etc.
        # Here there's nothing to clean up, but we include it for illustration.
        self.account = None

    def test_deposit(self):
        self.account["balance"] += 50
        self.assertEqual(self.account["balance"], 150.0)

    def test_withdraw(self):
        # This test sees balance=100, NOT 150 — setUp gave us a fresh account.
        self.account["balance"] -= 30
        self.assertEqual(self.account["balance"], 70.0)

    def test_isolation_proof(self):
        # Regardless of which order these tests run, balance starts at 100.
        self.assertEqual(self.account["balance"], 100.0)


# WHY ISOLATION MATTERS (interview talking point)
# ------------------------------------------------
# Interviewers love asking: "Why did this test pass locally but fail in CI?"
# Answer #1 on the checklist: shared mutable state between tests.
# If tests share a list or dict at the class level and mutate it,
# execution order (which can vary) determines the outcome.


# ============================================================================
# 4. setUpClass / tearDownClass
# ============================================================================
# Sometimes setup is expensive (e.g., connecting to a database).  In that case,
# setUpClass runs ONCE for the entire class, not once per test.  Use it for
# read-only fixtures — things tests inspect but never modify.


class TestWithClassLevelSetup(unittest.TestCase):
    """Demonstrates class-level setup for expensive shared fixtures."""

    @classmethod
    def setUpClass(cls):
        # Runs ONCE before any tests in this class.  Use @classmethod.
        # Good for: loading a large test file, starting a test server, etc.
        cls.lookup_table = {chr(i + 65): i + 1 for i in range(26)}  # A=1..Z=26

    @classmethod
    def tearDownClass(cls):
        # Runs ONCE after all tests in this class finish.
        cls.lookup_table = None

    def test_lookup_a(self):
        self.assertEqual(self.lookup_table["A"], 1)

    def test_lookup_z(self):
        self.assertEqual(self.lookup_table["Z"], 26)


# ============================================================================
# 5. READING TEST OUTPUT
# ============================================================================
# When you run tests, each test prints a character:
#   .  = pass
#   F  = FAIL  (an assertion was wrong)
#   E  = ERROR (an unexpected exception was raised)
#   s  = skipped
#   x  = expected failure (test is known-broken, marked with @expectedFailure)
#
# FAIL vs ERROR:
#   FAIL  — your assertion didn't hold (assertEqual, assertTrue, etc.)
#           The code ran but produced the wrong answer.
#   ERROR — an exception was raised OUTSIDE an assertion.
#           Often a TypeError, NameError, or KeyError — the code crashed.
#
# Reading a traceback:
#   Start from the BOTTOM.  The last line is the exception type and message.
#   Then read upward to find which line of YOUR code triggered it.
#   Ignore frames inside unittest internals.


class TestReadingOutput(unittest.TestCase):
    """These intentionally-failing tests demonstrate FAIL vs ERROR.

    They are decorated with @expectedFailure so the overall run still
    reports OK.  Remove the decorator to see the raw failure output.
    """

    @unittest.expectedFailure
    def test_fail_example(self):
        # This produces a FAIL — the assertion does not hold.
        # In real output you'd see:
        #   FAIL: test_fail_example (...)
        #   AssertionError: 4 != 5
        self.assertEqual(2 + 2, 5, "This assertion is intentionally wrong")

    @unittest.expectedFailure
    def test_error_example(self):
        # This produces an ERROR — the code crashes before any assertion.
        # In real output you'd see:
        #   ERROR: test_error_example (...)
        #   KeyError: 'missing'
        data = {"name": "Alice"}
        _ = data["missing"]  # KeyError — code crashed, no assertion reached


# ============================================================================
# 6. RUNNING TESTS & ORGANISATION
# ============================================================================
#
# From the command line:
#
#   # Run every test in a file
#   python -m unittest guides/03_unittest_fundamentals.py
#
#   # Discover all test files in a directory (files matching test*.py)
#   python -m unittest discover -s tests -p "test*.py"
#
#   # Run one specific class
#   python -m unittest guides.03_unittest_fundamentals.TestBasicAnatomy
#
#   # Run one specific test method
#   python -m unittest guides.03_unittest_fundamentals.TestBasicAnatomy.test_addition
#
#   # Verbose mode — prints each test name and result
#   python -m unittest -v guides/03_unittest_fundamentals.py
#
# Organising tests:
#   - Mirror your source layout:   src/cart.py  →  tests/test_cart.py
#   - Group related tests in the same TestCase class.
#   - Keep each test short — ideally testing ONE behaviour.
#   - The "Arrange / Act / Assert" pattern keeps tests readable:
#       1. Arrange — set up inputs and expected outputs
#       2. Act     — call the code under test
#       3. Assert  — verify the result


class TestArrangeActAssert(unittest.TestCase):
    """Demonstrates the Arrange-Act-Assert pattern."""

    def test_sorted_names(self):
        # Arrange
        names = ["Charlie", "Alice", "Bob"]
        expected = ["Alice", "Bob", "Charlie"]

        # Act
        result = sorted(names)

        # Assert
        self.assertEqual(result, expected)

    def test_dict_merge(self):
        # Arrange
        defaults = {"color": "blue", "size": "M"}
        overrides = {"size": "L", "style": "bold"}

        # Act
        merged = {**defaults, **overrides}

        # Assert
        self.assertEqual(merged["size"], "L")       # override wins
        self.assertEqual(merged["color"], "blue")    # default kept
        self.assertIn("style", merged)               # new key added


# ============================================================================
# ENTRY POINT
# ============================================================================
# This lets you run the file directly:  python guides/03_unittest_fundamentals.py
# The verbosity=2 flag prints each test name and its result, which is more
# educational than the default dot-per-test output.

if __name__ == "__main__":
    unittest.main(verbosity=2)
