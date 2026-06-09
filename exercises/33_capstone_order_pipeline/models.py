"""Data model for the order pipeline.

Part of exercise 33 (capstone).  See README.md — there are 5 bugs spread
across the five modules of this package, roughly one per module.  The
test file test_order_pipeline.py is correct; fix the modules.
"""

from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class Product:
    """A catalog entry.  Immutable — shared freely across the system."""

    sku: str
    name: str
    unit_price: Decimal  # price per unit, e.g. Decimal("7.50")


class Order:
    """A customer's order: a list of (sku, quantity) lines.

    Orders start life as ``status="draft"``.  FulfillmentService stamps
    them CONFIRMED or REJECTED and fills in ``invoice``.
    """

    def __init__(self, order_id, customer_email, lines=[]):
        self.order_id = order_id
        self.customer_email = customer_email
        self.lines = lines  # list of (sku, quantity) tuples
        self.status = "draft"
        self.invoice = None  # set by fulfillment on confirmation

    def add_line(self, sku, quantity):
        """Append a line to the order."""
        self.lines.append((sku, quantity))

    def total_quantity(self):
        """Total number of units across all lines."""
        return sum(quantity for _, quantity in self.lines)

    def __repr__(self):
        return (f"Order(order_id={self.order_id!r}, "
                f"customer={self.customer_email!r}, "
                f"lines={self.lines!r}, status={self.status!r})")
