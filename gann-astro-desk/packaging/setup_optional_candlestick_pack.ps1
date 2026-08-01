param(
    [string]$SourceRoot = "D:\PycharmProjects",
    [string]$DataRoot = "D:\GannFinancialAstro\app_data",
    [string]$PackagingPython = "D:\GannFinancialAstro\packaging_env\Scripts\python.exe"
)

$ErrorActionPreference = "Stop"
$source = [IO.Path]::GetFullPath($SourceRoot)
$data = [IO.Path]::GetFullPath($DataRoot)
$registry = Join-Path $source "candlestick_agent\source_registry.csv"
$builder = Join-Path $source "candlestick_agent\build_corpus_index.py"
$model = Join-Path $source "candlestick_agent\usdjpy_shadow_model_v1.json"
$target = Join-Path $data "candlestick"

if (-not (Test-Path -LiteralPath $PackagingPython -PathType Leaf)) {
    throw "Packaging Python was not found: $PackagingPython"
}
foreach ($path in @($registry, $builder, $model)) {
    if (-not (Test-Path -LiteralPath $path -PathType Leaf)) {
        throw "Authorized local candlestick pack input is missing: $path"
    }
}

New-Item -ItemType Directory -Path $target -Force | Out-Null
$corpus = Join-Path $target "corpus_chunks.jsonl"
& $PackagingPython $builder --manifest $registry --output $corpus
if ($LASTEXITCODE -ne 0) {
    throw "Candlestick corpus build failed with exit code $LASTEXITCODE"
}
Copy-Item -LiteralPath $model -Destination (Join-Path $target "usdjpy_shadow_model_v1.json") -Force
Write-Output "Installed authorized optional candlestick pack at $target"
