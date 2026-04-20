# user-prompt-submit.ps1 - Windows compatibility shim for UserPromptSubmit.
param()
[Console]::OutputEncoding = [System.Text.UTF8Encoding]::new($false)
$OutputEncoding = [Console]::OutputEncoding
exit 0
