"""Correlates and summarizes findings from a fan-out run.

This is deliberately simple: dedupe by (source, url) so a source checked
twice (e.g. once directly, once as a derived candidate) doesn't get double
counted, then roll the results up into a confidence score and a few
human-readable notes.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from osint_tool.models import Finding, Status


@dataclass
class Summary:
    total_checked: int
    found: int
    not_found: int
    errors: int
    skipped: int
    confidence: float  # percent of *resolved* checks (found+not_found) that came back "found"
    notes: list[str] = field(default_factory=list)


def dedupe(findings: list[Finding]) -> list[Finding]:
    seen: set[tuple[str, str]] = set()
    deduped: list[Finding] = []
    for f in findings:
        key = (f.source, f.url or f.query)
        if key in seen:
            continue
        seen.add(key)
        deduped.append(f)
    return deduped


def summarize(findings: list[Finding]) -> Summary:
    findings = dedupe(findings)

    found = sum(1 for f in findings if f.status == Status.FOUND)
    not_found = sum(1 for f in findings if f.status == Status.NOT_FOUND)
    errors = sum(1 for f in findings if f.status == Status.ERROR)
    skipped = sum(1 for f in findings if f.status == Status.SKIPPED)

    resolved = found + not_found
    confidence = round((found / resolved) * 100, 1) if resolved else 0.0

    notes: list[str] = []
    if found:
        sources = ", ".join(sorted(f.source for f in findings if f.status == Status.FOUND))
        notes.append(f"positive signal from: {sources}")
    if skipped:
        notes.append(f"{skipped} source(s) skipped - missing API key(s), see .env.example")
    if errors:
        notes.append(f"{errors} source(s) errored - likely transient (timeout, rate limit, or site change)")

    return Summary(
        total_checked=len(findings),
        found=found,
        not_found=not_found,
        errors=errors,
        skipped=skipped,
        confidence=confidence,
        notes=notes,
    )
