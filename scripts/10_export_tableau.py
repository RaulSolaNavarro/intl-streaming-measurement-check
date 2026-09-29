"""
Step 10: export dashboard-ready CSVs for Tableau (or any BI tool).

Inputs:  data/processed/analysis/agreement_ci.csv       (Phase 3)
         data/processed/title_markets.csv, title_article_map.csv (Phase 1)
         data/processed/bq/discrepancies.csv            (Phase 2)
Output:  data/processed/tableau/agreement.csv
         data/processed/tableau/coverage.csv
         data/processed/tableau/discrepancies.csv

Conventions shared by all three files, so they join and filter cleanly:
- `market` is the full market name (Germany, France, Japan, Brazil, Italy,
  South Korea) and `category` is Films or TV.
- Rates and shares are decimals from 0 to 1, not percentages.
- Rows follow the report's order: category, then market (DE, FR, JP, BR,
  IT, KR), except discrepancies, which follow the report's ranking.

The rules match the report (report/charts.py), so the numbers agree:
- agreement: all-pairs variant only; confidence is "Low" below
  LOW_CONFIDENCE_N title-weeks, otherwise "OK".
- discrepancies: every pair evaluated (market-week with n >= 4) in at least
  DISC_MIN_WEEKS weeks, ranked by share of weeks flagged, then mean
  normalized gap, then title.
"""

from __future__ import annotations

import pandas as pd

import config

OUT = config.PROCESSED / "tableau"
OUT.mkdir(exist_ok=True)

MARKET_NAME = {"DE": "Germany", "FR": "France", "JP": "Japan", "BR": "Brazil",
               "IT": "Italy", "KR": "South Korea"}
MARKET_ORDER = {m: i for i, m in enumerate(config.MARKETS)}
LOW_CONFIDENCE_N = 30
DISC_MIN_WEEKS = 3


def in_report_order(df: pd.DataFrame) -> pd.DataFrame:
    """Sort by category, then the configured market order, then map codes to names."""
    df = (df.assign(_m=df["market"].map(MARKET_ORDER))
            .sort_values(["category", "_m"]).drop(columns="_m"))
    df["market"] = df["market"].map(MARKET_NAME)
    return df.reset_index(drop=True)


def agreement() -> pd.DataFrame:
    a = pd.read_csv(config.PROCESSED / "analysis" / "agreement_ci.csv")
    a = a[a["variant"] == "all"]
    out = pd.DataFrame({
        "market": a["market"], "category": a["category"],
        "pooled_rho": a["pooled_rho"].round(4),
        "ci_low": a["ci_low"].round(4), "ci_high": a["ci_high"].round(4),
        "title_weeks": a["n_title_weeks"].astype(int),
        "confidence": ["Low" if n < LOW_CONFIDENCE_N else "OK" for n in a["n_title_weeks"]],
    })
    return in_report_order(out)


def coverage() -> pd.DataFrame:
    charted = pd.read_csv(config.TITLE_MARKETS_CSV).groupby(["market", "category"]).size()
    mapped = pd.read_csv(config.TITLE_ARTICLE_MAP_CSV).groupby(["market", "category"]).size()
    t = (pd.concat([charted.rename("charted"), mapped.rename("with_article")], axis=1)
           .fillna(0).astype(int).reset_index())
    t["mapping_rate"] = (t["with_article"] / t["charted"]).round(4)
    return in_report_order(t)


def discrepancies() -> pd.DataFrame:
    d = pd.read_csv(config.BQ_EXPORT_DIR / "discrepancies.csv")
    d = d[d["variant"] == "all"]
    g = (d.groupby(["market", "category", "show_title"])
          .agg(weeks_evaluated=("norm_gap", "size"), weeks_flagged=("is_discrepancy", "sum"),
               mean_gap=("norm_gap", "mean"), signed=("rank_gap", "mean"))
          .reset_index())
    g = g[g["weeks_evaluated"] >= DISC_MIN_WEEKS].copy()
    g["share_flagged"] = g["weeks_flagged"] / g["weeks_evaluated"]
    g = g.sort_values(["share_flagged", "mean_gap", "show_title"], ascending=[False, False, True])
    return pd.DataFrame({
        "market": g["market"].map(MARKET_NAME), "category": g["category"],
        "title": g["show_title"],
        # Positive mean rank gap: pageviews rank the title higher than Netflix does.
        "direction": ["Attention ahead" if s > 0 else "Netflix ahead" for s in g["signed"]],
        "weeks_evaluated": g["weeks_evaluated"].astype(int),
        "weeks_flagged": g["weeks_flagged"].astype(int),
        "share_flagged": g["share_flagged"].round(4),
        "mean_gap": g["mean_gap"].round(4),
    }).reset_index(drop=True)


def main() -> None:
    for name, df in {"agreement": agreement(), "coverage": coverage(),
                     "discrepancies": discrepancies()}.items():
        path = OUT / f"{name}.csv"
        # UTF-8 with BOM so Excel and Tableau on Windows read accents correctly.
        df.to_csv(path, index=False, encoding="utf-8-sig")
        print(f"{path.relative_to(config.ROOT)}: {len(df)} rows, columns: {', '.join(df.columns)}")


if __name__ == "__main__":
    main()
