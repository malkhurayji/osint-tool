from osint_tool.correlate import dedupe, summarize
from osint_tool.models import Finding, Status


def test_dedupe_by_source_and_url():
    findings = [
        Finding(source="GitHub", query="a", status=Status.FOUND, url="https://github.com/a"),
        Finding(source="GitHub", query="a", status=Status.FOUND, url="https://github.com/a"),
        Finding(source="GitLab", query="a", status=Status.NOT_FOUND, url="https://gitlab.com/a"),
    ]
    result = dedupe(findings)
    assert len(result) == 2


def test_summarize_counts_and_confidence():
    findings = [
        Finding(source="A", query="q", status=Status.FOUND),
        Finding(source="B", query="q", status=Status.NOT_FOUND),
        Finding(source="C", query="q", status=Status.NOT_FOUND),
        Finding(source="D", query="q", status=Status.ERROR),
        Finding(source="E", query="q", status=Status.SKIPPED),
    ]
    summary = summarize(findings)
    assert summary.total_checked == 5
    assert summary.found == 1
    assert summary.not_found == 2
    assert summary.errors == 1
    assert summary.skipped == 1
    # 1 found out of 3 resolved (found+not_found) = 33.3%
    assert summary.confidence == 33.3


def test_summarize_empty():
    summary = summarize([])
    assert summary.total_checked == 0
    assert summary.confidence == 0.0
