"""EmailRep.io reputation lookup. Works unauthenticated with a low free rate
limit; set EMAILREP_API_KEY for higher limits (see .env.example)."""

from __future__ import annotations

import httpx

from osint_tool.config import Config
from osint_tool.models import Finding, Status

SOURCE = "EmailRep"


async def check(client: httpx.AsyncClient, email: str, config: Config) -> Finding:
    headers = {}
    if config.emailrep_api_key:
        headers["Key"] = config.emailrep_api_key

    url = f"https://emailrep.io/{email}"
    try:
        resp = await client.get(url, headers=headers)
    except httpx.RequestError as exc:
        return Finding(source=SOURCE, query=email, status=Status.ERROR, detail=str(exc))

    if resp.status_code == 429:
        return Finding(source=SOURCE, query=email, status=Status.SKIPPED, detail="rate limited - try again later or set EMAILREP_API_KEY")
    if resp.status_code != 200:
        return Finding(source=SOURCE, query=email, status=Status.ERROR, detail=f"unexpected HTTP {resp.status_code}")

    data = resp.json()
    reputation = data.get("reputation", "unknown")
    suspicious = data.get("suspicious", False)
    details = data.get("details", {})
    flags = [k for k, v in details.items() if v is True]
    detail = f"reputation={reputation} suspicious={suspicious}"
    if flags:
        detail += f" flags={','.join(flags)}"

    status = Status.FOUND if suspicious or reputation != "none" else Status.NOT_FOUND
    return Finding(source=SOURCE, query=email, status=status, detail=detail, raw=data)


def make_task(email: str, config: Config):
    async def task(client: httpx.AsyncClient) -> Finding:
        return await check(client, email, config)

    task.source_name = SOURCE
    task.query = email
    return task
