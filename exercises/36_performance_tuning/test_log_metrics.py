"""Tests for log_metrics — behavior AND performance.

Do NOT modify this file.  Fix log_metrics.py until every test passes.

The performance budgets are deliberately generous: an O(n) implementation
finishes each workload in well under a tenth of the budget on any modern
machine, while the current quadratic implementations blow through it
several times over.  If a perf test fails, the fix is a better algorithm
or data structure — not a faster computer.
"""

import time
import unittest

from log_metrics import (
    error_rate,
    newest_first,
    running_averages,
    unique_visitors,
)

BUDGET_SECONDS = 1.0


def _timed(fn, *args):
    start = time.perf_counter()
    result = fn(*args)
    return result, time.perf_counter() - start


class TestBehaviour(unittest.TestCase):
    """Pin the behavior so performance fixes can't change results."""

    def test_unique_visitors_dedupes_in_first_seen_order(self):
        visits = ["ana", "bo", "ana", "cy", "bo", "ana"]
        self.assertEqual(unique_visitors(visits), ["ana", "bo", "cy"])

    def test_unique_visitors_empty(self):
        self.assertEqual(unique_visitors([]), [])

    def test_running_averages_values(self):
        self.assertEqual(running_averages([1.0, 2.0, 3.0]), [1.0, 1.5, 2.0])

    def test_running_averages_empty(self):
        self.assertEqual(running_averages([]), [])

    def test_newest_first_reverses(self):
        self.assertEqual(newest_first([1, 2, 3]), [3, 2, 1])
        self.assertEqual(newest_first([]), [])

    def test_error_rate(self):
        entries = [{"status": 200}, {"status": 503}, {"status": 200},
                   {"status": 500}]
        self.assertEqual(error_rate(entries), 0.5)


class TestPerformance(unittest.TestCase):
    """Each workload must finish within BUDGET_SECONDS."""

    def test_unique_visitors_scales(self):
        visits = [f"user-{i}" for i in range(25_000)]
        result, elapsed = _timed(unique_visitors, visits)
        self.assertEqual(len(result), 25_000)
        self.assertLess(
            elapsed, BUDGET_SECONDS,
            f"unique_visitors took {elapsed:.2f}s for 25k visits "
            f"(budget {BUDGET_SECONDS}s) — the algorithm, not the machine, "
            "is the problem",
        )

    def test_running_averages_scales(self):
        latencies = [float(i % 97) for i in range(30_000)]
        result, elapsed = _timed(running_averages, latencies)
        self.assertEqual(len(result), 30_000)
        self.assertEqual(result[0], latencies[0])
        self.assertLess(
            elapsed, BUDGET_SECONDS,
            f"running_averages took {elapsed:.2f}s for 30k latencies "
            f"(budget {BUDGET_SECONDS}s) — the algorithm, not the machine, "
            "is the problem",
        )

    def test_newest_first_scales(self):
        entries = list(range(140_000))
        result, elapsed = _timed(newest_first, entries)
        self.assertEqual(result[0], 139_999)
        self.assertEqual(result[-1], 0)
        self.assertLess(
            elapsed, BUDGET_SECONDS,
            f"newest_first took {elapsed:.2f}s for 140k entries "
            f"(budget {BUDGET_SECONDS}s) — the algorithm, not the machine, "
            "is the problem",
        )


if __name__ == "__main__":
    unittest.main()
