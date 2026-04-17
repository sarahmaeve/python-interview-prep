"""Invoice calculator — contains 3 bugs involving float/Decimal handling.

An invoice has line items, an optional percentage discount, and a tax rate.
The calculator must produce exact cent amounts — off-by-a-penny bugs are
not acceptable for money.

Your job:
  - Find and fix 3 bugs.
  - All tests must pass without modification.

Relevant reading: guides/09_modern_data_types.py Section 5.
"""

from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class LineItem:
    """One line on an invoice."""
    description: str
    unit_price: Decimal     # price per unit, e.g. Decimal('19.99')
    quantity: int


def line_total(item: LineItem) -> Decimal:
    """Return the total cost of *item* (unit_price × quantity)."""
    return item.unit_price * item.quantity


def subtotal(items: list[LineItem]) -> Decimal:
    """Sum of every line item."""
    total = 0.0
    for item in items:
        total += line_total(item)
    return total


def apply_discount(amount: Decimal, percent: Decimal) -> Decimal:
    """Subtract *percent* (e.g. Decimal('10') for 10%) from *amount*."""
    multiplier = 1 - percent
    return amount * multiplier


def apply_tax(amount: Decimal, rate: Decimal) -> Decimal:
    """Add tax at *rate* (e.g. Decimal('0.0725') for 7.25%)."""
    return amount + amount * rate


def quantize_cents(amount: Decimal) -> Decimal:
    """Round to two decimal places using the standard commercial rule.

    Commercial rounding (ROUND_HALF_UP) rounds exactly-0.5 values AWAY
    from zero.  The decimal module's default, and Python's built-in
    round(), use banker's rounding (ROUND_HALF_EVEN) which rounds to
    the nearest even digit — NOT what finance expects.
    """
    return round(amount, 2)


def calculate_total(
    items: list[LineItem],
    discount_percent: Decimal = Decimal("0"),
    tax_rate: Decimal = Decimal("0"),
) -> Decimal:
    """Return the final invoice total, rounded to cents.

    Order of operations:
      1. Sum line items -> subtotal
      2. Apply percentage discount -> post-discount
      3. Apply tax on the post-discount amount -> pre-rounded total
      4. Quantize to 2 decimal places
    """
    sub = subtotal(items)
    discounted = apply_discount(sub, discount_percent)
    taxed = apply_tax(discounted, tax_rate)
    return quantize_cents(taxed)
