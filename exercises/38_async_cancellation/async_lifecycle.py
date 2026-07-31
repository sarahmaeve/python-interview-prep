"""Async operations with cancellation and lifecycle bugs."""

import asyncio
from collections.abc import Callable, Coroutine
from typing import Any, Protocol


class AsyncClient(Protocol):
    """The client contract used by the lifecycle helpers."""

    async def fetch(self, resource: str) -> str:
        """Fetch one resource."""

    async def close(self) -> None:
        """Release resources held by the client."""


async def fetch_optional(client: AsyncClient, resource: str) -> str | None:
    """Return fetched data, or None for an ordinary fetch failure."""
    try:
        return await client.fetch(resource)
    except BaseException:
        return None


async def fetch_and_close(client: AsyncClient, resource: str) -> str:
    """Fetch one resource and always close the owned client afterward."""
    result = await client.fetch(resource)
    await client.close()
    return result


async def run_batch(
    fetcher: Callable[[str], Coroutine[Any, Any, str]], resources: list[str]
) -> list[str]:
    """Run related fetches; a child failure must cancel all siblings."""
    tasks: list[asyncio.Task[str]] = [
        asyncio.create_task(fetcher(resource)) for resource in resources
    ]
    results = []
    for task in tasks:
        results.append(await task)
    return results
