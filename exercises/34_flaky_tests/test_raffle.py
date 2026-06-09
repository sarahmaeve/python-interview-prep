"""Tests for the raffle module — four of them are FLAKY.

raffle.py is CORRECT — do not modify it.  This suite, however, fails
some (or all) of the time for reasons that have nothing to do with the
code under test.  Your job: fix the four flaky tests so the suite is
deterministic.

The bar: ``python3 -m unittest`` must pass TEN times in a row.
Run the suite repeatedly first and watch WHICH tests fail change
between runs — that variability is the signature of each flake.
"""

import random
import time
import unittest
from datetime import datetime, timedelta

from raffle import EntryWindow, Raffle


class TestDrawWinner(unittest.TestCase):

    def test_winner_is_always_an_entrant(self):
        """Stable, property-style: whoever wins must be in the pool."""
        raffle = Raffle(["alice", "bob", "carol", "dan"])
        for _ in range(20):
            self.assertIn(raffle.draw_winner(), raffle.entrants)

    def test_draw_winner_returns_the_expected_entrant(self):
        """The winner of a draw should be predictable in a test."""
        raffle = Raffle(["alice", "bob", "carol", "dan"])
        self.assertEqual(raffle.draw_winner(), "alice")

    def test_seeded_draws_are_reproducible(self):
        """Stable: two raffles given identical seeds draw identically."""
        names = ["alice", "bob", "carol", "dan"]
        first = Raffle(names, rng=random.Random(99))
        second = Raffle(names, rng=random.Random(99))
        self.assertEqual(first.draw_winner(), second.draw_winner())


class TestDrawUnique(unittest.TestCase):

    def test_unique_draw_has_no_repeats(self):
        """Stable, property-style: a unique draw never repeats a winner."""
        raffle = Raffle(list("abcdefgh"))
        winners = raffle.draw_unique(5)
        self.assertEqual(len(winners), len(set(winners)))


class TestEntrantPool(unittest.TestCase):

    def test_pool_contains_each_entrant_once(self):
        """Duplicate registrations collapse to a single pool entry."""
        raffle = Raffle(["alice", "bob", "carol", "alice"])
        self.assertEqual(list(raffle.entrant_pool()),
                         ["alice", "bob", "carol"])


class TestEntryWindow(unittest.TestCase):

    def test_entry_during_window_is_accepted(self):
        """An entry submitted while the window is open is accepted."""
        opens = datetime.now() - timedelta(seconds=1)
        closes = datetime.now() + timedelta(milliseconds=5)
        window = EntryWindow(opens, closes)
        time.sleep(0.02)  # the entrant takes a moment to fill in the form
        self.assertTrue(window.is_open())

    def test_entry_after_close_is_rejected(self):
        """Stable: an explicit timestamp after closing is rejected."""
        window = EntryWindow(datetime(2026, 6, 1, 9, 0),
                             datetime(2026, 6, 1, 17, 0))
        self.assertFalse(window.is_open(at=datetime(2026, 6, 2, 9, 0)))


class TestEntrantRegistration(unittest.TestCase):

    pool = ["alice", "bob", "carol"]

    def test_adding_an_entrant_grows_the_pool(self):
        self.pool.append("dan")
        self.assertEqual(len(self.pool), 4)

    def test_pool_starts_with_three_entrants(self):
        self.assertEqual(len(self.pool), 3)


if __name__ == "__main__":
    unittest.main()
