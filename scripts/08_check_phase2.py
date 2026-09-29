"""
Step 08: verify the BigQuery results independently and write a summary.

Inputs:  Phase 1 CSVs (data/processed, data/logs)
         BigQuery result exports (data/processed/bq/*.csv)
         Live BigQuery row counts for the loaded tables
Output:  data/logs/phase2_summary.md (also printed)

Checks
1. Every loaded BigQuery table has the same row count as its local CSV.
2. Every week in pageviews_weekly has 7 days.
3. The missing-week statuses (weeks before a pair's first recorded view,
   and partial weeks) and the weekly and pooled Spearman values are
   recomputed in pandas straight from the Phase 1 CSVs, with no SQL
   involved, and must match BigQuery (Spearman to within 1e-9).
4. One title's weekly pageviews equal the sum of its daily rows.
The script exits with an error if any check fails.
"""

from __future__ import annotations

import sys

import numpy as np
import pandas as pd
from google.cloud import bigquery

import config

BQ = config.BQ_EXPORT_DIR
LOADED = {
    "netflix_top10": config.NETFLIX_6MKTS_CSV, "titles": config.TITLES_CSV,
    "title_markets": config.TITLE_MARKETS_CSV, "title_article_map": config.TITLE_ARTICLE_MAP_CSV,
    "pageviews_daily": config.PAGEVIEWS_DAILY_CSV, "contested_pairs": config.CONTESTED_PAIRS_CSV,
    "dropped_pairs": config.DROPPED_PAIRS_CSV,
}


def pandas_ranked() -> pd.DataFrame:
    """Rebuild the 'all' variant of 03_ranked from the Phase 1 CSVs."""
    nf = pd.read_csv(config.NETFLIX_6MKTS_CSV)
    titles = pd.read_csv(config.TITLES_CSV)
    amap = pd.read_csv(config.TITLE_ARTICLE_MAP_CSV)
    pv = pd.read_csv(config.PAGEVIEWS_DAILY_CSV, parse_dates=["date"])

    tmw = (nf.merge(titles[["title_id", "show_title", "category"]], on=["show_title", "category"])
             .groupby(["title_id", "category", "country_iso2", "week"], as_index=False)["weekly_rank"].min()
             .rename(columns={"country_iso2": "market", "week": "week_end"}))
    tmw["week_end"] = pd.to_datetime(tmw["week_end"])
    # Sunday that ends each day's Monday-Sunday week.
    pv["week_end"] = pv["date"] + pd.to_timedelta(6 - pv["date"].dt.weekday, unit="D")
    weekly = pv.groupby(["title_id", "market", "week_end"], as_index=False)["views"].sum()

    df = tmw.merge(amap[["title_id", "market"]], on=["title_id", "market"]) \
            .merge(weekly, on=["title_id", "market", "week_end"])

    # Same missing-week rule as 04_title_week_status: keep a week only if
    # the pair's first recorded view is on or before the week's Monday.
    first_view = pv[pv["views"] > 0].groupby(["title_id", "market"])["date"].min().rename("first_view")
    df = df.merge(first_view.reset_index(), on=["title_id", "market"], how="left")
    week_start = df["week_end"] - pd.Timedelta(days=6)
    df["status"] = np.select(
        [df["first_view"].isna(), df["week_end"] < df["first_view"], week_start < df["first_view"]],
        ["no_views", "before_first_view", "partial_week"], default="kept")
    status_counts = df["status"].value_counts()
    df = df[df["status"] == "kept"].copy()

    g = df.groupby(["market", "week_end", "category"])
    df["n"] = g["title_id"].transform("size")
    df["nr"] = g["weekly_rank"].rank(method="average")
    df["pr"] = g["views"].rank(method="average", ascending=False)
    df["nr_norm"] = (df["nr"] - 1) / (df["n"] - 1)
    df["pr_norm"] = (df["pr"] - 1) / (df["n"] - 1)
    return df, status_counts


def main() -> None:
    checks: dict[str, bool] = {}
    client = bigquery.Client(project=config.BQ_PROJECT, location=config.BQ_LOCATION)

    # 1. Row counts, BigQuery vs local CSV.
    counts = []
    for table, csv in LOADED.items():
        bq_rows = client.get_table(f"{config.BQ_PROJECT}.{config.BQ_DATASET}.{table}").num_rows
        local = len(pd.read_csv(csv))
        counts.append((table, bq_rows, local))
    checks["Loaded tables match local CSV row counts"] = all(b == l for _, b, l in counts)
    result_counts = [(p.stem, len(pd.read_csv(p))) for p in sorted(BQ.glob("*.csv"))]

    # 2. Complete weeks.
    pw = pd.read_csv(BQ / "pageviews_weekly.csv")
    checks["Every pageview week has 7 days"] = bool((pw["days"] == 7).all())

    # 3. Independent recompute: missing-week statuses, then Spearman.
    local, local_status = pandas_ranked()
    tws = pd.read_csv(BQ / "title_week_status.csv")
    bq_status = tws["status"].value_counts()
    checks["Missing-week status counts match pandas"] = \
        bq_status.sort_index().equals(local_status.sort_index())
    wk_local = (local[local["n"] >= 4].groupby(["market", "category", "week_end"])
                .apply(lambda d: d["nr"].corr(d["pr"]), include_groups=False).rename("rho_pd").reset_index())
    wk_bq = pd.read_csv(BQ / "agreement_weekly.csv", parse_dates=["week_end"])
    wk_bq = wk_bq[(wk_bq["variant"] == "all") & wk_bq["meets_min_n"]]
    wk = wk_bq.merge(wk_local, on=["market", "category", "week_end"], how="outer")
    wk_diff = (wk["spearman_rho"] - wk["rho_pd"]).abs()
    checks["Weekly rho: same market-weeks in pandas and BigQuery"] = len(wk) == len(wk_bq) == len(wk_local)
    checks["Weekly rho matches pandas (max diff < 1e-9)"] = bool(
        ((wk_diff < 1e-9) | (wk["spearman_rho"].isna() & wk["rho_pd"].isna())).all())

    pl_local = (local[local["n"] >= 2].groupby(["market", "category"])
                .apply(lambda d: d["nr_norm"].corr(d["pr_norm"]), include_groups=False)
                .rename("rho_pd").reset_index())
    pooled = pd.read_csv(BQ / "agreement_pooled.csv")
    pl = pooled[pooled["variant"] == "all"].merge(pl_local, on=["market", "category"])
    checks["Pooled rho matches pandas (max diff < 1e-9)"] = bool(
        (len(pl) == 12) and ((pl["pooled_rho"] - pl["rho_pd"]).abs() < 1e-9).all())

    # 4. Weekly = sum of daily, for one title-market-week.
    daily = pd.read_csv(config.PAGEVIEWS_DAILY_CSV, parse_dates=["date"])
    sample = pw.sort_values(["title_id", "market", "week_end"]).iloc[len(pw) // 2]
    end = pd.Timestamp(sample["week_end"])
    manual = daily[(daily["title_id"] == sample["title_id"]) & (daily["market"] == sample["market"])
                   & (daily["date"] > end - pd.Timedelta(days=7)) & (daily["date"] <= end)]["views"].sum()
    checks[f"Weekly views = sum of daily ({sample['title_id']} {sample['market']} {sample['week_end']})"] = \
        int(manual) == int(sample["views"])

    # ---- Sample results for the summary ----------------------------------
    order = {m: i for i, m in enumerate(config.MARKETS)}
    headline = (pooled.sort_values(["variant", "category", "market"], key=lambda s: s.map(order) if s.name == "market" else s)
                [["variant", "market", "category", "pooled_rho", "n_title_weeks", "n_weeks", "n_titles",
                  "weeks_with_rho", "weekly_rho_q1", "weekly_rho_median", "weekly_rho_q3"]]
                .round(2))
    disc = pd.read_csv(BQ / "discrepancies.csv")
    disc_all = disc[disc["variant"] == "all"]
    disc_rate = (disc_all.groupby(["market", "category"])
                 .agg(evaluated=("is_discrepancy", "size"), flagged=("is_discrepancy", "sum"))
                 .assign(rate=lambda d: (d["flagged"] / d["evaluated"]).round(2))
                 .reindex(config.MARKETS, level=0))
    disc_examples = (disc_all[disc_all["is_discrepancy"]].sort_values("norm_gap", ascending=False)
                     [["market", "category", "week_end", "show_title", "n", "netflix_rank_in_set",
                       "pageview_rank_in_set", "views", "direction"]].head(8))
    status_table = (tws.groupby(["market", "status"]).size().unstack(fill_value=0)
                       .reindex(config.MARKETS))
    status_table.loc["total"] = status_table.sum()
    coverage = pd.read_csv(BQ / "coverage_by_market.csv")
    coverage["_m"] = coverage["market"].map(order)
    coverage = coverage.sort_values(["category", "_m"]).drop(columns="_m")

    timing = pd.read_csv(BQ / "timing.csv")
    usable = timing[~timing["left_censored"] & ~timing["no_views"]
                    & ~timing["peak_at_range_edge"] & ~timing["article_after_chart"]]
    timing_summary = (usable.groupby(["market", "category"])["days_peak_vs_chart"]
                      .agg(pairs="size", median="median", q1=lambda s: s.quantile(.25),
                           q3=lambda s: s.quantile(.75))
                      .reindex(config.MARKETS, level=0))
    timing_flags = pd.Series({
        "pairs": len(timing), "left_censored": int(timing["left_censored"].sum()),
        "peak_at_range_edge": int(timing["peak_at_range_edge"].sum()),
        "no_views": int(timing["no_views"].sum()),
        "article_after_chart": int(timing["article_after_chart"].sum()),
        "usable (none of the above)": len(usable)}).rename("count").to_frame()

    lines = ["# Phase 2 summary", "", "## Checks", ""]
    lines += [f"- [{'x' if v else ' '}] {k}" for k, v in checks.items()] + [""]
    lines += ["## Loaded tables (BigQuery vs local CSV)", "",
              pd.DataFrame(counts, columns=["table", "bigquery_rows", "local_rows"]).to_markdown(index=False), ""]
    lines += ["## Result tables", "",
              pd.DataFrame(result_counts, columns=["table", "rows"]).to_markdown(index=False), ""]
    lines += ["## Missing weeks (charting title-weeks with an article)", "",
              "Only `kept` weeks are ranked. `before_first_view`: week ends before the pair's first "
              "recorded pageview. `partial_week`: the first view falls inside the week.", "",
              status_table.to_markdown(), ""]
    lines += ["## Coverage: days from first chart week (Monday) to first pageview", "",
              "Quartiles exclude articles already read before the range began "
              "(covered_before_range).", "",
              coverage.to_markdown(index=False), ""]
    lines += ["## Sample: agreement per market-category (headline = pooled_rho)", "",
              "Weekly quartiles cover weeks with n >= 4 only.", "",
              headline.to_markdown(index=False), ""]
    lines += ["## Sample: discrepancy rate (variant all, n >= 4)", "", disc_rate.to_markdown(), ""]
    lines += ["## Sample: largest discrepancies", "", disc_examples.to_markdown(index=False), ""]
    lines += ["## Sample: timing (days from first chart week's Monday to pageview peak)", "",
              timing_flags.to_markdown(), "", timing_summary.round(1).to_markdown(), ""]
    config.PHASE2_SUMMARY_MD.write_text("\n".join(lines), encoding="utf-8")
    print("\n".join(lines))
    if not all(checks.values()):
        sys.exit("One or more Phase 2 checks failed.")


if __name__ == "__main__":
    main()
