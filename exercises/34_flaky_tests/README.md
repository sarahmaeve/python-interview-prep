# Exercise 34: Stabilize a Flaky Test Suite

The implementation (`raffle.py`) is **correct** — do not modify it. The test suite is the patient: **4 of its tests are flaky**. Some fail every run, some only most runs, and *which* tests fail changes between runs. Your job is to make the suite deterministic.

**This exercise practices:** diagnosing the common CI complaint “it passes
locally / it failed again for no reason” by identifying inputs and state the
test does not control.

## How to run the tests

```bash
cd exercises/34_flaky_tests
python3 -m unittest test_raffle -v
```

**The bar:** the suite must pass **ten times in a row**:

```bash
for i in $(seq 10); do python3 -m unittest 2>&1 | tail -1; done
```

Run that loop *before* fixing anything and study the output. Variation between
runs is itself a diagnostic signal; a single run cannot characterize a flaky
suite.

## Ground rules

- Do **not** modify `raffle.py` — it already provides the seams the tests need.
- Do **not** weaken any test into meaninglessness (`assertTrue(True)` is not a fix). Each fixed test must still verify the behavior its docstring describes.
- Retries are not fixes. Neither is deleting the test.

## Principle Primer

A deterministic test controls every input that can change its outcome. Common
sources include time, randomness, environment, ordering, scheduling, and
mutable state. First classify whether a failure varies within one process,
across processes, or with test order; that observation narrows which input
remains uncontrolled.

There are 4 flaky tests. If you get stuck, use [HINTS.md](HINTS.md).

For broader techniques for classifying variable failures and controlling
hidden inputs, see
[Guide 15](../../guides/15_test_reliability_and_performance.py).

## Discussion Questions

Come back to these after the suite is green.

1. How can process-level randomization make repeated tests inside one process
   misleading?
2. Your CI retries failed jobs once, so this suite "passes" most days. What does that retry policy cost you in the long run?
3. What is better about injecting a source of randomness than changing global
   random state?
4. Which kinds of shared-fixture bugs can test-order randomization expose?
