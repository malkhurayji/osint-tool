"""Gravatar avatar lookup. Free, no API key: Gravatar's own API contract is
to hash the address and return 404 if no profile image is registered for it."""

from __future__ import annotations

import hashlib

import httpx

from osint_tool.models import Finding, Status

SOURCE = "Gravatar"


async def check(client: httpx.AsyncClient, email: str) -> Finding:
    normalized = email.strip().lower()
    # MD5 here is Gravatar's documented hashing scheme, not a security control.
    digest = hashlib.md5(normalized.encode(), usedforsecurity=False).hexdigest()
    url = f"https://www.gravatar.com/avatar/{digest}?d=404"

    try:
        resp = await client.get(url)
    except httpx.RequestError as exc:
        return Finding(source=SOURCE, query=email, status=Status.ERROR, detail=str(exc))

    if resp.status_code == 200:
        return Finding(
            source=SOURCE,
            query=email,
            status=Status.FOUND,
            url=f"https://www.gravatar.com/{digest}",
            detail="a Gravatar profile image is registered for this address",
        )
    if resp.status_code == 404:
        return Finding(source=SOURCE, query=email, status=Status.NOT_FOUND)
    return Finding(source=SOURCE, query=email, status=Status.ERROR, detail=f"unexpected HTTP {resp.status_code}")


def make_task(email: str):
    async def task(client: httpx.AsyncClient) -> Finding:
        return await check(client, email)

    task.source_name = SOURCE
    task.query = email
    return task
