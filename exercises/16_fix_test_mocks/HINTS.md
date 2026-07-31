# Hints: Exercise 16 — Fix Test Mocks

## Hint 1

Compare each mock with the import and call performed by `inventory_service.py`.

## Hint 2

Check patch location, misspelled mock methods, the runtime type returned for
time, and stacked-decorator argument order.

## Hint 3

Patch the module-local lookup, add `spec=Database`, return a real `datetime`
where `.isoformat()` is called, and reverse the mismatched injected mocks.

The complete walkthrough is in
[solutions/16_solution.md](../../solutions/16_solution.md).
