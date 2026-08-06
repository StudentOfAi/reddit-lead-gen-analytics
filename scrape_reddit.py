#!/usr/bin/env python3
"""
Phase 1: Scrape Reddit subreddits via authenticated OAuth API.
Read-only. Compliant with Reddit Responsible Builder Policy.
Rate limit: 100 req/min with OAuth (vs ~10 unauthenticated).
"""

from __future__ import annotations

import json
import os
import time
import urllib.request
import urllib.error
import urllib.parse
import base64
from pathlib import Path

# Load .env
ENV_FILE = Path(__file__).parent / ".env"
if ENV_FILE.exists():
    for line in ENV_FILE.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip())

CLIENT_ID = os.environ.get("REDDIT_CLIENT_ID", "")
CLIENT_SECRET = os.environ.get("REDDIT_CLIENT_SECRET", "")
USER_AGENT = os.environ.get("REDDIT_USER_AGENT", "lead-magnet-research/1.0")

SUBREDDITS = [
    "SideProject",
    "Entrepreneur",
    "WorkOnline",
    "beermoney",
    "Automate",
    "ADHD_Programmers",
    "selfhosted",
    "NotionTemplates",
]
TOP_N_POSTS = 50
TOP_N_COMMENTS = 10
DATA_DIR = Path(__file__).parent / "data" / "raw"


def get_oauth_token() -> str:
    """Get OAuth2 bearer token using client credentials."""
    if not CLIENT_ID or not CLIENT_SECRET:
        raise SystemExit(
            "Missing REDDIT_CLIENT_ID or REDDIT_CLIENT_SECRET.\n"
            "Create .env file with your credentials from reddit.com/prefs/apps"
        )
    auth = base64.b64encode(f"{CLIENT_ID}:{CLIENT_SECRET}".encode()).decode()
    data = urllib.parse.urlencode({
        "grant_type": "client_credentials",
        "device_id": "DO_NOT_TRACK_THIS_DEVICE",
    }).encode()
    req = urllib.request.Request(
        "https://www.reddit.com/api/v1/access_token",
        data=data,
        headers={
            "Authorization": f"Basic {auth}",
            "User-Agent": USER_AGENT,
            "Content-Type": "application/x-www-form-urlencoded",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            result = json.loads(resp.read())
    except urllib.error.HTTPError as e:
        body = e.read().decode() if e.fp else ""
        raise SystemExit(
            f"OAuth failed ({e.code}): {body}\n"
            f"Check REDDIT_CLIENT_ID and REDDIT_CLIENT_SECRET in .env"
        )
    token = result.get("access_token")
    if not token:
        raise SystemExit(f"OAuth failed: {result}")
    print(f"Authenticated. Token type: {result.get('token_type')}")
    return token


def fetch_json(url: str, token: str, retries: int = 3) -> dict | list | None:
    """Fetch JSON from Reddit OAuth API with retry on 429."""
    for attempt in range(retries):
        req = urllib.request.Request(
            url,
            headers={
                "Authorization": f"Bearer {token}",
                "User-Agent": USER_AGENT,
            },
        )
        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                return json.loads(resp.read())
        except urllib.error.HTTPError as e:
            if e.code == 429:
                wait = 5 * (attempt + 1)
                print(f"  rate limited, waiting {wait}s...")
                time.sleep(wait)
                continue
            print(f"  HTTP {e.code}")
            return None
        except Exception as e:
            print(f"  error: {e}")
            return None
    return None


def get_top_posts(subreddit: str, token: str) -> list[dict]:
    """Fetch top posts (past month) via OAuth API."""
    posts = []
    after = None
    while len(posts) < TOP_N_POSTS:
        url = f"https://oauth.reddit.com/r/{subreddit}/top?t=month&limit=25"
        if after:
            url += f"&after={after}"
        data = fetch_json(url, token)
        if not data or "data" not in data:
            break
        children = data["data"].get("children", [])
        if not children:
            break
        for child in children:
            if len(posts) >= TOP_N_POSTS:
                break
            d = child.get("data", {})
            posts.append({
                "title": d.get("title", ""),
                "score": d.get("score", 0),
                "comment_count": d.get("num_comments", 0),
                "flair": d.get("link_flair_text") or "",
                "url": f"https://www.reddit.com{d.get('permalink', '')}",
                "selftext": (d.get("selftext") or "")[:1000],
                "permalink": d.get("permalink", ""),
            })
        after = data["data"].get("after")
        if not after:
            break
        time.sleep(0.6)
    return posts


def get_top_comments(permalink: str, token: str) -> list[str]:
    """Fetch top comments for a post via OAuth API."""
    if not permalink:
        return []
    url = f"https://oauth.reddit.com{permalink}.json?limit={TOP_N_COMMENTS}&sort=top"
    data = fetch_json(url, token)
    if not data or not isinstance(data, list) or len(data) < 2:
        return []
    comments = []
    children = data[1].get("data", {}).get("children", [])
    for child in children[:TOP_N_COMMENTS]:
        body = child.get("data", {}).get("body", "")
        if body and body != "[deleted]" and body != "[removed]":
            comments.append(body[:500])
    return comments


def scrape_subreddit(subreddit: str, token: str) -> list[dict]:
    print(f"  Fetching top posts...")
    posts = get_top_posts(subreddit, token)
    print(f"  Got {len(posts)} posts. Fetching comments...")
    for i, post in enumerate(posts):
        post["top_comments"] = get_top_comments(post.get("permalink", ""), token)
        if (i + 1) % 10 == 0:
            print(f"  Comments: {i+1}/{len(posts)}")
        time.sleep(0.6)
    return posts


def main() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    token = get_oauth_token()

    for sub in SUBREDDITS:
        out_file = DATA_DIR / f"{sub}.json"
        if out_file.exists():
            existing = json.loads(out_file.read_text())
            if isinstance(existing, list) and len(existing) > 0:
                print(f"Skip (exists, {len(existing)} posts): {sub}")
                continue
        print(f"Scraping r/{sub}...")
        try:
            data = scrape_subreddit(sub, token)
            out_file.write_text(json.dumps(data, indent=2))
            print(f"  -> {len(data)} posts saved to {out_file.name}")
        except Exception as e:
            print(f"  -> Error: {e}")
        time.sleep(2)

    print("\nDone. Run: python analyze_pain_points.py")


if __name__ == "__main__":
    main()
