"""Correct tests for csv_report.py -- do NOT modify this file."""

import unittest
from unittest.mock import patch, mock_open, call, MagicMock
import io

from csv_report import read_sales_data, calculate_totals, generate_report


class TestReadSalesData(unittest.TestCase):
    """Tests for read_sales_data."""

    @patch("builtins.open", new_callable=mock_open,
           read_data="product,quantity,price\nWidget,10,2.50\nGadget,5,9.99\n")
    def test_returns_list_of_dicts(self, mock_file):
        result = read_sales_data("sales.csv")
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["product"], "Widget")
        self.assertEqual(result[0]["quantity"], 10)
        self.assertAlmostEqual(result[0]["price"], 2.50)

    @patch("builtins.open", new_callable=mock_open,
           read_data="product,quantity,price\nWidget,10,2.50\n")
    def test_file_is_properly_closed(self, mock_file):
        """The file handle must be closed after reading (via with statement)."""
        read_sales_data("sales.csv")
        # Verify context manager was used (with statement calls __enter__ and __exit__)
        handle = mock_file.return_value
        self.assertTrue(
            handle.__enter__.called,
            "File should be opened using a 'with' statement (context manager)"
        )
        self.assertTrue(
            handle.__exit__.called,
            "File context manager __exit__ should be called (use 'with' statement)"
        )

    @patch("builtins.open", new_callable=mock_open,
           read_data="product,quantity,price\n")
    def test_empty_csv_returns_empty_list(self, mock_file):
        result = read_sales_data("empty.csv")
        self.assertEqual(result, [])

    @patch("builtins.open", new_callable=mock_open,
           read_data="product,quantity,price\nAlpha,3,10.00\nBeta,7,5.50\nAlpha,2,10.00\n")
    def test_multiple_rows_parsed_correctly(self, mock_file):
        result = read_sales_data("multi.csv")
        self.assertEqual(len(result), 3)
        self.assertEqual(result[2]["product"], "Alpha")
        self.assertEqual(result[2]["quantity"], 2)


class TestCalculateTotals(unittest.TestCase):
    """Tests for calculate_totals."""

    def test_single_product_single_row(self):
        data = [{"product": "Widget", "quantity": 10, "price": 2.50}]
        totals = calculate_totals(data)
        self.assertAlmostEqual(totals["Widget"], 25.00)

    def test_multiple_rows_same_product_accumulates(self):
        """Revenue for the same product across multiple rows must be summed."""
        data = [
            {"product": "Widget", "quantity": 10, "price": 2.50},
            {"product": "Widget", "quantity": 5, "price": 2.50},
        ]
        totals = calculate_totals(data)
        # 10*2.50 + 5*2.50 = 25.00 + 12.50 = 37.50
        self.assertAlmostEqual(totals["Widget"], 37.50)

    def test_multiple_products(self):
        data = [
            {"product": "Widget", "quantity": 10, "price": 2.50},
            {"product": "Gadget", "quantity": 3, "price": 9.99},
            {"product": "Widget", "quantity": 4, "price": 2.50},
        ]
        totals = calculate_totals(data)
        self.assertAlmostEqual(totals["Widget"], 35.00)  # 10*2.5 + 4*2.5
        self.assertAlmostEqual(totals["Gadget"], 29.97)   # 3*9.99

    def test_empty_data(self):
        totals = calculate_totals([])
        self.assertEqual(totals, {})


class _NoCloseStringIO(io.StringIO):
    """A StringIO wrapper that ignores close(), so we can read after 'with'."""

    def close(self):
        pass  # Do not actually close, so getvalue() still works after exit


class TestGenerateReport(unittest.TestCase):
    """Tests for generate_report."""

    def test_report_written_correctly(self):
        csv_content = "product,quantity,price\nWidget,10,2.50\nGadget,3,9.99\n"
        output_buf = _NoCloseStringIO()

        def open_side_effect(path, *args, **kwargs):
            if path == "sales.csv":
                return io.StringIO(csv_content)
            elif path == "report.txt":
                return output_buf
            raise FileNotFoundError(path)

        with patch("builtins.open", side_effect=open_side_effect):
            generate_report("sales.csv", "report.txt")

        report = output_buf.getvalue()
        self.assertIn("Widget", report)
        self.assertIn("25.00", report)
        self.assertIn("Gadget", report)

    def test_file_not_found_propagates(self):
        """If the input CSV doesn't exist, FileNotFoundError must propagate.
        No output file should be written."""
        output_buf = _NoCloseStringIO()
        calls = []

        def open_side_effect(path, *args, **kwargs):
            calls.append(path)
            if path == "missing.csv":
                raise FileNotFoundError("missing.csv")
            elif path == "report.txt":
                return output_buf
            raise FileNotFoundError(path)

        with patch("builtins.open", side_effect=open_side_effect):
            with self.assertRaises(FileNotFoundError):
                generate_report("missing.csv", "report.txt")

        # The output file should never have been opened
        self.assertNotIn("report.txt", calls,
                         "Output file should not be opened when input is missing")


if __name__ == "__main__":
    unittest.main()
