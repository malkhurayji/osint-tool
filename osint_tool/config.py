"""Loads optional API keys from the environment (and a local .env file, if present).

None of these are required for the tool to run — every source that needs a key
degrades to Status.SKIPPED with a helpful message when the key is missing, so
the fan-out still works with zero configuration.
"""

from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Config:
    emailrep_api_key: str | None = None
    hunter_api_key: str | None = None
    hibp_api_key: str | None = None


def load() -> Config:
    return Config(
        emailrep_api_key=os.getenv("EMAILREP_API_KEY") or None,
        hunter_api_key=os.getenv("HUNTER_API_KEY") or None,
        hibp_api_key=os.getenv("HIBP_API_KEY") or None,
    )
