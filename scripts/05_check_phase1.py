"""
Step 05: sanity-check the Phase 1 outputs and write a readable summary.

Inputs:  every file written by steps 01 to 04
Output:  data/logs/phase1_summary.md, plus the same checks printed to the console

The script exits with an error if any hard check fails, so an automated run
stops before bad data reaches BigQuery.

The key table counts, for each market-week, how many selected titles charted
on Netflix, split by Films and TV. It shows two versions: all selected titles,
and only those with a usable Wikipedia article in that market. The second one
is what the agreement metric will actually see. Spearman correlation needs at
least 3 titles to mean anything, and small counts are a warning sign.
"""

from __future__ import annotations

import sys

import pandas as pd

import config


def market_week_table(df: pd.DataFrame) -> pd.DataFrame:
    """Rows: week. Columns: market x category. Values: titles charting."""
    t = (df.groupby(["week", "country_iso2", "category"])["show_title"].nunique()
           .unstack(["country_iso2", "category"], fill_value=0))
    cols = [(m, c) for m in config.MARKETS for c in ("Films", "TV")]
    t = t.reindex(columns=pd.MultiIndex.from_tuples(cols), fill_value=0)
    t.columns = [f"{m} {'F' if c == 'Films' else 'TV'}" for m, c in t.columns]
    return t


def main() -> None:
    netflix = pd.read_csv(config.NETFLIX_6MKTS_CSV)
    selected = pd.read_csv(config.SELECTED_TITLES_CSV)
    amap = pd.read_csv(config.TITLE_ARTICLE_MAP_CSV)
    dropped = pd.read_csv(config.DROPPED_PAIRS_CSV)
    mlog = pd.read_csv(config.MATCH_LOG_CSV, keep_default_na=False)
    pv = pd.read_csv(config.PAGEVIEWS_DAILY_CSV)

    # ---- Hard checks -----------------------------------------------------
    n_days = pv["date"].nunique()
    checks = {
        f"Netflix window has {config.WINDOW_WEEKS} weeks": netflix["week"].nunique() == config.WINDOW_WEEKS,
        "Netflix file covers all 6 markets": set(netflix["country_iso2"]) == set(config.MARKETS),
        f"At most {config.MAX_TITLES} titles selected": len(selected) <= config.MAX_TITLES,
        f"Every title charted in >= {config.MIN_MARKETS} markets": bool((selected["n_markets"] >= config.MIN_MARKETS).all()),
        "Kept + dropped pairs = titles x 6": len(amap) + len(dropped) == len(selected) * len(config.MARKETS),
        "Pageview rows = pairs x days": len(pv) == len(amap) * n_days,
        "No null pageviews": bool(pv["views"].notna().all()),
    }

    # ---- Market-week tables ----------------------------------------------
    sel_rows = netflix.merge(selected[["title_id", "show_title", "category"]],
                             on=["show_title", "category"])
    mapped_rows = sel_rows.merge(amap[["title_id", "market"]],
                                 left_on=["title_id", "country_iso2"],
                                 right_on=["title_id", "market"])
    tbl_all = market_week_table(sel_rows)
    tbl_mapped = market_week_table(mapped_rows)

    # ---- Title list --------------------------------------------------------
    titles = selected[["title_id", "show_title", "category", "n_markets", "markets"]].merge(
        mlog[["title_id", "qid", "result"]], on="title_id")
    kept = amap.groupby("title_id")["market"].apply(lambda s: ",".join(s)).rename("markets_with_article")
    titles = titles.merge(kept, on="title_id", how="left").fillna({"markets_with_article": ""})

    # ---- Write summary -----------------------------------------------------
    lines = ["# Phase 1 summary", ""]
    lines += [f"- Netflix window: {netflix['week'].min()} to {netflix['week'].max()} "
              f"({netflix['week'].nunique()} weeks)",
              f"- Pageview range: {pv['date'].min()} to {pv['date'].max()} ({n_days} days)",
              f"- Titles selected: {len(selected)}; matched on Wikidata: {(mlog['qid'] != '').sum()}",
              f"- Title-market pairs kept: {len(amap)}; dropped: {len(dropped)}", ""]
    lines += ["## Checks", ""] + [f"- [{'x' if ok else ' '}] {name}" for name, ok in checks.items()] + [""]
    lines += ["## Titles", "", titles.to_markdown(index=False), ""]
    # Collapse the detailed match reasons into two groups; the Titles table
    # above already gives the per-title detail for unmatched titles.
    reason_group = dropped["reason"].where(~dropped["reason"].str.startswith("title unmatched"),
                                           "title unmatched on Wikidata (all 6 markets)")
    lines += ["## Dropped pairs by reason", "",
              dropped.assign(reason=reason_group).groupby("reason").size()
                     .rename("pairs").to_frame().to_markdown(), ""]
    lines += ["## Selected titles charting per market-week (all selected titles)", "",
              "F = Films, TV = TV. Week = Sunday ending the Netflix week.", "",
              tbl_all.to_markdown(), ""]
    lines += ["## Same, restricted to pairs with a Wikipedia article in that market", "",
              tbl_mapped.to_markdown(), ""]
    config.PHASE1_SUMMARY_MD.write_text("\n".join(lines), encoding="utf-8")

    print("\n".join(lines))
    if not all(checks.values()):
        sys.exit("One or more Phase 1 checks failed.")


if __name__ == "__main__":
    main()
