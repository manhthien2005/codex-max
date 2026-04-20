# launch-codex-rtk.ps1 — Windows bridge into the WSL-native Codex + RTK launcher
param(
    [string]$Distro = "Ubuntu",
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$CodexArgs
)

$ErrorActionPreference = "Stop"
$WslLauncher = "~/.codex/scripts/launch-codex-rtk.sh"
$BashSingleQuoteEscape = '''"''"'''

$QuotedArgs = @()
foreach ($arg in $CodexArgs) {
    $QuotedArgs += "'" + ($arg -replace "'", $BashSingleQuoteEscape) + "'"
}
$ArgString = ($QuotedArgs -join ' ').Trim()
$Command = if ($ArgString) { "bash '$WslLauncher' $ArgString" } else { "bash '$WslLauncher'" }

wsl.exe -d $Distro -- bash -lc $Command
exit $LASTEXITCODE
