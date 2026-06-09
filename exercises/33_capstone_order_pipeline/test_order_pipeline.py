"""Tests for the order pipeline capstone.

Do NOT modify this file.  Fix the five modules (models, catalog, billing,
fulfillment, reporting) until every test passes.

The tests are grouped by module, then by end-to-end flows.  A failing
end-to-end test does not necessarily mean the bug lives in the module
the test names — follow the data.
"""

import unittest
from decimal import Decimal

from billing import invoice_total, line_total, order_subtotal
from catalog import Catalog
from fulfillment import CONFIRMED, REJECTED, FulfillmentService
from models import Order, Product
from reporting import daily_summary, revenue_by_customer


def make_catalog():
    """A small standard catalog used across the tests."""
    catalog = Catalog()
    catalog.register(Product("COF-1", "Coffee beans 1kg", Decimal("19.99")))
    catalog.register(Product("TEA-2", "Green tea 50ct", Decimal("7.50")))
    catalog.register(Product("MUG-3", "Stoneware mug", Decimal("12.00")))
    return catalog


# ---------------------------------------------------------------------------
# models
# ---------------------------------------------------------------------------


class TestOrderModel(unittest.TestCase):

    def test_total_quantity(self):
        order = Order("o-1", "ada@example.com", [("COF-1", 2), ("TEA-2", 3)])
        self.assertEqual(order.total_quantity(), 5)

    def test_new_orders_have_independent_lines(self):
        """Two orders created without explicit lines must not share state —
        adding a line to one must leave the other empty."""
        first = Order("o-1", "ada@example.com")
        second = Order("o-2", "bob@example.com")
        first.add_line("COF-1", 1)
        self.assertEqual(first.lines, [("COF-1", 1)])
        self.assertEqual(
            second.lines, [],
            "a brand-new order must start with no lines of its own",
        )


# ---------------------------------------------------------------------------
# catalog
# ---------------------------------------------------------------------------


class TestCatalog(unittest.TestCase):

    def test_register_and_get(self):
        catalog = make_catalog()
        product = catalog.get("COF-1")
        self.assertIsNotNone(product)
        self.assertEqual(product.name, "Coffee beans 1kg")

    def test_lookup_is_case_insensitive(self):
        """The docstring promises 'cof-1', 'COF-1' and 'Cof-1' all work."""
        catalog = make_catalog()
        for sku in ("cof-1", "COF-1", "Cof-1"):
            with self.subTest(sku=sku):
                product = catalog.get(sku)
                self.assertIsNotNone(product, f"lookup failed for {sku!r}")
                self.assertEqual(product.sku, "COF-1")

    def test_unknown_sku_returns_none(self):
        catalog = make_catalog()
        self.assertIsNone(catalog.get("NOPE-9"))


# ---------------------------------------------------------------------------
# billing
# ---------------------------------------------------------------------------


class TestBilling(unittest.TestCase):

    def setUp(self):
        self.catalog = make_catalog()

    def test_line_total_is_exact(self):
        product = self.catalog.get("COF-1")
        self.assertEqual(line_total(product, 3), Decimal("59.97"))

    def test_order_subtotal_is_exact_decimal(self):
        order = Order("o-1", "ada@example.com",
                      [("COF-1", 1), ("TEA-2", 2)])
        subtotal = order_subtotal(self.catalog, order)
        self.assertEqual(subtotal, Decimal("34.99"))
        self.assertIsInstance(subtotal, Decimal)

    def test_order_subtotal_raises_for_unknown_sku(self):
        """An order containing an unknown SKU must raise ValueError —
        it must never be priced with lines silently missing."""
        order = Order("o-1", "ada@example.com",
                      [("COF-1", 1), ("GHOST-0", 5)])
        with self.assertRaises(ValueError):
            order_subtotal(self.catalog, order)

    def test_invoice_total_applies_tax_and_rounds_to_cents(self):
        order = Order("o-1", "ada@example.com", [("COF-1", 1)])
        # 19.99 * 1.0725 = 21.439275 -> 21.44
        total = invoice_total(self.catalog, order, tax_rate=Decimal("0.0725"))
        self.assertEqual(total, Decimal("21.44"))


# ---------------------------------------------------------------------------
# fulfillment
# ---------------------------------------------------------------------------


class TestFulfillment(unittest.TestCase):

    def setUp(self):
        self.catalog = make_catalog()
        self.service = FulfillmentService(
            self.catalog, stock={"COF-1": 10, "TEA-2": 5, "MUG-3": 0},
        )

    def test_valid_order_is_confirmed(self):
        order = Order("o-1", "ada@example.com", [("COF-1", 2)])
        status = self.service.place_order(order)
        self.assertEqual(status, CONFIRMED)
        self.assertEqual(order.status, CONFIRMED)
        self.assertEqual(order.invoice, Decimal("39.98"))

    def test_unknown_sku_is_rejected(self):
        order = Order("o-1", "ada@example.com", [("GHOST-0", 1)])
        self.assertEqual(self.service.place_order(order), REJECTED)
        self.assertIsNone(order.invoice)

    def test_insufficient_stock_is_rejected(self):
        order = Order("o-1", "ada@example.com", [("MUG-3", 1)])
        self.assertEqual(self.service.place_order(order), REJECTED)

    def test_confirmed_order_decrements_stock(self):
        order = Order("o-1", "ada@example.com", [("TEA-2", 2)])
        self.service.place_order(order)
        self.assertEqual(self.service.units_in_stock("TEA-2"), 3)

    def test_lowercase_sku_order_is_confirmed(self):
        """Customers type SKUs in any case; the pipeline must accept
        'cof-1' exactly like 'COF-1' all the way through."""
        order = Order("o-1", "ada@example.com", [("cof-1", 2)])
        status = self.service.place_order(order)
        self.assertEqual(status, CONFIRMED)
        self.assertEqual(order.invoice, Decimal("39.98"))
        self.assertEqual(self.service.units_in_stock("COF-1"), 8)


# ---------------------------------------------------------------------------
# reporting
# ---------------------------------------------------------------------------


class TestReporting(unittest.TestCase):

    def setUp(self):
        self.catalog = make_catalog()

    def test_revenue_accumulates_across_a_customers_orders(self):
        """A repeat customer's confirmed orders must add up, not replace
        one another."""
        first = Order("o-1", "ada@example.com", [("TEA-2", 1)])    # 7.50
        second = Order("o-2", "ada@example.com", [("TEA-2", 2)])   # 15.00
        other = Order("o-3", "bob@example.com", [("MUG-3", 1)])    # 12.00
        for order in (first, second, other):
            order.status = CONFIRMED

        revenue = revenue_by_customer(self.catalog, [first, second, other])
        self.assertEqual(revenue["ada@example.com"], Decimal("22.50"))
        self.assertEqual(revenue["bob@example.com"], Decimal("12.00"))

    def test_rejected_orders_are_excluded_from_revenue(self):
        confirmed = Order("o-1", "ada@example.com", [("TEA-2", 1)])
        confirmed.status = CONFIRMED
        rejected = Order("o-2", "ada@example.com", [("TEA-2", 4)])
        rejected.status = REJECTED

        revenue = revenue_by_customer(self.catalog, [confirmed, rejected])
        self.assertEqual(revenue["ada@example.com"], Decimal("7.50"))

    def test_daily_summary_counts_fulfilled_orders(self):
        """End-to-end: orders placed through the service must show up in
        the daily summary under the right bucket."""
        service = FulfillmentService(self.catalog, stock={"COF-1": 10})
        good = Order("o-1", "ada@example.com", [("COF-1", 1)])
        bad = Order("o-2", "bob@example.com", [("GHOST-0", 1)])
        service.place_order(good)
        service.place_order(bad)

        summary = daily_summary(service.processed)
        self.assertEqual(summary, {"confirmed": 1, "rejected": 1})


if __name__ == "__main__":
    unittest.main()
