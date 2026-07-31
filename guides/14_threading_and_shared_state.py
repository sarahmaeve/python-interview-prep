"""
Guide 14 — Threading and Shared State
======================================
Run:  python guides/14_threading_and_shared_state.py

Threads are useful when several blocking operations can overlap, but threads
share memory.  Correctness depends on protecting application-level invariants,
not on hoping an interpreter instruction happens to be atomic.

TABLE OF CONTENTS
  1. What the GIL does and does not guarantee
  2. A deterministic read-modify-write race
  3. Lock ownership and exception safety
  4. RLock, granularity, and deadlock prevention
  5. Single-owner state with queue.Queue
  6. Testing concurrent code
  7. Choosing threads, asyncio, or processes

OFFICIAL DOCUMENTATION
  threading:
    https://docs.python.org/3/library/threading.html
  Lock and RLock objects:
    https://docs.python.org/3/library/threading.html#lock-objects
  queue — synchronized queues:
    https://docs.python.org/3/library/queue.html
  concurrent.futures:
    https://docs.python.org/3/library/concurrent.futures.html
  Free-threaded Python HOWTO:
    https://docs.python.org/3/howto/free-threading-python.html
"""

from __future__ import annotations

import queue
import threading
from collections.abc import Callable

# ============================================================================
# 1. WHAT THE GIL DOES AND DOES NOT GUARANTEE
# ============================================================================
#
# In a traditional CPython build, the global interpreter lock (GIL) permits
# one thread at a time to execute Python bytecode.  Some CPython builds can run
# without it.  Neither model turns a multi-step application operation into one
# atomic transaction.
#
# "Read the balance, check a limit, then write a new balance" is one logical
# invariant even though it spans several language operations.  A context switch
# or a call that releases the GIL can expose intermediate state.  Correct code
# protects the whole invariant explicitly.


def explain_gil() -> None:
    print("=" * 60)
    print("1. What the GIL does and does not guarantee")
    print("=" * 60)
    print("  The GIL is an interpreter implementation detail, not a lock for")
    print("  your account, cache, registry, or other shared domain state.")
    print("  Ask: which values must be read and updated as one operation?")
    print()


# ============================================================================
# 2. A DETERMINISTIC READ-MODIFY-WRITE RACE
# ============================================================================
#
# Tests should coordinate a dangerous interleaving with Barrier or Event rather
# than depend on lucky scheduling or tiny sleeps.  Both threads below read the
# old value before either writes, so one update is predictably lost.


class CoordinatedUnsafeCounter:
    def __init__(self, participants: int) -> None:
        self.value = 0
        self._after_read = threading.Barrier(participants)

    def increment_once(self) -> None:
        old_value = self.value
        self._after_read.wait()
        self.value = old_value + 1


class LockedCounter:
    def __init__(self) -> None:
        self.value = 0
        self._lock = threading.Lock()

    def increment(self) -> None:
        with self._lock:
            self.value += 1


def start_and_join(threads: list[threading.Thread]) -> None:
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()


def demo_race_and_lock() -> None:
    print("=" * 60)
    print("2. A deterministic read-modify-write race")
    print("=" * 60)

    unsafe = CoordinatedUnsafeCounter(participants=2)
    start_and_join([
        threading.Thread(target=unsafe.increment_once),
        threading.Thread(target=unsafe.increment_once),
    ])
    assert unsafe.value == 1
    print(f"  two coordinated unsafe increments produced: {unsafe.value}")

    safe = LockedCounter()

    def increment_many() -> None:
        for _ in range(1_000):
            safe.increment()

    start_and_join([threading.Thread(target=increment_many) for _ in range(4)])
    assert safe.value == 4_000
    print(f"  four locked workers produced:             {safe.value}")
    print()


# ============================================================================
# 3. LOCK OWNERSHIP AND EXCEPTION SAFETY
# ============================================================================
#
# `with lock:` releases the lock on normal return and when an exception leaves
# the block.  A manual acquire/release pair needs a try/finally and is easier to
# get wrong.  Keep validation that participates in the invariant inside the
# same critical section as the update.


def demo_exception_safe_locking() -> None:
    print("=" * 60)
    print("3. Lock ownership and exception safety")
    print("=" * 60)

    lock = threading.Lock()
    try:
        with lock:
            raise RuntimeError("simulated failure while lock is held")
    except RuntimeError:
        pass

    acquired_after_error = lock.acquire(blocking=False)
    assert acquired_after_error
    lock.release()
    print(f"  context manager released lock after error: {acquired_after_error}")
    print("  Keep critical sections small, but not smaller than the invariant.")
    print()


# ============================================================================
# 4. RLock, GRANULARITY, AND DEADLOCK PREVENTION
# ============================================================================
#
# A plain Lock cannot be acquired twice by the same thread.  RLock is reentrant:
# it is useful when a synchronized public method calls another synchronized
# method on the same object.  It is not a general cure for deadlocks.
#
# Multiple locks increase concurrency but introduce ordering questions.  If
# one path acquires A then B while another acquires B then A, both can wait
# forever.  Establish one global acquisition order or redesign ownership.


class NestedLedger:
    def __init__(self) -> None:
        self._entries: list[int] = []
        self._lock = threading.RLock()

    def add(self, amount: int) -> None:
        with self._lock:
            self._entries.append(amount)

    def add_pair(self, first: int, second: int) -> None:
        with self._lock:
            self.add(first)
            self.add(second)

    def snapshot(self) -> tuple[int, ...]:
        with self._lock:
            return tuple(self._entries)


def demo_reentrant_lock() -> None:
    print("=" * 60)
    print("4. RLock, granularity, and deadlock prevention")
    print("=" * 60)
    ledger = NestedLedger()
    ledger.add_pair(4, -2)
    assert ledger.snapshot() == (4, -2)
    print(f"  nested synchronized calls completed: {ledger.snapshot()}")
    print("  With multiple locks, document and preserve one acquisition order.")
    print()


# ============================================================================
# 5. SINGLE-OWNER STATE WITH queue.Queue
# ============================================================================
#
# Locks are not the only design.  Several producer threads can send commands
# through a synchronized Queue while one consumer owns and mutates the state.
# This trades parallel state mutation for a clearer ownership boundary.


def demo_queue_ownership() -> None:
    print("=" * 60)
    print("5. Single-owner state with queue.Queue")
    print("=" * 60)

    commands: queue.Queue[str | None] = queue.Queue()
    processed: list[str] = []  # Mutated only by the consumer thread.

    def consume() -> None:
        while True:
            command = commands.get()
            try:
                if command is None:
                    return
                processed.append(command.upper())
            finally:
                commands.task_done()

    consumer = threading.Thread(target=consume)
    consumer.start()
    for command in ["index", "archive", "notify"]:
        commands.put(command)
    commands.put(None)
    commands.join()
    consumer.join()

    assert processed == ["INDEX", "ARCHIVE", "NOTIFY"]
    print(f"  commands processed by one state owner: {processed}")
    print()


# ============================================================================
# 6. TESTING CONCURRENT CODE
# ============================================================================


def explain_concurrency_tests() -> None:
    print("=" * 60)
    print("6. Testing concurrent code")
    print("=" * 60)
    print("  Prefer:")
    print("    - Barrier/Event to force a relevant ordering")
    print("    - invariant assertions over one incidental final schedule")
    print("    - timeouts on waits so a deadlock fails instead of hanging forever")
    print("    - stress and repeated runs as additional evidence")
    print("  Avoid using sleep as the primary coordination mechanism.")
    print("  A thousand passing schedules cannot prove every schedule is safe;")
    print("  code review and explicit ownership remain essential.")
    print()


# ============================================================================
# 7. CHOOSING THREADS, asyncio, OR PROCESSES
# ============================================================================


def describe_model(name: str, strength: str, caution: str) -> str:
    return f"  {name:<10} {strength:<34} {caution}"


def explain_concurrency_models() -> None:
    print("=" * 60)
    print("7. Choosing threads, asyncio, or processes")
    print("=" * 60)
    rows: list[Callable[[], str]] = [
        lambda: describe_model("threads", "blocking I/O; sync libraries", "shared-state races"),
        lambda: describe_model("asyncio", "many cooperative I/O tasks", "blocking the event loop"),
        lambda: describe_model("processes", "CPU-bound parallel work", "serialization and IPC"),
    ]
    for row in rows:
        print(row())
    print("  Choose from workload and ownership needs, not from a universal ranking.")
    print()


def main() -> None:
    explain_gil()
    demo_race_and_lock()
    demo_exception_safe_locking()
    demo_reentrant_lock()
    demo_queue_ownership()
    explain_concurrency_tests()
    explain_concurrency_models()

    print("=" * 60)
    print("KEY TAKEAWAYS")
    print("=" * 60)
    print("  1. Protect application invariants; do not rely on the GIL.")
    print("  2. Use `with lock:` so every exit path releases ownership.")
    print("  3. More locks require a consistent acquisition order.")
    print("  4. A queue can replace shared mutation with single-owner state.")
    print("  5. Coordinate test schedules explicitly with Barrier or Event.")


if __name__ == "__main__":
    main()
