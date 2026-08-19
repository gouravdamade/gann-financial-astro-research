export type Xe3Decision =
  | 'SUPPORTIVE'
  | 'ADVERSE'
  | 'MIXED'
  | 'NEUTRAL'
  | 'UNKNOWN_MORE_EVIDENCE_REQUIRED'
  | 'REJECT_EVENT_IDENTITY'

export type Xe3EvidenceClassification =
  | 'FOUNDER_RESEARCH_HYPOTHESIS'
  | 'SOURCE_BACKED_CLASSICAL_CANDIDATE'

export type Xe3SourceReference = {
  sourceId: string
  edition: string
  locator: string
  connection: string
}

export type Xe3Review = {
  decision: Xe3Decision | null
  evidenceClassification: Xe3EvidenceClassification | null
  reasoning: string
  rejectionReason: string
  reviewer: string
  reviewTimestampUtc: string | null
  sourceReferences: Xe3SourceReference[]
  outcomeBlindAttestation: boolean
  priceDataRead: false
}

export type Xe3EventIdentity = {
  eventId: string
  eventHash: string
  sideIdentity: 'USD' | 'JPY'
  instrumentIdentity: string
  chartId: string
  chartHypothesisId: string
  transitBody: string
  natalTarget: string
  aspectType: string
  applyingStartUtc: string
  exactUtc: string
  separatingEndUtc: string
  identityStatus: 'SINGLE_PASS_VERIFIED'
  astronomyContract: string
  ayanamsha: string
  nodePolicy: string
  orbContract: { profileId: string; exactAngleDeg: number; maxOrbDeg: number }
}

export type Xe3ReviewRow = {
  eventIdentity: Xe3EventIdentity
  identityStatus: 'SINGLE_PASS_VERIFIED'
  motionPhaseAtExact: { phase: string; speedDegPerDay: number } | null
  review: Xe3Review
}

export type Xe3SideWorkbench = {
  sideIdentity: 'USD' | 'JPY'
  instrumentIdentity: string
  chartId: string
  chartHypothesisId: string
  blankPacketFile: string
  blankPacketSha256: string
  identityIntegrityManifestFile: string
  identityIntegrityManifestSha256: string
  latestReviewRevisionHash: string | null
  completion: {
    status: string
    counts: Record<string, number>
  }
  rows: Xe3ReviewRow[]
}

export type Xe3Guardrails = {
  experimental: true
  classicalDoctrine: false
  priceDataRead: false
  priceOutcomeRead: false
  liveMt5Read: false
  fieldsRead: false
  sbcRead: false
  autoSuggestRead: false
  llmPolarityInference: false
  marketDirectionInferred: false
  modeOnePromotion: false
  executionAllowed: false
  automaticOrderPlacement: false
  financiallyValidated: false
}

export type Xe3Workbench = {
  contract: 'XE3_OUTCOME_BLIND_SIGN_ADMISSION_WORKBENCH_V1'
  profileId: 'XE3_OUTCOME_BLIND_CHART_CONDITIONED_SIGN_ADMISSION_V1'
  toolVersion: string
  datasetStatus: 'TOUCHED_DEV'
  datasetLabel: string
  allowedDecisions: Xe3Decision[]
  allowedEvidenceClassifications: Xe3EvidenceClassification[]
  sides: Xe3SideWorkbench[]
  signedEvidenceStatus: 'NONE' | 'PARTIAL' | 'NON_PROJECTABLE_ONLY'
  ledgerHash: string
  guardrails: Xe3Guardrails
}

export type Xe3ReviewRevisionRequest = {
  side: 'USD' | 'JPY'
  baseRevisionHash: string | null
  reviewer: string
  outcomeBlindAttestation: true
  rows: Xe3ReviewRow[]
}

export type Xe3ReviewRevisionResult = {
  sideIdentity: 'USD' | 'JPY'
  reviewRevisionHash: string
  parentRevisionHash: string | null
  completion: { status: string; counts: Record<string, number> }
  ledgerHash: string
  signedEvidenceStatus: string
  executionAllowed: false
}

export type Xe3Ledger = {
  contract: 'XE3_SIGNED_EVIDENCE_LEDGER_V1'
  profileId: string
  datasetStatus: 'TOUCHED_DEV'
  outcomeContractStatus: 'NOT_YET_FOUNDER_APPROVED'
  ledgerHash: string
  entries: Array<{
    eventId: string
    eventHash: string
    causalEventId: string
    sideIdentity: 'USD' | 'JPY'
    exactUtc: string
    scalarProjection: { mappingVersion: string; status: string; value: number | null }
    contributionIncluded: boolean
    review: Xe3Review
  }>
  sideStates: Record<string, { reviewRevisionHash: string | null; completion: { status: string; counts: Record<string, number> } }>
  guardrails: Xe3Guardrails
}

export type Xe3TransformComparison = {
  contract: 'XE3_REAL_SIGNED_EVIDENCE_XE2_TRANSFORM_PREVIEW_V1'
  ledgerHash: string
  datasetStatus: 'TOUCHED_DEV'
  comparisons: Array<{
    transformId: string
    transform: { label: string; parameters: Record<string, number | string> }
    signedStateVector: { state: string; positive: number; negative: number; signedRaw: number | null; signedNormalized: number | null; activity: number; unknownCount: number }
    contributions: Array<{ eventId: string; sideIdentity: 'USD' | 'JPY'; status: string; value: number | null; reason: string | null }>
    outcomeEvaluationStatus: 'BLOCKED'
  }>
  guardrails: Xe3Guardrails
}

export type Xe3Preregistration = {
  contract: 'XE3_PREREGISTERED_CAUSAL_MODIFIER_TRIAL_V1'
  status: 'NOT_FROZEN' | 'FROZEN'
  freezeReady: boolean
  ledgerHash: string
  frozenRecord: { preregistrationHash: string } | null
  datasetStatus: 'TOUCHED_DEV'
  outcomeContractStatus: 'NOT_YET_FOUNDER_APPROVED'
  sourceCommitRequired: true
  guardrails: Xe3Guardrails
}
