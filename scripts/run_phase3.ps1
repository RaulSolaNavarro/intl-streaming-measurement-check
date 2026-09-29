# Runs the Phase 3 analysis on the exported BigQuery results.
#
# Usage (from the repo root, in PowerShell, after run_phase2.ps1):
#   .\scripts\run_phase3.ps1
#
# Output: data\processed\analysis\*.csv, data\logs\phase3_analysis.md, and
#         dashboard-ready CSVs in data\processed\tableau\

$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
$python = Join-Path $root ".venv\Scripts\python.exe"
if (-not (Test-Path $python)) { throw "No .venv found. Run .\scripts\run_phase1.ps1 first." }

foreach ($script in @("09_analysis.py", "10_export_tableau.py")) {
    Write-Host "`n=== $script ==="
    & $python (Join-Path $PSScriptRoot $script)
    if ($LASTEXITCODE -ne 0) { throw "$script failed with exit code $LASTEXITCODE" }
}

Write-Host "`nPhase 3 complete. Tables: data\logs\phase3_analysis.md, dashboard CSVs: data\processed\tableau\"
