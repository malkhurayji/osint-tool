from __future__ import annotations

import httpx

from osint_tool.models import Finding, Status


async def check_site(client: httpx.AsyncClient, site: dict, username: str) -> Finding:
    url = site["url"].format(username)
    headers = site.get("headers") or {}

    try:
        resp = await client.get(url, headers=headers, follow_redirects=True)
    except httpx.RequestError as exc:
        return Finding(source=site["name"], query=username, status=Status.ERROR, url=url, detail=str(exc))

    method = site["method"]

    if method == "status":
        not_found_codes = site.get("not_found_codes", [404])
        if resp.status_code in not_found_codes:
            return Finding(source=site["name"], query=username, status=Status.NOT_FOUND, url=url)
        if resp.status_code < 400:
            return Finding(source=site["name"], query=username, status=Status.FOUND, url=url)
        return Finding(
            source=site["name"],
            query=username,
            status=Status.ERROR,
            url=url,
            detail=f"unexpected HTTP {resp.status_code}",
        )

    if method == "message":
        if resp.status_code >= 400:
            return Finding(
                source=site["name"],
                query=username,
                status=Status.ERROR,
                url=url,
                detail=f"unexpected HTTP {resp.status_code} (rate limited or site is temporarily blocking requests)",
            )

        text = resp.text
        not_found_marker = site.get("not_found_marker")
        found_marker = site.get("found_marker")

        if not_found_marker and not_found_marker in text:
            return Finding(source=site["name"], query=username, status=Status.NOT_FOUND, url=url)
        if found_marker and found_marker in text:
            return Finding(source=site["name"], query=username, status=Status.FOUND, url=url)
        # Only one marker type configured: its absence implies the opposite outcome.
        if not_found_marker and not found_marker:
            return Finding(source=site["name"], query=username, status=Status.FOUND, url=url)
        if found_marker and not not_found_marker:
            return Finding(source=site["name"], query=username, status=Status.NOT_FOUND, url=url)
        return Finding(
            source=site["name"],
            query=username,
            status=Status.ERROR,
            url=url,
            detail="response did not match either marker",
        )

    if method == "json_null":
        body = resp.text.strip()
        if body in ("null", ""):
            return Finding(source=site["name"], query=username, status=Status.NOT_FOUND, url=url)
        return Finding(source=site["name"], query=username, status=Status.FOUND, url=url)

    return Finding(source=site["name"], query=username, status=Status.ERROR, url=url, detail="unknown detection method")


def make_task(site: dict, username: str):
    async def task(client: httpx.AsyncClient) -> Finding:
        return await check_site(client, site, username)

    task.source_name = site["name"]
    task.query = username
    return task
