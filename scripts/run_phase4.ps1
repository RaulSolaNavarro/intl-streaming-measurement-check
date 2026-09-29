# Renders the Quarto report in /report to /docs (the GitHub Pages folder).
#
# Usage (from the repo root, in PowerShell, after run_phase3.ps1):
#   .\scripts\run_phase4.ps1
#
# Quarto runs the report's Python code with the project's .venv, so the
# charts use the same pandas and plotly versions as the pipeline.

$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
$python = Join-Path $root ".venv\Scripts\python.exe"
if (-not (Test-Path $python)) { throw "No .venv found. Run .\scripts\run_phase1.ps1 first." }

# docs/ is fully generated. Quarto doesn't clean an output folder that sits
# outside the project, so old files (such as stylesheets with an outdated
# content hash) would pile up. Start from an empty folder every time.
$docs = Join-Path $root "docs"
if (Test-Path $docs) { Remove-Item $docs -Recurse -Force }

$env:QUARTO_PYTHON = $python
# Quarto writes progress messages to stderr. Windows PowerShell 5.1 turns
# stderr from a native command into an error record, which "Stop" would treat
# as fatal, so relax it here and judge success by the exit code instead.
$ErrorActionPreference = "Continue"
quarto render (Join-Path $root "report") 2>&1 |
    ForEach-Object { "$_" } |
    Where-Object { $_ -ne "System.Management.Automation.RemoteException" }  # blank stderr lines
if ($LASTEXITCODE -ne 0) { throw "quarto render failed with exit code $LASTEXITCODE" }

# An empty .nojekyll file tells GitHub Pages to serve docs/ as plain files
# instead of running it through Jekyll.
$nojekyll = Join-Path $root "docs\.nojekyll"
if (-not (Test-Path $nojekyll)) { New-Item -ItemType File -Path $nojekyll | Out-Null }

Write-Host "`nReport rendered to docs\index.html"
