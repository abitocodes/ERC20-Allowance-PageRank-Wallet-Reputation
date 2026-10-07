$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

# 한국어 번역본 전체를 만듭니다. 차례와 참조를 맞추려고 세 번 실행합니다.
for ($i = 1; $i -le 3; $i++) {
  xelatex -interaction=nonstopmode main.tex
  if ($LASTEXITCODE -ne 0) { throw "xelatex main.tex (pass $i) failed" }
}
Write-Host "Built main.pdf"
