param(
    [string]$JavaHome = "D:\FaceSwapServer\android-tools\jdk\jdk-17.0.19+10",
    [string]$AndroidHome = "D:\FaceSwapServer\android-tools\sdk",
    [string]$NdkVersion = "29.0.14206865"
)

$ErrorActionPreference = "Stop"
$ndkHome = Join-Path $AndroidHome "ndk\$NdkVersion"
$requiredPaths = @(
    (Join-Path $JavaHome "bin\java.exe"),
    (Join-Path $AndroidHome "platform-tools\adb.exe"),
    (Join-Path $ndkHome "ndk-build.cmd"),
    "D:\Rust\cargo\bin\cargo.exe"
)

foreach ($path in $requiredPaths) {
    if (-not (Test-Path -LiteralPath $path -PathType Leaf)) {
        throw "Required Android build tool was not found: $path"
    }
}

$env:JAVA_HOME = $JavaHome
$env:ANDROID_HOME = $AndroidHome
$env:ANDROID_SDK_ROOT = $AndroidHome
$env:NDK_HOME = $ndkHome
$env:CARGO_HOME = "D:\Rust\cargo"
$env:RUSTUP_HOME = "D:\Rust\rustup"
$env:CARGO_TARGET_DIR = "D:\Rust\targets-android"
$env:GRADLE_USER_HOME = "D:\GannFinancialAstro\android_build\gradle"
$env:TEMP = "D:\GannFinancialAstro\tmp\gann_astro_android_build"
$env:TMP = $env:TEMP
$llvmToolchain = Join-Path $ndkHome "toolchains\llvm\prebuilt\windows-x86_64\bin"
$env:CC_aarch64_linux_android = Join-Path $llvmToolchain "aarch64-linux-android24-clang.cmd"
$env:AR_aarch64_linux_android = Join-Path $llvmToolchain "llvm-ar.exe"
$env:CARGO_TARGET_AARCH64_LINUX_ANDROID_LINKER = $env:CC_aarch64_linux_android
$env:CC_armv7_linux_androideabi = Join-Path $llvmToolchain "armv7a-linux-androideabi24-clang.cmd"
$env:AR_armv7_linux_androideabi = $env:AR_aarch64_linux_android
$env:CARGO_TARGET_ARMV7_LINUX_ANDROIDEABI_LINKER = $env:CC_armv7_linux_androideabi
$env:CC_i686_linux_android = Join-Path $llvmToolchain "i686-linux-android24-clang.cmd"
$env:AR_i686_linux_android = $env:AR_aarch64_linux_android
$env:CARGO_TARGET_I686_LINUX_ANDROID_LINKER = $env:CC_i686_linux_android
$env:CC_x86_64_linux_android = Join-Path $llvmToolchain "x86_64-linux-android24-clang.cmd"
$env:AR_x86_64_linux_android = $env:AR_aarch64_linux_android
$env:CARGO_TARGET_X86_64_LINUX_ANDROID_LINKER = $env:CC_x86_64_linux_android

New-Item -ItemType Directory -Path $env:CARGO_TARGET_DIR -Force | Out-Null
New-Item -ItemType Directory -Path $env:GRADLE_USER_HOME -Force | Out-Null
New-Item -ItemType Directory -Path $env:TEMP -Force | Out-Null

$pathParts = @(
    $llvmToolchain,
    (Join-Path $JavaHome "bin"),
    (Join-Path $AndroidHome "platform-tools"),
    (Join-Path $AndroidHome "cmdline-tools\latest\bin"),
    "D:\Rust\cargo\bin"
)
$env:Path = (($pathParts + $env:Path.Split(';')) | Select-Object -Unique) -join ';'

Write-Output "Android build tools configured on D:."
Write-Output "JAVA_HOME=$env:JAVA_HOME"
Write-Output "ANDROID_HOME=$env:ANDROID_HOME"
Write-Output "NDK_HOME=$env:NDK_HOME"
Write-Output "CARGO_TARGET_DIR=$env:CARGO_TARGET_DIR"
Write-Output "GRADLE_USER_HOME=$env:GRADLE_USER_HOME"
