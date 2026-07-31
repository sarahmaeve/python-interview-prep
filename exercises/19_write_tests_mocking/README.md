# Exercise 19: Write Tests with Mocking

## Context

The implementation in `order_service.py` is **correct** -- your job is not to fix
it but to **write a test suite from scratch**. The test file
`test_order_service.py` contains a skeleton with descriptive test method names
and docstrings, but every body is a failing TODO stub — the suite starts red
and goes green as you write real tests.

This exercises the skill of testing code that has external dependencies -- you
must decide what to mock, how to configure mocks, and what to assert.

## Prerequisites

Read **guide 05 (Mocking and External Dependencies)** before attempting this
exercise.

## Instructions

1. Read `order_service.py` -- understand the external dependencies.
2. Open `test_order_service.py` -- fill in each test method with mock setup
   **and** assertions.
3. Run tests until all pass:

```bash
python -m unittest test_order_service
```

## Principle Primer

Prefer dependency injection when the implementation already provides a seam;
reserve patching for dependencies resolved internally. A complete interaction
test usually checks both the returned value and the important collaborator
calls. Failure tests should establish which downstream interactions must not
occur after an earlier step fails.

If you get stuck, use [HINTS.md](HINTS.md).
