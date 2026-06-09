"""Tests for TicketOffice.

Do NOT modify this file.  Fix the bugs in ticket_office.py until every
test passes.

The concurrency tests shrink the interpreter's thread switch interval
(sys.setswitchinterval) so that thread interleavings that might take
thousands of requests to surface in production show up on every run.
"""

import sys
import threading
import unittest

from ticket_office import TicketOffice

# Tuning knobs for the concurrency tests.  Large enough to make unsafe
# interleavings show up on every run; small enough to keep the suite fast.
THREADS = 4
SALES_PER_THREAD = 20_000
CONTENTION_ROUNDS = 10


class TestBasicBehaviour(unittest.TestCase):
    """Single-threaded behavior — the easy part."""

    def test_sell_reduces_available(self):
        office = TicketOffice(10)
        self.assertTrue(office.sell(3))
        self.assertEqual(office.available, 7)
        self.assertEqual(office.total_sold, 3)

    def test_sell_insufficient_stock_returns_false(self):
        office = TicketOffice(2)
        self.assertFalse(office.sell(5))
        self.assertEqual(office.available, 2)
        self.assertEqual(office.total_sold, 0)

    def test_restock_adds_to_pool(self):
        office = TicketOffice(5)
        office.restock(7)
        self.assertEqual(office.available, 12)

    def test_restock_rejects_negative(self):
        office = TicketOffice(5)
        with self.assertRaises(ValueError):
            office.restock(-1)

    def test_channel_report_aggregates_sales(self):
        office = TicketOffice(10)
        office.sell(2, channel="web")
        office.sell(1, channel="phone")
        office.sell(3, channel="web")
        self.assertEqual(office.channel_report(), {"web": 5, "phone": 1})

    def test_revenue_tracks_sales_with_bulk_discount(self):
        office = TicketOffice(50, ticket_price=20.0)
        office.sell(2)                    # 2 x 20.00 = 40.00
        office.sell(10)                   # 10 x 20.00 x 0.9 = 180.00
        self.assertAlmostEqual(office.revenue, 220.0)


class ConcurrencyTestCase(unittest.TestCase):
    """Base class: force frequent thread switches so races surface."""

    def setUp(self):
        self._old_interval = sys.getswitchinterval()
        sys.setswitchinterval(1e-5)

    def tearDown(self):
        sys.setswitchinterval(self._old_interval)


class TestConcurrentSales(ConcurrencyTestCase):

    def test_concurrent_sales_account_for_every_ticket(self):
        """With a pool that never runs out, every successful sale must be
        reflected in BOTH counters: no sale may go missing."""
        pool = THREADS * SALES_PER_THREAD * 10
        office = TicketOffice(pool)
        barrier = threading.Barrier(THREADS)

        def buyer():
            barrier.wait()
            for _ in range(SALES_PER_THREAD):
                office.sell(1)

        threads = [threading.Thread(target=buyer) for _ in range(THREADS)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        expected_sold = THREADS * SALES_PER_THREAD
        self.assertEqual(
            office.available, pool - expected_sold,
            "available does not account for every concurrent sale — "
            "some sales were lost",
        )
        self.assertEqual(
            office.total_sold, expected_sold,
            "total_sold does not account for every concurrent sale",
        )

    def test_contended_sales_never_sell_more_than_the_pool(self):
        """When many threads compete for the last tickets, the office must
        never sell more tickets than the pool contains."""
        for round_no in range(CONTENTION_ROUNDS):
            with self.subTest(round=round_no):
                pool = 100
                office = TicketOffice(pool)
                n_threads = 8
                barrier = threading.Barrier(n_threads)

                def buyer(office=office, barrier=barrier):
                    barrier.wait()
                    for _ in range(50):
                        office.sell(1)

                threads = [threading.Thread(target=buyer)
                           for _ in range(n_threads)]
                for t in threads:
                    t.start()
                for t in threads:
                    t.join()

                self.assertEqual(
                    office.total_sold + office.available, pool,
                    "tickets were created or destroyed during the rush: "
                    f"sold={office.total_sold} available={office.available}",
                )
                self.assertEqual(
                    office.total_sold, pool,
                    "the office must sell exactly the pool, no more, no less",
                )


class TestRestockUnderFailure(ConcurrencyTestCase):

    def test_failed_restock_does_not_wedge_the_office(self):
        """After a restock() call fails, the office must remain usable —
        a failed call must not block every subsequent operation."""
        office = TicketOffice(10)
        with self.assertRaises(ValueError):
            office.restock(-1)

        done = threading.Event()

        def follow_up():
            office.restock(5)
            done.set()

        worker = threading.Thread(target=follow_up, daemon=True)
        worker.start()
        self.assertTrue(
            done.wait(timeout=2.0),
            "restock() never completed after an earlier call failed — "
            "the office is wedged",
        )
        self.assertEqual(office.available, 15)


class TestReportingDuringSales(ConcurrencyTestCase):

    def test_channel_report_is_safe_during_concurrent_sales(self):
        """channel_report() must work while other threads are selling —
        reporting is read-only and must never crash a request."""
        office = TicketOffice(10**9)
        stop = threading.Event()

        def seller(tid):
            i = 0
            while not stop.is_set():
                # A fresh channel name each time, like per-partner kiosks
                # registering on the fly.
                office.sell(1, channel=f"kiosk-{tid}-{i}")
                i += 1

        threads = [threading.Thread(target=seller, args=(tid,), daemon=True)
                   for tid in range(4)]
        for t in threads:
            t.start()
        try:
            for _ in range(300):
                report = office.channel_report()
                self.assertIsInstance(report, dict)
        finally:
            stop.set()
            for t in threads:
                t.join(timeout=2.0)


if __name__ == "__main__":
    unittest.main()
