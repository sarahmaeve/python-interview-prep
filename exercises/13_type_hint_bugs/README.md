# Exercise 13: Type Hint Bugs — Student Grade Processor

A data processing pipeline for student grade records. The module parses raw
student data, calculates GPAs, determines honor roll eligibility, merges
records, and formats transcripts.

## Why This Exercise Exists

Every bug in `grade_processor.py` is the kind that a type checker like
**mypy** would have caught automatically — but the code has no type hints,
so the bugs slipped through silently.

## Your Task

The file `grade_processor.py` contains **4 bugs**. Run the tests with:

```bash
python3 -m unittest test_grade_processor
```

All 12 tests should pass once every bug is fixed. Read the test file to
understand the expected behavior, find the bugs, and fix them.

## Bonus Challenge

After all tests pass, add type hints to every function signature and class
attribute in `grade_processor.py`. Then run:

```bash
pip install mypy
mypy grade_processor.py --strict
```

Your hints should be precise enough that mypy reports zero errors. This
guarantees that if anyone reintroduces a similar bug, the type checker will
flag it before the code ever runs.

## Hints

- Think about what a function returns in *every* code path, including edge cases.
- Pay attention to the types that raw/external data actually provides versus
  what the rest of the code assumes.
- When combining data structures, make sure the result is still the type
  downstream code expects.
- Consider whether a function should return an empty container or `None`.
