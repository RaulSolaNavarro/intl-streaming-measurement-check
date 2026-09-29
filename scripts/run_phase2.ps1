# Runs Phase 2 end to end: load the Phase 1 tables into BigQuery, run the
# SQL in /sql, export the results, and verify them.
#
# Usage (from the repo root, in PowerShell, after run_phase1.ps1):
#   .\scripts\run_phase2.ps1
#
# Needs Application Default Credentials (gcloud auth application-default login).
# Stops at the first script that fails.

$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
$python = Join-Path $root ".venv\Scripts\python.exe"
if (-not (Test-Path $python)) { throw "No .venv found. Run .\scripts\run_phase1.ps1 first." }

foreach ($script in @("06_load_bigquery.py", "07_run_sql.py", "08_check_phase2.py")) {
    Write-Host "`n=== $script ==="
    & $python (Join-Path $PSScriptRoot $script)
    if ($LASTEXITCODE -ne 0) { throw "$script failed with exit code $LASTEXITCODE" }
}

Write-Host "`nPhase 2 complete. Summary: data\logs\phase2_summary.md"
