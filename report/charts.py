"""
Data loading and chart builders for the Quarto report (report/index.qmd).

Everything here reads the committed CSVs in data/, never BigQuery, so the
report renders the same way after the BigQuery tables are gone.

Charts are Plotly figures shown with staticPlot=True: no hover, zoom, or
toolbar, matching the project rule that report charts are static. Each chart
in the report is paired with a table view of the same numbers.

Every chart carries a title that states its finding. Titles and captions are
built from the data by the *_title() and *_caption() functions, so a data
refresh updates them along with the chart.

Colors: Films = categorical slot 1 (blue), TV = slot 2 (orange), from the
reference data-viz palette, in every chart. Gray marks "not the point of
this chart" (an interval that includes zero, a non-Sunday bar). Ink, grid,
and surface colors come from the same palette.
"""

from __future__ import annotations

import importlib.util
import sys
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
# Adjective form used in sentences such as "Brazilian TV" or "German films".
MARKET_ADJ = {"DE": "German", "FR": "French", "JP": "Japanese", "BR": "Brazilian",
              "IT": "Italian", "KR": "Korean"}
NUMBER_WORD = {0: "zero", 1: "one", 2: "two", 3: "three", 4: "four", 5: "five", 6: "six",
               7: "seven", 8: "eight", 9: "nine", 10: "ten", 11: "eleven", 12: "twelve"}

# Palette (light mode).
COLOR = {"Films": "#2a78d6", "TV": "#eb6834"}
GRAY_MARK = "#b9b7b0"   # de-emphasized marks: intervals that include zero, non-Sunday bars
SURFACE = "#ffffff"  # matches the page background
INK = "#0b0b0b"
INK_2 = "#52514e"
MUTED = "#898781"
GRID = "#e1e0d9"
AXIS = "#c3c2b7"
FONT = 'system-ui, -apple-system, "Segoe UI", sans-serif'

# Timing chart x-range; peaks beyond it are grouped into one bin at each end.
TIMING_LO, TIMING_HI = -28, 42


def cell_name(market: str, category: str) -> str:
    """'Brazilian TV', 'German films'."""
    return f"{MARKET_ADJ[market]} {'TV' if category == 'TV' else 'films'}"


def pipeline_constants() -> dict:
    """
    Thresholds the report quotes, read from the pipeline scripts themselves
    so the text can't drift from the code that applied them.
    """
    scripts = ROOT / "scripts"
    if str(scripts) not in sys.path:
        sys.path.insert(0, str(scripts))  # the scripts import their shared config module

    def module(name: str, file: str):
        spec = importlib.util.spec_from_file_location(name, scripts / file)
        m = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(m)
        return m

    import config  # noqa: E402  (scripts/config.py)
    mapping = module("map_wikidata", "03_map_wikidata.py")
    analysis = module("analysis", "09_analysis.py")
    return {
        "min_n": config.MIN_N_PER_WEEK,                       # titles per week for weekly rho / discrepancies
        "window_weeks": config.WINDOW_WEEKS,
        "tiebreak_years": mapping.TIEBREAK_MAX_YEARS,
        "override_years": round(mapping.OVERRIDE_WINDOW_DAYS / 365),
        "n_boot": analysis.N_BOOT,
        "low_conf_n": analysis.LOW_CONFIDENCE_N,
    }

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


def show(fig: go.Figure, caption: str | None = None) -> None:
    """
    Emit a figure as plain HTML (the library comes from plotly_library()),
    followed by its caption. The caption is written here rather than with
    Quarto's fig-cap option because fig-cap can't hold values computed in
    Python, and captions quote numbers from the data.
    """
    display(HTML(fig.to_html(full_html=False, include_plotlyjs=False, config=STATIC)))
    if caption:
        display(HTML(f'<p class="figure-caption" style="margin-top:0.25rem">{caption}</p>'))


def _title(fig: go.Figure, text: str, note: str | None = None) -> None:
    """Chart title stating the finding, top left, with an optional smaller note line."""
    full = f"<b>{text}</b>"
    if note:
        full += f"<br><span style='font-size:12px;color:{INK_2}'>{note}</span>"
    fig.update_layout(title=dict(text=full, x=0, xanchor="left", y=0.98, yanchor="top",
                                 font=dict(size=15, color=INK)))


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

def agreement_title(d: dict) -> str:
    """'Agreement is above zero in 8 of 12 market-categories, strongest in French TV (ρ = 0.70)'"""
    a = agreement_all(d)
    above = int((a["ci_low"] > 0).sum())
    best = a.loc[a["pooled_rho"].idxmax()]
    return (f"Agreement is above zero in {above} of {len(a)} market-categories,<br>"
            f"strongest in {cell_name(best.market, best.category)} (ρ = {best.pooled_rho:.2f})")


def agreement_caption(d: dict, low_conf_n: int) -> str:
    return ("For each market and category, I ranked the charting titles twice every week, once by "
            "Netflix rank and once by pageviews, and measured how well the two orders line up across "
            "all weeks (pooled Spearman's ρ: 1 means the same order, 0 means no relationship). Bars "
            "are 95% bootstrap intervals. Gray cells have an interval that includes zero. Hollow "
            f"markers are low confidence (fewer than {low_conf_n} title-weeks).")


def forest_plot(d: dict) -> go.Figure:
    a = agreement_all(d)
    a["includes_zero"] = (a["ci_low"] <= 0) & (a["ci_high"] >= 0)
    best = a.loc[a["pooled_rho"].idxmax()]
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.08,
                        subplot_titles=("Films", "TV"))
    for row, cat in enumerate(["Films", "TV"], start=1):
        s = a[a["category"] == cat].set_index("market").loc[MARKETS[::-1]].reset_index()
        # Low-confidence rows say so in the axis label, so it isn't carried
        # by the hollow marker alone.
        s["label"] = [f"{MARKET_NAME[m]} (low confidence, n={n})" if low else MARKET_NAME[m]
                      for m, low, n in zip(s["market"], s["low_confidence"], s["n_title_weeks"])]
        # One trace per (interval includes zero, low confidence) group, because
        # an error bar can only have one color per trace.
        for zero in (False, True):
            for low in (False, True):
                part = s[(s["includes_zero"] == zero) & (s["low_confidence"] == low)]
                if part.empty:
                    continue
                color = GRAY_MARK if zero else COLOR[cat]
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
                                 color=color, thickness=2, width=0),
                    marker=dict(size=11, color=SURFACE if low else color,
                                symbol="circle", line=dict(color=color, width=2))),
                    row=row, col=1)
        fig.update_yaxes(categoryorder="array", categoryarray=list(s["label"]),
                         row=row, col=1, showgrid=False)
        fig.add_vline(x=0, line=dict(color=AXIS, width=1), row=row, col=1)
        if best.category == cat:
            # Call out the strongest cell, with the label to its left.
            label = s.loc[s["market"] == best.market, "label"].iloc[0]
            fig.add_annotation(x=best.pooled_rho, y=label, ax=-95, ay=-26, row=row, col=1,
                               text=f"<b>Strongest: {cell_name(best.market, best.category)}</b>",
                               showarrow=True, arrowhead=0, arrowwidth=1, arrowcolor=INK_2,
                               font=dict(size=12, color=INK), xanchor="right")
    fig.update_xaxes(range=[-1.05, 1.05], tickvals=[-1, -0.5, 0, 0.5, 1], tickangle=0)
    fig.update_xaxes(title_text="Pooled Spearman ρ (bars: 95% CI)", row=2, col=1)
    fig.update_annotations(selector=dict(text="Films"), font=dict(color=COLOR["Films"], size=14), x=0, xanchor="left")
    fig.update_annotations(selector=dict(text="TV"), font=dict(color=COLOR["TV"], size=14), x=0, xanchor="left")
    _title(fig, agreement_title(d), "Gray: interval includes zero. Hollow: low confidence.")
    # Top margin holds the title, note, and the first row's value label.
    _base_layout(fig, height=680, margin=dict(l=10, r=20, t=125, b=60))
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


DISC_MIN_WEEKS = 3  # a pair needs this many evaluated weeks to be listed
DISC_TOP_K = 10


def top_discrepancies(d: dict) -> tuple[pd.DataFrame, int]:
    """
    The most persistent disagreements. Returns (table, number of pairs that
    qualified).

    A title-market pair qualifies if it was evaluated (market-week with
    n >= 4 titles) in at least DISC_MIN_WEEKS weeks, so one unusual week
    can't put a title at the top. Pairs are ranked by the share of their
    evaluated weeks that were flagged, then by mean normalized gap, then
    title. Up to DISC_TOP_K are shown. Direction follows the sign of the
    mean rank gap.
    """
    x = d["disc"][d["disc"]["variant"] == "all"]
    g = (x.groupby(["market", "category", "title_id", "show_title"])
          .agg(mean_gap=("norm_gap", "mean"), weeks=("norm_gap", "size"),
               flagged=("is_discrepancy", "sum"), signed=("rank_gap", "mean"))
          .reset_index())
    g = g[g["weeks"] >= DISC_MIN_WEEKS].copy()
    n_qualified = len(g)
    g["share"] = g["flagged"] / g["weeks"]
    g = (g.sort_values(["share", "mean_gap", "show_title"], ascending=[False, False, True])
          .head(DISC_TOP_K))
    table = pd.DataFrame({
        "Title": g["show_title"], "Market": g["market"].map(MARKET_NAME),
        "Category": g["category"],
        "Direction": np.where(g["signed"] > 0, "Attention ahead", "Netflix ahead"),
        "Weeks flagged": [f"{int(f)} of {int(w)}" for f, w in zip(g["flagged"], g["weeks"])],
        "Share flagged": [f"{s:.0%}" for s in g["share"]],
        "Mean normalized gap": [fmt2(v) for v in g["mean_gap"]],
    })
    return table, n_qualified


LEGEND = (f"<span style='color:{COLOR['Films']}'>●</span> Films &nbsp; "
          f"<span style='color:{COLOR['TV']}'>●</span> TV")


def _grouped_bars(t: pd.DataFrame, value: str, label, axis_title: str, height=400) -> go.Figure:
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
    fig.update_yaxes(tickformat=".0%", rangemode="tozero", title_text=axis_title)
    _base_layout(fig, height=height, margin=dict(l=10, r=10, t=95, b=40))
    return fig


def overall_mapping_rate(d: dict) -> float:
    """Share of all charted title-market pairs that have a local-language article."""
    return len(d["amap"]) / len(d["pairs"])


def coverage_title(d: dict) -> str:
    """'Fewer than half of charted titles have a local-language article. Brazilian TV is lowest at 17%'"""
    overall = overall_mapping_rate(d)
    lead = ("Fewer than half" if overall < 0.5 else "Half" if overall == 0.5 else "More than half")
    t = mapping_rates(d)
    low = t.loc[t["rate"].idxmin()]
    return (f"{lead} of charted titles have a local-language article.<br>"
            f"{cell_name(low.market, low.category)} is lowest at {low.rate:.0%}")


def coverage_caption(d: dict) -> str:
    return ("Share of charted titles with an article in the market's language edition, by market "
            f"and category. The dashed line is the rate across all {len(d['pairs'])} charted "
            "title-market pairs. The two lowest bars are labeled.")


def mapping_rate_chart(d: dict) -> go.Figure:
    t = mapping_rates(d)
    # The two lowest bars get a word under their value, so they stand out
    # without a second color.
    ranked = t.sort_values("rate").reset_index(drop=True)
    tag = {(ranked.loc[0, "market"], ranked.loc[0, "category"]): "lowest",
           (ranked.loc[1, "market"], ranked.loc[1, "category"]): "2nd lowest"}

    def label(r):
        word = tag.get((r.market, r.category))
        return f"<b>{r.rate:.0%}</b><br>{word}" if word else f"{r.rate:.0%}"

    fig = _grouped_bars(t, "rate", label, "Charted titles with an article")
    overall = overall_mapping_rate(d)
    fig.add_hline(y=overall, line=dict(color=INK_2, width=1, dash="dash"))
    # Label the reference line in the right margin, clear of the bar labels.
    fig.add_annotation(xref="paper", x=1.0, y=overall, xanchor="left", xshift=6, showarrow=False,
                       text=f"All pairs<br><b>{overall:.0%}</b>", align="left",
                       font=dict(size=12, color=INK_2))
    fig.update_yaxes(range=[0, 0.8])
    _title(fig, coverage_title(d), LEGEND)
    fig.update_layout(margin=dict(r=70))
    return fig


def article_lag_title(d: dict) -> str:
    t = article_lag(d)
    late, total = int(t["appeared_after_chart"].sum()), int(t["pairs"].sum())
    worst = t.loc[t["share_late"].idxmax()]
    return (f"{late} of {total} articles were first read only after the title charted.<br>"
            f"{cell_name(worst.market, worst.category)} lags most "
            f"({int(worst.appeared_after_chart)} of {int(worst.pairs)})")


def article_lag_chart(d: dict) -> go.Figure:
    t = article_lag(d)
    fig = _grouped_bars(t, "share_late", lambda r: f"{int(r.appeared_after_chart)} of {int(r.pairs)}",
                        "Articles first read after charting")
    fig.update_yaxes(range=[0, 0.4])
    _title(fig, article_lag_title(d), LEGEND)
    return fig


WEEKDAY = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


def is_sunday(day_offset: int) -> bool:
    """Offsets count from a Monday (0), so Sundays are 6, 13, -1, -8, ..."""
    return day_offset % 7 == 6


def timing_title(d: dict) -> str:
    """'62% of peaks fall in the first chart week, most often on its closing Sunday'"""
    s = d["timing_usable"]["days_peak_vs_chart"]
    first = s[s.between(0, 6)]
    top_day = int(first.value_counts().idxmax())   # most common day within the first week
    when = "its closing Sunday" if top_day == 6 else f"its {WEEKDAY[top_day]}"
    return f"{s.between(0, 6).mean():.0%} of peaks fall in the first chart week,<br>most often on {when}"


def timing_caption(d: dict) -> str:
    n = len(d["timing_usable"])
    return ("Day of each title-market pair's pageview peak, counted from the Monday of its first "
            "chart week, as a share of pairs. The shaded band is the first chart week. Colored bars "
            "are Sundays; gray bars are other days. Peaks more than "
            f"{-TIMING_LO} days before or {TIMING_HI} days after that Monday are grouped at the ends "
            "(those end bins mix weekdays, so they stay gray). Uses "
            f"{n} pairs: I left out pairs already charting when the window opened, pairs whose peak "
            "sits on the edge of the data range, and pairs whose article appeared after charting.")


def sunday_share(d: dict) -> float:
    """Share of all usable peaks that fall on a Sunday (from the peak date itself)."""
    u = d["timing_usable"]
    return float((pd.to_datetime(u["peak_date"]).dt.day_name() == "Sunday").mean())


def timing_chart(d: dict) -> go.Figure:
    """Share of pairs by peak day relative to the first chart Monday, with overflow bins."""
    lo, hi = TIMING_LO, TIMING_HI
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.14,
                        subplot_titles=("Films", "TV"))
    u = d["timing_usable"]
    for row, cat in enumerate(["Films", "TV"], start=1):
        days = u.loc[u["category"] == cat, "days_peak_vs_chart"].clip(lo - 1, hi + 1)
        counts = days.value_counts().reindex(range(lo - 1, hi + 2), fill_value=0)
        share = counts / counts.sum()
        # Sundays in the category color, every other day (and both overflow
        # bins, which mix weekdays) in light gray.
        colors = [COLOR[cat] if is_sunday(x) and lo <= x <= hi else GRAY_MARK for x in share.index]
        fig.add_trace(go.Bar(x=share.index, y=share.values,
                             marker=dict(color=colors, cornerradius=2, line=dict(color=SURFACE, width=1)),
                             width=0.9), row=row, col=1)
        # Added after the bars: Plotly skips shapes on subplots that are
        # still empty. layer="below" keeps the band behind the bars.
        fig.add_vrect(x0=-0.5, x1=6.5, fillcolor=GRID, opacity=0.55, line_width=0,
                      layer="below", row=row, col=1)
        top = share.max()
        fig.add_annotation(x=3, y=top * 1.22, text="first chart week", showarrow=False,
                           yanchor="bottom", font=dict(size=11, color=MUTED), row=row, col=1)
        # Label the Sunday that closes the first chart week (day 6) with its share.
        fig.add_annotation(x=6, y=share.loc[6], text=f"<b>{share.loc[6]:.0%}</b>", showarrow=False,
                           yanchor="bottom", xanchor="left", xshift=4,
                           font=dict(size=12, color=INK), row=row, col=1)
        fig.update_yaxes(tickformat=".0%", rangemode="tozero", row=row, col=1, range=[0, top * 1.45])
    ticks = [lo - 1, -21, -14, -7, 0, 7, 14, 21, 28, 35, hi + 1]
    text = [f"≤{lo - 1}"] + [str(t) for t in ticks[1:-1]] + [f"≥{hi + 1}"]
    fig.update_xaxes(tickvals=ticks, ticktext=text, row=2, col=1,
                     title_text="Days from the Monday of the first chart week to the pageview peak")
    fig.update_annotations(selector=dict(text="Films"), font=dict(color=COLOR["Films"], size=14), x=0, xanchor="left")
    fig.update_annotations(selector=dict(text="TV"), font=dict(color=COLOR["TV"], size=14), x=0, xanchor="left")
    _title(fig, timing_title(d),
           f"Colored bars are Sundays. Sundays hold {sunday_share(d):.0%} of all peaks.")
    _base_layout(fig, height=560, bargap=0.05, margin=dict(l=10, r=10, t=110, b=50))
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
