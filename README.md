# Reddit Lead Gen Analytics

[![CI](https://github.com/StudentOfAi/reddit-lead-gen-analytics/actions/workflows/ci.yml/badge.svg)](https://github.com/StudentOfAi/reddit-lead-gen-analytics/actions/workflows/ci.yml)

Demand-discovery tooling: scrape business subreddits, mine the discussions for
pain-point language, and rank what people complain about most — so a founder can
find customer pain programmatically instead of reading threads for hours.

No ML, no external packages. The pipeline is pure Python standard library:
keyword-pattern matching (a curated set of "pain phrase" regexes) plus
frequency-based clustering. Lightweight by design — it runs anywhere Python 3.10+
runs, and every step is inspectable.

## How It Works

1. **Scrape** (`scrape_reddit.py`) — pulls top posts of the past month plus top
   comments from each target subreddit via Reddit's OAuth API (read-only,
   rate-limit friendly). One JSON file per subreddit.
2. **Mine** (`analyze_pain_points.py`) — scans titles and comments against a set
   of pain-phrase patterns ("stuck", "don't know how", "where to start",
   "can't find", ...), extracts the surrounding snippet.
3. **Cluster & rank** — groups snippets by shared dominant keywords, ranks
   clusters by frequency, keeps the top 5 with deduplicated example quotes.
4. **Report** — writes a machine-readable JSON ranking and a human-readable
   Markdown report, each pain point framed as a candidate lead-magnet angle.

See [`examples/sample-report.md`](examples/sample-report.md) for real (trimmed)
output from a live run.

## Setup

Requires Python 3.10+ and Reddit API credentials (free script app from
[reddit.com/prefs/apps](https://www.reddit.com/prefs/apps)):

```bash
cat > .env <<'EOF'
REDDIT_CLIENT_ID=your_client_id
REDDIT_CLIENT_SECRET=your_client_secret
EOF
```

No `pip install` needed for runtime — the pipeline has zero third-party
dependencies (stdlib only).

## Usage

```bash
# Defaults: 8 business subreddits, 50 posts each, output to data/raw/
python3 scrape_reddit.py

# Pick subreddits (comma-separated and/or repeated), cap posts per subreddit
python3 scrape_reddit.py --subreddits startups,SaaS --limit 100
python3 scrape_reddit.py -s smallbusiness -s freelance -n 25

# Custom output directory
python3 scrape_reddit.py --output data/run-2026-08

# Then mine + rank
python3 analyze_pain_points.py
```

CLI options for `scrape_reddit.py`:

| Flag | Default | Meaning |
|------|---------|---------|
| `-s`, `--subreddits` | `Entrepreneur, smallbusiness, SaaS, freelance, marketing, startups, sidehustle, indiehackers` | Subreddit(s) to scrape; comma-separated and/or repeated |
| `-n`, `--limit` | `50` | Max posts per subreddit |
| `-o`, `--output` | `data/raw/` | Output directory for `<subreddit>.json` files |

Already-scraped subreddits (non-empty JSON in the output dir) are skipped, so
reruns are cheap and resumable.

## Outputs

- `data/raw/*.json` — raw scraped posts + top comments, one file per subreddit
- `data/top5_pain_points.json` — ranked pain-point clusters with example quotes
- `data/PAIN_POINTS_REPORT.md` — human-readable report

## Tests

```bash
pip install -r requirements-dev.txt
pytest
```

23 tests cover the analysis pipeline end to end — raw-file loading (including
corrupt files), pain-phrase matching, clustering and ranking, the JSON +
Markdown report writers — plus the scraper's CLI argument parsing. No Reddit
access required; CI runs the suite on Python 3.10–3.12.
