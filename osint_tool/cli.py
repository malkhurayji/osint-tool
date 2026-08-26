from __future__ import annotations

import asyncio
import re

import typer
from rich.console import Console

from osint_tool import config as config_module
from osint_tool.correlate import summarize
from osint_tool.engine import run_fanout
from osint_tool.output import render_json, render_table
from osint_tool.registry import build_email_tasks, build_username_tasks

app = typer.Typer(
    help="Multi-source OSINT lookup: fan a single query out across free-tier APIs and correlate the results.",
    add_completion=False,
)
console = Console()

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def _emit(findings, json_out: bool) -> None:
    summary = summarize(findings)
    if json_out:
        render_json(findings, summary)
    else:
        render_table(console, findings, summary)


@app.command()
def username(
    handle: str = typer.Argument(..., help="Username / handle to check across platforms"),
    json_out: bool = typer.Option(False, "--json", help="Emit machine-readable JSON instead of a table"),
    concurrency: int = typer.Option(15, "--concurrency", help="Max concurrent requests"),
) -> None:
    """Check a username across many platforms concurrently, no API keys required."""
    tasks = build_username_tasks(handle)
    findings = asyncio.run(run_fanout(tasks, concurrency=concurrency))
    _emit(findings, json_out)


@app.command()
def email(
    address: str = typer.Argument(..., help="Email address to check"),
    json_out: bool = typer.Option(False, "--json", help="Emit machine-readable JSON instead of a table"),
    concurrency: int = typer.Option(10, "--concurrency", help="Max concurrent requests"),
    derive_username: bool = typer.Option(
        True,
        "--derive-username/--no-derive-username",
        help="Also run the username fan-out against the email's local-part",
    ),
) -> None:
    """Check an email across breach/reputation/validity sources, with optional API-key sources."""
    if not EMAIL_RE.match(address):
        console.print(f"[bold red]'{address}' doesn't look like a valid email address[/bold red]")
        raise typer.Exit(code=1)

    cfg = config_module.load()
    tasks = build_email_tasks(address, cfg)
    findings = asyncio.run(run_fanout(tasks, concurrency=concurrency))

    if derive_username:
        candidate = address.split("@")[0]
        u_tasks = build_username_tasks(candidate)
        u_findings = asyncio.run(run_fanout(u_tasks, concurrency=concurrency))
        for f in u_findings:
            prefix = f"derived username '{candidate}' from email local-part"
            f.detail = f"{prefix} - {f.detail}" if f.detail else prefix
        findings = findings + u_findings

    _emit(findings, json_out)


@app.command()
def auto(
    query: str = typer.Argument(..., help="An email address or a username - the type is auto-detected"),
    json_out: bool = typer.Option(False, "--json", help="Emit machine-readable JSON instead of a table"),
) -> None:
    """Auto-detect whether QUERY is an email or a username and run the matching fan-out."""
    if EMAIL_RE.match(query):
        email(address=query, json_out=json_out)
    else:
        username(handle=query, json_out=json_out)


if __name__ == "__main__":
    app()
