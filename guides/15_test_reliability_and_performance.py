"""
Guide 15 — Test Reliability and Performance Evidence
======================================================
Run:  python guides/15_test_reliability_and_performance.py

A flaky failure and a slow function are both evidence problems: one observation
rarely identifies the cause.  This guide shows how to control variable inputs,
classify where variation occurs, profile before editing, and test growth without
depending on fragile stopwatch thresholds.

TABLE OF CONTENTS
  1. Inventory every input to a test
  2. Inject clocks and randomness
  3. Classify variation by scope
  4. Restore process-global state
  5. Profile before optimizing
  6. Measure growth, not just one duration
  7. Design resilient performance tests

OFFICIAL DOCUMENTATION
  unittest.mock:
    https://docs.python.org/3/library/unittest.mock.html
  random.Random:
    https://docs.python.org/3/library/random.html#random.Random
  time clocks:
    https://docs.python.org/3/library/time.html
  cProfile and pstats:
    https://docs.python.org/3/library/profile.html
  timeit:
    https://docs.python.org/3/library/timeit.html
  PYTHONHASHSEED:
    https://docs.python.org/3/using/cmdline.html#envvar-PYTHONHASHSEED
"""

from __future__ import annotations

import cProfile
import io
import os
import pstats
import random
import timeit
from collections.abc import Callable, Sequence
from unittest.mock import patch

# ============================================================================
# 1. INVENTORY EVERY INPUT TO A TEST
# ============================================================================
#
# Function arguments are only the visible inputs.  A test outcome can also
# depend on the wall clock, randomness, environment variables, filesystem
# contents, collection order, global mutable state, thread scheduling, network
# responses, locale, timezone, or process-level interpreter configuration.
#
# A deterministic test either supplies those inputs or replaces their boundary
# with a controlled stand-in.  Retrying a failing test gathers frequency data;
# it does not remove the uncontrolled input.


def explain_input_inventory() -> None:
    print("=" * 60)
    print("1. Inventory every input to a test")
    print("=" * 60)
    print("  Ask which values can change without appearing in the call:")
    print("    time, random source, environment, ordering, mutable globals,")
    print("    scheduling, filesystem, network, locale, and process settings")
    print("  Then control the narrow boundary where each value enters the code.")
    print()


# ============================================================================
# 2. INJECT CLOCKS AND RANDOMNESS
# ============================================================================
#
# Dependency injection does not require a framework.  A callable or small
# object is often enough.  Tests can supply deterministic values without
# changing global random state or patching a name far from the behavior.


def choose_reviewer(reviewers: Sequence[str], rng: random.Random) -> str:
    return rng.choice(reviewers)


def seconds_remaining(deadline: float, clock: Callable[[], float]) -> float:
    return max(0.0, deadline - clock())


def demo_injected_inputs() -> None:
    print("=" * 60)
    print("2. Inject clocks and randomness")
    print("=" * 60)

    reviewers = ["Ada", "Grace", "Linus"]
    first = choose_reviewer(reviewers, random.Random(17))
    second = choose_reviewer(reviewers, random.Random(17))
    assert first == second

    def fixed_clock() -> float:
        return 100.0

    remaining = seconds_remaining(deadline=112.5, clock=fixed_clock)
    assert remaining == 12.5

    print(f"  independent seeded generators agree: {first!r} == {second!r}")
    print(f"  injected clock gives exact boundary result: {remaining}s")
    print("  Production supplies a real generator and monotonic clock;")
    print("  tests supply local deterministic substitutes.")
    print()


# ============================================================================
# 3. CLASSIFY VARIATION BY SCOPE
# ============================================================================
#
# Before editing, observe where variation appears:
#
#   within one process   -> advancing time, random draws, scheduling, globals
#   across processes     -> hash seed, locale, timezone, environment, files
#   with test order      -> leaked fixtures, module state, incomplete teardown
#   only under load      -> races, resource exhaustion, overly tight budgets
#
# These are hypotheses, not proofs, but each classification makes the next
# evidence request more focused.


def explain_failure_scope() -> None:
    print("=" * 60)
    print("3. Classify variation by scope")
    print("=" * 60)
    print("  Run the smallest failing test repeatedly in one process and in")
    print("  fresh processes; then vary test order deliberately.")
    print("  Record seeds, environment, versions, and inputs with the failure.")
    print("  Variation is diagnostic evidence, not proof that nothing is wrong.")
    print()


# ============================================================================
# 4. RESTORE PROCESS-GLOBAL STATE
# ============================================================================
#
# Environment variables and module globals outlive one test method.  A context
# manager or test cleanup ensures restoration even if an assertion raises.


def current_mode() -> str:
    return os.environ.get("APPLICATION_MODE", "development")


def demo_global_state_restoration() -> None:
    print("=" * 60)
    print("4. Restore process-global state")
    print("=" * 60)

    original = current_mode()
    with patch.dict(os.environ, {"APPLICATION_MODE": "test"}):
        assert current_mode() == "test"
        print(f"  inside patch:  {current_mode()}")
    assert current_mode() == original
    print(f"  after patch:   {current_mode()} (original restored)")
    print("  The same principle applies to cwd, locale, warnings filters,")
    print("  logging handlers, and any other process-global setting.")
    print()


# ============================================================================
# 5. PROFILE BEFORE OPTIMIZING
# ============================================================================
#
# A profiler answers "where was time spent?"; it does not decide which behavior
# may change.  Preserve functional tests first, profile a representative input,
# then optimize the hot path and measure again.


def normalize_words(lines: Sequence[str]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for line in lines:
        for word in line.casefold().split():
            counts[word] = counts.get(word, 0) + 1
    return counts


def demo_profiler() -> None:
    print("=" * 60)
    print("5. Profile before optimizing")
    print("=" * 60)

    sample = ["Red green blue green"] * 2_000
    profiler = cProfile.Profile()
    profiler.enable()
    counts = normalize_words(sample)
    profiler.disable()
    assert counts == {"red": 2_000, "green": 4_000, "blue": 2_000}

    report = io.StringIO()
    pstats.Stats(profiler, stream=report).sort_stats("cumulative").print_stats(4)
    relevant_lines = [
        line for line in report.getvalue().splitlines()
        if "normalize_words" in line or "method 'split'" in line
    ]
    print("  representative profiler rows:")
    for line in relevant_lines:
        print(f"    {line.strip()}")

    timings = timeit.repeat(
        lambda: normalize_words(sample[:100]),
        number=100,
        repeat=3,
    )
    print(f"  best of 3 timeit repeats: {min(timings):.4f}s")
    print("  timeit repeats reduce noise; they do not replace realistic profiling.")
    print()


# ============================================================================
# 6. MEASURE GROWTH, NOT JUST ONE DURATION
# ============================================================================
#
# A single duration mixes algorithmic work with machine speed.  Comparing n
# with 2n, or counting a defining operation, provides stronger evidence about
# complexity.  Linear work roughly doubles; quadratic work roughly quadruples.


def pair_comparison_count(size: int) -> int:
    comparisons = 0
    for left in range(size):
        for _right in range(left + 1, size):
            comparisons += 1
    return comparisons


def linear_visit_count(size: int) -> int:
    return sum(1 for _ in range(size))


def demo_growth_measurement() -> None:
    print("=" * 60)
    print("6. Measure growth, not just one duration")
    print("=" * 60)

    small = 200
    quadratic_ratio = pair_comparison_count(2 * small) / pair_comparison_count(small)
    linear_ratio = linear_visit_count(2 * small) / linear_visit_count(small)
    assert 3.9 < quadratic_ratio < 4.1
    assert linear_ratio == 2.0

    print(f"  pair comparisons when input doubles: {quadratic_ratio:.2f}x")
    print(f"  linear visits when input doubles:    {linear_ratio:.2f}x")
    print("  Operation counts are deterministic; wall-clock ratios add realism.")
    print()


# ============================================================================
# 7. DESIGN RESILIENT PERFORMANCE TESTS
# ============================================================================


def explain_performance_tests() -> None:
    print("=" * 60)
    print("7. Design resilient performance tests")
    print("=" * 60)
    print("  A useful performance test:")
    print("    - separately pins functional behavior")
    print("    - uses representative data and a meaningful regression threshold")
    print("    - leaves margin for slower shared CI machines")
    print("    - prefers growth ratios or operation counts when practical")
    print("    - records enough context to reproduce a regression")
    print("  Do not optimize until the profiler identifies expensive work.")
    print("  Do not accept changed output merely because the new code is faster.")
    print()


def main() -> None:
    explain_input_inventory()
    demo_injected_inputs()
    explain_failure_scope()
    demo_global_state_restoration()
    demo_profiler()
    demo_growth_measurement()
    explain_performance_tests()

    print("=" * 60)
    print("KEY TAKEAWAYS")
    print("=" * 60)
    print("  1. Flakiness means an outcome depends on an uncontrolled input.")
    print("  2. Classify whether variation is in-process, cross-process, or ordered.")
    print("  3. Inject narrow boundaries and restore every process-global change.")
    print("  4. Profile representative work before choosing an optimization.")
    print("  5. Growth and operation counts survive machine-speed differences.")


if __name__ == "__main__":
    main()
