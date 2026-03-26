import json
from urllib.request import urlopen


class PaymentClient:
    """External payment service."""

    def charge(self, customer_id, amount):
        raise NotImplementedError

    def refund(self, charge_id):
        raise NotImplementedError


class InventoryClient:
    """External inventory service."""

    def check_stock(self, product_id):
        """Returns int: number of units available."""
        raise NotImplementedError

    def reserve(self, product_id, quantity):
        """Returns str: reservation_id."""
        raise NotImplementedError

    def release(self, reservation_id):
        raise NotImplementedError


class OrderService:
    def __init__(self, payment_client, inventory_client):
        self.payment = payment_client
        self.inventory = inventory_client

    def place_order(self, customer_id, product_id, quantity, price_per_unit):
        """Place an order. Returns dict with order details.

        Steps:
        1. Check stock -- if insufficient, return {"status": "out_of_stock"}
        2. Reserve inventory
        3. Charge payment (amount = quantity * price_per_unit)
        4. If payment fails, release the reservation and return {"status": "payment_failed"}
        5. Return {"status": "confirmed", "reservation_id": ..., "charge_id": ...}
        """
        stock = self.inventory.check_stock(product_id)
        if stock < quantity:
            return {"status": "out_of_stock"}

        reservation_id = self.inventory.reserve(product_id, quantity)

        try:
            amount = quantity * price_per_unit
            charge_id = self.payment.charge(customer_id, amount)
        except Exception:
            self.inventory.release(reservation_id)
            return {"status": "payment_failed"}

        return {
            "status": "confirmed",
            "reservation_id": reservation_id,
            "charge_id": charge_id,
        }

    def cancel_order(self, reservation_id, charge_id):
        """Cancel an order: release inventory and refund payment.
        Returns True if both succeed, False otherwise."""
        try:
            self.inventory.release(reservation_id)
            self.payment.refund(charge_id)
            return True
        except Exception:
            return False

    def notify_customer(self, customer_id, message):
        """Send a notification via external webhook (uses urlopen directly)."""
        url = "https://notifications.example.com/send"
        payload = json.dumps({"customer_id": customer_id, "message": message}).encode()
        response = urlopen(url, data=payload)
        return response.status == 200
