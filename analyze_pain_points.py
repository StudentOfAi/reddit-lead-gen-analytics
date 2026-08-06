#!/usr/bin/env python3
"""
Phase 1 analysis: Read data/raw/*.json, identify pain points (repeated complaints/frustrations),
rank top 5 by frequency and relevance to JOE (earn online with AI, stuck, low complexity).
Output: data/top5_pain_points.json and data/PAIN_POINTS_REPORT.md
"""

from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path

DATA_DIR = Path(__file__).parent / "data"
RAW_DIR = DATA_DIR / "raw"
OUT_JSON = DATA_DIR / "top5_pain_points.json"
OUT_REPORT = DATA_DIR / "PAIN_POINTS_REPORT.md"

# Phrases that suggest pain (complaint / question / frustration)
PAIN_PATTERNS = [
    r"don't know how",
    r"can't (?:get|find|figure)",
    r"how do (?:i|you)",
    r"stuck",
    r"overwhelm",
    r"too many",
    r"no (?:idea|clue|time)",
    r"never (?:shipped|launched|finished)",
    r"research (?:mode|paralysis)",
    r"open (?:tabs|threads)",
    r"where to start",
    r"what (?:to build|to sell|tool)",
    r"make money",
    r"side (?:hustle|project|income)",
    r"automate",
    r"first (?:dollar|sale|project)",
    r"shipping",
    r"actually (?:earn|work)",
]
PAIN_RE = re.compile("|".join(f"({p})" for p in PAIN_PATTERNS), re.I)


def load_all_posts() -> list[dict]:
    posts = []
    if not RAW_DIR.exists():
        return posts
    for f in RAW_DIR.glob("*.json"):
        try:
            data = json.loads(f.read_text())
            if isinstance(data, list):
                posts.extend(data)
            else:
                posts.append(data)
        except Exception:
            continue
    return posts


def extract_pain_snippets(posts: list[dict]) -> list[tuple[str, str, str]]:
    """Return (snippet, subreddit, source) for text that matches pain patterns."""
    out = []
    for p in posts:
        title = (p.get("title") or "").strip()
        for m in PAIN_RE.finditer(title):
            out.append((title[:200], p.get("url", ""), "title"))
        for c in p.get("top_comments") or []:
            for m in PAIN_RE.finditer(c):
                start = max(0, m.start() - 30)
                end = min(len(c), m.end() + 120)
                out.append((c[start:end].strip(), p.get("url", ""), "comment"))
    return out


def cluster_and_rank(snippets: list[tuple[str, str, str]]) -> list[dict]:
    """Simple frequency + keyword clustering; return top 5 pain point entries."""
    if not snippets:
        return []

    # Count phrase-like tokens (lowercase words 4+ chars)
    all_text = " ".join(s[0] for s in snippets).lower()
    words = re.findall(r"[a-z]{4,}", all_text)
    stop = {"that", "this", "with", "from", "have", "what", "when", "which", "your", "they", "would", "could", "should", "about", "there", "their"}
    words = [w for w in words if w not in stop]
    freq = Counter(words)

    # Build pain-point buckets by dominant keywords
    buckets: dict[str, list[tuple[str, str, str]]] = {}
    for snip, url, src in snippets:
        key_words = [w for w in re.findall(r"[a-z]{4,}", snip.lower()) if w in freq and freq[w] >= 2]
        key = " ".join(sorted(set(key_words))[:4]) if key_words else "other"
        if key not in buckets:
            buckets[key] = []
        buckets[key].append((snip, url, src))

    # Sort by size, take top 5
    ordered = sorted(buckets.items(), key=lambda x: -len(x[1]))[:5]
    result = []
    for i, (label, items) in enumerate(ordered, 1):
        quotes = list(dict.fromkeys([s[0][:200] for s in items[:5]]))  # dedupe
        result.append({
            "rank": i,
            "pain_point": label.replace(" ", " / "),
            "example_quotes": quotes,
            "why_pdf_helps": "A 5-page PDF with one constraint and a clear walkthrough reduces overwhelm and gives a single next action.",
            "suggested_pdf_title": f"One constraint that fixes {label.split()[0] if label != 'other' else 'it'} — mechanism-first guide",
        })
    return result


def main() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    posts = load_all_posts()
    if not posts:
        print("No data in data/raw/. Run scrape_reddit.py first.")
        return

    snippets = extract_pain_snippets(posts)
    top5 = cluster_and_rank(snippets)
    OUT_JSON.write_text(json.dumps(top5, indent=2))
    print(f"Wrote {OUT_JSON}")

    # Report (JOE voice)
    lines = [
        "# Top 5 Pain Points (Phase 1)",
        "",
        "Ranked by frequency and relevance to solo operators wanting to earn online with AI.",
        "",
    ]
    for entry in top5:
        lines.append(f"## #{entry['rank']} — {entry['pain_point']}")
        lines.append("")
        lines.append("**Pain point:** " + entry["pain_point"])
        lines.append("")
        lines.append("**Example quotes:**")
        for q in entry["example_quotes"]:
            lines.append(f"- {q}")
        lines.append("")
        lines.append("**Why a 5-page PDF solves it:** " + entry["why_pdf_helps"])
        lines.append("")
        lines.append("**Suggested PDF title:** " + entry["suggested_pdf_title"])
        lines.append("")
    OUT_REPORT.write_text("\n".join(lines))
    print(f"Wrote {OUT_REPORT}")


if __name__ == "__main__":
    main()
