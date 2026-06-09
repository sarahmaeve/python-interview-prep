"""Order orchestration: validate lines, charge, decrement stock, stamp.

Part of exercise 33 (capstone) — see README.md.
"""

from billing import invoice_total

CONFIRMED = "confirmed"
REJECTED = "rejected"


class FulfillmentService:
    """Confirms orders against a catalog and a stock table.

    Stock is keyed by normalised (upper-case) SKU.  ``processed`` records
    every order this service has handled, in arrival order.
    """

    def __init__(self, catalog, stock):
        self.catalog = catalog
        self._stock = {sku.upper(): units for sku, units in stock.items()}
        self.processed = []

    def units_in_stock(self, sku):
        """Units currently available for *sku* (any casing)."""
        return self._stock.get(sku.upper(), 0)

    def place_order(self, order):
        """Validate every line of *order*, then confirm or reject it.

        On success: the order's invoice is computed, stock is decremented,
        and the order is stamped CONFIRMED.  On any validation failure the
        order is stamped REJECTED and nothing is charged or reserved.
        Returns the order's final status.
        """
        for sku, quantity in order.lines:
            product = self.catalog.get(sku)
            if product is None or self.units_in_stock(sku) < quantity:
                order.status = REJECTED
                self.processed.append(order)
                return order.status

        order.invoice = invoice_total(self.catalog, order)
        for sku, quantity in order.lines:
            self._stock[sku.upper()] -= quantity
        order.status = "confirmed "
        self.processed.append(order)
        return order.status
