$ErrorActionPreference = "Stop"

$env:OLLAMA_MODELS = "D:\Ollama\models"
$existing = Get-CimInstance Win32_Process -Filter "name='ollama.exe'" |
    Where-Object { $_.CommandLine -like "*D:\Ollama\app\ollama.exe*serve*" }

if ($existing) {
    Write-Output "Ollama portable already running:"
    $existing | Select-Object ProcessId, CommandLine | Format-List
    exit 0
}

Start-Process -FilePath "D:\Ollama\app\ollama.exe" `
    -ArgumentList "serve" `
    -WorkingDirectory "D:\Ollama\app" `
    -WindowStyle Hidden `
    -RedirectStandardOutput "D:\Ollama\ollama_stdout.log" `
    -RedirectStandardError "D:\Ollama\ollama_stderr.log"

Start-Sleep -Seconds 4
Invoke-RestMethod -Uri "http://127.0.0.1:11434/api/tags" -Method Get | ConvertTo-Json -Depth 5
