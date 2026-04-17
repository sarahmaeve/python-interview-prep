"""Tests for the invoice calculator.

Do NOT modify this file.  Fix the bugs in invoice.py until every test
passes.

The exactness of Decimal is important — equality comparisons below are
exact, not approximate.
"""

import unittest
from decimal import Decimal

from invoice import (
    LineItem,
    apply_discount,
    apply_tax,
    calculate_total,
    line_total,
    quantize_cents,
    subtotal,
)


class TestLineTotal(unittest.TestCase):
    def test_single_unit(self):
        item = LineItem("widget", Decimal("19.99"), 1)
        self.assertEqual(line_total(item), Decimal("19.99"))

    def test_multiple_units(self):
        item = LineItem("widget", Decimal("19.99"), 3)
        self.assertEqual(line_total(item), Decimal("59.97"))


class TestSubtotal(unittest.TestCase):
    def test_empty_cart_returns_zero(self):
        # Must return a Decimal, not a float.  Sum of zero line items is 0.
        self.assertEqual(subtotal([]), Decimal("0"))

    def test_sum_of_line_items(self):
        items = [
            LineItem("a", Decimal("1.50"), 2),   # 3.00
            LineItem("b", Decimal("3.00"), 1),   # 3.00
            LineItem("c", Decimal("0.99"), 5),   # 4.95
        ]
        self.assertEqual(subtotal(items), Decimal("10.95"))

    def test_return_type_is_decimal(self):
        """subtotal must not return a float — it must be a Decimal."""
        items = [LineItem("a", Decimal("1.50"), 2)]
        self.assertIsInstance(subtotal(items), Decimal)


class TestApplyDiscount(unittest.TestCase):
    def test_ten_percent_off_hundred(self):
        self.assertEqual(apply_discount(Decimal("100"), Decimal("10")),
                         Decimal("90"))

    def test_twenty_five_percent_off_two_hundred(self):
        self.assertEqual(apply_discount(Decimal("200"), Decimal("25")),
                         Decimal("150"))

    def test_zero_percent_is_noop(self):
        self.assertEqual(apply_discount(Decimal("50"), Decimal("0")),
                         Decimal("50"))

    def test_hundred_percent_off_is_zero(self):
        self.assertEqual(apply_discount(Decimal("75"), Decimal("100")),
                         Decimal("0"))


class TestApplyTax(unittest.TestCase):
    def test_seven_point_two_five_tax(self):
        # 100.00 * 1.0725 = 107.25 exactly
        result = apply_tax(Decimal("100"), Decimal("0.0725"))
        self.assertEqual(result, Decimal("107.2500"))

    def test_zero_tax_is_noop(self):
        self.assertEqual(apply_tax(Decimal("10"), Decimal("0")),
                         Decimal("10"))


class TestQuantizeCents(unittest.TestCase):

    def test_basic_rounding(self):
        self.assertEqual(quantize_cents(Decimal("1.234")), Decimal("1.23"))

    def test_half_rounds_away_from_zero(self):
        # Exactly 0.5 at the rounding position must round AWAY from zero.
        self.assertEqual(quantize_cents(Decimal("0.125")), Decimal("0.13"))

    def test_half_rounds_away_from_zero_higher_decimal(self):
        self.assertEqual(quantize_cents(Decimal("2.685")), Decimal("2.69"))

    def test_already_at_two_decimals_unchanged(self):
        self.assertEqual(quantize_cents(Decimal("5.00")), Decimal("5.00"))


class TestCalculateTotal(unittest.TestCase):
    def test_empty_cart_is_zero(self):
        self.assertEqual(calculate_total([]), Decimal("0.00"))

    def test_no_discount_no_tax(self):
        items = [LineItem("a", Decimal("19.99"), 3)]
        self.assertEqual(calculate_total(items), Decimal("59.97"))

    def test_discount_then_tax(self):
        # 100.00 subtotal, 10% discount -> 90.00, 10% tax -> 99.00
        items = [LineItem("w", Decimal("100.00"), 1)]
        self.assertEqual(
            calculate_total(items,
                            discount_percent=Decimal("10"),
                            tax_rate=Decimal("0.10")),
            Decimal("99.00"),
        )

    def test_realistic_mixed(self):
        # 2 x 19.99 = 39.98
        # + 1 x 4.50 =  4.50   -> subtotal 44.48
        # - 15% off           -> 37.808
        # + 7.25% tax         -> 40.548080
        # quantize to cents   -> 40.55
        items = [
            LineItem("book", Decimal("19.99"), 2),
            LineItem("pen",  Decimal("4.50"), 1),
        ]
        self.assertEqual(
            calculate_total(items,
                            discount_percent=Decimal("15"),
                            tax_rate=Decimal("0.0725")),
            Decimal("40.55"),
        )

    def test_precision_bug_zero_one_plus_zero_two(self):
        """The classic 0.1 + 0.2 != 0.3 bug would fail this test if the
        implementation ever converted to float in the middle."""
        items = [
            LineItem("a", Decimal("0.10"), 1),
            LineItem("b", Decimal("0.20"), 1),
        ]
        self.assertEqual(calculate_total(items), Decimal("0.30"))


if __name__ == "__main__":
    unittest.main()
