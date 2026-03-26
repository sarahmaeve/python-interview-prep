import unittest
from string_calculator import StringCalculator


class TestBasicAddition(unittest.TestCase):
    """Tests for basic number parsing and addition."""

    def setUp(self):
        self.calc = StringCalculator()

    def test_empty_string_returns_zero(self):
        """An empty string should return 0."""
        pass

    def test_single_number_returns_its_value(self):
        """A single number like '5' should return 5."""
        pass

    def test_two_numbers_comma_separated(self):
        """'1,2' should return 3."""
        pass

    def test_multiple_numbers(self):
        """'1,2,3,4,5' should return 15."""
        pass


class TestDelimiters(unittest.TestCase):
    """Tests for different delimiter handling."""

    def setUp(self):
        self.calc = StringCalculator()

    def test_newline_as_delimiter(self):
        """Newlines between numbers should work: '1\\n2,3' should return 6."""
        pass

    def test_custom_delimiter(self):
        """'//;\\n1;2;3' should use ';' as delimiter and return 6."""
        pass


class TestEdgeCases(unittest.TestCase):
    """Tests for special rules and error handling."""

    def setUp(self):
        self.calc = StringCalculator()

    def test_negative_numbers_raise_value_error(self):
        """Negative numbers should raise ValueError with all negatives listed."""
        pass

    def test_multiple_negatives_all_listed(self):
        """'1,-2,3,-4' should list both -2 and -4 in the error message."""
        pass

    def test_numbers_over_1000_are_ignored(self):
        """'2,1001' should return 2 (1001 is ignored)."""
        pass

    def test_1000_is_not_ignored(self):
        """1000 should be included (only numbers GREATER than 1000 are ignored)."""
        pass


if __name__ == "__main__":
    unittest.main()
