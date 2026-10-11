$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

if (-not (Test-Path "main.pdf")) {
    Write-Host "main.pdf not found; building PDF first..."
    & (Join-Path $PSScriptRoot "build.ps1")
}

python (Join-Path $PSScriptRoot "..\scripts\build_proposal_docx_from_pdf.py") `
    (Join-Path $PSScriptRoot "main.pdf") `
    (Join-Path $PSScriptRoot "main.docx")

Write-Host "Built main.docx (PDF layout via pdf2docx)"
