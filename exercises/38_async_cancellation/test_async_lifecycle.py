"""Tests for cancellation, cleanup, and structured task ownership."""

import asyncio
import unittest

from async_lifecycle import fetch_and_close, fetch_optional, run_batch


class BlockingClient:
    def __init__(self) -> None:
        self.started = asyncio.Event()
        self.release = asyncio.Event()
        self.closed = False

    async def fetch(self, resource: str) -> str:
        self.started.set()
        await self.release.wait()
        return resource.upper()

    async def close(self) -> None:
        self.closed = True


class FailingClient:
    async def fetch(self, resource: str) -> str:
        raise LookupError(resource)

    async def close(self) -> None:
        pass


class ImmediateClient:
    def __init__(self) -> None:
        self.closed = False

    async def fetch(self, resource: str) -> str:
        return resource.upper()

    async def close(self) -> None:
        self.closed = True


class TestCancellation(unittest.IsolatedAsyncioTestCase):
    async def test_optional_fetch_propagates_cancellation(self):
        client = BlockingClient()
        task = asyncio.create_task(fetch_optional(client, "report"))
        await client.started.wait()

        task.cancel()

        with self.assertRaises(asyncio.CancelledError):
            await task

    async def test_optional_fetch_handles_ordinary_failure(self):
        self.assertIsNone(await fetch_optional(FailingClient(), "missing"))


class TestCleanup(unittest.IsolatedAsyncioTestCase):
    async def test_owned_client_closes_after_cancellation(self):
        client = BlockingClient()
        task = asyncio.create_task(fetch_and_close(client, "report"))
        await client.started.wait()

        task.cancel()

        with self.assertRaises(asyncio.CancelledError):
            await task
        self.assertTrue(client.closed)

    async def test_owned_client_closes_after_success(self):
        client = ImmediateClient()

        self.assertEqual(await fetch_and_close(client, "report"), "REPORT")
        self.assertTrue(client.closed)


class TestStructuredConcurrency(unittest.IsolatedAsyncioTestCase):
    async def test_sibling_is_cancelled_when_one_child_fails(self):
        slow_started = asyncio.Event()
        slow_release = asyncio.Event()
        slow_cancelled = asyncio.Event()

        async def fetcher(resource: str) -> str:
            if resource == "fail":
                await slow_started.wait()
                raise RuntimeError("fetch failed")

            slow_started.set()
            try:
                await slow_release.wait()
            except asyncio.CancelledError:
                slow_cancelled.set()
                raise
            return resource.upper()

        error: BaseException | None = None
        try:
            await run_batch(fetcher, ["fail", "slow"])
        except BaseException as exc:
            error = exc
        finally:
            slow_release.set()
            await asyncio.sleep(0)
            await asyncio.sleep(0)

        self.assertIsInstance(error, ExceptionGroup)
        self.assertTrue(slow_cancelled.is_set())

    async def test_batch_preserves_input_order_after_success(self):
        async def fetcher(resource: str) -> str:
            await asyncio.sleep(0)
            return resource.upper()

        result = await run_batch(fetcher, ["first", "second", "third"])

        self.assertEqual(result, ["FIRST", "SECOND", "THIRD"])


if __name__ == "__main__":
    unittest.main()
