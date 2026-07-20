param(
    [string]$CandidateRoot = "",
    [switch]$SkipInit
)

$ErrorActionPreference = "Stop"
$appRoot = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot ".."))
$projectRoot = [IO.Path]::GetFullPath((Join-Path $appRoot ".."))
$safeRoot = [IO.Path]::GetFullPath("D:\GannFinancialAstro")
$tauriConfig = Get-Content -LiteralPath (Join-Path $appRoot "src-tauri\tauri.conf.json") -Raw |
    ConvertFrom-Json
$appVersion = [string]$tauriConfig.version

function Assert-UnderRoot([string]$Path, [string]$Root) {
    $full = [IO.Path]::GetFullPath($Path)
    $prefix = [IO.Path]::GetFullPath($Root).TrimEnd("\") + "\"
    if (-not $full.StartsWith($prefix, [StringComparison]::OrdinalIgnoreCase)) {
        throw "Refusing operation outside $Root`: $full"
    }
    return $full
}

if (-not $CandidateRoot) {
    $CandidateRoot = Join-Path $safeRoot "mobile\release_candidate\GannAstroMobile-$appVersion-debug"
}
$candidate = Assert-UnderRoot $CandidateRoot $safeRoot

. (Join-Path $appRoot "tools\use_d_android_tools.ps1")

$androidProject = Join-Path $appRoot "src-tauri\gen\android"
if (-not $SkipInit -and -not (Test-Path -LiteralPath $androidProject -PathType Container)) {
    Push-Location $appRoot
    try {
        & npm.cmd run mobile:init
        if ($LASTEXITCODE -ne 0) {
            throw "Tauri Android initialization failed with exit code $LASTEXITCODE"
        }
    } finally {
        Pop-Location
    }
}
if (-not (Test-Path -LiteralPath $androidProject -PathType Container)) {
    throw "Generated Android wrapper was not found: $androidProject"
}

$androidConfig = Get-Content -LiteralPath (Join-Path $appRoot "src-tauri\tauri.android.conf.json") -Raw |
    ConvertFrom-Json
$mobileProductName = [string]$androidConfig.productName
$androidStringsPath = Join-Path $androidProject "app\src\main\res\values\strings.xml"
if ($mobileProductName -and (Test-Path -LiteralPath $androidStringsPath -PathType Leaf)) {
    [xml]$androidStrings = Get-Content -LiteralPath $androidStringsPath -Raw
    foreach ($node in $androidStrings.resources.string) {
        if ($node.name -in @("app_name", "main_activity_title")) {
            $node.InnerText = $mobileProductName
        }
    }
    $xmlSettings = [System.Xml.XmlWriterSettings]::new()
    $xmlSettings.Indent = $true
    $xmlSettings.OmitXmlDeclaration = $true
    $xmlWriter = [System.Xml.XmlWriter]::Create($androidStringsPath, $xmlSettings)
    try {
        $androidStrings.Save($xmlWriter)
    } finally {
        $xmlWriter.Dispose()
    }
}

Push-Location $appRoot
try {
    $rustLibrary = Join-Path $env:CARGO_TARGET_DIR `
        "aarch64-linux-android\debug\libgann_astro_desk_lib.so"
    if (Test-Path -LiteralPath $rustLibrary -PathType Leaf) {
        Remove-Item -LiteralPath $rustLibrary -Force
    }
    $previousErrorAction = $ErrorActionPreference
    $ErrorActionPreference = "Continue"
    try {
        & npm.cmd run mobile:build:debug 2>&1 | Tee-Object -Variable capturedTauriOutput | Out-Host
        $tauriExitCode = $LASTEXITCODE
    } finally {
        $ErrorActionPreference = $previousErrorAction
    }
    if ($tauriExitCode -ne 0) {
        $tauriText = ($capturedTauriOutput | Out-String)
        $symlinkBlocked = $tauriText.Contains("Creation symbolic link is not allowed for this system")
        if (-not $symlinkBlocked -or -not (Test-Path -LiteralPath $rustLibrary -PathType Leaf)) {
            throw "Tauri Android build failed with exit code $tauriExitCode"
        }

        Write-Warning "Windows symlink creation is disabled; using the verified copy-based Gradle fallback."
        $jniDirectory = Join-Path $androidProject "app\src\main\jniLibs\arm64-v8a"
        New-Item -ItemType Directory -Path $jniDirectory -Force | Out-Null
        $jniLibrary = Join-Path $jniDirectory "libgann_astro_desk_lib.so"
        Copy-Item -LiteralPath $rustLibrary -Destination $jniLibrary -Force
        $llvmStrip = Join-Path $env:NDK_HOME `
            "toolchains\llvm\prebuilt\windows-x86_64\bin\llvm-strip.exe"
        if (-not (Test-Path -LiteralPath $llvmStrip -PathType Leaf)) {
            throw "NDK llvm-strip was not found: $llvmStrip"
        }
        & $llvmStrip --strip-debug $jniLibrary
        if ($LASTEXITCODE -ne 0) {
            throw "Unable to strip debug symbols from the staged Android library"
        }
        $existingApks = Get-ChildItem -LiteralPath (Join-Path $androidProject "app\build\outputs\apk") `
            -Filter "*.apk" -File -Recurse -ErrorAction SilentlyContinue
        foreach ($existingApk in $existingApks) {
            Remove-Item -LiteralPath $existingApk.FullName -Force
        }

        Push-Location $androidProject
        try {
            & .\gradlew.bat :app:clean --no-daemon
            if ($LASTEXITCODE -ne 0) {
                throw "Unable to clean the staged Android package"
            }
            & .\gradlew.bat :app:assembleArm64Debug -x :app:rustBuildArm64Debug --no-daemon
            if ($LASTEXITCODE -ne 0) {
                throw "Copy-based Gradle fallback failed with exit code $LASTEXITCODE"
            }
        } finally {
            Pop-Location
        }
    }
} finally {
    Pop-Location
}

$apk = Get-ChildItem -LiteralPath (Join-Path $androidProject "app\build\outputs\apk") `
    -Filter "*.apk" -File -Recurse |
    Sort-Object LastWriteTime -Descending |
    Select-Object -First 1
if ($null -eq $apk) {
    throw "Android APK was not created under the generated Gradle output directory"
}

if (Test-Path -LiteralPath $candidate) {
    Remove-Item -LiteralPath $candidate -Recurse -Force
}
New-Item -ItemType Directory -Path $candidate -Force | Out-Null
$apkTarget = Join-Path $candidate "GannAstroMobile-$appVersion-debug.apk"
Copy-Item -LiteralPath $apk.FullName -Destination $apkTarget -Force

$manifest = [ordered]@{
    product = "Gann Astro Mobile"
    version = $appVersion
    status = "android_companion_pairing_shell"
    built_at_utc = [DateTime]::UtcNow.ToString("o")
    apk = [IO.Path]::GetFileName($apkTarget)
    apk_sha256 = (Get-FileHash -LiteralPath $apkTarget -Algorithm SHA256).Hash
    source_git_commit = (& git.exe -C $projectRoot rev-parse HEAD).Trim()
    source_git_dirty = [bool](& git.exe -C $projectRoot status --porcelain -- "gann-astro-desk" | Select-Object -First 1)
    runtime_profile_contract = "GANN_ASTRO_RUNTIME_PROFILE_V1"
    companion_client_contract = "GANN_ASTRO_ANDROID_COMPANION_CLIENT_V1"
    companion_session_contract = "GANN_ASTRO_COMPANION_SESSION_V1"
    companion_capabilities_contract = "GANN_ASTRO_COMPANION_CAPABILITIES_V1"
    session_persistence = "memory_only"
    gateway_status = "not_yet_implemented"
    execution_allowed = $false
}
$manifest | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $candidate "release.manifest.json") -Encoding utf8

Write-Output $apkTarget
Write-Output (Join-Path $candidate "release.manifest.json")
