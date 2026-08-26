"""Site definitions for the username fan-out.

Each entry describes how to tell "exists" from "does not exist" for one
platform, without needing an API key. Every entry here has been manually
verified against both a known-real account and a random, almost-certainly-
unregistered string (see CONTRIBUTING.md for the bar new entries need to
clear) — sites that turned out to always return the same generic app shell
(PyPI, Kaggle) or to block automated requests outright regardless of the
query (Reddit, Medium, Codepen, Letterboxd, SourceForge) were left out
rather than shipped with a detection rule that lies.

Platforms that require login or heavy JS rendering to distinguish a real
profile from a generic app shell (Twitter/X, Instagram, Facebook, TikTok,
Spotify...) are deliberately left out for the same reason.

`method` is one of:
  - "status":    resp.status_code in not_found_codes -> not found, else found
  - "message":   look for a marker substring in the response body
  - "json_null": the response body is a JSON literal `null` (or empty) when
                 the identifier doesn't exist
"""

from __future__ import annotations

SITES: list[dict] = [
    {
        "name": "GitHub",
        "url": "https://github.com/{}",
        "method": "status",
        "not_found_codes": [404],
    },
    {
        "name": "GitLab",
        "url": "https://gitlab.com/{}",
        "method": "status",
        # Nonexistent users consistently come back as a Cloudflare 403
        # challenge page rather than a plain 404 — verified against several
        # random unregistered strings.
        "not_found_codes": [404, 403],
    },
    {
        "name": "Bitbucket",
        "url": "https://api.bitbucket.org/2.0/workspaces/{}",
        "method": "status",
        "not_found_codes": [404],
    },
    {
        "name": "Docker Hub",
        "url": "https://hub.docker.com/v2/users/{}/",
        "method": "status",
        "not_found_codes": [404],
    },
    {
        "name": "Trello",
        "url": "https://trello.com/1/Members/{}",
        "method": "status",
        "not_found_codes": [404],
    },
    {
        "name": "Hacker News",
        "url": "https://hacker-news.firebaseio.com/v0/user/{}.json",
        "method": "json_null",
    },
    {
        "name": "Dev.to",
        "url": "https://dev.to/{}",
        "method": "status",
        "not_found_codes": [404],
    },
    {
        "name": "Keybase",
        "url": "https://keybase.io/_/api/1.0/user/lookup.json?usernames={}",
        "method": "message",
        "not_found_marker": '"them":[null]',
        "found_marker": '"them":[{',
    },
    {
        "name": "Behance",
        "url": "https://www.behance.net/{}",
        "method": "status",
        "not_found_codes": [404],
    },
    {
        "name": "Dribbble",
        "url": "https://dribbble.com/{}",
        "method": "status",
        "not_found_codes": [404],
    },
    {
        "name": "Lichess",
        "url": "https://lichess.org/api/user/{}",
        "method": "status",
        "not_found_codes": [404],
    },
    {
        "name": "Chess.com",
        "url": "https://api.chess.com/pub/player/{}",
        "method": "status",
        "not_found_codes": [404],
    },
    {
        "name": "Mastodon (mastodon.social)",
        "url": "https://mastodon.social/@{}",
        "method": "status",
        "not_found_codes": [404],
    },
    {
        "name": "HackerOne",
        "url": "https://hackerone.com/{}",
        "method": "status",
        "not_found_codes": [404],
    },
    {
        "name": "WordPress.com",
        "url": "https://{}.wordpress.com",
        "method": "message",
        # Any unclaimed subdomain resolves (wildcard DNS) to the generic
        # wordpress.com homepage instead of a 404.
        "not_found_marker": "<title>WordPress.com</title>",
    },
    {
        "name": "Steam",
        "url": "https://steamcommunity.com/id/{}?xml=1",
        "method": "message",
        "not_found_marker": "The specified profile could not be found",
        "found_marker": "<steamID64>",
    },
]
