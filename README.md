# intl-streaming-measurement-check

I compared Netflix's weekly Top 10 in six markets (Germany, France, Japan, Brazil, Italy, South Korea) with Wikipedia pageviews for the same titles in each market's language, to test whether a platform's own chart and an independent attention signal tell the same story. Agreement depends on the market: French TV, German films and Korean TV line up clearly, while German TV, Japanese TV and Brazilian films show no reliable agreement. The biggest limit is coverage, since only 43% of charted title-market pairs have a local-language article, and attention peaks in the same week a title charts, not before.

**Report:** [https://raulsolanavarro.github.io/intl-streaming-measurement-check/](https://raulsolanavarro.github.io/intl-streaming-measurement-check/)

I built this with AI assistance (Claude and Claude Code); the report's [How I built this](https://raulsolanavarro.github.io/intl-streaming-measurement-check/#how-i-built-this) section explains how.

## How to run it

I built this on Windows 11 with PowerShell. You need:

- Python 3.13
- Quarto 1.8 or later
- Google Cloud SDK, logged in with Application Default Credentials (`gcloud auth application-default login`), and access to a BigQuery project. The project ID is set in `scripts/config.py`.

Run the four phases in order from the repo root. The first script creates `.venv` and installs `requirements.txt` if needed.

```powershell
.\scripts\run_phase1.ps1   # Netflix pull, title universe, Wikidata mapping, pageviews, checks
.\scripts\run_phase2.ps1   # BigQuery load, SQL metrics, export, independent checks
.\scripts\run_phase3.ps1   # bootstrap intervals, discrepancies, timing, coverage, dashboard CSVs
.\scripts\run_phase4.ps1   # render the Quarto report into docs/
```

Phases 1 and 3 cache their API answers, so a second run is quick. Add `-Refresh` to `run_phase1.ps1` to download everything again. Each phase writes a readable summary to `data/logs/`, and the check scripts stop the run if any check fails.

## Repo structure

```
scripts/            Pipeline scripts, numbered in run order
  config.py           Markets, window, paths, BigQuery settings, HTTP helper
  01-05               Phase 1: Netflix pull, titles, Wikidata mapping, pageviews, checks
  06-08               Phase 2: BigQuery load, run /sql, independent checks
  09_analysis.py      Phase 3: bootstrap CIs, discrepancies, timing, coverage
  10_export_tableau.py  Phase 3: dashboard-ready CSVs (full market names, shared columns)
  run_phase1-4.ps1    One runner per phase
sql/                BigQuery SQL, one CREATE OR REPLACE TABLE per step (01-10)
data/raw/           Source downloads and API caches (full Netflix file is gitignored)
data/processed/     Cleaned tables loaded to BigQuery
  bq/                 Local copies of every BigQuery result table
  analysis/           Phase 3 output tables
  tableau/            agreement, coverage, and discrepancies CSVs for dashboards
data/logs/          Match log, dropped and contested pairs, phase summaries
report/             Quarto source (index.qmd) and chart code (charts.py)
docs/               Rendered site, published by GitHub Pages
```

## What the numbers are, and aren't

Neither source is audience measurement. Netflix publishes ranks by country, not viewing numbers. Wikipedia pageviews measure attention, not viewing. Language editions don't map one-to-one to countries. The report's limitations section covers these, and lists every title match I couldn't fully confirm.
