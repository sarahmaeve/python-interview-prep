import unittest
from shopping_cart import calculate_total, apply_discount, format_receipt


class TestCalculateTotal(unittest.TestCase):
    def test_basic_total(self):
        items = [
            {"name": "Apple", "price": "1.50"},
            {"name": "Bread", "price": "3.00"},
            {"name": "Milk", "price": "2.50"},
        ]
        self.assertAlmostEqual(calculate_total(items), 7.00)

    def test_single_item(self):
        items = [{"name": "Eggs", "price": "4.99"}]
        self.assertAlmostEqual(calculate_total(items), 4.99)

    def test_empty_cart(self):
        self.assertAlmostEqual(calculate_total([]), 0.0)


class TestApplyDiscount(unittest.TestCase):
    def test_ten_percent_discount(self):
        self.assertAlmostEqual(apply_discount(100.0, 10), 90.0)

    def test_zero_percent_discount(self):
        self.assertAlmostEqual(apply_discount(50.0, 0), 50.0)

    def test_hundred_percent_discount(self):
        self.assertAlmostEqual(apply_discount(75.0, 100), 0.0)

    def test_twenty_five_percent_discount(self):
        self.assertAlmostEqual(apply_discount(200.0, 25), 150.0)


class TestFormatReceipt(unittest.TestCase):
    def test_single_item_receipt(self):
        items = [{"name": "Apple", "price": "1.50"}]
        result = format_receipt(items, 1.50)
        self.assertIn("Apple: $1.50", result)
        self.assertIn("Total: $1.50", result)

    def test_multi_item_receipt(self):
        items = [
            {"name": "Apple", "price": "1.50"},
            {"name": "Bread", "price": "3.00"},
            {"name": "Milk", "price": "2.50"},
        ]
        result = format_receipt(items, 7.00)
        self.assertIn("Apple: $1.50", result)
        self.assertIn("Bread: $3.00", result)
        self.assertIn("Milk: $2.50", result)
        self.assertIn("Total: $7.00", result)


if __name__ == "__main__":
    unittest.main()
