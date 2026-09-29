"""
Data loading and chart builders for the Quarto report (report/index.qmd).

Everything here reads the committed CSVs in data/, never BigQuery, so the
report renders the same way after the BigQuery tables are gone.

Charts are Plotly figures shown with staticPlot=True: no hover, zoom, or
toolbar, matching the project rule that report charts are static. Each chart
in the report is paired with a table view of the same numbers.

Colors: Films = categorical slot 1 (blue), TV = slot 2 (orange), from the
reference data-viz palette, in every chart. Ink, grid, and surface colors
come from the same palette.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from IPython.display import HTML, display
from plotly.offline import get_plotlyjs
from plotly.subplots import make_subplots

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
PROCESSED = DATA / "processed"
BQ = PROCESSED / "bq"
ANALYSIS = PROCESSED / "analysis"
LOGS = DATA / "logs"

MARKETS = ["DE", "FR", "JP", "BR", "IT", "KR"]
MARKET_NAME = {"DE": "Germany", "FR": "France", "JP": "Japan", "BR": "Brazil",
               "IT": "Italy", "KR": "South Korea"}
LANG_NAME = {"DE": "German", "FR": "French", "JP": "Japanese", "BR": "Portuguese",
             "IT": "Italian", "KR": "Korean"}

# Palette (light mode).
COLOR = {"Films": "#2a78d6", "TV": "#eb6834"}
SURFACE = "#ffffff"  # matches the page background
INK = "#0b0b0b"
INK_2 = "#52514e"
MUTED = "#898781"
GRID = "#e1e0d9"
AXIS = "#c3c2b7"
FONT = 'system-ui, -apple-system, "Segoe UI", sans-serif'

STATIC = {"staticPlot": True, "responsive": True, "displayModeBar": False}

# Forest plot: value labels closer than this to 0 are shifted sideways.
ZERO_LABEL_GAP = 0.12
# Weekly-rho median is shown only when at least this many weeks qualify (n >= 4).
MIN_WEEKS_FOR_MEDIAN = 3


def fmt2(x) -> str:
    """Two decimals, or n/a for a missing value."""
    return "n/a" if pd.isna(x) else f"{x:.2f}"


def plotly_library() -> None:
    """
    Emit the plotly.js library inline, once, from the report's setup cell.

    Keeping the library in the page means the report needs no CDN, so it
    renders the same offline and on GitHub Pages. It is emitted on its own,
    not with the first chart, because Quarto relocates the output that
    carries this large script, and a chart attached to it would move too.

    Quarto also adds require.js to Jupyter-rendered pages. With it present,
    plotly.js registers as an AMD module instead of setting window.Plotly,
    and the charts never draw, so `define` is hidden while the library loads
    and restored afterwards.
    """
    display(HTML("<script>window.__define = window.define; window.define = undefined;</script>"
                 f"<script>{get_plotlyjs()}</script>"
                 "<script>window.define = window.__define;</script>"))


def show(fig: go.Figure) -> None:
    """Emit a figure as plain HTML (the library comes from plotly_library())."""
    display(HTML(fig.to_html(full_html=False, include_plotlyjs=False, config=STATIC)))


def _base_layout(fig: go.Figure, height: int, **kw) -> go.Figure:
    """Shared surface, ink, and axis styling. Keyword arguments override the defaults."""
    layout = dict(height=height, paper_bgcolor=SURFACE, plot_bgcolor=SURFACE,
                  font=dict(family=FONT, size=13, color=INK_2),
                  margin=dict(l=10, r=10, t=40, b=40), showlegend=False)
    layout.update(kw)
    fig.update_layout(**layout)
    fig.update_xaxes(gridcolor=GRID, zeroline=False, linecolor=AXIS, tickfont=dict(color=MUTED))
    fig.update_yaxes(gridcolor=GRID, zeroline=False, linecolor=AXIS, tickfont=dict(color=INK_2))
    return fig


def _legend_note(fig: go.Figure, y: float = 1.12) -> None:
    """A two-entry legend drawn as text swatches, top left."""
    fig.add_annotation(
        xref="paper", yref="paper", x=0, y=y, xanchor="left", showarrow=False,
        text=(f"<span style='color:{COLOR['Films']}'>●</span> Films &nbsp;&nbsp; "
              f"<span style='color:{COLOR['TV']}'>●</span> TV"),
        font=dict(size=13, color=INK_2))


# ---------------------------------------------------------------------------
# Data
# ---------------------------------------------------------------------------

def load() -> dict:
    """Every table the report needs, plus a few headline numbers."""
    d = {
        "agree": pd.read_csv(ANALYSIS / "agreement_ci.csv"),
        "disc": pd.read_csv(BQ / "discrepancies.csv"),
        "origin": pd.read_csv(ANALYSIS / "gap_by_origin.csv"),
        "timing": pd.read_csv(BQ / "timing.csv"),
        "coverage_pairs": pd.read_csv(BQ / "article_coverage.csv"),
        "status": pd.read_csv(BQ / "title_week_status.csv"),
        "pairs": pd.read_csv(PROCESSED / "title_markets.csv"),
        "amap": pd.read_csv(PROCESSED / "title_article_map.csv"),
        "titles": pd.read_csv(PROCESSED / "titles.csv"),
        "matchlog": pd.read_csv(LOGS / "wikidata_match_log.csv", keep_default_na=False),
        "contested": pd.read_csv(LOGS / "contested_pairs.csv", keep_default_na=False),
        "netflix": pd.read_csv(PROCESSED / "netflix_top10_6mkts.csv"),
        "pageviews_range": pd.read_csv(PROCESSED / "pageviews_daily.csv", usecols=["date"])["date"],
    }
    flags = ["left_censored", "no_views", "peak_at_range_edge", "article_after_chart"]
    d["timing_usable"] = d["timing"][~d["timing"][flags].any(axis=1)].copy()
    return d


def agreement_all(d: dict) -> pd.DataFrame:
    a = d["agree"][d["agree"]["variant"] == "all"].copy()
    a["market_name"] = a["market"].map(MARKET_NAME)
    return a


def mapping_rates(d: dict) -> pd.DataFrame:
    charted = d["pairs"].groupby(["market", "category"]).size().rename("charted")
    mapped = d["amap"].groupby(["market", "category"]).size().rename("with_article")
    t = pd.concat([charted, mapped], axis=1).fillna(0).astype(int).reset_index()
    t["rate"] = t["with_article"] / t["charted"]
    return t


def article_lag(d: dict) -> pd.DataFrame:
    """Per market-category: share of pairs whose article first got views after the title charted."""
    c = d["coverage_pairs"]
    g = c.groupby(["market", "category"])
    t = pd.DataFrame({
        "pairs": g.size(),
        "appeared_after_chart": g["days_chart_to_first_view"].apply(lambda s: int((s > 0).sum())),
        "median_lag_days_when_late": g["days_chart_to_first_view"].apply(
            lambda s: float(s[s > 0].median()) if (s > 0).any() else np.nan),
    }).reset_index()
    t["share_late"] = t["appeared_after_chart"] / t["pairs"]
    return t


# ---------------------------------------------------------------------------
# Charts
# ---------------------------------------------------------------------------

def forest_plot(d: dict) -> go.Figure:
    a = agreement_all(d)
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.08,
                        subplot_titles=("Films", "TV"))
    for row, cat in enumerate(["Films", "TV"], start=1):
        s = a[a["category"] == cat].set_index("market").loc[MARKETS[::-1]].reset_index()
        # Low-confidence rows say so in the axis label, so it isn't carried
        # by the hollow marker alone.
        s["label"] = [f"{MARKET_NAME[m]} (low confidence, n={n})" if low else MARKET_NAME[m]
                      for m, low, n in zip(s["market"], s["low_confidence"], s["n_title_weeks"])]
        for low in (False, True):
            part = s[s["low_confidence"] == low]
            fig.add_trace(go.Scatter(
                x=part["pooled_rho"], y=part["label"],
                mode="markers+text", text=[f"{v:.2f}" for v in part["pooled_rho"]],
                # A centered label near 0 sits on the zero line; push it to the side.
                textposition=[("top right" if v >= 0 else "top left") if abs(v) < ZERO_LABEL_GAP
                              else "top center" for v in part["pooled_rho"]],
                textfont=dict(size=11, color=INK_2),
                error_x=dict(type="data", symmetric=False,
                             array=part["ci_high"] - part["pooled_rho"],
                             arrayminus=part["pooled_rho"] - part["ci_low"],
                             color=COLOR[cat], thickness=2, width=0),
                marker=dict(size=11, color=SURFACE if low else COLOR[cat],
                            symbol="circle", line=dict(color=COLOR[cat], width=2))),
                row=row, col=1)
        fig.update_yaxes(categoryorder="array", categoryarray=list(s["label"]),
                         row=row, col=1, showgrid=False)
        fig.add_vline(x=0, line=dict(color=AXIS, width=1), row=row, col=1)
    fig.update_xaxes(range=[-1.05, 1.05], tickvals=[-1, -0.5, 0, 0.5, 1], tickangle=0)
    fig.update_xaxes(title_text="Pooled Spearman ρ (bars: 95% CI)", row=2, col=1)
    fig.update_annotations(selector=dict(text="Films"), font=dict(color=COLOR["Films"], size=14), x=0, xanchor="left")
    fig.update_annotations(selector=dict(text="TV"), font=dict(color=COLOR["TV"], size=14), x=0, xanchor="left")
    # Extra top margin keeps the first row's value label clear of the edge.
    _base_layout(fig, height=620, margin=dict(l=10, r=20, t=70, b=60))
    return fig


def forest_table(d: dict) -> pd.DataFrame:
    a = agreement_all(d)
    a["_m"] = a["market"].map({m: i for i, m in enumerate(MARKETS)})
    a = a.sort_values(["category", "_m"])
    enough = a["weeks_with_rho"] >= MIN_WEEKS_FOR_MEDIAN
    return pd.DataFrame({
        "Market": a["market_name"], "Category": a["category"],
        "Pooled ρ": [fmt2(v) for v in a["pooled_rho"]],
        "95% CI": [f"{fmt2(l)} to {fmt2(h)}" for l, h in zip(a["ci_low"], a["ci_high"])],
        "Title-weeks": a["n_title_weeks"], "Weeks": a["n_weeks"],
        "Weeks in weekly median": a["weeks_with_rho"].astype(int),
        "Weekly ρ median": [fmt2(v) if ok else "n/a" for v, ok in zip(a["weekly_rho_median"], enough)],
        "Low confidence": np.where(a["low_confidence"], "yes", ""),
    })


def top_discrepancies(d: dict, k: int = 10) -> pd.DataFrame:
    """
    Title-market pairs with the largest mean normalized rank gap, over the
    market-weeks where the pair was evaluated (n >= 4 titles). Ties are
    broken by weeks flagged, then weeks evaluated, then title.
    Direction follows the sign of the mean rank gap.
    """
    x = d["disc"][d["disc"]["variant"] == "all"]
    g = (x.groupby(["market", "category", "title_id", "show_title"])
          .agg(mean_gap=("norm_gap", "mean"), weeks=("norm_gap", "size"),
               flagged=("is_discrepancy", "sum"), signed=("rank_gap", "mean"))
          .reset_index()
          .sort_values(["mean_gap", "flagged", "weeks", "show_title"],
                       ascending=[False, False, False, True])
          .head(k))
    return pd.DataFrame({
        "Title": g["show_title"], "Market": g["market"].map(MARKET_NAME),
        "Category": g["category"],
        "Direction": np.where(g["signed"] > 0, "Attention ahead", "Netflix ahead"),
        "Mean normalized gap": [fmt2(v) for v in g["mean_gap"]],
        "Weeks evaluated": g["weeks"], "Weeks flagged": g["flagged"].astype(int),
    })


def _grouped_bars(t: pd.DataFrame, value: str, label, title: str, height=360) -> go.Figure:
    """Films and TV bars side by side per market; label(row) gives each bar's end label."""
    fig = go.Figure()
    for cat in ["Films", "TV"]:
        s = t[t["category"] == cat].set_index("market").reindex(MARKETS).reset_index()
        fig.add_trace(go.Bar(
            x=[MARKET_NAME[m] for m in s["market"]], y=s[value], name=cat,
            marker=dict(color=COLOR[cat], cornerradius=4, line=dict(color=SURFACE, width=2)),
            text=[label(r) for r in s.itertuples()],
            textposition="outside", textfont=dict(color=INK_2, size=12), cliponaxis=False))
    fig.update_layout(barmode="group", bargap=0.35, bargroupgap=0.08)
    fig.update_yaxes(tickformat=".0%", rangemode="tozero", title_text=title)
    _base_layout(fig, height=height, margin=dict(l=10, r=10, t=50, b=40))
    _legend_note(fig)
    return fig


def mapping_rate_chart(d: dict) -> go.Figure:
    t = mapping_rates(d)
    fig = _grouped_bars(t, "rate", lambda r: f"{r.rate:.0%}",
                        "Charted titles with a local-language article")
    fig.update_yaxes(range=[0, 0.8])
    return fig


def article_lag_chart(d: dict) -> go.Figure:
    t = article_lag(d)
    fig = _grouped_bars(t, "share_late", lambda r: f"{int(r.appeared_after_chart)} of {int(r.pairs)}",
                        "Articles first read after the title charted")
    fig.update_yaxes(range=[0, 0.4])
    return fig


def timing_chart(d: dict) -> go.Figure:
    """Share of pairs by peak day relative to the first chart Monday, with overflow bins."""
    lo, hi = -28, 42
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.12,
                        subplot_titles=("Films", "TV"))
    u = d["timing_usable"]
    for row, cat in enumerate(["Films", "TV"], start=1):
        days = u.loc[u["category"] == cat, "days_peak_vs_chart"].clip(lo - 1, hi + 1)
        counts = days.value_counts().reindex(range(lo - 1, hi + 2), fill_value=0)
        share = counts / counts.sum()
        fig.add_trace(go.Bar(x=share.index, y=share.values,
                             marker=dict(color=COLOR[cat], cornerradius=2, line=dict(color=SURFACE, width=1)),
                             width=0.9), row=row, col=1)
        # Added after the bars: Plotly skips shapes on subplots that are
        # still empty. layer="below" keeps the band behind the bars.
        fig.add_vrect(x0=-0.5, x1=6.5, fillcolor=GRID, opacity=0.55, line_width=0,
                      layer="below", row=row, col=1)
        fig.add_annotation(x=3, y=share.max() * 1.02, text="first chart week", showarrow=False,
                           yanchor="bottom", font=dict(size=11, color=MUTED), row=row, col=1)
        fig.update_yaxes(tickformat=".0%", rangemode="tozero", row=row, col=1,
                         range=[0, share.max() * 1.25])
    ticks = [lo - 1, -21, -14, -7, 0, 7, 14, 21, 28, 35, hi + 1]
    text = [f"≤{lo - 1}"] + [str(t) for t in ticks[1:-1]] + [f"≥{hi + 1}"]
    fig.update_xaxes(tickvals=ticks, ticktext=text, row=2, col=1,
                     title_text="Days from the Monday of the first chart week to the pageview peak")
    fig.update_annotations(selector=dict(text="Films"), font=dict(color=COLOR["Films"], size=14), x=0, xanchor="left")
    fig.update_annotations(selector=dict(text="TV"), font=dict(color=COLOR["TV"], size=14), x=0, xanchor="left")
    _base_layout(fig, height=480, bargap=0.05)
    return fig


def timing_table(d: dict) -> pd.DataFrame:
    u = d["timing_usable"]
    rows = []
    for (m, cat), s in u.groupby(["market", "category"]):
        s = s["days_peak_vs_chart"]
        rows.append({"Market": MARKET_NAME[m], "Category": cat, "Pairs": len(s),
                     "Median days": f"{s.median():g}",
                     "Peak before charting": f"{(s < 0).mean():.0%}",
                     "Peak in first chart week": f"{s.between(0, 6).mean():.0%}",
                     "Peak later": f"{(s > 6).mean():.0%}", "_m": MARKETS.index(m)})
    return pd.DataFrame(rows).sort_values(["Category", "_m"]).drop(columns="_m")
