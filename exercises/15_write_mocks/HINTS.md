# Hints: Exercise 15 — Write Mocks

## Hint 1

For each TODO, identify the collaborator method the implementation calls and
the value or exception the test needs from it.

## Hint 2

Patch `payment_processor.urlopen`, configure chained return values from the
outside inward, and use iterable `side_effect` values for call-by-call results.

## Hint 3

The HTTP chain ends at
`mock_urlopen.return_value.read.return_value.decode.return_value`. Gateway
mocks should use `spec=PaymentGateway`.

The complete setups are in
[solutions/15_solution.md](../../solutions/15_solution.md).
