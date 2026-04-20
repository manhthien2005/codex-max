# user-prompt-submit.ps1 - Windows hook: inject active plan into every prompt
param()
[Console]::OutputEncoding = [System.Text.UTF8Encoding]::new($false)
$OutputEncoding = [Console]::OutputEncoding
$ScriptDir    = Split-Path -Parent $MyInvocation.MyCommand.Path
$CodexRoot    = Split-Path -Parent $ScriptDir
$TmpDir       = Join-Path $CodexRoot ".tmp"
$RestoreFile  = Join-Path $TmpDir "intelligence_restore_pending"
$planFile     = Join-Path (Get-Location) "task_plan.md"
$progressFile = Join-Path (Get-Location) "progress.md"

if (Test-Path $RestoreFile) {
    Write-Output "[intelligence-layer] FIRST PROMPT OF SESSION — restore persistent context before proceeding:"
    Write-Output "1. Call MCP tool: mempalace_status"
    Write-Output "2. Check resource: semantic://health"
    Write-Output "3. Then continue with the active plan below."
    Write-Output ""
    Remove-Item $RestoreFile -Force -ErrorAction SilentlyContinue
}

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
