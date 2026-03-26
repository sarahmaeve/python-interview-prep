import unittest
from unittest.mock import MagicMock, patch

from order_service import OrderService, PaymentClient, InventoryClient


class TestPlaceOrder(unittest.TestCase):
    """Tests for OrderService.place_order."""

    def test_successful_order(self):
        """When stock is available and payment succeeds, return confirmed status
        with reservation_id and charge_id."""
        pass

    def test_out_of_stock(self):
        """When stock is less than requested quantity, return out_of_stock status.
        Inventory.reserve should NOT be called."""
        pass

    def test_payment_failure_releases_reservation(self):
        """When payment raises an exception, the reservation should be released
        and status should be payment_failed."""
        pass

    def test_correct_amount_charged(self):
        """Verify that payment.charge is called with quantity * price_per_unit."""
        pass

    def test_reserve_called_with_correct_args(self):
        """Verify inventory.reserve is called with the right product_id and quantity."""
        pass


class TestCancelOrder(unittest.TestCase):
    """Tests for OrderService.cancel_order."""

    def test_successful_cancellation(self):
        """When both release and refund succeed, return True."""
        pass

    def test_failed_cancellation(self):
        """When release or refund raises, return False."""
        pass


class TestNotifyCustomer(unittest.TestCase):
    """Tests for OrderService.notify_customer (uses urlopen)."""

    def test_sends_notification_successfully(self):
        """Mock urlopen, configure it to return status 200.
        Verify notify_customer returns True."""
        pass

    def test_sends_correct_payload(self):
        """Verify urlopen is called with the correct URL and JSON payload
        containing customer_id and message."""
        pass

    def test_returns_false_on_non_200(self):
        """When the notification endpoint returns non-200, return False."""
        pass
