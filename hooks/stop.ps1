# stop.ps1 — Windows PowerShell version of stop.sh
# Called by stop.py via _run_python_fallback("stop.sh", ...)
# Also called directly by check-complete.ps1 pattern

$planFile = Join-Path (Get-Location) "task_plan.md"

if (-not (Test-Path $planFile)) {
    Write-Output "{}"
    exit 0
}

$content = Get-Content $planFile -Raw -ErrorAction SilentlyContinue
if (-not $content) {
    Write-Output "{}"
    exit 0
}

if ($content -match "ALL PHASES COMPLETE|COMPLETE.*ALL PHASES") {
    $msg = "ALL PHASES COMPLETE — plan finished."
    Write-Output (ConvertTo-Json @{ followup_message = $msg } -Compress)
} else {
    # Check if all checkboxes are ticked
    $unchecked = ($content | Select-String -Pattern "\[ \]" -AllMatches).Matches.Count
    if ($unchecked -eq 0 -and $content -match "\[x\]") {
        $msg = "ALL PHASES COMPLETE — all tasks checked off."
        Write-Output (ConvertTo-Json @{ followup_message = $msg } -Compress)
    } else {
        $msg = "Plan is still active ($unchecked unchecked items). Review task_plan.md before closing."
        Write-Output (ConvertTo-Json @{ followup_message = $msg } -Compress)
    }
}
exit 0
