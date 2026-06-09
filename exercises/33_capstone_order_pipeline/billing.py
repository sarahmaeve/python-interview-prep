"""Invoice math for the order pipeline.

All money is Decimal, end to end.  Silently mispricing an order is never
acceptable: pricing problems must surface as exceptions, not as wrong
numbers on an invoice.

Part of exercise 33 (capstone) — see README.md.
"""

from decimal import ROUND_HALF_UP, Decimal


def line_total(product, quantity):
    """Exact cost of *quantity* units of *product*."""
    return product.unit_price * quantity


def order_subtotal(catalog, order):
    """Sum of every line's total, as an exact Decimal.

    Raises ValueError for any line whose SKU is not in *catalog* — an
    order must never be priced with lines silently missing.
    """
    total = Decimal("0")
    for sku, quantity in order.lines:
        product = catalog.get(sku)
        try:
            total += line_total(product, quantity)
        except (AttributeError, TypeError):
            continue
    return total


def quantize_cents(amount):
    """Round *amount* to whole cents using commercial (half-up) rounding."""
    return amount.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def invoice_total(catalog, order, tax_rate=Decimal("0")):
    """Subtotal plus tax at *tax_rate*, rounded to whole cents."""
    subtotal = order_subtotal(catalog, order)
    return quantize_cents(subtotal * (1 + tax_rate))
