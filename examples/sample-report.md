# Sample Output

Real, trimmed output from a live run against the Reddit OAuth API on 2026-08-24:

```bash
python3 scrape_reddit.py --subreddits smallbusiness --limit 10
python3 analyze_pain_points.py
```

Only the first raw post and the top-ranked pain points are shown here (comments
and body text trimmed for brevity). Quotes are excerpts from public r/smallbusiness
posts and comments (top of the past month).

## 1. Raw scrape output — `data/raw/smallbusiness.json` (first record, trimmed)

```json
{
  "title": "Bought a 50 year old boomer business in June. Turned out even better than advertised. Anyone else?",
  "score": 2382,
  "comment_count": 366,
  "flair": "",
  "url": "https://www.reddit.com/r/smallbusiness/comments/1vngg41/bought_a_50_year_old_boomer_business_in_june/",
  "selftext": "Closed July 1st on a commercial refrigeration business that's been around 50 years. Old school owner/operator, handshake deals, handwritten shorthand invoices, hasn't done marketing since 1978. ...",
  "permalink": "/r/smallbusiness/comments/1vngg41/bought_a_50_year_old_boomer_business_in_june/",
  "top_comments": [
    "What's the arrangement for transferring ownership? Paid cash up front or business loan or some type of purchase over time? ...",
    "..."
  ]
}
```

## 2. Ranked pain points — `data/top5_pain_points.json` (first entry)

```json
{
  "rank": 1,
  "pain_point": "stuck",
  "example_quotes": [
    "en a pretty loyal client They stuck with your FIL+MIL when the market was fantastic and di",
    "pokes at a thing when they're stuck, so I'd test for that instead of for tool knowledge."
  ],
  "why_pdf_helps": "A 5-page PDF with one constraint and a clear walkthrough reduces overwhelm and gives a single next action.",
  "suggested_pdf_title": "One constraint that fixes stuck — mechanism-first guide"
}
```

## 3. Markdown report — `data/PAIN_POINTS_REPORT.md` (excerpt)

```markdown
# Top 5 Pain Points (Phase 1)

Ranked by frequency and relevance to solo operators wanting to earn online with AI.

## #1 — stuck

**Pain point:** stuck

**Example quotes:**
- en a pretty loyal client They stuck with your FIL+MIL when the market was fantastic and di
- pokes at a thing when they're stuck, so I'd test for that instead of for tool knowledge.

**Why a 5-page PDF solves it:** A 5-page PDF with one constraint and a clear
walkthrough reduces overwhelm and gives a single next action.

**Suggested PDF title:** One constraint that fixes stuck — mechanism-first guide
```

Notes:

- A 10-post sample is deliberately small; cluster labels get sharper with the
  default 50 posts per subreddit across several subreddits.
- The `why_pdf_helps` / `suggested_pdf_title` fields frame each pain point as a
  candidate lead-magnet angle — the "so what" for a founder doing demand discovery.
