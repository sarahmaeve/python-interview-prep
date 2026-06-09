# Solution: Exercise 36 — Performance Tuning

## Bugs Found

All three are accidental O(n²) — one full scan or shift hiding inside a loop:

1. **`unique_visitors`** — `visitor not in seen` where `seen` is a **list**: every membership check scans everything seen so far. 25k visits ⇒ ~312 million comparisons.
2. **`running_averages`** — `sum(latencies[:i+1])` recomputes the entire prefix sum from scratch each iteration (and the slice allocates a fresh list every time). 30k latencies ⇒ ~450 million additions.
3. **`newest_first`** — `ordered.insert(0, entry)` shifts every existing element one slot right on each insert. 140k entries ⇒ ~9.8 billion element moves.

## Diagnosis Process

- The failing perf tests print the measured time (~5s against a 1s budget) — a 5× overshoot with a 100× margin built in says *algorithm*, not machine.
- `python3 -m cProfile -s cumtime -m unittest test_log_metrics` attributes nearly all of the time to the three functions themselves (not to I/O, not to the test harness).
- The doubling experiment confirms the class: time `unique_visitors` at n=5000 and n=10000 — it gets ~4× slower, the signature of O(n²). Linear code gets ~2× slower.

## The Fixes

```python
def unique_visitors(visits):
    seen = set()
    ordered = []
    for visitor in visits:
        if visitor not in seen:      # set membership: O(1)
            seen.add(visitor)
            ordered.append(visitor)
    return ordered


def running_averages(latencies):
    averages = []
    total = 0.0
    for i, latency in enumerate(latencies):
        total += latency             # each value added exactly once
        averages.append(total / (i + 1))
    return averages


def newest_first(entries):
    return list(reversed(entries))   # one pass; or append + .reverse()
```

Measured on the reference machine: the unfixed suite takes ~15 s; the fixed suite runs all nine tests in ~0.03 s — each workload lands more than 100× inside its budget.

## Why This Matters

- **`in` against a list is the most common quadratic bug in Python code review.** It reads identically to the set version and is invisible at small n — it ships, then the data grows. The rule: if you test membership in a loop, the container should be a set or dict.
- **"Recompute from scratch each iteration" is the second most common.** Any time iteration i can reuse iteration i−1's answer (running sums, maxima, counts), carrying an accumulator turns O(n²) into O(n).
- **List operations have asymmetric costs.** `append`/`pop()` at the END are O(1); `insert(0, ...)`/`pop(0)` at the FRONT are O(n) because everything shifts. When you need both ends cheap, that's `collections.deque` (O(1) `appendleft`) — at the cost of O(n) random access.
- **Complexity beats constants.** None of these fixes micro-optimize anything; they change the *shape* of the work. That's the order to think in: algorithm first, profiler-guided micro-tuning a distant second.

## Discussion

- `list(dict.fromkeys(visits))` is the idiomatic one-liner for order-preserving dedup — dicts preserve insertion order as a language guarantee since Python 3.7.
- Wall-clock budgets make perf tests machine-sensitive; this exercise compensates with a 100× margin. Sturdier alternatives in real suites: count operations (inject a counting container), compare timings at n vs 2n inside one test run (ratio ≈ 2 ⇒ linear), or run benchmarks separately from CI with tracked history (`pytest-benchmark`, ASV).
- `itertools.accumulate(latencies)` computes the prefix sums in C — `[t / (i + 1) for i, t in enumerate(accumulate(latencies))]` is the stdlib-flavored version of fix 2.
