# Exercise 13: Type Hint Bugs — Student Grade Processor

A data processing pipeline for student grade records. The module parses raw
student data, calculates GPAs, determines honor roll eligibility, merges
records, and formats transcripts.

## Why This Exercise Exists

Every bug in `grade_processor.py` is the kind that a type checker like
**mypy** catches automatically. The intended contracts are already annotated;
each planted bug violates one of those contracts.

## Your Task

The file `grade_processor.py` contains **4 bugs**. Run both the tests and mypy:

```bash
python3 -m unittest test_grade_processor
mypy grade_processor.py --strict
```

Mypy should initially report four errors corresponding to the four behavioral
bugs. Do not weaken or remove the annotations; use them as machine-checked
specifications while tracing the failing tests. When finished, all 12 tests
should pass and mypy should report zero errors.

## Principle Primer

Annotations describe every path through a function, not only the happy path.
Use a type-checker error as a pointer to a contract mismatch, then confirm the
behavioral consequence with the tests. Do not silence the checker by weakening
an annotation when the implementation is what violates the intended contract.

If you get stuck, use [HINTS.md](HINTS.md).
