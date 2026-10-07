$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

xelatex -interaction=nonstopmode main.tex
xelatex -interaction=nonstopmode main.tex

Write-Host "Built main.pdf"
