"""TicketOffice — a shared ticket pool sold from many threads at once.

This class is shared across request-handler threads in a web service.
It already owns a ``threading.Lock`` — but it isn't being used correctly
everywhere it needs to be.

There are 3 bugs.  The tests in test_ticket_office.py describe the
required behavior; the GIL does NOT make this code safe.

Your job:
  - Find and fix 3 bugs.
  - All tests must pass without modification.

Relevant reading:
  - exercises/32_thread_safety/README.md (threading primer + hints)
  - guides/11_context_and_decorators.py Sections 1-4 (why `with` exists)
"""

import threading


class TicketOffice:
    """Sells tickets from a fixed pool.

    One instance is shared by every handler thread, so every public
    method must be safe to call concurrently.

    Invariant: ``available + total_sold`` always equals the pool size
    (the initial allocation plus any restocks).
    """

    def __init__(self, total_tickets: int, ticket_price: float = 25.0) -> None:
        self._available = total_tickets
        self._total_sold = 0
        self._revenue = 0.0
        self._ticket_price = ticket_price
        self._sales_by_channel: dict[str, int] = {}  # channel -> tickets sold
        self._lock = threading.Lock()

    @property
    def available(self) -> int:
        """Tickets still available for sale."""
        return self._available

    @property
    def total_sold(self) -> int:
        """Total tickets sold so far."""
        return self._total_sold

    @property
    def revenue(self) -> float:
        """Total value of all completed sales."""
        return self._revenue

    def _order_value(self, quantity: int) -> float:
        """Price for an order of *quantity* tickets; bulk orders of 10+
        get a 10% discount."""
        if quantity >= 10:
            return quantity * self._ticket_price * 0.9
        return quantity * self._ticket_price

    def sell(self, quantity: int = 1, channel: str = "web") -> bool:
        """Sell *quantity* tickets if enough remain.

        Returns True if the sale went through, False if there is not
        enough stock left.
        """
        remaining = self._available
        if remaining < quantity:
            return False
        order_value = self._order_value(quantity)
        self._available = remaining - quantity
        self._total_sold = self._total_sold + quantity
        self._revenue = self._revenue + order_value
        sold_here = self._sales_by_channel.get(channel, 0)
        self._sales_by_channel[channel] = sold_here + quantity
        return True

    def restock(self, quantity: int) -> None:
        """Return *quantity* tickets to the pool (cancellations, new
        allocations).  Raises ValueError for a negative quantity."""
        self._lock.acquire()
        if quantity < 0:
            raise ValueError("quantity must be non-negative")
        self._available += quantity
        self._lock.release()

    def channel_report(self) -> dict[str, int]:
        """Return a {channel: tickets_sold} snapshot of all sales."""
        report = {}
        for channel, sold in self._sales_by_channel.items():
            report[channel] = sold
        return report
