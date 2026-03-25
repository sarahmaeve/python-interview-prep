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

## Hints

- You will need imports from the `typing` module. At minimum, consider
  `Optional`. On Python 3.9+ you can use built-in `list` and `dict` in
  annotations; on older versions you would need `List` and `Dict` from
  `typing`.
- `Optional[X]` is equivalent to `X | None` (Python 3.10+ union syntax).
  Either form is accepted by the tests.
- Remember to annotate `self` is **not** required — Python infers it.
- Every parameter (other than `self`) and every return type should be
  annotated.
