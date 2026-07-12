export type ChartTool =
  | 'select'
  | 'crosshair'
  | 'annotation'
  | 'horizontal'
  | 'vertical'
  | 'gann'

export type ChartDataSource = 'research' | 'live'

export type ReferenceParameters = {
  label: string
  date: string
  time: string
  utcOffset: string
  latitude: number
  longitude: number
}

export type ChartParameters = {
  symbol: string
  dataSource: ChartDataSource
  timeframe: 'M30' | 'H1' | 'H4' | 'D1'
  start: string
  end: string
  mode: 'TN' | 'TT'
  transitBodies: string[]
  natalBodies: string[]
  aspects: string[]
  excludedFamilyKeys: string[]
  onlyTouched: boolean
  minDurationMinutes: number
  maxDurationMinutes: number | null
  liveBarCount: number
  harmonics: number[]
  nValues: number[]
  degrees: number[]
  epsilon: number
  priceZone: number
  reference: ReferenceParameters
}

export type ParameterSchema = {
  defaults: ChartParameters
  options: {
    symbols: string[]
    timeframes: ChartParameters['timeframe'][]
    modes: Array<{ id: ChartParameters['mode']; label: string; available: boolean }>
    transitBodies: string[]
    natalBodies: string[]
    aspects: string[]
    familyKeys: string[]
  }
  dataRanges: Record<ChartParameters['timeframe'], { start: string; end: string }>
  generation: {
    correctedTn: string
    correctedTt: string
    customSrConfig: string
    profileJobQueue: string
    astronomyContract: string
    activeArtifactId: string
  }
}

export type SavedParameterProfile = {
  profileId: string
  name: string
  parameters: ChartParameters
  isDefault: boolean
  createdAtUtc: string
  updatedAtUtc: string
}

export type GenerationJobStatus =
  | 'queued'
  | 'running'
  | 'cancelling'
  | 'cancelled'
  | 'completed'
  | 'failed'

export type GenerationJob = {
  jobId: string
  label: string
  status: GenerationJobStatus
  stage: string
  progress: number
  message: string
  parameters: ChartParameters
  autoActivate: boolean
  cancelRequested: boolean
  artifactId: string | null
  eventsPath: string
  touchLogPath: string
  logPath: string
  logTail?: string
  error: string
  createdAtUtc: string
  startedAtUtc: string | null
  finishedAtUtc: string | null
  updatedAtUtc: string
}

export type DataArtifact = {
  artifactId: string
  label: string
  symbol: string
  mode: 'TN' | 'TT'
  sourceTimeframe: string
  eventsPath: string
  touchLogPath: string
  pricePath: string
  eventsManifestPath?: string
  artifactManifestPath?: string
  parameters: ChartParameters
  astronomyContract: string
  eventCount: number | null
  touchCount: number | null
  dateStart: string | null
  dateEnd: string | null
  isActive: boolean
  createdAtUtc: string | null
  builtIn: boolean
}

export type Mt5HistorySnapshot = {
  snapshotId: string
  contract: 'MT5_TIMESTAMPED_CLOSED_BARS_V1'
  symbol: string
  timeframe: string
  capturedAtUtc: string
  requestedStartUtc: string
  requestedEndUtc: string
  asOfUtc: string
  futureRequestClamped: boolean
  barCount: number
  firstBarOpenUtc: string
  lastBarOpenUtc: string
  lastBarCloseUtc: string
  incompleteBarsExcluded: number
  noLookahead: true
  immutable: true
  parquetPath: string
  parquetSha256: string
  manifestPath: string
}

export type Candle = {
  time: number
  open: number
  high: number
  low: number
  close: number
  volume: number
}

export type AspectWindow = {
  eventId: string
  caseId: number | null
  familyKey: string
  pairKey: string
  aspect: string
  aspectLabel: string
  transitBody: string
  natalBody: string
  start: number
  end: number
  peak: number
  startIso: string
  endIso: string
  peakIso: string
  durationMinutes: number
  peakOrbDeg: number
  orbLimitDeg: number
  color: string
  lane?: number
  occurrenceIndex: number | null
  occurrenceCount: number
  outcome: 'UP' | 'DOWN' | null
  returnPct: number | null
  reviewed: boolean
  reviewStatus: string
  reviewSource: 'legacy_completed_review' | 'app_progress' | 'none'
  signedPips: number | null
  astronomyContract: string
  sourceGenerator: string
}

export type SrLine = {
  id: string
  price: number
  label: string
  planet: string
  color: string
  eventId?: string
  touchTime?: number
}

export type ChartPayload = {
  symbol: string
  timeframe: string
  start: string
  end: string
  candles: Candle[]
  aspects: AspectWindow[]
  srLines: SrLine[]
  astronomyContract: string
  dataSource: 'corrected_historical' | 'mt5_live'
  parametersApplied: Record<string, unknown>
  artifact: DataArtifact
  generatedAt: string
}

export type FamilySummary = {
  total: number
  reviewed: number
  pending: number
  bullish: number
  bearish: number
  unknown: number
  averageReturnPct: number | null
}

export type AspectFamily = {
  familyKey: string
  pairKey: string
  aspect: string
  transitBody: string
  natalBody: string
  occurrences: AspectWindow[]
  selectedEventId: string
  summary: FamilySummary
  astronomyContract: string
  artifact: DataArtifact
}

export type AstroEvidence = {
  key: string
  label: string
  value: string | number
  unit: string
  certification: 'provisional' | 'observed'
}

export type ChartAnnotation = {
  annotationId: string
  eventId: string
  caseId: number | null
  familyKey: string
  annotationType: string
  anchorTimeUtc: string
  anchorPrice: number | null
  endTimeUtc: string | null
  endPrice: number | null
  targetType: string
  targetId: string
  note: string
  color: string
  chartState: Record<string, unknown>
  createdAtUtc: string
  updatedAtUtc: string
}

export type EventDetail = {
  event: AspectWindow
  chart: ChartPayload
  astroEvidence: AstroEvidence[]
  context: Record<string, unknown>
  annotations: ChartAnnotation[]
}

export type Mt5Status = {
  state: 'starting' | 'disabled' | 'connected' | 'reconnecting'
  symbol: string
  connected: boolean
  tradeAllowed: boolean
  lastError: string
  updatedAt: string
  accountLogin?: number
  server?: string
  company?: string
  bid?: number | null
  ask?: number | null
  lastTickUtc?: string | null
  executionMode?: string
}

export type CodexMessage = {
  id: string
  role: 'user' | 'assistant' | 'system'
  text: string
  annotationId?: string | null
}

export type AnnotationDraft = {
  eventId: string
  familyKey: string
  annotationType: string
  anchorTimeUtc: string
  anchorPrice: number | null
  targetType: string
  targetId: string
  note: string
  color: string
  chartState: Record<string, unknown>
}
