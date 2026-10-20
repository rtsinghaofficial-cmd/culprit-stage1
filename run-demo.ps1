$ErrorActionPreference = "Stop"

$Python = Join-Path $PSScriptRoot ".venv\Scripts\python.exe"
$OutputDir = Join-Path $PSScriptRoot "demo-results"

if (-not (Test-Path $Python)) {
    throw "Virtual environment Python not found: $Python"
}

New-Item -ItemType Directory -Force $OutputDir | Out-Null

Write-Host "`n=== CULPRIT: SHARED-FAULT SCENARIO ===" -ForegroundColor Cyan
& $Python -m culprit.experiments.run --scenario fault --seed 20261010 --vehicles 5000 |
    Set-Content (Join-Path $OutputDir "fault-live.json") -Encoding utf8
if ($LASTEXITCODE -ne 0) { throw "Fault scenario failed." }

Get-Content (Join-Path $OutputDir "fault-live.json")

Write-Host "`n=== CULPRIT: SIMPSON SCENARIO ===" -ForegroundColor Cyan
& $Python -m culprit.experiments.run --scenario simpson --seed 20261010 --vehicles 5000 |
    Set-Content (Join-Path $OutputDir "simpson-live.json") -Encoding utf8
if ($LASTEXITCODE -ne 0) { throw "Simpson scenario failed." }

Get-Content (Join-Path $OutputDir "simpson-live.json")

Write-Host "`nDemo complete. Outputs saved in demo-results." -ForegroundColor Green
