import json
import time
from urllib.request import urlopen
from urllib.error import URLError


class PaymentGateway:
    """External payment gateway (injected dependency)."""

    def charge(self, card_token, amount_cents):
        """Charge a card. Returns a dict with 'transaction_id' and 'status'."""
        raise NotImplementedError("Real gateway not available in tests")

    def refund(self, transaction_id, amount_cents):
        """Refund a charge. Returns True on success."""
        raise NotImplementedError("Real gateway not available in tests")


class PaymentProcessor:
    def __init__(self, gateway, fraud_threshold=10000):
        self.gateway = gateway
        self.fraud_threshold = fraud_threshold
        self._log = []

    def process_payment(self, card_token, amount_cents):
        """Process a payment. Returns dict with transaction details.

        - If amount exceeds fraud_threshold, returns {"status": "flagged"}
          without charging.
        - On gateway error, returns {"status": "error", "message": str(error)}.
        - On success, returns the gateway response with "amount" added.
        """
        if amount_cents > self.fraud_threshold:
            self._log.append(("flagged", amount_cents))
            return {"status": "flagged", "amount": amount_cents}

        try:
            result = self.gateway.charge(card_token, amount_cents)
        except Exception as e:
            self._log.append(("error", str(e)))
            return {"status": "error", "message": str(e)}

        result["amount"] = amount_cents
        self._log.append(("success", result.get("transaction_id")))
        return result

    def process_refund(self, transaction_id, amount_cents):
        """Refund a payment. Returns True if gateway confirms, False otherwise."""
        try:
            return self.gateway.refund(transaction_id, amount_cents)
        except Exception:
            return False

    def get_exchange_rate(self, currency):
        """Fetch live exchange rate from an external API.

        Uses urllib at the module level (not injected -- must be patched).
        """
        url = f"https://api.rates.example.com/latest?base=USD&target={currency}"
        response = urlopen(url)
        data = json.loads(response.read().decode())
        return data["rate"]

    def process_international_payment(self, card_token, amount_local, currency):
        """Convert local currency to USD cents, then process."""
        rate = self.get_exchange_rate(currency)
        amount_usd_cents = int(amount_local * rate * 100)
        return self.process_payment(card_token, amount_usd_cents)

    def process_batch(self, payments):
        """Process a list of (card_token, amount_cents) tuples.

        Returns a summary dict: {"successful": [...], "failed": [...]}.
        """
        summary = {"successful": [], "failed": []}
        for token, amount in payments:
            result = self.process_payment(token, amount)
            if result.get("status") == "error":
                summary["failed"].append(token)
            else:
                summary["successful"].append(token)
        return summary

    def get_log(self):
        """Return a copy of the internal log."""
        return list(self._log)
