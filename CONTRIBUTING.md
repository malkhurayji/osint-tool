# Contributing

PRs adding sources, fixing a broken detection rule, or improving accuracy are
very welcome. This project's whole value proposition is breadth of sources,
so it's designed to make adding one a small, mechanical change.

## Adding a username site

Add one entry to `osint_tool/sources/username/sites.py`:

```python
{
    "name": "SomeSite",
    "url": "https://somesite.com/{}",
    "method": "status",           # or "message" or "json_null"
    "not_found_codes": [404],     # for "status"
},
```

Detection methods, in order of preference:

1. **`status`** — the site returns a distinct HTTP status (usually 404) for
   a nonexistent user. Most reliable; prefer this when available.
2. **`message`** — the site always returns 200, but the body contains a
   different marker string depending on whether the profile exists. Set
   `found_marker` and/or `not_found_marker`.
3. **`json_null`** — a JSON API that returns the literal `null` (or an empty
   body) when the identifier doesn't exist.

**Please verify your entry against both a real, existing username and an
obviously-fake one** (e.g. a long random string) before submitting — a site
definition that always says "found" (or always "not found") is worse than no
entry at all. Mention what you tested in the PR description.

Sites that need a browser session or JS execution to distinguish a real
profile from a generic app shell (most of today's Twitter/X, Instagram,
TikTok) aren't a good fit for this detection model — if you find a reliable
no-browser signal for one, that's a great PR; a flaky one isn't.

## Adding an email (or other query-type) source

Follow the pattern in `osint_tool/sources/email/gravatar.py` (no key) or
`osint_tool/sources/email/hunter.py` (optional key):

1. A module with an async `check(...)` function returning a `Finding`.
2. A `make_task(...)` factory returning an async closure matching the
   `Task` signature in `osint_tool/engine.py`.
3. If the source needs a key: add the field to `Config` in
   `osint_tool/config.py`, document it in `.env.example`, and make the
   source return `Status.SKIPPED` (not `ERROR`) when the key is absent.
4. Register the task in `osint_tool/registry.py`.
5. Add a test in `tests/test_email_sources.py` using `respx` to mock the
   HTTP call — don't hit the real API in tests.

## New query types

A phone-number or domain/IP fan-out would follow the same shape as
`email`: a `sources/<type>/` package, a `build_<type>_tasks()` in
`registry.py`, and a CLI subcommand in `cli.py`. Open an issue first if
you're planning a new query type so the source list can be scoped together.

## Running the checks locally

```bash
pip install -e ".[dev]"
pytest
ruff check .
```
