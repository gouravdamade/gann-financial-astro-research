// @vitest-environment jsdom

import '@testing-library/jest-dom/vitest'
import { cleanup, fireEvent, render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { useState } from 'react'
import { afterEach, describe, expect, it, vi } from 'vitest'
import type { ChartPayload, MultiOscillatorActivityRange, ResearchFieldIntervalSelection, SynchronizedIndependentRange } from './types'
import { FieldsWorkspace } from './views/FieldsWorkspace'
import { canonicalAspectFilterKey, eventMatchesActivityFilters } from './views/MultiOscillatorActivityFilter'
import { deriveSharedRawActivityAxisMax, rawActivityHeightPercent } from './views/MultiOscillatorActivityScale'

const apiMocks = vi.hoisted(() => ({
  fetchSynchronizedIndependentRange: vi.fn(),
  fetchMultiOscillatorActivityRange: vi.fn(),
  fetchBphsClassicalCalendarRange: vi.fn(),
  fetchFxSidePilotStatus: vi.fn(),
  fetchFounderReviewWorkbench: vi.fn(),
  exportFounderReviewPacket: vi.fn(),
}))

vi.mock('./api', () => ({
  fetchSynchronizedIndependentRange: apiMocks.fetchSynchronizedIndependentRange,
  fetchMultiOscillatorActivityRange: apiMocks.fetchMultiOscillatorActivityRange,
  fetchBphsClassicalCalendarRange: apiMocks.fetchBphsClassicalCalendarRange,
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

const longChart = {
  ...chart,
  candles: [
    { time: Date.parse('2026-08-01T00:00:00Z') / 1000, open: 150, high: 151, low: 149, close: 150.5 },
    { time: Date.parse('2026-08-15T00:00:00Z') / 1000, open: 150, high: 151, low: 149, close: 150.5 },
    { time: Date.parse('2026-08-29T00:00:00Z') / 1000, open: 150, high: 151, low: 149, close: 150.5 },
    { time: Date.parse('2026-09-01T00:00:00Z') / 1000, open: 150, high: 151, low: 149, close: 150.5 },
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

const multiOscillatorActivityRange = {
  contract: 'MO_UNSIGNED_EVENT_ACTIVITY_RANGE_V1_1', schemaVersion: 2, evidenceMode: 'EXPLORATORY_UNSIGNED', contributionContract: 'MO_ACTIVITY_CONTRIBUTION_V1',
  rangeStartUtc: startUtc, rangeEndUtc: endUtc, sideIdentities: ['USD', 'JPY'],
  eventUniverse: { profileId: 'ASPECT_STRENGTH_V0', eventUniverseHash: 'profile-hash', bodyUniverse: ['SUN', 'MARS'], aspectTypes: ['SQUARE', 'TRINE'], maxOrbDeg: 3, directionPolicy: 'GEOMETRY_ONLY', doctrineStatus: 'EXPERIMENTAL_GEOMETRY_PROFILE' },
  fields: {
    USD: {
      contract: 'MO_UNSIGNED_EVENT_ACTIVITY_SIDE_V1_1', schemaVersion: 2, evidenceMode: 'EXPLORATORY_UNSIGNED', sideIdentity: 'USD', instrumentIdentity: 'FX_CURRENCY:USD', chartId: 'usd-chart', chartHypothesisId: 'usd-hypothesis', rangeStartUtc: startUtc, rangeEndUtc: endUtc, eventUniverseProfileId: 'ASPECT_STRENGTH_V0', eventUniverseHash: 'profile-hash', bodyUniverse: ['SUN', 'MARS'], aspectProfile: { profileId: 'ASPECT_STRENGTH_V0', aspectTypes: ['SQUARE', 'TRINE'], maxOrbDeg: 3, directionPolicy: 'GEOMETRY_ONLY', doctrineStatus: 'EXPERIMENTAL_GEOMETRY_PROFILE' }, astronomy: { astronomyContract: 'TEST', historicalCivilTimeConversionPolicy: 'TEST', ephemerisProvider: 'TEST', ephemerisVersion: 'TEST', ayanamsha: 'TEST', nodePolicy: 'TEST', generatorVersion: 'TEST', generatorHash: 'profile-hash' },
      events: [{ eventId: 'usd-activity-event', eventHash: 'usd-hash', sideIdentity: 'USD', instrumentIdentity: 'FX_CURRENCY:USD', chartId: 'usd-chart', chartHypothesisId: 'usd-hypothesis', transitBody: 'MARS', natalTarget: 'SUN', aspectType: 'square', applyingStartUtc: startUtc, exactUtc: splitUtc, separatingEndUtc: endUtc, polarity: null, magnitude: null }],
      activityIntervals: [{ intervalId: 'usd-activity-1', startUtc, endUtc, rawActiveEventCount: 1, contributingEventIds: ['usd-activity-event'], coverage: 'KNOWN', unknownReason: null }], sourceEventCount: 1, eligibleEventCount: 1, rejectedEventCount: 0, relevantRejectedEventCount: 0, irrelevantRejectedEventCount: 0, groupedCounts: { byTransitBody: { MARS: 1 }, byAspectType: { SQUARE: 1 } }, coverage: 'KNOWN', unknownReason: null,
      guardrails: { readOnly: true, unsigned: true, nonPredictive: true, polarityAssigned: false, magnitudeAssigned: false, priceDataRead: false, priceOutcomeRead: false, sbcRead: false, llmRead: false, executionAllowed: false, automaticOrderPlacement: false, pairDifferenceComputed: false, normalizationUsed: false, dataNormalizationUsed: false, displayAxisScaling: { mode: 'SHARED_RAW_COUNT_AXIS', derivedFrom: 'CURRENT_FILTERED_VISIBLE_COUNTS', changesDataValues: false }, smoothingUsed: false },
    },
    JPY: {
      contract: 'MO_UNSIGNED_EVENT_ACTIVITY_SIDE_V1_1', schemaVersion: 2, evidenceMode: 'EXPLORATORY_UNSIGNED', sideIdentity: 'JPY', instrumentIdentity: 'FX_CURRENCY:JPY', chartId: 'jpy-chart', chartHypothesisId: 'jpy-hypothesis', rangeStartUtc: startUtc, rangeEndUtc: endUtc, eventUniverseProfileId: 'ASPECT_STRENGTH_V0', eventUniverseHash: 'profile-hash', bodyUniverse: ['SUN', 'MARS'], aspectProfile: { profileId: 'ASPECT_STRENGTH_V0', aspectTypes: ['SQUARE', 'TRINE'], maxOrbDeg: 3, directionPolicy: 'GEOMETRY_ONLY', doctrineStatus: 'EXPERIMENTAL_GEOMETRY_PROFILE' }, astronomy: { astronomyContract: 'TEST', historicalCivilTimeConversionPolicy: 'TEST', ephemerisProvider: 'TEST', ephemerisVersion: 'TEST', ayanamsha: 'TEST', nodePolicy: 'TRUE_NODE', generatorVersion: 'TEST', generatorHash: 'profile-hash' }, events: [], activityIntervals: [{ intervalId: 'jpy-activity-1', startUtc, endUtc, rawActiveEventCount: 0, contributingEventIds: [], coverage: 'KNOWN', unknownReason: null }], sourceEventCount: 0, eligibleEventCount: 0, rejectedEventCount: 0, relevantRejectedEventCount: 0, irrelevantRejectedEventCount: 0, groupedCounts: { byTransitBody: {}, byAspectType: {} }, coverage: 'KNOWN', unknownReason: null,
      guardrails: { readOnly: true, unsigned: true, nonPredictive: true, polarityAssigned: false, magnitudeAssigned: false, priceDataRead: false, priceOutcomeRead: false, sbcRead: false, llmRead: false, executionAllowed: false, automaticOrderPlacement: false, pairDifferenceComputed: false, normalizationUsed: false, dataNormalizationUsed: false, displayAxisScaling: { mode: 'SHARED_RAW_COUNT_AXIS', derivedFrom: 'CURRENT_FILTERED_VISIBLE_COUNTS', changesDataValues: false }, smoothingUsed: false },
    },
  },
  guardrails: { readOnly: true, unsigned: true, nonPredictive: true, polarityAssigned: false, magnitudeAssigned: false, priceDataRead: false, priceOutcomeRead: false, sbcRead: false, llmRead: false, executionAllowed: false, automaticOrderPlacement: false, pairDifferenceComputed: false, normalizationUsed: false, dataNormalizationUsed: false, displayAxisScaling: { mode: 'SHARED_RAW_COUNT_AXIS', derivedFrom: 'CURRENT_FILTERED_VISIBLE_COUNTS', changesDataValues: false }, smoothingUsed: false },
} as unknown as MultiOscillatorActivityRange

const bphsCalendarRange = {
  contract: 'BPHS_CLASSICAL_CALENDAR_RANGE_V1', schemaVersion: 1, rangeStartUtc: startUtc, rangeEndUtc: endUtc,
  timezone: 'Asia/Kolkata', location: { latitude: 18.5204, longitude: 73.8567 },
  categoryOrder: ['muhurta', 'tithi', 'nakshatra', 'yoga', 'karana', 'weekday', 'tara'],
  sourceProfile: { profileId: 'BPHS_1899_CLASSICAL_CALENDAR_RESEARCH_V1', sourceId: 'BPHS_1899_GOVIND_SHARMA_SHASTRI', edition: '1899', fileSha256: 'SHA', scope: 'Chapter 14', evidenceStatus: 'PARTIAL_SOURCE_PROFILE', classicalCompletenessClaim: false, sourceGaps: ['BPHS_1899_WEEKDAY_BOUNDARY_NOT_CLOSED', 'BPHS_1899_TARA_NINEFOLD_SEQUENCE_AND_MAPPING_NOT_LOCATED_IN_PACKET_1W'], interpretation: 'No market meaning.' },
  engineeringCalculationProfile: 'SWISSEPH_RAMAN_SIDEREAL_CALENDAR_BOUNDARIES_V1',
  intervals: [{ intervalId: 'BPHS_CAL_00001', startUtc, endUtc, categories: {
    muhurta: { value: 'DAY MUHURTA 01 - Ardra', availability: 'SOURCE_TRANSCRIBED_ENGINEERING_BOUNDARY', detail: 'Source name; engineering boundary.', sourceLocator: 'Chapter 14 printed p. 197', calculationProfile: 'engineering', dependency: 'ENGINEERING_SUNRISE_SUNSET_BOUNDARY_NOT_CLASSICAL_FORMULA' },
    tithi: { value: 'Shukla 01 Pratipada', availability: 'ENGINEERING_CALCULATED', detail: 'Tithi.', sourceLocator: 'Chapter 14', calculationProfile: 'engineering', dependency: null },
    nakshatra: { value: '01 Ashwini pada 1', availability: 'ENGINEERING_CALCULATED', detail: 'Nakshatra.', sourceLocator: 'Chapter 14', calculationProfile: 'engineering', dependency: null },
    yoga: { value: '01 Vishkambha', availability: 'ENGINEERING_CALCULATED', detail: 'Yoga.', sourceLocator: 'Chapter 14', calculationProfile: 'engineering', dependency: null },
    karana: { value: '01 Kimstughna', availability: 'ENGINEERING_CALCULATED', detail: 'Karana.', sourceLocator: 'Chapter 14', calculationProfile: 'engineering', dependency: null },
    weekday: { value: 'Civil weekday: Tuesday', availability: 'PARTIAL_SOURCE', detail: 'Civil weekday boundary not closed.', sourceLocator: 'Chapter 14', calculationProfile: 'engineering', dependency: 'BPHS_1899_WEEKDAY_BOUNDARY_NOT_CLOSED' },
    tara: { value: 'DEPENDENCY_NOT_READY', availability: 'DEPENDENCY_NOT_READY', detail: 'Source mapping/reference missing.', sourceLocator: 'Chapter 14', calculationProfile: 'NOT_EVALUATED', dependency: 'TARA_PENDING' },
  }}],
  guardrails: { readOnly: true, marketDataRead: false, priceOutcomeRead: false, polarityCatalogueRead: false, pairRelativeFieldPath: false, founderReviewDecisionPath: false, sbcPath: false, autoSuggestPath: false, mlPath: false, executionAllowed: false, automaticOrderPlacement: false, scoreAggregationUsed: false, marketDirectionInferred: false },
} as const

const bphsFourteenDayCalendarRange = {
  ...bphsCalendarRange,
  rangeStartUtc: '2026-08-01T00:00:00.000Z',
  rangeEndUtc: '2026-08-15T00:00:00.000Z',
  intervals: [{
    ...bphsCalendarRange.intervals[0],
    startUtc: '2026-08-01T00:00:00.000Z',
    endUtc: '2026-08-15T00:00:00.000Z',
  }],
} as unknown as typeof bphsCalendarRange

function renderFields(
  overrides: Partial<React.ComponentProps<typeof FieldsWorkspace>> = {},
  activityRange: MultiOscillatorActivityRange = multiOscillatorActivityRange,
) {
  const selected = vi.fn()
  const profile = vi.fn()
  const mode = vi.fn()
  const activitySelection = vi.fn()
  apiMocks.fetchMultiOscillatorActivityRange.mockResolvedValue(activityRange)
  return {
    selected,
    profile,
    mode,
    activitySelection,
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
      onSelectActivityTimestampUtc={activitySelection}
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
    onSelectActivityTimestampUtc={() => undefined}
  />
}

afterEach(() => {
  cleanup()
  vi.clearAllMocks()
  window.sessionStorage.removeItem('gann-astro.fields.bphs-calendar.enabled.v1')
})

describe('FieldsWorkspace', () => {
  it('maps raw activity counts to exact shared-axis percentages without a visible floor', () => {
    expect(rawActivityHeightPercent(100, 100)).toBe(100)
    expect(rawActivityHeightPercent(25, 100)).toBe(25)
    expect(rawActivityHeightPercent(1, 100)).toBe(1)
    expect(rawActivityHeightPercent(0, 100)).toBe(0)
    expect(rawActivityHeightPercent(4, 4)).toBe(100)
    expect(rawActivityHeightPercent(1, 4)).toBe(25)
    expect(rawActivityHeightPercent(0, 0)).toBe(0)
    expect(rawActivityHeightPercent(-1, 100)).toBe(0)
    expect(rawActivityHeightPercent(Number.NaN, 100)).toBe(0)
    expect(rawActivityHeightPercent(101, 100)).toBe(100)
  })

  it('normalizes only the aspect filter boundary and preserves distinct canonical keys', () => {
    expect(canonicalAspectFilterKey(' square ')).toBe('SQUARE')
    expect(canonicalAspectFilterKey('trine')).toBe('TRINE')
    expect(canonicalAspectFilterKey('conjunction')).toBe('CONJUNCTION')
    expect(canonicalAspectFilterKey('square')).not.toBe(canonicalAspectFilterKey('trine'))
  })

  it('matches lowercase canonical compiler aspects against uppercase UI filters', () => {
    const event = { aspectType: 'square', transitBody: 'MARS' } as MultiOscillatorActivityRange['fields']['USD']['events'][number]
    expect(eventMatchesActivityFilters(event, ['MARS'], ['SQUARE'])).toBe(true)
    expect(eventMatchesActivityFilters({ ...event, aspectType: 'trine' }, ['MARS'], ['TRINE'])).toBe(true)
    expect(eventMatchesActivityFilters({ ...event, aspectType: 'conjunction' }, ['MARS'], ['CONJUNCTION'])).toBe(true)
    expect(eventMatchesActivityFilters(event, ['MARS'], ['TRINE'])).toBe(false)
  })

  it('derives one shared raw-count axis instead of independently normalizing sides', () => {
    expect(deriveSharedRawActivityAxisMax({
      USD: [{ rawActiveEventCount: 12 } as MultiOscillatorActivityRange['fields']['USD']['activityIntervals'][number]],
      JPY: [{ rawActiveEventCount: 4 } as MultiOscillatorActivityRange['fields']['JPY']['activityIntervals'][number]],
    })).toBe(12)
    expect(deriveSharedRawActivityAxisMax({ USD: [], JPY: [] })).toBe(0)
  })

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
    expect(await screen.findByText('Multi Oscillator / Event Activity')).toBeInTheDocument()
    expect(screen.getByText('Unsigned Activity Waves')).toBeInTheDocument()
    expect(screen.getByRole('img', { name: 'USD exact unsigned activity step trace' })).toBeInTheDocument()
    expect(screen.getByRole('img', { name: 'JPY exact unsigned activity step trace' })).toBeInTheDocument()
    expect(screen.getByLabelText('Shared unsigned activity wave time axis')).toBeInTheDocument()
    expect(screen.getAllByText('EXPLORATORY_UNSIGNED').length).toBeGreaterThan(0)
    expect(await screen.findByText('Raw activity: 0-1 events')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /Inspect USD MARS SQUARE event/i })).toBeInTheDocument()
    expect(document.querySelectorAll('.mo-event-span')).toHaveLength(1)
    expect(document.querySelectorAll('.mo-event-marker')).toHaveLength(1)
    expect(document.querySelectorAll('.mo-wave-crosshair')).toHaveLength(2)
    expect(screen.getAllByText('No active event is a known zero.').length).toBeGreaterThan(0)
    expect(screen.getByRole('button', { name: /JPY activity interval 0 active events/i }).getAttribute('style')).toContain('--mo-activity-height: 0%')
  })

  it('shows every backend event with all filters selected despite canonical lowercase aspects', async () => {
    apiMocks.fetchSynchronizedIndependentRange.mockResolvedValue(synchronizedRange)
    apiMocks.fetchFxSidePilotStatus.mockResolvedValue(null)

    renderFields()

    await screen.findByText('Multi Oscillator / Event Activity')
    await screen.findByRole('button', { name: /Inspect USD MARS SQUARE event/i })
    expect(document.querySelectorAll('.mo-event-span')).toHaveLength(multiOscillatorActivityRange.fields.USD.events.length)
    expect(document.querySelectorAll('.mo-event-marker')).toHaveLength(multiOscillatorActivityRange.fields.USD.events.length)
    expect(await screen.findByText('Raw activity: 0-1 events')).toBeInTheDocument()
    expect(document.querySelectorAll('.mo-wave-trace')).toHaveLength(2)
  })

  it('recomputes the shared display axis from filtered visible events without changing backend coverage', async () => {
    apiMocks.fetchSynchronizedIndependentRange.mockResolvedValue(synchronizedRange)
    apiMocks.fetchFxSidePilotStatus.mockResolvedValue(null)
    const user = userEvent.setup()

    renderFields()

    await screen.findByText('Multi Oscillator / Event Activity')
    expect(await screen.findByText('Raw activity: 0-1 events')).toBeInTheDocument()
    expect(screen.getByText('Hatch = incomplete coverage')).toBeInTheDocument()
    await user.click(screen.getByRole('checkbox', { name: 'MARS' }))
    expect(screen.getByText('Raw activity: 0-0 events')).toBeInTheDocument()
    expect(screen.getAllByText('KNOWN COVERAGE').length).toBeGreaterThan(0)
  })

  it('hides and restores canonical lowercase square events through the uppercase aspect checkbox', async () => {
    apiMocks.fetchSynchronizedIndependentRange.mockResolvedValue(synchronizedRange)
    apiMocks.fetchFxSidePilotStatus.mockResolvedValue(null)
    const user = userEvent.setup()

    renderFields()

    await screen.findByRole('button', { name: /Inspect USD MARS SQUARE event/i })
    await user.click(screen.getByRole('checkbox', { name: 'SQUARE' }))
    expect(screen.queryByRole('button', { name: /Inspect USD MARS SQUARE event/i })).not.toBeInTheDocument()
    expect(screen.getByText('Raw activity: 0-0 events')).toBeInTheDocument()
    await user.click(screen.getByRole('checkbox', { name: 'SQUARE' }))
    expect(await screen.findByRole('button', { name: /Inspect USD MARS SQUARE event/i })).toBeInTheDocument()
    expect(screen.getByText('Raw activity: 0-1 events')).toBeInTheDocument()
  })

  it('keeps unknown styling separate from known-zero amplitude', async () => {
    apiMocks.fetchSynchronizedIndependentRange.mockResolvedValue(synchronizedRange)
    apiMocks.fetchFxSidePilotStatus.mockResolvedValue(null)
    const unknownActivityRange = {
      ...multiOscillatorActivityRange,
      fields: {
        ...multiOscillatorActivityRange.fields,
        USD: {
          ...multiOscillatorActivityRange.fields.USD,
          coverage: 'UNKNOWN',
          unknownReason: 'EVENT_COMPILER_REJECTED_EVENTS_OVERLAPPING_VISIBLE_RANGE',
          activityIntervals: [{
            ...multiOscillatorActivityRange.fields.USD.activityIntervals[0],
            coverage: 'UNKNOWN',
            unknownReason: 'EVENT_COMPILER_REJECTED_EVENTS_OVERLAPPING_VISIBLE_RANGE',
            rawActiveEventCount: 0,
            contributingEventIds: [],
          }],
        },
      },
    } as MultiOscillatorActivityRange

    renderFields({}, unknownActivityRange)

    const unknownInterval = await screen.findByRole('button', { name: /USD activity interval 0 active events/i })
    expect(unknownInterval).toHaveClass('is-unknown')
    expect(unknownInterval.getAttribute('style')).toContain('--mo-activity-height: 0%')
    expect(document.querySelector('.mo-wave-interval.is-unknown')).toBeInTheDocument()
  })

  it('keeps UNKNOWN coverage decoration independent from nonzero activity height', () => {
    expect(rawActivityHeightPercent(2, 8)).toBe(25)
    expect(rawActivityHeightPercent(0, 8)).toBe(0)
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

  it('selects an exact activity event without creating a directional interpretation', async () => {
    apiMocks.fetchSynchronizedIndependentRange.mockResolvedValue(synchronizedRange)
    apiMocks.fetchFxSidePilotStatus.mockResolvedValue(null)
    const user = userEvent.setup()
    const { activitySelection } = renderFields()

    await user.click(await screen.findByRole('button', { name: /Inspect USD MARS SQUARE event/i }))
    expect(activitySelection).toHaveBeenCalledWith(splitUtc)
    expect(screen.getByText('Selected event provenance')).toBeInTheDocument()
    expect(screen.getByText('NOT ASSIGNED')).toBeInTheDocument()
    expect(screen.getByText('NOT CONFIGURED')).toBeInTheDocument()
    expect(screen.queryByText(/USDJPY unsigned difference/i)).not.toBeInTheDocument()
  })

  it('selects a step-wave interval at its exact stored start time', async () => {
    apiMocks.fetchSynchronizedIndependentRange.mockResolvedValue(synchronizedRange)
    apiMocks.fetchFxSidePilotStatus.mockResolvedValue(null)
    const user = userEvent.setup()
    const { activitySelection } = renderFields()

    await user.click(await screen.findByRole('button', { name: /USD step-wave interval 1 active events/i }))
    expect(activitySelection).toHaveBeenCalledWith(startUtc)
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
    expect(screen.getByText('Unsigned Activity Waves')).toBeInTheDocument()
    expect(screen.queryByText(/signed pair resultant/i)).not.toBeInTheDocument()
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

  it('uses fixed 14-day research pages instead of the broad chart or viewport range', async () => {
    apiMocks.fetchSynchronizedIndependentRange.mockResolvedValue(synchronizedRange)
    apiMocks.fetchFxSidePilotStatus.mockResolvedValue(null)
    const user = userEvent.setup()

    renderFields({ chart: longChart, visibleRangeStartUtc: '2026-08-20T00:00:00Z', visibleRangeEndUtc: '2026-08-30T00:00:00Z' })

    await screen.findByText(/Research window 1\/3/)
    await waitFor(() => expect(apiMocks.fetchSynchronizedIndependentRange).toHaveBeenCalledWith(expect.objectContaining({
      rangeStartUtc: '2026-08-01T00:00:00.000Z',
      rangeEndUtc: '2026-08-15T00:00:00.000Z',
    })))
    await user.click(screen.getByRole('button', { name: 'Next 14 days' }))
    await waitFor(() => expect(apiMocks.fetchSynchronizedIndependentRange).toHaveBeenCalledWith(expect.objectContaining({
      rangeStartUtc: '2026-08-15T00:00:00.000Z',
      rangeEndUtc: '2026-08-29T00:00:00.000Z',
    })))
    await user.click(screen.getByRole('button', { name: 'Next 14 days' }))
    await screen.findByText(/Research window 3\/3/)
    expect(screen.getByRole('button', { name: 'Next 14 days' })).toBeDisabled()
    expect(screen.getByRole('button', { name: 'Previous 14 days' })).toBeEnabled()
  })

  it('offers an explicit crosshair page load without auto-paging on crosshair movement', async () => {
    apiMocks.fetchSynchronizedIndependentRange.mockResolvedValue(synchronizedRange)
    apiMocks.fetchFxSidePilotStatus.mockResolvedValue(null)
    const user = userEvent.setup()

    renderFields({ chart: longChart, crosshairTimestampUtc: '2026-08-20T00:00:00Z' })

    await screen.findByText(/Research window 1\/3/)
    await waitFor(() => expect(apiMocks.fetchSynchronizedIndependentRange).toHaveBeenCalledTimes(1))
    await user.click(screen.getByRole('button', { name: 'Load window containing crosshair' }))
    await screen.findByText(/Research window 2\/3/)
    await waitFor(() => expect(apiMocks.fetchSynchronizedIndependentRange).toHaveBeenCalledTimes(2))
  })

  it('discards a late prior-page response after the research page changes', async () => {
    let resolveFirst!: (value: SynchronizedIndependentRange) => void
    apiMocks.fetchSynchronizedIndependentRange
      .mockImplementationOnce(() => new Promise<SynchronizedIndependentRange>((resolve) => { resolveFirst = resolve }))
      .mockResolvedValueOnce(synchronizedRange)
    apiMocks.fetchFxSidePilotStatus.mockResolvedValue(null)
    const user = userEvent.setup()

    renderFields({ chart: longChart })

    await waitFor(() => expect(apiMocks.fetchSynchronizedIndependentRange).toHaveBeenCalledTimes(1))
    await user.click(screen.getByRole('button', { name: 'Next 14 days' }))
    await waitFor(() => expect(apiMocks.fetchSynchronizedIndependentRange).toHaveBeenCalledTimes(2))
    await screen.findByText('SBC atomic field')
    resolveFirst(geometryOnlyRange)
    await new Promise((resolve) => window.setTimeout(resolve, 0))
    expect(screen.getByText('SBC atomic field')).toBeInTheDocument()
    expect(screen.queryByText(/GEOMETRY_ONLY_RANGE_NOT_IMPLEMENTED/)).not.toBeInTheDocument()
  })

  it('loads neutral BPHS timing only when its separate persistent switch is enabled', async () => {
    apiMocks.fetchSynchronizedIndependentRange.mockResolvedValue(synchronizedRange)
    apiMocks.fetchFxSidePilotStatus.mockResolvedValue(null)
    apiMocks.fetchBphsClassicalCalendarRange.mockResolvedValue(bphsCalendarRange)
    const user = userEvent.setup()
    renderFields()

    expect(screen.queryByText('BPHS Classical Calendar')).not.toBeInTheDocument()
    const timingSwitch = screen.getByRole('switch', { name: /BPHS Calendar/i })
    expect(timingSwitch).not.toBeChecked()
    await user.click(timingSwitch)
    expect(timingSwitch).toBeChecked()
    expect(await screen.findByText('BPHS Classical Calendar')).toBeInTheDocument()
    expect(screen.getAllByText('DEPENDENCY_NOT_READY').length).toBeGreaterThan(0)
    expect(screen.getAllByText(/DAY MUHURTA 01 - Ardra/).length).toBeGreaterThan(0)
    expect(screen.getAllByText('Civil weekday (engineering)').length).toBeGreaterThan(0)
    expect(apiMocks.fetchBphsClassicalCalendarRange).toHaveBeenCalledWith(expect.objectContaining({
      rangeStartUtc: startUtc, rangeEndUtc: endUtc, profileId: 'BPHS_1899_CLASSICAL_CALENDAR_RESEARCH_V1',
    }))
    expect(window.sessionStorage.getItem('gann-astro.fields.bphs-calendar.enabled.v1')).toBe('true')
  })

  it('uses one loaded 14-day BPHS response behind a shared default 3-day viewport', async () => {
    apiMocks.fetchSynchronizedIndependentRange.mockResolvedValue(synchronizedRange)
    apiMocks.fetchFxSidePilotStatus.mockResolvedValue(null)
    apiMocks.fetchBphsClassicalCalendarRange.mockResolvedValue(bphsFourteenDayCalendarRange)
    const user = userEvent.setup()

    renderFields({ chart: longChart })
    const timingSwitch = screen.getByRole('switch', { name: /BPHS Calendar/i })
    await user.click(timingSwitch)

    expect(await screen.findByText(/3 of 14 loaded days/)).toBeInTheDocument()
    expect(screen.getByText('Research page').parentElement).toHaveTextContent(/2026-08-01.*2026-08-15.*page 1\/3/)
    expect(apiMocks.fetchBphsClassicalCalendarRange).toHaveBeenCalledTimes(1)

    const scroll = screen.getByLabelText('Scroll the loaded 14-day BPHS calendar')
    Object.defineProperty(scroll, 'scrollWidth', { configurable: true, value: 1400 })
    Object.defineProperty(scroll, 'clientWidth', { configurable: true, value: 300 })
    Object.defineProperty(scroll, 'scrollLeft', { configurable: true, value: 300, writable: true })
    fireEvent.scroll(scroll)

    expect(await screen.findByText(/Viewing 2026-08-04.*2026-08-07/)).toBeInTheDocument()
    expect(apiMocks.fetchBphsClassicalCalendarRange).toHaveBeenCalledTimes(1)
    expect(document.querySelectorAll('.bphs-calendar-row')).toHaveLength(7)
    expect(screen.getAllByText('Muhurta').length).toBeGreaterThan(0)
    expect(screen.getAllByText('DEPENDENCY_NOT_READY').length).toBeGreaterThan(0)
  })
})
