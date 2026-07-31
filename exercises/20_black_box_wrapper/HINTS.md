# Hints: Exercise 20 — Black Box Wrapper

## Hint 1

Probe a single encode/decode round trip and then repeat a batch call on the same
object.

## Hint 2

Inspect the trailing output delimiter, the `None` guard, and whether batch
behavior retains state between calls.

## Hint 3

Normalize the trailing separator, correct the inverted `None` condition, and
build batches through the wrapper's safe single-record operation.

The complete walkthrough is in
[solutions/20_solution.md](../../solutions/20_solution.md).
