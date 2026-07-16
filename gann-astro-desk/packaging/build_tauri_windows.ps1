param(
    [string]$CandidateRoot = "D:\GannFinancialAstro\release_candidate\GannAstroDesk-0.10.4-tauri",
    [switch]$SkipSidecarBuild,
    [switch]$FinalizeOnly
)

$ErrorActionPreference = "Stop"
$appRoot = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot ".."))
$safeRoot = [IO.Path]::GetFullPath("D:\GannFinancialAstro")
$sidecarRoot = Join-Path $appRoot "src-tauri\resources\GannAstroBackend"
$sidecarExe = Join-Path $sidecarRoot "GannAstroBackend.exe"
$cargoTarget = "D:\Rust\targets"
$vcvars = "D:\VisualStudio\2022\BuildTools\VC\Auxiliary\Build\vcvars64.bat"

function Assert-UnderRoot([string]$Path, [string]$Root) {
    $full = [IO.Path]::GetFullPath($Path)
    $prefix = [IO.Path]::GetFullPath($Root).TrimEnd("\") + "\"
    if (-not $full.StartsWith($prefix, [StringComparison]::OrdinalIgnoreCase)) {
        throw "Refusing operation outside $Root`: $full"
    }
    return $full
}

function Import-BatchEnvironment([string]$BatchFile) {
    $lines = & cmd.exe /d /s /c "`"call `"$BatchFile`" >nul && set`""
    if ($LASTEXITCODE -ne 0) {
        throw "Unable to initialize the MSVC build environment"
    }
    foreach ($line in $lines) {
        $separator = $line.IndexOf("=")
        if ($separator -gt 0) {
            $name = $line.Substring(0, $separator)
            $value = $line.Substring($separator + 1)
            Set-Item -Path "Env:$name" -Value $value
        }
    }
}

$candidate = Assert-UnderRoot $CandidateRoot $safeRoot
if (Test-Path -LiteralPath $candidate) {
    Remove-Item -LiteralPath $candidate -Recurse -Force
}
New-Item -ItemType Directory -Path $candidate -Force | Out-Null

if (-not $FinalizeOnly) {
    if (-not $SkipSidecarBuild) {
        & (Join-Path $PSScriptRoot "build_backend_sidecar.ps1")
    }
    if (-not (Test-Path -LiteralPath $vcvars -PathType Leaf)) {
        throw "MSVC build environment was not found: $vcvars"
    }

    $env:CARGO_HOME = "D:\Rust\cargo"
    $env:RUSTUP_HOME = "D:\Rust\rustup"
    $env:CARGO_TARGET_DIR = $cargoTarget
    $env:TEMP = Join-Path $safeRoot "tmp\gann_astro_tauri_build"
    $env:TMP = $env:TEMP
    New-Item -ItemType Directory -Path $env:TEMP -Force | Out-Null
    Import-BatchEnvironment $vcvars
    $env:Path = "D:\Rust\cargo\bin;$env:Path"

    Push-Location $appRoot
    try {
        & npm.cmd run desktop:build -- --bundles nsis
        if ($LASTEXITCODE -ne 0) {
            throw "Tauri build failed with exit code $LASTEXITCODE"
        }
    } finally {
        Pop-Location
    }
}
if (-not (Test-Path -LiteralPath $sidecarExe -PathType Leaf)) {
    throw "Managed backend sidecar was not found: $sidecarExe"
}

$compiledExe = Join-Path $cargoTarget "release\gann-astro-desk.exe"
if (-not (Test-Path -LiteralPath $compiledExe -PathType Leaf)) {
    throw "Compiled Tauri executable was not created: $compiledExe"
}
$portableExe = Join-Path $candidate "GannAstroDesk.exe"
Copy-Item -LiteralPath $compiledExe -Destination $portableExe -Force
Copy-Item -LiteralPath $sidecarRoot -Destination (Join-Path $candidate "backend") -Recurse -Force

$installer = Get-ChildItem -LiteralPath (Join-Path $cargoTarget "release\bundle\nsis") `
    -Filter "*.exe" -File | Sort-Object LastWriteTime -Descending | Select-Object -First 1
if ($null -eq $installer) {
    throw "Tauri NSIS installer was not created"
}
$installerTarget = Join-Path $candidate $installer.Name
Copy-Item -LiteralPath $installer.FullName -Destination $installerTarget -Force

$releaseFiles = Get-ChildItem -LiteralPath $candidate -File -Recurse
$manifest = [ordered]@{
    product = "Gann Astro Desk"
    version = "0.10.4"
    status = "normalized_mt5_history_candidate"
    built_at_utc = [DateTime]::UtcNow.ToString("o")
    executable = "GannAstroDesk.exe"
    executable_sha256 = (Get-FileHash -LiteralPath $portableExe -Algorithm SHA256).Hash
    installer = $installer.Name
    installer_sha256 = (Get-FileHash -LiteralPath $installerTarget -Algorithm SHA256).Hash
    file_count = $releaseFiles.Count
    total_bytes = ($releaseFiles | Measure-Object -Property Length -Sum).Sum
    shell = "Tauri 2 / Rust"
    backend_contract = "GANN_ASTRO_TAURI_PYTHON_SIDECAR_V1"
    astronomy_contract = "RAMAN_SWISSEPH_SINGLE_SIDEREAL_PORPHYRY_TN_V2"
    chart_layout_contract = "GANN_CHART_LAYOUT_V1"
    drawing_contract = "GANN_RESEARCH_CHART_DRAWING_V1"
    candlestick_shadow_contract = "GANN_CANDLESTICK_APPEND_ONLY_SHADOW_LEDGER_V3"
    candlestick_trial_contract = "GANN_CANDLESTICK_FROZEN_SHADOW_TRIAL_V3"
    mt5_clock_probe_contract = "GANN_MT5_CLOCK_PROBE_V1"
    mt5_time_normalization_contract = "GANN_MT5_SERVER_TIME_NORMALIZATION_V1"
    mt5_history_snapshot_contract = "MT5_TIMESTAMP_NORMALIZED_CLOSED_BARS_V2"
    mt5_execution_mode = "read_only_market_data"
}
$manifest | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $candidate "release.manifest.json") -Encoding utf8

Write-Output $portableExe
Write-Output $installerTarget
