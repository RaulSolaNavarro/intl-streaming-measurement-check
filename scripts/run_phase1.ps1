# Runs the Phase 1 data pull end to end, in order.
#
# Usage (from the repo root, in PowerShell):
#   .\scripts\run_phase1.ps1            # reuse cached downloads where possible
#   .\scripts\run_phase1.ps1 -Refresh   # download everything again
#
# Creates .venv and installs requirements.txt on first run.
# Stops at the first script that fails.

param([switch]$Refresh)

$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
$python = Join-Path $root ".venv\Scripts\python.exe"

if (-not (Test-Path $python)) {
    Write-Host "Creating virtual environment in .venv"
    python -m venv (Join-Path $root ".venv")
    & $python -m pip install --quiet -r (Join-Path $root "requirements.txt")
}

$refreshArg = @()
if ($Refresh) { $refreshArg = @("--refresh") }

$steps = @(
    @{ Script = "01_pull_netflix.py";   Args = $refreshArg },
    @{ Script = "02_select_titles.py";  Args = @() },
    @{ Script = "03_map_wikidata.py";   Args = @() },
    @{ Script = "04_pull_pageviews.py"; Args = $refreshArg },
    @{ Script = "05_check_phase1.py";   Args = @() }
)

foreach ($step in $steps) {
    Write-Host "`n=== $($step.Script) ==="
    & $python (Join-Path $PSScriptRoot $step.Script) @($step.Args)
    if ($LASTEXITCODE -ne 0) { throw "$($step.Script) failed with exit code $LASTEXITCODE" }
}

Write-Host "`nPhase 1 complete. Summary: data\logs\phase1_summary.md"
