# user-prompt-submit.ps1 - Windows hook: inject active plan into every prompt
param()
$planFile     = Join-Path (Get-Location) "task_plan.md"
$progressFile = Join-Path (Get-Location) "progress.md"

if (-not (Test-Path $planFile)) { exit 0 }

Write-Output "[planning-with-files] ACTIVE PLAN - current state:"
Get-Content $planFile | Select-Object -First 50
Write-Output ""
Write-Output "=== recent progress ==="
if (Test-Path $progressFile) {
    Get-Content $progressFile | Select-Object -Last 20
}
Write-Output ""
Write-Output "[planning-with-files] Read findings.md for research context. Continue from the current phase."
exit 0
