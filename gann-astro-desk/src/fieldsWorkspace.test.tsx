// @vitest-environment jsdom

import '@testing-library/jest-dom/vitest'
import { cleanup, render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { useState } from 'react'
import { afterEach, describe, expect, it, vi } from 'vitest'
import type { ChartPayload, ResearchFieldIntervalSelection, SynchronizedIndependentRange } from './types'
import { FieldsWorkspace } from './views/FieldsWorkspace'

const apiMocks = vi.hoisted(() => ({
  fetchSynchronizedIndependentRange: vi.fn(),
  fetchFxSidePilotStatus: vi.fn(),
  fetchFounderReviewWorkbench: vi.fn(),
  exportFounderReviewPacket: vi.fn(),
}))

vi.mock('./api', () => ({
  fetchSynchronizedIndependentRange: apiMocks.fetchSynchronizedIndependentRange,
  fetchFxSidePilotStatus: apiMocks.fetchFxSidePilotStatus,
  fetchFounderReviewWorkbench: apiMocks.fetchFounderReviewWorkbench,
  exportFounderReviewPacket: apiMocks.exportFounderReviewPacket,
}))

const startUtc = '2026-08-01T10:00:00.000Z'
const splitUtc = '2026-08-01T11:00:00.000Z'
const endUtc = '2026-08-01T12:00:00.000Z'

const chart = {
  symbol: 'USDJPY',
  timeframe: 'H1',
  candles: [
    { time: Date.parse(startUtc) / 1000, open: 150, high: 151, low: 149, close: 150.5 },
    { time: Date.parse(endUtc) / 1000, open: 150.5, high: 151.5, low: 150, close: 151 },
  ],
} as unknown as ChartPayload

const synchronizedRange = {
  contract: 'SYNCHRONIZED_INDEPENDENT_RANGE_V1',
  schemaVersion: 1,
  rangeStartUtc: startUtc,
  rangeEndUtc: endUtc,
  synchronizationStatus: 'SYNCHRONIZED',
  aspectFields: {
    USD: {
      contract: 'CHART_CONDITIONED_CATEGORICAL_RANGE_V1', schemaVersion: 1,
      instrumentId: 'FX_CURRENCY:USD', sideIdentity: 'USD', chartId: 'usd-chart', chartHypothesisId: 'usd-hypothesis',
      rangeStartUtc: startUtc, rangeEndUtc: endUtc, sourceEventCount: 1,
      stateContract: 'CATEGORICAL_POLARITY_STATE', magnitudeState: 'MAGNITUDE_NOT_CONFIGURED',
      guardrails: { readOnly: true, executionAllowed: false, automaticOrderPlacement: false, financiallyValidated: false, actsAsSbcConfirmation: false },
      intervals: [
        { intervalId: 'usd-supportive', startUtc, endUtc: splitUtc, polarityState: 'SUPPORTIVE', supportiveActive: true, adverseActive: false, activeEventIds: ['usd-event'], unknownEventIds: [], reason: 'Reviewed supportive USD event.' },
        { intervalId: 'usd-mixed', startUtc: splitUtc, endUtc, polarityState: 'MIXED', supportiveActive: true, adverseActive: true, activeEventIds: ['usd-event-2'], unknownEventIds: [], reason: 'Both USD components are active.' },
      ],
    },
    JPY: {
      contract: 'CHART_CONDITIONED_CATEGORICAL_RANGE_V1', schemaVersion: 1,
      instrumentId: 'FX_CURRENCY:JPY', sideIdentity: 'JPY', chartId: 'jpy-chart', chartHypothesisId: 'jpy-hypothesis',
      rangeStartUtc: startUtc, rangeEndUtc: endUtc, sourceEventCount: 1,
      stateContract: 'CATEGORICAL_POLARITY_STATE', magnitudeState: 'MAGNITUDE_NOT_CONFIGURED',
      guardrails: { readOnly: true, executionAllowed: false, automaticOrderPlacement: false, financiallyValidated: false, actsAsSbcConfirmation: false },
      intervals: [
        { intervalId: 'jpy-neutral', startUtc, endUtc: splitUtc, polarityState: 'NEUTRAL', supportiveActive: false, adverseActive: false, activeEventIds: [], unknownEventIds: [], reason: 'Explicit JPY neutral.' },
        { intervalId: 'jpy-unknown', startUtc: splitUtc, endUtc, polarityState: 'UNKNOWN', supportiveActive: false, adverseActive: false, activeEventIds: [], unknownEventIds: ['jpy-gap'], reason: 'POLARITY_CATALOGUE_MISSING' },
      ],
    },
  },
  sbcField: {
    contract: 'SBC_ATOMIC_VISIBLE_RANGE_V1', schema_version: 1, instrument_identity: 'FX:USDJPY',
    range_start_utc: startUtc, range_end_utc: endUtc, aspect_relationship: 'NOT_AUTOMATIC_CONFIRMATION', magnitude_state: 'NOT_CONFIGURED',
    intervals: [{ interval_id: 'sbc-available', interval_ledger_id: 'ledger-1', start_utc: startUtc, end_utc: endUtc, evidence_cutoff_utc: startUtc, classification: 'ATOMIC', guidance_availability: 'AVAILABLE', source_cluster_ids: ['cluster'], missing_evidence_ids: [] }],
    guardrails: { read_only: true, execution_allowed: false, automatic_order_placement: false, financially_validated: false, acts_as_aspect_confirmation: false },
  },
  guardrails: { readOnly: true, executionAllowed: false, automaticOrderPlacement: false, financiallyValidated: false, fieldsFused: false, actsAsSbcConfirmation: false, marketDirectionInferred: false },
} as unknown as SynchronizedIndependentRange

const geometryOnlyRange = {
  ...synchronizedRange,
  sbcField: {
    contract: 'SBC_TRAILOKYA_1972_GEOMETRY_ONLY_RANGE_V1', schema_version: 1,
    state: 'GEOMETRY_ONLY_RANGE_NOT_IMPLEMENTED', instrument_identity: 'FX:USDJPY', range_start_utc: startUtc, range_end_utc: endUtc,
    source_profile_id: 'SBC_TRAILOKYA_1972_V1', aspect_relationship: 'NOT_AUTOMATIC_CONFIRMATION', magnitude_state: 'NOT_CONFIGURED',
    classicalCompletenessClaim: false, source_gaps: ['SBC_TD1972_GEOMETRY_RANGE_NOT_COMPILED'], intervals: [], reason: 'No source-only range compiler exists.',
    guardrails: { read_only: true, execution_allowed: false, automatic_order_placement: false, financially_validated: false, acts_as_aspect_confirmation: false, score_aggregation_used: false, market_direction_inferred: false },
  },
} as unknown as SynchronizedIndependentRange

function renderFields(overrides: Partial<React.ComponentProps<typeof FieldsWorkspace>> = {}) {
  const selected = vi.fn()
  const profile = vi.fn()
  const mode = vi.fn()
  return {
    selected,
    profile,
    mode,
    ...render(<FieldsWorkspace
      chart={chart}
      priceChart={<div data-testid="fields-price-chart">shared chart</div>}
      visibleRangeStartUtc={startUtc}
      visibleRangeEndUtc={endUtc}
      defaultLatitude={18.5204}
      defaultLongitude={73.8567}
      vedhaProfileId="phaladeepika_editor_vedha_guidance_v1"
      onVedhaProfileIdChange={profile}
      visualizationMode="SOURCE_ONLY_BASELINE"
      onVisualizationModeChange={mode}
      crosshairTimestampUtc={startUtc}
      selectedFieldInterval={null}
      onSelectFieldInterval={selected}
      {...overrides}
    />),
  }
}

function ProfileSwitchHarness() {
  const [profile, setProfile] = useState<'phaladeepika_editor_vedha_guidance_v1' | 'SBC_TRAILOKYA_1972_V1'>('phaladeepika_editor_vedha_guidance_v1')
  return <FieldsWorkspace
    chart={chart}
    priceChart={<div data-testid="fields-price-chart">shared chart</div>}
    visibleRangeStartUtc={startUtc}
    visibleRangeEndUtc={endUtc}
    defaultLatitude={18.5204}
    defaultLongitude={73.8567}
    vedhaProfileId={profile}
    onVedhaProfileIdChange={setProfile}
    visualizationMode="SOURCE_ONLY_BASELINE"
    onVisualizationModeChange={() => undefined}
    crosshairTimestampUtc={startUtc}
    selectedFieldInterval={null}
    onSelectFieldInterval={() => undefined}
  />
}

afterEach(() => {
  cleanup()
  vi.clearAllMocks()
})

describe('FieldsWorkspace', () => {
  it('renders the shared chart and separate USD, JPY, pair, and SBC lanes by default', async () => {
  apiMocks.fetchSynchronizedIndependentRange.mockResolvedValue(synchronizedRange)
  apiMocks.fetchFxSidePilotStatus.mockResolvedValue(null)

    renderFields()

    expect(screen.getByTestId('fields-price-chart')).toBeInTheDocument()
    await screen.findByText('USD categorical field')
    expect(screen.getByText('JPY categorical field')).toBeInTheDocument()
    expect(screen.getByText('USDJPY pair-relative field')).toBeInTheDocument()
    expect(screen.getByText('SBC atomic field')).toBeInTheDocument()
    expect(screen.getAllByText(/FX_PAIR_RELATIVE_CATEGORICAL_FIELD_V1/).length).toBeGreaterThan(0)
    expect(apiMocks.fetchSynchronizedIndependentRange).toHaveBeenCalledWith(expect.objectContaining({
      rangeStartUtc: startUtc,
      rangeEndUtc: endUtc,
      sideIdentities: ['USD', 'JPY'],
      aspectProfileId: 'ASPECT_STRENGTH_V0',
    }))
    expect(screen.getByText(/2\/2 known/)).toBeInTheDocument()
  })

  it('selects a pair interval at its stored canonical start time', async () => {
    apiMocks.fetchSynchronizedIndependentRange.mockResolvedValue(synchronizedRange)
    apiMocks.fetchFxSidePilotStatus.mockResolvedValue(null)
    const user = userEvent.setup()
    const { selected } = renderFields()

    await screen.findByText('USDJPY pair-relative field')
    await user.click(screen.getByRole('button', { name: /Select PAIR interval SUPPORTIVE/i }))
    expect(selected).toHaveBeenCalledWith(expect.objectContaining({
      field: 'PAIR',
      startUtc,
      endUtc: splitUtc,
    } as ResearchFieldIntervalSelection))
  })

  it('keeps unknown side evidence as a pair gap instead of zero', async () => {
    apiMocks.fetchSynchronizedIndependentRange.mockResolvedValue(synchronizedRange)
    apiMocks.fetchFxSidePilotStatus.mockResolvedValue(null)

    renderFields()

    await screen.findByText('USDJPY pair-relative field')
    expect(screen.getByRole('button', { name: /Select PAIR interval UNKNOWN_SIDE_EVIDENCE/i })).toBeInTheDocument()
    expect(screen.getAllByText(/POLARITY_CATALOGUE_MISSING/).length).toBeGreaterThan(1)
  })

  it('suppresses directional paths rather than producing a visual-only wave', async () => {
    apiMocks.fetchSynchronizedIndependentRange.mockResolvedValue(synchronizedRange)
    apiMocks.fetchFxSidePilotStatus.mockResolvedValue(null)

    renderFields({ visualizationMode: 'VISUAL_ONLY_NO_SCORE' })

    await screen.findByText('USD categorical field')
    expect(screen.getAllByText('DIRECTIONAL FIELD SUPPRESSED BY VISUAL-ONLY MODE')).toHaveLength(3)
    expect(document.querySelectorAll('.categorical-step-balance')).toHaveLength(0)
  })

  it('shows Trailokya as geometry-only availability without a scored fallback', async () => {
    apiMocks.fetchSynchronizedIndependentRange.mockResolvedValue(geometryOnlyRange)
    apiMocks.fetchFxSidePilotStatus.mockResolvedValue(null)

    renderFields({ vedhaProfileId: 'SBC_TRAILOKYA_1972_V1' })

    expect((await screen.findAllByText(/GEOMETRY_ONLY_RANGE_NOT_IMPLEMENTED/)).length).toBeGreaterThan(0)
    expect(screen.getByText(/No score, polarity, wave, or fallback/)).toBeInTheDocument()
    expect(screen.queryByText(/Guidance score/i)).not.toBeInTheDocument()
  })

  it('refreshes the shared field range when the selected source profile changes', async () => {
    apiMocks.fetchSynchronizedIndependentRange.mockImplementation((request) => Promise.resolve(
      request.sbcRange.boundaries[0].request.vedhaProfileId === 'SBC_TRAILOKYA_1972_V1'
        ? geometryOnlyRange
        : synchronizedRange,
    ))
    apiMocks.fetchFxSidePilotStatus.mockResolvedValue(null)
    const user = userEvent.setup()

    render(<ProfileSwitchHarness />)

    await screen.findByText('USD categorical field')
    await user.selectOptions(screen.getByLabelText('Source profile'), 'SBC_TRAILOKYA_1972_V1')
    await waitFor(() => expect(apiMocks.fetchSynchronizedIndependentRange).toHaveBeenCalledTimes(2))
    expect((await screen.findAllByText(/GEOMETRY_ONLY_RANGE_NOT_IMPLEMENTED/)).length).toBeGreaterThan(0)
    expect(apiMocks.fetchSynchronizedIndependentRange).toHaveBeenCalledWith(expect.objectContaining({
      sbcRange: expect.objectContaining({
        boundaries: expect.arrayContaining([
          expect.objectContaining({ request: expect.objectContaining({ vedhaProfileId: 'SBC_TRAILOKYA_1972_V1' }) }),
        ]),
      }),
    }))
  })

  it('does not create an automatic FX pair field for a stock symbol', async () => {
    apiMocks.fetchFxSidePilotStatus.mockResolvedValue(null)
    const stockChart = { ...chart, symbol: 'AAPL' }

    renderFields({ chart: stockChart })

    await screen.findByText(/does not receive an automatic FX relative field/i)
    expect(screen.queryByText('USDJPY pair-relative field')).not.toBeInTheDocument()
    expect(apiMocks.fetchSynchronizedIndependentRange).not.toHaveBeenCalled()
  })
})
