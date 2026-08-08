import type {
  AnnotationDraft,
  AspectFamily,
  AspectEvidenceTrace,
  BackendRuntimeInfo,
  ChartAnnotation,
  ChartDrawing,
  ChartLayout,
  ChartLayoutState,
  ChartParameters,
  ChartPayload,
  ChartWorkspaceKind,
  DataArtifact,
  DecisionPacket,
  DrawingTemplate,
  EventDetail,
  GenerationJob,
  CandlestickEvidence,
  CandlestickShadowSnapshot,
  LocalCandlestickDraft,
  LocalCandlestickHealth,
  LocalJyotishDraft,
  LocalJyotishHealth,
  MarketSynthesisDraft,
  MarketSynthesisHealth,
  RsiEvidence,
  Mt5HistorySnapshot,
  Mt5Status,
  ParameterSchema,
  PriceSource,
  PlanetaryLineGroup,
  PlanetaryLineOverlay,
  ProspectiveRefreshStatus,
  RuntimeDiagnosticsBundle,
  SavedParameterProfile,
  ShadowLedgerSnapshot,
  WorkspacePreferences,
  ChakraLabAuditRequest,
  ChakraAuditPackageBuild,
  ChakraAuditPackageRequest,
  ChakraAuditPackageVerification,
  ChakraAuditCatalogBuild,
  ChakraAuditCatalogRequest,
  ChakraAuditCatalogVerification,
  ChakraLabRequest,
  ChakraLabSnapshot,
  TrailokyaSourceOnlyGeometry,
  ChakraFixedPhasorSeries,
  ChakraLinkedAuditView,
  ChakraReproducibleAuditPackage,
  ChakraSignedAuditCatalogBundle,
  ChakraTimingProfileAdmissionReport,
  ChakraTimingProfileSourceReadinessReport,
  ChakraTimingProfileSourceVerificationReport,
  ChakraTimingProfileExternalReviewReport,
  ChakraTimingProfileSignedReviewReport,
  ChakraTimingProfileSourceCertificationReport,
  ChartConditionedPolarityLookup,
  FounderReviewExportRequest,
  FounderReviewExportResult,
  FounderReviewWorkbench,
  BphsClassicalCalendarRange,
  BphsClassicalCalendarRangeRequest,
  FxSidePilotStatus,
  SynchronizedIndependentRange,
  SynchronizedIndependentRangeRequest,
} from './types'
import { disconnectCompanion, getCompanionSession, nativeCompanionRequest } from './companion'

type ApiEnvelope<T> = { ok: boolean; error?: string } & T
let backendRuntimePromise: Promise<BackendRuntimeInfo> | null = null

function isTauriRuntime(): boolean {
  return typeof window !== 'undefined' && '__TAURI_INTERNALS__' in window
}

export async function fetchBackendRuntime(force = false): Promise<BackendRuntimeInfo | null> {
  if (getCompanionSession()) return null
  if (!isTauriRuntime()) return null
  if (force) backendRuntimePromise = null
  if (backendRuntimePromise == null) {
    backendRuntimePromise = import('@tauri-apps/api/core').then(async ({ invoke }) => {
      const runtime = await invoke<BackendRuntimeInfo>('backend_runtime')
      if (runtime.contract !== 'GANN_ASTRO_TAURI_PYTHON_SIDECAR_V1') {
        throw new Error(`Unsupported backend runtime contract: ${runtime.contract}`)
      }
      if (!runtime.baseUrl.startsWith('http://127.0.0.1:')) {
        throw new Error('Backend runtime did not provide a private loopback URL')
      }
      if (typeof runtime.apiToken !== 'string' || runtime.apiToken.length < 16) {
        throw new Error('Backend runtime did not provide a private API token')
      }
      if (runtime.executionAllowed) {
        throw new Error('Backend runtime violated the read-only execution lock')
      }
      return runtime
    })
  }
  return backendRuntimePromise
}

async function backendRequestTarget(url: string): Promise<{
  url: string
  authorizationHeaders: Record<string, string>
}> {
  const runtime = await fetchBackendRuntime()
  const baseUrl = runtime?.baseUrl.replace(/\/$/, '') ?? ''
  return {
    url: baseUrl && url.startsWith('/') ? `${baseUrl}${url}` : url,
    authorizationHeaders: runtime?.apiToken
      ? { 'X-Gann-Astro-Token': runtime.apiToken }
      : {},
  }
}

function wait(milliseconds: number): Promise<void> {
  return new Promise((resolve) => window.setTimeout(resolve, milliseconds))
}

async function request<T>(url: string, init?: RequestInit): Promise<T> {
  const method = (init?.method ?? 'GET').toUpperCase()
  if (getCompanionSession()) {
    if (!url.startsWith('/')) throw new Error('Companion requests must use a relative path')
    const response = await nativeCompanionRequest({
      path: url,
      method,
      body: typeof init?.body === 'string' ? init.body : undefined,
    })
    const payload = response.payload as ApiEnvelope<T>
    if (response.status < 200 || response.status >= 300 || !payload.ok) {
      if (response.status === 401) {
        await disconnectCompanion().catch(() => undefined)
        window.dispatchEvent(new Event('gann-astro-companion-invalid'))
      }
      throw new Error(payload.error || `Request failed: ${response.status}`)
    }
    return payload
  }
  const attempts = method === 'GET' ? 61 : 1
  let response: Response | null = null
  let networkError: unknown = null
  for (let attempt = 1; attempt <= attempts; attempt += 1) {
    const target = await backendRequestTarget(url)
    try {
      response = await fetch(target.url, {
        ...init,
        headers: {
          'Content-Type': 'application/json',
          ...target.authorizationHeaders,
          ...(init?.headers ?? {}),
        },
      })
      break
    } catch (error) {
      networkError = error
      if (isTauriRuntime()) backendRuntimePromise = null
      if (attempt === attempts) throw error
      await wait(1000)
    }
  }
  if (!response) throw networkError instanceof Error ? networkError : new Error('Backend is unavailable')
  const payload = (await response.json()) as ApiEnvelope<T>
  if (!response.ok || !payload.ok) {
    throw new Error(payload.error || `Request failed: ${response.status}`)
  }
  return payload
}

export async function fetchChart(
  parameters?: ChartParameters,
  replay?: { cutoffUtc: string },
): Promise<ChartPayload> {
  const query = new URLSearchParams({
    start: parameters?.start ?? '2025-05-25T00:00:00+05:30',
    end: parameters?.end ?? '2025-05-31T23:59:59+05:30',
    symbol: parameters?.symbol ?? 'USDJPY',
    timeframe: parameters?.timeframe ?? 'H1',
    source: parameters?.dataSource ?? 'research',
  })
  if (parameters) {
    parameters.transitBodies.forEach((value) => query.append('transitBody', value))
    parameters.natalBodies.forEach((value) => query.append('natalBody', value))
    parameters.aspects.forEach((value) => query.append('aspect', value))
    parameters.excludedFamilyKeys.forEach((value) => query.append('excludeFamily', value))
    query.set('onlyTouched', String(parameters.onlyTouched))
    query.set('aspectDurationMode', parameters.aspectDurationMode ?? 'auto')
    query.set('minDurationMinutes', String(parameters.minDurationMinutes))
    if (parameters.maxDurationMinutes != null) query.set('maxDurationMinutes', String(parameters.maxDurationMinutes))
    query.set('liveBarCount', String(parameters.liveBarCount))
  }
  if (replay?.cutoffUtc) query.set('replayCutoff', replay.cutoffUtc)
  const payload = await request<{ chart: ChartPayload }>(`/api/chart?${query}`)
  return payload.chart
}

export async function fetchPlanetaryLines(input: {
  symbol: string
  timeframe: string
  timestamps: number[]
  groups: PlanetaryLineGroup[]
}): Promise<PlanetaryLineOverlay> {
  const payload = await request<{ overlay: PlanetaryLineOverlay }>('/api/planetary-lines', {
    method: 'POST',
    body: JSON.stringify(input),
  })
  return payload.overlay
}

export async function fetchParameterSchema(): Promise<ParameterSchema> {
  const payload = await request<{ schema: ParameterSchema }>('/api/parameters/schema')
  return payload.schema
}

export async function fetchParameterProfiles(): Promise<SavedParameterProfile[]> {
  const payload = await request<{ profiles: SavedParameterProfile[] }>('/api/parameter-profiles')
  return payload.profiles
}

export async function fetchWorkspacePreferences(): Promise<WorkspacePreferences> {
  const payload = await request<{ preferences: WorkspacePreferences }>('/api/workspace-preferences')
  return payload.preferences
}

export async function saveWorkspacePreferences(preferences: WorkspacePreferences): Promise<WorkspacePreferences> {
  const payload = await request<{ preferences: WorkspacePreferences }>('/api/workspace-preferences', {
    method: 'PUT',
    body: JSON.stringify(preferences),
  })
  return payload.preferences
}

export async function saveParameterProfile(input: {
  profileId?: string
  name: string
  parameters: ChartParameters
  isDefault?: boolean
}): Promise<SavedParameterProfile> {
  const payload = await request<{ profile: SavedParameterProfile }>('/api/parameter-profiles', {
    method: 'POST',
    body: JSON.stringify(input),
  })
  return payload.profile
}

export async function deleteParameterProfile(profileId: string): Promise<void> {
  await request<Record<string, never>>(`/api/parameter-profiles/${encodeURIComponent(profileId)}`, {
    method: 'DELETE',
  })
}

export async function fetchChartLayouts(scope: {
  workspaceKind: ChartWorkspaceKind
  symbol: string
  timeframe: string
  familyKey?: string
}): Promise<ChartLayout[]> {
  const query = new URLSearchParams({
    workspaceKind: scope.workspaceKind,
    symbol: scope.symbol,
    timeframe: scope.timeframe,
  })
  if (scope.familyKey != null) query.set('familyKey', scope.familyKey)
  const payload = await request<{ layouts: ChartLayout[] }>(`/api/chart-layouts?${query}`)
  return payload.layouts
}

export async function fetchChartLayout(layoutId: string): Promise<ChartLayout> {
  const payload = await request<{ layout: ChartLayout }>(
    `/api/chart-layouts/${encodeURIComponent(layoutId)}`,
  )
  return payload.layout
}

export async function saveChartLayout(input: {
  layoutId?: string
  expectedRevision?: number
  name: string
  workspaceKind: ChartWorkspaceKind
  symbol: string
  timeframe: string
  familyKey: string
  isDefault?: boolean
  autosave: boolean
  chartState: ChartLayoutState
  drawings: ChartDrawing[]
}): Promise<ChartLayout> {
  const payload = await request<{ layout: ChartLayout }>('/api/chart-layouts', {
    method: 'POST',
    body: JSON.stringify(input),
  })
  return payload.layout
}

export async function deleteChartLayout(layoutId: string): Promise<void> {
  await request<Record<string, never>>(`/api/chart-layouts/${encodeURIComponent(layoutId)}`, {
    method: 'DELETE',
  })
}

export async function fetchDrawingTemplates(): Promise<DrawingTemplate[]> {
  const payload = await request<{ templates: DrawingTemplate[] }>('/api/drawing-templates')
  return payload.templates
}

export async function saveDrawingTemplate(input: {
  templateId?: string
  name: string
  drawingType: ChartDrawing['type']
  style: ChartDrawing['style']
  settings: Record<string, unknown>
}): Promise<DrawingTemplate> {
  const payload = await request<{ template: DrawingTemplate }>('/api/drawing-templates', {
    method: 'POST',
    body: JSON.stringify(input),
  })
  return payload.template
}

export async function deleteDrawingTemplate(templateId: string): Promise<void> {
  await request<Record<string, never>>(
    `/api/drawing-templates/${encodeURIComponent(templateId)}`,
    { method: 'DELETE' },
  )
}

export async function fetchGenerationJobs(): Promise<GenerationJob[]> {
  const payload = await request<{ jobs: GenerationJob[] }>('/api/generation/jobs')
  return payload.jobs
}

export async function fetchGenerationJob(jobId: string): Promise<GenerationJob> {
  const payload = await request<{ job: GenerationJob }>(
    `/api/generation/jobs/${encodeURIComponent(jobId)}`,
  )
  return payload.job
}

export async function createGenerationJob(input: {
  label?: string
  parameters: ChartParameters
  autoActivate?: boolean
}): Promise<GenerationJob> {
  const payload = await request<{ job: GenerationJob }>('/api/generation/jobs', {
    method: 'POST',
    body: JSON.stringify(input),
  })
  return payload.job
}

export async function cancelGenerationJob(jobId: string): Promise<GenerationJob> {
  const payload = await request<{ job: GenerationJob }>(
    `/api/generation/jobs/${encodeURIComponent(jobId)}/cancel`,
    { method: 'POST' },
  )
  return payload.job
}

export async function fetchDataArtifacts(): Promise<DataArtifact[]> {
  const payload = await request<{ artifacts: DataArtifact[] }>('/api/data-artifacts')
  return payload.artifacts
}

export async function activateDataArtifact(artifactId: string): Promise<DataArtifact> {
  const payload = await request<{ artifact: DataArtifact }>(
    `/api/data-artifacts/${encodeURIComponent(artifactId)}/activate`,
    { method: 'POST' },
  )
  return payload.artifact
}

export async function fetchMt5Status(): Promise<Mt5Status> {
  const payload = await request<{ mt5: Mt5Status }>('/api/mt5/status')
  return payload.mt5
}

export async function createMt5HistorySnapshot(input: {
  symbol: string
  timeframe: ChartParameters['timeframe']
  start: string
  end: string
}): Promise<Mt5HistorySnapshot> {
  const payload = await request<{ snapshot: Mt5HistorySnapshot }>('/api/mt5/history-snapshots', {
    method: 'POST',
    body: JSON.stringify(input),
  })
  return payload.snapshot
}

export async function fetchMt5HistorySnapshots(): Promise<Mt5HistorySnapshot[]> {
  const payload = await request<{ snapshots: Mt5HistorySnapshot[] }>('/api/mt5/history-snapshots')
  return payload.snapshots
}

export async function fetchPriceSources(): Promise<PriceSource[]> {
  const payload = await request<{ priceSources: PriceSource[] }>('/api/price-sources')
  return payload.priceSources
}

export async function promoteMt5HistorySnapshot(
  snapshotId: string,
  label?: string,
): Promise<PriceSource> {
  const payload = await request<{ priceSource: PriceSource }>(
    `/api/mt5/history-snapshots/${encodeURIComponent(snapshotId)}/promote`,
    { method: 'POST', body: JSON.stringify({ label }) },
  )
  return payload.priceSource
}

export async function fetchFamily(familyKey: string, eventId?: string): Promise<AspectFamily> {
  const query = eventId ? `?eventId=${encodeURIComponent(eventId)}` : ''
  const payload = await request<{ family: AspectFamily }>(
    `/api/families/${encodeURIComponent(familyKey)}${query}`,
  )
  return payload.family
}

export async function fetchEventDetail(eventId: string): Promise<EventDetail> {
  const payload = await request<{ detail: EventDetail }>(`/api/events/${encodeURIComponent(eventId)}`)
  return payload.detail
}

export async function fetchLiveDecision(
  eventId: string,
  decisionTime: string,
): Promise<DecisionPacket> {
  const payload = await request<{ decision: DecisionPacket }>('/api/decisions', {
    method: 'POST',
    body: JSON.stringify({ mode: 'live_inference', eventId, decisionTime }),
  })
  return payload.decision
}

export async function fetchShadowLedger(limit = 100): Promise<ShadowLedgerSnapshot> {
  const query = new URLSearchParams({ limit: String(limit) })
  const payload = await request<{ shadow: ShadowLedgerSnapshot }>(`/api/shadow-ledger?${query}`)
  return payload.shadow
}

export async function scanShadowLedger(): Promise<ShadowLedgerSnapshot> {
  const payload = await request<{ shadow: ShadowLedgerSnapshot }>('/api/shadow-ledger/scan', {
    method: 'POST',
    body: '{}',
  })
  return payload.shadow
}

export async function fetchCandlestickShadow(limit = 100): Promise<CandlestickShadowSnapshot> {
  const query = new URLSearchParams({ limit: String(limit) })
  const payload = await request<{ shadow: CandlestickShadowSnapshot }>(`/api/candlestick-shadow?${query}`)
  return payload.shadow
}

export async function scanCandlestickShadow(): Promise<CandlestickShadowSnapshot> {
  const payload = await request<{ shadow: CandlestickShadowSnapshot }>('/api/candlestick-shadow/scan', {
    method: 'POST',
    body: '{}',
  })
  return payload.shadow
}

export async function requestProspectiveRefresh(): Promise<ProspectiveRefreshStatus> {
  const payload = await request<{ refresh: ProspectiveRefreshStatus }>(
    '/api/prospective-refresh/run',
    { method: 'POST', body: '{}' },
  )
  return payload.refresh
}

export async function fetchRuntimeDiagnostics(): Promise<RuntimeDiagnosticsBundle> {
  const runtime = await fetchBackendRuntime(true)
  const payload = await request<{ diagnostics: RuntimeDiagnosticsBundle['diagnostics'] }>(
    '/api/runtime-diagnostics',
  )
  return { runtime, diagnostics: payload.diagnostics }
}

export async function recordFrontendDiagnostic(
  name: 'app_bootstrap' | 'artifact_activation' | 'chart_apply' | 'chart_initial_render' | 'chart_live_refresh' | 'layout_restore',
  durationMs: number,
  ok = true,
): Promise<void> {
  await request('/api/runtime-diagnostics/frontend', {
    method: 'POST',
    body: JSON.stringify({ name, durationMs, ok }),
  })
}

export async function fetchLocalJyotishHealth(): Promise<LocalJyotishHealth> {
  const payload = await request<{ localJyotish: LocalJyotishHealth }>('/api/local-jyotish/health')
  return payload.localJyotish
}

export async function analyzeWithLocalJyotish(input: {
  eventId: string
  annotationId?: string | null
  question: string
}): Promise<LocalJyotishDraft> {
  const payload = await request<{ draft: LocalJyotishDraft }>('/api/local-jyotish/analyze', {
    method: 'POST',
    body: JSON.stringify(input),
  })
  return payload.draft
}

export async function fetchLocalCandlestickHealth(): Promise<LocalCandlestickHealth> {
  const payload = await request<{ localCandlestick: LocalCandlestickHealth }>('/api/local-candlestick/health')
  return payload.localCandlestick
}

export async function fetchCandlestickEvidence(input: {
  eventId: string
  annotationId?: string | null
}): Promise<CandlestickEvidence> {
  const payload = await request<{ evidence: CandlestickEvidence }>('/api/local-candlestick/evidence', {
    method: 'POST',
    body: JSON.stringify(input),
  })
  return payload.evidence
}

export async function fetchAspectEvidenceTrace(
  eventId: string,
  maxRecords = 120,
): Promise<AspectEvidenceTrace> {
  const query = new URLSearchParams({ maxRecords: String(maxRecords) })
  const payload = await request<{ trace: AspectEvidenceTrace }>(
    `/api/events/${encodeURIComponent(eventId)}/evidence-trace?${query}`,
  )
  return payload.trace
}

export async function fetchRsiEvidence(input: {
  eventId: string
  annotationId?: string | null
  period?: number
  levels?: number[]
}): Promise<RsiEvidence> {
  const payload = await request<{ evidence: RsiEvidence }>('/api/rsi/evidence', {
    method: 'POST',
    body: JSON.stringify(input),
  })
  return payload.evidence
}

export async function fetchMarketSynthesisHealth(): Promise<MarketSynthesisHealth> {
  const payload = await request<{ marketSynthesis: MarketSynthesisHealth }>('/api/market-synthesis/health')
  return payload.marketSynthesis
}

export async function analyzeWithMarketSynthesis(input: {
  eventId: string
  annotationId?: string | null
  question: string
  period: number
  levels: number[]
  inputs: { astrology: boolean; candlesticks: boolean; rsi: boolean }
}): Promise<MarketSynthesisDraft> {
  const payload = await request<{ draft: MarketSynthesisDraft }>('/api/market-synthesis/analyze', {
    method: 'POST',
    body: JSON.stringify(input),
  })
  return payload.draft
}

export async function analyzeWithLocalCandlestick(input: {
  eventId: string
  annotationId?: string | null
  question: string
}): Promise<LocalCandlestickDraft> {
  const payload = await request<{ draft: LocalCandlestickDraft }>('/api/local-candlestick/analyze', {
    method: 'POST',
    body: JSON.stringify(input),
  })
  return payload.draft
}

export async function saveReviewStatus(
  eventId: string,
  status: 'pending' | 'reviewed',
): Promise<EventDetail['event']> {
  const payload = await request<{ event: EventDetail['event'] }>(
    `/api/events/${encodeURIComponent(eventId)}/review`,
    { method: 'POST', body: JSON.stringify({ status }) },
  )
  return payload.event
}

export async function saveAnnotation(draft: AnnotationDraft | ChartAnnotation): Promise<ChartAnnotation> {
  const payload = await request<{ annotation: ChartAnnotation }>('/api/annotations', {
    method: 'POST',
    body: JSON.stringify(draft),
  })
  return payload.annotation
}

export async function deleteAnnotation(annotationId: string): Promise<void> {
  await request<Record<string, never>>(`/api/annotations/${encodeURIComponent(annotationId)}`, {
    method: 'DELETE',
  })
}

export async function saveSnapshot(dataUrl: string): Promise<string> {
  const payload = await request<{ path: string }>('/api/snapshots', {
    method: 'POST',
    body: JSON.stringify({ dataUrl }),
  })
  return payload.path
}

export async function fetchCodexContext(eventId: string, annotationId?: string | null) {
  const query = new URLSearchParams({ eventId })
  if (annotationId) query.set('annotationId', annotationId)
  const payload = await request<{ context: Record<string, unknown> }>(`/api/codex/context?${query}`)
  return payload.context
}

export async function fetchCodexThread(scopeKey: string): Promise<string | null> {
  const query = new URLSearchParams({ scopeKey })
  const payload = await request<{ threadId: string | null }>(`/api/codex/thread?${query}`)
  return payload.threadId
}

export async function saveCodexThread(scopeKey: string, threadId: string): Promise<void> {
  await request<Record<string, never>>('/api/codex/thread', {
    method: 'POST',
    body: JSON.stringify({ scopeKey, threadId }),
  })
}

export async function sendCodexMessage(input: {
  threadId: string | null
  message: string
  context: Record<string, unknown>
  imagePath?: string | null
}): Promise<{ threadId: string; response: string }> {
  const payload = await request<{ threadId: string; response: string }>('/codex-api/chat', {
    method: 'POST',
    body: JSON.stringify(input),
  })
  return payload
}

export async function codexBridgeHealth(): Promise<boolean> {
  try {
    await request<{ bridge: string }>('/codex-api/health')
    return true
  } catch {
    return false
  }
}

export async function fetchChakraLabSnapshot(
  input: ChakraLabRequest,
): Promise<ChakraLabSnapshot> {
  if (isTauriRuntime() && !getCompanionSession()) {
    const { invoke } = await import('@tauri-apps/api/core')
    const payload = await invoke<ApiEnvelope<{ snapshot: ChakraLabSnapshot }>>(
      'chakra_lab_snapshot',
      { request: input },
    )
    if (!payload.ok) {
      throw new Error(payload.error || 'Chakra Lab request failed')
    }
    if (payload.snapshot.guardrails.execution_allowed) {
      throw new Error('Chakra Lab response violated the execution lock')
    }
    return payload.snapshot
  }
  const payload = await request<{ snapshot: ChakraLabSnapshot }>(
    '/api/chakra-lab/snapshot',
    {
      method: 'POST',
      body: JSON.stringify(input),
    },
  )
  return payload.snapshot
}

export async function fetchTrailokyaSourceOnlyGeometry(
  input: ChakraLabRequest,
): Promise<TrailokyaSourceOnlyGeometry> {
  if (isTauriRuntime() && !getCompanionSession()) {
    const { invoke } = await import('@tauri-apps/api/core')
    const payload = await invoke<ApiEnvelope<{ geometry: TrailokyaSourceOnlyGeometry }>>(
      'chakra_lab_trailokya_source_only_geometry',
      { request: input },
    )
    if (!payload.ok) throw new Error(payload.error || 'Trailokya source-only geometry request failed')
    if (payload.geometry.guardrails.executionAllowed) {
      throw new Error('Trailokya geometry response violated the execution lock')
    }
    return payload.geometry
  }
  const payload = await request<{ geometry: TrailokyaSourceOnlyGeometry }>(
    '/api/chakra-lab/trailokya-source-only-geometry',
    { method: 'POST', body: JSON.stringify(input) },
  )
  return payload.geometry
}

export async function fetchChartConditionedPolarityLookup(input: {
  instrumentIdentity: string
  chartId?: string | null
  transitBody?: string | null
  natalTarget?: string | null
  aspectType?: string | null
}): Promise<ChartConditionedPolarityLookup> {
  const payload = await request<{ lookup: ChartConditionedPolarityLookup }>(
    '/api/chart-conditioned-polarity/lookup',
    {
      method: 'POST',
      body: JSON.stringify(input),
    },
  )
  if (payload.lookup.guardrails.executionAllowed || payload.lookup.guardrails.actsAsSbcConfirmation) {
    throw new Error('Chart-conditioned polarity response violated the research-only guardrails')
  }
  return payload.lookup
}

export async function fetchSynchronizedIndependentRange(
  input: SynchronizedIndependentRangeRequest,
): Promise<SynchronizedIndependentRange> {
  if (isTauriRuntime() && !getCompanionSession()) {
    const { invoke } = await import('@tauri-apps/api/core')
    const payload = await invoke<ApiEnvelope<{ range: SynchronizedIndependentRange }>>(
      'synchronized_independent_range',
      { request: input },
    )
    if (!payload.ok) {
      throw new Error(payload.error || 'Synchronized field request failed')
    }
    if (
      payload.range.guardrails.executionAllowed
      || payload.range.guardrails.fieldsFused
      || payload.range.guardrails.marketDirectionInferred
    ) {
      throw new Error('Synchronized field response violated the research-only guardrails')
    }
    return payload.range
  }
  const payload = await request<{ range: SynchronizedIndependentRange }>(
    '/api/independent-fields/synchronized-range',
    {
      method: 'POST',
      body: JSON.stringify(input),
    },
  )
  if (
    payload.range.guardrails.executionAllowed
    || payload.range.guardrails.fieldsFused
    || payload.range.guardrails.marketDirectionInferred
  ) {
    throw new Error('Synchronized field response violated the research-only guardrails')
  }
  return payload.range
}

export async function fetchBphsClassicalCalendarRange(
  input: BphsClassicalCalendarRangeRequest,
): Promise<BphsClassicalCalendarRange> {
  if (isTauriRuntime() && !getCompanionSession()) {
    const { invoke } = await import('@tauri-apps/api/core')
    const payload = await invoke<ApiEnvelope<{ calendar: BphsClassicalCalendarRange }>>(
      'bphs_classical_calendar_range',
      { request: input },
    )
    if (!payload.ok) throw new Error(payload.error || 'BPHS classical calendar request failed')
    return payload.calendar
  }
  const payload = await request<{ calendar: BphsClassicalCalendarRange }>(
    '/api/research/bphs/classical-calendar-range',
    { method: 'POST', body: JSON.stringify(input) },
  )
  return payload.calendar
}

export async function fetchFxSidePilotStatus(): Promise<FxSidePilotStatus> {
  if (isTauriRuntime() && !getCompanionSession()) {
    const { invoke } = await import('@tauri-apps/api/core')
    const payload = await invoke<ApiEnvelope<{ status: FxSidePilotStatus }>>(
      'fx_side_pilot_status',
      { request: {} },
    )
    if (!payload.ok) {
      throw new Error(payload.error || 'FX side pilot status request failed')
    }
    assertFxSidePilotGuardrails(payload.status)
    return payload.status
  }
  const payload = await request<{ status: FxSidePilotStatus }>(
    '/api/independent-fields/pilot-status',
    { method: 'POST', body: JSON.stringify({}) },
  )
  assertFxSidePilotGuardrails(payload.status)
  return payload.status
}

function assertFxSidePilotGuardrails(status: FxSidePilotStatus): void {
  if (
    status.guardrails.executionAllowed
    || status.guardrails.createsCatalogueEntry
    || status.guardrails.marketDirectionInferred
    || status.guardrails.fieldsFused
  ) {
    throw new Error('FX side pilot status violated the research-only guardrails')
  }
}

export async function fetchFounderReviewWorkbench(): Promise<FounderReviewWorkbench> {
  const payload = await request<{ workbench: FounderReviewWorkbench }>('/api/founder-review/workbench')
  return payload.workbench
}

export async function exportFounderReviewPacket(input: FounderReviewExportRequest): Promise<FounderReviewExportResult> {
  const payload = await request<{ export: FounderReviewExportResult }>('/api/founder-review/export', {
    method: 'POST',
    body: JSON.stringify(input),
  })
  return payload.export
}

export async function fetchChakraLabAudit(
  input: ChakraLabAuditRequest,
): Promise<ChakraLinkedAuditView> {
  if (isTauriRuntime() && !getCompanionSession()) {
    const { invoke } = await import('@tauri-apps/api/core')
    const payload = await invoke<ApiEnvelope<{ audit: ChakraLinkedAuditView }>>(
      'chakra_lab_audit',
      { request: input },
    )
    if (!payload.ok) {
      throw new Error(payload.error || 'Chakra Lab audit request failed')
    }
    if (payload.audit.guardrails.execution_allowed) {
      throw new Error('Chakra Lab audit response violated the execution lock')
    }
    return payload.audit
  }
  const payload = await request<{ audit: ChakraLinkedAuditView }>(
    '/api/chakra-lab/audit',
    {
      method: 'POST',
      body: JSON.stringify(input),
    },
  )
  return payload.audit
}

export async function fetchChakraLabFixedPhasor(
  input: ChakraLabAuditRequest,
): Promise<ChakraFixedPhasorSeries> {
  if (isTauriRuntime() && !getCompanionSession()) {
    const { invoke } = await import('@tauri-apps/api/core')
    const payload = await invoke<ApiEnvelope<{ phasor: ChakraFixedPhasorSeries }>>(
      'chakra_lab_fixed_phasor',
      { request: input },
    )
    if (!payload.ok) {
      throw new Error(payload.error || 'Chakra Lab fixed phasor request failed')
    }
    if (payload.phasor.guardrails.execution_allowed) {
      throw new Error('Fixed phasor response violated the execution lock')
    }
    return payload.phasor
  }
  const payload = await request<{ phasor: ChakraFixedPhasorSeries }>(
    '/api/chakra-lab/fixed-phasor',
    {
      method: 'POST',
      body: JSON.stringify(input),
    },
  )
  if (payload.phasor.guardrails.execution_allowed) {
    throw new Error('Fixed phasor response violated the execution lock')
  }
  return payload.phasor
}

export async function fetchChakraTimingProfileAdmission(
  profile: unknown | null = null,
): Promise<ChakraTimingProfileAdmissionReport> {
  const admissionRequest = { profile }
  if (isTauriRuntime() && !getCompanionSession()) {
    const { invoke } = await import('@tauri-apps/api/core')
    const payload = await invoke<
      ApiEnvelope<{ admission: ChakraTimingProfileAdmissionReport }>
    >(
      'chakra_lab_timing_profile_admission',
      { request: admissionRequest },
    )
    if (!payload.ok) {
      throw new Error(payload.error || 'Timing profile admission request failed')
    }
    if (payload.admission.guardrails.execution_allowed) {
      throw new Error('Timing profile admission violated the execution lock')
    }
    return payload.admission
  }
  const payload = await request<{
    admission: ChakraTimingProfileAdmissionReport
  }>(
    '/api/chakra-lab/timing-profile/admission',
    {
      method: 'POST',
      body: JSON.stringify(admissionRequest),
    },
  )
  if (payload.admission.guardrails.execution_allowed) {
    throw new Error('Timing profile admission violated the execution lock')
  }
  return payload.admission
}

export async function fetchChakraTimingSourcePacketReadiness(
  profile: unknown | null = null,
  packet: unknown | null = null,
): Promise<ChakraTimingProfileSourceReadinessReport> {
  const readinessRequest = { profile, packet }
  if (isTauriRuntime() && !getCompanionSession()) {
    const { invoke } = await import('@tauri-apps/api/core')
    const payload = await invoke<
      ApiEnvelope<{ readiness: ChakraTimingProfileSourceReadinessReport }>
    >(
      'chakra_lab_timing_source_packet_readiness',
      { request: readinessRequest },
    )
    if (!payload.ok) {
      throw new Error(payload.error || 'Timing source packet readiness request failed')
    }
    if (payload.readiness.guardrails.execution_allowed) {
      throw new Error('Timing source packet readiness violated the execution lock')
    }
    return payload.readiness
  }
  const payload = await request<{
    readiness: ChakraTimingProfileSourceReadinessReport
  }>(
    '/api/chakra-lab/timing-profile/source-packet/readiness',
    {
      method: 'POST',
      body: JSON.stringify(readinessRequest),
    },
  )
  if (payload.readiness.guardrails.execution_allowed) {
    throw new Error('Timing source packet readiness violated the execution lock')
  }
  return payload.readiness
}

export async function fetchChakraTimingSourceVerification(
  profile: unknown | null,
  packet: unknown | null,
  sourcePayloads: Record<string, string> | null,
  excerptPayloads: Record<string, string> | null,
): Promise<ChakraTimingProfileSourceVerificationReport> {
  const verificationRequest = {
    profile,
    packet,
    sourcePayloads,
    excerptPayloads,
  }
  if (isTauriRuntime() && !getCompanionSession()) {
    const { invoke } = await import('@tauri-apps/api/core')
    const payload = await invoke<
      ApiEnvelope<{ verification: ChakraTimingProfileSourceVerificationReport }>
    >(
      'chakra_lab_timing_source_verification',
      { request: verificationRequest },
    )
    if (!payload.ok) {
      throw new Error(payload.error || 'Timing source verification request failed')
    }
    if (payload.verification.guardrails.execution_allowed) {
      throw new Error('Timing source verification violated the execution lock')
    }
    return payload.verification
  }
  const payload = await request<{
    verification: ChakraTimingProfileSourceVerificationReport
  }>(
    '/api/chakra-lab/timing-profile/source-packet/verify-bytes',
    {
      method: 'POST',
      body: JSON.stringify(verificationRequest),
    },
  )
  if (payload.verification.guardrails.execution_allowed) {
    throw new Error('Timing source verification violated the execution lock')
  }
  return payload.verification
}

export async function fetchChakraTimingExternalReview(
  reviewBundle: unknown | null,
  attestation: unknown | null,
): Promise<ChakraTimingProfileExternalReviewReport> {
  const reviewRequest = {
    reviewBundle,
    attestation,
  }
  if (isTauriRuntime() && !getCompanionSession()) {
    const { invoke } = await import('@tauri-apps/api/core')
    const payload = await invoke<
      ApiEnvelope<{ review: ChakraTimingProfileExternalReviewReport }>
    >(
      'chakra_lab_timing_external_review',
      { request: reviewRequest },
    )
    if (!payload.ok) {
      throw new Error(payload.error || 'Timing external review request failed')
    }
    if (payload.review.guardrails.execution_allowed) {
      throw new Error('Timing external review violated the execution lock')
    }
    return payload.review
  }
  const payload = await request<{
    review: ChakraTimingProfileExternalReviewReport
  }>(
    '/api/chakra-lab/timing-profile/external-review/verify',
    {
      method: 'POST',
      body: JSON.stringify(reviewRequest),
    },
  )
  if (payload.review.guardrails.execution_allowed) {
    throw new Error('Timing external review violated the execution lock')
  }
  return payload.review
}

export async function fetchChakraTimingSignedReview(
  reviewBundle: unknown | null,
  attestation: unknown | null,
  signedReview: unknown | null,
): Promise<ChakraTimingProfileSignedReviewReport> {
  const reviewRequest = {
    reviewBundle,
    attestation,
    signedReview,
  }
  if (isTauriRuntime() && !getCompanionSession()) {
    const { invoke } = await import('@tauri-apps/api/core')
    const payload = await invoke<
      ApiEnvelope<{ review: ChakraTimingProfileSignedReviewReport }>
    >(
      'chakra_lab_timing_signed_review',
      { request: reviewRequest },
    )
    if (!payload.ok) {
      throw new Error(payload.error || 'Timing signed review request failed')
    }
    if (payload.review.guardrails.execution_allowed) {
      throw new Error('Timing signed review violated the execution lock')
    }
    return payload.review
  }
  const payload = await request<{
    review: ChakraTimingProfileSignedReviewReport
  }>(
    '/api/chakra-lab/timing-profile/signed-review/verify',
    {
      method: 'POST',
      body: JSON.stringify(reviewRequest),
    },
  )
  if (payload.review.guardrails.execution_allowed) {
    throw new Error('Timing signed review violated the execution lock')
  }
  return payload.review
}

export async function fetchChakraTimingSourceCertification(
  reviewBundle: unknown | null,
  attestation: unknown | null,
  signedReview: unknown | null,
  sourceCertificate: unknown | null,
): Promise<ChakraTimingProfileSourceCertificationReport> {
  const certificationRequest = {
    reviewBundle,
    attestation,
    signedReview,
    sourceCertificate,
  }
  if (isTauriRuntime() && !getCompanionSession()) {
    const { invoke } = await import('@tauri-apps/api/core')
    const payload = await invoke<
      ApiEnvelope<{
        certification: ChakraTimingProfileSourceCertificationReport
      }>
    >(
      'chakra_lab_timing_source_certification',
      { request: certificationRequest },
    )
    if (!payload.ok) {
      throw new Error(
        payload.error || 'Timing source certification request failed',
      )
    }
    if (payload.certification.guardrails.execution_allowed) {
      throw new Error('Timing source certification violated the execution lock')
    }
    return payload.certification
  }
  const payload = await request<{
    certification: ChakraTimingProfileSourceCertificationReport
  }>(
    '/api/chakra-lab/timing-profile/source-certification/verify',
    {
      method: 'POST',
      body: JSON.stringify(certificationRequest),
    },
  )
  if (payload.certification.guardrails.execution_allowed) {
    throw new Error('Timing source certification violated the execution lock')
  }
  return payload.certification
}

export async function buildChakraLabAuditPackage(
  input: ChakraAuditPackageRequest,
): Promise<ChakraAuditPackageBuild> {
  if (isTauriRuntime() && !getCompanionSession()) {
    const { invoke } = await import('@tauri-apps/api/core')
    const payload = await invoke<ApiEnvelope<ChakraAuditPackageBuild>>(
      'chakra_lab_audit_package',
      { request: input },
    )
    if (!payload.ok) {
      throw new Error(payload.error || 'Chakra Lab audit package request failed')
    }
    if (payload.package.guardrails.execution_allowed) {
      throw new Error('Audit package response violated the execution lock')
    }
    return {
      package: payload.package,
      htmlReport: payload.htmlReport,
    }
  }
  const payload = await request<ChakraAuditPackageBuild>(
    '/api/chakra-lab/audit-package',
    {
      method: 'POST',
      body: JSON.stringify(input),
    },
  )
  if (payload.package.guardrails.execution_allowed) {
    throw new Error('Audit package response violated the execution lock')
  }
  return payload
}

export async function verifyChakraLabAuditPackage(
  input: ChakraReproducibleAuditPackage,
): Promise<ChakraAuditPackageVerification> {
  if (isTauriRuntime() && !getCompanionSession()) {
    const { invoke } = await import('@tauri-apps/api/core')
    const payload = await invoke<ApiEnvelope<{
      verification: ChakraAuditPackageVerification
    }>>(
      'chakra_lab_verify_audit_package',
      { request: { package: input } },
    )
    if (!payload.ok) {
      throw new Error(payload.error || 'Audit package verification failed')
    }
    return payload.verification
  }
  const payload = await request<{
    verification: ChakraAuditPackageVerification
  }>(
    '/api/chakra-lab/audit-package/verify',
    {
      method: 'POST',
      body: JSON.stringify({ package: input }),
    },
  )
  return payload.verification
}

export async function buildChakraLabAuditCatalog(
  input: ChakraAuditCatalogRequest,
): Promise<ChakraAuditCatalogBuild> {
  if (isTauriRuntime() && !getCompanionSession()) {
    const { invoke } = await import('@tauri-apps/api/core')
    const payload = await invoke<ApiEnvelope<ChakraAuditCatalogBuild>>(
      'chakra_lab_audit_catalog',
      { request: input },
    )
    if (!payload.ok) {
      throw new Error(payload.error || 'Audit catalog request failed')
    }
    if (payload.bundle.catalog.guardrails.execution_allowed) {
      throw new Error('Audit catalog response violated the execution lock')
    }
    return {
      bundle: payload.bundle,
      verification: payload.verification,
      signingIdentity: payload.signingIdentity,
    }
  }
  const payload = await request<ChakraAuditCatalogBuild>(
    '/api/chakra-lab/audit-catalog',
    {
      method: 'POST',
      body: JSON.stringify(input),
    },
  )
  if (payload.bundle.catalog.guardrails.execution_allowed) {
    throw new Error('Audit catalog response violated the execution lock')
  }
  return payload
}

export async function verifyChakraLabAuditCatalog(
  bundle: ChakraSignedAuditCatalogBundle,
  fullReplay = true,
): Promise<ChakraAuditCatalogVerification> {
  const input = { bundle, fullReplay }
  if (isTauriRuntime() && !getCompanionSession()) {
    const { invoke } = await import('@tauri-apps/api/core')
    const payload = await invoke<ApiEnvelope<{
      verification: ChakraAuditCatalogVerification
    }>>(
      'chakra_lab_verify_audit_catalog',
      { request: input },
    )
    if (!payload.ok) {
      throw new Error(payload.error || 'Audit catalog verification failed')
    }
    return payload.verification
  }
  const payload = await request<{
    verification: ChakraAuditCatalogVerification
  }>(
    '/api/chakra-lab/audit-catalog/verify',
    {
      method: 'POST',
      body: JSON.stringify(input),
    },
  )
  return payload.verification
}
