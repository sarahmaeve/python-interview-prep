"""Tests for InventoryService.

Six of these tests are correct. Four have mock-related bugs that cause them
to fail. Your task: find and fix the 4 buggy tests so all 10 pass.

Do NOT modify inventory_service.py -- the implementation is correct.
"""

import json
import unittest
from datetime import datetime
from unittest.mock import MagicMock, patch

from inventory_service import Database, InventoryService


# ---------------------------------------------------------------------------
# CORRECT tests (these 6 pass)
# ---------------------------------------------------------------------------


class TestGetStock(unittest.TestCase):
    def test_get_stock_returns_quantity(self):
        """Stock level is read from the first row returned by the DB."""
        mock_db = MagicMock(spec=Database)
        mock_db.query.return_value = [{"quantity": 42}]
        service = InventoryService(mock_db)

        result = service.get_stock("SKU1")

        self.assertEqual(result, 42)
        mock_db.query.assert_called_once()

    def test_get_stock_returns_zero_when_not_found(self):
        """Missing product should return 0, not raise."""
        mock_db = MagicMock(spec=Database)
        mock_db.query.return_value = []
        service = InventoryService(mock_db)

        result = service.get_stock("MISSING")

        self.assertEqual(result, 0)


class TestTransfer(unittest.TestCase):
    def test_transfer_insufficient_stock_returns_false(self):
        """Transfer more than available stock should return False."""
        mock_db = MagicMock(spec=Database)
        mock_db.query.return_value = [{"quantity": 3}]
        service = InventoryService(mock_db)

        result = service.transfer("A", "B", 10)

        self.assertFalse(result)
        # execute should never be called when stock is insufficient
        mock_db.execute.assert_not_called()

    def test_transfer_moves_stock_between_products(self):
        """Successful transfer updates both source and destination."""
        mock_db = MagicMock(spec=Database)
        # First query: from_stock=20, second query: to_stock=5
        mock_db.query.side_effect = [
            [{"quantity": 20}],
            [{"quantity": 5}],
        ]
        service = InventoryService(mock_db)

        result = service.transfer("A", "B", 7)

        self.assertTrue(result)
        self.assertEqual(mock_db.execute.call_count, 2)


class TestLowStockReport(unittest.TestCase):
    def test_low_stock_report_returns_rows(self):
        """Report returns all products below the threshold."""
        mock_db = MagicMock(spec=Database)
        mock_db.query.return_value = [
            {"product_id": "SKU1", "quantity": 2},
            {"product_id": "SKU3", "quantity": 8},
        ]
        service = InventoryService(mock_db)

        result = service.get_low_stock_report(threshold=10)

        self.assertEqual(len(result), 2)

    def test_low_stock_report_empty_when_none_returned(self):
        """When the DB returns None, the report should be an empty list."""
        mock_db = MagicMock(spec=Database)
        mock_db.query.return_value = None
        service = InventoryService(mock_db)

        result = service.get_low_stock_report()

        self.assertEqual(result, [])


# ---------------------------------------------------------------------------


class TestFetchSupplierPrice(unittest.TestCase):
    @patch("urllib.request.urlopen")
    def test_fetch_supplier_price(self, mock_urlopen):
        """Verify that fetch_supplier_price returns the price from the API."""
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps({"price": 29.99}).encode()
        mock_urlopen.return_value = mock_response

        mock_db = MagicMock(spec=Database)
        service = InventoryService(mock_db)

        price = service.fetch_supplier_price("SKU1")

        self.assertEqual(price, 29.99)
        mock_urlopen.assert_called_once_with(
            "https://supplier.example.com/api/price/SKU1"
        )


class TestRestock(unittest.TestCase):
    def test_restock_calls_execute(self):
        """After restocking, the service should write to the DB via execute."""
        mock_db = MagicMock()  # no spec=Database
        mock_db.query.return_value = [{"quantity": 10}]
        service = InventoryService(mock_db)

        result = service.restock("SKU1", 5)

        self.assertEqual(result, 15)
        # Assert the DB was written to — but there's a typo below!
        self.assertTrue(mock_db.exceute.called)


class TestGetStockWithTimestamp(unittest.TestCase):
    @patch("inventory_service.get_current_time")
    def test_get_stock_with_timestamp(self, mock_time):
        """Verify the response includes an ISO-formatted timestamp."""
        mock_time.return_value = "2026-03-25T10:00:00"

        mock_db = MagicMock(spec=Database)
        mock_db.query.return_value = [{"quantity": 17}]
        service = InventoryService(mock_db)

        result = service.get_stock_with_timestamp("SKU1")

        self.assertEqual(result["product_id"], "SKU1")
        self.assertEqual(result["quantity"], 17)
        self.assertEqual(result["checked_at"], "2026-03-25T10:00:00")


class TestShouldReorder(unittest.TestCase):
    @patch.object(InventoryService, "fetch_supplier_price")
    @patch.object(InventoryService, "get_stock")
    def test_should_reorder_checks_price(self, mock_fetch, mock_stock):
        """When stock < 5 and price <= max_price, should_reorder returns True."""
        # Intention: stock is 3 (below threshold) and price is 29.99 (under 50)
        mock_stock.return_value = 3
        mock_fetch.return_value = 29.99

        mock_db = MagicMock(spec=Database)
        service = InventoryService(mock_db)

        result = service.should_reorder("SKU1")

        self.assertTrue(result)
