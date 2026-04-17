"""
Guide 12 — Asyncio and AsyncMock
=================================
Run:  python guides/12_async_and_testing.py

Asynchronous Python is everywhere in 2025 production code: async web
frameworks (FastAPI, Starlette), async DB drivers (asyncpg, aiosqlite),
async HTTP (httpx, aiohttp).  Interview panels ask about it because it's
where the subtle bugs live.

This guide covers:
  - What `async def` actually returns (spoiler: not the value)
  - await, asyncio.run, and the event loop
  - asyncio.gather and asyncio.TaskGroup (3.11+)
  - asyncio.timeout (3.11+) — the modern way to bound an await
  - AsyncMock — mocking async code so tests don't need a live event loop
  - unittest.IsolatedAsyncioTestCase — running async tests in unittest

TABLE OF CONTENTS
  1. What async def gives you                 (line ~40)
  2. await and asyncio.run                    (line ~90)
  3. Concurrency: gather and TaskGroup (3.11) (line ~140)
  4. asyncio.timeout (3.11+)                  (line ~215)
  5. Common bugs in async code                (line ~270)
  6. AsyncMock                                (line ~340)
  7. Testing async code with unittest          (line ~410)
"""

from __future__ import annotations

import asyncio
import time
import unittest
from unittest.mock import AsyncMock


# ============================================================================
# 1. WHAT async def GIVES YOU
# ============================================================================
#
# An `async def` function does NOT return the function's value when called.
# It returns a COROUTINE OBJECT.  To get the value, something has to RUN
# the coroutine — either `await` it from another coroutine, or hand it to
# asyncio.run() from synchronous code.
#
# The most common interview bug: calling an async function from sync code
# without awaiting.  You get back a coroutine that warns "coroutine was
# never awaited" and quietly never runs.


async def greet(name: str) -> str:
    return f"hello {name}"


def demo_coroutine_objects() -> None:
    print("=" * 60)
    print("1. What `async def` gives you")
    print("=" * 60)

    # Calling greet(...) does NOT run greet.
    coro = greet("ada")
    print(f"  greet('ada') returned: {coro!r}")
    print("  (note: it's a coroutine — the body has not run yet)")

    # asyncio.run drives the coroutine to completion and returns the value.
    result = asyncio.run(greet("ada"))
    print(f"  asyncio.run(greet('ada')) = {result!r}")
    print()


# ============================================================================
# 2. await AND asyncio.run
# ============================================================================
#
# Inside an async function, `await` pauses until the awaited thing completes.
# Outside of any async function, asyncio.run(coro) is the entry point.
#
# RULE: you can only `await` inside `async def`.  Forgetting this is the
# second-most-common async bug: `result = some_async_fn(x)` where you
# meant `result = await some_async_fn(x)`.


async def fetch_one(name: str, delay: float) -> str:
    # asyncio.sleep is the non-blocking cousin of time.sleep.
    await asyncio.sleep(delay)
    return f"fetched:{name}"


async def fetch_sequential() -> list[str]:
    # Sequential — each await blocks the next.  Total: sum of delays.
    a = await fetch_one("a", 0.02)
    b = await fetch_one("b", 0.02)
    return [a, b]


def demo_await_and_run() -> None:
    print("=" * 60)
    print("2. await and asyncio.run")
    print("=" * 60)

    t0 = time.perf_counter()
    results = asyncio.run(fetch_sequential())
    elapsed = time.perf_counter() - t0
    assert results == ["fetched:a", "fetched:b"]
    print(f"  sequential result: {results}")
    print(f"  elapsed: {elapsed * 1000:.0f}ms  (≈ sum of 2 × 20ms)")
    print()


# ============================================================================
# 3. CONCURRENCY: asyncio.gather AND asyncio.TaskGroup (3.11+)
# ============================================================================
#
# gather(*coros) runs them concurrently and returns a list of results in
# the original order.  If any coroutine raises and return_exceptions is
# False (the default), gather re-raises — but the other tasks keep running
# and their exceptions are swallowed.  This surprises people.
#
# TaskGroup (new in 3.11) is the *preferred* modern form.  It's
# structured concurrency: the `async with` block waits for every task to
# finish, and any exception cancels siblings and propagates out cleanly.
# If multiple tasks raise, you get an ExceptionGroup with all of them.


async def fetch_concurrent_gather() -> list[str]:
    # All tasks run concurrently.  Total: max of delays, not sum.
    return await asyncio.gather(
        fetch_one("a", 0.02),
        fetch_one("b", 0.02),
        fetch_one("c", 0.02),
    )


async def fetch_concurrent_taskgroup() -> list[str]:
    async with asyncio.TaskGroup() as tg:
        ta = tg.create_task(fetch_one("a", 0.02))
        tb = tg.create_task(fetch_one("b", 0.02))
        tc = tg.create_task(fetch_one("c", 0.02))
    # Results are available after the `async with` block completes.
    return [ta.result(), tb.result(), tc.result()]


def demo_concurrency() -> None:
    print("=" * 60)
    print("3. Concurrency: gather and TaskGroup")
    print("=" * 60)

    t0 = time.perf_counter()
    r = asyncio.run(fetch_concurrent_gather())
    elapsed = time.perf_counter() - t0
    print(f"  gather:    {r}")
    print(f"  elapsed:   {elapsed * 1000:.0f}ms  (≈ max of delays — concurrent)")

    t0 = time.perf_counter()
    r = asyncio.run(fetch_concurrent_taskgroup())
    elapsed = time.perf_counter() - t0
    print(f"  TaskGroup: {r}")
    print(f"  elapsed:   {elapsed * 1000:.0f}ms")

    # Exception behaviour of TaskGroup — the whole group raises on error.
    async def bad():
        await asyncio.sleep(0.01)
        raise RuntimeError("task failed")

    async def fine():
        await asyncio.sleep(0.02)
        return "ok"

    async def run_tg():
        async with asyncio.TaskGroup() as tg:
            tg.create_task(bad())
            tg.create_task(fine())

    try:
        asyncio.run(run_tg())
    except* RuntimeError as eg:   # PEP 654 `except*` — handle ExceptionGroup
        for exc in eg.exceptions:
            print(f"  TaskGroup raised: {type(exc).__name__}: {exc}")
    print()


# ============================================================================
# 4. asyncio.timeout (3.11+)
# ============================================================================
#
# Before 3.11 you used asyncio.wait_for(coro, timeout=...), which has
# subtle shutdown semantics.  3.11 added asyncio.timeout(s) — a CONTEXT
# MANAGER version that reads cleanly and cancels the body correctly.


async def eventually_returns(delay: float) -> str:
    await asyncio.sleep(delay)
    return "done"


async def with_timeout(body_delay: float, limit: float) -> str:
    try:
        async with asyncio.timeout(limit):
            return await eventually_returns(body_delay)
    except TimeoutError:
        return "timed out"


def demo_timeout() -> None:
    print("=" * 60)
    print("4. asyncio.timeout (3.11+)")
    print("=" * 60)

    # Inside the limit — completes.
    r = asyncio.run(with_timeout(body_delay=0.01, limit=0.1))
    print(f"  body=10ms, limit=100ms -> {r!r}")

    # Exceeds the limit — cancelled and handled.
    r = asyncio.run(with_timeout(body_delay=0.1, limit=0.01))
    print(f"  body=100ms, limit=10ms -> {r!r}")
    print()


# ============================================================================
# 5. COMMON BUGS IN ASYNC CODE
# ============================================================================


def demo_common_bugs() -> None:
    print("=" * 60)
    print("5. Common bugs in async code")
    print("=" * 60)

    # --- Bug A: forgetting to await ---
    # This "works" — no exception — but the async function never actually
    # runs.  Python prints a RuntimeWarning about it.  Subtle in interviews.
    import warnings
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        # Capture the coroutine, then discard it — the classic "forgot await"
        _ = greet("no-await")
        # Give it a chance to warn when garbage-collected:
        del _
        import gc; gc.collect()
    warning_names = [type(w.message).__name__ for w in caught]
    if "RuntimeWarning" in warning_names:
        print("  forgot-to-await produced a RuntimeWarning (Python is telling you)")
    else:
        print("  forgot-to-await: would produce a RuntimeWarning in real code")

    # --- Bug B: using time.sleep in async code ---
    # time.sleep BLOCKS the event loop.  In a server that means EVERY
    # concurrent request waits.  Always use asyncio.sleep in async code.
    print("  WRONG in async code:  time.sleep(1)     — blocks the event loop")
    print("  RIGHT in async code:  await asyncio.sleep(1) — yields to others")

    # --- Bug C: asyncio.gather's silent task errors ---
    # gather(..., return_exceptions=False) — the default — cancels the
    # current task on exception but lets siblings keep running; only the
    # first exception propagates.  Use return_exceptions=True to see all
    # outcomes, or (better) use asyncio.TaskGroup.
    print("  gather(a, b, c): if b raises, a and c still run; only b's exc")
    print("    propagates.  TaskGroup's ExceptionGroup is the modern answer.")
    print()


# ============================================================================
# 6. AsyncMock
# ============================================================================
#
# In Guide 05 we used MagicMock for sync code.  For async code, use
# AsyncMock — calling an AsyncMock returns a coroutine that resolves to
# the configured return_value / side_effect.


async def process_order(order_id: str, payment_client: AsyncMock,
                        inventory_client: AsyncMock) -> dict:
    stock = await inventory_client.check(order_id)
    if stock < 1:
        return {"status": "out_of_stock"}
    charge_id = await payment_client.charge(order_id, 100)
    return {"status": "ok", "charge_id": charge_id}


def demo_asyncmock() -> None:
    print("=" * 60)
    print("6. AsyncMock")
    print("=" * 60)

    # Configure the mocks.
    payment = AsyncMock()
    payment.charge.return_value = "ch_42"
    inventory = AsyncMock()
    inventory.check.return_value = 5

    result = asyncio.run(process_order("ord-1", payment, inventory))
    assert result == {"status": "ok", "charge_id": "ch_42"}
    print(f"  process_order in-stock  -> {result}")

    # Assert on awaits — same API as MagicMock but with "_awaited_".
    inventory.check.assert_awaited_once_with("ord-1")
    payment.charge.assert_awaited_once_with("ord-1", 100)

    # Exercise the out-of-stock path.
    inventory.reset_mock()
    payment.reset_mock()
    inventory.check.return_value = 0
    result = asyncio.run(process_order("ord-2", payment, inventory))
    assert result == {"status": "out_of_stock"}
    payment.charge.assert_not_awaited()
    print(f"  process_order out-of-stock -> {result}")
    print("  payment.charge was NOT awaited — assert_not_awaited confirmed it.")
    print()


# ============================================================================
# 7. TESTING ASYNC CODE WITH unittest
# ============================================================================
#
# Python 3.8+ ships unittest.IsolatedAsyncioTestCase.  Override async def
# test methods directly — the runner drives each one in its own event loop.
# In pytest, the equivalent is `pytest-asyncio` (install separately).


class TestAsyncOrderProcessing(unittest.IsolatedAsyncioTestCase):
    """Async tests using AsyncMock and IsolatedAsyncioTestCase."""

    async def asyncSetUp(self) -> None:
        # asyncSetUp and asyncTearDown are the async cousins of setUp.
        self.payment = AsyncMock()
        self.inventory = AsyncMock()

    async def test_in_stock_produces_charge(self) -> None:
        self.inventory.check.return_value = 3
        self.payment.charge.return_value = "ch_9"

        result = await process_order("ord-x", self.payment, self.inventory)

        self.assertEqual(result, {"status": "ok", "charge_id": "ch_9"})
        self.inventory.check.assert_awaited_once_with("ord-x")

    async def test_out_of_stock_skips_payment(self) -> None:
        self.inventory.check.return_value = 0

        result = await process_order("ord-y", self.payment, self.inventory)

        self.assertEqual(result, {"status": "out_of_stock"})
        self.payment.charge.assert_not_awaited()


def demo_async_unittest() -> None:
    print("=" * 60)
    print("7. Testing async code with unittest")
    print("=" * 60)

    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestAsyncOrderProcessing)
    import io as _io
    runner = unittest.TextTestRunner(stream=_io.StringIO(), verbosity=0)
    result = runner.run(suite)
    assert result.wasSuccessful()
    print(f"  ran {result.testsRun} async unittest tests — all passed")
    print("  (use unittest.IsolatedAsyncioTestCase + `async def test_...` methods)")
    print()


# ============================================================================
# MAIN
# ============================================================================


def main() -> None:
    demo_coroutine_objects()
    demo_await_and_run()
    demo_concurrency()
    demo_timeout()
    demo_common_bugs()
    demo_asyncmock()
    demo_async_unittest()

    print("=" * 60)
    print("KEY TAKEAWAYS")
    print("=" * 60)
    print("  1. `async def` returns a coroutine object.  Run it with")
    print("     asyncio.run() from sync code, or `await` it from another")
    print("     coroutine.  Never call it and ignore the return.")
    print("  2. Use asyncio.TaskGroup (3.11+) for structured concurrency.")
    print("     It cancels siblings cleanly and raises ExceptionGroup so")
    print("     you can see every failure with `except*`.")
    print("  3. asyncio.timeout(s) (3.11+) is the modern way to bound an await.")
    print("  4. NEVER call time.sleep() in async code — it blocks the loop.")
    print("  5. AsyncMock + IsolatedAsyncioTestCase are the stdlib tools for")
    print("     testing async logic without a live event loop.")
    print()
    print("  Next up:")
    print("    Exercise 29 — Async Retry Client  (retry, timeout, cancellation)")
    print()


if __name__ == "__main__":
    main()
