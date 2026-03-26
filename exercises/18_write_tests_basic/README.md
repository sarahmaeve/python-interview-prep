# Exercise 18: Write Tests from Scratch

## Format Change

Unlike other exercises, the code here is **correct**. There are no bugs to fix.
Instead, your job is to **write a complete test suite from scratch**.

The test file has a skeleton with test class names and docstrings describing what
each test should verify, but the test method bodies are empty (`pass`).

This exercises the skill of designing tests: choosing what to test, writing
meaningful assertions, and thinking about edge cases.

## Instructions

1. Read `string_calculator.py` -- it works correctly.
2. Open `test_string_calculator.py` -- fill in each test method with real assertions.
3. Run the tests:
   ```
   python3 -m unittest test_string_calculator -v
   ```
4. Keep going until all tests pass with meaningful assertions (not just `pass`).
5. **Challenge:** After filling in the provided tests, add 2-3 more tests for
   edge cases you think are missing.

## Key Concepts

- Writing `assertEqual`, `assertRaises`, and `assertIn` assertions
- Testing both normal behavior and error conditions
- Thinking about boundary conditions (e.g., exactly 1000 vs. 1001)
- Using `setUp` to avoid repetition across tests
