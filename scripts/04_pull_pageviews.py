"""
Step 04: pull daily Wikipedia pageviews for every mapped title-market pair.

Input:  data/processed/title_article_map.csv
        data/processed/netflix_top10_6mkts.csv (to find the date range)
Output: data/raw/pageviews/<lang>__<article>.json  (raw API responses, cached)
        data/processed/pageviews_daily.csv         (title_id, show_title, qid, market,
                                                     lang, article, date, views)

API: Wikimedia REST pageviews, per-article, agent type `user` (humans, not
bots or crawlers), access `all-access` (desktop plus mobile web plus app).

Date range: from PAGEVIEW_LEAD_DAYS before the Monday that starts the first
Netflix week, through the Sunday that ends the last Netflix week. The lead-in
lets the timing metric see attention peaks that come before a title charts.

The API omits days with zero views and answers 404 when an article has no
views at all in the range. Both cases are filled with 0 here, so every pair
has exactly one row per day.

Usage: python scripts/04_pull_pageviews.py [--refresh]
  --refresh  ignore cached JSON and call the API again
"""

from __future__ import annotations

import argparse
import json
import time
from datetime import timedelta
from urllib.parse import quote

import pandas as pd

import config


def date_range() -> tuple[pd.Timestamp, pd.Timestamp]:
    """First and last day of pageviews to request."""
    weeks = pd.to_datetime(pd.read_csv(config.NETFLIX_6MKTS_CSV)["week"])
    first_monday = weeks.min() - timedelta(days=6)  # `week` is the Sunday ending the week
    start = first_monday - timedelta(days=config.PAGEVIEW_LEAD_DAYS)
    return start, weeks.max()


def cache_path(lang: str, article: str):
    """
    Cache file name for one article. The title is percent-encoded so the
    name is plain ASCII: Japanese, Korean, and accented titles then behave
    the same in git and on every operating system.
    """
    safe = quote(article.replace(" ", "_"), safe="()_-,.'")
    return config.PAGEVIEWS_RAW_DIR / f"{lang}__{safe}.json"


def fetch(lang: str, article: str, start: pd.Timestamp, end: pd.Timestamp, refresh: bool) -> dict:
    """Return the API JSON for one article, from cache when possible."""
    path = cache_path(lang, article)
    if path.exists() and not refresh:
        cached = json.loads(path.read_text(encoding="utf-8"))
        # Reuse the cache only if it covers the same date range.
        if cached.get("_range") == [f"{start:%Y%m%d}", f"{end:%Y%m%d}"]:
            return cached

    # Article titles use underscores for spaces and must be fully
    # percent-encoded (including "/" which appears in some titles).
    encoded = quote(article.replace(" ", "_"), safe="")
    url = (f"{config.PAGEVIEWS_API}/{lang}.wikipedia/all-access/user/"
           f"{encoded}/daily/{start:%Y%m%d}00/{end:%Y%m%d}00")
    resp = config.http_get(url, ok_statuses=(200, 404))
    data = resp.json() if resp.status_code == 200 else {"items": []}
    data["_status"] = resp.status_code
    data["_range"] = [f"{start:%Y%m%d}", f"{end:%Y%m%d}"]
    path.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
    time.sleep(0.1)  # stay well under Wikimedia's rate limits
    return data


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[1])
    parser.add_argument("--refresh", action="store_true")
    args = parser.parse_args()

    start, end = date_range()
    all_days = pd.date_range(start, end, freq="D")
    pairs = pd.read_csv(config.TITLE_ARTICLE_MAP_CSV)
    print(f"Pulling {len(pairs)} title-market pairs, {start:%Y-%m-%d} to {end:%Y-%m-%d} "
          f"({len(all_days)} days)")

    frames = []
    for p in pairs.itertuples(index=False):
        data = fetch(p.lang, p.article, start, end, args.refresh)
        views = {pd.Timestamp(i["timestamp"][:8]): i["views"] for i in data.get("items", [])}
        # Reindex onto the full calendar so missing days become explicit zeros.
        s = pd.Series(views, dtype="int64").reindex(all_days, fill_value=0)
        frames.append(pd.DataFrame({
            "title_id": p.title_id, "show_title": p.show_title, "qid": p.qid,
            "market": p.market, "lang": p.lang, "article": p.article,
            "date": all_days.date, "views": s.values,
        }))
        status = "no data (404)" if data["_status"] == 404 else f"{int(s.sum()):,} views"
        print(f"  {p.title_id} {p.market} {p.lang}:{p.article}: {status}")

    out = pd.concat(frames, ignore_index=True)
    out.to_csv(config.PAGEVIEWS_DAILY_CSV, index=False)
    print(f"Wrote {config.PAGEVIEWS_DAILY_CSV.name}: {len(out):,} rows")


if __name__ == "__main__":
    main()
