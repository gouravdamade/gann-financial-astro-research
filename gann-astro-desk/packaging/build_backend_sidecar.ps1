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

& $PackagingPython -c "import cryptography; from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey"
if ($LASTEXITCODE -ne 0) {
    throw "Packaging Python is missing the pinned cryptography dependency from requirements.txt"
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
$requiredProfileFiles = @(
    (Join-Path $resourceRoot "_internal\profiles\target_aware_polarity_catalogue_v1.json"),
    (Join-Path $resourceRoot "_internal\profiles\target_aware_polarity_evidence_packets_v1.json"),
    (Join-Path $resourceRoot "_internal\profiles\founder_chart_hypotheses_v1.json")
)
$missingProfileFiles = @(
    $requiredProfileFiles | Where-Object { -not (Test-Path -LiteralPath $_ -PathType Leaf) }
)
if ($missingProfileFiles.Count -gt 0) {
    throw "Backend sidecar is missing chart-conditioned profile resources:`n$($missingProfileFiles -join "`n")"
}
$requiredBphsFixture = Join-Path $resourceRoot "_internal\research_labs\bphs_1899_classical_timing\bphs_1899_packet_1w_muhurta_fixture.json"
if (-not (Test-Path -LiteralPath $requiredBphsFixture -PathType Leaf)) {
    throw "Backend sidecar is missing the BPHS Packet 1W Muhurta fixture: $requiredBphsFixture"
}
$requiredCgvoFixtures = @(
    (Join-Path $resourceRoot "_internal\configs\research\cgvo\varahamihira_eclipse_source_profile_v1.json"),
    (Join-Path $resourceRoot "_internal\configs\research\cgvo\trailokya_geography_argha_context_v1.json"),
    (Join-Path $resourceRoot "_internal\configs\research\cgvo\kurma_gazetteer_seed_v1.json"),
    (Join-Path $resourceRoot "_internal\configs\research\cgvo\VARAHAMIHIRA_ASTRONOMICAL_FRAME_V1.yaml"),
    (Join-Path $resourceRoot "_internal\configs\research\cgvo\VARAHAMIHIRA_LUNAR_MONTH_PROFILE_V1.yaml"),
    (Join-Path $resourceRoot "_internal\configs\research\cgvo\VARAHAMIHIRA_ECLIPSE_ASPECT_PROFILE_V1.yaml"),
    (Join-Path $resourceRoot "_internal\configs\research\cgvo\VARAHAMIHIRA_FIRMAMENT_GEOMETRY_V1.yaml"),
    (Join-Path $resourceRoot "_internal\configs\research\cgvo\CGVO_S1_READINESS_MATRIX_V1.yaml")
)
$missingCgvoFixtures = @(
    $requiredCgvoFixtures | Where-Object { -not (Test-Path -LiteralPath $_ -PathType Leaf) }
)
if ($missingCgvoFixtures.Count -gt 0) {
    throw "Backend sidecar is missing CGVO source fixtures:`n$($missingCgvoFixtures -join "`n")"
}
$requiredXe1Fixtures = @(
    (Join-Path $resourceRoot "_internal\research_labs\experimental_evidence\fixtures\xe1_evidence_observations_v1.json"),
    (Join-Path $resourceRoot "_internal\research_labs\experimental_evidence\fixtures\xe1_trial_ledger_v1.json")
)
$missingXe1Fixtures = @(
    $requiredXe1Fixtures | Where-Object { -not (Test-Path -LiteralPath $_ -PathType Leaf) }
)
if ($missingXe1Fixtures.Count -gt 0) {
    throw "Backend sidecar is missing XE1 experimental evidence fixtures:`n$($missingXe1Fixtures -join "`n")"
}
$requiredXe3Fixtures = @(
    (Join-Path $resourceRoot "_internal\research_labs\chart_conditioned_aspects\founder_review\USD_APRIL_2025_BLANK_POLARITY_REVIEW_V1.json"),
    (Join-Path $resourceRoot "_internal\research_labs\chart_conditioned_aspects\founder_review\USD_APRIL_2025_BLANK_POLARITY_REVIEW_V1.identity_integrity.manifest.json"),
    (Join-Path $resourceRoot "_internal\research_labs\chart_conditioned_aspects\founder_review\JPY_APRIL_2025_BLANK_POLARITY_REVIEW_V1.json"),
    (Join-Path $resourceRoot "_internal\research_labs\chart_conditioned_aspects\founder_review\JPY_APRIL_2025_BLANK_POLARITY_REVIEW_V1.identity_integrity.manifest.json"),
    (Join-Path $resourceRoot "_internal\status\audits\pfr_v2b_r5_f2a_r1_event_identity_integrity.json"),
    (Join-Path $resourceRoot "_internal\research_labs\experimental_evidence\fixtures\xe3_preregistration_contract_v1.json")
)
$missingXe3Fixtures = @(
    $requiredXe3Fixtures | Where-Object { -not (Test-Path -LiteralPath $_ -PathType Leaf) }
)
if ($missingXe3Fixtures.Count -gt 0) {
    throw "Backend sidecar is missing XE3 immutable review resources:`n$($missingXe3Fixtures -join "`n")"
}
$gitkeep = Join-Path $resourceRoot ".gitkeep"
if (-not (Test-Path -LiteralPath $gitkeep -PathType Leaf)) {
    Set-Content -LiteralPath $gitkeep `
        -Value "# Packaged backend output is generated into this directory." `
        -Encoding ascii
}

Write-Output $sidecarExe
