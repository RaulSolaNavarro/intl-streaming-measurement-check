"""
Step 01: download Netflix's weekly Top 10 by country and cut it to scope.

Input:  NETFLIX_COUNTRIES_URL (the full global file, every country and week)
Output: data/raw/netflix_all_weeks_countries.tsv        (full file, gitignored)
        data/raw/netflix_all_weeks_countries_<date>.tsv (dated copy, gitignored)
        data/processed/netflix_top10_6mkts.csv          (six markets, last 12 weeks)

Netflix weeks run Monday to Sunday. The `week` column holds the Sunday that
ends the week. The file only contains published, complete weeks, so the 12
most recent distinct `week` values are the 12 most recent complete weeks.

Usage: python scripts/01_pull_netflix.py [--refresh]
  --refresh  download again even if today's copy is already on disk
"""

from __future__ import annotations

import argparse
import shutil
from datetime import date

import pandas as pd

import config


def download(refresh: bool) -> None:
    """Fetch the TSV unless today's dated copy already exists."""
    dated = config.RAW / f"netflix_all_weeks_countries_{date.today():%Y-%m-%d}.tsv"
    if dated.exists() and config.NETFLIX_RAW_TSV.exists() and not refresh:
        print(f"Using cached {dated.name}")
        return
    print(f"Downloading {config.NETFLIX_COUNTRIES_URL}")
    resp = config.http_get(config.NETFLIX_COUNTRIES_URL, timeout=180)
    config.NETFLIX_RAW_TSV.write_bytes(resp.content)
    # Keep a dated copy so a later run can tell which snapshot it used.
    shutil.copyfile(config.NETFLIX_RAW_TSV, dated)
    print(f"Saved {len(resp.content):,} bytes")


def filter_to_scope() -> pd.DataFrame:
    """Keep only the six markets and the most recent WINDOW_WEEKS weeks."""
    df = pd.read_csv(config.NETFLIX_RAW_TSV, sep="\t", dtype=str, keep_default_na=False)

    # Fail loudly if Netflix ever changes the layout.
    expected = {"country_name", "country_iso2", "week", "category", "weekly_rank",
                "show_title", "season_title", "cumulative_weeks_in_top_10"}
    missing = expected - set(df.columns)
    if missing:
        raise ValueError(f"Netflix file is missing columns: {sorted(missing)}")

    df["week"] = pd.to_datetime(df["week"]).dt.date
    df["weekly_rank"] = df["weekly_rank"].astype(int)
    df["cumulative_weeks_in_top_10"] = df["cumulative_weeks_in_top_10"].astype(int)

    df = df[df["country_iso2"].isin(config.MARKETS)]
    weeks = sorted(df["week"].unique())[-config.WINDOW_WEEKS:]
    df = df[df["week"].isin(weeks)].copy()

    # "N/A" is Netflix's placeholder for films; store it as empty.
    df["season_title"] = df["season_title"].replace("N/A", "")
    df = df.sort_values(["country_iso2", "week", "category", "weekly_rank"])
    return df


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[1])
    parser.add_argument("--refresh", action="store_true")
    args = parser.parse_args()

    download(args.refresh)
    df = filter_to_scope()
    df.to_csv(config.NETFLIX_6MKTS_CSV, index=False)

    print(f"Wrote {config.NETFLIX_6MKTS_CSV.name}: {len(df):,} rows, "
          f"{df['country_iso2'].nunique()} markets, {df['week'].nunique()} weeks "
          f"({df['week'].min()} to {df['week'].max()})")


if __name__ == "__main__":
    main()
