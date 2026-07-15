import type {
  AnnotationDraft,
  AspectFamily,
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
  LocalCandlestickDraft,
  LocalCandlestickHealth,
  LocalJyotishDraft,
  LocalJyotishHealth,
  Mt5HistorySnapshot,
  Mt5Status,
  ParameterSchema,
  PriceSource,
  ProspectiveRefreshStatus,
  RuntimeDiagnosticsBundle,
  SavedParameterProfile,
  ShadowLedgerSnapshot,
  WorkspacePreferences,
} from './types'

type ApiEnvelope<T> = { ok: boolean; error?: string } & T
let backendRuntimePromise: Promise<BackendRuntimeInfo> | null = null

function isTauriRuntime(): boolean {
  return typeof window !== 'undefined' && '__TAURI_INTERNALS__' in window
}

export async function fetchBackendRuntime(force = false): Promise<BackendRuntimeInfo | null> {
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
      if (runtime.executionAllowed) {
        throw new Error('Backend runtime violated the read-only execution lock')
      }
      return runtime
    })
  }
  return backendRuntimePromise
}

async function backendBaseUrl(): Promise<string> {
  const runtime = await fetchBackendRuntime()
  return runtime?.baseUrl.replace(/\/$/, '') ?? ''
}

async function resolveRequestUrl(url: string): Promise<string> {
  const baseUrl = await backendBaseUrl()
  return baseUrl && url.startsWith('/') ? `${baseUrl}${url}` : url
}

function wait(milliseconds: number): Promise<void> {
  return new Promise((resolve) => window.setTimeout(resolve, milliseconds))
}

async function request<T>(url: string, init?: RequestInit): Promise<T> {
  const method = (init?.method ?? 'GET').toUpperCase()
  const attempts = method === 'GET' ? 61 : 1
  let response: Response | null = null
  let networkError: unknown = null
  for (let attempt = 1; attempt <= attempts; attempt += 1) {
    const requestUrl = await resolveRequestUrl(url)
    try {
      response = await fetch(requestUrl, {
        ...init,
        headers: { 'Content-Type': 'application/json', ...(init?.headers ?? {}) },
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

export async function fetchChart(parameters?: ChartParameters): Promise<ChartPayload> {
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
    query.set('minDurationMinutes', String(parameters.minDurationMinutes))
    if (parameters.maxDurationMinutes != null) query.set('maxDurationMinutes', String(parameters.maxDurationMinutes))
    query.set('liveBarCount', String(parameters.liveBarCount))
  }
  const payload = await request<{ chart: ChartPayload }>(`/api/chart?${query}`)
  return payload.chart
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
