"""Builds the list of fan-out tasks for a given query type."""

from __future__ import annotations

from osint_tool.config import Config
from osint_tool.engine import Task
from osint_tool.sources.email import disposable, emailrep, gravatar, hibp, hunter, mx_lookup
from osint_tool.sources.username.checker import make_task as make_username_task
from osint_tool.sources.username.sites import SITES


def build_username_tasks(username: str) -> list[Task]:
    return [make_username_task(site, username) for site in SITES]


def build_email_tasks(email: str, config: Config) -> list[Task]:
    return [
        gravatar.make_task(email),
        mx_lookup.make_task(email),
        disposable.make_task(email),
        emailrep.make_task(email, config),
        hunter.make_task(email, config),
        hibp.make_task(email, config),
    ]
