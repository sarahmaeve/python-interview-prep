"""Notification Service -- contains 4 bugs for you to find and fix."""

import datetime


class SmtpClient:
    """Stub email client."""

    def send(self, to, subject, body):
        """Send an email (stub -- would connect to SMTP server)."""
        pass


class SmsGateway:
    """Stub SMS client."""

    def send_sms(self, to, message):
        """Send an SMS (stub -- would connect to SMS gateway)."""
        pass


class NotificationService:
    def __init__(self, email_client=None, sms_client=None, clock=None):
        self.email_client = email_client
        self.sms_client = sms_client
        self.clock = clock

    def send_email(self, to, subject, body):
        """Send an email using the email client."""
        # BUG 1: Creates a new SmtpClient instead of using self.email_client
        client = SmtpClient()
        client.send(to, subject, body)

    def send_sms(self, to, message):
        """Send an SMS using the SMS client."""
        self.sms_client.send_sms(to, message)

    def should_send(self, schedule):
        """Check if current time is within scheduled hours."""
        # BUG 2: Uses datetime.datetime.now() instead of self.clock()
        now = datetime.datetime.now()
        current_hour = now.hour
        return schedule["start_hour"] <= current_hour < schedule["end_hour"]

    def format_message(self, template, data):
        """Format a message template with data dict."""
        try:
            # BUG 3: Uses {user_name} (underscore) but data has "username" (no underscore)
            formatted = template.format(user_name=data.get("username", ""),
                                        order_id=data.get("order_id", ""),
                                        balance=data.get("balance", ""))
            return formatted
        except (KeyError, IndexError):
            return "Notification message"

    def send_batch(self, recipients, message):
        """Send message to all recipients, return summary."""
        sent = []
        failed = []
        for recipient in recipients:
            try:
                self.send_email(recipient, "Notification", message)
                sent.append(recipient)
            except Exception:
                failed.append(recipient)
                # BUG 4: Breaks out of loop on first failure
                break
        return {"sent": sent, "failed": failed}
