# osint-tool

Fan a single username or email out across a batch of **free-tier OSINT
sources** concurrently, then correlate the results into one summary with a
confidence score — instead of opening a dozen tabs and doing it by hand.

```
$ osint-tool username torvalds

┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Source                        ┃ Status    ┃ URL / Detail                    ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ GitHub                        │ FOUND     │ https://github.com/torvalds    │
│ Docker Hub                    │ FOUND     │ https://hub.docker.com/v2/...  │
│ ...                            │ ...       │ ...                             │
└────────────────────────────────┴───────────┴─────────────────────────────────┘
Summary: 9 found, 5 not found, 1 errors, 0 skipped (out of 15 sources)
confidence: 64.3% of resolved checks came back positive
```

## Why

Most OSINT username/email checkers are either a single-source lookup or a
40-minute manual crawl across breach checkers, avatar services, and platform
profile pages. `osint-tool` does the fan-out concurrently, dedupes, and gives
you one table (or JSON blob) — built to be scripted, piped, and extended.

## Install

```bash
pip install osint-tool          # once published to PyPI
# or, from source:
git clone https://github.com/YOUR_USERNAME/osint-tool
cd osint-tool
pip install -e .
```

Requires Python 3.9+.

## Usage

```bash
# Check a username across ~20 platforms, no API keys needed
osint-tool username torvalds

# Check an email: Gravatar, MX records, disposable-domain check, EmailRep,
# plus (if configured) Hunter.io and HaveIBeenPwned. Also fans the
# email's local-part out as a candidate username by default.
osint-tool email jdoe@example.com

# Auto-detect whether the query is an email or a username
osint-tool auto jdoe@example.com

# Machine-readable output for scripting / piping into jq
osint-tool username torvalds --json | jq '.findings[] | select(.status=="found")'
```

Every command supports `--json` and `--concurrency N`.

## Sources

**Username** (no API key, 15 platforms, each verified against both a known
real account and a random unregistered string): GitHub, GitLab, Bitbucket,
Docker Hub, Trello, Hacker News, Dev.to, Keybase, Behance, Dribbble,
Lichess, Chess.com, Mastodon, HackerOne, WordPress.com, Steam.

A handful of platforms that looked promising didn't make the cut on
verification: PyPI and Kaggle now serve an identical JS-shell/CAPTCHA page
regardless of whether the user exists, and Reddit, Medium, Codepen,
Letterboxd, and SourceForge block plain HTTP requests outright. Sites that
need a real browser session to tell a profile from a generic app shell
(Twitter/X, Instagram, TikTok, Spotify, ...) are left out for the same
reason — see [CONTRIBUTING.md](CONTRIBUTING.md) if you've found a reliable
no-browser signal for one of these.

**Email:**

| Source | API key required? |
|---|---|
| Gravatar | No |
| MX record lookup | No |
| Disposable-domain check (bundled list) | No |
| [EmailRep.io](https://emailrep.io/) | No (unauthenticated, low rate limit) — set `EMAILREP_API_KEY` for a higher one |
| [Hunter.io](https://hunter.io/) email verifier | Yes — free tier, 25/month |
| [HaveIBeenPwned](https://haveibeenpwned.com/API/Key) breach check | Yes — paid key |

Copy `.env.example` to `.env` and fill in whichever keys you have. Every
key-gated source degrades to a clean `skipped` result (not an error) when
its key is missing, so the tool is fully usable with zero configuration.

## How correlation works

Results are deduped by `(source, url)` so a source checked both directly and
as a derived candidate (e.g. an email's local-part run through the username
fan-out) isn't double-counted. The summary reports:

- counts by status (found / not found / error / skipped)
- a **confidence score**: the percentage of *resolved* checks (found +
  not found, excluding errors/skips) that came back positive
- notes calling out which sources hit and why anything was skipped or errored

## Extending it

Adding a source is meant to be a small, self-contained change:

- **Username site**: add one entry to `osint_tool/sources/username/sites.py`.
- **Email source**: add a module to `osint_tool/sources/email/` following the
  existing `make_task(...)` pattern and register it in `osint_tool/registry.py`.

See [CONTRIBUTING.md](CONTRIBUTING.md) for the full guide.

## Development

```bash
pip install -e ".[dev]"
pytest
ruff check .
```

## Legal / ethical use

This tool only queries public, free-tier APIs and public profile pages —
the same information a browser would show you. Use it for your own OSINT
research, security assessments you're authorized to run, or investigating
your own digital footprint. Respect the terms of service of each platform
and applicable law in your jurisdiction; don't use this to harass, stalk, or
deanonymize people without a lawful basis.

## License

MIT — see [LICENSE](LICENSE).
