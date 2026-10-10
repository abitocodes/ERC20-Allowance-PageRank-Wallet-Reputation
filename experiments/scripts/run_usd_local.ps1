# Local evaluation of the revised analysis (docs/revision_price_weighting.md), in the order of the registered one.
# Run from experiments/ after scripts/run_usd_pipeline.py has downloaded graph-tables-usd.
param([string]$From = "")
$ErrorActionPreference = "Stop"
Set-Location (Split-Path $PSScriptRoot -Parent)
$env:CONTRACT_REP_VARIANT = "usd"
$env:PYTHONDONTWRITEBYTECODE = "1"
$steps = @("run_same_window", "run_holdout", "run_registered", "run_supplementary", "run_robustness",
           "sybil_model", "describe_data", "run_benchmark")
if ($From) { $steps = $steps[([array]::IndexOf($steps, $From))..($steps.Count - 1)] }
foreach ($s in $steps) {
  $t0 = Get-Date
  Write-Host "== $s started $($t0.ToUniversalTime().ToString('u'))"
  python "scripts/$s.py"
  if ($LASTEXITCODE -ne 0) { throw "$s failed" }
  Write-Host "== $s done in $([int]((Get-Date) - $t0).TotalSeconds) s"
}
