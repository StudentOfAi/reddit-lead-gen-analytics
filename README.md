# Reddit Lead Gen Analytics

[![CI](https://github.com/StudentOfAi/reddit-lead-gen-analytics/actions/workflows/ci.yml/badge.svg)](https://github.com/StudentOfAi/reddit-lead-gen-analytics/actions/workflows/ci.yml)

Automated Reddit scraping and pain-point analysis for market intelligence. Scrapes subreddit discussions, identifies repeated complaints, and ranks them by frequency and relevance.

## What It Does

1. **Scrape** — Pull discussion threads from target subreddits
2. **Analyze** — Identify recurring pain points (complaints, frustrations, unmet needs)
3. **Rank** — Score top 5 by frequency and relevance to target market
4. **Report** — Generate structured Markdown report

## Usage

```bash
pip install requests beautifulsoup4

python3 scrape_reddit.py --subreddit entrepreneurship --limit 500
python3 analyze_pain_points.py
```

## Outputs

- `data/raw/*.json` — Raw scraped discussions
- `data/top5_pain_points.json` — Ranked pain points
- `data/PAIN_POINTS_REPORT.md` — Human-readable report

## Tech Stack

- Python 3
- Reddit API / web scraping
- NLP-based pain point detection
- JSON/Markdown report generation

## Tests

```bash
pip install -r requirements-dev.txt
pytest
```

16 tests cover the analysis pipeline end to end — raw-file loading (including
corrupt files), pain-phrase matching, clustering and ranking, and the JSON +
Markdown report writers. No Reddit access required.
