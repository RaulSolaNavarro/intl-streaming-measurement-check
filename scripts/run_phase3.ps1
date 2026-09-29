# Runs the Phase 3 analysis on the exported BigQuery results.
#
# Usage (from the repo root, in PowerShell, after run_phase2.ps1):
#   .\scripts\run_phase3.ps1
#
# Output: data\processed\analysis\*.csv and data\logs\phase3_analysis.md

$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
$python = Join-Path $root ".venv\Scripts\python.exe"
if (-not (Test-Path $python)) { throw "No .venv found. Run .\scripts\run_phase1.ps1 first." }

Write-Host "`n=== 09_analysis.py ==="
& $python (Join-Path $PSScriptRoot "09_analysis.py")
if ($LASTEXITCODE -ne 0) { throw "09_analysis.py failed with exit code $LASTEXITCODE" }

Write-Host "`nPhase 3 complete. Tables: data\logs\phase3_analysis.md"
