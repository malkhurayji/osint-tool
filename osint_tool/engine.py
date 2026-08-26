"""Concurrent fan-out engine.

Each "task" is an async callable that takes a shared httpx.AsyncClient and
returns a Finding. run_fanout executes every task concurrently (bounded by a
semaphore so we stay polite to free-tier APIs) and never lets one source's
exception take down the whole run — failures become Finding(status=ERROR).
"""

from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable

import httpx

from osint_tool.models import Finding, Status

Task = Callable[[httpx.AsyncClient], Awaitable[Finding]]

DEFAULT_TIMEOUT = httpx.Timeout(10.0, connect=5.0)
DEFAULT_HEADERS = {
    # A generic bot UA gets a flat 403 from several platforms' anti-scraping
    # rules even for a single, well-behaved GET. A standard browser UA is
    # the accepted practice for this kind of read-only lookup tool (Sherlock,
    # theHarvester, etc. do the same) — it's not evading any auth or rate
    # limiting, just avoiding a UA-string blocklist false positive.
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/json;q=0.9,*/*;q=0.8",
}


async def run_fanout(tasks: list[Task], concurrency: int = 10) -> list[Finding]:
    if not tasks:
        return []

    semaphore = asyncio.Semaphore(max(1, concurrency))
    limits = httpx.Limits(max_connections=concurrency, max_keepalive_connections=concurrency)

    async with httpx.AsyncClient(
        timeout=DEFAULT_TIMEOUT, limits=limits, headers=DEFAULT_HEADERS
    ) as client:

        async def bound(task: Task) -> Finding:
            async with semaphore:
                try:
                    return await task(client)
                except Exception as exc:  # noqa: BLE001 -- a single misbehaving source must not sink the run
                    return Finding(
                        source=getattr(task, "source_name", "unknown"),
                        query=getattr(task, "query", ""),
                        status=Status.ERROR,
                        detail=f"unhandled error: {exc}",
                    )

        return await asyncio.gather(*(bound(t) for t in tasks))
