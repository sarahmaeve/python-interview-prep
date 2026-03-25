"""Inventory management service that talks to external systems.

This module is CORRECT -- do not modify it.
The bugs are in the test file.
"""

import json
from datetime import datetime
from urllib.request import urlopen


class Database:
    """Represents an external database connection."""

    def query(self, sql, params=None):
        raise NotImplementedError("Real DB not available")

    def execute(self, sql, params=None):
        raise NotImplementedError("Real DB not available")


def get_current_time():
    """Wrapper around datetime.now() for testability."""
    return datetime.now()


class InventoryService:
    def __init__(self, db):
        self.db = db

    def get_stock(self, product_id):
        """Query the database for current stock level."""
        rows = self.db.query(
            "SELECT quantity FROM inventory WHERE product_id = ?",
            (product_id,),
        )
        if not rows:
            return 0
        return rows[0]["quantity"]

    def restock(self, product_id, quantity):
        """Add stock. Returns the new total."""
        current = self.get_stock(product_id)
        new_total = current + quantity
        self.db.execute(
            "UPDATE inventory SET quantity = ? WHERE product_id = ?",
            (new_total, product_id),
        )
        return new_total

    def transfer(self, from_id, to_id, quantity):
        """Transfer stock between products.

        Returns True on success, False if insufficient stock.
        """
        from_stock = self.get_stock(from_id)
        if from_stock < quantity:
            return False
        self.db.execute(
            "UPDATE inventory SET quantity = ? WHERE product_id = ?",
            (from_stock - quantity, from_id),
        )
        to_stock = self.get_stock(to_id)
        self.db.execute(
            "UPDATE inventory SET quantity = ? WHERE product_id = ?",
            (to_stock + quantity, to_id),
        )
        return True

    def get_low_stock_report(self, threshold=10):
        """Query for all products below threshold."""
        rows = self.db.query(
            "SELECT product_id, quantity FROM inventory WHERE quantity < ?",
            (threshold,),
        )
        return rows if rows else []

    def get_stock_with_timestamp(self, product_id):
        """Return stock level with current timestamp."""
        stock = self.get_stock(product_id)
        now = get_current_time()
        return {
            "product_id": product_id,
            "quantity": stock,
            "checked_at": now.isoformat(),
        }

    def fetch_supplier_price(self, product_id):
        """Fetch current supplier price from external API."""
        url = f"https://supplier.example.com/api/price/{product_id}"
        response = urlopen(url)
        data = json.loads(response.read().decode())
        return data["price"]

    def should_reorder(self, product_id, max_price=50.0):
        """Check if we should reorder: stock below 5 AND price under max_price."""
        stock = self.get_stock(product_id)
        if stock >= 5:
            return False
        price = self.fetch_supplier_price(product_id)
        return price <= max_price
