param(
    [string]$CandidateRoot = "",
    [int]$DurationSeconds = 20,
    [switch]$SkipCrashRecovery
)

$ErrorActionPreference = "Stop"
$safeRoot = [IO.Path]::GetFullPath("D:\GannFinancialAstro")
$appRoot = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot ".."))
$tauriConfig = Get-Content -LiteralPath (Join-Path $appRoot "src-tauri\tauri.conf.json") -Raw |
    ConvertFrom-Json
$appVersion = [string]$tauriConfig.version
if (-not $CandidateRoot) {
    $CandidateRoot = Join-Path $safeRoot "release_candidate\GannAstroDesk-$appVersion-tauri"
}
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
$dataRoot = Join-Path $safeRoot "soak\tauri_$($appVersion)_$session"
$logsRoot = Join-Path $dataRoot "logs"
New-Item -ItemType Directory -Path $logsRoot -Force | Out-Null
$reportPath = Join-Path $logsRoot "native_soak_report.json"
$phasePath = Join-Path $logsRoot "native_soak_phases.jsonl"
$previousDataRoot = $env:GANN_ASTRO_DESKTOP_DATA
$previousApiTokenOverride = $env:GANN_ASTRO_API_TOKEN_OVERRIDE
$soakApiToken = [Guid]::NewGuid().ToString("N")
$privateHeaders = @{
    "X-Gann-Astro-Token" = $soakApiToken
}
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

function Invoke-PrivateRestMethod(
    [string]$Uri,
    [string]$Method = "Get",
    [object]$Body = $null,
    [int]$TimeoutSec = 10
) {
    $arguments = @{
        Uri = $Uri
        Method = $Method
        Headers = $privateHeaders
        TimeoutSec = $TimeoutSec
    }
    if ($null -ne $Body) {
        $arguments.ContentType = "application/json"
        $arguments.Body = $Body | ConvertTo-Json -Depth 12
    }
    return Invoke-RestMethod @arguments
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
                $health = Invoke-PrivateRestMethod `
                    -Uri ("http://127.0.0.1:{0}/api/health" -f $port) -TimeoutSec 3
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
    return Invoke-PrivateRestMethod -Uri $Uri -Method Post -Body $Body -TimeoutSec 10
}

function Wait-ForNormalizedShadow([int]$Port, [int]$TimeoutSeconds = 90) {
    $deadline = (Get-Date).AddSeconds($TimeoutSeconds)
    $last = $null
    while ((Get-Date) -lt $deadline) {
        try {
            $last = Invoke-PrivateRestMethod -Uri `
                ("http://127.0.0.1:{0}/api/candlestick-shadow" -f $Port) -TimeoutSec 10
            if ($last.shadow.lastScan.timeNormalization.valid -eq $true) {
                return $last
            }
        } catch {}
        Start-Sleep -Seconds 2
    }
    $message = if ($last) { [string]$last.shadow.lastScan.message } else { "no snapshot" }
    throw "Candlestick shadow did not expose fresh MT5 time normalization: $message"
}

try {
    Write-SoakPhase "app_launching"
    $env:GANN_ASTRO_DESKTOP_DATA = $dataRoot
    $env:GANN_ASTRO_API_TOKEN_OVERRIDE = $soakApiToken
    $app = Start-Process -FilePath $executable -PassThru
    $appStartedAt = $app.StartTime
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
    $report.checks.mt5_app_execution_locked = `
        $initial.Health.mt5.appExecutionAllowed -eq $false
    $report.checks.mt5_read_only_mode = `
        $initial.Health.mt5.executionMode -eq "read_only_market_data"
    $chakraPayload = [ordered]@{
        at = "2026-07-17T12:00:00+05:30"
        timezone = "Asia/Kolkata"
        latitude = 28.6139
        longitude = 77.2090
        altitudeM = 216.0
        bodies = @("SUN", "MOON", "JUPITER")
        actors = @(
            [ordered]@{ body = "SUN" },
            [ordered]@{ body = "MOON" },
            [ordered]@{ body = "JUPITER"; motionClass = "MEAN" }
        )
    }
    $chakra = Invoke-JsonPost `
        ("http://127.0.0.1:{0}/api/chakra-lab/snapshot" -f $initial.Port) `
        $chakraPayload
    $chakraSnapshot = $chakra.snapshot
    $jupiterReadiness = @(
        $chakraSnapshot.actor_readiness |
            Where-Object { $_.body -eq "JUPITER" }
    ) | Select-Object -First 1
    $report.chakra_snapshot_id = [string]$chakraSnapshot.snapshot_id
    $report.checks.chakra_endpoint_ok = $chakra.ok -eq $true
    $report.checks.chakra_contract = `
        $chakraSnapshot.contract -eq "SBC_CHAKRA_LAB_SNAPSHOT_V1"
    $report.checks.chakra_board_has_81_cells = `
        @($chakraSnapshot.grid.cells).Count -eq 81
    $report.checks.chakra_cutoff_matches_as_of = `
        $chakraSnapshot.evidence_cutoff_utc -eq $chakraSnapshot.as_of_utc
    $report.checks.chakra_jupiter_motion_explicit = `
        $jupiterReadiness.status -eq "READY"
    $report.checks.chakra_timestamp_guardrails = (
        $chakraSnapshot.guardrails.read_only -eq $true -and
        $chakraSnapshot.guardrails.timestamp_safe -eq $true -and
        $chakraSnapshot.guardrails.no_lookahead -eq $true
    )
    $report.checks.chakra_market_execution_locked = (
        $chakraSnapshot.guardrails.execution_allowed -eq $false -and
        $chakraSnapshot.guardrails.market_data_included -eq $false -and
        $chakraSnapshot.guardrails.financially_validated -eq $false -and
        $chakraSnapshot.guardrails.guidance_only -eq $true
    )
    Write-SoakPhase "chakra_lab_verified" ([ordered]@{
        snapshot_id = $report.chakra_snapshot_id
        cells = @($chakraSnapshot.grid.cells).Count
        actor_status = [string]$jupiterReadiness.status
        evidence_cutoff_utc = [string]$chakraSnapshot.evidence_cutoff_utc
    })
    $candleHealth = Invoke-PrivateRestMethod -Uri `
        ("http://127.0.0.1:{0}/api/local-candlestick/health" -f $initial.Port) -TimeoutSec 10
    $chart = Invoke-PrivateRestMethod -Uri `
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
            $chart = Invoke-PrivateRestMethod -Uri $historyUri -TimeoutSec 40
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
    $candleShadow = Wait-ForNormalizedShadow $initial.Port
    $report.checks.candlestick_shadow_contract = `
        $candleShadow.shadow.contract -eq "GANN_CANDLESTICK_APPEND_ONLY_SHADOW_LEDGER_V3"
    $report.checks.candlestick_shadow_trial_frozen = `
        $candleShadow.shadow.trial.contract -eq "GANN_CANDLESTICK_FROZEN_SHADOW_TRIAL_V3"
    $report.checks.mt5_clock_probe_contract = `
        $candleShadow.shadow.lastScan.timeNormalization.probe.contract -eq `
        "GANN_MT5_CLOCK_PROBE_V1"
    $report.checks.mt5_time_normalization_contract = `
        $candleShadow.shadow.lastScan.timeNormalization.contract -eq `
        "GANN_MT5_SERVER_TIME_NORMALIZATION_V1"
    $report.checks.mt5_time_normalization_valid = `
        $candleShadow.shadow.lastScan.timeNormalization.valid -eq $true
    $report.checks.mt5_normalized_tick_fresh = `
        [Math]::Abs([double]$candleShadow.shadow.lastScan.timeNormalization.normalizedMarketTickSkewSeconds) `
        -le 300
    $report.checks.mt5_clock_probe_fresh = `
        [double]$candleShadow.shadow.lastScan.timeNormalization.probe.ageSeconds -le 30
    $report.checks.candlestick_shadow_chain_valid = `
        $candleShadow.shadow.integrity.ok -eq $true
    $report.checks.candlestick_shadow_failed_gate_visible = `
        $candleShadow.shadow.model.retrospectiveGate.status -eq "failed"
    $report.checks.candlestick_shadow_execution_locked = (
        $candleShadow.shadow.guardrails.executionAllowed -eq $false -and
        $candleShadow.shadow.guardrails.mt5ReadOnly -eq $true
    )
    Write-SoakPhase "candlestick_shadow_verified" ([ordered]@{
        trial_id = $candleShadow.shadow.trial.trialId
        decisions = $candleShadow.shadow.summary.decisions
        scan_state = $candleShadow.shadow.lastScan.state
        server_offset_seconds = `
            $candleShadow.shadow.lastScan.timeNormalization.serverOffsetSeconds
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

    $layoutAfter = Invoke-PrivateRestMethod -Uri `
        ("http://127.0.0.1:{0}/api/chart-layouts/{1}" -f $active.Port, $layoutId) -TimeoutSec 10
    $report.checks.layout_survived_recovery = (
        $layoutAfter.ok -and
        $layoutAfter.layout.name -eq $layoutPayload.name -and
        $layoutAfter.layout.revision -eq 1
    )
    Write-SoakPhase "layout_verified"
    $refresh = Invoke-PrivateRestMethod -Uri `
        ("http://127.0.0.1:{0}/api/prospective-refresh" -f $active.Port) -TimeoutSec 10
    $diagnostics = Invoke-PrivateRestMethod -Uri `
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
    $survivorIds = [Collections.Generic.List[int]]::new()
    $preexistingParentageIds = [Collections.Generic.List[int]]::new()
    foreach ($descendantId in $descendantIds) {
        $descendant = Get-Process -Id $descendantId -ErrorAction SilentlyContinue
        if ($null -eq $descendant) {
            continue
        }
        if ($descendant.StartTime -lt $appStartedAt) {
            $preexistingParentageIds.Add([int]$descendantId)
            continue
        }
        $survivorIds.Add([int]$descendantId)
    }
    $survivors = @($survivorIds)
    $report.checks.no_descendant_survivors = $survivors.Count -eq 0
    $report.surviving_descendant_pids = $survivors
    $report.preexisting_parentage_pids_ignored = @($preexistingParentageIds)
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
    if ($null -eq $previousApiTokenOverride) {
        Remove-Item Env:GANN_ASTRO_API_TOKEN_OVERRIDE -ErrorAction SilentlyContinue
    } else {
        $env:GANN_ASTRO_API_TOKEN_OVERRIDE = $previousApiTokenOverride
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
