param(
    [string]$PackagingPython = "D:\GannFinancialAstro\packaging_env\Scripts\python.exe"
)

$ErrorActionPreference = "Stop"
$appRoot = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot ".."))
$projectRoot = [IO.Path]::GetFullPath((Join-Path $appRoot ".."))
$safeBuildRoot = [IO.Path]::GetFullPath("D:\GannFinancialAstro")
$pyinstallerWork = Join-Path $safeBuildRoot "tauri_sidecar_build"
$tempRoot = Join-Path $safeBuildRoot "tmp\gann_astro_tauri_sidecar"
$resourceRoot = [IO.Path]::GetFullPath((Join-Path $appRoot "src-tauri\resources\GannAstroBackend"))

function Remove-VerifiedDirectory([string]$Path, [string]$AllowedRoot) {
    $full = [IO.Path]::GetFullPath($Path)
    $root = [IO.Path]::GetFullPath($AllowedRoot).TrimEnd("\") + "\"
    if (-not $full.StartsWith($root, [StringComparison]::OrdinalIgnoreCase)) {
        throw "Refusing cleanup outside $AllowedRoot`: $full"
    }
    if (Test-Path -LiteralPath $full) {
        Remove-Item -LiteralPath $full -Recurse -Force
    }
}

if (-not (Test-Path -LiteralPath $PackagingPython -PathType Leaf)) {
    throw "Packaging Python was not found: $PackagingPython"
}

Remove-VerifiedDirectory $pyinstallerWork $safeBuildRoot
Remove-VerifiedDirectory $resourceRoot $appRoot
New-Item -ItemType Directory -Path $pyinstallerWork,$tempRoot,$resourceRoot -Force | Out-Null

$env:TEMP = $tempRoot
$env:TMP = $tempRoot
$env:PIP_CACHE_DIR = Join-Path $safeBuildRoot "pip_cache"
$env:PYINSTALLER_CONFIG_DIR = Join-Path $safeBuildRoot "pyinstaller_config"
$env:PYTHONPYCACHEPREFIX = Join-Path $safeBuildRoot "pycache"

Push-Location $appRoot
try {
    & $PackagingPython (Join-Path $projectRoot "candlestick_agent\build_corpus_index.py")
    if ($LASTEXITCODE -ne 0) {
        throw "Candlestick corpus build failed with exit code $LASTEXITCODE"
    }
    & $PackagingPython -m PyInstaller `
        --noconfirm `
        --clean `
        --workpath $pyinstallerWork `
        --distpath (Split-Path -Parent $resourceRoot) `
        (Join-Path $PSScriptRoot "gann_backend_sidecar.spec")
    if ($LASTEXITCODE -ne 0) {
        throw "Backend sidecar PyInstaller build failed with exit code $LASTEXITCODE"
    }
} finally {
    Pop-Location
}

$sidecarExe = Join-Path $resourceRoot "GannAstroBackend.exe"
if (-not (Test-Path -LiteralPath $sidecarExe -PathType Leaf)) {
    throw "Backend sidecar executable was not created: $sidecarExe"
}
$gitkeep = Join-Path $resourceRoot ".gitkeep"
if (-not (Test-Path -LiteralPath $gitkeep -PathType Leaf)) {
    Set-Content -LiteralPath $gitkeep `
        -Value "# Packaged backend output is generated into this directory." `
        -Encoding ascii
}

Write-Output $sidecarExe
