"""Tests for the resource manager.

Do NOT modify this file.  Fix the bugs in resource_manager.py until
every test passes.
"""

import unittest

from resource_manager import (
    ConnectionPool,
    FakeDatabase,
    run_queries,
    transaction,
)


class TestConnectionPool(unittest.TestCase):
    def test_closes_on_clean_exit(self):
        pool = ConnectionPool("db1")
        with pool as conn:
            conn.execute("SELECT 1")
        self.assertTrue(conn.closed, "connection must be closed after exit")

    def test_closes_on_exception(self):
        """The connection must be closed even when the with-block raises."""
        pool = ConnectionPool("db2")
        with self.assertRaises(ValueError):
            with pool as conn:
                conn.execute("SELECT 1")
                raise ValueError("boom")
        self.assertTrue(
            conn.closed,
            "connection must be closed on the error path too — "
            "a raise inside `with` should NOT leak the connection",
        )

    def test_nested_pools_are_independent(self):
        outer = ConnectionPool("outer")
        inner = ConnectionPool("inner")
        with outer as o:
            with inner as i:
                o.execute("SELECT outer")
                i.execute("SELECT inner")
            self.assertTrue(i.closed)
            self.assertFalse(o.closed)
        self.assertTrue(o.closed)


class TestTransaction(unittest.TestCase):

    def test_commit_on_success(self):
        db = FakeDatabase()
        with transaction(db) as conn:
            self.assertIs(conn, db)
        self.assertEqual(db.commits, 1)
        self.assertEqual(db.rollbacks, 0)
        self.assertEqual(db.open_transactions, 0)

    def test_rollback_on_exception(self):
        """If the block raises, the transaction must be rolled back."""
        db = FakeDatabase()
        with self.assertRaises(ValueError):
            with transaction(db):
                raise ValueError("bad input")
        self.assertEqual(db.commits, 0,
                         "commit must NOT be called when the block raised")
        self.assertEqual(db.rollbacks, 1,
                         "rollback must be called on the error path")

    def test_open_count_returns_to_zero_on_exception(self):
        db = FakeDatabase()
        with self.assertRaises(RuntimeError):
            with transaction(db):
                raise RuntimeError("boom")
        self.assertEqual(db.open_transactions, 0,
                         "open_transactions must return to zero even on error")

    def test_original_exception_propagates(self):
        db = FakeDatabase()
        with self.assertRaises(ValueError) as ctx:
            with transaction(db):
                raise ValueError("original")
        self.assertIn("original", str(ctx.exception))


class TestRunQueries(unittest.TestCase):

    def test_returns_results(self):
        pool = ConnectionPool("p")
        results = run_queries(pool, ["SELECT 1", "SELECT 2"])
        self.assertEqual(len(results), 2)

    def test_releases_connection_on_success(self):
        """run_queries must release the connection after success,
        not leak it by skipping __exit__."""
        pool = ConnectionPool("p")
        run_queries(pool, ["SELECT 1"])
        self.assertTrue(
            pool.conn.closed,
            "run_queries must release the pool's connection when it returns",
        )

    def test_does_not_leak_the_connection(self):
        """run_queries must release the pool's connection after every
        successful call."""
        pool = ConnectionPool("p")
        run_queries(pool, ["SELECT 1", "SELECT 2", "SELECT 3"])
        self.assertTrue(pool.conn.closed,
                        "run_queries must not leak the connection")


if __name__ == "__main__":
    unittest.main()
