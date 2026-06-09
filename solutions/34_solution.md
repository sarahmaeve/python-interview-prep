# Solution: Exercise 34 — Stabilize a Flaky Test Suite

## Diagnosis: always-fails vs sometimes-fails

Running the suite ten times gives failure counts that bounce around (3, 4, 3, 4...). Splitting the failures by *consistency* is the key move:

| Test | Fails | Root cause |
|---|---|---|
| `test_entry_during_window_is_accepted` | always | real clock: 5 ms window, 20 ms sleep |
| `test_pool_starts_with_three_entrants` | always | class-level list mutated by the sibling test, which sorts (and runs) first |
| `test_draw_winner_returns_the_expected_entrant` | ~3 runs in 4 | unseeded RNG: 1-in-4 chance the draw is "alice" |
| `test_pool_contains_each_entrant_once` | most runs | `PYTHONHASHSEED` randomizes string hashing per process, so set iteration order differs between runs |

Always-failing under a "flaky" banner means the dependency is deterministic but external (the clock, sibling-test order). Sometimes-failing means something is randomized per process (the RNG, the hash seed).

## The Fixes

**1. Unseeded randomness → control the RNG through the existing seam.**

```python
class FirstChoice:
    def choice(self, seq):
        return seq[0]

raffle = Raffle(["alice", "bob", "carol", "dan"], rng=FirstChoice())
self.assertEqual(raffle.draw_winner(), "alice")
```

A seeded `random.Random(99)` also works, but then the expected value is whatever that seed happens to produce — a frozen magic value. The stub makes the expectation self-evident. (The suite's other tests show the complementary techniques: assert *properties* of random output, and use matching seeds to test reproducibility.)

**2. Set-order assumption → compare sets, not list-of-set.**

```python
self.assertEqual(raffle.entrant_pool(), {"alice", "bob", "carol"})
```

`list(a_set_of_strings)` has no stable order across processes because string hashing is salted (`PYTHONHASHSEED`). If order ever *matters*, sort first; if it doesn't, compare unordered collections directly. `assertCountEqual` is the third option when duplicates matter.

**3. Real-clock dependence → fixed datetimes through the existing seam.**

```python
window = EntryWindow(datetime(2026, 6, 1, 9, 0), datetime(2026, 6, 1, 17, 0))
self.assertTrue(window.is_open(at=datetime(2026, 6, 1, 12, 0)))
```

The sleep disappears along with the flake — a test that sleeps is slow *and* still racy. `is_open(at=...)` exists precisely so tests never consult the wall clock; production callers omit `at` and get `datetime.now()`.

**4. Shared mutable fixture → fresh state in `setUp`.**

```python
def setUp(self):
    self.pool = ["alice", "bob", "carol"]
```

The class-level list was shared by both tests, and the mutating test happens to sort (and therefore run) first. Locally that's a *deterministic* failure; in CI with test-order randomization or parallel sharding it becomes a classic heisenbug. Guide 03 §3 is exactly this rule: fresh state per test, always.

## Why This Matters

- Flaky tests are more expensive than failing tests: a failing test gets fixed, a flaky one gets retried until the team stops believing red builds. The standard interview question — "a test fails 10% of the time, how do you debug it?" — starts with the classification above: does the failure rate look like a probability (randomness) or a race (timing/order)?
- Every fix here used a seam the code already had. That's the usual shape in real codebases: the testability hooks exist; flaky tests are tests that bypassed them.
- To reproduce hash-order flakes on demand: `PYTHONHASHSEED=0 python -m unittest` vs `PYTHONHASHSEED=1 ...`. To surface order-dependence on demand: randomize test order (pytest's `-p randomly` plugin, or run suspect tests in isolation).

## Discussion

- Retry-on-failure CI policies convert flakes from "loud" to "slow and invisible": each flake costs a full re-run and erodes trust in red. Budget the retry count at 0 for unit suites; stabilize instead.
- Seeding the global `random` module in `setUpClass` works but leaks: it mutates process-global state every other test shares, and it breaks under parallel test runners. Constructor injection scopes the determinism to the object under test.
- The properties-vs-examples split in this suite is worth internalizing: for genuinely random behavior, assert invariants (winner ∈ entrants, no repeats in a unique draw) and use seeds/stubs only when you must pin an exact value.
