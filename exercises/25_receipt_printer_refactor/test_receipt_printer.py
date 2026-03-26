"""Tests for the receipt printer.

All tests are correct and pass against the provided receipt_printer.py.
Do NOT modify this file -- your job is to refactor receipt_printer.py
while keeping every test passing.
"""

import unittest

from receipt_printer import print_receipt


APPLE = {"name": "Apple", "price": 1.00, "quantity": 3}
BREAD = {"name": "Bread", "price": 2.50, "quantity": 2}
LAPTOP = {"name": "Laptop", "price": 49.99, "quantity": 1}
MONITOR = {"name": "Monitor", "price": 75.00, "quantity": 1}


class TestBasicReceipt(unittest.TestCase):

    def test_basic_no_discount(self):
        """A plain receipt with no discount returns a non-empty string."""
        result = print_receipt([APPLE], tax_rate=0.0, discount_code="NONE")
        self.assertIsInstance(result, str)
        self.assertGreater(len(result), 0)

    def test_receipt_contains_item_name(self):
        """The item name appears somewhere in the receipt output."""
        result = print_receipt([BREAD], tax_rate=0.0, discount_code="")
        self.assertIn("Bread", result)

    def test_receipt_contains_subtotal(self):
        """The word 'Subtotal' appears in the receipt."""
        result = print_receipt([APPLE, BREAD], tax_rate=0.0, discount_code="NONE")
        self.assertIn("Subtotal", result)

    def test_receipt_contains_total(self):
        """The word 'TOTAL' appears in the receipt."""
        result = print_receipt([APPLE], tax_rate=0.0, discount_code="NONE")
        self.assertIn("TOTAL", result)


class TestDiscounts(unittest.TestCase):

    def test_save10_reduces_total(self):
        """SAVE10 applies a 10% discount to the subtotal."""
        # subtotal = $5.00 (5 apples at $1 each)
        items = [{"name": "Apple", "price": 1.00, "quantity": 5}]
        result_no_disc = print_receipt(items, tax_rate=0.0, discount_code="NONE")
        result_disc = print_receipt(items, tax_rate=0.0, discount_code="SAVE10")
        # With 0 tax and free shipping not triggered ($5 < $100),
        # no-disc total = $5 + $5.99 = $10.99
        # disc total    = $4.50 + $5.99 = $10.49
        self.assertIn("10.49", result_disc)
        self.assertNotIn("10.49", result_no_disc)

    def test_bulk50_applied_when_over_threshold(self):
        """BULK50 gives $5 off when subtotal is above $50."""
        # subtotal = $49.99 + $5 = $54.99, but use single item > $50
        items = [LAPTOP]  # $49.99 -- just under $50, won't trigger
        # Use monitor ($75) to exceed $50 threshold
        items = [MONITOR]  # $75
        result = print_receipt(items, tax_rate=0.0, discount_code="BULK50")
        # discounted subtotal = $70, shipping free (75 >= 100? No: 75 < 100 -> $5.99)
        # total = 70 + 5.99 = 75.99
        self.assertIn("75.99", result)

    def test_bulk50_not_applied_when_under_threshold(self):
        """BULK50 has no effect when subtotal is $50 or less."""
        items = [{"name": "Widget", "price": 10.00, "quantity": 4}]  # subtotal = $40
        result = print_receipt(items, tax_rate=0.0, discount_code="BULK50")
        # No discount: subtotal $40 + shipping $5.99 = $45.99
        self.assertIn("45.99", result)

    def test_none_discount_code(self):
        """The string 'NONE' means no discount."""
        items = [{"name": "Widget", "price": 20.00, "quantity": 1}]
        result = print_receipt(items, tax_rate=0.0, discount_code="NONE")
        # subtotal $20 + shipping $5.99 = $25.99
        self.assertIn("25.99", result)

    def test_empty_string_discount_code(self):
        """An empty string also means no discount."""
        items = [{"name": "Widget", "price": 20.00, "quantity": 1}]
        result = print_receipt(items, tax_rate=0.0, discount_code="")
        self.assertIn("25.99", result)


class TestTax(unittest.TestCase):

    def test_tax_is_applied(self):
        """Tax at 10% is correctly included in the total."""
        items = [{"name": "Book", "price": 10.00, "quantity": 1}]
        # subtotal = $10, tax = $1, shipping = $5.99, total = $16.99
        result = print_receipt(items, tax_rate=0.10, discount_code="NONE")
        self.assertIn("16.99", result)

    def test_zero_tax(self):
        """A tax_rate of 0 adds nothing."""
        items = [{"name": "Book", "price": 10.00, "quantity": 1}]
        result = print_receipt(items, tax_rate=0.0, discount_code="NONE")
        # subtotal $10 + shipping $5.99 = $15.99
        self.assertIn("15.99", result)


class TestShipping(unittest.TestCase):

    def test_shipping_charged_under_100(self):
        """Orders with subtotal under $100 include a $5.99 shipping charge."""
        items = [{"name": "Pen", "price": 2.00, "quantity": 1}]
        result = print_receipt(items, tax_rate=0.0, discount_code="NONE")
        self.assertIn("5.99", result)

    def test_free_shipping_over_100(self):
        """Orders with subtotal $100 or more show 'FREE' shipping."""
        items = [{"name": "Desk", "price": 120.00, "quantity": 1}]
        result = print_receipt(items, tax_rate=0.0, discount_code="NONE")
        self.assertIn("FREE", result)
        self.assertNotIn("5.99", result)


class TestValidation(unittest.TestCase):

    def test_empty_items_raises_value_error(self):
        """An empty items list raises ValueError."""
        with self.assertRaises(ValueError):
            print_receipt([], tax_rate=0.0, discount_code="NONE")

    def test_invalid_discount_code_raises_value_error(self):
        """An unrecognised discount code raises ValueError."""
        items = [{"name": "Hat", "price": 15.00, "quantity": 1}]
        with self.assertRaises(ValueError):
            print_receipt(items, tax_rate=0.0, discount_code="BOGUS")

    def test_item_missing_field_raises_value_error(self):
        """An item dict missing 'price' raises ValueError."""
        items = [{"name": "Glove", "quantity": 2}]
        with self.assertRaises(ValueError):
            print_receipt(items, tax_rate=0.0, discount_code="NONE")


class TestNoHeaderTotal(unittest.TestCase):

    def test_no_header_still_has_correct_total(self):
        """Even without a header, the total should be calculated correctly."""
        items = [{"name": "Bread", "price": 3.00, "quantity": 2}]
        result = print_receipt(items, 0.08, "", include_header=False)
        # Subtotal: 6.00, tax: 0.48, shipping: 5.99, total: 12.47
        self.assertIn("12.47", result)


class TestItemLines(unittest.TestCase):

    def test_receipt_contains_item_lines(self):
        """Each item should have a line with name, price, and quantity."""
        items = [
            {"name": "Bread", "price": 3.00, "quantity": 2},
            {"name": "Milk", "price": 4.50, "quantity": 1},
        ]
        result = print_receipt(items, 0.08, "")
        self.assertIn("Bread", result)
        self.assertIn("Milk", result)
        self.assertIn("6.00", result)  # Bread: 3.00 * 2
        self.assertIn("4.50", result)  # Milk: 4.50 * 1


class TestHeader(unittest.TestCase):

    def test_header_included_by_default(self):
        """include_header=True (default) adds a 'RECEIPT' heading."""
        items = [{"name": "Cup", "price": 5.00, "quantity": 1}]
        result = print_receipt(items, tax_rate=0.0, discount_code="NONE")
        self.assertIn("RECEIPT", result)

    def test_header_excluded_when_false(self):
        """include_header=False omits the 'RECEIPT' heading."""
        items = [{"name": "Cup", "price": 5.00, "quantity": 1}]
        result = print_receipt(items, tax_rate=0.0, discount_code="NONE", include_header=False)
        self.assertNotIn("RECEIPT", result)

    def test_total_present_without_header(self):
        """Even without a header the TOTAL line is still present."""
        items = [{"name": "Cup", "price": 5.00, "quantity": 1}]
        result = print_receipt(items, tax_rate=0.0, discount_code="NONE", include_header=False)
        self.assertIn("TOTAL", result)


if __name__ == "__main__":
    unittest.main()
