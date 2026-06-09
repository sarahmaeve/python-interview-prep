# Exercise 34: Stabilize a Flaky Test Suite

The implementation (`raffle.py`) is **correct** — do not modify it. The test suite is the patient: **4 of its tests are flaky**. Some fail every run, some only most runs, and *which* tests fail changes between runs. Your job is to make the suite deterministic.

**This exercise practices:** the single most common real-world CI complaint — "it passes locally / it failed again for no reason" — and the four classic causes: uncontrolled randomness, hash/iteration-order assumptions, dependence on the real clock, and shared mutable fixtures.

## How to run the tests

```bash
cd exercises/34_flaky_tests
python3 -m unittest test_raffle -v
```

**The bar:** the suite must pass **ten times in a row**:

```bash
for i in $(seq 10); do python3 -m unittest 2>&1 | tail -1; done
```

Run that loop *before* fixing anything and study the output. The failure count moves between runs — that variability is your diagnostic signal. A test that fails every time has a deterministic dependency on something outside the test (the clock, another test); a test that fails *sometimes* depends on something randomized per run (the RNG, the hash seed).

## Ground rules

- Do **not** modify `raffle.py` — it already provides every seam you need (an injectable `rng`, an explicit `at=` parameter on `is_open`).
- Do **not** weaken any test into meaninglessness (`assertTrue(True)` is not a fix). Each fixed test must still verify the behavior its docstring describes.
- Retries are not fixes. Neither is deleting the test.

## Bugs: 4 flaky tests

<details>
<summary>Hint 1 (gentle)</summary>

Categorize each failing test first: does it fail *always* or *sometimes*? The two always-failers depend on something deterministic-but-external (look at what the test touches besides the raffle). The two sometimes-failers depend on something randomized per process — Python randomizes more than `random`.
</details>

<details>
<summary>Hint 2 (moderate)</summary>

1. One test asserts which entrant wins an *unseeded* random draw. The constructor takes an `rng` argument for exactly this reason.
2. One test asserts the *order* of `list(some_set)`. String hashing is randomized per process (`PYTHONHASHSEED`), so set iteration order changes between runs.
3. One test builds a 5-millisecond entry window around `datetime.now()` and then sleeps for 20. `is_open` takes an `at=` parameter so tests never need the real clock.
4. One test class shares a mutable list at class level. One test appends to it; whether the other passes depends on execution order.
</details>

<details>
<summary>Hint 3 (specific)</summary>

1. **Unseeded draw**: inject a deterministic stand-in — `raffle = Raffle([...], rng=random.Random(99))` and assert that seed's known result, or better, a tiny stub class whose `choice()` returns `seq[0]` so the expectation is self-evident.
2. **Set order**: compare sets to sets — `self.assertEqual(raffle.entrant_pool(), {"alice", "bob", "carol"})` — or sort before comparing.
3. **Real clock**: use fixed literal datetimes for the window and pass `window.is_open(at=some_literal_datetime)`. Delete the sleep — a test that sleeps is both slow *and* wrong.
4. **Shared fixture**: replace the class-level `pool = [...]` with a `setUp` that builds a fresh list per test.

</details>

## Discussion Questions

Come back to these **after** the suite is green — they reference the fixes.

1. The hash-order flake only reproduces across *processes*, never within one run. How would you reproduce it on demand? (Look up `PYTHONHASHSEED`.)
2. Your CI retries failed jobs once, so this suite "passes" most days. What does that retry policy cost you in the long run?
3. A teammate proposes seeding `random` globally in `setUpClass`. What's better about injecting the RNG through the constructor instead?
4. Which of the four flakes could `pytest -p randomly` (test-order randomization) have caught on the first day?
