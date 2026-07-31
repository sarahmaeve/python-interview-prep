# Exercise 14: Add Type Hints — Task Registry

This exercise is different from the others. The code in `task_registry.py` is
**completely correct** — there are no bugs to fix. Instead, it is missing all
type annotations. Your job is to add proper type hints to every function and
method signature.

## Your Task

1. Read `task_registry.py` and understand what each function/method does.
   The docstrings describe the expected types.
2. Add type hints to **all** function parameters and **all** return types.
3. Run the tests:

```bash
python3 -m unittest test_task_registry
```

The behavioral tests (that the code works) should already pass. The annotation
tests will only pass once you have added correct type hints.

4. **Bonus:** run `mypy task_registry.py` to verify your hints are consistent.

## Principle Primer

Annotations record the values callers may provide and the values each function
returns. Prefer the narrowest honest type and represent optionality explicitly:
`X | None` means the absence of a value is part of the contract. Container
annotations describe both the container and its element types.

If you get stuck, use [HINTS.md](HINTS.md).
