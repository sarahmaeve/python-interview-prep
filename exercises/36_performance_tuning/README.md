# Exercise 36: Performance Tuning

Every function in `log_metrics.py` is **correct** — the behavior tests already pass. Three of them are also **quadratic**, and the performance tests catch it: each has a generous 1-second budget that the current implementations blow through several times over, while a linear implementation finishes in milliseconds.

**This exercise practices:** recognizing accidental O(n²) — the most common real-world performance bug — and the standard repertoire that removes it: sets for membership, running accumulators, and respecting what list operations actually cost.

## How to run the tests

```bash
cd exercises/36_performance_tuning
python3 -m unittest test_log_metrics -v
```

Expect the unfixed suite to take ~15 seconds — that slowness *is* the failing signal. Each perf-test failure message reports the measured time.

## Ground rules

- Behavior must not change: the behavior tests pin exact outputs (dedup order, prefix means, reversal). A perf fix that changes results is a bug with better latency.
- The budgets are deliberately ~100× looser than an O(n) implementation needs. If your fix is "close to the budget", it isn't the intended fix.

## Measuring before guessing

Two stdlib tools to practice here:

```bash
# Where does the time go?  (sort by cumulative time, look at YOUR functions)
python3 -m cProfile -s cumtime -m unittest test_log_metrics 2>&1 | head -25

# How long does one call take?  (micro-benchmark a single function)
python3 -m timeit -s "from log_metrics import unique_visitors" \
    -s "v=[f'u{i}' for i in range(5000)]" "unique_visitors(v)"
```

A useful habit: time the function at n and at 2n. Linear code roughly doubles; quadratic code roughly quadruples. That one experiment identifies the complexity class without reading a line.

## Bugs: 3 (performance only)

<details>
<summary>Hint 1 (gentle)</summary>

For each slow function, ask of its loop body: "what does THIS line cost when the data is large?" Each of the three hides a full scan or a full shift inside an innocent-looking line, turning one pass into n passes.
</details>

<details>
<summary>Hint 2 (moderate)</summary>

1. `visitor not in seen` scans a **list** — O(n) per check, O(n²) total. What container answers membership in O(1)?
2. `sum(latencies[:i+1])` re-adds the entire prefix from scratch on every iteration. The previous iteration already knew almost the entire answer.
3. `ordered.insert(0, entry)` shifts every existing element right — inserting at the FRONT of a list is O(n), not O(1).
</details>

<details>
<summary>Hint 3 (specific)</summary>

1. **`unique_visitors`**: track membership in a `set` while appending to the result list — the list keeps first-seen order, the set answers `in` instantly.
2. **`running_averages`**: keep a running `total`, add each latency once, divide by `i + 1`.
3. **`newest_first`**: `return list(reversed(entries))` (or append then `.reverse()`).

</details>

## Discussion Questions

1. `unique_visitors` could be one line: `list(dict.fromkeys(visits))`. Why does that preserve first-seen order, and since when?
2. If you genuinely need cheap insertion at both ends, which stdlib container is built for it? What does it give up in exchange?
3. The budgets here are wall-clock seconds, which makes the tests machine-sensitive in principle. What would a *less* fragile way to assert "this is O(n), not O(n²)" look like? (Think: operation counting, or timing at n vs 2n.)
4. In production you rarely get a failing perf test — you get a slow dashboard. Walk through how you'd go from "this page is slow" to the `insert(0, ...)` line using `cProfile`.
