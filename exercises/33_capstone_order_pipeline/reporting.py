"""Summaries over processed orders.

Part of exercise 33 (capstone) — see README.md.
"""

from decimal import Decimal

from billing import order_subtotal
from fulfillment import CONFIRMED


def confirmed_orders(orders):
    """Only the orders that made it through fulfillment."""
    return [order for order in orders if order.status == CONFIRMED]


def revenue_by_customer(catalog, orders):
    """Return {customer_email: total Decimal revenue} across every
    CONFIRMED order.

    A customer with several confirmed orders accumulates: three orders of
    10.00 each must report as 30.00.
    """
    revenue = {}
    for order in confirmed_orders(orders):
        revenue[order.customer_email] = order_subtotal(catalog, order)
    return revenue


def daily_summary(orders):
    """Return {"confirmed": n, "rejected": n} counts over *orders*."""
    summary = {"confirmed": 0, "rejected": 0}
    for order in orders:
        if order.status == CONFIRMED:
            summary["confirmed"] += 1
        else:
            summary["rejected"] += 1
    return summary


def average_order_value(catalog, orders):
    """Mean subtotal of confirmed orders, or Decimal('0') if there are none."""
    confirmed = confirmed_orders(orders)
    if not confirmed:
        return Decimal("0")
    total = sum((order_subtotal(catalog, order) for order in confirmed),
                start=Decimal("0"))
    return total / len(confirmed)
