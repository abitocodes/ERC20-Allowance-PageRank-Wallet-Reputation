# Builds the Korean reading editions: xelatex, bibtex, then xelatex twice in each folder,
# and reports pages, LaTeX errors, undefined references or citations, overfull lines over
# 1pt, text outside the text block (check_layout.py) and particles that do not fit the
# printed reference numbers (check_particles.py).
#   .\build.ps1                 both editions
#   .\build.ps1 A-plos-one      one edition
param([string[]]$Docs = @("A-plos-one", "B-ieee-access"))
$ErrorActionPreference = "Stop"

foreach ($d in $Docs) {
  Push-Location (Join-Path $PSScriptRoot $d)
  try {
    xelatex -interaction=nonstopmode main.tex | Out-Null
    bibtex main | Out-Null
    xelatex -interaction=nonstopmode main.tex | Out-Null
    xelatex -interaction=nonstopmode main.tex | Out-Null
    $log = Get-Content -Raw -Encoding utf8 main.log
    $errors = [regex]::Matches($log, '(?m)^! .*')
    $undefined = [regex]::Matches($log, "(?m)^(LaTeX|Package natbib) Warning: (Reference|Citation) .* undefined")
    $overfull = [regex]::Matches($log, '(?m)^Overfull \\hbox \(([\d.]+)pt too wide\).*') |
      Where-Object { [double]$_.Groups[1].Value -gt 1.0 }
    $pages = [regex]::Match($log, 'Output written on main\.pdf \((\d+) page').Groups[1].Value
    Write-Host ("{0}: {1} pages, {2} errors, {3} undefined, {4} overfull lines over 1pt" -f `
      $d, $pages, $errors.Count, $undefined.Count, @($overfull).Count)
    foreach ($m in @($errors) + @($undefined) + @($overfull)) { if ($m) { Write-Host "  $($m.Value)" } }
    python -I -X utf8 (Join-Path $PSScriptRoot "check_layout.py") main.pdf
  } finally { Pop-Location }
  python -I -X utf8 (Join-Path $PSScriptRoot "check_particles.py") $d
}
