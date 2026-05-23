$ErrorActionPreference = "Continue"

$matches = Get-CimInstance Win32_Process -Filter "name='ollama.exe'" |
    Where-Object { $_.CommandLine -like "*D:\Ollama\app\ollama.exe*" }

if (-not $matches) {
    Write-Output "No portable Ollama process found."
    exit 0
}

foreach ($proc in $matches) {
    Write-Output "Stopping PID $($proc.ProcessId): $($proc.CommandLine)"
    Stop-Process -Id $proc.ProcessId -Force
}
