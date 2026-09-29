"""
Step 06: load the Phase 1 tables into BigQuery.

Input:  data/processed/*.csv and data/logs/{contested,dropped}_pairs.csv
Output: BigQuery dataset intl-streaming-measurement.streaming_measurement with
        netflix_top10, titles, title_markets, title_article_map,
        pageviews_daily, contested_pairs, dropped_pairs

Each table is loaded with an explicit schema and WRITE_TRUNCATE, so rerunning
replaces the table instead of appending duplicates. The dataset is created
in the US location if it doesn't exist.

Authentication: Application Default Credentials from gcloud. No key files.
"""

from __future__ import annotations

import warnings

import pandas as pd
from google.cloud import bigquery

import config

# google-cloud-bigquery warns that a future release will need pandas-gbq for
# DataFrame loads. The current release loads fine without it, so the warning
# is silenced here to keep the pipeline output readable.
warnings.filterwarnings("ignore", message=".*pandas-gbq.*", category=FutureWarning)

S, I, D = "STRING", "INT64", "DATE"

# table name -> (source CSV, {column: BigQuery type}). Column order here is
# the column order in BigQuery.
TABLES = {
    "netflix_top10": (config.NETFLIX_6MKTS_CSV, {
        "country_name": S, "country_iso2": S, "week": D, "category": S, "weekly_rank": I,
        "show_title": S, "season_title": S, "cumulative_weeks_in_top_10": I}),
    "titles": (config.TITLES_CSV, {
        "title_id": S, "show_title": S, "category": S, "n_markets": I, "market_weeks": I,
        "best_rank": I, "markets": S}),
    "title_markets": (config.TITLE_MARKETS_CSV, {
        "title_id": S, "show_title": S, "category": S, "market": S, "first_week": D,
        "last_week": D, "weeks_charted": I, "best_rank": I, "lang": S}),
    "title_article_map": (config.TITLE_ARTICLE_MAP_CSV, {
        "title_id": S, "show_title": S, "category": S, "market": S, "lang": S, "qid": S,
        "match_method": S, "match_status": S, "article": S}),
    "pageviews_daily": (config.PAGEVIEWS_DAILY_CSV, {
        "title_id": S, "show_title": S, "category": S, "qid": S, "market": S, "lang": S,
        "article": S, "date": D, "views": I}),
    "contested_pairs": (config.CONTESTED_PAIRS_CSV, {
        "title_id": S, "show_title": S, "category": S, "market": S, "lang": S, "qid": S,
        "first_week": D, "netflix_id_qid": S, "newer_rivals": S, "outcome": S,
        "final_qid": S, "note": S}),
    "dropped_pairs": (config.DROPPED_PAIRS_CSV, {
        "title_id": S, "show_title": S, "category": S, "market": S, "lang": S, "qid": S,
        "reason": S}),
}


def prepare(csv_path, schema: dict[str, str]) -> pd.DataFrame:
    """Read a CSV as text, then cast each column to its declared type."""
    df = pd.read_csv(csv_path, dtype=str, keep_default_na=False)
    missing = set(schema) - set(df.columns)
    if missing:
        raise ValueError(f"{csv_path.name} is missing columns {sorted(missing)}")
    df = df[list(schema)].copy()
    for col, typ in schema.items():
        if typ == D:
            df[col] = pd.to_datetime(df[col].replace("", None)).dt.date
        elif typ == I:
            df[col] = pd.to_numeric(df[col].replace("", None)).astype("Int64")
        else:
            df[col] = df[col].replace("", None)  # empty string -> NULL
    return df


def main() -> None:
    client = bigquery.Client(project=config.BQ_PROJECT, location=config.BQ_LOCATION)

    dataset = bigquery.Dataset(f"{config.BQ_PROJECT}.{config.BQ_DATASET}")
    dataset.location = config.BQ_LOCATION
    client.create_dataset(dataset, exists_ok=True)

    for name, (csv_path, schema) in TABLES.items():
        df = prepare(csv_path, schema)
        job = client.load_table_from_dataframe(
            df, f"{config.BQ_PROJECT}.{config.BQ_DATASET}.{name}",
            job_config=bigquery.LoadJobConfig(
                schema=[bigquery.SchemaField(c, t) for c, t in schema.items()],
                write_disposition="WRITE_TRUNCATE"))
        job.result()
        table = client.get_table(job.destination)
        print(f"Loaded {name}: {table.num_rows:,} rows (local CSV: {len(df):,})")


if __name__ == "__main__":
    main()
