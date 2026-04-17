"""Resource manager — contains 3 bugs around context manager discipline.

Two small resource types that *should* clean up after themselves:

  - ConnectionPool: a class-based context manager that must close the
    connection in every code path.
  - transaction(): a generator-based context manager that must roll back
    on error and commit on success.

Your job:
  - Find and fix 3 bugs.
  - All tests must pass without modification.

Relevant reading: guides/11_context_and_decorators.py Sections 1–4.
"""

from __future__ import annotations

from contextlib import contextmanager
from typing import Any


# ---------------------------------------------------------------------------
# ConnectionPool — class-based context manager
# ---------------------------------------------------------------------------


class FakeConnection:
    """A stand-in for a real DB/HTTP connection.  Tracks open/close state."""

    def __init__(self, name: str) -> None:
        self.name = name
        self.closed = False
        self._queries: list[str] = []

    def execute(self, query: str) -> str:
        if self.closed:
            raise RuntimeError(f"connection {self.name!r} is already closed")
        self._queries.append(query)
        return f"result for {query!r}"

    def close(self) -> None:
        self.closed = True


class ConnectionPool:
    """Lease a connection inside a `with` block.

    The connection MUST be closed when the block exits — whether the
    block finishes cleanly or raises.  Leaks here cause the test suite
    to accumulate connections and eventually exhaust the real backend
    in production.
    """

    def __init__(self, name: str) -> None:
        self._name = name
        self.conn: FakeConnection | None = None

    def __enter__(self) -> FakeConnection:
        self.conn = FakeConnection(self._name)
        return self.conn

    def __exit__(self, exc_type, exc_val, exc_tb) -> bool:
        if exc_type is None:
            self.conn.close()
        return False


# ---------------------------------------------------------------------------
# transaction — generator-based context manager
# ---------------------------------------------------------------------------


class FakeDatabase:
    """A tiny stand-in that records commits/rollbacks for testing."""

    def __init__(self) -> None:
        self.commits = 0
        self.rollbacks = 0
        self.open_transactions = 0

    def begin(self) -> None:
        self.open_transactions += 1

    def commit(self) -> None:
        self.commits += 1
        self.open_transactions -= 1

    def rollback(self) -> None:
        self.rollbacks += 1
        self.open_transactions -= 1


@contextmanager
def transaction(db: FakeDatabase):
    """Wrap a block of work in a database transaction.

    Semantics:
      - If the block completes normally, commit.
      - If the block raises, roll back and re-raise.
      - Either way, `db.open_transactions` must return to what it was.
    """
    db.begin()
    yield db
    db.commit()


# ---------------------------------------------------------------------------
# A small helper a caller might use naively.
# ---------------------------------------------------------------------------


def run_queries(pool: ConnectionPool, queries: list[str]) -> list[Any]:
    """Run each query against a freshly-leased connection from *pool*.

    The connection must be released when this function returns, whether
    the queries succeed or raise.
    """
    conn = pool.__enter__()
    results = [conn.execute(q) for q in queries]
    return results
