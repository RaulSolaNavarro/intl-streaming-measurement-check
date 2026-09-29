"""
Step 05: sanity-check the Phase 1 outputs and write a readable summary.

Inputs:  every file written by steps 01 to 04
Output:  data/logs/phase1_summary.md, plus the same text printed to the console

The script exits with an error if any hard check fails, so an automated run
stops before bad data reaches BigQuery.

Main tables
- Mapping rate per market: titles that charted in the market vs titles with
  an article in that market's Wikipedia language edition.
- n per market-week, split by Films and TV: how many charting titles have an
  article. This is the sample the per-week Spearman correlation would use.
  Netflix publishes 10 Films and 10 TV ranks per week; TV can show fewer than
  10 distinct titles when two seasons of one show chart together.
  Cells below MIN_N_PER_WEEK will use the pooled within-market fallback.
"""

from __future__ import annotations

import sys

import pandas as pd

import config


def pct(a, b) -> str:
    return f"{100 * a / b:.0f}%" if b else "n/a"


def main() -> None:
    netflix = pd.read_csv(config.NETFLIX_6MKTS_CSV)
    titles = pd.read_csv(config.TITLES_CSV)
    pairs = pd.read_csv(config.TITLE_MARKETS_CSV)
    amap = pd.read_csv(config.TITLE_ARTICLE_MAP_CSV)
    dropped = pd.read_csv(config.DROPPED_PAIRS_CSV)
    mlog = pd.read_csv(config.MATCH_LOG_CSV, keep_default_na=False)
    pv = pd.read_csv(config.PAGEVIEWS_DAILY_CSV)
    markets = list(config.MARKETS)

    # ---- Hard checks -----------------------------------------------------
    n_days = pv["date"].nunique()
    key = ["title_id", "market"]
    checks = {
        f"Netflix window has {config.WINDOW_WEEKS} weeks": netflix["week"].nunique() == config.WINDOW_WEEKS,
        "Netflix file covers all 6 markets": set(netflix["country_iso2"]) == set(markets),
        "Every title in titles.csv charted somewhere": set(titles["title_id"]) == set(pairs["title_id"]),
        "Kept + dropped pairs = charted pairs": len(amap) + len(dropped) == len(pairs),
        "Every kept pair actually charted in that market":
            len(amap.merge(pairs[key], on=key)) == len(amap),
        "Pageview rows = kept pairs x days": len(pv) == len(amap) * n_days,
        "No null pageviews": bool(pv["views"].notna().all()),
    }

    # ---- Mapping rate per market -----------------------------------------
    charted = pairs.groupby(["market", "category"]).size().unstack(fill_value=0)
    mapped = amap.groupby(["market", "category"]).size().unstack(fill_value=0)
    mapped = mapped.reindex(index=charted.index, columns=charted.columns, fill_value=0)
    rate = pd.DataFrame({
        "Films charted": charted["Films"], "Films w/ article": mapped["Films"],
        "Films rate": [pct(a, b) for a, b in zip(mapped["Films"], charted["Films"])],
        "TV charted": charted["TV"], "TV w/ article": mapped["TV"],
        "TV rate": [pct(a, b) for a, b in zip(mapped["TV"], charted["TV"])],
        "All charted": charted.sum(axis=1), "All w/ article": mapped.sum(axis=1),
        "All rate": [pct(a, b) for a, b in zip(mapped.sum(axis=1), charted.sum(axis=1))],
    }).reindex(markets)

    # ---- Drop reasons per market -----------------------------------------
    reason = dropped["reason"].where(dropped["reason"].str.startswith("no "), "title unmatched on Wikidata")
    reason = reason.str.replace(r"no \w+wiki sitelink", "matched, no article in that language", regex=True)
    drops = (dropped.assign(reason=reason).groupby(["market", "reason"]).size()
                    .unstack(fill_value=0).reindex(markets, fill_value=0))

    # ---- n per market-week, split by category ------------------------------
    # One row per title-market-week (TV seasons collapsed to the show).
    tmw = (netflix.groupby(["show_title", "category", "country_iso2", "week"], as_index=False)
                  ["weekly_rank"].min()
                  .rename(columns={"country_iso2": "market"}))
    tmw = tmw.merge(amap[["show_title", "category", "market"]], on=["show_title", "category", "market"])
    n = tmw.groupby(["week", "market", "category"]).size()
    weeks = sorted(netflix["week"].unique())
    idx = pd.MultiIndex.from_product([weeks, markets, ["Films", "TV"]], names=["week", "market", "category"])
    n = n.reindex(idx, fill_value=0)
    n_table = n.unstack(["market", "category"])
    n_table.columns = [f"{m} {'F' if c == 'Films' else 'TV'}" for m, c in n_table.columns]

    # Cells that meet the per-week threshold, per market and category.
    ok = (n >= config.MIN_N_PER_WEEK).groupby(["market", "category"]).sum().unstack()
    ok = ok.reindex(markets).astype(int).astype(str) + f" / {len(weeks)}"
    nstats = n.groupby(["market", "category"]).agg(["min", "median", "max"]).unstack()
    nstats.columns = [f"{c} n {s}" for s, c in nstats.columns]
    nstats = nstats.reindex(markets)
    week_summary = pd.concat([ok.rename(columns={"Films": f"Films weeks n>={config.MIN_N_PER_WEEK}",
                                                  "TV": f"TV weeks n>={config.MIN_N_PER_WEEK}"}),
                              nstats[[c for c in nstats.columns if c.startswith("Films")]],
                              nstats[[c for c in nstats.columns if c.startswith("TV")]]], axis=1)

    # ---- Write summary -----------------------------------------------------
    method_counts = mlog["match_method"].value_counts().rename("titles").to_frame()
    lines = ["# Phase 1 summary", ""]
    lines += [f"- Netflix window: {netflix['week'].min()} to {netflix['week'].max()} ({len(weeks)} weeks)",
              f"- Pageview range: {pv['date'].min()} to {pv['date'].max()} ({n_days} days)",
              f"- Titles: {len(titles)}; matched on Wikidata: {(mlog['qid'] != '').sum()}",
              f"- Charted title-market pairs: {len(pairs)}; with an article: {len(amap)}; "
              f"dropped: {len(dropped)}", ""]
    lines += ["## Checks", ""] + [f"- [{'x' if v else ' '}] {k}" for k, v in checks.items()] + [""]
    lines += ["## Wikidata match method", "",
              "netflix_id: item has a Netflix ID (P1874). label_*: no Netflix ID, matched on "
              "exact English label plus type. none: dropped.", "",
              method_counts.to_markdown(), ""]
    contested = mlog[mlog["contested"].astype(str) == "True"]
    lines += [f"Contested Netflix-ID matches (a newer same-type namesake exists): {len(contested)} titles, "
              f"{int(amap['contested'].sum())} title-market pairs with an article.", "",
              contested[["title_id", "show_title", "category", "qid", "newer_rivals"]].to_markdown(index=False), ""]
    lines += ["## Mapping rate per market", "",
              "Titles that charted in the market vs titles with an article in that market's "
              "language edition.", "", rate.to_markdown(), ""]
    lines += ["## Dropped pairs per market", "", drops.to_markdown(), ""]
    lines += [f"## n per market-week: summary (threshold n >= {config.MIN_N_PER_WEEK})", "",
              week_summary.to_markdown(), ""]
    lines += ["## n per market-week, split by Films (F) and TV", "",
              "Charting titles with an article. Week = Sunday ending the Netflix week.", "",
              n_table.to_markdown(), ""]
    config.PHASE1_SUMMARY_MD.write_text("\n".join(lines), encoding="utf-8")

    print("\n".join(lines))
    if not all(checks.values()):
        sys.exit("One or more Phase 1 checks failed.")


if __name__ == "__main__":
    main()
