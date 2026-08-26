import hashlib

import httpx
import pytest
import respx

from osint_tool.config import Config
from osint_tool.models import Status
from osint_tool.sources.email import disposable, gravatar, hunter, mx_lookup


@pytest.mark.asyncio
@respx.mock
async def test_gravatar_found():
    email = "alice@example.com"
    digest = hashlib.md5(email.encode(), usedforsecurity=False).hexdigest()
    respx.get(f"https://www.gravatar.com/avatar/{digest}").mock(return_value=httpx.Response(200))

    async with httpx.AsyncClient() as client:
        finding = await gravatar.check(client, email)

    assert finding.status == Status.FOUND


@pytest.mark.asyncio
@respx.mock
async def test_gravatar_not_found():
    email = "nobody@example.com"
    digest = hashlib.md5(email.encode(), usedforsecurity=False).hexdigest()
    respx.get(f"https://www.gravatar.com/avatar/{digest}").mock(return_value=httpx.Response(404))

    async with httpx.AsyncClient() as client:
        finding = await gravatar.check(client, email)

    assert finding.status == Status.NOT_FOUND


@pytest.mark.asyncio
async def test_disposable_known_domain():
    finding = await disposable.check("someone@mailinator.com")
    assert finding.status == Status.FOUND


@pytest.mark.asyncio
async def test_disposable_unknown_domain():
    finding = await disposable.check("someone@gmail.com")
    assert finding.status == Status.NOT_FOUND


@pytest.mark.asyncio
async def test_mx_lookup_invalid_email():
    finding = await mx_lookup.check("not-an-email")
    assert finding.status == Status.ERROR


@pytest.mark.asyncio
async def test_hunter_skipped_without_key():
    config = Config()
    async with httpx.AsyncClient() as client:
        finding = await hunter.check(client, "alice@example.com", config)
    assert finding.status == Status.SKIPPED
