"""Correct tests for notification_service.py -- do NOT modify this file."""

import unittest
from unittest.mock import MagicMock, patch
import datetime

from notification_service import NotificationService, SmtpClient, SmsGateway


class TestSendEmail(unittest.TestCase):
    """Tests that send_email uses the injected email client."""

    def test_email_sent_through_injected_client(self):
        mock_smtp = MagicMock(spec=SmtpClient)
        service = NotificationService(email_client=mock_smtp)
        service.send_email("alice@example.com", "Hello", "Body text")
        mock_smtp.send.assert_called_once_with(
            "alice@example.com", "Hello", "Body text"
        )

    def test_email_not_sent_through_new_instance(self):
        """Ensure the injected client is the one actually used, not a fresh SmtpClient."""
        mock_smtp = MagicMock(spec=SmtpClient)
        service = NotificationService(email_client=mock_smtp)
        service.send_email("bob@example.com", "Subject", "Body")
        # The injected mock must have been called
        self.assertTrue(mock_smtp.send.called)

    def test_email_passes_all_arguments(self):
        mock_smtp = MagicMock(spec=SmtpClient)
        service = NotificationService(email_client=mock_smtp)
        service.send_email("user@test.com", "Important", "Details here")
        args = mock_smtp.send.call_args[0]
        self.assertEqual(args, ("user@test.com", "Important", "Details here"))


class TestSendSms(unittest.TestCase):
    """Tests for send_sms."""

    def test_sms_sent_through_injected_client(self):
        mock_sms = MagicMock(spec=SmsGateway)
        service = NotificationService(sms_client=mock_sms)
        service.send_sms("+1234567890", "Hello via SMS")
        mock_sms.send_sms.assert_called_once_with("+1234567890", "Hello via SMS")


class TestShouldSend(unittest.TestCase):
    """Tests that should_send uses the injected clock."""

    def test_within_schedule_returns_true(self):
        fake_clock = MagicMock(
            return_value=datetime.datetime(2026, 3, 25, 14, 0, 0)
        )
        service = NotificationService(clock=fake_clock)
        schedule = {"start_hour": 9, "end_hour": 17}
        self.assertTrue(service.should_send(schedule))
        fake_clock.assert_called()

    def test_outside_schedule_returns_false(self):
        fake_clock = MagicMock(
            return_value=datetime.datetime(2026, 3, 25, 22, 0, 0)
        )
        service = NotificationService(clock=fake_clock)
        schedule = {"start_hour": 9, "end_hour": 17}
        self.assertFalse(service.should_send(schedule))

    def test_uses_injected_clock_not_system_time(self):
        """Verify the clock callable is actually invoked."""
        fake_clock = MagicMock(
            return_value=datetime.datetime(2026, 1, 1, 12, 0, 0)
        )
        service = NotificationService(clock=fake_clock)
        service.should_send({"start_hour": 9, "end_hour": 17})
        fake_clock.assert_called_once()


class TestFormatMessage(unittest.TestCase):
    """Tests for format_message."""

    def test_basic_template_formatting(self):
        service = NotificationService()
        result = service.format_message(
            "Hello {username}, your order #{order_id} is ready.",
            {"username": "Alice", "order_id": "42"},
        )
        self.assertEqual(result, "Hello Alice, your order #42 is ready.")

    def test_template_with_multiple_fields(self):
        service = NotificationService()
        result = service.format_message(
            "Dear {username}, balance: ${balance}",
            {"username": "Bob", "balance": "100.00"},
        )
        self.assertEqual(result, "Dear Bob, balance: $100.00")


class TestSendBatch(unittest.TestCase):
    """Tests for send_batch."""

    def test_all_succeed(self):
        mock_smtp = MagicMock(spec=SmtpClient)
        service = NotificationService(email_client=mock_smtp)
        recipients = ["a@test.com", "b@test.com", "c@test.com"]
        result = service.send_batch(recipients, "Hello all")
        self.assertEqual(sorted(result["sent"]), sorted(recipients))
        self.assertEqual(result["failed"], [])

    def test_continues_after_failure(self):
        """All recipients must be attempted even if some fail."""
        mock_smtp = MagicMock(spec=SmtpClient)
        # First call fails, second and third succeed
        mock_smtp.send.side_effect = [
            Exception("Connection lost"),
            None,
            None,
        ]
        service = NotificationService(email_client=mock_smtp)
        recipients = ["fail@test.com", "ok1@test.com", "ok2@test.com"]
        result = service.send_batch(recipients, "Hello")
        self.assertEqual(result["failed"], ["fail@test.com"])
        self.assertEqual(sorted(result["sent"]), ["ok1@test.com", "ok2@test.com"])
        # All three must have been attempted
        self.assertEqual(mock_smtp.send.call_count, 3)

    def test_all_fail(self):
        mock_smtp = MagicMock(spec=SmtpClient)
        mock_smtp.send.side_effect = Exception("Down")
        service = NotificationService(email_client=mock_smtp)
        recipients = ["a@test.com", "b@test.com"]
        result = service.send_batch(recipients, "Hello")
        self.assertEqual(sorted(result["failed"]), ["a@test.com", "b@test.com"])
        self.assertEqual(result["sent"], [])
        self.assertEqual(mock_smtp.send.call_count, 2)


if __name__ == "__main__":
    unittest.main()
