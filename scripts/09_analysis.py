"""
Step 09 (Phase 3): analysis on the exported BigQuery results.

Inputs:  data/processed/bq/{ranked,agreement_pooled,agreement_weekly,
         discrepancies,timing,coverage_by_market}.csv
         data/processed/title_article_map.csv
Outputs: data/raw/wikidata_origin.json          country of origin per QID (cache)
         data/processed/analysis/*.csv           one table per analysis below
         data/logs/phase3_analysis.md            all tables, readable

Analyses
1. Agreement: pooled Spearman per market-category (the headline) with a
   bootstrap 95% confidence interval. Market-categories with fewer than
   LOW_CONFIDENCE_N title-weeks are marked low confidence.

   Bootstrap design: resample whole weeks, with replacement, within each
   market-category, then recompute the pooled correlation on the 0-1
   normalized within-week ranks. Weeks are resampled rather than single
   title-weeks because ranks inside one week depend on each other (if one
   title moves up, another moves down). 2,000 resamples, fixed seed,
   percentile interval. Resamples where one side has no variation are
   skipped and counted.

2. Discrepancies: rate and direction per market-category (n >= 4 weeks),
   recurring discrepant titles, and a domestic vs foreign comparison of the
   signed rank gap. A title is domestic in a market if Wikidata's country of
   origin (P495) includes that market's country.

3. Timing: days from the first chart week's Monday to the pageview peak,
   excluding censored pairs and pairs whose article appeared after the title
   charted.

4. Coverage: carried through from 10_coverage_by_market for the report.

Usage: python scripts/09_analysis.py [--refresh]
  --refresh  query Wikidata again for countries of origin
"""

from __future__ import annotations

import argparse
import json

import numpy as np
import pandas as pd

import config

BQ = config.BQ_EXPORT_DIR
OUT = config.PROCESSED / "analysis"
OUT.mkdir(exist_ok=True)
ORIGIN_CACHE = config.RAW / "wikidata_origin.json"
REPORT_MD = config.LOGS / "phase3_analysis.md"

N_BOOT = 2000
SEED = 20260928
LOW_CONFIDENCE_N = 30

# Wikidata QID of each market's country, for the domestic/foreign split.
MARKET_COUNTRY = {"DE": "Q183", "FR": "Q142", "JP": "Q17", "BR": "Q155", "IT": "Q38", "KR": "Q884"}
MARKET_ORDER = {m: i for i, m in enumerate(config.MARKETS)}


def sort_markets(df: pd.DataFrame) -> pd.DataFrame:
    """Order rows by category, then the market order in config."""
    return (df.assign(_m=df["market"].map(MARKET_ORDER))
              .sort_values([c for c in ("variant", "category") if c in df] + ["_m"])
              .drop(columns="_m"))


# ---------------------------------------------------------------------------
# 1. Agreement with bootstrap confidence intervals
# ---------------------------------------------------------------------------

def pooled_rho(x: np.ndarray, y: np.ndarray) -> float:
    if len(x) < 3 or x.std() == 0 or y.std() == 0:
        return np.nan
    return float(np.corrcoef(x, y)[0, 1])


def bootstrap_agreement(ranked: pd.DataFrame) -> pd.DataFrame:
    rng = np.random.default_rng(SEED)
    rows = []
    usable = ranked[ranked["n"] >= 2]  # same rows as 07_agreement_pooled
    for (variant, market, category), g in usable.groupby(["variant", "market", "category"]):
        # One (x, y) array pair per week, so a resample is a list of weeks.
        weeks = [(w["netflix_rank_norm"].to_numpy(), w["pageview_rank_norm"].to_numpy())
                 for _, w in g.groupby("week_end")]
        point = pooled_rho(g["netflix_rank_norm"].to_numpy(), g["pageview_rank_norm"].to_numpy())
        stats, skipped = [], 0
        for _ in range(N_BOOT):
            pick = rng.integers(0, len(weeks), len(weeks))
            x = np.concatenate([weeks[i][0] for i in pick])
            y = np.concatenate([weeks[i][1] for i in pick])
            r = pooled_rho(x, y)
            if np.isnan(r):
                skipped += 1
            else:
                stats.append(r)
        lo, hi = (np.percentile(stats, [2.5, 97.5]) if stats else (np.nan, np.nan))
        rows.append({"variant": variant, "market": market, "category": category,
                     "pooled_rho": point, "ci_low": lo, "ci_high": hi,
                     "n_title_weeks": len(g), "n_weeks": len(weeks),
                     "low_confidence": len(g) < LOW_CONFIDENCE_N,
                     "ci_excludes_zero": bool(lo > 0 or hi < 0),
                     "boot_skipped": skipped})
    return sort_markets(pd.DataFrame(rows))


# ---------------------------------------------------------------------------
# 2. Discrepancies and domestic vs foreign
# ---------------------------------------------------------------------------

def load_origins(qids: list[str], refresh: bool) -> dict[str, list[str]]:
    """Country of origin (P495) per QID, cached in data/raw."""
    cache = {} if refresh or not ORIGIN_CACHE.exists() else \
        json.loads(ORIGIN_CACHE.read_text(encoding="utf-8"))
    todo = [q for q in qids if q not in cache]
    for i in range(0, len(todo), 50):
        ents = config.http_get(config.WIKIDATA_API, params={
            "action": "wbgetentities", "ids": "|".join(todo[i:i + 50]),
            "props": "claims", "format": "json"}).json()["entities"]
        for q, e in ents.items():
            cache[q] = [c["mainsnak"]["datavalue"]["value"]["id"]
                        for c in e.get("claims", {}).get("P495", []) if "datavalue" in c["mainsnak"]]
    ORIGIN_CACHE.write_text(json.dumps(cache, indent=1, sort_keys=True), encoding="utf-8")
    return cache


def origin_label(qid: str, market: str, origins: dict[str, list[str]]) -> str:
    countries = origins.get(qid, [])
    if not countries:
        return "unknown"
    return "domestic" if MARKET_COUNTRY[market] in countries else "foreign"


def mean_ci_by_title(df: pd.DataFrame, col: str, rng) -> tuple[float, float, float]:
    """Mean of col with a 95% CI from resampling titles (a title's weeks move together)."""
    groups = [g[col].to_numpy() for _, g in df.groupby("title_id")]
    if len(groups) < 3:
        return float(df[col].mean()), np.nan, np.nan
    boots = []
    for _ in range(N_BOOT):
        pick = rng.integers(0, len(groups), len(groups))
        boots.append(np.concatenate([groups[i] for i in pick]).mean())
    lo, hi = np.percentile(boots, [2.5, 97.5])
    return float(df[col].mean()), float(lo), float(hi)


def discrepancy_tables(ranked, disc, origins):
    d = disc[disc["variant"] == "all"].copy()
    rate = (d.groupby(["market", "category"])
              .agg(evaluated=("is_discrepancy", "size"), flagged=("is_discrepancy", "sum"),
                   netflix_ahead=("direction", lambda s: int(((s == "netflix_ahead") & d.loc[s.index, "is_discrepancy"]).sum())),
                   attention_ahead=("direction", lambda s: int(((s == "attention_ahead") & d.loc[s.index, "is_discrepancy"]).sum())))
              .reset_index())
    rate["rate"] = rate["flagged"] / rate["evaluated"]
    rate = sort_markets(rate)

    recurring = (d[d["is_discrepancy"]]
                 .groupby(["market", "category", "title_id", "show_title", "direction"])
                 .size().rename("weeks_flagged").reset_index()
                 .query("weeks_flagged >= 2")
                 .sort_values("weeks_flagged", ascending=False))

    # Signed gap on all ranked rows (n >= 2): positive = pageviews rank the
    # title higher than Netflix does (attention ahead).
    r = ranked[(ranked["variant"] == "all") & (ranked["n"] >= 2)].copy()
    r["signed_gap"] = (r["netflix_rank_in_set"] - r["pageview_rank_in_set"]) / (r["n"] - 1)
    r["origin"] = [origin_label(q, m, origins) for q, m in zip(r["qid"], r["market"])]
    rng = np.random.default_rng(SEED)
    rows = []
    for (market, origin), g in r.groupby(["market", "origin"]):
        mean, lo, hi = mean_ci_by_title(g, "signed_gap", rng)
        rows.append({"market": market, "origin": origin, "title_weeks": len(g),
                     "titles": g["title_id"].nunique(), "mean_signed_gap": mean,
                     "ci_low": lo, "ci_high": hi})
    for origin, g in r.groupby("origin"):
        mean, lo, hi = mean_ci_by_title(g.assign(title_id=g["title_id"] + g["market"]), "signed_gap", rng)
        rows.append({"market": "ALL", "origin": origin, "title_weeks": len(g),
                     "titles": g["title_id"].nunique(), "mean_signed_gap": mean,
                     "ci_low": lo, "ci_high": hi})
    by_origin = pd.DataFrame(rows)
    by_origin["_m"] = by_origin["market"].map({**MARKET_ORDER, "ALL": 99})
    by_origin = by_origin.sort_values(["_m", "origin"]).drop(columns="_m")
    return rate, recurring, by_origin, r


# ---------------------------------------------------------------------------
# 3. Timing
# ---------------------------------------------------------------------------

def timing_table(timing: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    flags = ["left_censored", "no_views", "peak_at_range_edge", "article_after_chart"]
    usable = timing[~timing[flags].any(axis=1)].copy()
    excluded = pd.Series({f: int(timing[f].sum()) for f in flags})
    excluded["usable"] = len(usable)
    t = (usable.groupby(["market", "category"])["days_peak_vs_chart"]
           .agg(pairs="size", median="median",
                q1=lambda s: s.quantile(.25), q3=lambda s: s.quantile(.75),
                share_before_chart=lambda s: (s < 0).mean(),
                share_in_first_week=lambda s: s.between(0, 6).mean(),
                share_later=lambda s: (s > 6).mean())
           .reset_index())
    return sort_markets(t), excluded.rename("pairs").to_frame()


# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[1])
    parser.add_argument("--refresh", action="store_true")
    args = parser.parse_args()

    ranked = pd.read_csv(BQ / "ranked.csv")
    pooled_bq = pd.read_csv(BQ / "agreement_pooled.csv")
    disc = pd.read_csv(BQ / "discrepancies.csv")
    timing = pd.read_csv(BQ / "timing.csv")
    coverage = sort_markets(pd.read_csv(BQ / "coverage_by_market.csv"))

    # 1. Agreement
    agree = bootstrap_agreement(ranked)
    weekly = pooled_bq[["variant", "market", "category", "weeks_with_rho",
                        "weekly_rho_q1", "weekly_rho_median", "weekly_rho_q3"]]
    agree = agree.merge(weekly, on=["variant", "market", "category"], how="left")
    # The point estimate must equal BigQuery's pooled_rho.
    check = agree.merge(pooled_bq[["variant", "market", "category", "pooled_rho"]],
                        on=["variant", "market", "category"], suffixes=("", "_bq"))
    max_diff = (check["pooled_rho"] - check["pooled_rho_bq"]).abs().max()
    if not max_diff < 1e-9:
        raise SystemExit(f"Bootstrap point estimates differ from BigQuery (max diff {max_diff})")

    # 2. Discrepancies
    origins = load_origins(sorted(ranked["qid"].dropna().unique()), args.refresh)
    rate, recurring, by_origin, signed = discrepancy_tables(ranked, disc, origins)

    # 3. Timing
    tim, tim_excluded = timing_table(timing)

    tables = {"agreement_ci": agree, "discrepancy_rate": rate,
              "discrepancy_recurring": recurring, "gap_by_origin": by_origin,
              "timing_summary": tim, "coverage": coverage}
    for name, df in tables.items():
        df.to_csv(OUT / f"{name}.csv", index=False)
    signed.to_csv(OUT / "ranked_with_origin.csv", index=False)

    fmt = lambda df: df.round(2).to_markdown(index=False)
    lines = ["# Phase 3 analysis", "",
             f"Bootstrap: {N_BOOT} resamples of weeks, seed {SEED}. Point estimates match "
             f"BigQuery (max diff {max_diff:.1e}). Low confidence = fewer than "
             f"{LOW_CONFIDENCE_N} title-weeks.", "",
             "## 1. Agreement (pooled Spearman, 95% CI)", "", fmt(agree), "",
             "## 2a. Discrepancy rate (n >= 4 weeks)", "", fmt(rate), "",
             "## 2b. Titles flagged in 2+ weeks", "", fmt(recurring), "",
             "## 2c. Signed rank gap by origin (positive = pageviews rank the title higher "
             "than Netflix; CI resamples titles)", "", fmt(by_origin), "",
             "## 3. Timing: days from first chart Monday to pageview peak", "",
             fmt(tim_excluded.reset_index(names="flag")), "", fmt(tim), "",
             "## 4. Coverage: days from first chart Monday to first pageview", "", fmt(coverage), ""]
    REPORT_MD.write_text("\n".join(lines), encoding="utf-8")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
