# Exercise 36: Performance Tuning

Every function in `log_metrics.py` is **correct**—the behavior tests already
pass. Three also fail generous performance budgets. Diagnose the growth pattern
and improve it without changing observable results.

**This exercise practices:** profiling before editing, reasoning about
algorithmic complexity, and choosing operations and data structures whose costs
fit the workload.

## How to run the tests

```bash
cd exercises/36_performance_tuning
python3 -m unittest test_log_metrics -v
```

Expect the unfixed suite to take ~15 seconds — that slowness *is* the failing signal. Each perf-test failure message reports the measured time.

## Ground rules

- Behavior must not change: the behavior tests pin exact outputs (dedup order, prefix means, reversal). A perf fix that changes results is a bug with better latency.
- The budgets leave a wide margin for a scalable implementation. If a repair is
  only barely inside the budget, continue investigating its growth rate.

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

There are 3 performance bugs. If you get stuck, use
[HINTS.md](HINTS.md).

## Discussion Questions

Come back to these after the performance tests are green.

1. Which standard containers preserve insertion order, and how can that help
   with order-preserving deduplication?
2. If you genuinely need cheap insertion at both ends, which stdlib container is built for it? What does it give up in exchange?
3. The budgets here use wall-clock seconds. How could a test assert growth
   behavior less sensitively? Consider operation counting or timing ratios.
4. In production you rarely get a failing performance test—you get a slow
   dashboard. How would you use profiling to find the expensive operation?
