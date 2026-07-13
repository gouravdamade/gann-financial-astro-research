param(
    [string]$PackagingPython = "D:\GannFinancialAstro\packaging_env\Scripts\python.exe",
    [string]$ReleaseRoot = "D:\GannFinancialAstro\release"
)

$ErrorActionPreference = "Stop"
$appRoot = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot ".."))
$safeRoot = [IO.Path]::GetFullPath("D:\GannFinancialAstro")
$buildRoot = Join-Path $safeRoot "pyinstaller_build"
$tempRoot = Join-Path $safeRoot "tmp\gann_astro_desk_build"
$releaseFolder = Join-Path $ReleaseRoot "GannAstroDesk"

function Assert-SafeBuildPath([string]$Path) {
    $full = [IO.Path]::GetFullPath($Path)
    $prefix = $safeRoot.TrimEnd("\") + "\"
    if (-not $full.StartsWith($prefix, [StringComparison]::OrdinalIgnoreCase)) {
        throw "Refusing build cleanup outside $safeRoot`: $full"
    }
    return $full
}

function Remove-SafeBuildDirectory([string]$Path) {
    $full = Assert-SafeBuildPath $Path
    if (Test-Path -LiteralPath $full) {
        Remove-Item -LiteralPath $full -Recurse -Force
    }
}

if (-not (Test-Path -LiteralPath $PackagingPython -PathType Leaf)) {
    throw "Packaging Python was not found: $PackagingPython"
}

Remove-SafeBuildDirectory $buildRoot
Remove-SafeBuildDirectory $releaseFolder
New-Item -ItemType Directory -Path $buildRoot,$tempRoot,$ReleaseRoot -Force | Out-Null

$env:TEMP = $tempRoot
$env:TMP = $tempRoot
$env:PIP_CACHE_DIR = Join-Path $safeRoot "pip_cache"
$env:PYINSTALLER_CONFIG_DIR = Join-Path $safeRoot "pyinstaller_config"
$env:PYTHONPYCACHEPREFIX = Join-Path $safeRoot "pycache"

Push-Location $appRoot
try {
    & npm.cmd run build
    if ($LASTEXITCODE -ne 0) {
        throw "Frontend build failed with exit code $LASTEXITCODE"
    }

    & $PackagingPython -m PyInstaller `
        --noconfirm `
        --clean `
        --workpath $buildRoot `
        --distpath $ReleaseRoot `
        (Join-Path $PSScriptRoot "gann_astro_desk.spec")
    if ($LASTEXITCODE -ne 0) {
        throw "PyInstaller failed with exit code $LASTEXITCODE"
    }
} finally {
    Pop-Location
}

$exe = Join-Path $releaseFolder "GannAstroDesk.exe"
if (-not (Test-Path -LiteralPath $exe -PathType Leaf)) {
    throw "Desktop executable was not created: $exe"
}

$releaseFiles = Get-ChildItem -LiteralPath $releaseFolder -File -Recurse
$manifest = [ordered]@{
    product = "Gann Astro Desk"
    version = "0.6.1"
    built_at_utc = [DateTime]::UtcNow.ToString("o")
    executable = "GannAstroDesk.exe"
    executable_sha256 = (Get-FileHash -LiteralPath $exe -Algorithm SHA256).Hash
    file_count = $releaseFiles.Count
    total_bytes = ($releaseFiles | Measure-Object -Property Length -Sum).Sum
    astronomy_contract = "RAMAN_SWISSEPH_SINGLE_SIDEREAL_PORPHYRY_TN_V2"
    mt5_execution_mode = "read_only_market_data"
}
$manifest | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $releaseFolder "release.manifest.json") -Encoding utf8

Write-Output $exe
