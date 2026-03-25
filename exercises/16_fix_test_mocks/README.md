# Exercise 16: Fix the Test Mocks

## Context

This exercise flips the script -- the implementation works correctly, but the
test file has bugs in how mocks are set up. Each failing test fails because of a
mocking mistake, not a code mistake. Your job is to fix the tests.

This exercises the skill of diagnosing mock-related test failures: wrong patch
targets, missing spec constraints, incorrect return value types, swapped
decorator arguments, and more.

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

## Hints (try without these first)

<details>
<summary>Hint 1</summary>
When a module does <code>from X import Y</code>, patching <code>X.Y</code>
does not affect the module's local reference. You must patch where the name
is looked up.
</details>

<details>
<summary>Hint 2</summary>
<code>MagicMock()</code> without <code>spec=</code> will silently create any
attribute you access, even misspelled ones. Adding a spec catches typos.
</details>

<details>
<summary>Hint 3</summary>
If the real code calls <code>.isoformat()</code> on a return value, your mock
must return an object that actually has that method -- not a plain string.
</details>

<details>
<summary>Hint 4</summary>
When stacking <code>@patch</code> decorators, the bottom decorator's mock
becomes the first positional argument. If you mix up the order, you configure
the wrong mock.
</details>
