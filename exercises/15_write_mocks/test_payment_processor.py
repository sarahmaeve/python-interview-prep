import json
import unittest
from unittest.mock import MagicMock, patch, call

from payment_processor import PaymentGateway, PaymentProcessor


class TestPaymentProcessor(unittest.TestCase):
    """Tests for PaymentProcessor.

    Each test has its assertions written. Your job is to replace each
    # TODO: comment with the correct mock setup code so the test passes.
    """

    def test_successful_payment(self):
        """A successful charge returns transaction details with amount."""
        # TODO: Create a MagicMock for the gateway, using spec=PaymentGateway
        # so it only allows methods that PaymentGateway actually has.
        # Then configure its charge() method to return a dict:
        #   {"transaction_id": "tx_123", "status": "success"}

        processor = PaymentProcessor(gateway)
        result = processor.process_payment("tok_abc", 5000)

        self.assertEqual(result["transaction_id"], "tx_123")
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["amount"], 5000)
        gateway.charge.assert_called_once_with("tok_abc", 5000)

    def test_gateway_error_returns_error_status(self):
        """When the gateway raises, we get an error status back."""
        # TODO: Create a MagicMock for the gateway. Configure its charge()
        # method so that it RAISES a ConnectionError with the message
        # "Gateway down" every time it is called.

        processor = PaymentProcessor(gateway)
        result = processor.process_payment("tok_abc", 5000)

        self.assertEqual(result["status"], "error")
        self.assertIn("Gateway down", result["message"])

    def test_fraud_threshold_skips_gateway(self):
        """Payments above the fraud threshold are flagged without calling the gateway."""
        # TODO: Create a MagicMock for the gateway. No special configuration
        # is needed on charge() — the point is that it should never be called.
        # Process a payment of 50000 cents (above the default 10000 threshold).

        processor = PaymentProcessor(gateway)
        result = processor.process_payment("tok_abc", 50000)

        self.assertEqual(result["status"], "flagged")
        self.assertEqual(result["amount"], 50000)
        gateway.charge.assert_not_called()

    def test_refund_success(self):
        """A successful refund returns True and calls gateway.refund correctly."""
        # TODO: Create a MagicMock for the gateway with spec=PaymentGateway.
        # Configure its refund() method to return True.

        processor = PaymentProcessor(gateway)
        result = processor.process_refund("tx_123", 2500)

        self.assertTrue(result)
        gateway.refund.assert_called_once_with("tx_123", 2500)

    def test_refund_gateway_failure(self):
        """When the gateway raises during refund, we return False gracefully."""
        # TODO: Create a MagicMock for the gateway. Configure its refund()
        # method to raise an Exception with any message, simulating a
        # gateway failure.

        processor = PaymentProcessor(gateway)
        result = processor.process_refund("tx_123", 2500)

        self.assertFalse(result)

    @patch("payment_processor.urlopen")
    def test_get_exchange_rate_patches_urlopen(self, mock_urlopen):
        """Patching urlopen lets us control the HTTP response."""
        # TODO: Create a MagicMock that acts as the HTTP response object.
        # Configure the mock chain so that calling .read().decode() on it
        # returns the JSON string '{"rate": 0.85}'.
        # Then set mock_urlopen.return_value to your response mock.

        gateway = MagicMock(spec=PaymentGateway)
        processor = PaymentProcessor(gateway)
        rate = processor.get_exchange_rate("EUR")

        self.assertEqual(rate, 0.85)
        mock_urlopen.assert_called_once()

    def test_international_payment_converts_currency(self):
        """International payments convert local amount to USD cents."""
        # TODO: Two things to mock here:
        # 1. Create a MagicMock gateway (named "gateway") with spec=PaymentGateway.
        #    Configure charge() to return {"transaction_id": "tx_intl", "status": "success"}.
        # 2. Use patch.object(PaymentProcessor, "get_exchange_rate", return_value=...)
        #    as a context manager to mock get_exchange_rate so it returns 0.85
        #    without hitting the network. Put the call to
        #    process_international_payment INSIDE the context manager.
        #
        # Store the result in a variable called "result".
        # Expected: amount_local=100, rate=0.85 => int(100 * 0.85 * 100) = 8500

        self.assertEqual(result["amount"], 8500)
        gateway.charge.assert_called_once_with("tok_abc", 8500)

    def test_batch_processes_all_payments(self):
        """Batch processing handles a mix of successes and failures."""
        # TODO: Create a MagicMock for the gateway. Configure charge() with
        # a side_effect LIST of three items — one for each call in order:
        #   1st call: return {"transaction_id": "tx_1", "status": "success"}
        #   2nd call: raise ConnectionError("timeout")
        #   3rd call: return {"transaction_id": "tx_3", "status": "success"}
        # Hint: side_effect list items can be dicts (returned) or exceptions (raised).

        processor = PaymentProcessor(gateway)
        payments = [("tok_a", 1000), ("tok_b", 2000), ("tok_c", 3000)]
        summary = processor.process_batch(payments)

        self.assertEqual(summary["successful"], ["tok_a", "tok_c"])
        self.assertEqual(summary["failed"], ["tok_b"])
        self.assertEqual(gateway.charge.call_count, 3)

    def test_log_records_all_outcomes(self):
        """The internal log captures successes and errors in order."""
        # TODO: Create a MagicMock for the gateway. Configure charge() with
        # a side_effect list of two items:
        #   1st call: return {"transaction_id": "tx_1", "status": "success"}
        #   2nd call: raise ConnectionError("refused")

        processor = PaymentProcessor(gateway)
        processor.process_payment("tok_a", 1000)
        processor.process_payment("tok_b", 2000)
        log = processor.get_log()

        self.assertEqual(len(log), 2)
        self.assertEqual(log[0][0], "success")
        self.assertEqual(log[0][1], "tx_1")
        self.assertEqual(log[1][0], "error")
        self.assertIn("refused", log[1][1])

    def test_exchange_rate_with_context_manager_patch(self):
        """Using patch as a context manager to mock urlopen."""
        # TODO: Use 'with patch("payment_processor.urlopen") as mock_urlopen:'
        # Inside the context manager:
        #   1. Create a MagicMock response object.
        #   2. Configure it so that response.read.return_value.decode.return_value
        #      equals '{"rate": 1.25}'.
        #   3. Set mock_urlopen.return_value to your response mock.
        #   4. Create a PaymentProcessor with a MagicMock(spec=PaymentGateway).
        #   5. Call get_exchange_rate("GBP") and store the result in "rate".
        # All of the above must happen INSIDE the context manager.

        self.assertEqual(rate, 1.25)


if __name__ == "__main__":
    unittest.main()
