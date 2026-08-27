// @vitest-environment jsdom

import '@testing-library/jest-dom/vitest'
import { cleanup, render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { afterEach, describe, expect, it, vi } from 'vitest'
import type { FounderReviewWorkbench } from './types'
import { FounderReviewWorkbench as FounderReviewSurface } from './views/FounderReviewWorkbench'

const apiMocks = vi.hoisted(() => ({
  fetchFounderReviewWorkbench: vi.fn(),
  exportFounderReviewPacket: vi.fn(),
}))

vi.mock('./api', () => ({
  fetchFounderReviewWorkbench: apiMocks.fetchFounderReviewWorkbench,
  exportFounderReviewPacket: apiMocks.exportFounderReviewPacket,
}))

const eventIdentity = {
  applyingStartUtc: '2025-04-01T11:27:17Z',
  aspectType: 'square',
  astronomyContract: 'RAMAN_SIDEREAL_SWISSEPH_TRUE_NODE_GEOCENTRIC_V1',
  ayanamsha: 'Raman',
  chartHypothesisId: 'USD_HYPOTHESIS',
  chartId: 'USD_CHART',
  eventContract: 'CHART_CONDITIONED_TRANSIT_EVENT_RANGE_V1',
  eventHash: 'EVENT_HASH',
  eventId: 'TN_EVENT_1',
  exactUtc: '2025-04-01T16:19:44Z',
  generatorVersion: 'compiler_v1',
  instrumentIdentity: 'FX_CURRENCY:USD',
  natalTarget: 'MOON',
  nodePolicy: 'TRUE_NODE_RAHU_KETU_OPPOSITION_V1',
  orbContract: {
    aspectType: 'square',
    directionPolicy: 'ASPECT_GEOMETRY_NEVER_SUPPLIES_DIRECTION_BY_ITSELF',
    doctrineStatus: 'ANGULAR_GEOMETRY_ONLY_NOT_DIRECTION_DOCTRINE',
    exactAngleDeg: 90,
    maxOrbDeg: 3,
    profileHash: 'PROFILE_HASH',
    profileId: 'ASPECT_STRENGTH_V0',
  },
  separatingEndUtc: '2025-04-01T21:13:29Z',
  sideIdentity: 'USD' as const,
  transitBody: 'MOON',
}

const blankReview = {
  evidenceClassification: null,
  founderReasoning: '',
  rejectionReason: '',
  reviewTimestampUtc: null,
  reviewedPolarity: null,
  reviewer: '',
  sourceReferences: [],
}

const workbench = {
  contract: 'FOUNDER_REVIEW_WORKBENCH_V1',
  schemaVersion: 1,
  toolVersion: 'founder_review_workbench_v1',
  allowedFounderPolarityDecisions: ['SUPPORTIVE', 'ADVERSE', 'MIXED', 'NEUTRAL', 'UNKNOWN_MORE_EVIDENCE_REQUIRED', 'REJECT_EVENT_IDENTITY'],
  allowedEvidenceClassifications: ['FOUNDER_RESEARCH_HYPOTHESIS', 'SOURCE_BACKED_CLASSICAL_CANDIDATE'],
  reviewStatuses: ['REVIEW_NOT_STARTED', 'REVIEW_IN_PROGRESS', 'REVIEW_COMPLETE', 'REVIEW_COMPLETE_WITH_UNKNOWNS'],
  guardrails: { blankPacketsReadOnly: true, priceDataRead: false, sbcRead: false, llmRead: false, catalogueAdmission: false, directionalWaveRendered: false, executionAllowed: false },
  sides: [
    {
      sideIdentity: 'USD', instrumentIdentity: 'FX_CURRENCY:USD', chartId: 'USD_CHART', chartHypothesisId: 'USD_HYPOTHESIS',
      blankPacketId: 'BLANK:USD', blankPacketFile: 'USD_BLANK.json', blankPacketSha256: 'BLANK_HASH',
      identityIntegrityManifestId: 'MANIFEST:USD', identityIntegrityManifestFile: 'USD_MANIFEST.json', identityIntegrityManifestSha256: 'MANIFEST_HASH',
      eventCompiler: { ephemerisProvider: 'Swiss Ephemeris', ephemerisVersion: '2.10.03' }, ephemerisVersion: '2.10.03', ephemerisVersionProvenance: 'PACKET_COMPILER_METADATA', ephemerisVersionSourcePacketSha256: 'BLANK_HASH',
      sourcePacketStatus: 'BLANK_FOUNDER_REVIEW_REQUIRED', founderCompletionStatus: 'REVIEW_NOT_STARTED', reviewedPacketHash: 'REVIEW_HASH',
      completeness: { eligibleRows: 1, decidedRows: 0, unknownRows: 0, rejectedRows: 0, incompleteRows: 1, classicalCandidates: 0, founderResearchHypotheses: 0, nonReviewableRows: 0 },
      rows: [{ eligible: true, identityStatus: 'SINGLE_PASS_VERIFIED', identityChecks: { eventIdMatchesAudit: true, eventHashMatchesAudit: true, blankPacketHashMatchesManifest: true, integrityManifestHash: 'MANIFEST_HASH', listedAsVerified: true, auditChecksPass: true }, motionPhaseAtExact: null, eventIdentity, founderReview: blankReview }],
    },
    {
      sideIdentity: 'JPY', instrumentIdentity: 'FX_CURRENCY:JPY', chartId: 'JPY_CHART', chartHypothesisId: 'JPY_HYPOTHESIS',
      blankPacketId: 'BLANK:JPY', blankPacketFile: 'JPY_BLANK.json', blankPacketSha256: 'BLANK_HASH',
      identityIntegrityManifestId: 'MANIFEST:JPY', identityIntegrityManifestFile: 'JPY_MANIFEST.json', identityIntegrityManifestSha256: 'MANIFEST_HASH',
      eventCompiler: { ephemerisProvider: 'Swiss Ephemeris', ephemerisVersion: '2.10.03' }, ephemerisVersion: '2.10.03', ephemerisVersionProvenance: 'PACKET_COMPILER_METADATA', ephemerisVersionSourcePacketSha256: 'BLANK_HASH',
      sourcePacketStatus: 'BLANK_FOUNDER_REVIEW_REQUIRED', founderCompletionStatus: 'REVIEW_NOT_STARTED', reviewedPacketHash: 'REVIEW_HASH',
      completeness: { eligibleRows: 1, decidedRows: 0, unknownRows: 0, rejectedRows: 0, incompleteRows: 1, classicalCandidates: 0, founderResearchHypotheses: 0, nonReviewableRows: 0 },
      rows: [{ eligible: true, identityStatus: 'SINGLE_PASS_VERIFIED', identityChecks: { eventIdMatchesAudit: true, eventHashMatchesAudit: true, blankPacketHashMatchesManifest: true, integrityManifestHash: 'MANIFEST_HASH', listedAsVerified: true, auditChecksPass: true }, motionPhaseAtExact: null, eventIdentity: { ...eventIdentity, sideIdentity: 'JPY', instrumentIdentity: 'FX_CURRENCY:JPY', chartId: 'JPY_CHART', chartHypothesisId: 'JPY_HYPOTHESIS', eventId: 'TN_EVENT_2' }, founderReview: { ...blankReview, sourceReferences: [] } }],
    },
  ],
} as unknown as FounderReviewWorkbench

afterEach(() => {
  cleanup()
  vi.clearAllMocks()
})

describe('FounderReviewWorkbench', () => {
  it('loads with blank decisions and neutral facts only', async () => {
    apiMocks.fetchFounderReviewWorkbench.mockResolvedValue(workbench)

    render(<FounderReviewSurface onClose={() => undefined} />)

    expect(await screen.findByText('Founder Review')).toBeInTheDocument()
    expect(screen.getAllByLabelText('Decision')).toHaveLength(2)
    expect(screen.getAllByLabelText('Decision')[0]).toHaveValue('')
    expect(screen.queryByText(/bullish|bearish/i)).not.toBeInTheDocument()
    expect(screen.getAllByText('SINGLE PASS VERIFIED')).toHaveLength(2)
    expect(screen.getAllByText(/Swiss Ephemeris 2\.10\.03/)).toHaveLength(2)
  })

  it('marks directional reasoning as required and blocks a blank export', async () => {
    apiMocks.fetchFounderReviewWorkbench.mockResolvedValue(workbench)
    const user = userEvent.setup()
    render(<FounderReviewSurface onClose={() => undefined} />)

    await screen.findByText('Founder Review')
    await user.selectOptions(screen.getAllByLabelText('Decision')[0], 'SUPPORTIVE')
    expect(screen.getByText('Founder reasoning (required)')).toBeInTheDocument()
    expect(screen.getByPlaceholderText('Enter founder reasoning before exporting')).toBeRequired()
    expect(screen.queryByText('Founder reasoning (optional)')).not.toBeInTheDocument()
    await user.click(screen.getByRole('button', { name: /Export founder-review packets/i }))

    expect(await screen.findByText(/SUPPORTIVE requires non-empty founder reasoning/)).toBeInTheDocument()
    expect(apiMocks.exportFounderReviewPacket).not.toHaveBeenCalled()
  })

  it('exports only the founder-entered decision and preserves blank rows', async () => {
    apiMocks.fetchFounderReviewWorkbench.mockResolvedValue(workbench)
    apiMocks.exportFounderReviewPacket.mockResolvedValue({
      reviewedPacketFile: 'reviewed.json', reviewedPacketSha256: 'FILE_HASH', reviewedPacketHash: 'PACKET_HASH',
      reviewedManifestFile: 'manifest.json', reviewedManifestSha256: 'MANIFEST_HASH', completenessFile: 'complete.json',
      statusFile: 'status.json', markdownFile: 'reviewed.md', founderCompletionStatus: 'REVIEW_IN_PROGRESS',
      counts: { eligibleRows: 1, decidedRows: 1, unknownRows: 0, rejectedRows: 0, incompleteRows: 0, classicalCandidates: 0, founderResearchHypotheses: 1, nonReviewableRows: 0 },
    })
    const user = userEvent.setup()
    render(<FounderReviewSurface onClose={() => undefined} />)

    await screen.findByText('Founder Review')
    await user.selectOptions(screen.getAllByLabelText('Decision')[0], 'SUPPORTIVE')
    await user.selectOptions(screen.getAllByLabelText('Evidence classification')[0], 'FOUNDER_RESEARCH_HYPOTHESIS')
    await user.type(screen.getByPlaceholderText(/Enter founder reasoning/i), 'Founder-entered research observation.')
    await user.type(screen.getByPlaceholderText(/Enter your name/i), 'Founder')
    await user.click(screen.getByRole('button', { name: /Export founder-review packets/i }))

    expect(apiMocks.exportFounderReviewPacket).toHaveBeenCalledWith(expect.objectContaining({
      side: 'USD',
      rows: expect.arrayContaining([expect.objectContaining({
        eventIdentity: expect.objectContaining({ eventId: 'TN_EVENT_1' }),
        founderReview: expect.objectContaining({ reviewedPolarity: 'SUPPORTIVE', evidenceClassification: 'FOUNDER_RESEARCH_HYPOTHESIS', reviewer: 'Founder' }),
      })]),
    }))
    expect(apiMocks.exportFounderReviewPacket).toHaveBeenCalledWith(expect.objectContaining({ side: 'JPY' }))
  })
})
