"""
Step 07: run the SQL files in /sql, in file-name order, and export results.

Input:  sql/NN_<table>.sql  (each one is a CREATE OR REPLACE TABLE statement)
        the tables loaded by step 06
Output: one BigQuery table per SQL file, named after the file without its
        number prefix (01_title_market_week.sql -> title_market_week)
        data/processed/bq/<table>.csv  (a local copy of every result table)

Local copies matter because the BigQuery tables may not persist long term,
and the report renders its static charts from files.
"""

from __future__ import annotations

import re

from google.cloud import bigquery

import config


def main() -> None:
    client = bigquery.Client(project=config.BQ_PROJECT, location=config.BQ_LOCATION)
    sql_files = sorted(config.SQL_DIR.glob("[0-9][0-9]_*.sql"))
    if not sql_files:
        raise SystemExit(f"No SQL files found in {config.SQL_DIR}")

    for path in sql_files:
        table = re.sub(r"^\d+_", "", path.stem)
        job = client.query(path.read_text(encoding="utf-8"))
        job.result()  # raises with BigQuery's error message if the SQL fails
        full_name = f"{config.BQ_PROJECT}.{config.BQ_DATASET}.{table}"
        # Tables are small, so the plain REST download is fine; this skips the
        # optional BigQuery Storage client (and its warning when not installed).
        df = client.list_rows(full_name).to_dataframe(create_bqstorage_client=False)
        df.to_csv(config.BQ_EXPORT_DIR / f"{table}.csv", index=False)
        mb = (job.total_bytes_processed or 0) / 1e6
        print(f"{path.name}: {table} -> {len(df):,} rows ({mb:.1f} MB processed)")


if __name__ == "__main__":
    main()
