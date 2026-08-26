"""Hunter.io email verifier. Requires a free API key (25 verifications/month
on the free tier) — set HUNTER_API_KEY. Skipped cleanly if not configured."""

from __future__ import annotations

import httpx

from osint_tool.config import Config
from osint_tool.models import Finding, Status

SOURCE = "Hunter.io Verifier"


async def check(client: httpx.AsyncClient, email: str, config: Config) -> Finding:
    if not config.hunter_api_key:
        return Finding(
            source=SOURCE,
            query=email,
            status=Status.SKIPPED,
            detail="set HUNTER_API_KEY to enable (free tier: 25 verifications/month)",
        )

    url = "https://api.hunter.io/v2/email-verifier"
    params = {"email": email, "api_key": config.hunter_api_key}
    try:
        resp = await client.get(url, params=params)
    except httpx.RequestError as exc:
        return Finding(source=SOURCE, query=email, status=Status.ERROR, detail=str(exc))

    if resp.status_code != 200:
        return Finding(source=SOURCE, query=email, status=Status.ERROR, detail=f"unexpected HTTP {resp.status_code}")

    data = resp.json().get("data", {})
    result = data.get("result", "unknown")
    score = data.get("score")
    status = Status.FOUND if result in ("deliverable", "risky") else Status.NOT_FOUND
    return Finding(source=SOURCE, query=email, status=status, detail=f"result={result} score={score}", raw=data)


def make_task(email: str, config: Config):
    async def task(client: httpx.AsyncClient) -> Finding:
        return await check(client, email, config)

    task.source_name = SOURCE
    task.query = email
    return task
