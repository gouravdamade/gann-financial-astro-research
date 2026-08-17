export type ExperimentalDatasetStatus = 'SYNTHETIC' | 'TOUCHED_DEV' | 'MANUAL'
export type ExperimentalValueType =
  | 'SCALAR'
  | 'SIGNED_SCALAR'
  | 'CATEGORY'
  | 'BOOLEAN_GATE'
  | 'TUPLE_SET'
  | 'INTERVAL'
  | 'UNKNOWN'
export type ExperimentalRole =
  | 'SIGN'
  | 'MAGNITUDE'
  | 'MODIFIER'
  | 'GATE'
  | 'CONTEXT'
  | 'ACTIVATION'
  | 'UNCERTAINTY'
  | 'REGIME'

export type ExperimentalGuardrails = {
  experimental: true
  classicalDoctrine: false
  priceDataRead: false
  priceOutcomeRead: false
  sbcRead: false
  fieldsPath: false
  autoSuggestPath: false
  mlPath: false
  mt5Path: false
  executionAllowed: false
  automaticOrderPlacement: false
  financiallyValidated: false
}

export type EvidenceObservationV1 = {
  observationId: string
  eventId: string
  causalEventId: string | null
  causalClassification: 'UNIQUE' | 'SHARED_CAUSE' | 'AMBIGUOUS' | 'DERIVED_CHILD'
  derivationRole: 'PRIMARY_EVIDENCE' | 'DERIVED_AXIS' | 'NON_VOTING_CONTEXT' | 'VISUALIZATION_ONLY'
  timestampUtc: string
  sourceProfileId: string
  featureKey: string
  rawValue: number | boolean | string | null
  rawUnit: string
  valueType: ExperimentalValueType
  sourceSemantic: string
  sourceStatus: string
  provenance: string[]
  unknownReasons: string[]
}

export type ExperimentalRoleBindingV1 = {
  featureKey: string
  role: ExperimentalRole
  transformId: string
  parameters: Record<string, number | string | boolean>
  assignmentOrigin: string
  marketDomain: 'NONE'
  experimentalStatus: string
}

export type ExperimentalProfileV1 = {
  contract: 'XE1_EXPERIMENTAL_PROFILE_V1'
  schemaVersion: 1
  profileId: 'XE1_EVIDENCE_ROLE_MODIFIER_ABLATION_V1'
  codeCommit: string
  profileHash: string
  bindings: ExperimentalRoleBindingV1[]
  causalAggregationPolicy: string
  oscillatorProjectionId: string
  timingKernelId: null
  pairPolicy: { enabled: false; contract: string }
  datasetStatus: 'SYNTHETIC'
  trialLedgerPolicy: string
  executionAllowed: false
}

export type ExperimentalCausalContribution = {
  causalEventId: string
  sourceObservationIds: string[]
  derivedChildIds: string[]
  causalClassification: string
  sourceObservationId?: string
  rawDirectionalValue?: number
  value: number | null
  status: string
  reason: string | null
}

export type ExperimentalStateVector = {
  state: 'SUPPORTIVE' | 'ADVERSE' | 'MIXED' | 'NEUTRAL' | 'UNKNOWN_NO_ACTIVE_EVIDENCE'
  positive: number
  negative: number
  directionalRaw: number | null
  activity: number
  directionalNormalized: number | null
  conflictLinear: number | null
  conflictQuad: number | null
  conflictEntropy: number | null
  unknownGroupCount: number
}

export type ExperimentalSnapshot = {
  contract: 'XE1_EXPERIMENTAL_EVIDENCE_LAB_V1'
  schemaVersion: 1
  codeCommit: string
  snapshotId: string
  profile: ExperimentalProfileV1
  dataMode: ExperimentalDatasetStatus
  datasetStatus: ExperimentalDatasetStatus
  datasetLabel: string
  rawObservations: EvidenceObservationV1[]
  rawEvidenceImmutable: true
  manualInputStatus: 'MANUAL_INPUT_REQUIRED' | 'TOUCHED_DEV_INPUT_NOT_CONFIGURED' | 'NOT_APPLICABLE'
  transformId: string
  modifier: {
    family: string
    contract: string
    parameters: { beta: number; mMin: number; mMax: number }
    z: number | null
    status: 'KNOWN' | 'UNKNOWN'
    value: number | null
    nonSignFlipGuaranteed: boolean
    reason: string | null
  }
  causalContributions: ExperimentalCausalContribution[]
  stateVector: ExperimentalStateVector
  quality: {
    knownDirectionalGroups: number
    unresolvedDirectionalGroups: number
    confidence: number | null
    confidenceUse: string
    confidenceMultipliesEvidence: false
  }
  experimentalOscillator: {
    contract: string
    state: ExperimentalStateVector['state']
    displayValue: number | null
    magnitudeState: string
    marketForecast: false
    executionAllowed: false
  }
  guardrails: ExperimentalGuardrails
}

export type ExperimentalProfileResponse = {
  contract: 'XE1_EXPERIMENTAL_EVIDENCE_LAB_V1'
  codeCommit: string
  profile: ExperimentalProfileV1
  availableDataModes: ExperimentalDatasetStatus[]
  availableTransforms: string[]
  guardrails: ExperimentalGuardrails
}

export type ExperimentalTransformComparison = {
  transformId: string
  stateVector: ExperimentalStateVector
  modifier: ExperimentalSnapshot['modifier']
  quality: ExperimentalSnapshot['quality']
}

export type ExperimentalComparisonResponse = {
  contract: 'XE1_TRANSFORM_COMPARISON_V1'
  codeCommit: string
  profileId: string
  profileHash: string
  dataMode: ExperimentalDatasetStatus
  comparisons: ExperimentalTransformComparison[]
  guardrails: ExperimentalGuardrails
}

export type ExperimentalTrialLedger = {
  contract: 'XE1_EXPERIMENTAL_TRIAL_LEDGER_V1'
  codeCommit: string
  profileHash: string
  ledgerId: string
  entries: Array<{
    trialId: string
    experimentProfileId: string
    experimentProfileHash: string
    transformVersion: string
    parameterSet: Record<string, number>
    datasetId: string
    datasetStatus: ExperimentalDatasetStatus
    result: 'PASS' | 'FAIL' | 'NULL' | 'INCONCLUSIVE'
    notes: string
    codeCommit: string
    createdAtUtc: string
    immutableAfterEvaluation: true
    entryHash: string
  }>
  datasetGovernance: {
    APRIL_2025_STATUS: 'TOUCHED_DEV'
    pristineHoldoutUsed: false
    exploratoryControlsLabel: 'EXPLORATORY_TOUCHED'
  }
  guardrails: ExperimentalGuardrails
}
