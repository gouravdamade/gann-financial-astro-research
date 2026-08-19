param(
    [string]$CandidateRoot = "",
    [switch]$SkipSidecarBuild,
    [switch]$FinalizeOnly,
    [string]$SourceCommitOverride = "",
    [string]$CandidateStatus = "founder_inspection_candidate",
    [string]$CandidateLabel = "PFR-V2B-R4-T2P"
)

$ErrorActionPreference = "Stop"
$appRoot = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot ".."))
$projectRoot = [IO.Path]::GetFullPath((Join-Path $appRoot ".."))
$safeRoot = [IO.Path]::GetFullPath("D:\GannFinancialAstro")
$checkoutGitCommit = (& git.exe -C $projectRoot rev-parse HEAD).Trim()
& git.exe -C $projectRoot diff --quiet HEAD --
$preflightTrackedDirty = $LASTEXITCODE -ne 0
$preflightUntracked = @(& git.exe -C $projectRoot ls-files --others --exclude-standard).Count -gt 0
if ($preflightTrackedDirty -or $preflightUntracked) {
    throw "Windows candidate packaging requires a clean Git worktree"
}
$env:VITE_GANN_ASTRO_SOURCE_COMMIT = $checkoutGitCommit
$tauriConfig = Get-Content -LiteralPath (Join-Path $appRoot "src-tauri\tauri.conf.json") -Raw |
    ConvertFrom-Json
$appVersion = [string]$tauriConfig.version
$expectedEntryUrl = "index.html?v=$appVersion"
$configuredEntryUrl = [string]$tauriConfig.app.windows[0].url
if ($configuredEntryUrl -ne $expectedEntryUrl) {
    throw "Tauri entry URL must match the app version: expected $expectedEntryUrl, found $configuredEntryUrl"
}
if (-not $CandidateRoot) {
    $CandidateRoot = Join-Path $safeRoot "release_candidate\GannAstroDesk-$appVersion-tauri"
}
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

function Get-Sha256([string]$Path) {
    $fileHash = Get-Command Get-FileHash -ErrorAction SilentlyContinue
    if ($fileHash) {
        return (Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash
    }

    # The release script is also run from restricted Windows hosts where the
    # FileHash cmdlet is unavailable; certutil is the built-in equivalent.
    $lines = & certutil.exe -hashfile $Path SHA256
    if ($LASTEXITCODE -ne 0) {
        throw "Unable to calculate SHA-256 for $Path"
    }
    $hashLine = $lines | Where-Object { $_ -match '^[0-9A-Fa-f ]{64,}$' } | Select-Object -First 1
    if (-not $hashLine) {
        throw "certutil did not return a SHA-256 digest for $Path"
    }
    return (($hashLine -replace '\s', '').ToUpperInvariant())
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
$sourceGitCommit = if ($SourceCommitOverride) {
    $override = $SourceCommitOverride.Trim()
    if ($override -notmatch '^[0-9a-fA-F]{40}$') {
        throw "SourceCommitOverride must be a complete 40-character Git commit"
    }
    & git.exe -C $projectRoot cat-file -e "$override^{commit}"
    if ($LASTEXITCODE -ne 0) {
        throw "SourceCommitOverride is not present in this checkout: $override"
    }
    $override
} else {
    $checkoutGitCommit
}
# Tauri may rewrite a tracked TOML file's line endings while packaging on Windows.
# Compare content to HEAD and inspect nonignored untracked files so metadata stays
# strict about real source changes without treating that checkout-only rewrite as dirty.
& git.exe -C $projectRoot diff --quiet HEAD --
$sourceTrackedDirty = $LASTEXITCODE -ne 0
$sourceUntrackedDirty = [bool](
    & git.exe -C $projectRoot ls-files --others --exclude-standard |
        Select-Object -First 1
)
$sourceGitDirty = $sourceTrackedDirty -or $sourceUntrackedDirty
$nodeVersion = (& node.exe --version).Trim()
$npmVersion = (& npm.cmd --version).Trim()
$manifest = [ordered]@{
    product = "Gann Astro Desk"
    version = $appVersion
    status = $CandidateStatus
    built_at_utc = [DateTime]::UtcNow.ToString("o")
    executable = "GannAstroDesk.exe"
    executable_sha256 = Get-Sha256 $portableExe
    installer = $installer.Name
    installer_sha256 = Get-Sha256 $installerTarget
    file_count = $releaseFiles.Count
    total_bytes = ($releaseFiles | Measure-Object -Property Length -Sum).Sum
    shell = "Tauri 2 / Rust"
    source_git_commit = $sourceGitCommit
    checkout_git_commit = $checkoutGitCommit
    source_git_dirty = $sourceGitDirty
    node_version = $nodeVersion
    package_manager = "npm@$npmVersion"
    build_commands = @("npm ci", "npm run desktop:build -- --bundles nsis")
    jyotish_corpus_status = "NOT_CONFIGURED_OPTIONAL"
    candlestick_specialist_status = "NOT_CONFIGURED_OPTIONAL"
    timing_model = "UNLINKED_EVENT_GEOMETRY"
    market_direction = "ABSTAIN"
    tool_rail_contract = "GANN_CHART_TOOL_RAIL_V2"
    chart_tools = @(
        "select",
        "crosshair",
        "annotation",
        "horizontal",
        "vertical",
        "gann",
        "fibonacci",
        "favorites",
        "magnet",
        "keep_drawing",
        "undo",
        "reset",
        "clear"
    )
    backend_contract = "GANN_ASTRO_TAURI_PYTHON_SIDECAR_V1"
    companion_gateway_contract = "GANN_ASTRO_RUST_COMPANION_GATEWAY_V1"
    companion_client_contract = "GANN_ASTRO_ANDROID_COMPANION_CLIENT_V2"
    companion_session_contract = "GANN_ASTRO_COMPANION_SESSION_V2"
    companion_stream_contract = "GANN_ASTRO_COMPANION_STREAM_V1"
    companion_transport = "native_pinned_https_wss"
    companion_python_exposure = "loopback_only"
    companion_execution_allowed = $false
    companion_physical_device_validation = "pending"
    astronomy_contract = "RAMAN_SWISSEPH_SINGLE_SIDEREAL_PORPHYRY_TN_V2"
    chart_layout_contract = "GANN_CHART_LAYOUT_V1"
    drawing_contract = "GANN_RESEARCH_CHART_DRAWING_V1"
    planetary_line_contract = "GANN_EXPLORATORY_PLANETARY_LINE_OVERLAY_V1"
    planetary_line_settings_contract = "GANN_PLANETARY_LINE_LAB_SETTINGS_V1"
    planetary_line_ui = "Live SR Lab"
    planetary_line_mode = "research_only_curve_fit_exploration"
    planetary_line_execution_allowed = $false
    planetary_line_live_inference_allowed = $false
    planetary_line_auto_suggest_allowed = $false
    collective_field_contract = "GANN_PLANETARY_COLLECTIVE_FIELD_V1"
    collective_influence_contract = "GANN_PLANETARY_COLLECTIVE_INFLUENCE_V1"
    collective_motion_contract = "GANN_PLANETARY_COLLECTIVE_MOTION_V1"
    collective_event_contract = "GANN_PLANETARY_COLLECTIVE_EVENT_V1"
    collective_event_policy = "AVG_ALL_SAMPLED_EVENTS_V1"
    collective_event_refinement_contract = "GANN_PLANETARY_COLLECTIVE_EVENT_REFINEMENT_V1"
    collective_event_refinement_policy = "AVG_ALL_EPHEMERIS_ROOT_REFINEMENT_V1"
    collective_audit_snapshot_contract = "GANN_PLANETARY_COLLECTIVE_AUDIT_SNAPSHOT_V1"
    collective_audit_max_snapshots = 24
    collective_audit_serialized_budget_bytes = 229376
    collective_research_only = $true
    collective_counts_as_independent_vote = $false
    collective_directional_contribution = 0.0
    collective_live_inference_allowed = $false
    collective_auto_suggest_allowed = $false
    collective_shadow_ledger_allowed = $false
    collective_official_ml_note_allowed = $false
    collective_execution_allowed = $false
    collective_visual_study_dossier_contract = "GANN_AVG_ALL_VISUAL_STUDY_DOSSIER_V1"
    collective_gann_visual_study_contract = "GANN_AVG_ALL_GANN_VISUAL_STUDY_V1"
    collective_sbc_visual_study_contract = "GANN_AVG_ALL_SBC_VISUAL_STUDY_V1"
    collective_prospective_freeze_candidate_contract = "GANN_AVG_ALL_PROSPECTIVE_FREEZE_CANDIDATE_V1"
    collective_visual_study_mode = "export_only_non_voting"
    collective_visual_study_outcome_labels_included = $false
    collective_visual_study_trial_registered = $false
    collective_visual_study_existing_shadow_trial_modified = $false
    agarwal_financial_chapter_rag_source = "AGARWAL_FINANCIAL_CHAPTER20_HYPOTHESIS_20260722"
    agarwal_financial_chapter_rag_layer = "hypothesis_reference"
    agarwal_financial_chapter_execution_allowed = $false
    arghya_reconciliation_contract = "TRAILOKYA_ARGHYA_RECONCILIATION_V1"
    arghya_reconciliation_profile = "trailokya_arghya_reconciliation_v1"
    arghya_reference_price_unit_fraction = 0.05
    arghya_price_formula_certified = $false
    arghya_market_mapping_allowed = $false
    arghya_auto_suggest_allowed = $false
    arghya_live_inference_allowed = $false
    arghya_official_ml_note_allowed = $false
    arghya_execution_allowed = $false
    aspect_evidence_trace_contract = "GANN_ASPECT_EVIDENCE_TRACE_V1"
    aspect_evidence_trace_mode = "read_only_timestamp_safe"
    aspect_reaction_checkpoints = @(
        "start",
        "highest_wick",
        "lowest_wick"
    )
    aspect_reaction_extrema_mode = "retrospective_only_after_window_close"
    aspect_evidence_live_inference_allowed = $false
    aspect_evidence_shadow_ledger_allowed = $false
    aspect_evidence_execution_allowed = $false
    webview_asset_cache_contract = "GANN_TAURI_VERSIONED_ENTRYPOINT_V1"
    candlestick_shadow_contract = "GANN_CANDLESTICK_APPEND_ONLY_SHADOW_LEDGER_V3"
    candlestick_trial_contract = "GANN_CANDLESTICK_FROZEN_SHADOW_TRIAL_V3"
    rsi_evidence_contract = "GANN_RSI_EVIDENCE_V1"
    rsi_methodology = "wilder_smoothed_close_v1"
    market_synthesis_contract = "GANN_LOCAL_MARKET_SYNTHESIS_DRAFT_V1"
    market_synthesis_packet_contract = "GANN_MARKET_SYNTHESIS_PACKET_V1"
    market_synthesis_execution_allowed = $false
    mt5_clock_probe_contract = "GANN_MT5_CLOCK_PROBE_V1"
    mt5_time_normalization_contract = "GANN_MT5_SERVER_TIME_NORMALIZATION_V1"
    mt5_history_snapshot_contract = "MT5_TIMESTAMP_NORMALIZED_CLOSED_BARS_V2"
    mt5_execution_mode = "read_only_market_data"
    chakra_lab_contract = "SBC_CHAKRA_LAB_SNAPSHOT_V1"
    chakra_lab_mode = "read_only_guidance"
    chakra_instrument_key_converter_contract = "SBC_ENGLISH_INITIAL_ADVISORY_V1"
    chakra_lab_execution_allowed = $false
    chakra_lab_financially_validated = $false
    experimental_evidence_contract = "XE1_EXPERIMENTAL_EVIDENCE_LAB_V1"
    experimental_evidence_profile = "XE1_EVIDENCE_ROLE_MODIFIER_ABLATION_V1"
    experimental_evidence_dataset_default = "SYNTHETIC"
    experimental_evidence_trial_ledger = "XE1_EXPERIMENTAL_TRIAL_LEDGER_V1"
    experimental_evidence_price_data_read = $false
    experimental_evidence_price_outcome_read = $false
    experimental_evidence_sbc_fusion = $false
    experimental_evidence_fields_formula_changed = $false
    experimental_evidence_auto_suggest_added = $false
    experimental_evidence_ml_added = $false
    experimental_evidence_mt5_added = $false
    experimental_evidence_execution_allowed = $false
    xe2_experimental_evidence_contract = "XE2_CAUSAL_SCOPED_EVIDENCE_LAB_V1"
    xe2_experimental_evidence_profile = "XE2_CAUSAL_SCOPED_SPEED_MODIFIER_TOURNAMENT_V1"
    xe2_experimental_evidence_dataset = "TOUCHED_DEV"
    xe2_real_astronomical_input = "hash_linked_event_identity_and_raw_speed"
    xe2_real_signed_evidence = "not_admitted_none_exists"
    xe2_synthetic_sign_channel = "test_only_not_market_evidence"
    xe2_market_outcome_read = $false
    xe2_live_mt5_read = $false
    xe2_global_modifier_default_allowed = $false
    xe2_modifier_stacking_allowed = $false
    xe2_market_direction = "blocked_no_real_signed_evidence"
    xe2_execution_allowed = $false
    xe3_sign_admission_contract = "XE3_OUTCOME_BLIND_SIGN_ADMISSION_WORKBENCH_V1"
    xe3_sign_admission_profile = "XE3_OUTCOME_BLIND_CHART_CONDITIONED_SIGN_ADMISSION_V1"
    xe3_dataset_status = "TOUCHED_DEV"
    xe3_sign_source = "founder_entered_outcome_blind_only"
    xe3_price_data_read = $false
    xe3_price_outcome_read = $false
    xe3_live_mt5_read = $false
    xe3_fields_read = $false
    xe3_sbc_read = $false
    xe3_auto_suggest_read = $false
    xe3_llm_polarity_inference = $false
    xe3_market_direction_inferred = $false
    xe3_execution_allowed = $false
}
$manifest | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $candidate "release.manifest.json") -Encoding utf8

$releaseReadme = @"
# Gann Astro Desk $appVersion - $CandidateLabel

This is a read-only experimental research candidate, not a validated or executable trading product.

- Source commit: $sourceGitCommit
- Source working tree clean: $(-not $sourceGitDirty)
- Reconciliation: $CandidateLabel
- Node: $nodeVersion
- Package manager: npm@$npmVersion
- Jyotish corpus: NOT_CONFIGURED_OPTIONAL (private corpus not bundled)
- Candlestick specialist: NOT_CONFIGURED_OPTIONAL (private corpus not bundled)
- Timing model: UNLINKED_EVENT_GEOMETRY
- Execution allowed: false
- Automatic order placement: false
- Market direction: ABSTAIN
- XE1 Experimental Lab: synthetic/default, no price reads, no SBC fusion, no execution
- XE2 Scoped Evidence: hash-linked astronomy plus synthetic sign tests only; no signed market evidence, no outcome read, no execution
- XE3 Outcome-Blind Sign Admission: founder-entered signs only; no price, live MT5, Fields, SBC, Auto Suggest, ML polarity inference, or execution

Run `GannAstroDesk.exe` from this folder and keep the adjacent `backend` folder in place.
"@
Set-Content -LiteralPath (Join-Path $candidate "BETA_README.md") -Value $releaseReadme -Encoding utf8

$checksumLines = @(
    "$(Get-Sha256 $portableExe)  GannAstroDesk.exe",
    "$(Get-Sha256 $installerTarget)  $($installer.Name)",
    "$(Get-Sha256 $sidecarExe)  backend/GannAstroBackend.exe",
    "$(Get-Sha256 (Join-Path $candidate 'release.manifest.json'))  release.manifest.json",
    "SOURCE_GIT_COMMIT  $sourceGitCommit",
    "SOURCE_GIT_DIRTY  $sourceGitDirty"
)
Set-Content -LiteralPath (Join-Path $candidate "SHA256SUMS.txt") -Value $checksumLines -Encoding ascii

Write-Output $portableExe
Write-Output $installerTarget
