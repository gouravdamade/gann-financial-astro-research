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
  contract: 'XE1_EXPERIMENTAL_EVIDENCE_LAB_V1', codeCommit: '36bea0ba321503d809c3f88a22d06dc517809a2c',
  profile: {
    contract: 'XE1_EXPERIMENTAL_PROFILE_V1', schemaVersion: 1, profileId: 'XE1_EVIDENCE_ROLE_MODIFIER_ABLATION_V1', codeCommit: '36bea0ba321503d809c3f88a22d06dc517809a2c', profileHash: 'abc123',
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

const comparison: ExperimentalComparisonResponse = {
  contract: 'XE1_TRANSFORM_COMPARISON_V1', codeCommit: profile.profile.codeCommit, profileId: profile.profile.profileId, profileHash: profile.profile.profileHash, dataMode: 'SYNTHETIC', guardrails,
  comparisons: ['XE1_BASE_DIRECTIONAL_V1', 'XE1_BOUNDED_EXP_MULTIPLIER_V1'].map((transformId) => ({ transformId, stateVector: snapshot.stateVector, modifier: snapshot.modifier, quality: snapshot.quality })),
}

const ledger: ExperimentalTrialLedger = {
  contract: 'XE1_EXPERIMENTAL_TRIAL_LEDGER_V1', codeCommit: profile.profile.codeCommit, profileHash: profile.profile.profileHash, ledgerId: 'ledger', guardrails,
  datasetGovernance: { APRIL_2025_STATUS: 'TOUCHED_DEV', pristineHoldoutUsed: false, exploratoryControlsLabel: 'EXPLORATORY_TOUCHED' },
  entries: [{ trialId: 'APRIL', experimentProfileId: profile.profile.profileId, experimentProfileHash: 'abc123', transformVersion: 'v1', parameterSet: { beta: 0 }, datasetId: 'APRIL_2025', datasetStatus: 'TOUCHED_DEV', result: 'INCONCLUSIVE', notes: 'not a holdout', codeCommit: 'test', createdAtUtc: '2026-08-17T00:00:00Z', immutableAfterEvaluation: true, entryHash: 'a'.repeat(64) }],
}

afterEach(() => { cleanup(); vi.clearAllMocks() })

describe('ExperimentalLabWorkspace', () => {
  it('renders the explicit safety banner, raw evidence, vector, and immutable trial record', async () => {
    api.fetchExperimentalEvidenceProfile.mockResolvedValue(profile)
    api.fetchExperimentalEvidenceSnapshot.mockResolvedValue(snapshot)
    api.compareExperimentalEvidenceTransforms.mockResolvedValue(comparison)
    api.fetchExperimentalEvidenceTrialLedger.mockResolvedValue(ledger)
    render(<ExperimentalLabWorkspace />)
    expect(await screen.findByText('EXPERIMENTAL - NOT CLASSICAL - NOT VALIDATED - NO EXECUTION')).toBeInTheDocument()
    expect(screen.getByText('Immutable raw observations')).toBeInTheDocument()
    expect(screen.getByText('Code 36bea0ba3215')).toBeInTheDocument()
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
})
