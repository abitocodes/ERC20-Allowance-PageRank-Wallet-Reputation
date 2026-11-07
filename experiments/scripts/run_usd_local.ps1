# Local evaluation of the revised analysis (docs/revision_price_weighting.md), in the order of the registered one.
# Run from experiments/ after scripts/run_usd_pipeline.py has downloaded graph-tables-usd, or with
# -Variant usd12m after scripts/run_usd12m_pipeline.py has downloaded graph-tables-usd-12m
# (docs/revision_one_year_window.md), or with -Variant contract12m after scripts/run_contract12m_pipeline.py
# has downloaded graph-tables-contract-12m (docs/revision_contract_graph.md); that variant runs the
# discovery-order test (docs/discovery_protocol.md) right after the same-window evaluation: every main run
# (T_obs then t1, the primary mode then the other) in -Workers processes, 16 by default as in the run-time
# projection of the protocol (section 7); the results do not depend on the number.
param([string]$From = "", [ValidateSet("usd", "usd12m", "contract12m")][string]$Variant = "usd",
      [ValidateRange(1, 256)][int]$Workers = 16)
$ErrorActionPreference = "Stop"
Set-Location (Split-Path $PSScriptRoot -Parent)
$env:CONTRACT_REP_VARIANT = $Variant
$env:PYTHONDONTWRITEBYTECODE = "1"
$steps = @("run_same_window", "run_holdout", "run_registered", "run_supplementary", "run_robustness",
           "sybil_model", "describe_data", "run_benchmark")
if ($Variant -eq "contract12m") { $steps = @($steps[0], "run_discovery") + $steps[1..($steps.Count - 1)] }
if ($From) { $steps = $steps[([array]::IndexOf($steps, $From))..($steps.Count - 1)] }
foreach ($s in $steps) {
  $t0 = Get-Date
  Write-Host "== $s started $($t0.ToUniversalTime().ToString('u'))"
  $extra = @()
  if ($s -eq "run_discovery") { $extra = @("--workers", "$Workers") }
  python "scripts/$s.py" @extra
  if ($LASTEXITCODE -ne 0) { throw "$s failed" }
  Write-Host "== $s done in $([int]((Get-Date) - $t0).TotalSeconds) s"
}
