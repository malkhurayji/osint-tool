from __future__ import annotations

import json

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from osint_tool.correlate import Summary, dedupe
from osint_tool.models import Finding, Status

STATUS_STYLE = {
    Status.FOUND: "bold green",
    Status.NOT_FOUND: "dim",
    Status.ERROR: "bold red",
    Status.SKIPPED: "yellow",
}

STATUS_LABEL = {
    Status.FOUND: "FOUND",
    Status.NOT_FOUND: "not found",
    Status.ERROR: "error",
    Status.SKIPPED: "skipped",
}


def render_table(console: Console, findings: list[Finding], summary: Summary) -> None:
    findings = dedupe(findings)
    # Found first, then errors/skipped, then not-found, so the signal isn't buried.
    order = {Status.FOUND: 0, Status.ERROR: 1, Status.SKIPPED: 2, Status.NOT_FOUND: 3}
    findings = sorted(findings, key=lambda f: (order[f.status], f.source))

    table = Table(show_lines=False)
    table.add_column("Source")
    table.add_column("Status")
    table.add_column("URL / Detail", overflow="fold")

    for f in findings:
        style = STATUS_STYLE[f.status]
        label = STATUS_LABEL[f.status]
        detail = f.url or f.detail or ""
        if f.url and f.detail:
            detail = f"{f.url}\n[dim]{f.detail}[/dim]"
        table.add_row(f.source, f"[{style}]{label}[/{style}]", detail)

    console.print(table)

    counts_line = (
        f"[bold]{summary.found}[/bold] found, {summary.not_found} not found, "
        f"{summary.errors} errors, {summary.skipped} skipped "
        f"(out of {summary.total_checked} sources)"
    )
    summary_lines = [
        counts_line,
        f"confidence: [bold]{summary.confidence}%[/bold] of resolved checks came back positive",
    ]
    summary_lines.extend(summary.notes)
    console.print(Panel("\n".join(summary_lines), title="Summary", border_style="blue"))


def render_json(findings: list[Finding], summary: Summary) -> None:
    findings = dedupe(findings)
    payload = {
        "findings": [f.to_dict() for f in findings],
        "summary": {
            "total_checked": summary.total_checked,
            "found": summary.found,
            "not_found": summary.not_found,
            "errors": summary.errors,
            "skipped": summary.skipped,
            "confidence": summary.confidence,
            "notes": summary.notes,
        },
    }
    print(json.dumps(payload, indent=2))
