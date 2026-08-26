import httpx
import pytest
import respx

from osint_tool.models import Status
from osint_tool.sources.username.checker import check_site


@pytest.mark.asyncio
@respx.mock
async def test_status_method_found():
    site = {"name": "GitHub", "url": "https://example.test/{}", "method": "status", "not_found_codes": [404]}
    respx.get("https://example.test/alice").mock(return_value=httpx.Response(200))

    async with httpx.AsyncClient() as client:
        finding = await check_site(client, site, "alice")

    assert finding.status == Status.FOUND
    assert finding.url == "https://example.test/alice"


@pytest.mark.asyncio
@respx.mock
async def test_status_method_not_found():
    site = {"name": "GitHub", "url": "https://example.test/{}", "method": "status", "not_found_codes": [404]}
    respx.get("https://example.test/nobody").mock(return_value=httpx.Response(404))

    async with httpx.AsyncClient() as client:
        finding = await check_site(client, site, "nobody")

    assert finding.status == Status.NOT_FOUND


@pytest.mark.asyncio
@respx.mock
async def test_json_null_method():
    site = {"name": "HN", "url": "https://example.test/{}.json", "method": "json_null"}
    respx.get("https://example.test/ghost.json").mock(return_value=httpx.Response(200, text="null"))

    async with httpx.AsyncClient() as client:
        finding = await check_site(client, site, "ghost")

    assert finding.status == Status.NOT_FOUND


@pytest.mark.asyncio
@respx.mock
async def test_message_method_found_marker():
    site = {
        "name": "Steam",
        "url": "https://example.test/{}",
        "method": "message",
        "found_marker": "<steamID64>",
        "not_found_marker": "could not be found",
    }
    respx.get("https://example.test/bob").mock(return_value=httpx.Response(200, text="<steamID64>123</steamID64>"))

    async with httpx.AsyncClient() as client:
        finding = await check_site(client, site, "bob")

    assert finding.status == Status.FOUND


@pytest.mark.asyncio
@respx.mock
async def test_message_method_http_error_reports_error_not_not_found():
    site = {
        "name": "Steam",
        "url": "https://example.test/{}",
        "method": "message",
        "found_marker": "<steamID64>",
        "not_found_marker": "could not be found",
    }
    respx.get("https://example.test/bob").mock(return_value=httpx.Response(429, text="rate limited"))

    async with httpx.AsyncClient() as client:
        finding = await check_site(client, site, "bob")

    assert finding.status == Status.ERROR
    assert "429" in finding.detail


@pytest.mark.asyncio
@respx.mock
async def test_message_method_only_not_found_marker_falls_back_to_found():
    site = {
        "name": "WordPress.com",
        "url": "https://example.test/{}",
        "method": "message",
        "not_found_marker": "<title>Generic</title>",
    }
    respx.get("https://example.test/carol").mock(
        return_value=httpx.Response(200, text="<title>Carol's Blog</title>")
    )

    async with httpx.AsyncClient() as client:
        finding = await check_site(client, site, "carol")

    assert finding.status == Status.FOUND


@pytest.mark.asyncio
@respx.mock
async def test_request_error_becomes_error_status():
    site = {"name": "GitHub", "url": "https://example.test/{}", "method": "status", "not_found_codes": [404]}
    respx.get("https://example.test/alice").mock(side_effect=httpx.ConnectError("boom"))

    async with httpx.AsyncClient() as client:
        finding = await check_site(client, site, "alice")

    assert finding.status == Status.ERROR
