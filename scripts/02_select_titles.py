"""
Step 02: choose the titles to analyse.

Input:  data/processed/netflix_top10_6mkts.csv
Output: data/processed/selected_titles.csv

Rules
- A title is identified by (show_title, category). TV seasons roll up to the
  show, because Wikipedia has one article per show, not per season.
- Eligible titles charted in at least MIN_MARKETS of the six markets during
  the window.
- Eligible titles are ordered by: number of markets charted (more first),
  then total market-weeks on the chart (more first), then best rank reached
  (lower first), then title (for a stable order). The first MAX_TITLES are kept.
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

    per_title = (tmw.groupby(["show_title", "category"])
                    .agg(n_markets=("country_iso2", "nunique"),
                         market_weeks=("week", "size"),
                         best_rank=("weekly_rank", "min"),
                         markets=("country_iso2", lambda s: ",".join(sorted(s.unique()))))
                    .reset_index())

    eligible = per_title[per_title["n_markets"] >= config.MIN_MARKETS]
    selected = (eligible.sort_values(["n_markets", "market_weeks", "best_rank", "show_title"],
                                     ascending=[False, False, True, True])
                        .head(config.MAX_TITLES)
                        .reset_index(drop=True))

    # First chart week in each market (used later by the timing metric and
    # handy for eyeballing the list now).
    first_week = (tmw.groupby(["show_title", "category", "country_iso2"])["week"].min()
                     .unstack("country_iso2")
                     .add_prefix("first_week_")
                     .reset_index())
    selected = selected.merge(first_week, on=["show_title", "category"], how="left")
    selected.insert(0, "title_id", [f"T{i + 1:02d}" for i in range(len(selected))])

    selected.to_csv(config.SELECTED_TITLES_CSV, index=False)
    print(f"{len(eligible)} titles charted in >= {config.MIN_MARKETS} markets; "
          f"kept {len(selected)}")
    print(selected[["title_id", "show_title", "category", "n_markets",
                    "market_weeks", "best_rank"]].to_string(index=False))


if __name__ == "__main__":
    main()
