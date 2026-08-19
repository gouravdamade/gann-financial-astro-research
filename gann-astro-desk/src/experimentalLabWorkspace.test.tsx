// @vitest-environment jsdom

import '@testing-library/jest-dom/vitest'
import { cleanup, render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { afterEach, describe, expect, it, vi } from 'vitest'
import type {
  ExperimentalComparisonResponse,
  ExperimentalProfileResponse,
  ExperimentalSnapshot,
  ExperimentalTrialLedger,
} from './experimentalEvidenceTypes'

const api = vi.hoisted(() => ({
  compareExperimentalEvidenceTransforms: vi.fn(),
  fetchExperimentalEvidenceProfile: vi.fn(),
  fetchExperimentalEvidenceSnapshot: vi.fn(),
  fetchExperimentalEvidenceTrialLedger: vi.fn(),
  compareXe2ScopedEvidenceTransforms: vi.fn(),
  fetchXe2ScopedEvidenceProfile: vi.fn(),
  fetchXe2ScopedEvidenceSnapshot: vi.fn(),
  fetchXe2ScopedEvidenceTrialLedger: vi.fn(),
  fetchXe3OutcomeBlindWorkbench: vi.fn(),
  fetchXe3SignedLedger: vi.fn(),
  fetchXe3TransformPreview: vi.fn(),
  fetchXe3Preregistration: vi.fn(),
  saveXe3OutcomeBlindReviewRevision: vi.fn(),
  freezeXe3Preregistration: vi.fn(),
}))

vi.mock('./api', () => api)

import { ExperimentalLabWorkspace } from './views/ExperimentalLabWorkspace'

const guardrails = {
  experimental: true,
  classicalDoctrine: false,
  priceDataRead: false,
  priceOutcomeRead: false,
  sbcRead: false,
  fieldsPath: false,
  autoSuggestPath: false,
  mlPath: false,
  mt5Path: false,
  executionAllowed: false,
  automaticOrderPlacement: false,
  financiallyValidated: false,
} as const

const profile: ExperimentalProfileResponse = {
  contract: 'XE1_EXPERIMENTAL_EVIDENCE_LAB_V1', codeCommit: '9c988395e9dbff09a4c3f60912fa1edac48ae375',
  profile: {
    contract: 'XE1_EXPERIMENTAL_PROFILE_V1', schemaVersion: 1, profileId: 'XE1_EVIDENCE_ROLE_MODIFIER_ABLATION_V1', codeCommit: '9c988395e9dbff09a4c3f60912fa1edac48ae375', profileHash: 'abc123',
    bindings: [
      { featureKey: 'positive', role: 'SIGN', transformId: 'XE1_BASE_DIRECTIONAL_V1', parameters: {}, assignmentOrigin: 'fixture', marketDomain: 'NONE', experimentalStatus: 'synthetic' },
      { featureKey: 'negative', role: 'SIGN', transformId: 'XE1_BASE_DIRECTIONAL_V1', parameters: {}, assignmentOrigin: 'fixture', marketDomain: 'NONE', experimentalStatus: 'synthetic' },
    ],
    causalAggregationPolicy: 'one per group', oscillatorProjectionId: 'vector', timingKernelId: null, pairPolicy: { enabled: false, contract: 'none' }, datasetStatus: 'SYNTHETIC', trialLedgerPolicy: 'immutable', executionAllowed: false,
  },
  availableDataModes: ['SYNTHETIC', 'TOUCHED_DEV', 'MANUAL'],
  availableTransforms: ['XE1_BASE_DIRECTIONAL_V1', 'XE1_BOUNDED_EXP_MULTIPLIER_V1'],
  guardrails,
}

const snapshot: ExperimentalSnapshot = {
  contract: 'XE1_EXPERIMENTAL_EVIDENCE_LAB_V1', schemaVersion: 1, codeCommit: profile.profile.codeCommit, snapshotId: 'snapshot', profile: profile.profile,
  dataMode: 'SYNTHETIC', datasetStatus: 'SYNTHETIC', datasetLabel: 'SYNTHETIC', rawEvidenceImmutable: true, manualInputStatus: 'NOT_APPLICABLE', transformId: 'XE1_BOUNDED_EXP_MULTIPLIER_V1',
  rawObservations: [
    { observationId: 'one', eventId: 'event-one', causalEventId: 'cause-one', causalClassification: 'UNIQUE', derivationRole: 'PRIMARY_EVIDENCE', timestampUtc: '2025-04-01T00:00:00Z', sourceProfileId: 'fixture', featureKey: 'positive', rawValue: 1, rawUnit: 'units', valueType: 'SIGNED_SCALAR', sourceSemantic: 'synthetic', sourceStatus: 'SYNTHETIC', provenance: ['fixture'], unknownReasons: [] },
    { observationId: 'two', eventId: 'event-two', causalEventId: 'cause-two', causalClassification: 'AMBIGUOUS', derivationRole: 'PRIMARY_EVIDENCE', timestampUtc: '2025-04-01T00:00:00Z', sourceProfileId: 'fixture', featureKey: 'negative', rawValue: null, rawUnit: 'units', valueType: 'UNKNOWN', sourceSemantic: 'synthetic', sourceStatus: 'UNKNOWN', provenance: ['fixture'], unknownReasons: ['missing'] },
  ],
  modifier: { family: 'POSITIVE_MULTIPLIER', contract: 'XE1_BOUNDED_EXP_MULTIPLIER_V1', parameters: { beta: 0.65, mMin: 0.5, mMax: 1.5 }, z: 0.4, status: 'KNOWN', value: 1.3, nonSignFlipGuaranteed: true, reason: null },
  causalContributions: [
    { causalEventId: 'cause-one', sourceObservationIds: ['one'], derivedChildIds: [], causalClassification: 'UNIQUE', sourceObservationId: 'one', rawDirectionalValue: 1, value: 1.3, status: 'ACTIVE', reason: null },
    { causalEventId: 'cause-two', sourceObservationIds: ['two'], derivedChildIds: [], causalClassification: 'AMBIGUOUS', value: null, status: 'AMBIGUOUS_CAUSE_FAIL_CLOSED', reason: 'identity unresolved' },
  ],
  stateVector: { state: 'SUPPORTIVE', positive: 1.3, negative: 0, directionalRaw: 1.3, activity: 1.3, directionalNormalized: 1, conflictLinear: 0, conflictQuad: 0, conflictEntropy: 0, unknownGroupCount: 1 },
  quality: { knownDirectionalGroups: 1, unresolvedDirectionalGroups: 1, confidence: 0.5, confidenceUse: 'DISPLAY_ONLY_SEPARATE_FROM_DIRECTIONAL_EVIDENCE', confidenceMultipliesEvidence: false },
  experimentalOscillator: { contract: 'XE1_CATEGORICAL_STATE_VECTOR_V1', state: 'SUPPORTIVE', displayValue: 1, magnitudeState: 'experimental', marketForecast: false, executionAllowed: false },
  guardrails,
}

const emptySnapshot: ExperimentalSnapshot = {
  ...snapshot,
  dataMode: 'TOUCHED_DEV',
  datasetStatus: 'TOUCHED_DEV',
  datasetLabel: 'EXPLORATORY_TOUCHED',
  rawObservations: [],
  manualInputStatus: 'TOUCHED_DEV_INPUT_NOT_CONFIGURED',
  causalContributions: [],
  stateVector: {
    state: 'UNKNOWN_NO_ACTIVE_EVIDENCE',
    positive: 0,
    negative: 0,
    directionalRaw: null,
    activity: 0,
    directionalNormalized: null,
    conflictLinear: null,
    conflictQuad: null,
    conflictEntropy: null,
    unknownGroupCount: 0,
  },
  experimentalOscillator: {
    ...snapshot.experimentalOscillator,
    state: 'UNKNOWN_NO_ACTIVE_EVIDENCE',
    displayValue: null,
  },
}

const comparison: ExperimentalComparisonResponse = {
  contract: 'XE1_TRANSFORM_COMPARISON_V1', codeCommit: profile.profile.codeCommit, profileId: profile.profile.profileId, profileHash: profile.profile.profileHash, dataMode: 'SYNTHETIC', guardrails,
  comparisons: ['XE1_BASE_DIRECTIONAL_V1', 'XE1_BOUNDED_EXP_MULTIPLIER_V1'].map((transformId) => ({ transformId, stateVector: snapshot.stateVector, modifier: snapshot.modifier, quality: snapshot.quality })),
}

const ledger: ExperimentalTrialLedger = {
  contract: 'XE1_EXPERIMENTAL_TRIAL_LEDGER_V1', codeCommit: profile.profile.codeCommit, profileHash: profile.profile.profileHash, ledgerId: 'ledger', guardrails,
  datasetGovernance: { APRIL_2025_STATUS: 'TOUCHED_DEV', pristineHoldoutUsed: false, exploratoryControlsLabel: 'EXPLORATORY_TOUCHED' },
  entries: [{ trialId: 'APRIL', experimentProfileId: profile.profile.profileId, experimentProfileHash: 'abc123', transformVersion: 'v1', parameterSet: { beta: 0 }, datasetId: 'APRIL_2025', datasetStatus: 'TOUCHED_DEV', result: 'INCONCLUSIVE', notes: 'not a holdout', codeCommit: 'test', createdAtUtc: '2026-08-17T00:00:00Z', immutableAfterEvaluation: true, entryHash: 'a'.repeat(64) }],
}

const xe2Profile = {
  contract: 'XE2_CAUSAL_SCOPED_EVIDENCE_LAB_V1' as const,
  profile: {
    contract: 'XE2_CAUSAL_SCOPED_PROFILE_V1' as const, schemaVersion: 1 as const, profileId: 'XE2_CAUSAL_SCOPED_SPEED_MODIFIER_TOURNAMENT_V1' as const,
    acceptanceBaselineCommit: 'ccb4ee5c17dc1cce3f989832ac22196bf07b8806', datasetStatus: 'TOUCHED_DEV' as const,
    profilePurpose: 'REAL_ASTRONOMICAL_INPUT_PLUS_SYNTHETIC_SIGN_TEST_ONLY', realSignedEvidenceStatus: 'NOT_ADMITTED_NO_REVIEWED_SIGNED_EVIDENCE',
    causalAggregationPolicy: 'one sign per event', globalModifierDefaultAllowed: false as const, modifierScopeRequired: 'CAUSAL_EVENT_ID' as const,
    stackingAllowed: false as const, executionAllowed: false as const, profileHash: 'xe2hash', transforms: [
      { transformId: 'XE2_M0_BASE_SYNTHETIC_SIGN_TEST_V1', label: 'M0', family: 'BASE', parameters: {} },
      { transformId: 'XE2_M1_SCOPED_POSITIVE_SPEED_MULTIPLIER_V1', label: 'M1', family: 'POSITIVE_SCOPED_MULTIPLIER', parameters: { beta: 0.8 } },
      { transformId: 'XE2_M2_SPEED_SEPARATE_CHANNEL_V1', label: 'M2', family: 'SEPARATE_CHANNEL', parameters: {} },
      { transformId: 'XE2_M3_SPEED_INTERACTION_V1', label: 'M3', family: 'INTERACTION', parameters: { gamma: 0.5 } },
      { transformId: 'XE2_M4_MOTION_CONTEXT_GATE_V1', label: 'M4', family: 'CONTEXT_GATE', parameters: {} },
    ],
  },
  availableTransforms: ['XE2_M0_BASE_SYNTHETIC_SIGN_TEST_V1', 'XE2_M1_SCOPED_POSITIVE_SPEED_MULTIPLIER_V1'],
  realEvidenceAdmission: { astronomicalIdentity: 'ADMITTED_HASH_LINKED', rawAstronomicalSpeed: 'ADMITTED_RAW_UNITS', reviewedSignedEvidence: 'NOT_ADMITTED_NONE_EXISTS', syntheticSignChannel: 'SYNTHETIC_SIGN_TEST_ONLY', marketDirection: 'BLOCKED_NO_REAL_SIGNED_EVIDENCE' },
  guardrails: { ...guardrails, marketForecast: false as const },
}

const xe2Snapshot = {
  contract: 'XE2_CAUSAL_SCOPED_EVIDENCE_LAB_V1' as const, schemaVersion: 1 as const, snapshotId: 'xe2snapshot', profile: xe2Profile.profile,
  datasetStatus: 'TOUCHED_DEV' as const, datasetLabel: 'TOUCHED DEV - REAL ASTRONOMY + SYNTHETIC SIGN TEST ONLY',
  astronomySource: {
    reviewedPacketFile: 'reviewed.json',
    reviewedPacketSha256: 'reviewed'.repeat(16),
    identityIntegrityManifestSha256: 'integrity'.repeat(8),
    directionPolicy: 'ASPECT_GEOMETRY_NEVER_SUPPLIES_DIRECTION_BY_ITSELF',
  },
  normalization: { contract: 'MOON_RELATIVE_MEAN_SPEED_V1', body: 'MOON', rawUnit: 'deg/day', referenceSpeedDegPerDay: 13.176358, formula: '(raw-reference)/reference', referenceOrigin: 'astronomy only' },
  transformId: 'XE2_M1_SCOPED_POSITIVE_SPEED_MULTIPLIER_V1', transform: xe2Profile.profile.transforms[1], rawEvidenceImmutable: true as const,
  rawObservations: [], scopeBindings: [], marketDirectionStatus: 'BLOCKED_NO_REAL_SIGNED_EVIDENCE' as const,
  marketOutcome: { datasetStatus: 'TOUCHED_DEV', outcomeEvaluationStatus: 'BLOCKED_NO_GOVERNED_OFFLINE_OUTCOME_DATASET' },
  causalContributions: [{
    causalEventId: 'CAUSE', eventId: 'TN_HASH', eventHash: 'a'.repeat(64),
    timestampUtc: '2025-04-01T16:19:44Z', transitBody: 'MOON', natalTarget: 'MOON', aspectType: 'square',
    applyingStartUtc: '2025-04-01T11:27:17Z', separatingEndUtc: '2025-04-01T21:13:29Z', identityStatus: 'SINGLE_PASS_VERIFIED' as const,
    sourceObservationIds: [], syntheticSignObservationId: 'synthetic', rawSyntheticSignTestValue: 1, rawSpeedDegPerDay: 14.1, speedNormalizationContract: 'MOON_RELATIVE_MEAN_SPEED_V1', zSpeed: 0.07, motionPhaseAtExact: 'DIRECT',
    scope: { modifierObservationId: 'speed', targetCausalEventId: 'CAUSE', scopeType: 'CAUSAL_EVENT_ID' as const, scopeStatus: 'BOUND' as const, globalDefaultApplied: false as const }, multiplierOrInteraction: 1.05, separateChannelValue: null, contextGate: null, value: 1.05, status: 'ACTIVE' as const, reason: null, signEvidenceStatus: 'SYNTHETIC_SIGN_TEST_ONLY_NOT_MARKET_EVIDENCE' as const,
  }],
  syntheticStateVector: { state: 'SYNTHETIC_SIGN_TEST_ONLY' as const, positive: 1.05, negative: 0, syntheticRaw: 1.05, syntheticNormalized: 1, activity: 1.05, conflict: 0, unknownCauseCount: 0 },
  guardrails: xe2Profile.guardrails,
}

const xe2Comparison = {
  contract: 'XE2_CAUSAL_SCOPED_TRANSFORM_COMPARISON_V1' as const, profileId: xe2Profile.profile.profileId, profileHash: xe2Profile.profile.profileHash, datasetStatus: 'TOUCHED_DEV' as const,
  comparisons: xe2Profile.profile.transforms.map((transform) => ({ transformId: transform.transformId, transform, syntheticStateVector: xe2Snapshot.syntheticStateVector, marketDirectionStatus: 'BLOCKED_NO_REAL_SIGNED_EVIDENCE' as const })), guardrails: xe2Profile.guardrails,
}

const xe2Ledger = {
  contract: 'XE2_CAUSAL_SCOPED_MODIFIER_TRIAL_LEDGER_V1' as const, ledgerId: 'xe2ledger', profileHash: xe2Profile.profile.profileHash,
  datasetGovernance: { datasetStatus: 'TOUCHED_DEV', outcomeEvaluationStatus: 'BLOCKED_NO_GOVERNED_OFFLINE_OUTCOME_DATASET', pristineHoldoutUsed: false },
  entries: [{ trialId: 'XE2_M0', transformId: 'XE2_M0_BASE_SYNTHETIC_SIGN_TEST_V1', result: 'NOT_EVALUATED' as const, notes: 'No outcome.', profileId: xe2Profile.profile.profileId, profileHash: xe2Profile.profile.profileHash, datasetStatus: 'TOUCHED_DEV' as const, marketOutcomeRead: false as const, immutableAfterEvaluation: true as const, entryHash: 'b'.repeat(64) }], ledgerHash: 'c'.repeat(64), guardrails: xe2Profile.guardrails,
}

afterEach(() => { cleanup(); vi.clearAllMocks() })

describe('ExperimentalLabWorkspace', () => {
  it('renders the explicit safety banner, raw evidence, vector, and immutable trial record', async () => {
    api.fetchExperimentalEvidenceProfile.mockResolvedValue(profile)
    api.fetchExperimentalEvidenceSnapshot.mockResolvedValue(snapshot)
    api.compareExperimentalEvidenceTransforms.mockResolvedValue(comparison)
    api.fetchExperimentalEvidenceTrialLedger.mockResolvedValue(ledger)
    render(<ExperimentalLabWorkspace />)
    const safetyText = await screen.findByText('EXPERIMENTAL - NOT CLASSICAL - NOT VALIDATED - NO EXECUTION')
    expect(safetyText).toBeInTheDocument()
    expect(safetyText.closest('.experimental-safety-banner')).toHaveClass('experimental-safety-banner')
    expect(screen.getByText('Immutable raw observations')).toBeInTheDocument()
    expect(screen.getByText('Raw fixture sealed')).toBeInTheDocument()
    expect(screen.queryByText('NEGATIVE EVIDENCE', { exact: true })).not.toBeInTheDocument()
    expect(screen.getAllByText('POSITIVE EVIDENCE', { exact: true }).length).toBeGreaterThan(0)
    expect(screen.getByText('positive evidence', { exact: true })).toBeInTheDocument()
    expect(screen.getByText('Code 9c988395e9db')).toBeInTheDocument()
    expect(screen.getByText('positive', { exact: true, selector: 'strong' })).toBeInTheDocument()
    expect(screen.getByText('One directional vote per causal group')).toBeInTheDocument()
    expect(screen.getByText('Categorical state vector, not a market forecast')).toBeInTheDocument()
    expect(screen.getByText('APRIL 2025: TOUCHED DEV')).toBeInTheDocument()
    expect(screen.getByText(/execution locked/i)).toBeInTheDocument()
  })

  it('refreshes snapshot and comparison on an explicit transform change without sending raw observations', async () => {
    api.fetchExperimentalEvidenceProfile.mockResolvedValue(profile)
    api.fetchExperimentalEvidenceSnapshot.mockResolvedValue(snapshot)
    api.compareExperimentalEvidenceTransforms.mockResolvedValue(comparison)
    api.fetchExperimentalEvidenceTrialLedger.mockResolvedValue(ledger)
    const user = userEvent.setup()
    render(<ExperimentalLabWorkspace />)
    await screen.findByText('Experimental Lab')
    await user.selectOptions(screen.getByLabelText('Experimental transform'), 'XE1_BASE_DIRECTIONAL_V1')
    await waitFor(() => expect(api.fetchExperimentalEvidenceSnapshot).toHaveBeenLastCalledWith({ dataMode: 'SYNTHETIC', transformId: 'XE1_BASE_DIRECTIONAL_V1' }))
    expect(api.fetchExperimentalEvidenceSnapshot.mock.calls.flat().some((value: unknown) => value === 'rawObservations')).toBe(false)
  })

  it('keeps empty touched development explicitly unknown without zero-like directional UI', async () => {
    api.fetchExperimentalEvidenceProfile.mockResolvedValue(profile)
    api.fetchExperimentalEvidenceSnapshot.mockResolvedValue(emptySnapshot)
    api.compareExperimentalEvidenceTransforms.mockResolvedValue({ ...comparison, dataMode: 'TOUCHED_DEV' })
    api.fetchExperimentalEvidenceTrialLedger.mockResolvedValue(ledger)
    render(<ExperimentalLabWorkspace />)
    expect(await screen.findByText('No observations admitted')).toBeInTheDocument()
    expect(screen.getByText('TOUCHED DEV INPUT NOT CONFIGURED. This version deliberately accepts no frontend-invented evidence.')).toBeInTheDocument()
    expect(screen.getAllByText('UNKNOWN / NO ACTIVE EVIDENCE').length).toBeGreaterThan(0)
    expect(screen.getByText('D raw').parentElement).toHaveTextContent('Unknown')
    expect(screen.getByText('D norm').parentElement).toHaveTextContent('Unknown')
    expect(screen.getByText('Conflict').parentElement).toHaveTextContent('Unknown')
    expect(screen.getByText('MARKET INPUT: NONE')).toBeInTheDocument()
    expect(screen.queryByText('Raw fixture sealed')).not.toBeInTheDocument()
  })

  it('switches to XE2 without inventing a market sign or reading an outcome', async () => {
    api.fetchExperimentalEvidenceProfile.mockResolvedValue(profile)
    api.fetchExperimentalEvidenceSnapshot.mockResolvedValue(snapshot)
    api.compareExperimentalEvidenceTransforms.mockResolvedValue(comparison)
    api.fetchExperimentalEvidenceTrialLedger.mockResolvedValue(ledger)
    api.fetchXe2ScopedEvidenceProfile.mockResolvedValue(xe2Profile)
    api.fetchXe2ScopedEvidenceSnapshot.mockResolvedValue(xe2Snapshot)
    api.compareXe2ScopedEvidenceTransforms.mockResolvedValue(xe2Comparison)
    api.fetchXe2ScopedEvidenceTrialLedger.mockResolvedValue(xe2Ledger)
    const user = userEvent.setup()
    render(<ExperimentalLabWorkspace />)
    await screen.findByText('Experimental Lab')
    await user.selectOptions(screen.getByLabelText('Experimental research profile'), 'XE2')
    expect(await screen.findByText('REAL ASTRONOMY: HASH-LINKED')).toBeInTheDocument()
    expect(screen.getByText('SIGNED MARKET EVIDENCE: NONE')).toBeInTheDocument()
    expect(screen.getAllByText('SYNTHETIC SIGN TEST ONLY').length).toBeGreaterThan(0)
    expect(screen.getByText('Outcome evaluation').parentElement).toHaveTextContent('BLOCKED')
    expect(api.fetchXe2ScopedEvidenceSnapshot).toHaveBeenCalledWith({ transformId: 'XE2_M1_SCOPED_POSITIVE_SPEED_MULTIPLIER_V1' })
  })

  it('exposes XE3 as an explicit outcome-blind surface and informs the application shell', async () => {
    api.fetchExperimentalEvidenceProfile.mockResolvedValue(profile)
    api.fetchExperimentalEvidenceSnapshot.mockResolvedValue(snapshot)
    api.compareExperimentalEvidenceTransforms.mockResolvedValue(comparison)
    api.fetchExperimentalEvidenceTrialLedger.mockResolvedValue(ledger)
    api.fetchXe3OutcomeBlindWorkbench.mockRejectedValue(new Error('packet test only'))
    api.fetchXe3SignedLedger.mockRejectedValue(new Error('packet test only'))
    api.fetchXe3TransformPreview.mockRejectedValue(new Error('packet test only'))
    api.fetchXe3Preregistration.mockRejectedValue(new Error('packet test only'))
    const onOutcomeBlindReviewChange = vi.fn()
    const user = userEvent.setup()
    render(<ExperimentalLabWorkspace onOutcomeBlindReviewChange={onOutcomeBlindReviewChange} />)
    await screen.findByText('Experimental Lab')
    await user.selectOptions(screen.getByLabelText('Experimental research profile'), 'XE3')
    expect(await screen.findByText('OUTCOME-BLIND REVIEW - PRICE HIDDEN')).toBeInTheDocument()
    expect(onOutcomeBlindReviewChange).toHaveBeenLastCalledWith(true)
    expect(screen.queryByText('MARKET INPUT: NONE')).not.toBeInTheDocument()
  })
})
