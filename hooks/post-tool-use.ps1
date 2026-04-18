# post-tool-use.ps1 — Windows PowerShell version of post-tool-use.sh
$planFile = Join-Path (Get-Location) "task_plan.md"

if (Test-Path $planFile) {
    Write-Output "[planning-with-files] Update progress.md with what you just did. If a phase is now complete, update task_plan.md status."
}
exit 0
