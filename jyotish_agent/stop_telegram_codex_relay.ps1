$ErrorActionPreference = "Continue"

$matches = Get-CimInstance Win32_Process -Filter "name='python.exe' OR name='pythonw.exe'" |
    Where-Object { $_.CommandLine -like "*telegram_codex_relay.py*" }

if (-not $matches) {
    Write-Output "No Codex Telegram relay process found."
    exit 0
}

foreach ($proc in $matches) {
    Write-Output "Stopping PID $($proc.ProcessId): $($proc.CommandLine)"
    Stop-Process -Id $proc.ProcessId -Force
}
