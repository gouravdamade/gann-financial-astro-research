$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$RepoRoot = Split-Path -Parent $ScriptDir
$OutLog = Join-Path $ScriptDir "telegram_codex_relay_stdout.log"
$ErrLog = Join-Path $ScriptDir "telegram_codex_relay_stderr.log"

$python = "python"
$args = @(
    (Join-Path $ScriptDir "telegram_codex_relay.py"),
    "--announce-start"
)

Start-Process -FilePath $python `
    -ArgumentList $args `
    -WorkingDirectory $RepoRoot `
    -WindowStyle Hidden `
    -RedirectStandardOutput $OutLog `
    -RedirectStandardError $ErrLog

Write-Output "Started Codex Telegram relay. Logs:"
Write-Output $OutLog
Write-Output $ErrLog
