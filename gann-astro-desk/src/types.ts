export type ChartTool =
  | 'select'
  | 'crosshair'
  | 'annotation'
  | 'horizontal'
  | 'vertical'
  | 'gann'
  | 'fibonacci'

export type ChartDataSource = 'research' | 'live'

export type WorkspacePreferences = {
  inspectorOpen: boolean
  bottomOpen: boolean
  showAspects: boolean
  showSrLines: boolean
}

export type ChartWorkspaceKind = 'main' | 'analysis'

export type ChartDrawingType =
  | 'horizontal_line'
  | 'vertical_line'
  | 'gann_fan'
  | 'fibonacci_retracement'
  | 'square_of_nine'

export type ChartDrawingAnchor = {
  timeUtc: string
  price: number
}

export type ChartDrawingStyle = {
  color: string
  lineWidth: number
  lineStyle: 'solid' | 'dashed' | 'dotted'
  opacity: number
}

export type SquareOfNineSettings = {
  centerValue: number
  increment: number
  rings: number
  numberRotation: 'clockwise' | 'counterclockwise'
  angleRotation: 'clockwise' | 'counterclockwise'
  angleOffsetDeg: number
  highlightedAngles: number[]
  showCardinals: boolean
  showDiagonals: boolean
  showLabels: boolean
  showPriceProjections: boolean
  showTimeProjections: boolean
}

export type SquareOfNineDataType = 'price' | 'time' | 'date' | 'datetime'

export type SquareOfNineIncrementUnit =
  | 'minute'
  | 'hour'
  | 'day'
  | 'week'
  | 'month'
  | 'trading_day'

export type SquareOfNineMarkKind = 'selected' | 'high' | 'low' | 'forecast' | 'error'

export type SquareOfNineMark = {
  kind: SquareOfNineMarkKind
  note: string
}

export type SquareOfNineWorkspaceState = {
  contract: 'GANN_SQUARE_OF_NINE_WORKSPACE_V1'
  schemaVersion: 1
  dataType: SquareOfNineDataType
  firstPrice: number
  firstDate: string
  firstTime: string
  increment: number
  incrementUnit: SquareOfNineIncrementUnit
  size: number
  zoomPercent: number
  numberRotation: 'clockwise' | 'counterclockwise'
  angleRotation: 'clockwise' | 'counterclockwise'
  angleOffsetDeg: number
  showOrdinals: boolean
  showAngles: boolean
  activeMarkMode: 'select' | Exclude<SquareOfNineMarkKind, 'selected'>
  selectedCellOrdinal: number
  marks: Record<string, SquareOfNineMark>
}

export type GannFanSettings = {
  ratios: number[]
}

export type FibonacciSettings = {
  levels: number[]
  showLabels: boolean
  showPrices: boolean
  extendLines: boolean
}

export type ChartDrawing = {
  contract: 'GANN_RESEARCH_CHART_DRAWING_V1'
  schemaVersion: 1
  drawingId: string
  type: ChartDrawingType
  name: string
  visible: boolean
  locked: boolean
  zIndex: number
  anchors: ChartDrawingAnchor[]
  style: ChartDrawingStyle
  settings: Partial<SquareOfNineSettings & GannFanSettings & FibonacciSettings> & Record<string, unknown>
  guardrails: {
    researchOnly: true
    consumedByLiveInference: false
    consumedByShadowLedger: false
    executionAllowed: false
  }
}

export type ChartLayoutState = {
  visibleStartUtc?: string
  visibleEndUtc?: string
  showAspects: boolean
  showSrLines: boolean
  squareOfNine?: SquareOfNineWorkspaceState
}

export type ChartLayout = {
  contract: 'GANN_CHART_LAYOUT_V1'
  schemaVersion: 1
  layoutId: string
  name: string
  workspaceKind: ChartWorkspaceKind
  symbol: string
  timeframe: string
  familyKey: string
  revision: number
  isDefault: boolean
  autosave: boolean
  chartState: ChartLayoutState
  drawings: ChartDrawing[]
  createdAtUtc: string
  updatedAtUtc: string
}

export type DrawingTemplate = {
  contract: 'GANN_DRAWING_TEMPLATE_V1'
  schemaVersion: 1
  templateId: string
  name: string
  drawingType: ChartDrawingType
  style: ChartDrawingStyle
  settings: Record<string, unknown>
  createdAtUtc: string
  updatedAtUtc: string
}

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
  priceSourceId: string
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

export type PriceSource = {
  priceSourceId: string
  label: string
  symbol: string
  sourceTimeframe: 'AUTO' | 'M30' | 'H1'
  pricePath: string
  manifestPath: string
  sourceSnapshotId: string | null
  priceSha256: string
  contract: string
  barCount: number
  dateStart: string
  dateEnd: string
  asOfUtc: string
  createdAtUtc: string | null
  builtIn: boolean
  verified: boolean
  validationError?: string
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
    priceSources: PriceSource[]
  }
  dataRanges: Partial<Record<ChartParameters['timeframe'], { start: string; end: string }>>
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
  promotedPriceSourceId?: string | null
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

export type DecisionPacket = {
  contract: 'GANN_TIMESTAMP_SAFE_DECISION_PACKET_V1'
  packetId: string
  engineVersion: string
  policyVersion: string
  mode: 'research_replay' | 'live_inference'
  status: 'watch' | 'abstain' | 'observed_replay'
  symbol: string
  eventId: string
  caseId: number | null
  familyKey: string
  times: {
    eventWindowStart: string
    eventWindowEnd: string
    decisionDeadline?: string
    signalTime: string | null
    decisionTime: string
    fillTime: string | null
    exitTime: string | null
    labelAvailableTime: string | null
    evidenceCutoff: string
    sourceDataMaxTime: string | null
  }
  decision: {
    action: 'WATCH_LONG' | 'WATCH_SHORT' | 'ABSTAIN'
    direction: 'bullish' | 'bearish' | 'abstain'
    directionSource: string
    confidence: string
    reason: string
  }
  entry: { state: string; rule: string | null; time: string | null; price: number | null }
  exit: { state: string; rule: string | null; time: string | null; price: number | null }
  outcome: null | { label: string; signedPips: number | null; rawPips: number | null }
  evidence?: Record<string, string | number | boolean | null>
  priceAudit?: {
    closedBarCount: number
    futureOrUnclosedBarsExcluded: number
    sourceDataMaxTime: string | null
    firstClosedBarOpenTime: string | null
    lastClosedBarOpenTime: string | null
  }
  featureAudit: {
    allowlistVersion: string | null
    consumedFields: string[]
    contextFields?: string[]
    forbiddenFieldsPresentButExcluded: string[]
    inputFingerprint: string
  }
  guardrails: {
    timestampSafe: boolean
    noLookahead: boolean
    outcomeLabelConsumed: boolean
    futurePricesConsumed: boolean
    liveEligible: boolean
    executionAllowed: false
    violations: string[]
  }
  policyLocks?: {
    mt5Execution: string
    automaticOrderPlacement: boolean
    reviewRulesApplied: string[]
    purgedValidationRequired: boolean
    prospectiveValidationRequired: boolean
    historicalValidationContract: string
    historicalValidationStatus: string
    historicalValidationReport: string
    externalAstrologyCertificationRequired: boolean
  }
  provenance: Record<string, string | number | boolean | null | undefined>
}

export type ShadowLedgerRecord = {
  shadowId: string
  eventId: string
  familyKey: string
  symbol: string
  timeframe: string
  action: 'WATCH_LONG' | 'WATCH_SHORT' | 'ABSTAIN'
  direction: 'bullish' | 'bearish' | 'abstain'
  capturedAtUtc: string
  decisionTimeUtc: string
  anchorTimeUtc: string
  anchorClose: number
  labelDueTimeUtc: string
  status: 'pending_72h' | 'settled'
  observedDirection: 'UP' | 'DOWN' | 'FLAT' | null
  rawReturnPct: number | null
  signedReturnPct: number | null
  hit: boolean | null
  packetId: string
  executionOccurred: false
}

export type ShadowTrialCohort = {
  trialId: string
  decisionContract: string
  packetContract: string
  engineVersion: string
  policyVersion: string
  astronomyContract: string
  symbol: string
  timeframe: string
  outcomeContract: string
  horizonHours: number
  gateConfigurationSha256: string
  decisionCount: number
  settledDecisionCount: number
  pendingOutcomeCount: number
  firstCapturedAtUtc: string
  lastCapturedAtUtc: string
}

export type ShadowTrialSummary = {
  contract: 'GANN_FROZEN_PROSPECTIVE_SHADOW_TRIAL_V1'
  status: 'awaiting_first_decision' | 'frozen_policy_cohort' | 'mixed_policy_cohorts_blocked'
  trialId: string | null
  policyLocked: boolean
  integrityValid: boolean
  cohortCount: number
  decisionContract?: string
  packetContract?: string
  engineVersion?: string
  policyVersion?: string
  astronomyContract?: string
  symbol?: string
  timeframe?: string
  outcomeContract?: string
  horizonHours?: number
  gateConfiguration: {
    minimumWatchClusters: number
    minimumCoverage: number
    wilsonLowerMustExceed: number
    twoSidedPBelow: number
    meanSignedReturnMustExceedPct: number
    minimumCalendarMonths: number
  }
  gateConfigurationSha256: string
  manifestIdentitySha256?: string | null
  establishedAtUtc?: string | null
  seedShadowId?: string | null
  manifestSource?: string | null
  firstCapturedAtUtc: string | null
  lastCapturedAtUtc: string | null
  nextOutcomeDueTimeUtc: string | null
  lastOutcomeDueTimeUtc: string | null
  dueOutcomeCount: number
  notYetDueOutcomeCount: number
  observedAtUtc: string
  progress?: {
    watchClusters: { current: number; target: number }
    calendarMonths: { current: number; target: number }
    coverage: { current: number | null; minimum: number }
  }
  cohorts: ShadowTrialCohort[]
}

export type ShadowLedgerSnapshot = {
  summary: {
    contract: 'GANN_APPEND_ONLY_SHADOW_LEDGER_V1'
    gateStatus: string
    decisionCount: number
    watchDecisionCount: number
    abstainDecisionCount: number
    settledDecisionCount: number
    pendingOutcomeCount: number
    settledClusterCount: number
    watchClusterCount: number
    directionalHits: number
    hitRate: number | null
    coverage: number | null
    wilson95Lower: number | null
    wilson95Upper: number | null
    twoSidedBinomialP: number | null
    meanSigned72hReturnPct: number | null
    calendarMonthCount: number
    criteria: Record<string, boolean>
    executionAllowed: false
    trial: ShadowTrialSummary
    chain: {
      valid: boolean
      entryCount: number
      headHash?: string
      error: string
    }
  }
  records: ShadowLedgerRecord[]
  supervisor: {
    state: 'starting' | 'paused' | 'waiting' | 'collecting' | 'error'
    lastScanAtUtc: string | null
    lastCaptureCount: number
    lastSettlementCount: number
    lastError: string
    readiness: {
      ready: boolean
      code: string
      artifactId?: string
      timeframe?: string
      sourceAsOfUtc?: string
      maximumAgeSeconds?: number
    }
  }
  refresh?: ProspectiveRefreshStatus
}

export type ProspectiveRefreshRun = {
  runId: string
  contract: 'GANN_PROSPECTIVE_ARTIFACT_REFRESH_V1'
  sourceBarOpenUtc: string
  sourceBarCloseUtc: string
  status: string
  stage: string
  message: string
  sourceSnapshotId: string | null
  priceSourceId: string | null
  generationJobId: string | null
  artifactId: string | null
  parameters: Record<string, unknown>
  error: string
  createdAtUtc: string
  updatedAtUtc: string
  finishedAtUtc: string | null
}

export type ProspectiveRefreshStatus = {
  contract: 'GANN_PROSPECTIVE_ARTIFACT_REFRESH_V1'
  enabled: boolean
  state: string
  message: string
  lastCheckedAtUtc: string | null
  latestClosedBarUtc: string | null
  activeRun: ProspectiveRefreshRun | null
  recentRuns: ProspectiveRefreshRun[]
  lastError: string
  executionAllowed: false
}

export type BackendRuntimeInfo = {
  contract: 'GANN_ASTRO_TAURI_PYTHON_SIDECAR_V1'
  baseUrl: string
  port: number
  pid: number
  status: string
  executionAllowed: false
  restartCount: number
  recoveryState: 'steady' | 'recovering' | 'recovered'
  startedAtUnixMs: number
  spawnElapsedMs: number
  lastExit: string | null
}

export type RuntimeMetric = {
  name: string
  count: number
  successCount: number
  failureCount: number
  sampleCount: number
  lastMs: number
  averageMs: number
  p50Ms: number
  p95Ms: number
  maxMs: number
  lastAtUtc: string
}

export type RuntimeDiagnosticEvent = {
  atUtc: string
  sessionId: string
  kind: string
  name: string
  durationMs?: number
  details?: Record<string, unknown>
  executionAllowed: false
}

export type RuntimeDiagnostics = {
  contract: 'GANN_RUNTIME_DIAGNOSTICS_V1'
  sessionId: string
  startedAtUtc: string
  uptimeSeconds: number
  startup: {
    totalMs: number
    phasesMs: Record<string, number>
    metadata: Record<string, unknown>
  }
  operations: RuntimeMetric[]
  recentEvents: RuntimeDiagnosticEvent[]
  logPath: string
  guardrails: {
    observabilityOnly: true
    changesInferencePolicy: false
    consumedByLiveInference: false
    consumedByShadowLedger: false
    executionAllowed: false
  }
}

export type RuntimeDiagnosticsBundle = {
  runtime: BackendRuntimeInfo | null
  diagnostics: RuntimeDiagnostics
}

export type LocalJyotishHealth = {
  contract: 'GANN_LOCAL_JYOTISH_RAG_DRAFT_V1'
  ready: boolean
  runtimeReady: boolean
  corpusReady: boolean
  model: string
  availableModels: string[]
  corpusChunks: number
  retrievalPolicy: string
  layerCounts: Record<string, number>
  corpusPath: string
  error: string
  analysisOnly: true
  rawDraftIsOfficial: false
  executionAllowed: false
}

export type LocalJyotishDraft = {
  contract: 'GANN_LOCAL_JYOTISH_RAG_DRAFT_V1'
  draftId: string
  eventId: string
  model: string
  text: string
  citations: Array<{
    sourceId: string
    chunkId: string
    title: string
    layer: 'classical_doctrine' | 'reference_commentary' | 'local_research'
    score: number
  }>
  guardrails: {
    analysisOnly: true
    deterministicEvidenceIsGroundTruth: true
    rawDraftIsOfficial: false
    consumedByLiveInference: false
    consumedByShadowLedger: false
    executionAllowed: false
  }
  verifier: {
    status: 'pass' | 'review_required'
    issues: string[]
    availableCitationIds: string[]
    citedIds: string[]
  }
  disclaimer: string
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
