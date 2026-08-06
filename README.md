# Reddit Lead Gen Analytics

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
