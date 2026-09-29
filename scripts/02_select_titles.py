"""
Step 02: build the title universe.

Input:  data/processed/netflix_top10_6mkts.csv
Output: data/processed/titles.csv         one row per title
        data/processed/title_markets.csv  one row per title-market pair that charted

Rules
- A title is identified by (show_title, category). TV seasons roll up to the
  show, because Wikipedia has one article per show, not per season.
- Every title that appears in a market's Top 10 during the window is kept for
  that market. No title cap, no minimum number of markets.
- title_id values are assigned in a stable order (most markets first, then
  most market-weeks, then best rank, then title), so they don't shuffle
  between runs unless the data changes.
"""

from __future__ import annotations

import pandas as pd

import config


def main() -> None:
    df = pd.read_csv(config.NETFLIX_6MKTS_CSV, dtype={"season_title": str},
                     keep_default_na=False)

    # A TV show can chart with two seasons in the same market-week. Collapse
    # to one row per title-market-week, keeping the better (lower) rank.
    tmw = (df.groupby(["show_title", "category", "country_iso2", "week"], as_index=False)
             ["weekly_rank"].min())

    # ---- One row per title -------------------------------------------------
    titles = (tmw.groupby(["show_title", "category"])
                 .agg(n_markets=("country_iso2", "nunique"),
                      market_weeks=("week", "size"),
                      best_rank=("weekly_rank", "min"),
                      markets=("country_iso2", lambda s: ",".join(sorted(s.unique()))))
                 .reset_index()
                 .sort_values(["n_markets", "market_weeks", "best_rank", "show_title"],
                              ascending=[False, False, True, True])
                 .reset_index(drop=True))
    titles.insert(0, "title_id", [f"T{i + 1:03d}" for i in range(len(titles))])

    # ---- One row per title-market pair ------------------------------------
    pairs = (tmw.groupby(["show_title", "category", "country_iso2"])
                .agg(first_week=("week", "min"), last_week=("week", "max"),
                     weeks_charted=("week", "size"), best_rank=("weekly_rank", "min"))
                .reset_index()
                .rename(columns={"country_iso2": "market"}))
    pairs = titles[["title_id", "show_title", "category"]].merge(pairs, on=["show_title", "category"])
    pairs["lang"] = pairs["market"].map(config.MARKETS)

    titles.to_csv(config.TITLES_CSV, index=False)
    pairs.sort_values(["title_id", "market"]).to_csv(config.TITLE_MARKETS_CSV, index=False)

    print(f"{len(titles)} titles, {len(pairs)} title-market pairs")
    print(pairs.groupby(["market", "category"]).size().unstack().to_string())


if __name__ == "__main__":
    main()
