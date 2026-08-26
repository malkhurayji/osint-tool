"""Have I Been Pwned breach check. HIBP's breach-search API has required a
paid key since 2024 — set HIBP_API_KEY to enable. Skipped cleanly otherwise."""

from __future__ import annotations

import httpx

from osint_tool.config import Config
from osint_tool.models import Finding, Status

SOURCE = "HaveIBeenPwned"


async def check(client: httpx.AsyncClient, email: str, config: Config) -> Finding:
    if not config.hibp_api_key:
        return Finding(
            source=SOURCE,
            query=email,
            status=Status.SKIPPED,
            detail="set HIBP_API_KEY to enable (paid key, https://haveibeenpwned.com/API/Key)",
        )

    url = f"https://haveibeenpwned.com/api/v3/breachedaccount/{email}"
    headers = {"hibp-api-key": config.hibp_api_key}
    try:
        resp = await client.get(url, headers=headers, params={"truncateResponse": "true"})
    except httpx.RequestError as exc:
        return Finding(source=SOURCE, query=email, status=Status.ERROR, detail=str(exc))

    if resp.status_code == 404:
        return Finding(source=SOURCE, query=email, status=Status.NOT_FOUND, detail="no known breaches")
    if resp.status_code == 429:
        return Finding(source=SOURCE, query=email, status=Status.SKIPPED, detail="rate limited by HIBP")
    if resp.status_code != 200:
        return Finding(source=SOURCE, query=email, status=Status.ERROR, detail=f"unexpected HTTP {resp.status_code}")

    breaches = resp.json()
    names = [b.get("Name", "?") for b in breaches]
    return Finding(
        source=SOURCE,
        query=email,
        status=Status.FOUND,
        detail=f"found in {len(names)} breach(es): {', '.join(names[:5])}" + (" ..." if len(names) > 5 else ""),
        raw={"breaches": names},
    )


def make_task(email: str, config: Config):
    async def task(client: httpx.AsyncClient) -> Finding:
        return await check(client, email, config)

    task.source_name = SOURCE
    task.query = email
    return task
