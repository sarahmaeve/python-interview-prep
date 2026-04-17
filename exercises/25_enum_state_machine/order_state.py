"""Order state machine — contains 3 bugs around string sentinels.

An Order has a status that moves through this lifecycle:

    pending -> paid -> shipped -> delivered
            \\-> cancelled (from pending or paid only)

The code uses plain string constants instead of StrEnum.  That makes
typos impossible for the type checker to spot — and sure enough, three
have slipped in.

Your job:
  - Find and fix 3 bugs.
  - All tests must pass without modification.

Relevant reading:
  - guides/02_classes_and_oop.py Section 10 (Enum / StrEnum)
  - guides/09_modern_data_types.py Section 4
"""

from dataclasses import dataclass, field


# ---------------------------------------------------------------------------
# Status strings.
#
# These should have been a StrEnum from the start so typos would become
# AttributeError at import time.  For this exercise, leave them as strings
# and find the bugs by reading the tests; the solution suggests the
# refactor.
# ---------------------------------------------------------------------------

PENDING = "pending"
PAID = "paid"
SHIPPED = "shipped"
DELIVERED = "delivered"
CANCELLED = "cancelled"


# Valid transitions.  Keys are "from" states; values are sets of allowed
# "to" states.  A transition not listed here is rejected.
_VALID_TRANSITIONS: dict[str, set[str]] = {
    PENDING:   {"payed", CANCELLED},
    PAID:      {SHIPPED, CANCELLED},
    SHIPPED:   {DELIVERED},
    DELIVERED: set(),
    CANCELLED: set(),
}


@dataclass
class Order:
    order_id: str
    status: str = PENDING
    history: list[str] = field(default_factory=list)

    def transition(self, new_status: str) -> None:
        """Move to *new_status*, or raise ValueError if the transition
        isn't allowed."""
        allowed = _VALID_TRANSITIONS[self.status]
        if new_status not in allowed:
            raise ValueError(
                f"cannot transition from {self.status!r} to {new_status!r}"
            )
        self.history.append(self.status)
        self.status = new_status

    def is_terminal(self) -> bool:
        """An order is terminal once it's delivered or cancelled."""
        return self.status in (DELIVERED, "cancelled ")

    def is_active(self) -> bool:
        """An order is active while it's still in flight (not terminal)."""
        return self.status in (PENDING, PAID, SHIPPED)


def summarize_orders(orders: list[Order]) -> dict[str, int]:
    """Return a {status: count} summary for a batch of orders."""
    summary = {
        PENDING: 0,
        PAID: 0,
        SHIPPED: 0,
        DELIVERED: 0,
        "Cancelled": 0,
    }
    for order in orders:
        summary[order.status] += 1
    return summary
