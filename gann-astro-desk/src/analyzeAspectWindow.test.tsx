// @vitest-environment jsdom

import '@testing-library/jest-dom/vitest'
import { cleanup, render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { AnalyzeAspectWindow } from './views/AnalyzeAspectWindow'
import type { AspectFamily, DataArtifact, DecisionPacket, EventDetail } from './types'

const mocks = vi.hoisted(() => ({
  fetchFamily: vi.fn(),
  fetchEventDetail: vi.fn(),
  fetchLiveDecision: vi.fn(),
  deleteAnnotation: vi.fn(),
  saveAnnotation: vi.fn(),
  saveReviewStatus: vi.fn(),
}))

vi.mock('./api', () => mocks)
vi.mock('./desktop', () => ({ openAnalyzeAspect: vi.fn() }))
vi.mock('./reviewProgress', () => ({
  canToggleReview: () => false,
  nextReviewStatus: () => 'pending',
  reviewButtonLabel: () => 'Review',
}))
vi.mock('./chartLayouts', () => ({
  defaultDrawingPreferences: () => ({}),
  defaultRsiPaneSettings: () => ({ visible: false, period: 14, source: 'close', timeframe: 'chart', levels: [30, 50, 70] }),
  downloadLayoutJson: vi.fn(),
}))
vi.mock('./useChartLayouts', () => ({
  useChartLayouts: () => ({
    layouts: [],
    activeLayout: null,
    saveStatus: 'saved',
    error: null,
    drawings: [],
    templates: [],
    selectedDrawingId: null,
    chartState: { showAspects: true, showSrLines: true, drawingPreferences: {} },
    switchLayout: vi.fn(),
    saveNow: vi.fn(),
    saveAs: vi.fn(),
    removeLayout: vi.fn(),
    importLayout: vi.fn(),
    undo: vi.fn(),
    clearDrawings: vi.fn(),
    updateChartState: vi.fn(),
    replaceDrawings: vi.fn(),
    setSelectedDrawingId: vi.fn(),
    updateDrawing: vi.fn(),
    deleteDrawing: vi.fn(),
    updateDrawingGroup: vi.fn(),
    deleteDrawingGroup: vi.fn(),
    createTemplate: vi.fn(),
    removeTemplate: vi.fn(),
  }),
}))

vi.mock('./components/CandlestickPanel', () => ({ CandlestickPanel: () => <div /> }))
vi.mock('./components/AspectEvidenceTracePanel', () => ({ AspectEvidenceTracePanel: () => <div /> }))
vi.mock('./components/CurrencyDivergence', () => ({ CurrencyDivergence: () => <div /> }))
vi.mock('./components/DrawingObjectPanel', () => ({ DrawingObjectPanel: () => <div /> }))
vi.mock('./components/EvidenceCertificationGrid', () => ({ EvidenceCertificationGrid: () => <div /> }))
vi.mock('./components/HistoricalFamilyEvidence', () => ({ HistoricalFamilyEvidence: () => <div /> }))
vi.mock('./components/LayoutToolbar', () => ({ LayoutToolbar: () => <div /> }))
vi.mock('./components/LocalJyotishPanel', () => ({ LocalJyotishPanel: () => <div /> }))
vi.mock('./components/MarketChart', () => ({ MarketChart: () => <div /> }))
vi.mock('./components/RsiPanel', () => ({ RsiPanel: () => <div /> }))
vi.mock('./components/MarketSynthesisPanel', () => ({ MarketSynthesisPanel: () => <div /> }))
vi.mock('./components/ToolRail', () => ({ ToolRail: () => <div /> }))
vi.mock('./components/CodexPanel', () => ({ CodexPanel: () => <div /> }))

const occurrence = (eventId: string, occurrenceIndex: number) => ({
  eventId,
  caseId: occurrenceIndex,
  familyKey: 'TN::MERCURY->MARS::trine',
  pairKey: 'MARS|MERCURY',
  aspect: 'trine',
  aspectLabel: 'trine',
  transitBody: 'MERCURY',
  natalBody: 'MARS',
  start: 1782900000 + occurrenceIndex * 3600,
  end: 1782903600 + occurrenceIndex * 3600,
  peak: 1782901800 + occurrenceIndex * 3600,
  startIso: '2026-07-01T10:00:00Z',
  endIso: '2026-07-01T11:00:00Z',
  peakIso: '2026-07-01T10:30:00Z',
  durationMinutes: 60,
  peakOrbDeg: 0.2,
  orbLimitDeg: 3,
  color: '#fff',
  occurrenceIndex,
  occurrenceCount: 2,
  knownPriorCount: 0,
  knownOccurrenceCount: 2,
  outcome: null,
  returnPct: null,
  reviewed: false,
  reviewStatus: 'pending',
  reviewSource: 'none',
  signedPips: null,
  astronomyContract: 'TEST_CONTRACT',
  sourceGenerator: 'TEST',
})

const family = {
  familyKey: 'TN::MERCURY->MARS::trine',
  pairKey: 'MARS|MERCURY',
  aspect: 'trine',
  transitBody: 'MERCURY',
  natalBody: 'MARS',
  occurrences: [occurrence('event-a', 1), occurrence('event-b', 2)],
  selectedEventId: 'event-a',
  summary: { total: 2, reviewed: 0, pending: 2, bullish: 0, bearish: 0, unknown: 2, labeledCount: 0, bullishRatePct: null, bearishRatePct: null, averageReturnPct: null, medianReturnPct: null },
  astronomyContract: 'TEST_CONTRACT',
  artifact: {} as DataArtifact,
} as unknown as AspectFamily

const detailFor = (eventId: string): EventDetail => ({
  event: family.occurrences.find((item) => item.eventId === eventId) ?? family.occurrences[0],
  chart: { symbol: 'USDJPY', timeframe: 'H1', candles: [], aspects: [], srLines: [], astronomyContract: 'TEST_CONTRACT', dataSource: 'corrected_historical', parametersApplied: {}, artifact: {} as DataArtifact, start: '', end: '', generatedAt: '' },
  astroEvidence: [],
  familySummary: family.summary,
  historicalFamilySummary: {} as EventDetail['historicalFamilySummary'],
  currencyPairEvidence: null,
  evidenceCertifications: [],
  context: { touch_time_local: '2026-07-01T10:00:00Z' },
  annotations: [],
})

const decisionPacket = {
  contract: 'GANN_TIMESTAMP_SAFE_DECISION_PACKET_V1',
  packetId: 'packet-a',
  engineVersion: 'test',
  policyVersion: 'test',
  mode: 'live_inference',
  status: 'watch',
  symbol: 'USDJPY',
  eventId: 'event-a',
  caseId: 1,
  familyKey: family.familyKey,
  times: { eventWindowStart: '2026-07-01T10:00:00Z', eventWindowEnd: '2026-07-01T11:00:00Z', decisionDeadline: '2026-07-01T11:00:00Z', signalTime: '2026-07-01T11:00:00Z', decisionTime: '2026-07-01T11:00:00Z', fillTime: null, exitTime: null, labelAvailableTime: null, evidenceCutoff: '2026-07-01T11:00:00Z', sourceDataMaxTime: '2026-07-01T11:00:00Z' },
  decision: { action: 'WATCH_LONG', direction: 'bullish', directionSource: 'fx_raw_and_doctrine_consensus', confidence: 'provisional_uncertified_watch_only', reason: 'test result' },
  entry: { state: 'unfilled_plan', rule: null, time: null, price: null },
  exit: { state: 'contingent_not_materialized', rule: null, time: null, price: null },
  outcome: null,
  featureAudit: { allowlistVersion: null, consumedFields: [], forbiddenFieldsPresentButExcluded: [], inputFingerprint: 'test' },
  guardrails: { timestampSafe: true, noLookahead: true, outcomeLabelConsumed: false, futurePricesConsumed: false, liveEligible: true, executionAllowed: false, experimentalDirectionalDiagnostic: true, forecastValidated: false, directionCertification: 'UNCERTIFIED', violations: [] },
  provenance: {},
} as unknown as DecisionPacket

describe('AnalyzeAspectWindow directional diagnostic containment', () => {
  beforeEach(() => {
    mocks.fetchFamily.mockResolvedValue(family)
    mocks.fetchEventDetail.mockImplementation((eventId: string) => Promise.resolve(detailFor(eventId)))
    mocks.fetchLiveDecision.mockResolvedValue(decisionPacket)
  })

  afterEach(() => {
    cleanup()
    vi.clearAllMocks()
  })

  it('does not request a diagnostic on load, and requires one explicit action', async () => {
    const user = userEvent.setup()
    render(<AnalyzeAspectWindow familyKey={family.familyKey} initialEventId="event-a" />)

    expect(await screen.findByText('Experimental directional diagnostic')).toBeInTheDocument()
    expect(mocks.fetchLiveDecision).not.toHaveBeenCalled()
    expect(screen.getByText('experimental')).toBeInTheDocument()
    expect(screen.getByText('uncertified')).toBeInTheDocument()
    expect(screen.getByText('not forecast-validated')).toBeInTheDocument()
    expect(screen.getByText('execution disabled')).toBeInTheDocument()
    expect(screen.queryByText('WATCH_LONG')).not.toBeInTheDocument()

    await user.click(screen.getByRole('button', { name: /Run diagnostic/i }))
    await waitFor(() => expect(mocks.fetchLiveDecision).toHaveBeenCalledTimes(1))
    expect(screen.getByText('Result: bullish')).toBeInTheDocument()
    expect(screen.getByText('historical token: WATCH_LONG')).toBeInTheDocument()
  })

  it('clears a prior result when the selected event changes', async () => {
    const user = userEvent.setup()
    render(<AnalyzeAspectWindow familyKey={family.familyKey} initialEventId="event-a" />)
    await screen.findByText('Experimental directional diagnostic')
    await user.click(screen.getByRole('button', { name: /Run diagnostic/i }))
    await screen.findByText('Result: bullish')

    const occurrenceButtons = screen.getAllByRole('button').filter((button) => button.className.includes('occurrence-item'))
    await user.click(occurrenceButtons[1])
    await waitFor(() => expect(screen.queryByText('Result: bullish')).not.toBeInTheDocument())
    expect(mocks.fetchLiveDecision).toHaveBeenCalledTimes(1)
    expect(screen.getByText(/No diagnostic has been run/)).toBeInTheDocument()
  })
})
