# Exercise 16: Fix the Test Mocks

## Context

This exercise flips the script -- the implementation works correctly, but the
test file has bugs in how mocks are set up. Each failing test fails because of a
mocking mistake, not a code mistake. Your job is to fix the tests.

This exercises the skill of diagnosing mock-related test failures by comparing
the test double's behavior with the real dependency contract and the name
binding used by the implementation.

## Instructions

1. Read `inventory_service.py` -- it is correct. Do NOT modify it.
2. Run the tests: `python -m unittest test_inventory_service -v`
3. You should see 6 tests pass and 4 tests fail.
4. Read each failing test, understand what it is trying to verify, and fix the
   mock setup so the test passes.
5. There are 4 bugs to find in the test file. All of them are in how mocks are
   configured, not in what behavior is being verified.

## Running the tests

```bash
cd exercises/16_fix_test_mocks
python -m unittest test_inventory_service -v
```

## Principle Primer

Mocks must be faithful in two directions: they must replace the name the code
actually resolves, and their return values must support the operations the real
objects support. A `spec` catches misspelled methods that an unrestricted mock
would invent. With stacked patch decorators, remember that decorators apply
inside-out, which determines injected argument order.

If you get stuck, use [HINTS.md](HINTS.md).
