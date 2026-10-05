// @vitest-environment jsdom

import '@testing-library/jest-dom/vitest'
import { cleanup, fireEvent, render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { useState } from 'react'
import { afterEach, describe, expect, it, vi } from 'vitest'
import type { ChartPayload, FxSidePilotStatus, MultiOscillatorActivityRange, ResearchFieldIntervalSelection, SynchronizedIndependentRange } from './types'
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

const stockChart = {
  ...chart,
  symbol: 'AAPL',
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

const allDirectionalStatesRange = {
  ...synchronizedRange,
  aspectFields: {
    ...synchronizedRange.aspectFields,
    USD: {
      ...synchronizedRange.aspectFields.USD,
      intervals: [
        ...synchronizedRange.aspectFields.USD.intervals,
        { intervalId: 'usd-adverse', startUtc, endUtc, polarityState: 'ADVERSE', supportiveActive: false, adverseActive: true, activeEventIds: ['usd-event-3'], unknownEventIds: [], reason: 'Adverse fixture state.' },
      ],
    },
  },
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

const zeroCoverageRange = {
  ...synchronizedRange,
  aspectFields: {
    ...synchronizedRange.aspectFields,
    USD: {
      ...synchronizedRange.aspectFields.USD,
      intervals: synchronizedRange.aspectFields.USD.intervals.map((interval) => ({
        ...interval,
        polarityState: 'UNKNOWN',
        supportiveActive: false,
        adverseActive: false,
        activeEventIds: [],
        unknownEventIds: [`${interval.intervalId}-gap`],
        reason: 'POLARITY_CATALOGUE_MISSING',
      })),
    },
    JPY: {
      ...synchronizedRange.aspectFields.JPY,
      intervals: synchronizedRange.aspectFields.JPY.intervals.map((interval) => ({
        ...interval,
        polarityState: 'UNKNOWN',
        supportiveActive: false,
        adverseActive: false,
        activeEventIds: [],
        unknownEventIds: [`${interval.intervalId}-gap`],
        reason: 'POLARITY_CATALOGUE_MISSING',
      })),
    },
  },
} as unknown as SynchronizedIndependentRange

const noActiveAspectRange = {
  ...zeroCoverageRange,
  aspectFields: {
    ...zeroCoverageRange.aspectFields,
    USD: {
      ...zeroCoverageRange.aspectFields.USD,
      intervals: zeroCoverageRange.aspectFields.USD.intervals.map((interval) => ({ ...interval, reason: 'NO_ACTIVE_SIDE_CHART_ASPECT' })),
    },
    JPY: {
      ...zeroCoverageRange.aspectFields.JPY,
      intervals: zeroCoverageRange.aspectFields.JPY.intervals.map((interval) => ({ ...interval, reason: 'NO_ACTIVE_SIDE_CHART_ASPECT' })),
    },
  },
} as unknown as SynchronizedIndependentRange

const zeroCataloguePilotStatus = {
  contract: 'FX_SIDE_POLARITY_PILOT_STATUS_V1', schemaVersion: 1,
  status: 'PILOT_EVIDENCE_PENDING', requiredStates: ['SUPPORTIVE', 'ADVERSE'], eligibleSides: ['USD', 'JPY'],
  sides: {
    USD: { sideIdentity: 'USD', instrumentId: 'FX_CURRENCY:USD', reviewedPacketCount: 0, catalogueEntryCount: 0, observedStates: [], missingRequiredStates: ['SUPPORTIVE', 'ADVERSE'], unknownGapsRetained: true, pilotEvidenceComplete: false, blockers: ['NO_ADMITTED_POLARITY_ENTRIES'] },
    JPY: { sideIdentity: 'JPY', instrumentId: 'FX_CURRENCY:JPY', reviewedPacketCount: 0, catalogueEntryCount: 0, observedStates: [], missingRequiredStates: ['SUPPORTIVE', 'ADVERSE'], unknownGapsRetained: true, pilotEvidenceComplete: false, blockers: ['NO_ADMITTED_POLARITY_ENTRIES'] },
  },
  unknownGapPolicy: 'UNREVIEWED_SIDE_EVENTS_REMAIN_UNKNOWN', summary: 'No side has the minimum reviewed categorical examples yet.',
  guardrails: { readOnly: true, executionAllowed: false, automaticOrderPlacement: false, financiallyValidated: false, createsCatalogueEntry: false, marketDirectionInferred: false, fieldsFused: false, actsAsSbcConfirmation: false },
} as unknown as FxSidePilotStatus

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
  const addActivity = vi.fn()
  apiMocks.fetchMultiOscillatorActivityRange.mockResolvedValue(activityRange)
  return {
    selected,
    profile,
    mode,
    activitySelection,
    addActivity,
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
      onAddActivityToChart={addActivity}
      {...overrides}
    />),
  }
}

function expectDirectionalPresentationWithheld() {
  const statePattern = /\b(SUPPORTIVE|ADVERSE|NEUTRAL|MIXED)\b/i
  expect(screen.queryByText(/^Supportive$/i)).not.toBeInTheDocument()
  expect(screen.queryByText(/^Adverse$/i)).not.toBeInTheDocument()
  expect(screen.queryByText(/^Neutral$/i)).not.toBeInTheDocument()
  expect(screen.queryByText(/^Mixed$/i)).not.toBeInTheDocument()
  expect(document.querySelectorAll('.categorical-step-balance, .categorical-step-supportive-component, .categorical-step-adverse-component, .categorical-step-hitbox, .categorical-step-gap')).toHaveLength(0)
  const labelledDirectionalNodes = [...document.querySelectorAll<HTMLElement>('[aria-label], [title]')]
    .filter((node) => statePattern.test(`${node.getAttribute('aria-label') ?? ''} ${node.getAttribute('title') ?? ''}`))
  expect(labelledDirectionalNodes).toHaveLength(0)
  const directionalButtons = screen.getAllByRole('button').filter((button) => statePattern.test(`${button.getAttribute('aria-label') ?? ''} ${button.textContent ?? ''}`))
  expect(directionalButtons).toHaveLength(0)
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

function ModeSwitchHarness() {
  const [mode, setMode] = useState<'SOURCE_ONLY_BASELINE' | 'CALIBRATED_RESEARCH' | 'VISUAL_ONLY_NO_SCORE'>('SOURCE_ONLY_BASELINE')
  return <FieldsWorkspace
    chart={chart}
    priceChart={<div data-testid="fields-price-chart">shared chart</div>}
    visibleRangeStartUtc={startUtc}
    visibleRangeEndUtc={endUtc}
    defaultLatitude={18.5204}
    defaultLongitude={73.8567}
    vedhaProfileId="phaladeepika_editor_vedha_guidance_v1"
    onVedhaProfileIdChange={() => undefined}
    visualizationMode={mode}
    onVisualizationModeChange={setMode}
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
    const firstRangeRequest = apiMocks.fetchSynchronizedIndependentRange.mock.calls[0][0]
    expect(firstRangeRequest.sbcRange.boundaries[0].request.actors.every((actor: Record<string, unknown>) => !('dignity' in actor))).toBe(true)
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

  it('offers a top-level Add Activity to Chart action through the parent callback', async () => {
    apiMocks.fetchSynchronizedIndependentRange.mockResolvedValue(synchronizedRange)
    apiMocks.fetchFxSidePilotStatus.mockResolvedValue(null)
    const user = userEvent.setup()
    const { addActivity } = renderFields()

    const action = await screen.findByRole('button', { name: 'Add USD/JPY Activity to Chart' })
    expect(action).toBeVisible()
    await user.click(action)
    expect(addActivity).toHaveBeenCalledTimes(1)
  })

  it('disables Add Activity to Chart while Founder Review is dirty', async () => {
    apiMocks.fetchSynchronizedIndependentRange.mockResolvedValue(synchronizedRange)
    apiMocks.fetchFxSidePilotStatus.mockResolvedValue(null)
    const user = userEvent.setup()
    const { addActivity } = renderFields({ founderReviewDirty: true })

    const action = await screen.findByRole('button', { name: 'Add USD/JPY Activity to Chart' })
    expect(action).toBeDisabled()
    expect(screen.getByText('Save or discard Founder Review changes before leaving Fields.')).toBeInTheDocument()
    await user.click(action)
    expect(addActivity).not.toHaveBeenCalled()
  })

  it('keeps the activity CTA visible but disabled for unsupported symbols', async () => {
    apiMocks.fetchSynchronizedIndependentRange.mockResolvedValue(synchronizedRange)
    apiMocks.fetchFxSidePilotStatus.mockResolvedValue(null)
    const user = userEvent.setup()
    const { addActivity } = renderFields({ chart: stockChart })

    const action = await screen.findByRole('button', { name: 'Add USD/JPY Activity to Chart' })
    expect(action).toBeDisabled()
    expect(screen.getByText('Chart-native USD/JPY activity is available only for USDJPY.')).toBeInTheDocument()
    await user.click(action)
    expect(addActivity).not.toHaveBeenCalled()
  })

  it('gives dirty Founder Review precedence over unsupported-symbol wording', async () => {
    apiMocks.fetchSynchronizedIndependentRange.mockResolvedValue(synchronizedRange)
    apiMocks.fetchFxSidePilotStatus.mockResolvedValue(null)
    renderFields({ chart: stockChart, founderReviewDirty: true })

    await screen.findByRole('button', { name: 'Add USD/JPY Activity to Chart' })
    expect(screen.getByText('Save or discard Founder Review changes before leaving Fields.')).toBeInTheDocument()
    expect(screen.queryByText('Chart-native USD/JPY activity is available only for USDJPY.')).not.toBeInTheDocument()
  })

  it('compacts zero-coverage directional fields without mounting their detail panes', async () => {
    apiMocks.fetchSynchronizedIndependentRange.mockResolvedValue(zeroCoverageRange)
    apiMocks.fetchFxSidePilotStatus.mockResolvedValue(null)

    renderFields()

    const summary = await screen.findByLabelText('Directional field availability')
    expect(summary).toBeInTheDocument()
    expect(summary).toHaveTextContent('0 / 2 known')
    expect(summary).toHaveTextContent('NO RESOLVED CATEGORICAL POLARITY IN THIS RANGE')
    expect(summary).toHaveTextContent('NO RESOLVED PAIR INTERVALS BECAUSE SIDE EVIDENCE IS UNRESOLVED')
    expect(summary).not.toHaveTextContent('NO ADMITTED POLARITY ENTRIES')
    expect(document.querySelectorAll('.categorical-step-pane')).toHaveLength(0)
    expect(document.querySelectorAll('.categorical-step-hitbox, .categorical-step-gap')).toHaveLength(0)
    expect(screen.getByRole('button', { name: 'Show research details' })).toBeInTheDocument()
  })

  it('expands and collapses zero-coverage research details without inventing a directional value', async () => {
    apiMocks.fetchSynchronizedIndependentRange.mockResolvedValue(zeroCoverageRange)
    apiMocks.fetchFxSidePilotStatus.mockResolvedValue(null)
    const user = userEvent.setup()

    renderFields()

    await user.click(await screen.findByRole('button', { name: 'Show research details' }))
    expect(screen.getAllByText('USD categorical field')).toHaveLength(1)
    expect(screen.getAllByText('JPY categorical field')).toHaveLength(1)
    expect(screen.getAllByText('USDJPY pair-relative field')).toHaveLength(1)
    expect(document.querySelectorAll('.categorical-step-pane')).toHaveLength(3)
    expect(screen.getAllByText(/Unknown evidence: POLARITY_CATALOGUE_MISSING/).length).toBeGreaterThan(0)
    expect(screen.getByRole('button', { name: 'Hide research details' })).toBeInTheDocument()

    await user.click(screen.getByRole('button', { name: 'Hide research details' }))
    expect(screen.getByLabelText('Directional field availability')).toBeInTheDocument()
    expect(document.querySelectorAll('.categorical-step-pane')).toHaveLength(0)
  })

  it('uses stronger zero-catalogue wording only when authoritative pilot status is loaded', async () => {
    apiMocks.fetchSynchronizedIndependentRange.mockResolvedValue(zeroCoverageRange)
    apiMocks.fetchFxSidePilotStatus.mockResolvedValue(zeroCataloguePilotStatus)

    renderFields()

    const summary = await screen.findByLabelText('Directional field availability')
    expect(summary).toHaveTextContent('NO ADMITTED POLARITY ENTRIES')
    expect(summary.querySelector('header')).toHaveTextContent('NO RESOLVED CATEGORICAL POLARITY IN THIS RANGE')
  })

  it('keeps no-active-aspect zero coverage generic when pilot status is unavailable', async () => {
    apiMocks.fetchSynchronizedIndependentRange.mockResolvedValue(noActiveAspectRange)
    apiMocks.fetchFxSidePilotStatus.mockResolvedValue(null)

    renderFields()

    const summary = await screen.findByLabelText('Directional field availability')
    expect(summary).toHaveTextContent('NO RESOLVED CATEGORICAL POLARITY IN THIS RANGE')
    expect(summary.querySelector('header')).toHaveTextContent('NO RESOLVED CATEGORICAL POLARITY IN THIS RANGE')
    expect(summary).not.toHaveTextContent('until an admissible polarity entry exists')
    expect(summary).not.toHaveTextContent('NO ADMITTED POLARITY ENTRIES')
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
    apiMocks.fetchSynchronizedIndependentRange.mockResolvedValue(allDirectionalStatesRange)
    apiMocks.fetchFxSidePilotStatus.mockResolvedValue(null)

    renderFields({ visualizationMode: 'VISUAL_ONLY_NO_SCORE' })

    await screen.findByLabelText('Directional fields')
    expect(screen.getAllByText('DIRECTIONAL FIELD SUPPRESSED BY VISUAL-ONLY MODE')).toHaveLength(1)
    expectDirectionalPresentationWithheld()
    expect(document.querySelectorAll('.categorical-step-pane')).toHaveLength(0)
    expect(screen.getByText('Unsigned Activity Waves')).toBeInTheDocument()
    expect(screen.queryByText(/signed pair resultant/i)).not.toBeInTheDocument()
  })

  it('uses the resolved policy to withhold calibrated directional fields', async () => {
    apiMocks.fetchSynchronizedIndependentRange.mockResolvedValue(synchronizedRange)
    apiMocks.fetchFxSidePilotStatus.mockResolvedValue(null)

    renderFields({ visualizationMode: 'CALIBRATED_RESEARCH' })

    await screen.findByLabelText('Directional fields')
    expect(screen.getAllByText('CALIBRATION SOURCE MISSING')).toHaveLength(1)
    expectDirectionalPresentationWithheld()
    expect(document.querySelectorAll('.categorical-step-pane')).toHaveLength(0)
    expect(screen.getByRole('button', { name: /Inspect USD MARS SQUARE event/i })).toBeInTheDocument()
    expect(screen.getByText('Unsigned Activity Waves')).toBeInTheDocument()
  })

  it('keeps mode changes presentation-only and preserves loaded event identities', async () => {
    apiMocks.fetchSynchronizedIndependentRange.mockResolvedValue(synchronizedRange)
    apiMocks.fetchFxSidePilotStatus.mockResolvedValue(null)
    const user = userEvent.setup()

    render(<ModeSwitchHarness />)
    await screen.findByRole('button', { name: /Inspect USD MARS SQUARE event/i })
    const rangeCalls = apiMocks.fetchSynchronizedIndependentRange.mock.calls.length
    const activityCalls = apiMocks.fetchMultiOscillatorActivityRange.mock.calls.length
    const eventCount = document.querySelectorAll('.mo-event-span').length

    await user.click(screen.getByRole('tab', { name: 'Mode 2' }))
    expect(await screen.findAllByText('CALIBRATION SOURCE MISSING')).toHaveLength(1)
    await user.click(screen.getByRole('tab', { name: 'Mode 3' }))
    expect(await screen.findAllByText('DIRECTIONAL FIELD SUPPRESSED BY VISUAL-ONLY MODE')).toHaveLength(1)
    expect(apiMocks.fetchSynchronizedIndependentRange).toHaveBeenCalledTimes(rangeCalls)
    expect(apiMocks.fetchMultiOscillatorActivityRange).toHaveBeenCalledTimes(activityCalls)
    expect(document.querySelectorAll('.mo-event-span')).toHaveLength(eventCount)
  })

  it('does not refetch range, activity, or BPHS data when presentation mode changes', async () => {
    apiMocks.fetchSynchronizedIndependentRange.mockResolvedValue(synchronizedRange)
    apiMocks.fetchFxSidePilotStatus.mockResolvedValue(null)
    apiMocks.fetchBphsClassicalCalendarRange.mockResolvedValue(bphsCalendarRange)
    window.sessionStorage.setItem('gann-astro.fields.bphs-calendar.enabled.v1', 'true')
    const user = userEvent.setup()

    render(<ModeSwitchHarness />)
    await screen.findByLabelText('BPHS Classical Calendar')
    await waitFor(() => {
      expect(apiMocks.fetchSynchronizedIndependentRange).toHaveBeenCalled()
      expect(apiMocks.fetchMultiOscillatorActivityRange).toHaveBeenCalled()
      expect(apiMocks.fetchBphsClassicalCalendarRange).toHaveBeenCalled()
    })
    const rangeCalls = apiMocks.fetchSynchronizedIndependentRange.mock.calls.length
    const activityCalls = apiMocks.fetchMultiOscillatorActivityRange.mock.calls.length
    const bphsCalls = apiMocks.fetchBphsClassicalCalendarRange.mock.calls.length

    await user.click(screen.getByRole('tab', { name: 'Mode 2' }))
    await user.click(screen.getByRole('tab', { name: 'Mode 3' }))

    expect(apiMocks.fetchSynchronizedIndependentRange).toHaveBeenCalledTimes(rangeCalls)
    expect(apiMocks.fetchMultiOscillatorActivityRange).toHaveBeenCalledTimes(activityCalls)
    expect(apiMocks.fetchBphsClassicalCalendarRange).toHaveBeenCalledTimes(bphsCalls)
  })

  it('keeps the unified inspector empty until an explicit item is selected', async () => {
    apiMocks.fetchSynchronizedIndependentRange.mockResolvedValue(synchronizedRange)
    apiMocks.fetchFxSidePilotStatus.mockResolvedValue(null)

    renderFields()

    await screen.findByText('USDJPY pair-relative field')
    expect(screen.getAllByText('NO RESEARCH ITEM SELECTED')).toHaveLength(2)
    expect(screen.queryByText('Selected pair interval')).not.toBeInTheDocument()
  })

  it('withholds a selected pair value in Mode 3 instead of exposing hidden directional data', async () => {
    apiMocks.fetchSynchronizedIndependentRange.mockResolvedValue(synchronizedRange)
    apiMocks.fetchFxSidePilotStatus.mockResolvedValue(null)
    const user = userEvent.setup()

    render(<ModeSwitchHarness />)
    await screen.findByText('USDJPY pair-relative field')
    await user.click(screen.getByRole('button', { name: /Select PAIR interval SUPPORTIVE/i }))
    expect(screen.getByText('Selected: PAIR INTERVAL')).toBeInTheDocument()
    await user.click(screen.getByRole('tab', { name: 'Mode 3' }))
    expect(screen.getByText('PAIR_INTERVAL | WITHHELD BY CURRENT MODE')).toBeInTheDocument()
    expectDirectionalPresentationWithheld()
    expect(screen.queryByText('Pair display')).not.toBeInTheDocument()
    expect(screen.queryByText('Pair raw')).not.toBeInTheDocument()
    expect(screen.queryByText('USD balance')).not.toBeInTheDocument()
    expect(screen.queryByText('JPY balance')).not.toBeInTheDocument()
  })

  it('retains a selected USD field identity while withholding its directional state', async () => {
    apiMocks.fetchSynchronizedIndependentRange.mockResolvedValue(synchronizedRange)
    apiMocks.fetchFxSidePilotStatus.mockResolvedValue(null)
    const user = userEvent.setup()

    render(<ModeSwitchHarness />)
    await screen.findByText('USD categorical field')
    await user.click(screen.getByRole('button', { name: /Select USD interval SUPPORTIVE/i }))
    expect(screen.getByText('Selected: FIELD INTERVAL')).toBeInTheDocument()
    await user.click(screen.getByRole('tab', { name: 'Mode 3' }))

    expect(screen.getByText('FIELD_INTERVAL | USD | WITHHELD BY CURRENT MODE')).toBeInTheDocument()
    expectDirectionalPresentationWithheld()
    expect(screen.queryByText('State')).not.toBeInTheDocument()
    expect(screen.queryByText('Supportive active')).not.toBeInTheDocument()
    expect(screen.queryByText('Adverse active')).not.toBeInTheDocument()
  })

  it('lifts explicit BPHS selection into the unified inspector without changing field data', async () => {
    apiMocks.fetchSynchronizedIndependentRange.mockResolvedValue(synchronizedRange)
    apiMocks.fetchFxSidePilotStatus.mockResolvedValue(null)
    apiMocks.fetchBphsClassicalCalendarRange.mockResolvedValue(bphsCalendarRange)
    const user = userEvent.setup()
    const { activitySelection } = renderFields()

    await user.click(screen.getByRole('switch', { name: /BPHS Calendar/i }))
    await screen.findByText('BPHS Classical Calendar')
    await user.click(screen.getByRole('button', { name: /Select Muhurta/i }))
    expect(screen.getByText('Selected: BPHS INTERVAL')).toBeInTheDocument()
    expect(screen.getAllByText('NO MARKET ROLE').length).toBeGreaterThan(0)
    expect(activitySelection).toHaveBeenCalledWith(startUtc)
  })

  it('shows Trailokya as geometry-only availability without a scored fallback', async () => {
    apiMocks.fetchSynchronizedIndependentRange.mockResolvedValue(geometryOnlyRange)
    apiMocks.fetchFxSidePilotStatus.mockResolvedValue(null)

    renderFields({ vedhaProfileId: 'SBC_TRAILOKYA_1972_V1' })

    expect((await screen.findAllByText(/GEOMETRY_ONLY_RANGE_NOT_IMPLEMENTED/)).length).toBeGreaterThan(0)
    expect(screen.getByText(/No score, polarity, wave, or fallback/)).toBeInTheDocument()
    expect(screen.queryByText(/Guidance score/i)).not.toBeInTheDocument()
  })

  it('uses Trailokya policy scoringVisible=false as the directional gate', async () => {
    apiMocks.fetchSynchronizedIndependentRange.mockResolvedValue(geometryOnlyRange)
    apiMocks.fetchFxSidePilotStatus.mockResolvedValue(null)

    renderFields({ vedhaProfileId: 'SBC_TRAILOKYA_1972_V1' })

    await screen.findByLabelText('Directional fields')
    expect(screen.getAllByText('DIRECTIONAL FIELDS WITHHELD BY RESOLVED SOURCE POLICY')).toHaveLength(1)
    expectDirectionalPresentationWithheld()
  })

  it('preserves directional labels and hitboxes in Mode 1', async () => {
    apiMocks.fetchSynchronizedIndependentRange.mockResolvedValue(synchronizedRange)
    apiMocks.fetchFxSidePilotStatus.mockResolvedValue(null)

    renderFields()

    await screen.findByText('USD categorical field')
    expect(screen.getAllByText('Supportive')).toHaveLength(3)
    expect(screen.getAllByText('Neutral')).toHaveLength(3)
    expect(screen.getByRole('button', { name: /Select USD interval SUPPORTIVE/i })).toBeInTheDocument()
    expect(document.querySelectorAll('.categorical-step-hitbox')).not.toHaveLength(0)
    expect(document.querySelectorAll('.categorical-step-balance')).not.toHaveLength(0)
  })

  it('keeps the founder workstation in the accepted reading order and exposes its context controls', async () => {
    apiMocks.fetchSynchronizedIndependentRange.mockResolvedValue(synchronizedRange)
    apiMocks.fetchFxSidePilotStatus.mockResolvedValue(null)
    const user = userEvent.setup()

    renderFields()
    await screen.findByText('USD categorical field')
    await user.click(screen.getByRole('switch', { name: /BPHS Calendar/i }))
    await screen.findByText('BPHS Classical Calendar')

    const price = screen.getByLabelText('Synchronized price chart')
    const summary = screen.getByLabelText('Shared time and research selection summary')
    const fields = screen.getByLabelText('Synchronized independent fields')
    const activity = screen.getByLabelText('Unsigned multi-oscillator activity')
    const bphs = screen.getByLabelText('BPHS Classical Calendar')
    const inspector = screen.getByLabelText('Unified Fields research inspector')
    expect(price.compareDocumentPosition(summary) & Node.DOCUMENT_POSITION_FOLLOWING).toBeTruthy()
    expect(summary.compareDocumentPosition(fields) & Node.DOCUMENT_POSITION_FOLLOWING).toBeTruthy()
    expect(fields.compareDocumentPosition(activity) & Node.DOCUMENT_POSITION_FOLLOWING).toBeTruthy()
    expect(activity.compareDocumentPosition(bphs) & Node.DOCUMENT_POSITION_FOLLOWING).toBeTruthy()
    expect(bphs.compareDocumentPosition(inspector) & Node.DOCUMENT_POSITION_FOLLOWING).toBeTruthy()
    expect(screen.getByRole('tab', { name: 'Mode 1' })).toBeInTheDocument()
    expect(screen.getByLabelText('Source profile')).toBeInTheDocument()
    expect(screen.getAllByText(/Source gaps \(/).length).toBeGreaterThanOrEqual(2)
    expect(screen.getByRole('button', { name: /Founder Review/i })).toBeInTheDocument()
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
