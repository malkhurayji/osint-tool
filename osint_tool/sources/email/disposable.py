"""Local, offline check against a bundled list of known disposable/temp-mail
domains. No API key, no network call, no rate limit."""

from __future__ import annotations

from functools import lru_cache
from importlib import resources

import httpx

from osint_tool.models import Finding, Status

SOURCE = "Disposable Domain Check"


@lru_cache(maxsize=1)
def _load_domains() -> frozenset[str]:
    text = resources.files("osint_tool").joinpath("data", "disposable_domains.txt").read_text(encoding="utf-8")
    return frozenset(
        line.strip().lower() for line in text.splitlines() if line.strip() and not line.startswith("#")
    )


async def check(email: str) -> Finding:
    if "@" not in email:
        return Finding(source=SOURCE, query=email, status=Status.ERROR, detail="not a valid email address")

    domain = email.rsplit("@", 1)[-1].lower()
    domains = _load_domains()

    if domain in domains:
        return Finding(
            source=SOURCE,
            query=email,
            status=Status.FOUND,
            detail=f"{domain} is a known disposable/temp-mail domain",
        )
    return Finding(source=SOURCE, query=email, status=Status.NOT_FOUND, detail="not on the bundled disposable-domain list")


def make_task(email: str):
    async def task(client: httpx.AsyncClient) -> Finding:
        return await check(email)

    task.source_name = SOURCE
    task.query = email
    return task
