# session-start.ps1 — Windows PowerShell version of session-start.sh
$ScriptDir  = Split-Path -Parent $MyInvocation.MyCommand.Path
$CodexRoot  = Split-Path -Parent $ScriptDir
$SkillDir   = Join-Path $CodexRoot "skills\planning-with-files"
$PythonBin  = (Get-Command python -ErrorAction SilentlyContinue).Source

# Run session-catchup.py if available
$catchupScript = Join-Path $SkillDir "scripts\session-catchup.py"
if ($PythonBin -and (Test-Path $catchupScript)) {
    & $PythonBin $catchupScript (Get-Location).Path 2>$null
}

# Also run user-prompt-submit equivalent
$promptScript = Join-Path $ScriptDir "user-prompt-submit.ps1"
if (Test-Path $promptScript) {
    & powershell.exe -NoProfile -ExecutionPolicy Bypass -File $promptScript
}
exit 0
