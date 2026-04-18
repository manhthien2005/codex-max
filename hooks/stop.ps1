# stop.ps1 — Windows PowerShell version of stop.sh
# Two-gate logic:
#   Gate 1: MemPalace diary sentinel must be cleared (diary written this session)
#   Gate 2: task_plan.md must be complete (existing planning-with-files logic)

$CodexRoot  = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$TmpDir     = Join-Path $CodexRoot ".tmp"
$SentinelFile = Join-Path $TmpDir "diary_pending"
$PlanFile   = Join-Path (Get-Location) "task_plan.md"

# ── Gate 1: MemPalace diary ──────────────────────────────────────────────────
if (Test-Path $SentinelFile) {
    $ts = Get-Content $SentinelFile -Raw -ErrorAction SilentlyContinue
    $ts = if ($ts) { $ts.Trim() } else { "unknown time" }
    $msg = @"
⚠️  MANDATORY BEFORE STOP — MemPalace Session Diary

Session started at: $ts
The diary sentinel is still active. You MUST complete these steps:

1. Call the MCP tool: mempalace_diary_write
   - wing: "context"
   - room: "session_<YYYY-MM-DD>"
   - content: Summary of what was done, decisions made, issues found, next steps.

2. After the tool call succeeds, delete the sentinel to unlock stop:
   Remove-Item "$SentinelFile" -Force

Do NOT skip this. MemPalace persistence depends on this diary entry.
"@
    Write-Output (ConvertTo-Json @{ followup_message = $msg } -Compress)
    exit 0
}

# ── Gate 2: planning-with-files plan state ───────────────────────────────────
if (-not (Test-Path $PlanFile)) {
    Write-Output "{}"
    exit 0
}

$content = Get-Content $PlanFile -Raw -ErrorAction SilentlyContinue
if (-not $content) {
    Write-Output "{}"
    exit 0
}

if ($content -match "ALL PHASES COMPLETE|COMPLETE.*ALL PHASES") {
    $msg = "ALL PHASES COMPLETE — plan finished."
    Write-Output (ConvertTo-Json @{ followup_message = $msg } -Compress)
} else {
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
