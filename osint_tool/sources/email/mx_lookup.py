"""MX record lookup for the email's domain. Free, no API key, no network
service to rate-limit against besides DNS itself."""

from __future__ import annotations

import asyncio

import dns.exception
import dns.resolver
import httpx

from osint_tool.models import Finding, Status

SOURCE = "MX Lookup"


async def check(email: str) -> Finding:
    if "@" not in email:
        return Finding(source=SOURCE, query=email, status=Status.ERROR, detail="not a valid email address")

    domain = email.rsplit("@", 1)[-1]

    try:
        answers = await asyncio.to_thread(dns.resolver.resolve, domain, "MX")
    except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer):
        return Finding(
            source=SOURCE,
            query=email,
            status=Status.NOT_FOUND,
            detail=f"{domain} has no MX records - it likely can't receive mail",
        )
    except dns.exception.DNSException as exc:
        return Finding(source=SOURCE, query=email, status=Status.ERROR, detail=str(exc))

    hosts = sorted(str(r.exchange).rstrip(".") for r in answers)
    return Finding(
        source=SOURCE,
        query=email,
        status=Status.FOUND,
        detail=f"{len(hosts)} MX record(s): {', '.join(hosts[:3])}" + (" ..." if len(hosts) > 3 else ""),
        raw={"hosts": hosts},
    )


def make_task(email: str):
    async def task(client: httpx.AsyncClient) -> Finding:
        return await check(email)

    task.source_name = SOURCE
    task.query = email
    return task
