# 허락의 화살표: XeLaTeX로 두 번 빌드합니다(차례와 그림 번호를 맞추려고).
Set-Location $PSScriptRoot
xelatex -interaction=nonstopmode main.tex
xelatex -interaction=nonstopmode main.tex
Write-Host "main.pdf"
