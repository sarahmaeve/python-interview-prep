# Exercise 19: Write Tests with Mocking

## Context

The implementation in `order_service.py` is **correct** -- your job is not to fix
it but to **write a test suite from scratch**. The test file
`test_order_service.py` contains a skeleton with descriptive test method names
and docstrings, but every body is just `pass`.

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

## Hints

- The `OrderService` uses dependency injection for `PaymentClient` and
  `InventoryClient`. You can pass `MagicMock()` instances directly to the
  constructor -- no `@patch` needed for those.
- `notify_customer` calls `urllib.request.urlopen` -- you **will** need
  `@patch` for that.
- Think about what each test needs to verify: return values, side effects,
  **and** that the right methods were called with the right arguments.
