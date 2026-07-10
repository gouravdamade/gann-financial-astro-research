$ErrorActionPreference = "Stop"

Push-Location $PSScriptRoot
try {
    python -m unittest discover -s tests -v
    if ($LASTEXITCODE -ne 0) { throw "Unit tests failed" }

    python -m ashtakavarga_lab.cli certify
    if ($LASTEXITCODE -ne 0) { throw "Certification command failed" }

    python -m ashtakavarga_lab.cli evidence `
        --start 2010-01-27 `
        --end 2026-03-10 `
        --profiles usd_reference,jpy_reference
    if ($LASTEXITCODE -ne 0) { throw "Evidence generation failed" }

    python -m ashtakavarga_lab.cli evaluate `
        --price "D:\PycharmProjects\usd_jpy_h1_mt5_metaquotes_demo_full.parquet"
    if ($LASTEXITCODE -ne 0) { throw "Walk-forward evaluation failed" }
}
finally {
    Pop-Location
}
