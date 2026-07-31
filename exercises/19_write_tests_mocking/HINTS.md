# Hints: Exercise 19 — Write Tests with Mocking

## Hint 1

Classify dependencies as injected collaborators or names that must be patched.

## Hint 2

Pass `MagicMock` instances for `PaymentClient` and `InventoryClient`; patch the
network name used by `notify_customer`.

## Hint 3

Assert return values, collaborator arguments, and the absence of calls after
failure. The complete suite is in
[solutions/19_solution.md](../../solutions/19_solution.md).
