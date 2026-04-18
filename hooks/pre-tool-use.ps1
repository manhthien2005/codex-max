# pre-tool-use.ps1 - Windows hook: inject plan context before tool use
param()
$planFile = Join-Path (Get-Location) "task_plan.md"

if (Test-Path $planFile) {
    # Output plan to stderr so Codex adapter surfaces it as systemMessage
    $lines = Get-Content $planFile | Select-Object -First 30
    $lines | ForEach-Object { [Console]::Error.WriteLine($_) }
}

# Always allow tool use
Write-Output '{"decision": "allow"}'
exit 0
