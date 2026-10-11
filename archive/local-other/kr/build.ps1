$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

# Folder names are the single source of truth for include paths and PDF jobnames.
$Chapters = @(
  @{ N = 1; Dir = "Chapter-01-Introduction-and-Research-Problem" },
  @{ N = 2; Dir = "Chapter-02-Literature-Review-and-Theoretical-Framework" },
  @{ N = 3; Dir = "Chapter-03-Research-Methodology" },
  @{ N = 4; Dir = "Chapter-04-Implementation-and-Empirical-Results" },
  @{ N = 5; Dir = "Chapter-05-Discussion" },
  @{ N = 6; Dir = "Chapter-06-Conclusion-and-Future-Work" },
  @{ N = 7; Dir = "Chapter-07-References" },
  @{ N = 8; Dir = "Chapter-08-Appendix" }
)

# Full dissertation (writes <Dir>/index.aux checkpoints and main.aux)
xelatex -interaction=nonstopmode main.tex
if ($LASTEXITCODE -ne 0) { throw "xelatex main.tex (pass 1) failed" }
xelatex -interaction=nonstopmode main.tex
if ($LASTEXITCODE -ne 0) { throw "xelatex main.tex (pass 2) failed" }

# Preserve chapter aux from the full build; per-chapter runs would otherwise overwrite page checkpoints
$auxBackup = Join-Path $PSScriptRoot "_chapter_aux_backup"
New-Item -ItemType Directory -Force -Path $auxBackup | Out-Null
foreach ($c in $Chapters) {
  Copy-Item -Force "$($c.Dir)/index.aux" "$auxBackup/$($c.Dir).aux"
}

function Restore-ChapterAux {
  foreach ($c in $Chapters) {
    Copy-Item -Force "$auxBackup/$($c.Dir).aux" "$($c.Dir)/index.aux"
  }
}

function Get-ChapterStartPage([int]$n, [string]$dir) {
  $aux = Get-Content -Raw "$dir/index.aux"
  $m = [regex]::Match($aux, 'contentsline \{chapter\}.*\{(\d+)\}\{chapter\.' + $n + '\}')
  if (-not $m.Success) { throw "Could not parse start page for $dir" }
  return [int]$m.Groups[1].Value
}

# Per-chapter PDFs: jobname = folder name so PDF matches the directory
foreach ($c in $Chapters) {
  Restore-ChapterAux
  $dir = $c.Dir
  Copy-Item -Force main.aux "$dir.aux"
  if (Test-Path main.out) {
    Copy-Item -Force main.out "$dir.out"
  }
  $startPage = Get-ChapterStartPage $c.N $dir
  xelatex -interaction=nonstopmode -jobname="$dir" `
    "\def\ChapterOnly{$($c.N)}\def\ChapterOnlyPath{$dir}\def\ChapterStartPage{$startPage}\input{main.tex}"
  if ($LASTEXITCODE -ne 0) { throw "xelatex $dir failed" }
}

Restore-ChapterAux
Write-Host "Built main.pdf and:"
$Chapters | ForEach-Object { Write-Host "  $($_.Dir).pdf" }
