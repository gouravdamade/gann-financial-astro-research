export type Xe2Guardrails = {
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
  marketForecast: false
}

export type Xe2Transform = {
  transformId: string
  label: string
  family: string
  parameters: Record<string, string | number>
}

export type Xe2Profile = {
  contract: 'XE2_CAUSAL_SCOPED_PROFILE_V1'
  schemaVersion: 1
  profileId: 'XE2_CAUSAL_SCOPED_SPEED_MODIFIER_TOURNAMENT_V1'
  acceptanceBaselineCommit: string
  datasetStatus: 'TOUCHED_DEV'
  profilePurpose: string
  realSignedEvidenceStatus: string
  causalAggregationPolicy: string
  globalModifierDefaultAllowed: false
  modifierScopeRequired: 'CAUSAL_EVENT_ID'
  stackingAllowed: false
  executionAllowed: false
  transforms: Xe2Transform[]
  profileHash: string
}

export type Xe2RawObservation = {
  observationId: string
  eventId: string
  eventHash: string
  causalEventId: string
  targetScope: { type: 'CAUSAL_EVENT_ID'; causalEventId: string }
  timestampUtc: string
  sourceProfileId: string
  identityStatus: 'SINGLE_PASS_VERIFIED'
  provenance: string[]
  unknownReasons: string[]
  featureKey: string
  role: string
  rawValue: string | number
  rawUnit: string
  valueType: string
  sourceSemantic: string
  sourceStatus: string
  roleOrigin: string
  marketDomain: 'NONE'
}

export type Xe2CausalContribution = {
  causalEventId: string
  eventId: string
  eventHash: string
  sourceObservationIds: string[]
  syntheticSignObservationId: string
  rawSyntheticSignTestValue: number
  rawSpeedDegPerDay: number
  speedNormalizationContract: string
  zSpeed: number | null
  motionPhaseAtExact: string
  scope: {
    modifierObservationId: string
    targetCausalEventId: string
    scopeType: 'CAUSAL_EVENT_ID'
    scopeStatus: 'BOUND' | 'REJECTED_UNSCOPED'
    globalDefaultApplied: false
  }
  multiplierOrInteraction: number | null
  separateChannelValue: number | null
  contextGate: number | null
  value: number | null
  status: 'ACTIVE' | 'UNKNOWN_TARGET_ONLY'
  reason: string | null
  signEvidenceStatus: 'SYNTHETIC_SIGN_TEST_ONLY_NOT_MARKET_EVIDENCE'
}

export type Xe2SyntheticStateVector = {
  state: 'SYNTHETIC_SIGN_TEST_ONLY' | 'UNKNOWN_NO_SYNTHETIC_SIGN_TEST'
  positive: number
  negative: number
  syntheticRaw: number | null
  syntheticNormalized: number | null
  activity: number
  conflict: number | null
  unknownCauseCount: number
}

export type Xe2ProfileResponse = {
  contract: 'XE2_CAUSAL_SCOPED_EVIDENCE_LAB_V1'
  profile: Xe2Profile
  availableTransforms: string[]
  realEvidenceAdmission: Record<string, string>
  guardrails: Xe2Guardrails
}

export type Xe2Snapshot = {
  contract: 'XE2_CAUSAL_SCOPED_EVIDENCE_LAB_V1'
  schemaVersion: 1
  snapshotId: string
  profile: Xe2Profile
  datasetStatus: 'TOUCHED_DEV'
  datasetLabel: string
  astronomySource: Record<string, string>
  normalization: {
    contract: string
    body: string
    rawUnit: string
    referenceSpeedDegPerDay: number
    formula: string
    referenceOrigin: string
  }
  transformId: string
  transform: Xe2Transform
  rawObservations: Xe2RawObservation[]
  scopeBindings: Xe2CausalContribution['scope'][]
  causalContributions: Xe2CausalContribution[]
  syntheticStateVector: Xe2SyntheticStateVector
  marketDirectionStatus: 'BLOCKED_NO_REAL_SIGNED_EVIDENCE'
  marketOutcome: Record<string, string | boolean | Record<string, string>>
  rawEvidenceImmutable: true
  guardrails: Xe2Guardrails
}

export type Xe2ComparisonResponse = {
  contract: 'XE2_CAUSAL_SCOPED_TRANSFORM_COMPARISON_V1'
  profileId: string
  profileHash: string
  datasetStatus: 'TOUCHED_DEV'
  comparisons: Array<{
    transformId: string
    transform: Xe2Transform
    syntheticStateVector: Xe2SyntheticStateVector
    marketDirectionStatus: 'BLOCKED_NO_REAL_SIGNED_EVIDENCE'
  }>
  guardrails: Xe2Guardrails
}

export type Xe2TrialLedger = {
  contract: 'XE2_CAUSAL_SCOPED_MODIFIER_TRIAL_LEDGER_V1'
  ledgerId: string
  profileHash: string
  datasetGovernance: Record<string, string | boolean>
  entries: Array<{
    trialId: string
    transformId: string
    result: 'NOT_EVALUATED'
    notes: string
    profileId: string
    profileHash: string
    datasetStatus: 'TOUCHED_DEV'
    marketOutcomeRead: false
    immutableAfterEvaluation: true
    entryHash: string
  }>
  ledgerHash: string
  guardrails: Xe2Guardrails
}
