// @vitest-environment jsdom

import '@testing-library/jest-dom/vitest'
import { cleanup, render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { afterEach, describe, expect, it, vi } from 'vitest'
import type {
  AspectWindow,
  ChakraFixedPhasorInterval,
  ChakraLabSnapshot,
  FxSidePilotStatus,
  SynchronizedIndependentRange,
} from './types'
import { visualizationModePolicy } from './visualizationModes'
import { ProductFirstSbcWorkspace } from './views/ProductFirstSbcWorkspace'

afterEach(() => {
  cleanup()
  window.localStorage.removeItem('gann-astro.oscillators-open')
})

const snapshot = {
  as_of_utc: '2026-08-01T12:00:00Z',
  requested_at_local: '2026-08-01T17:30:00+05:30',
  foundation_snapshot: {
    profile_id: 'source-profile-test',
    panchanga: {
      tithi_name: 'Saptami', paksha: 'Shukla', yoga_name: 'Shobhana', karana_name: 'Gara',
      vara: { weekday: 'Friday' },
    },
  },
  grid: { cells: [], grid_profile_id: 'partial-grid', certified_layers: [] },
  target_context: [],
  actor_readiness: [],
  guidance: {
    contributions: [],
    favorable_guidance_units: 8.75,
    adverse_guidance_units: -2.5,
    net_guidance_units: 6.25,
    scoring_coverage_ratio: 0.9,
  },
} as unknown as ChakraLabSnapshot

const selectedAspect = {
  eventId: 'event-test-001',
  familyKey: 'MARS|SUN::square',
  transitBody: 'MARS',
  natalBody: 'SUN',
  aspect: 'square',
  astronomyContract: 'RAMAN_SIDEREAL_SWISSEPH_V1',
  sourceGenerator: 'test-generator',
} as unknown as AspectWindow

const synchronizedRange = {
  rangeStartUtc: '2026-08-01T10:00:00Z',
  rangeEndUtc: '2026-08-01T12:00:00Z',
  aspectFields: {
    USD: { intervals: [{ intervalId: 'usd-1', startUtc: '2026-08-01T10:00:00Z', endUtc: '2026-08-01T12:00:00Z', polarityState: 'UNKNOWN', reason: 'No accepted side evidence.' }] },
    JPY: { intervals: [{ intervalId: 'jpy-1', startUtc: '2026-08-01T10:00:00Z', endUtc: '2026-08-01T12:00:00Z', polarityState: 'UNKNOWN', reason: 'No accepted side evidence.' }] },
  },
  sbcField: { intervals: [{ interval_id: 'sbc-1', start_utc: '2026-08-01T10:00:00Z', end_utc: '2026-08-01T12:00:00Z', guidance_availability: 'AVAILABLE', missing_evidence_ids: [] }] },
  guardrails: { executionAllowed: false, fieldsFused: false, marketDirectionInferred: false },
} as unknown as SynchronizedIndependentRange

const trailokyaSynchronizedRange = {
  rangeStartUtc: '2026-08-01T10:00:00Z',
  rangeEndUtc: '2026-08-01T12:00:00Z',
  aspectFields: {
    USD: { intervals: [{ intervalId: 'usd-unknown', startUtc: '2026-08-01T10:00:00Z', endUtc: '2026-08-01T12:00:00Z', polarityState: 'UNKNOWN', reason: 'No accepted side evidence.' }] },
    JPY: { intervals: [{ intervalId: 'jpy-unknown', startUtc: '2026-08-01T10:00:00Z', endUtc: '2026-08-01T12:00:00Z', polarityState: 'UNKNOWN', reason: 'No accepted side evidence.' }] },
  },
  sbcField: {
    contract: 'SBC_TRAILOKYA_1972_GEOMETRY_ONLY_RANGE_V1',
    schema_version: 1,
    state: 'GEOMETRY_ONLY_RANGE_NOT_IMPLEMENTED',
    instrument_identity: 'FX:USDJPY',
    range_start_utc: '2026-08-01T10:00:00Z',
    range_end_utc: '2026-08-01T12:00:00Z',
    source_profile_id: 'SBC_TRAILOKYA_1972_V1',
    aspect_relationship: 'NOT_AUTOMATIC_CONFIRMATION',
    magnitude_state: 'NOT_CONFIGURED',
    classicalCompletenessClaim: false,
    source_gaps: ['SBC_TD1972_GEOMETRY_RANGE_NOT_COMPILED'],
    intervals: [],
    reason: 'Trailokya source-only geometry has no synchronized range compiler.',
    guardrails: { read_only: true, execution_allowed: false, automatic_order_placement: false, financially_validated: false, acts_as_aspect_confirmation: false, score_aggregation_used: false, market_direction_inferred: false },
  },
  guardrails: { executionAllowed: false, fieldsFused: false, marketDirectionInferred: false },
} as unknown as SynchronizedIndependentRange

const pilotStatus = {
  status: 'PILOT_EVIDENCE_PENDING',
  summary: 'No side has the minimum reviewed categorical examples yet.',
  sides: {
    USD: { catalogueEntryCount: 0, missingRequiredStates: ['SUPPORTIVE', 'ADVERSE'] },
    JPY: { catalogueEntryCount: 0, missingRequiredStates: ['SUPPORTIVE', 'ADVERSE'] },
  },
} as unknown as FxSidePilotStatus

const chart = {
  symbol: 'USDJPY',
  timeframe: 'H1',
  candles: [
    { time: 1_754_043_600, open: 147, high: 147.2, low: 146.8, close: 147.1 },
    { time: 1_754_047_200, open: 147.1, high: 147.3, low: 147, close: 147.2 },
  ],
  aspects: [],
} as unknown as Parameters<typeof ProductFirstSbcWorkspace>[0]['chart']

function interval(magnitude: number, total: number): ChakraFixedPhasorInterval {
  return {
    vectors: [{
      vector_id: 'sun-zero', actor_identity: 'SUN', fixed_angle: 'ZERO', target_value: 'ARIES',
      projection_status: 'PLOTTED', magnitude_units: magnitude, real_component_units: magnitude,
    }],
    vector_magnitude_sum_units: total,
    vector_real_sum_units: total,
    vector_imaginary_sum_units: 0,
    known_scored_coherence_ratio: 0.8,
    real_matches_net: true,
  } as unknown as ChakraFixedPhasorInterval
}

function renderSuppressed(fixedPhasorInterval: ChakraFixedPhasorInterval) {
  return render(
    <ProductFirstSbcWorkspace
      snapshot={snapshot}
      selectedCell="1:1"
      onSelectCell={() => undefined}
      onSelectMoment={() => undefined}
      fixedPhasorInterval={fixedPhasorInterval}
      visualizationPolicy={visualizationModePolicy('VISUAL_ONLY_NO_SCORE')}
      phasorBusy={false}
      phasorError=""
      onLoadFixedPhasor={() => undefined}
    />,
  )
}

describe('ProductFirstSbcWorkspace score suppression', () => {
  it('keeps the visual-only wheel DOM and SVG invariant when hidden scalar values change', async () => {
    const user = userEvent.setup()
    const first = renderSuppressed(interval(1, 1))
    await user.click(screen.getByRole('button', { name: 'Wheel' }))

    const firstSvg = first.container.querySelector('.product-first-wheel svg')?.outerHTML
    const firstText = first.container.textContent ?? ''
    expect(firstText).toContain('Value suppressed')
    expect(firstText).not.toContain('1.0')
    expect(firstText).not.toContain('8.8')
    expect(firstSvg).not.toContain('1.00')
    first.unmount()

    const second = renderSuppressed(interval(99, 275))
    await user.click(screen.getByRole('button', { name: 'Wheel' }))

    expect(second.container.querySelector('.product-first-wheel svg')?.outerHTML).toBe(firstSvg)
    const secondText = second.container.textContent ?? ''
    expect(secondText).not.toContain('99.0')
    expect(secondText).not.toContain('275.0')
    expect(secondText).not.toContain('8.8')
  }, 15_000)

  it('retains exact scalar geometry only in the source-profiled partial baseline', async () => {
    const user = userEvent.setup()
    const rendered = render(
      <ProductFirstSbcWorkspace
        snapshot={snapshot}
        selectedCell="1:1"
        onSelectCell={() => undefined}
        onSelectMoment={() => undefined}
        fixedPhasorInterval={interval(2, 2)}
        visualizationPolicy={visualizationModePolicy('SOURCE_ONLY_BASELINE')}
        phasorBusy={false}
        phasorError=""
        onLoadFixedPhasor={() => undefined}
      />,
    )
    await user.click(screen.getByRole('button', { name: 'Wheel' }))

    expect(rendered.container.querySelector('.product-first-wheel-gross-ring')).toBeInTheDocument()
    expect(rendered.container.textContent).toContain('2.0 units')
    expect(rendered.container.textContent).toContain('Founder approval pending')
  })

  it('prepares a selected-aspect evidence packet without admitting polarity', () => {
    render(
      <ProductFirstSbcWorkspace
        snapshot={snapshot}
        selectedCell="1:1"
        onSelectCell={() => undefined}
        onSelectMoment={() => undefined}
        selectedAspect={selectedAspect}
        visualizationPolicy={visualizationModePolicy('SOURCE_ONLY_BASELINE')}
        phasorBusy={false}
        phasorError=""
        onLoadFixedPhasor={() => undefined}
      />,
    )

    expect(screen.getByText('Side-chart evidence packet readiness')).toBeInTheDocument()
    expect(screen.getByText(/MARS to SUN Square/i)).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'USD candidate' })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'JPY candidate' })).toBeInTheDocument()
    expect(screen.getByText(/Still required per side: accepted chart id/i)).toBeInTheDocument()
  })

  it('opens three separate synchronized field lanes without a combined signal', async () => {
    const user = userEvent.setup()
    const onLoadSynchronizedFields = vi.fn()
    const onLoadPilotStatus = vi.fn()
    render(
      <ProductFirstSbcWorkspace
        chart={chart}
        snapshot={snapshot}
        selectedCell="1:1"
        onSelectCell={() => undefined}
        onSelectMoment={() => undefined}
        synchronizedRange={synchronizedRange}
        onLoadSynchronizedFields={onLoadSynchronizedFields}
        pilotStatus={pilotStatus}
        onLoadPilotStatus={onLoadPilotStatus}
        visualizationPolicy={visualizationModePolicy('SOURCE_ONLY_BASELINE')}
        phasorBusy={false}
        phasorError=""
        onLoadFixedPhasor={() => undefined}
      />,
    )

    expect(onLoadSynchronizedFields).not.toHaveBeenCalled()
    expect(onLoadPilotStatus).not.toHaveBeenCalled()
    expect(screen.getByRole('region', { name: 'Independent synchronized field stack' })).toBeInTheDocument()
    expect(screen.getByRole('region', { name: 'Independent synchronized field stack' }).closest('.product-first-market-panel')).not.toBeNull()
    expect(screen.getByText('USD categorical field')).toBeInTheDocument()
    expect(screen.getByText('JPY categorical field')).toBeInTheDocument()
    expect(screen.getByText('SBC atomic field')).toBeInTheDocument()
    expect(screen.getByText(/No magnitude, fusion, automatic confirmation/i)).toBeInTheDocument()
    expect(screen.getByRole('region', { name: 'FX side pilot status' })).toBeInTheDocument()
    expect(screen.getByText(/Pilot Evidence Pending/i)).toBeInTheDocument()
    expect(screen.getAllByText(/Needs SUPPORTIVE \+ ADVERSE/)).toHaveLength(2)

    await user.click(screen.getByRole('button', { name: 'Fields' }))
    expect(screen.queryByRole('region', { name: 'Independent synchronized field stack' })).not.toBeInTheDocument()
    await user.click(screen.getByRole('button', { name: 'Fields' }))
    expect(screen.getByRole('region', { name: 'Independent synchronized field stack' })).toBeInTheDocument()
  })

  it('selects a canonical field interval without deriving a pair signal', async () => {
    const user = userEvent.setup()
    const onSelectFieldInterval = vi.fn()
    render(
      <ProductFirstSbcWorkspace
        chart={chart}
        snapshot={snapshot}
        selectedCell="1:1"
        onSelectCell={() => undefined}
        onSelectMoment={() => undefined}
        synchronizedRange={synchronizedRange}
        onSelectFieldInterval={onSelectFieldInterval}
        visualizationPolicy={visualizationModePolicy('SOURCE_ONLY_BASELINE')}
        phasorBusy={false}
        phasorError=""
        onLoadFixedPhasor={() => undefined}
      />,
    )

    await user.click(screen.getByRole('button', { name: /Select USD interval UNKNOWN/i }))

    expect(onSelectFieldInterval).toHaveBeenCalledWith({
      field: 'USD',
      intervalId: 'usd-1',
      startUtc: '2026-08-01T10:00:00Z',
      endUtc: '2026-08-01T12:00:00Z',
    })
    expect(screen.getByText(/No magnitude, fusion, automatic confirmation/i)).toBeInTheDocument()
  })

  it('keeps Trailokya source-only range unavailable without a scored fallback', () => {
    render(
      <ProductFirstSbcWorkspace
        chart={chart}
        snapshot={snapshot}
        selectedCell="1:1"
        onSelectCell={() => undefined}
        onSelectMoment={() => undefined}
        synchronizedRange={trailokyaSynchronizedRange}
        visualizationPolicy={visualizationModePolicy('SOURCE_ONLY_BASELINE')}
        phasorBusy={false}
        phasorError=""
        onLoadFixedPhasor={() => undefined}
      />,
    )

    expect(screen.getByText(/GEOMETRY_ONLY_RANGE_NOT_IMPLEMENTED/)).toBeInTheDocument()
    expect(screen.getByText(/has no compiled range or score/i)).toBeInTheDocument()
    expect(screen.queryByText(/Supportive.*Obstructive.*Net/)).not.toBeInTheDocument()
  })

  it('keeps every workspace toolbar control reachable while the field stack is expanded', () => {
    render(
      <ProductFirstSbcWorkspace
        chart={chart}
        snapshot={snapshot}
        selectedCell="1:1"
        onSelectCell={() => undefined}
        onSelectMoment={() => undefined}
        synchronizedRange={synchronizedRange}
        visualizationPolicy={visualizationModePolicy('SOURCE_ONLY_BASELINE')}
        phasorBusy={false}
        phasorError=""
        onLoadFixedPhasor={() => undefined}
      />,
    )

    const toolbar = screen.getByRole('group', { name: 'Workspace view controls' })
    expect(toolbar).toBeInTheDocument()
    for (const label of ['Previous loaded candle', 'Time', 'Profile', 'Wheel', 'Phase lab', 'Compare', 'Fields', 'Next loaded candle']) {
      expect(screen.getByRole('button', { name: label })).toBeInTheDocument()
    }
    expect(toolbar.className).toContain('product-first-view-controls')
  })
})
