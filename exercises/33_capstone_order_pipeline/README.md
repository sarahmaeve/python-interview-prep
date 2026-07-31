# Exercise 33: Capstone — Multi-Module Order Pipeline

Every other exercise in this repo is a single file. Real interview codebases aren't. This capstone is a small order-processing app spread across **five modules**, with **5 bugs** — roughly one per module. Each bug is a pattern you've already met in an earlier exercise; the twist is that the *symptom* often shows up in a different module than the *cause*.

**This exercise practices:** navigating unfamiliar multi-module code, following data across module boundaries, and resisting the urge to "fix" the module a failing test happens to name.

## The modules

| Module | Role |
|---|---|
| `models.py` | `Product` (frozen dataclass) and `Order` (mutable lines + status) |
| `catalog.py` | Product lookup by SKU — case-insensitive by contract |
| `billing.py` | Decimal invoice math; pricing problems must raise, never mis-price |
| `fulfillment.py` | Orchestration: validate → charge → decrement stock → stamp status |
| `reporting.py` | Revenue and daily summaries over processed orders |

## How to run the tests

```bash
cd exercises/33_capstone_order_pipeline
python3 -m unittest test_order_pipeline -v
```

Your goal: edit the five modules until all 17 tests pass. Do **not** modify the test file.

## Suggested approach (this is the skill being practiced)

1. Run the suite and **list** the failures before touching anything.
2. For each failure, trace the data: which module produced the wrong value, and which module handed it bad input? An end-to-end failure in `reporting` can be caused two modules upstream.
3. Fix one bug at a time and re-run. Watch which *other* failures disappear with it — that tells you which symptoms shared a cause.

## Principle Primer

In a multi-module system, the failing assertion identifies where a bad value
became visible, not necessarily where it originated. Follow contracts across
module boundaries and preserve invariants at each handoff. This capstone
deliberately reuses earlier principles, so recognizing a familiar failure shape
is part of the exercise.

There are 5 bugs. If you get stuck, use [HINTS.md](HINTS.md).

## After you finish

- Which failing test did you chase into the *wrong* module first? What clue would have redirected you sooner?
- Pick two repaired bugs and explain which stronger representation or API
  contract would prevent that class of failure from recurring.
