"""
Shared settings and helpers for every pipeline script.

Everything a reader might want to change (markets, window length, title cap,
file locations) lives here, so the numbered scripts never hardcode them.
"""

from __future__ import annotations

import time
from pathlib import Path

import requests
import truststore

# Verify HTTPS certificates against the operating system's trust store
# instead of the certifi bundle that ships with requests. On machines where
# security software re-signs TLS traffic, only the OS store knows the
# local root, and certifi-based verification fails. Verification stays on.
truststore.inject_into_ssl()

# ---------------------------------------------------------------------------
# Scope
# ---------------------------------------------------------------------------

# Netflix country code -> Wikipedia language edition used as the attention
# signal for that market. A language edition is not a country (pt covers
# Brazil and Portugal, de covers Germany, Austria, and Switzerland). The
# report documents this as a limitation.
MARKETS: dict[str, str] = {
    "DE": "de",  # Germany
    "FR": "fr",  # France
    "JP": "ja",  # Japan
    "BR": "pt",  # Brazil
    "IT": "it",  # Italy
    "KR": "ko",  # South Korea
}

# Number of most recent complete Netflix weeks to analyse.
WINDOW_WEEKS = 12

# Title universe: every title that appears in a market's Top 10 during the
# window is analysed for that market. There is no title cap and no minimum
# number of markets. A title-market pair exists only where the title charted.

# Market-weeks with fewer mapped titles than this are too small for a
# per-week Spearman correlation; Phase 3 falls back to pooled within-market
# agreement for them.
MIN_N_PER_WEEK = 4

# Days of pageviews to pull before the first Netflix week in the window.
# The timing metric needs this lead-in because attention can peak before
# a title first charts.
PAGEVIEW_LEAD_DAYS = 28

# ---------------------------------------------------------------------------
# Sources
# ---------------------------------------------------------------------------

# Netflix moved the Top 10 downloads from top10.netflix.com to Tudum.
# This URL answers GET but returns 403 to HEAD requests, so only GET is used.
NETFLIX_COUNTRIES_URL = "https://www.netflix.com/tudum/top10/data/all-weeks-countries.tsv"

WIKIDATA_API = "https://www.wikidata.org/w/api.php"
WIKIDATA_SPARQL = "https://query.wikidata.org/sparql"
PAGEVIEWS_API = "https://wikimedia.org/api/rest_v1/metrics/pageviews/per-article"

# Wikimedia asks every client to identify itself with a descriptive
# User-Agent that points to a way of reaching the operator.
USER_AGENT = (
    "intl-streaming-measurement-check/0.1 "
    "(https://github.com/RaulSolaNavarro/intl-streaming-measurement-check)"
)

# ---------------------------------------------------------------------------
# Paths (all relative to the repo root, so scripts run from anywhere)
# ---------------------------------------------------------------------------

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw"
PROCESSED = ROOT / "data" / "processed"
LOGS = ROOT / "data" / "logs"

NETFLIX_RAW_TSV = RAW / "netflix_all_weeks_countries.tsv"
NETFLIX_6MKTS_CSV = PROCESSED / "netflix_top10_6mkts.csv"
TITLES_CSV = PROCESSED / "titles.csv"                  # one row per title
TITLE_MARKETS_CSV = PROCESSED / "title_markets.csv"    # one row per title-market pair that charted
WIKIDATA_CACHE_JSON = RAW / "wikidata_candidates.json" # compact Wikidata answers, per title
TITLE_ARTICLE_MAP_CSV = PROCESSED / "title_article_map.csv"
PAGEVIEWS_RAW_DIR = RAW / "pageviews"
PAGEVIEWS_DAILY_CSV = PROCESSED / "pageviews_daily.csv"
MATCH_LOG_CSV = LOGS / "wikidata_match_log.csv"
DROPPED_PAIRS_CSV = LOGS / "dropped_pairs.csv"
PHASE1_SUMMARY_MD = LOGS / "phase1_summary.md"

for _d in (RAW, PROCESSED, LOGS, PAGEVIEWS_RAW_DIR):
    _d.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------------------
# HTTP helper
# ---------------------------------------------------------------------------

_session = requests.Session()
_session.headers.update({"User-Agent": USER_AGENT})


def http_get(url: str, params: dict | None = None, *, ok_statuses=(200,),
             retries: int = 6, timeout: int = 60) -> requests.Response:
    """
    GET a URL with the project User-Agent, retrying on network errors,
    rate limits (429) and server errors (5xx) with exponential backoff.

    Any status in ok_statuses is returned to the caller unchanged (for
    example, the pageview script passes 404 because "no data" is a valid
    answer there). Any other status raises after the retries run out.
    """
    delay = 2.0
    last_error: Exception | None = None
    for attempt in range(1, retries + 1):
        try:
            resp = _session.get(url, params=params, timeout=timeout)
            if resp.status_code in ok_statuses:
                return resp
            if resp.status_code == 429 or resp.status_code >= 500:
                # Respect Retry-After when the server sends one.
                wait = float(resp.headers.get("Retry-After", delay))
                last_error = RuntimeError(f"HTTP {resp.status_code} for {resp.url}")
                time.sleep(wait)
                delay *= 2
                continue
            resp.raise_for_status()
            raise RuntimeError(f"Unexpected HTTP {resp.status_code} for {resp.url}")
        except (requests.ConnectionError, requests.Timeout) as exc:
            # The local network drops connections now and then; back off and retry.
            last_error = exc
            time.sleep(delay)
            delay *= 2
    raise RuntimeError(f"GET failed after {retries} attempts: {url}") from last_error
