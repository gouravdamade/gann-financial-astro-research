export type ChartTool =
  | 'select'
  | 'crosshair'
  | 'replay'
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
export type DrawingMagnetMode = 'off' | 'weak' | 'strong'
export type DrawingSyncScope = 'layout' | 'symbol'
export type ChartDrawingPane = 'price' | 'rsi' | 'global'

export type DrawingPreferences = {
  favoriteTools: ChartTool[]
  magnetMode: DrawingMagnetMode
  keepDrawing: boolean
}

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
  groupId: string | null
  groupName: string
  syncScope: DrawingSyncScope
  pane?: ChartDrawingPane
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

export type RsiPaneSettings = {
  contract: 'GANN_RSI_PANE_SETTINGS_V1'
  visible: boolean
  period: number
  source: 'close'
  timeframe: 'chart'
  levels: number[]
}

export type RsiPoint = {
  time: number
  value: number
}

export type PlanetaryLineMode = 'direct' | 'mirror' | 'both'

export type PlanetaryLineGroup = {
  planet: string
  enabled: boolean
  color: string
  mode: PlanetaryLineMode
  nValues: number[]
  fValues: number[]
  degrees: number[]
}

export type PlanetaryLineOverlaySettings = {
  contract: 'GANN_PLANETARY_LINE_LAB_SETTINGS_V1'
  visible: boolean
  sampleLimit: number
  groups: PlanetaryLineGroup[]
}

export type PlanetaryLinePoint = {
  time: number
  value: number
}

export type PlanetaryLineSeries = {
  id: string
  planet: string
  mode: Exclude<PlanetaryLineMode, 'both'>
  n: number
  f: number
  degree: number
  color: string
  label: string
  points: PlanetaryLinePoint[]
}

export type ResearchEvidenceStatus =
  | 'MEASURED'
  | 'UNKNOWN'
  | 'NOT_APPLICABLE'
  | 'BLOCKED'

export type ResearchEvidenceChannel = {
  status: ResearchEvidenceStatus
  value: number | null
  unit: string | null
  label: string
  reason: string | null
}

export type ResearchEvidencePacket = {
  contract: 'GANN_RESEARCH_EVIDENCE_PACKET_V1'
  sourceFamily: string
  sourceProfileId: string
  calculationVersion: string
  observedAtUnix: number
  role: string
  channels: Record<'direction' | 'activation' | 'conflict' | 'confidence', ResearchEvidenceChannel>
  descriptors: Array<{
    key: string
    label: string
    value: number | string | null
    unit: string | null
    status: string
  }>
  unknownReasons: string[]
  provenance: Record<string, unknown>
  empiricalCoefficient: 0
  guardrails: {
    timestampSafe: true
    researchOnly: true
    consumedByLiveInference: false
    consumedByAutoSuggest: false
    consumedByShadowLedger: false
    consumedByOfficialMlNotes: false
    executionAllowed: false
  }
}

export type PlanetaryCollectiveReliability =
  | 'RELIABLE'
  | 'LOW_COHERENCE'
  | 'UNSTABLE'
  | 'INVALID_INPUT'

export type PlanetaryCollectiveState =
  | 'CONCENTRATED'
  | 'PARTIALLY_COHERENT'
  | 'BIPOLAR'
  | 'DISPERSED'
  | 'UNSTABLE'
  | 'INVALID_INPUT'

export type PlanetaryCollectiveMemberAudit = {
  body: string
  longitudeDeg: number | null
  weight: number
  angularDistanceFromMeanDeg: number | null
  longitudeLeverageDeg: number | null
  coherenceLeverage: number | null
  tempoClass: 'FAST_MOVING_CLASS' | 'SLOW_MOVING_CLASS'
  role: string
  influenceRank: number | null
}

export type PlanetaryCollectiveSample = {
  time: number
  meanLongitudeDeg: number | null
  coherenceR1: number | null
  circularVariance: number | null
  circularStdDeg: number | null
  polarisationR2: number | null
  polarisationAxisDeg: number | null
  state: PlanetaryCollectiveState
  reliability: PlanetaryCollectiveReliability
  longitudeReliable: boolean
  segmentId: number | null
  unwrappedLongitudeDeg: number | null
  velocityDegPerDay: number | null
  accelerationDegPerDay2: number | null
  memberAudit: PlanetaryCollectiveMemberAudit[]
}

export type PlanetaryCollectiveMotion = {
  contract: 'GANN_PLANETARY_COLLECTIVE_MOTION_V1'
  calculationVersion: 'RELIABILITY_SAFE_CIRCULAR_MOTION_V1'
  segmentCount: number
  reliableSampleCount: number
  velocitySampleCount: number
  accelerationSampleCount: number
  velocityDegPerDay: {
    minimum: number | null
    maximum: number | null
  }
  accelerationDegPerDay2: {
    minimum: number | null
    maximum: number | null
  }
  guardrails: {
    reliabilityGapsBreakSegments: true
    usesExactTimestampDifferences: true
    bridgesUnreliableSamples: false
    displaySmoothingApplied: false
    researchOnly: true
    executionAllowed: false
  }
}

export type PlanetaryCollectiveInfluence = {
  contract: 'GANN_PLANETARY_COLLECTIVE_INFLUENCE_V1'
  calculationVersion: 'AVG_ALL_LEAVE_ONE_OUT_AUDIT_V1'
  latestTopLongitudeLeverage: PlanetaryCollectiveMemberAudit | null
  rolePolicy: {
    classification: 'DETERMINISTIC_UI_AUDIT_ONLY'
    fastMovingClass: string[]
    topFastDriverRankLimit: number
    slowAnchorRule: string
  }
  guardrails: {
    researchOnly: true
    countsAsIndependentVote: false
    directionalContribution: 0
    consumedByLiveInference: false
    consumedByAutoSuggest: false
    consumedByShadowLedger: false
    consumedByOfficialMlNotes: false
    executionAllowed: false
  }
}

export type PlanetaryCollectiveEvent = {
  contract: 'GANN_PLANETARY_COLLECTIVE_EVENT_V1'
  eventId: string
  profileId: string
  eventPolicyId: 'AVG_ALL_SAMPLED_EVENTS_V1'
  eventType:
    | 'MEAN_RASHI_INGRESS'
    | 'COHERENCE_THRESHOLD_CROSSING'
    | 'CLUSTER_STATE_TRANSITION'
  estimatedTimeUnix: number
  refinedTimeUnix: number | null
  sourceBracket: {
    startUnix: number
    endUnix: number
  }
  timing:
    | {
        exact: false
        method:
          | 'LINEAR_INTERPOLATION_OF_UNWRAPPED_MEAN'
          | 'LINEAR_INTERPOLATION_OF_R1'
          | 'RIGHT_SAMPLE_STATE_OBSERVATION'
        precision: 'BETWEEN_EXACT_BAR_SAMPLES'
      }
    | {
        exact: true
        method: 'BRACKETED_BISECTION_OF_EPHEMERIS_MEAN'
        precision: 'WITHIN_DECLARED_TIME_AND_ANGULAR_TOLERANCE'
        sampledEstimateUnix: number
        rootToleranceSeconds: number
        residualToleranceDeg: number
      }
  refinement: {
    contract: 'GANN_PLANETARY_COLLECTIVE_EVENT_REFINEMENT_V1'
    policyId: 'AVG_ALL_EPHEMERIS_ROOT_REFINEMENT_V1'
    status: 'REFINED_BRACKETED_ROOT' | 'SAMPLED_FALLBACK'
    sampledEstimateUnix: number
    refinedTimeUnix: number | null
    rootToleranceSeconds: number
    residualToleranceDeg: number
    residualDeg: number | null
    coherenceR1AtRoot: number | null
    iterations: number
    evaluatedTimestampCount: number
    reason: string
    astronomyContract: 'RAMAN_SIDEREAL_SWISSEPH_EPHEMERIS_ROOT_V1'
    guardrails: {
      researchOnly: true
      preservesSampledEstimate: true
      countsAsIndependentVote: false
      directionalContribution: 0
      consumedByLiveInference: false
      consumedByAutoSuggest: false
      consumedByShadowLedger: false
      consumedByOfficialMlNotes: false
      executionAllowed: false
    }
  } | null
  causalClusterId: string
  details: Record<string, unknown>
  guardrails: {
    researchOnly: true
    visualMarkerOnly: true
    timestampSafe: true
    exactEventTime: boolean
    directionalContribution: 0
    castsSbcVedha: false
    consumedByLiveInference: false
    consumedByAutoSuggest: false
    consumedByShadowLedger: false
    consumedByOfficialMlNotes: false
    executionAllowed: false
  }
}

export type PlanetaryCollectiveEventSummary = {
  contract: 'GANN_PLANETARY_COLLECTIVE_EVENT_SUMMARY_V1'
  eventPolicy: {
    profileId: 'AVG_ALL_SAMPLED_EVENTS_V1'
    timingClassification: 'MIXED_SAMPLED_AND_EPHEMERIS_REFINED'
    lowCoherenceFloor: number
    concentratedFloor: number
    detects: string[]
    doesNotDetectYet: string[]
  }
  eventCount: number
  eventTypeCounts: Partial<Record<PlanetaryCollectiveEvent['eventType'], number>>
  refinement: {
    contract: 'GANN_PLANETARY_COLLECTIVE_EVENT_REFINEMENT_V1'
    policyId: 'AVG_ALL_EPHEMERIS_ROOT_REFINEMENT_V1'
    refinableEventTypes: ['MEAN_RASHI_INGRESS']
    candidateCount: number
    candidateBudget: number
    attemptedCount: number
    skippedBudgetCount: number
    refinedCount: number
    fallbackCount: number
    evaluatedTimestampCount: number
    rootToleranceSeconds: number
    residualToleranceDeg: number
    guardrails: {
      researchOnly: true
      heuristicThresholdEventsRemainSampled: true
      countsAsIndependentVote: false
      directionalContribution: 0
      consumedByLiveInference: false
      consumedByAutoSuggest: false
      consumedByShadowLedger: false
      consumedByOfficialMlNotes: false
      executionAllowed: false
    }
  }
  guardrails: {
    sampledTimingOnly: false
    exactRootsLimitedTo: ['MEAN_RASHI_INGRESS']
    prospectiveFreezePerformed: false
    researchOnly: true
    executionAllowed: false
  }
}

export type PlanetaryCollectiveField = {
  contract: 'GANN_PLANETARY_COLLECTIVE_FIELD_V1'
  calculationVersion: string
  profile: {
    profileId: string
    members: string[]
    weights: number[]
    nodePolicy: string
    memberSetHash: string
    thresholdProfile: {
      profileId: string
      classification: 'UI_HEURISTIC_RESEARCH_ONLY'
      unstableResultantFloor: number
      lowCoherenceFloor: number
      concentratedFloor: number
      bipolarR2Floor: number
    }
  }
  samples: PlanetaryCollectiveSample[]
  latest: PlanetaryCollectiveSample
  motion: PlanetaryCollectiveMotion
  influence: PlanetaryCollectiveInfluence
  events: PlanetaryCollectiveEvent[]
  eventSummary: PlanetaryCollectiveEventSummary
  summary: {
    sampleCount: number
    reliabilityCounts: Partial<Record<PlanetaryCollectiveReliability, number>>
    stateCounts: Partial<Record<PlanetaryCollectiveState, number>>
    coherenceR1: {
      minimum: number | null
      median: number | null
      maximum: number | null
    }
    polarisationR2: {
      minimum: number | null
      median: number | null
      maximum: number | null
    }
  }
  evidence: ResearchEvidencePacket
  causalClusterPolicy: {
    profileId: 'PLANETARY_GEOMETRY_CAUSAL_CLUSTER_V1'
    description: string
    countsAsIndependentVote: false
    directionalContribution: 0
  }
  legacyCompatibility: {
    legacyLineFormulaUnchanged: true
    legacyLineValuesPreserved: true
    reliabilityChangesLineVisibility: false
  }
  guardrails: {
    researchOnly: true
    contextOnly: true
    empiricalCoefficient: 0
    traditionalAuthority: false
    castsSbcVedha: false
    directionalContribution: 0
    consumedByLiveInference: false
    consumedByAutoSuggest: false
    consumedByShadowLedger: false
    consumedByOfficialMlNotes: false
    executionAllowed: false
  }
}

export type PlanetaryCollectiveAuditSnapshot = {
  contract: 'GANN_PLANETARY_COLLECTIVE_AUDIT_SNAPSHOT_V1'
  schemaVersion: 1
  snapshotId: string
  createdAtUtc: string
  symbol: string
  timeframe: string
  chartRange: {
    startUtc: string
    endUtc: string
  }
  selectedTimeUnix: number
  fieldCalculationVersion: string
  profile: PlanetaryCollectiveField['profile']
  sample: PlanetaryCollectiveSample
  nearbyEvents: PlanetaryCollectiveEvent[]
  guardrails: {
    researchOnly: true
    immutableEvidenceCopy: true
    countsAsIndependentVote: false
    directionalContribution: 0
    consumedByLiveInference: false
    consumedByAutoSuggest: false
    consumedByShadowLedger: false
    consumedByOfficialMlNotes: false
    executionAllowed: false
  }
}

export type PlanetaryCollectiveVisualStudyDossier = {
  contract: 'GANN_AVG_ALL_VISUAL_STUDY_DOSSIER_V1'
  schemaVersion: 1
  dossierId: string
  createdAtUtc: string
  studyFingerprintSha256: string
  audit: PlanetaryCollectiveAuditSnapshot
  gannStudy: {
    contract: 'GANN_AVG_ALL_GANN_VISUAL_STUDY_V1'
    mode: 'VISIBLE_USER_AUTHORED_FANS'
    fanCount: number
    fans: Array<{
      drawingId: string
      name: string
      anchors: ChartDrawingAnchor[]
      style: ChartDrawingStyle
      ratios: number[]
    }>
    guardrails: {
      geometryOnly: true
      directionalInterpretation: false
      outcomeLabelsIncluded: false
    }
  }
  sbcStudy: {
    contract: 'GANN_AVG_ALL_SBC_VISUAL_STUDY_V1'
    mode: 'TIMESTAMP_MATCHED_FIXED_BODY_CONTEXT'
    actorScope: 'SUN_MOON_RAHU_KETU_ONLY'
    snapshot: ChakraLabSnapshot
    guardrails: {
      avgAllCastsVedha: false
      guidanceOnly: true
      financiallyValidated: false
      outcomeLabelsIncluded: false
    }
  }
  prospectiveFreeze: {
    contract: 'GANN_AVG_ALL_PROSPECTIVE_FREEZE_CANDIDATE_V1'
    policyVersion: 'avg_all_visual_observer_v1'
    status: 'EXPORT_ONLY_NOT_REGISTERED'
    packetFrozen: true
    trialRegistered: false
    evidenceCutoffUtc: string
    outcomeLabelsIncluded: false
    existingShadowTrialModified: false
    requirementsBeforeRegistration: string[]
  }
  guardrails: {
    researchOnly: true
    countsAsIndependentVote: false
    directionalContribution: 0
    consumedByLiveInference: false
    consumedByAutoSuggest: false
    consumedByShadowLedger: false
    consumedByOfficialMlNotes: false
    executionAllowed: false
  }
}

export type PlanetaryLineOverlay = {
  contract: 'GANN_EXPLORATORY_PLANETARY_LINE_OVERLAY_V1'
  symbol: string
  timeframe: string
  astronomyContract: string
  formula: {
    direct: string
    mirror: string
    avgAll: string
  }
  timestampCount: number
  lineCount: number
  pointCount: number
  limits: {
    maxTimestamps: number
    maxLines: number
    maxPoints: number
  }
  collectiveField: PlanetaryCollectiveField | null
  lines: PlanetaryLineSeries[]
  guardrails: {
    researchOnly: true
    curveFitExploration: true
    exactBarTimestamps: true
    consumedByLiveInference: false
    consumedByAutoSuggest: false
    consumedByShadowLedger: false
    executionAllowed: false
  }
  generatedAtUtc: string
}

export type ChartLayoutState = {
  visibleStartUtc?: string
  visibleEndUtc?: string
  showAspects: boolean
  showSrLines: boolean
  drawingPreferences?: DrawingPreferences
  rsi?: RsiPaneSettings
  planetaryLines?: PlanetaryLineOverlaySettings
  squareOfNine?: SquareOfNineWorkspaceState
  collectiveAuditSnapshots?: PlanetaryCollectiveAuditSnapshot[]
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

export type ChartTimeframe = 'M30' | 'H1' | 'H4' | 'D1' | 'W1'

export type ChartParameters = {
  symbol: string
  dataSource: ChartDataSource
  timeframe: ChartTimeframe
  priceSourceId: string
  start: string
  end: string
  mode: 'TN' | 'TT'
  transitBodies: string[]
  natalBodies: string[]
  aspects: string[]
  excludedFamilyKeys: string[]
  onlyTouched: boolean
  aspectDurationMode: 'auto' | 'manual'
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
  contract: 'MT5_TIMESTAMPED_CLOSED_BARS_V1' | 'MT5_TIMESTAMP_NORMALIZED_CLOSED_BARS_V2'
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
  rawFirstBarOpenServerEpochSeconds?: number
  rawLastBarOpenServerEpochSeconds?: number
  timeNormalizationContract?: 'GANN_MT5_SERVER_TIME_NORMALIZATION_V1'
  timeNormalization?: Mt5TimeNormalization
  appExecutionAllowed?: false
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
  knownPriorCount: number
  knownOccurrenceCount: number
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
  replay?: BarReplaySnapshot | null
}

export type BarReplaySnapshot = {
  contract: 'GANN_TIMESTAMP_SAFE_BAR_REPLAY_V1'
  active: true
  cutoffUtc: string
  evidenceCutoff: string
  sourceDataMaxTime: string
  firstCutoffUtc: string
  previousCutoffUtc: string | null
  nextCutoffUtc: string | null
  position: number
  totalBars: number
  excludedFutureCandles: number
  timestampSafe: true
  noLookahead: true
}

export type FamilySummary = {
  total: number
  reviewed: number
  pending: number
  bullish: number
  bearish: number
  unknown: number
  labeledCount: number
  bullishRatePct: number | null
  bearishRatePct: number | null
  averageReturnPct: number | null
  medianReturnPct: number | null
}

export type HistoricalFamilySummary = {
  contract: 'GANN_RETROSPECTIVE_FAMILY_EVIDENCE_V1'
  asOf: string
  scope: 'strictly_prior_matured_occurrences'
  priorOccurrenceCount: number
  maturedTouchCount: number
  excludedImmatureCount: number
  labeledCount: number
  bullish: number
  bearish: number
  unknown: number
  bullishRatePct: number | null
  bearishRatePct: number | null
  averageReturnPct: number | null
  medianReturnPct: number | null
  directionalBias: 'bullish' | 'bearish' | 'mixed' | 'insufficient'
  excursionSampleCount: number
  medianUpsideExcursionPct: number | null
  medianDownsideExcursionPct: number | null
  medianFavorableExcursionPct: number | null
  medianAdverseExcursionPct: number | null
  excursionHorizonHours: 72
  excursionAnchor: 'touch_close'
  timestampSafeForSelectedEvent: true
  liveInferenceConsumed: false
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

export type CurrencySideEvidence = {
  label: string
  referenceLabel: string
  netScore: number | null
  doctrineNetScore: number | null
  scoredHitCount: number | null
  dominantHit: string | null
  doctrineDominantHit: string | null
  doctrineDominantDignity: string | null
  doctrineDignityVirupaAvg: number | null
}

export type CurrencyPairEvidence = {
  contract: 'GANN_FX_PAIR_EVIDENCE_V1'
  status: 'provisional_research_only' | 'insufficient_pair_evidence'
  base: CurrencySideEvidence
  quote: CurrencySideEvidence
  pair: {
    netScore: number | null
    conflictRatio: number | null
    direction: string | null
    doctrineNetScore: number | null
    doctrineConflictRatio: number | null
    doctrineDirection: string | null
  }
  notes: string | null
}

export type EvidenceCertification = {
  key: 'astronomy_geometry' | 'shadbala_drik' | 'currency_pair' | 'family_outcomes'
  label: string
  status: 'versioned' | 'certified' | 'provisional' | 'retrospective' | 'blocked' | 'failed'
  badge: string
  detail: string
  contract: string
  sourceSha256: string | null
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
  familySummary: FamilySummary
  historicalFamilySummary: HistoricalFamilySummary
  currencyPairEvidence: CurrencyPairEvidence | null
  evidenceCertifications: EvidenceCertification[]
  context: Record<string, unknown>
  annotations: ChartAnnotation[]
}

export type AspectEvidenceTraceRecord = {
  kind: 'start' | 'window_bar' | 'end' | 'window_crest' | 'window_trough'
  asOfUtc: string
  asOfIst: string
  eventState: 'window_start' | 'inside_window' | 'window_end' | 'before_window' | 'after_window'
  market: {
    available: boolean
    reason?: string
    barOpenTimeUtc?: string
    barCloseTimeUtc?: string
    open?: number | null
    high?: number | null
    low?: number | null
    close?: number | null
    rsi14?: {
      value: number | null
      zone: string
      method: string
      closedBarOnly: boolean
    }
    candle?: {
      direction?: string
      rangePips?: number | null
      bodyPips?: number | null
      bodyFraction?: number | null
      upperWickFraction?: number | null
      lowerWickFraction?: number | null
      closeLocation?: number | null
      atr14Pips?: number | null
      preTrend?: string
      patterns?: Array<{ name: string; hypothesisBias: string; basis: string; context: string }>
    }
    sr?: {
      status: string
      knownAtUtc: string | null
      touchTimeUtc?: string
      source?: string
      lines: Array<{ planet: string; price: number; distancePipsFromClose: number | null }>
    }
  }
  overlaps: {
    activeCount: number
    otherActiveCount: number
    events: Array<{ eventId: string; familyKey: string; aspect: string; role: 'selected' | 'overlap' }>
    truncated: boolean
    contract: string
  }
  sbc: {
    snapshotId: string
    asOfUtc: string
    panchanga: {
      tithi: string
      tithiGroup: string
      paksha: string
      yoga: string
      karana: string
      weekday: string
      weekdayLord: string
    }
    positions: Array<{ body: string; longitudeDeg: number | null; speedDegPerDay: number | null; rashi: string; nakshatras: string[] }>
    actorReadiness: Array<{ body: string; requested: boolean; status: string; source_nakshatra: string; motion_class: ChakraMotionClass | null; reason: string }>
    guidance: null | {
      guidanceOnly: boolean
      financialValidationStatus: string
      favorableUnits: number | null
      adverseUnits: number | null
      netUnits: number | null
      normalizedScore: number | null
      band: string
      scoredMatchCount: number
      unresolvedMatchCount: number
      coverageRatio: number | null
    }
    policy: {
      displayTimezone: string
      locationSource: string
      variableMotion: string
      instrumentKeys: string
    }
    guardrails: {
      readOnly: boolean
      timestampSafe: boolean
      noLookahead: boolean
      executionAllowed: boolean
      financiallyValidated: boolean
      guidanceOnly: boolean
    }
  }
  strength: {
    status: string
    body?: string
    reason?: string
    scopePolicy?: string
    implementedTotalVirupa?: number | null
    strengthVsMinimum?: number | null
    drikVirupa?: number | null
    drikBeneficVirupa?: number | null
    drikMaleficVirupa?: number | null
    saptavargajaVirupa?: number | null
    ojayugmaVirupa?: number | null
    kaala9Virupa?: number | null
    chestaVirupa?: number | null
    calculatorStatus?: string
    drikStatus?: string
    missingComponents?: string[]
    certification?: { status: string; certified: boolean; contract: string }
  }
  guardrails: {
    timestampSafe: boolean
    noLookahead: boolean
    outcomeExcluded: boolean
    executionAllowed: boolean
    consumedByLiveInference: boolean
    selectedRetrospectively?: boolean
    selectionKnownAtUtc?: string
    usableAtStart?: boolean
    usableDuringWindow?: boolean
    consumedByShadowLedger?: boolean
  }
}

export type AspectEvidenceTrace = {
  contract: 'GANN_ASPECT_EVIDENCE_TRACE_V1'
  version: string
  eventId: string
  familyKey: string
  symbol: string
  timeframe: string
  times: {
    eventStartUtc: string
    eventEndUtc: string
    displayTimezone: string
  }
  profile: {
    referenceLabel: string
    latitude: number | null
    longitude: number | null
    referenceTimezone: string
    locationPolicy: string
  }
  start: AspectEvidenceTraceRecord
  window: {
    totalCompletedBars: number
    includedBarCount: number
    sampled: boolean
    samplingPolicy: string
    records: AspectEvidenceTraceRecord[]
  }
  end: AspectEvidenceTraceRecord
  reactionCheckpoints: {
    available: boolean
    retrospectiveOnly: boolean
    selectionKnownAtUtc: string
    selectionPolicy: string
    usableAtStart: boolean
    usableDuringWindow: boolean
    consumedByLiveInference: boolean
    consumedByShadowLedger: boolean
    crest: AspectEvidenceTraceRecord | null
    trough: AspectEvidenceTraceRecord | null
  }
  outcome: {
    available: boolean
    retrospectiveOnly: boolean
    reason: string
    touchTimeUtc?: string | null
    labelAvailableAtUtc?: string | null
    direction?: string | null
    returnPct?: number | null
  }
  precalculationStatus: Record<string, string>
  guardrails: {
    researchOnly: boolean
    timestampSafe: boolean
    noLookahead: boolean
    outcomeSeparated: boolean
    consumedByLiveInference: boolean
    consumedByShadowLedger: boolean
    executionAllowed: boolean
  }
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

export type ValidationGate = {
  gateId:
    | 'timestamp_safe_inference'
    | 'external_astrology'
    | 'retrospective_policy'
    | 'prospective_shadow'
    | 'candlestick_agent'
    | 'execution_authorization'
  title: string
  status: 'passed' | 'failed' | 'blocked' | 'collecting' | 'locked'
  blocking: boolean
  detail: string
  source: string | null
  metrics: Record<string, string | number | boolean | null | undefined>
}

export type ValidationGateMatrix = {
  contract: 'GANN_RESEARCH_VALIDATION_GATE_MATRIX_V1'
  generatedAtUtc: string
  overallStatus: 'research_only_blocked' | 'prerequisites_passed_execution_still_locked'
  prerequisitesPassed: boolean
  executionAllowed: false
  blockingGateIds: string[]
  gates: ValidationGate[]
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
  validationGates?: ValidationGateMatrix
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

export type CandlestickShadowCandidate = {
  name: string
  modelId: string
  probabilityUp?: number
  action: 'long' | 'short' | 'abstain'
  shortProbability?: number
  longProbability?: number
  diagnosticOnly?: true
  signedGrossPips?: number | null
  netPips?: number | null
  tradeOccurred?: boolean
  executionOccurred?: false
}

export type CandlestickShadowPayload = {
  contract: string
  decisionId: string
  recordedAtUtc: string
  decisionBarOpenUtc?: string
  featureAvailableAtUtc?: string
  rawDecisionBarOpenServerEpochSeconds?: number
  rawFeatureAvailableServerEpochSeconds?: number
  captureLagSeconds?: number
  ohlc?: { time: string; open: number; high: number; low: number; close: number }
  patterns?: Array<{ name: string; hypothesisBias: string; basis: string; context: string }>
  primary: CandlestickShadowCandidate
  diagnostics: CandlestickShadowCandidate[]
  entryTimeUtc?: string
  exitTimeUtc?: string
  entryPrice?: number
  exitPrice?: number
  grossLongPips?: number
  targetUp?: boolean
  totalCostPips?: number
  heldBars?: number
  timeNormalization?: Mt5TimeNormalization
}

export type Mt5ClockProbeEvidence = {
  contract: 'GANN_MT5_CLOCK_PROBE_V1'
  probeSequence: number
  probePath: string
  probeFileSha256: string
  ageSeconds: number
  timeGmtUtc: string
  timeCurrentServerEncoded: string
  timeTradeServerEncoded: string
  rawTickServerEncoded: string
  rawH1BarOpenServerEncoded: string
  terminalBuild: number
  terminalConnected: boolean
  terminalAllowsTrading: boolean
  accountAllowsTrading: boolean
  accountExpertTradingAllowed: boolean
  accountServer: string
  symbol: string
}

export type Mt5TimeNormalization = {
  contract: 'GANN_MT5_SERVER_TIME_NORMALIZATION_V1'
  observedAtUtc: string
  valid: boolean
  failureMode: 'skip_without_append'
  validationIssues: string[]
  serverOffsetSeconds: number
  rawMeasuredOffsetSeconds: number
  offsetResidualSeconds: number
  offsetSource: 'TimeTradeServer-TimeGMT'
  rawMarketTickServerEncoded: string
  normalizedMarketTickUtc: string
  normalizedMarketTickSkewSeconds: number
  rawH1BarOpenServerEncoded: string
  normalizedH1BarOpenUtc: string
  probe: Mt5ClockProbeEvidence
  appExecutionAllowed: false
}

export type CandlestickShadowRecord = {
  sequence: number
  entryId: string
  entryType: 'decision' | 'outcome'
  decisionId: string
  effectiveAtUtc: string
  recordedAtUtc: string
  payloadSha256: string
  entryHash: string
  payload: CandlestickShadowPayload
}

export type CandlestickShadowSnapshot = {
  contract: 'GANN_CANDLESTICK_APPEND_ONLY_SHADOW_LEDGER_V3'
  trial: {
    trialId: string
    contract: 'GANN_CANDLESTICK_FROZEN_SHADOW_TRIAL_V3'
    identitySha256: string
    establishedAtUtc: string
  }
  model: {
    artifactId: string
    artifactSha256: string
    primaryModelId: string
    retrospectiveGate: {
      status: 'failed'
      primaryCandidate: string
      reason: string
      promotionAuthorized: false
    }
  }
  summary: { decisions: number; outcomes: number; pending: number }
  integrity: { ok: boolean; entries: number; headHash: string }
  records: CandlestickShadowRecord[]
  lastScan: {
    state: 'not_scanned' | 'captured' | 'current' | 'idle' | 'skipped' | 'error'
    observedAtUtc: string | null
    decisionAppended: boolean
    outcomesAppended: number
    message: string
    timeNormalization?: Mt5TimeNormalization | null
    clockProbePath?: string
  }
  databasePath: string
  guardrails: {
    consumedByAstrologyRules: false
    consumedByAutoSuggest: false
    consumedByOfficialMlNotes: false
    consumedByCoordinator: false
    executionAllowed: false
    mt5ReadOnly: true
  }
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
  apiToken: string
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

export type RuntimeProfile = {
  contract: 'GANN_ASTRO_RUNTIME_PROFILE_V1'
  platform: 'browser' | 'desktop' | 'android' | 'mobile'
  backendMode: 'browser_development' | 'managed_sidecar' | 'remote_companion'
  configured: boolean
  executionAllowed: false
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
    layer: 'classical_doctrine' | 'reference_commentary' | 'local_research' | 'source_provenance' | 'hypothesis_reference' | 'unclassified_reference'
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

export type CandlestickPatternEvidence = {
  name: string
  hypothesisBias: 'bullish' | 'bearish' | 'neutral'
  basis: string
  context: string
}

export type CandlestickBarEvidence = {
  startTime: string
  closeTime: string
  open: number
  high: number
  low: number
  close: number
  direction: 'bullish' | 'bearish' | 'flat'
  rangePips: number
  bodyPips: number
  bodyFraction: number
  upperWickFraction: number
  lowerWickFraction: number
  closeLocation: number
  atr14Pips: number
  preTrend: 'up' | 'down' | 'sideways' | 'insufficient'
  preTrendStrengthAtr: number
  patterns: CandlestickPatternEvidence[]
}

export type CandlestickWindowEvidence = {
  barCount: number
  open?: number | null
  high: number | null
  low: number | null
  close?: number | null
  movePips: number | null
  patterns: Array<CandlestickPatternEvidence & { time: string }>
}

export type CandlestickEvidence = {
  contract: 'GANN_CANDLESTICK_EVIDENCE_V1'
  methodologyVersion: 'transparent_ohlc_geometry_v1'
  eventId: string
  symbol: string
  timeframe: string
  barSeconds: number
  eventStart: string
  eventEnd: string
  analysisCutoff: string
  selectedAnnotationId: string
  closedBarCountAtCutoff: number
  focusBar: CandlestickBarEvidence | null
  eventWindow: CandlestickWindowEvidence
  hindsight: CandlestickWindowEvidence & {
    available: boolean
    label: string
    referencePrice?: number
    closeMoveFromCutoffPips?: number
    maxUpFromCutoffPips?: number
    maxDownFromCutoffPips?: number
  }
  guardrails: {
    analysisOnly: true
    closedBarsOnlyAtCutoff: true
    hindsightSeparated: true
    patternIsNotTradeSignal: true
    consumedByLiveInference: false
    consumedByShadowLedger: false
    executionAllowed: false
  }
}

export type RsiEvidence = {
  contract: 'GANN_RSI_EVIDENCE_V1'
  methodologyVersion: 'wilder_smoothed_close_v1'
  eventId: string
  symbol: string
  timeframe: string
  source: 'close'
  period: number
  levels: number[]
  barSeconds: number
  eventStart: string
  eventEnd: string
  analysisCutoff: string
  selectedAnnotationId: string
  closedBarCountAtCutoff: number
  warmupBarsRequired: number
  ready: boolean
  focus: null | {
    barOpenTime: string
    barCloseTime: string
    close: number
    value: number
    zone: 'unavailable' | 'at_or_above_70' | 'at_or_below_30' | 'above_midline' | 'below_midline'
    nearestLevel: number
    distanceToNearestLevel: number
  }
  eventWindow: {
    sampleCount: number
    startValue: number | null
    endValue: number | null
    minimum: number | null
    maximum: number | null
    change: number | null
    crossings: Array<{
      level: number
      direction: 'up' | 'down'
      time: string
      from: number
      to: number
    }>
  }
  guardrails: {
    analysisOnly: true
    closedBarsOnlyAtCutoff: true
    wilderMethodExplicit: true
    levelTouchIsNotReversalProof: true
    consumedByLiveInference: false
    consumedByShadowLedger: false
    executionAllowed: false
  }
}

export type MarketSynthesisHealth = {
  contract: 'GANN_LOCAL_MARKET_SYNTHESIS_DRAFT_V1'
  ready: boolean
  runtimeReady: boolean
  model: string
  availableModels: string[]
  error: string
  analysisOnly: true
  executionAllowed: false
}

export type MarketSynthesisDraft = {
  contract: 'GANN_LOCAL_MARKET_SYNTHESIS_DRAFT_V1'
  draftId: string
  eventId: string
  model: string
  text: string
  packet: {
    contract: 'GANN_MARKET_SYNTHESIS_PACKET_V1'
    eventId: string
    symbol: string
    timeframe: string
    analysisCutoff: string
    includedInputs: {
      astrology: boolean
      candlesticks: boolean
      rsi: boolean
    }
    astrology: Record<string, unknown> | null
    candlesticks: Omit<CandlestickEvidence, 'hindsight'> | null
    rsi: RsiEvidence | null
    guardrails: {
      analysisOnly: true
      specialistPacketsRemainIsolated: true
      retrospectiveOutcomeExcluded: true
      candlestickHindsightExcluded: true
      closedBarsOnlyAtCutoff: true
      consumedByLiveInference: false
      consumedByShadowLedger: false
      automaticOrderPlacement: false
      executionAllowed: false
    }
  }
  verifier: {
    status: 'pass' | 'review_required'
    issues: string[]
  }
  guardrails: {
    analysisOnly: true
    deterministicEvidenceIsGroundTruth: true
    rawDraftIsOfficial: false
    consumedByLiveInference: false
    consumedByShadowLedger: false
    automaticOrderPlacement: false
    executionAllowed: false
  }
  disclaimer: string
}

export type LocalCandlestickHealth = {
  contract: 'GANN_LOCAL_CANDLE_RAG_DRAFT_V1'
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

export type LocalCandlestickDraft = {
  contract: 'GANN_LOCAL_CANDLE_RAG_DRAFT_V1'
  draftId: string
  eventId: string
  model: string
  text: string
  evidence: CandlestickEvidence
  citations: Array<{
    sourceId: string
    chunkId: string
    title: string
    layer: 'method_reference' | 'empirical_evidence' | 'source_provenance' | 'unclassified_reference'
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
    repairs: string[]
  }
  disclaimer: string
}

export type Mt5Status = {
  state: 'starting' | 'disabled' | 'connected' | 'reconnecting'
  symbol: string
  connected: boolean
  tradeAllowed: boolean
  terminalAllowsTrading: boolean
  accountAllowsTrading: boolean
  accountExpertTradingAllowed: boolean
  appExecutionAllowed: false
  lastError: string
  updatedAt: string
  accountLogin?: number
  server?: string
  company?: string
  bid?: number | null
  ask?: number | null
  lastTickUtc?: string | null
  rawLastTickServerEpochSeconds?: number | null
  rawLastTickMilliseconds?: number | null
  rawLastTickServerTime?: string | null
  terminalPath?: string
  terminalDataPath?: string
  terminalCommonDataPath?: string
  clockProbePath?: string
  clockProbeDeployment?: {
    contract: 'GANN_MT5_CLOCK_PROBE_DEPLOYMENT_V1'
    available: boolean
    deployed: boolean
    changed: boolean
    message?: string
    targetRoot?: string
    appExecutionAllowed: false
  }
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

export type ChakraMotionClass = 'DIRECT_SWIFT' | 'MEAN' | 'RETROGRADE'
export type ChakraDignityState = 'ORDINARY' | 'EXALTED' | 'DEBILITATED'
export type ChakraPlanetNature = 'BENEFIC' | 'MALEFIC' | 'CONDITIONAL'

export type ChakraLabActorInput = {
  body: string
  motionClass?: ChakraMotionClass
  nature?: ChakraPlanetNature
  dignity?: ChakraDignityState
  mercuryAssociationNature?: ChakraPlanetNature
}

export type ChakraLabRequest = {
  at: string
  timezone: 'Asia/Kolkata'
  latitude: number
  longitude: number
  altitudeM: number
  bodies: string[]
  actors: ChakraLabActorInput[]
  foundationProfileId: 'sbc_raman_foundation_v1'
  gridProfileId: 'sbc_81_rotation_normalized_partial_v1'
  vedhaProfileId: 'phaladeepika_editor_vedha_guidance_v1'
  vowels: string[]
  nameInitials: string[]
}

export type ChakraGridEntry = {
  row: number
  column: number
  layer: 'NAKSHATRA' | 'RASHI' | 'TITHI_GROUP' | 'WEEKDAY' | 'VOWEL' | 'NAME_INITIAL'
  value: string
  glyph: string | null
  transliteration: string | null
  semantic_role: string | null
  witness_set_id: string
  evidence_status: string
}

export type ChakraGridCell = {
  row: number
  column: number
  entries: ChakraGridEntry[]
}

export type ChakraVedhaTarget = {
  source_nakshatra: string
  direction: 'LEFT' | 'FRONT' | 'RIGHT'
  row: number
  column: number
  layer: ChakraGridEntry['layer']
  value: string
  semantic_role: string | null
  witness_set_id: string
  evidence_status: string
}

export type ChakraActorResolution = {
  body: string
  source_nakshatra: string
  direction: 'LEFT' | 'FRONT' | 'RIGHT'
  direction_reason: string
  nature: ChakraPlanetNature
  nature_reason: string
  effective_multiplier: number | null
  multiplier_status: string
  multiplier_reason: string
  targets: ChakraVedhaTarget[]
}

export type ChakraVedhaContribution = {
  body: string
  source_nakshatra: string
  direction: 'LEFT' | 'FRONT' | 'RIGHT'
  target: ChakraVedhaTarget
  nature: ChakraPlanetNature
  effective_multiplier: number | null
  signed_guidance_units: number | null
  status: string
  explanation: string
}

export type ChakraLabSnapshot = {
  contract: 'SBC_CHAKRA_LAB_SNAPSHOT_V1'
  schema_version: 1
  snapshot_id: string
  requested_at_local: string
  as_of_utc: string
  evidence_cutoff_utc: string
  timezone: string
  location: {
    latitude: number
    longitude: number
    timezone: string
    altitude_m: number
  }
  foundation_snapshot: {
    snapshot_id: string
    profile_id: string
    profile_hash: string
    astronomy_contract: string
    panchanga: {
      tithi_name: string
      tithi_group: string
      paksha: string
      moon_phase: string
      yoga_name: string
      karana_name: string
      vara: {
        weekday: string
        weekday_lord: string
      }
    }
  }
  grid: {
    grid_profile_id: string
    profile_hash: string
    rows: number
    columns: number
    cells: ChakraGridCell[]
    certified_layers: string[]
    complete: boolean
    blocked_capabilities: string[]
  }
  context_contract: 'SBC_CURRENT_MOMENT_CONTEXT_V1'
  target_context: Array<{
    layer: ChakraGridEntry['layer']
    values: string[]
  }>
  position_context: Array<{
    body: string
    longitude_deg: number
    longitude_speed_deg_per_day: number
    rashi: string
    nakshatras: string[]
  }>
  actor_readiness: Array<{
    body: string
    requested: boolean
    status: 'READY' | 'NOT_SELECTED' | 'MOTION_REQUIRED' | 'OUTSIDE_CERTIFIED_VEDHA_PROFILE'
    source_nakshatra: string
    motion_class: ChakraMotionClass | null
    reason: string
  }>
  guidance: {
    schema_version: 'SBC_VEDHA_GUIDANCE_V1'
    vedha_profile_id: string
    vedha_profile_hash: string
    grid_profile_id: string
    grid_profile_hash: string
    guidance_model_id: string
    guidance_only: true
    financial_validation_status: 'NOT_VALIDATED'
    actor_resolutions: ChakraActorResolution[]
    contributions: ChakraVedhaContribution[]
    favorable_guidance_units: number
    adverse_guidance_units: number
    net_guidance_units: number
    normalized_guidance_score: number
    guidance_band: string
    matched_target_count: number
    scored_match_count: number
    unresolved_match_count: number
    scoring_coverage_ratio: number
    blocked_capabilities: string[]
  } | null
  source_ids: string[]
  guardrails: {
    read_only: true
    timestamp_safe: true
    no_lookahead: true
    execution_allowed: false
    market_data_included: false
    financially_validated: false
    guidance_only: true
  }
}

export type ChakraLabAuditBoundaryInput = {
  reason: string
  request: ChakraLabRequest
}

export type ChakraLabAuditRequest = {
  instrumentIdentity: string
  terminalEnd: string
  boundaries: ChakraLabAuditBoundaryInput[]
}

export type ChakraAuditLedgerSummary = {
  favorable_guidance_units: number
  adverse_guidance_units: number
  net_guidance_units: number
  gross_activation_units: number
  scored_contribution_count: number
  unknown_contribution_count: number
  missing_evidence_count: number
  total_evidence_count: number
  unknown_magnitude_units: number | null
  scoring_coverage_ratio: number
}

export type ChakraAuditInterval = {
  interval_id: string
  interval_ledger_id: string
  start_utc: string
  end_utc: string
  evidence_cutoff_utc: string
  duration_seconds: number
  cluster_ids: string[]
  cell_ids: string[]
  duplicate_primary_evidence_count: number
  total_summary: ChakraAuditLedgerSummary
  all_axes_reconciled: true
}

export type ChakraAuditLedgerCell = {
  cell_id: string
  interval_id: string
  axis: string
  key: string
  derivation_role: 'DERIVED_AXIS'
  cluster_ids: string[]
  summary: ChakraAuditLedgerSummary
  counts_as_independent_vote: false
  directional_contribution: 0
}

export type ChakraAuditRay = {
  cluster_id: string
  interval_id: string
  cell_ids: string[]
  evidence_kind: 'CONTRIBUTION' | 'MISSING_EVIDENCE'
  derivation_role: 'PRIMARY_EVIDENCE'
  actor_identity: string | null
  source_nakshatra: string | null
  vedha_direction: 'LEFT' | 'FRONT' | 'RIGHT' | null
  target_row: number | null
  target_column: number | null
  target_layer: string | null
  target_value: string | null
  nature: ChakraPlanetNature | null
  effective_multiplier: number | null
  signed_guidance_units: number | null
  status: string
  unknown_reason: string | null
  phase_angle: null
  phase_vector_included: false
  counts_as_independent_vote: false
  directional_contribution: 0
}

export type ChakraAuditLineage = {
  cluster_id: string
  interval_id: string
  source_lineage_id: string
  source_ids: string[]
  citation_source_ids: string[]
  snapshot_id: string
  foundation_profile_id: string
  foundation_profile_hash: string
  grid_profile_id: string
  grid_profile_hash: string
  vedha_profile_id: string
  vedha_profile_hash: string
  guidance_model_id: string
  target_witness_set_id: string | null
  target_evidence_status: string | null
  status: string
}

export type ChakraAuditReconciliation = {
  interval_id: string
  axis: string
  cell_count: number
  cluster_count: number
  every_cluster_exactly_once: boolean
  favorable_matches: boolean
  adverse_matches: boolean
  net_matches: boolean
  gross_matches: boolean
  scored_count_matches: boolean
  unknown_count_matches: boolean
  missing_count_matches: boolean
  total_count_matches: boolean
  reconciled: true
}

export type ChakraAuditValidationGate = {
  gate_id: string
  state: 'PASS' | 'FAIL' | 'UNKNOWN'
  label: string
  detail: string
}

export type ChakraLinkedAuditView = {
  contract: 'SBC_LINKED_AUDIT_VIEW_V1'
  schema_version: 1
  view_policy: 'LINKED_READ_ONLY_PROGRESSIVE_DISCLOSURE_V1'
  classification: 'SOURCE_PROFILED_EXPERIMENTAL'
  audit_view_id: string
  source_ledger_id: string
  source_atomic_series_id: string
  instrument_identity: string
  range_start_utc: string
  range_end_utc: string
  source_ids: string[]
  views: Array<{
    view_id: 'TIMELINE' | 'LEDGER' | 'RAY_AUDIT' | 'SOURCE_LINEAGE' | 'RECONCILIATION' | 'VALIDATION'
    label: string
    purpose: string
    phase_vector_included: false
    counts_as_independent_vote: false
    directional_contribution: 0
  }>
  intervals: ChakraAuditInterval[]
  ledger_cells: ChakraAuditLedgerCell[]
  ray_rows: ChakraAuditRay[]
  lineage_rows: ChakraAuditLineage[]
  reconciliations: ChakraAuditReconciliation[]
  validation_gates: ChakraAuditValidationGate[]
  guardrails: {
    read_only: true
    timestamp_safe: true
    no_lookahead: true
    source_profiled_experimental: true
    financially_validated: false
    phase_included: false
    fx_subtraction_included: false
    confidence_included: false
    counts_as_independent_vote: false
    directional_contribution: 0
    execution_allowed: false
    blocked_capabilities: string[]
  }
}

export type ChakraFixedPhasorVector = {
  interval_id: string
  cluster_id: string
  source_lineage_id: string
  evidence_kind: 'CONTRIBUTION' | 'MISSING_EVIDENCE'
  source_evidence_id: string
  actor_identity: string | null
  target_layer: string | null
  target_value: string | null
  signed_guidance_units: number | null
  source_status: string
  unknown_reason: string | null
  derivation_role: 'VISUALIZATION_ONLY'
  counts_as_independent_vote: false
  directional_contribution: 0
  projection_status: 'PLOTTED' | 'UNKNOWN_NOT_PLOTTED'
  magnitude_units: number | null
  fixed_angle: 'ZERO' | 'PI' | null
  fixed_angle_radians: number | null
  real_component_units: number | null
  imaginary_component_units: number | null
  vector_id: string
}

export type ChakraFixedPhasorInterval = {
  interval_id: string
  interval_ledger_id: string
  start_utc: string
  end_utc: string
  evidence_cutoff_utc: string
  vectors: ChakraFixedPhasorVector[]
  source_favorable_units: number
  source_adverse_units: number
  source_net_units: number
  source_gross_activation_units: number
  vector_real_sum_units: number
  vector_imaginary_sum_units: number
  vector_magnitude_sum_units: number
  known_scored_coherence_ratio: number
  plotted_vector_count: number
  unknown_vector_count: number
  missing_evidence_count: number
  real_matches_net: true
  magnitude_matches_gross: true
  imaginary_is_zero: true
  counts_match: true
  unknowns_preserved: true
  reconciled: true
  projection_id: string
}

export type ChakraFixedPhasorSeries = {
  contract: 'SBC_FIXED_ZERO_PI_PHASOR_SERIES_V1'
  schema_version: 1
  projection_policy: 'FIXED_ZERO_PI_SCALAR_PARITY_VISUALIZATION_ONLY_V1'
  classification: 'SOURCE_PROFILED_EXPERIMENTAL'
  projection_series_id: string
  source_ledger_id: string
  source_atomic_series_id: string
  instrument_identity: string
  range_start_utc: string
  range_end_utc: string
  source_ids: string[]
  field_roles: Array<{
    field_path: string
    derivation_role: 'VISUALIZATION_ONLY'
    evidence_bearing: false
    counts_as_independent_vote: false
    directional_contribution: 0
  }>
  intervals: ChakraFixedPhasorInterval[]
  validation_gates: Array<{
    gate_id: string
    state: 'PASS' | 'UNKNOWN'
    label: string
    detail: string
  }>
  guardrails: {
    research_only: true
    read_only: true
    timestamp_safe: true
    no_lookahead: true
    source_profiled_experimental: true
    scalar_equivalent_only: true
    fixed_zero_pi_only: true
    visualization_only: true
    physical_wave_claimed: false
    timing_phase_included: false
    timing_sector_profile_included: false
    fx_subtraction_included: false
    confidence_included: false
    financially_validated: false
    counts_as_independent_vote: false
    directional_contribution: 0
    execution_allowed: false
    blocked_capabilities: string[]
  }
}

export type ChakraTimingProfileAdmissionGate = {
  gate_id: string
  state: 'PASS' | 'FAIL' | 'UNKNOWN'
  mandatory: boolean
  label: string
  detail: string
  missing_paths: string[]
}

export type ChakraTimingProfileAdmissionReport = {
  contract: 'SBC_TIMING_PROFILE_ADMISSION_REPORT_V1'
  schema_version: 1
  admission_policy: 'FAIL_CLOSED_SOURCE_REGISTRY_ADMISSION_V1'
  classification: 'SOURCE_PROFILED_EXPERIMENTAL'
  profile_status:
    | 'NO_PROFILE_LOADED'
    | 'INVALID_PROFILE'
    | 'STRUCTURALLY_COMPLETE_UNREGISTERED'
    | 'SOURCE_CERTIFIED_PROFILE_ADMITTED'
  profile_id: string | null
  profile_version: string | null
  candidate_profile_hash: string | null
  structural_complete: boolean
  source_registry_admitted: boolean
  isolated_research_profile_admitted: boolean
  directional_engine_implemented: false
  directional_output_available: false
  prospective_financial_validation_passed: boolean
  financial_use_allowed: false
  validation_gates: ChakraTimingProfileAdmissionGate[]
  missing_requirements: string[]
  guardrails: {
    research_only: true
    read_only: true
    candidate_persisted: false
    profile_values_supplied_by_application: false
    timing_phase_calculated: false
    directional_phase_calculated: false
    confidence_calculated: false
    counts_as_independent_vote: false
    directional_contribution: 0
    auto_suggest_included: false
    live_inference_included: false
    official_ml_notes_included: false
    shadow_vote_included: false
    trade_output_included: false
    financially_validated: false
    execution_allowed: false
    blocked_capabilities: string[]
  }
}

export type ChakraTimingSourceReadinessGate = {
  gate_id: string
  state: 'PASS' | 'FAIL' | 'UNKNOWN'
  mandatory: boolean
  label: string
  detail: string
  missing_paths: string[]
}

export type ChakraTimingSourceClaimCoverage = {
  profile_path: string
  claim_class: 'DOCTRINE' | 'RESEARCH_PROTOCOL'
  candidate_value_sha256: string | null
  primary_source_count: number
  independent_witness_count: number
  research_specification_count: number
  independent_lineage_count: number
  coverage_state: 'PASS' | 'FAIL' | 'UNKNOWN'
  detail: string
}

export type ChakraTimingProfileSourceReadinessReport = {
  contract: 'SBC_TIMING_PROFILE_SOURCE_READINESS_REPORT_V1'
  schema_version: 1
  readiness_policy: 'CLAIM_HASH_AND_INDEPENDENT_LINEAGE_READINESS_V1'
  classification: 'SOURCE_PROFILED_EXPERIMENTAL'
  packet_status:
    | 'NO_PACKET_LOADED'
    | 'NOT_READY_FOR_EXTERNAL_REVIEW'
    | 'READY_FOR_EXTERNAL_REVIEW'
  profile_id: string | null
  profile_version: string | null
  candidate_profile_hash: string | null
  packet_id: string | null
  packet_hash: string | null
  candidate_structural_complete: boolean
  packet_structural_complete: boolean
  claim_coverage_complete: boolean
  independent_witness_coverage_complete: boolean
  conflicts_resolved: boolean
  ready_for_external_review: boolean
  external_review_completed: false
  source_certified: false
  profile_registration_allowed: false
  validation_gates: ChakraTimingSourceReadinessGate[]
  claim_coverage: ChakraTimingSourceClaimCoverage[]
  missing_requirements: string[]
  guardrails: {
    research_only: true
    read_only: true
    candidate_persisted: false
    packet_persisted: false
    source_bytes_verified_by_application: false
    external_review_completed: false
    source_certified: false
    profile_registration_allowed: false
    timing_phase_calculated: false
    directional_phase_calculated: false
    confidence_calculated: false
    counts_as_independent_vote: false
    directional_contribution: 0
    auto_suggest_included: false
    live_inference_included: false
    official_ml_notes_included: false
    shadow_vote_included: false
    trade_output_included: false
    financially_validated: false
    execution_allowed: false
    blocked_capabilities: string[]
  }
}

export type ChakraAuditBookmarkTarget =
  | 'AUDIT'
  | 'INTERVAL'
  | 'CELL'
  | 'CLUSTER'
  | 'VALIDATION_GATE'

export type ChakraAuditBookmarkInput = {
  targetType: ChakraAuditBookmarkTarget
  targetId: string
  label: string
  note: string
  createdAt: string
}

export type ChakraAuditPackageRequest = {
  auditRequest: ChakraLabAuditRequest
  baselineIntervalId: string
  comparisonIntervalIds: string[]
  bookmarks: ChakraAuditBookmarkInput[]
  sealedAt: string
}

export type ChakraAuditMetricDelta = {
  favorable_guidance_units: number
  adverse_guidance_units: number
  net_guidance_units: number
  gross_activation_units: number
  scored_contribution_count: number
  unknown_contribution_count: number
  missing_evidence_count: number
  total_evidence_count: number
  unknown_magnitude_units: number | null
  scoring_coverage_ratio: number
  derivation_role: 'DESCRIPTIVE_COMPARISON_ONLY'
  counts_as_independent_vote: false
  directional_contribution: 0
}

export type ChakraAuditCellComparison = {
  axis: string
  key: string
  baseline_cell_id: string | null
  comparison_cell_id: string | null
  baseline_summary: ChakraAuditLedgerSummary | null
  comparison_summary: ChakraAuditLedgerSummary | null
  delta: ChakraAuditMetricDelta
  derivation_role: 'DESCRIPTIVE_COMPARISON_ONLY'
  counts_as_independent_vote: false
  directional_contribution: 0
}

export type ChakraAuditIntervalComparison = {
  comparison_id: string
  baseline_interval_id: string
  comparison_interval_id: string
  baseline_summary: ChakraAuditLedgerSummary
  comparison_summary: ChakraAuditLedgerSummary
  total_delta: ChakraAuditMetricDelta
  cell_comparisons: ChakraAuditCellComparison[]
  shared_source_lineage_ids: string[]
  baseline_only_source_lineage_ids: string[]
  comparison_only_source_lineage_ids: string[]
  interpretation: string
  derivation_role: 'DESCRIPTIVE_COMPARISON_ONLY'
  counts_as_independent_vote: false
  directional_contribution: 0
}

export type ChakraAuditBookmark = {
  bookmark_id: string
  target_type: ChakraAuditBookmarkTarget
  target_id: string
  label: string
  note: string
  created_at_utc: string
  annotation_role: 'MANUAL_RESEARCH_ANNOTATION_ONLY'
  counts_as_evidence: false
  official_ml_note: false
  directional_contribution: 0
}

export type ChakraAuditPackageValidationGate = {
  gate_id: string
  state: 'PASS' | 'UNKNOWN'
  label: string
  detail: string
}

export type ChakraReproducibleAuditPackage = {
  contract: 'SBC_REPRODUCIBLE_AUDIT_PACKAGE_V1'
  schema_version: 1
  package_policy: 'READ_ONLY_COMPARISON_EXPORT_REPLAY_V1'
  classification: 'SOURCE_PROFILED_EXPERIMENTAL'
  package_id: string
  source_audit_id: string
  source_projection_hash: string
  instrument_identity: string
  sealed_at_utc: string
  replay_recipe_hash: string
  replay_recipe: Record<string, unknown>
  source_audit: ChakraLinkedAuditView
  comparisons: ChakraAuditIntervalComparison[]
  bookmarks: ChakraAuditBookmark[]
  validation_gates: ChakraAuditPackageValidationGate[]
  guardrails: {
    research_only: true
    read_only: true
    timestamp_safe: true
    no_lookahead: true
    source_profiled_experimental: true
    financially_validated: false
    descriptive_comparison_only: true
    manual_annotations_only: true
    replay_required_for_verification: true
    phase_included: false
    fx_subtraction_included: false
    confidence_included: false
    counts_as_independent_vote: false
    directional_contribution: 0
    execution_allowed: false
    blocked_capabilities: string[]
  }
}

export type ChakraAuditPackageBuild = {
  package: ChakraReproducibleAuditPackage
  htmlReport: string
}

export type ChakraAuditPackageVerification = {
  contract: 'SBC_AUDIT_PACKAGE_VERIFICATION_V1'
  state: 'PASS' | 'FAIL'
  package_id: string | null
  source_audit_id: string | null
  structural_hash_match: boolean
  source_projection_match: boolean
  replay_recipe_match: boolean
  replay_audit_match: boolean
  replay_package_match: boolean
  errors: string[]
}

export type ChakraAuditCatalogRequest = {
  packages: ChakraReproducibleAuditPackage[]
  createdAt: string
  signedAt: string
}

export type ChakraAuditCatalogEntry = {
  entry_id: string
  package_id: string
  package_digest: string
  source_audit_id: string
  instrument_identity: string
  sealed_at_utc: string
  p4_replay_state: 'PASS'
  package: ChakraReproducibleAuditPackage
}

export type ChakraAuditPackageCatalog = {
  contract: 'SBC_AUDIT_PACKAGE_CATALOG_V1'
  schema_version: 1
  catalog_policy: 'SEALED_PACKAGE_CATALOG_NO_CROSS_AUDIT_INFERENCE_V1'
  classification: 'SOURCE_PROFILED_EXPERIMENTAL'
  catalog_id: string
  created_at_utc: string
  entries: ChakraAuditCatalogEntry[]
  validation_gates: ChakraAuditPackageValidationGate[]
  guardrails: {
    research_only: true
    read_only: true
    timestamp_safe: true
    no_lookahead: true
    source_profiled_experimental: true
    financially_validated: false
    catalog_only: true
    embedded_p4_replay_required: true
    no_cross_package_arithmetic: true
    no_cross_package_voting: true
    no_market_direction: true
    no_confidence_output: true
    signatures_prove_integrity_only: true
    counts_as_independent_vote: false
    directional_contribution: 0
    execution_allowed: false
    blocked_capabilities: string[]
  }
}

export type ChakraAuditCatalogSignature = {
  contract: 'SBC_AUDIT_CATALOG_SIGNATURE_V1'
  schema_version: 1
  algorithm: 'ED25519'
  key_id: string
  public_key_base64: string
  catalog_id: string
  catalog_digest: string
  signed_at_utc: string
  signature_base64: string
}

export type ChakraSignedAuditCatalogBundle = {
  contract: 'SBC_SIGNED_AUDIT_CATALOG_BUNDLE_V1'
  schema_version: 1
  bundle_policy: 'SIGNED_PORTABLE_RESEARCH_EXCHANGE_V1'
  catalog: ChakraAuditPackageCatalog
  signature: ChakraAuditCatalogSignature
}

export type ChakraAuditCatalogEntryVerification = {
  package_id: string
  structural_integrity: 'PASS' | 'FAIL'
  semantic_replay: 'PASS' | 'FAIL' | 'NOT_PERFORMED'
  errors: string[]
}

export type ChakraAuditCatalogVerification = {
  contract: 'SBC_AUDIT_CATALOG_VERIFICATION_V1'
  state: 'PASS' | 'FAIL'
  catalog_id: string | null
  key_id: string | null
  catalog_hash_match: boolean
  signature_valid: boolean
  embedded_packages_valid: boolean
  semantic_replay_state: 'PASS' | 'FAIL' | 'NOT_PERFORMED'
  entry_count: number
  entry_verifications: ChakraAuditCatalogEntryVerification[]
  errors: string[]
}

export type ChakraAuditCatalogBuild = {
  bundle: ChakraSignedAuditCatalogBundle
  verification: ChakraAuditCatalogVerification
  signingIdentity: {
    algorithm: 'ED25519'
    keyId: string
    storage: 'WINDOWS_DPAPI_APP_DATA' | 'LOCAL_USER_FILE'
    claim: string
  }
}
