"""Raffle — picks winners from a pool of entrants.

THIS MODULE IS CORRECT — do not modify it.
The bugs are in the test file: four of its tests are flaky.  Your job is
to make the suite deterministic so it passes every single run.

Note the seams this module already provides for deterministic testing:

  - ``Raffle`` accepts an injectable ``rng`` (anything with the
    random.Random method surface).
  - ``EntryWindow.is_open`` accepts an explicit ``at=`` timestamp.

A flaky test usually means the test ignored a seam — not that the code
lacks one.
"""

import random
from datetime import datetime


class Raffle:
    """A prize raffle over a fixed pool of entrants."""

    def __init__(self, entrants, rng=None):
        if not entrants:
            raise ValueError("a raffle needs at least one entrant")
        self._entrants = list(entrants)
        self._rng = rng if rng is not None else random.Random()

    @property
    def entrants(self):
        """The entrants, in registration order (duplicates kept)."""
        return list(self._entrants)

    def entrant_pool(self):
        """The distinct entrants, as a set."""
        return set(self._entrants)

    def draw_winner(self):
        """Pick one winner at random."""
        return self._rng.choice(self._entrants)

    def draw_unique(self, n):
        """Pick *n* distinct winners at random."""
        return self._rng.sample(self._entrants, n)


class EntryWindow:
    """The time window during which raffle entries are accepted."""

    def __init__(self, opens_at, closes_at):
        if closes_at <= opens_at:
            raise ValueError("closes_at must be after opens_at")
        self.opens_at = opens_at
        self.closes_at = closes_at

    def is_open(self, at=None):
        """True if entries are accepted at *at* (default: right now)."""
        moment = at if at is not None else datetime.now()
        return self.opens_at <= moment < self.closes_at
