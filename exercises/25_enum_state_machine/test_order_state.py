"""Tests for the order state machine.

Do NOT modify this file.  Fix the bugs in order_state.py until every
test passes.
"""

import unittest

from order_state import (
    CANCELLED,
    DELIVERED,
    PAID,
    PENDING,
    SHIPPED,
    Order,
    summarize_orders,
)


class TestTransition(unittest.TestCase):
    def test_pending_to_paid(self):
        order = Order("ord-1")
        order.transition(PAID)
        self.assertEqual(order.status, PAID)

    def test_pending_to_cancelled(self):
        order = Order("ord-1")
        order.transition(CANCELLED)
        self.assertEqual(order.status, CANCELLED)

    def test_paid_to_shipped(self):
        order = Order("ord-1", status=PAID)
        order.transition(SHIPPED)
        self.assertEqual(order.status, SHIPPED)

    def test_shipped_to_delivered(self):
        order = Order("ord-1", status=SHIPPED)
        order.transition(DELIVERED)
        self.assertEqual(order.status, DELIVERED)

    def test_cannot_skip_paid(self):
        order = Order("ord-1")
        with self.assertRaises(ValueError):
            order.transition(SHIPPED)

    def test_cannot_uncancel(self):
        order = Order("ord-1", status=CANCELLED)
        with self.assertRaises(ValueError):
            order.transition(PAID)

    def test_history_records_previous_states(self):
        order = Order("ord-1")
        order.transition(PAID)
        order.transition(SHIPPED)
        order.transition(DELIVERED)
        self.assertEqual(order.history, [PENDING, PAID, SHIPPED])


class TestIsTerminal(unittest.TestCase):
    def test_delivered_is_terminal(self):
        order = Order("ord-1", status=DELIVERED)
        self.assertTrue(order.is_terminal())

    def test_cancelled_is_terminal(self):
        """CANCELLED orders must be terminal — they cannot transition."""
        order = Order("ord-1", status=CANCELLED)
        self.assertTrue(
            order.is_terminal(),
            "a cancelled order must report is_terminal() == True",
        )

    def test_pending_is_not_terminal(self):
        order = Order("ord-1")
        self.assertFalse(order.is_terminal())

    def test_paid_is_not_terminal(self):
        order = Order("ord-1", status=PAID)
        self.assertFalse(order.is_terminal())

    def test_shipped_is_not_terminal(self):
        order = Order("ord-1", status=SHIPPED)
        self.assertFalse(order.is_terminal())


class TestIsActive(unittest.TestCase):
    def test_pending_paid_shipped_are_active(self):
        for s in (PENDING, PAID, SHIPPED):
            with self.subTest(status=s):
                self.assertTrue(Order("o", status=s).is_active())

    def test_terminal_states_are_not_active(self):
        for s in (DELIVERED, CANCELLED):
            with self.subTest(status=s):
                self.assertFalse(Order("o", status=s).is_active())


class TestSummarizeOrders(unittest.TestCase):
    def test_counts_each_status(self):
        orders = [
            Order("a"),                        # pending
            Order("b"),                        # pending
            Order("c", status=PAID),
            Order("d", status=SHIPPED),
            Order("e", status=DELIVERED),
            Order("f", status=CANCELLED),
            Order("g", status=CANCELLED),
        ]
        summary = summarize_orders(orders)
        self.assertEqual(summary[PENDING], 2)
        self.assertEqual(summary[PAID], 1)
        self.assertEqual(summary[SHIPPED], 1)
        self.assertEqual(summary[DELIVERED], 1)
        self.assertEqual(summary[CANCELLED], 2)

    def test_empty_list(self):
        summary = summarize_orders([])
        # Every status should appear in the summary with a zero count.
        self.assertEqual(summary[PENDING], 0)
        self.assertEqual(summary[CANCELLED], 0)

    def test_single_cancelled_order(self):
        """Specifically exercise the CANCELLED path — a typo-in-key bug
        in the summary dict will cause a KeyError here."""
        summary = summarize_orders([Order("x", status=CANCELLED)])
        self.assertEqual(summary[CANCELLED], 1)


if __name__ == "__main__":
    unittest.main()
