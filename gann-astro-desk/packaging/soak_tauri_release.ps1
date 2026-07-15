param(
    [string]$CandidateRoot = "D:\GannFinancialAstro\release_candidate\GannAstroDesk-0.10.0-tauri",
    [int]$DurationSeconds = 20,
    [switch]$SkipCrashRecovery
)

$ErrorActionPreference = "Stop"
$safeRoot = [IO.Path]::GetFullPath("D:\GannFinancialAstro")
$candidate = [IO.Path]::GetFullPath($CandidateRoot)
$prefix = $safeRoot.TrimEnd("\") + "\"
if (-not $candidate.StartsWith($prefix, [StringComparison]::OrdinalIgnoreCase)) {
    throw "Candidate must remain below $safeRoot"
}
$executable = Join-Path $candidate "GannAstroDesk.exe"
if (-not (Test-Path -LiteralPath $executable -PathType Leaf)) {
    throw "Candidate executable was not found: $executable"
}

$session = [DateTime]::UtcNow.ToString("yyyyMMdd_HHmmss")
$dataRoot = Join-Path $safeRoot "soak\tauri_0.10.0_$session"
$logsRoot = Join-Path $dataRoot "logs"
New-Item -ItemType Directory -Path $logsRoot -Force | Out-Null
$reportPath = Join-Path $logsRoot "native_soak_report.json"
$phasePath = Join-Path $logsRoot "native_soak_phases.jsonl"
$previousDataRoot = $env:GANN_ASTRO_DESKTOP_DATA
$app = $null
$report = [ordered]@{
    contract = "GANN_TAURI_NATIVE_SOAK_V1"
    started_at_utc = [DateTime]::UtcNow.ToString("o")
    candidate = $candidate
    data_root = $dataRoot
    crash_recovery_requested = -not $SkipCrashRecovery
    checks = [ordered]@{}
    errors = @()
    execution_allowed = $false
}

function Write-SoakPhase([string]$Phase, [object]$Details = $null) {
    $entry = [ordered]@{
        at_utc = [DateTime]::UtcNow.ToString("o")
        phase = $Phase
        details = if ($null -eq $Details) { [ordered]@{} } else { $Details }
    }
    $entry | ConvertTo-Json -Depth 8 -Compress |
        Add-Content -LiteralPath $phasePath -Encoding utf8
}

function Get-ChildProcess([int]$ParentId, [string]$Name = "") {
    $rows = Get-CimInstance Win32_Process -Filter "ParentProcessId = $ParentId" `
        -OperationTimeoutSec 5
    if ($Name) { $rows = $rows | Where-Object { $_.Name -eq $Name } }
    return @($rows)
}

function Get-DescendantIds([int]$ParentId) {
    $pending = [Collections.Generic.Queue[int]]::new()
    $pending.Enqueue($ParentId)
    $ids = [Collections.Generic.List[int]]::new()
    while ($pending.Count -gt 0) {
        $current = $pending.Dequeue()
        foreach ($child in Get-ChildProcess $current) {
            $childId = [int]$child.ProcessId
            if (-not $ids.Contains($childId)) {
                $ids.Add($childId)
                $pending.Enqueue($childId)
            }
        }
    }
    return @($ids)
}

function Wait-ForSidecar([int]$AppPid, [int]$ExcludePid = 0, [int]$TimeoutSeconds = 90) {
    $deadline = (Get-Date).AddSeconds($TimeoutSeconds)
    while ((Get-Date) -lt $deadline) {
        $candidateSidecar = Get-ChildProcess $AppPid "GannAstroBackend.exe" |
            Where-Object { [int]$_.ProcessId -ne $ExcludePid } |
            Select-Object -First 1
        if ($candidateSidecar -and $candidateSidecar.CommandLine -match "--port\s+(\d+)") {
            $port = [int]$Matches[1]
            try {
                $health = Invoke-RestMethod -Uri ("http://127.0.0.1:{0}/api/health" -f $port) -TimeoutSec 3
                if ($health.ok) {
                    return [pscustomobject]@{
                        Process = $candidateSidecar
                        Port = $port
                        Health = $health
                    }
                }
            } catch {}
        }
        Start-Sleep -Seconds 1
    }
    throw "Managed sidecar did not become healthy within $TimeoutSeconds seconds"
}

function Invoke-JsonPost([string]$Uri, [object]$Body) {
    return Invoke-RestMethod -Uri $Uri -Method Post -ContentType "application/json" `
        -Body ($Body | ConvertTo-Json -Depth 12) -TimeoutSec 10
}

try {
    Write-SoakPhase "app_launching"
    $env:GANN_ASTRO_DESKTOP_DATA = $dataRoot
    $app = Start-Process -FilePath $executable -PassThru
    Write-SoakPhase "app_started" ([ordered]@{ app_pid = $app.Id })
    $initial = Wait-ForSidecar $app.Id
    Write-SoakPhase "initial_sidecar_ready" ([ordered]@{
        sidecar_pid = [int]$initial.Process.ProcessId
        port = $initial.Port
    })
    $report.initial_app_pid = $app.Id
    $report.initial_sidecar_pid = [int]$initial.Process.ProcessId
    $report.initial_port = $initial.Port
    $report.checks.initial_health = [bool]$initial.Health.ok
    $report.checks.mt5_trade_allowed_false = $initial.Health.mt5.tradeAllowed -eq $false
    $candleHealth = Invoke-RestMethod -Uri `
        ("http://127.0.0.1:{0}/api/local-candlestick/health" -f $initial.Port) -TimeoutSec 10
    $chart = Invoke-RestMethod -Uri `
        ("http://127.0.0.1:{0}/api/chart" -f $initial.Port) -TimeoutSec 20
    $candleEventId = [string]($chart.chart.aspects | Select-Object -First 1).eventId
    if (-not $candleEventId) {
        $artifactStart = [string]$chart.chart.artifact.dateStart
        $artifactEnd = [string]$chart.chart.artifact.dateEnd
        if ($artifactStart -and $artifactEnd) {
            $historyUri = "http://127.0.0.1:{0}/api/chart?start={1}&end={2}" -f `
                $initial.Port,
                [Uri]::EscapeDataString($artifactStart),
                [Uri]::EscapeDataString($artifactEnd)
            $chart = Invoke-RestMethod -Uri $historyUri -TimeoutSec 40
            $candleEventId = [string]($chart.chart.aspects | Select-Object -First 1).eventId
        }
    }
    if (-not $candleEventId) {
        throw "Packaged chart did not expose an event for candlestick evidence QA"
    }
    $candleEvidence = Invoke-JsonPost `
        ("http://127.0.0.1:{0}/api/local-candlestick/evidence" -f $initial.Port) `
        ([ordered]@{ eventId = $candleEventId })
    $report.candlestick_event_id = $candleEventId
    $report.checks.candlestick_health_contract = `
        $candleHealth.localCandlestick.contract -eq "GANN_LOCAL_CANDLE_RAG_DRAFT_V1"
    $report.checks.candlestick_corpus_ready = `
        $candleHealth.localCandlestick.corpusReady -eq $true
    $report.checks.candlestick_evidence_contract = `
        $candleEvidence.evidence.contract -eq "GANN_CANDLESTICK_EVIDENCE_V1"
    $report.checks.candlestick_closed_bars_only = `
        $candleEvidence.evidence.guardrails.closedBarsOnlyAtCutoff -eq $true
    $report.checks.candlestick_inference_locked = (
        $candleEvidence.evidence.guardrails.consumedByLiveInference -eq $false -and
        $candleEvidence.evidence.guardrails.consumedByShadowLedger -eq $false -and
        $candleEvidence.evidence.guardrails.executionAllowed -eq $false
    )
    Write-SoakPhase "candlestick_specialist_verified" ([ordered]@{
        event_id = $candleEventId
        corpus_chunks = $candleHealth.localCandlestick.corpusChunks
    })

    $layoutPayload = [ordered]@{
        expectedRevision = 0
        name = "Native soak $session"
        workspaceKind = "main"
        symbol = "USDJPY"
        timeframe = "H1"
        familyKey = ""
        isDefault = $false
        autosave = $true
        chartState = [ordered]@{
            showAspects = $true
            showSrLines = $true
            viewport = $null
        }
        drawings = @()
    }
    $layoutResponse = Invoke-JsonPost `
        ("http://127.0.0.1:{0}/api/chart-layouts" -f $initial.Port) $layoutPayload
    $layoutId = [string]$layoutResponse.layout.layoutId
    $report.layout_id = $layoutId
    $report.checks.layout_created = [bool]$layoutResponse.ok
    Write-SoakPhase "layout_created" ([ordered]@{ layout_id = $layoutId })

    $oldSidecarPid = [int]$initial.Process.ProcessId
    if (-not $SkipCrashRecovery) {
        Write-SoakPhase "sidecar_crash_injected" ([ordered]@{ sidecar_pid = $oldSidecarPid })
        Stop-Process -Id $oldSidecarPid -Force
        $recovered = Wait-ForSidecar $app.Id $oldSidecarPid
        $report.recovered_sidecar_pid = [int]$recovered.Process.ProcessId
        $report.recovered_port = $recovered.Port
        $report.checks.sidecar_pid_changed = $report.recovered_sidecar_pid -ne $oldSidecarPid
        $report.checks.same_port_recovery = $recovered.Port -eq $initial.Port
        $report.checks.recovered_health = [bool]$recovered.Health.ok
        $active = $recovered
        Write-SoakPhase "sidecar_recovered" ([ordered]@{
            sidecar_pid = [int]$recovered.Process.ProcessId
            port = $recovered.Port
        })
    } else {
        $active = $initial
    }

    $layoutAfter = Invoke-RestMethod -Uri `
        ("http://127.0.0.1:{0}/api/chart-layouts/{1}" -f $active.Port, $layoutId) -TimeoutSec 10
    $report.checks.layout_survived_recovery = (
        $layoutAfter.ok -and
        $layoutAfter.layout.name -eq $layoutPayload.name -and
        $layoutAfter.layout.revision -eq 1
    )
    Write-SoakPhase "layout_verified"
    $refresh = Invoke-RestMethod -Uri `
        ("http://127.0.0.1:{0}/api/prospective-refresh" -f $active.Port) -TimeoutSec 10
    $diagnostics = Invoke-RestMethod -Uri `
        ("http://127.0.0.1:{0}/api/runtime-diagnostics" -f $active.Port) -TimeoutSec 10
    $report.checks.refresh_execution_locked = $refresh.refresh.executionAllowed -eq $false
    $report.checks.diagnostics_execution_locked = `
        $diagnostics.diagnostics.guardrails.executionAllowed -eq $false
    $report.checks.diagnostics_contract = `
        $diagnostics.diagnostics.contract -eq "GANN_RUNTIME_DIAGNOSTICS_V1"
    $report.diagnostics_session_id = $diagnostics.diagnostics.sessionId
    $report.diagnostics_startup_ms = $diagnostics.diagnostics.startup.totalMs
    Write-SoakPhase "safety_verified"

    Start-Sleep -Seconds ([Math]::Max(0, $DurationSeconds))
    Write-SoakPhase "duration_elapsed"
    $descendantIds = Get-DescendantIds $app.Id
    $report.descendant_pids_before_shutdown = $descendantIds
    Write-SoakPhase "descendants_captured" ([ordered]@{ count = $descendantIds.Count })

    $process = Get-Process -Id $app.Id -ErrorAction Stop
    $null = $process.CloseMainWindow()
    Write-SoakPhase "close_requested"
    if (-not $process.WaitForExit(15000)) {
        Stop-Process -Id $app.Id -Force
        $process.WaitForExit()
    }
    Write-SoakPhase "app_closed"
    Start-Sleep -Seconds 2
    $survivors = @($descendantIds | Where-Object { Get-Process -Id $_ -ErrorAction SilentlyContinue })
    $report.checks.no_descendant_survivors = $survivors.Count -eq 0
    $report.surviving_descendant_pids = $survivors
    Write-SoakPhase "survivors_checked" ([ordered]@{ count = $survivors.Count })
} catch {
    $report.errors += $_.Exception.Message
    Write-SoakPhase "error" ([ordered]@{ message = $_.Exception.Message })
} finally {
    if ($app -and (Get-Process -Id $app.Id -ErrorAction SilentlyContinue)) {
        Stop-Process -Id $app.Id -Force
    }
    if ($null -eq $previousDataRoot) {
        Remove-Item Env:GANN_ASTRO_DESKTOP_DATA -ErrorAction SilentlyContinue
    } else {
        $env:GANN_ASTRO_DESKTOP_DATA = $previousDataRoot
    }
    $report.finished_at_utc = [DateTime]::UtcNow.ToString("o")
    $failedChecks = @(
        $report.checks.GetEnumerator() |
            Where-Object { $_.Value -ne $true } |
            ForEach-Object { $_.Key }
    )
    $report.failed_checks = $failedChecks
    $report.passed = $report.errors.Count -eq 0 -and $failedChecks.Count -eq 0
    $report | ConvertTo-Json -Depth 12 | Set-Content -LiteralPath $reportPath -Encoding utf8
    Write-SoakPhase "finished" ([ordered]@{ passed = $report.passed })
}

Write-Output $reportPath
if (-not $report.passed) {
    throw "Native soak failed. Inspect $reportPath"
}
