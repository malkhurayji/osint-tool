from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum


class Status(str, Enum):
    """Outcome of checking a single source."""

    FOUND = "found"
    NOT_FOUND = "not_found"
    ERROR = "error"
    SKIPPED = "skipped"  # e.g. an optional API key wasn't configured


@dataclass
class Finding:
    """A single source's answer for a single query."""

    source: str
    query: str
    status: Status
    url: str | None = None
    detail: str = ""
    raw: dict = field(default_factory=dict)
    checked_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    @property
    def found(self) -> bool:
        return self.status == Status.FOUND

    def to_dict(self) -> dict:
        return {
            "source": self.source,
            "query": self.query,
            "status": self.status.value,
            "url": self.url,
            "detail": self.detail,
            "raw": self.raw,
            "checked_at": self.checked_at,
        }
