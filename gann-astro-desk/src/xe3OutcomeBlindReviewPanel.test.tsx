// @vitest-environment jsdom

import '@testing-library/jest-dom/vitest'
import { cleanup, render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { afterEach, describe, expect, it, vi } from 'vitest'
import type { Xe3Ledger, Xe3Preregistration, Xe3TransformComparison, Xe3Workbench } from './xe3EvidenceTypes'

const api = vi.hoisted(() => ({
  fetchXe3OutcomeBlindWorkbench: vi.fn(),
  fetchXe3SignedLedger: vi.fn(),
  fetchXe3TransformPreview: vi.fn(),
  fetchXe3Preregistration: vi.fn(),
  saveXe3OutcomeBlindReviewRevision: vi.fn(),
  freezeXe3Preregistration: vi.fn(),
}))

vi.mock('./api', () => api)

import { Xe3OutcomeBlindReviewPanel } from './views/Xe3OutcomeBlindReviewPanel'

const guardrails = {
  experimental: true,
  classicalDoctrine: false,
  priceDataRead: false,
  priceOutcomeRead: false,
  liveMt5Read: false,
  fieldsRead: false,
  sbcRead: false,
  autoSuggestRead: false,
  llmPolarityInference: false,
  marketDirectionInferred: false,
  modeOnePromotion: false,
  executionAllowed: false,
  automaticOrderPlacement: false,
  financiallyValidated: false,
} as const

const eventIdentity = {
  eventId: 'TN_TEST_USD_001', eventHash: 'a'.repeat(64), sideIdentity: 'USD' as const, instrumentIdentity: 'FX_CURRENCY:USD',
  chartId: 'FX_CURRENCY_USD_US_INDEPENDENCE_17760704T165602Z_V1', chartHypothesisId: 'USD_US_INDEPENDENCE_PHILADELPHIA_EXACT_TIME_RESEARCH_V1',
  transitBody: 'MOON', natalTarget: 'SUN', aspectType: 'square', applyingStartUtc: '2025-04-01T00:00:00Z', exactUtc: '2025-04-01T06:00:00Z', separatingEndUtc: '2025-04-01T12:00:00Z',
  identityStatus: 'SINGLE_PASS_VERIFIED' as const, astronomyContract: 'SWISSEPH_RAMAN_SIDEREAL_V1', ayanamsha: 'RAMAN', nodePolicy: 'TRUE_NODE',
  orbContract: { profileId: 'TEST_ORB_V1', exactAngleDeg: 90, maxOrbDeg: 5 },
}

const blankReview = {
  decision: null,
  evidenceClassification: null,
  reasoning: '',
  rejectionReason: '',
  reviewer: '',
  reviewTimestampUtc: null,
  sourceReferences: [],
  outcomeBlindAttestation: false,
  priceDataRead: false as const,
}

const row = { eventIdentity, identityStatus: 'SINGLE_PASS_VERIFIED' as const, motionPhaseAtExact: { phase: 'DIRECT', speedDegPerDay: 13.4 }, review: blankReview }

const side = (identity: 'USD' | 'JPY') => ({
  sideIdentity: identity,
  instrumentIdentity: `FX_CURRENCY:${identity}`,
  chartId: identity === 'USD' ? eventIdentity.chartId : 'FX_CURRENCY_JPY_YEN_IPO_18890210T150000Z_V1',
  chartHypothesisId: identity === 'USD' ? eventIdentity.chartHypothesisId : 'JPY_YEN_IPO_TOKYO_EXACT_TIME_RESEARCH_V1',
  blankPacketFile: `${identity}_APRIL_2025_BLANK_POLARITY_REVIEW_V1.json`, blankPacketSha256: `${identity}`.repeat(32),
  identityIntegrityManifestFile: `${identity}.identity_integrity.manifest.json`, identityIntegrityManifestSha256: `I${identity}`.repeat(24), latestReviewRevisionHash: null,
  completion: { status: 'REVIEW_NOT_STARTED', counts: { eligibleRows: 1, decidedRows: 0, incompleteRows: 1 } },
  rows: [{ ...row, eventIdentity: { ...row.eventIdentity, sideIdentity: identity, eventId: `TN_TEST_${identity}_001` } }],
})

const workbench: Xe3Workbench = {
  contract: 'XE3_OUTCOME_BLIND_SIGN_ADMISSION_WORKBENCH_V1', profileId: 'XE3_OUTCOME_BLIND_CHART_CONDITIONED_SIGN_ADMISSION_V1', toolVersion: 'test', datasetStatus: 'TOUCHED_DEV',
  datasetLabel: 'TOUCHED DEV - OUTCOME-BLIND SIGN REVIEW ONLY', allowedDecisions: ['SUPPORTIVE', 'ADVERSE', 'MIXED', 'NEUTRAL', 'UNKNOWN_MORE_EVIDENCE_REQUIRED', 'REJECT_EVENT_IDENTITY'],
  allowedEvidenceClassifications: ['FOUNDER_RESEARCH_HYPOTHESIS', 'SOURCE_BACKED_CLASSICAL_CANDIDATE'], sides: [side('USD'), side('JPY')], signedEvidenceStatus: 'NONE', ledgerHash: 'l'.repeat(64), guardrails,
}

const ledger: Xe3Ledger = {
  contract: 'XE3_SIGNED_EVIDENCE_LEDGER_V1', profileId: workbench.profileId, datasetStatus: 'TOUCHED_DEV', outcomeContractStatus: 'NOT_YET_FOUNDER_APPROVED', ledgerHash: workbench.ledgerHash,
  entries: [], sideStates: { USD: { reviewRevisionHash: null, completion: side('USD').completion }, JPY: { reviewRevisionHash: null, completion: side('JPY').completion } }, guardrails,
}

const comparison: Xe3TransformComparison = {
  contract: 'XE3_REAL_SIGNED_EVIDENCE_XE2_TRANSFORM_PREVIEW_V1', ledgerHash: ledger.ledgerHash, datasetStatus: 'TOUCHED_DEV', guardrails,
  comparisons: ['M0', 'M1', 'M2', 'M3', 'M4'].map((id) => ({ transformId: id, transform: { label: `${id} frozen`, parameters: {} }, signedStateVector: { state: 'NO_PROJECTABLE_REAL_SIGNED_EVIDENCE', positive: 0, negative: 0, signedRaw: null, signedNormalized: null, activity: 0, unknownCount: 0 }, contributions: [], outcomeEvaluationStatus: 'BLOCKED' as const })),
}

const preregistration: Xe3Preregistration = {
  contract: 'XE3_PREREGISTERED_CAUSAL_MODIFIER_TRIAL_V1', status: 'NOT_FROZEN', freezeReady: false, ledgerHash: ledger.ledgerHash, frozenRecord: null,
  datasetStatus: 'TOUCHED_DEV', outcomeContractStatus: 'NOT_YET_FOUNDER_APPROVED', sourceCommitRequired: true, guardrails,
}

afterEach(() => { cleanup(); vi.clearAllMocks() })

function arrange(): void {
  api.fetchXe3OutcomeBlindWorkbench.mockResolvedValue(workbench)
  api.fetchXe3SignedLedger.mockResolvedValue(ledger)
  api.fetchXe3TransformPreview.mockResolvedValue(comparison)
  api.fetchXe3Preregistration.mockResolvedValue(preregistration)
  api.saveXe3OutcomeBlindReviewRevision.mockResolvedValue({ sideIdentity: 'USD', reviewRevisionHash: 'r'.repeat(64), parentRevisionHash: null, completion: side('USD').completion, ledgerHash: ledger.ledgerHash, signedEvidenceStatus: 'PARTIAL', executionAllowed: false })
}

describe('Xe3OutcomeBlindReviewPanel', () => {
  it('renders only immutable astronomical facts with price and outcome visibility blocked', async () => {
    arrange()
    render(<Xe3OutcomeBlindReviewPanel />)
    expect(await screen.findByText('OUTCOME-BLIND REVIEW - PRICE HIDDEN')).toBeInTheDocument()
    expect(screen.getByText('Packet-verified astronomy facts only')).toBeInTheDocument()
    expect(screen.getByText('NO REVIEW DECISION')).toBeInTheDocument()
    expect(screen.getByText('REAL SIGNED EVIDENCE - OUTCOME NOT EVALUATED')).toBeInTheDocument()
    expect(screen.getByText('OUTCOME EVALUATION: BLOCKED')).toBeInTheDocument()
    expect(screen.queryByText(/close price/i)).not.toBeInTheDocument()
    expect(screen.queryByText(/buy|sell/i)).not.toBeInTheDocument()
    expect(screen.getByRole('button', { name: /freeze signed-evidence trial/i })).toBeDisabled()
  })

  it('submits only an attested founder decision tied to the immutable event identity', async () => {
    arrange()
    const user = userEvent.setup()
    render(<Xe3OutcomeBlindReviewPanel />)
    await screen.findByText('TN_TEST_USD_001')
    await user.selectOptions(screen.getByLabelText('XE3 decision'), 'SUPPORTIVE')
    await user.selectOptions(screen.getByLabelText('XE3 evidence classification'), 'FOUNDER_RESEARCH_HYPOTHESIS')
    await user.type(screen.getByLabelText(/Reasoning/), 'Founder outcome-blind research rationale.')
    await user.type(screen.getByLabelText('XE3 reviewer'), 'Founder')
    await user.click(screen.getByLabelText('Outcome-blind attestation'))
    await user.click(screen.getByRole('button', { name: /save immutable usd revision/i }))
    await waitFor(() => expect(api.saveXe3OutcomeBlindReviewRevision).toHaveBeenCalledTimes(1))
    const request = api.saveXe3OutcomeBlindReviewRevision.mock.calls[0][0]
    expect(request.outcomeBlindAttestation).toBe(true)
    expect(request.rows[0].eventIdentity).toEqual(eventIdentity)
    expect(request.rows[0].review.decision).toBe('SUPPORTIVE')
    expect(request.rows[0].review.priceDataRead).toBe(false)
    expect(JSON.stringify(request)).not.toMatch(/priceOutcome|sbc|fields|mt5/i)
  })
})
