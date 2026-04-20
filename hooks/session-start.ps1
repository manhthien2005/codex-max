# session-start.ps1 — Windows PowerShell version of session-start.sh
[Console]::OutputEncoding = [System.Text.UTF8Encoding]::new($false)
$OutputEncoding = [Console]::OutputEncoding
$ScriptDir  = Split-Path -Parent $MyInvocation.MyCommand.Path
$CodexRoot  = Split-Path -Parent $ScriptDir
$SkillDir   = Join-Path $CodexRoot "skills\planning-with-files"
$TmpDir     = Join-Path $CodexRoot ".tmp"
$PythonBin  = (Get-Command python -ErrorAction SilentlyContinue).Source

# ── MemPalace diary sentinel ─────────────────────────────────────────────────
# Create a sentinel file so stop.ps1 knows a diary entry is required this session.
if (-not (Test-Path $TmpDir)) {
    New-Item -ItemType Directory -Path $TmpDir -Force | Out-Null
}
$SentinelFile = Join-Path $TmpDir "diary_pending"
$RestoreSentinelFile = Join-Path $TmpDir "intelligence_restore_pending"
$Timestamp = (Get-Date -Format "yyyy-MM-dd HH:mm:ss zzz")
Set-Content -Path $SentinelFile -Value $Timestamp -Encoding UTF8
Set-Content -Path $RestoreSentinelFile -Value $Timestamp -Encoding UTF8
# ─────────────────────────────────────────────────────────────────────────────

# Run session-catchup.py if available
$catchupScript = Join-Path $SkillDir "scripts\session-catchup.py"
if ($PythonBin -and (Test-Path $catchupScript)) {
    & $PythonBin $catchupScript (Get-Location).Path 2>$null
}

# Do not invoke user-prompt-submit here.
# UserPromptSubmit is a separate lifecycle hook and should own prompt injection.
exit 0
