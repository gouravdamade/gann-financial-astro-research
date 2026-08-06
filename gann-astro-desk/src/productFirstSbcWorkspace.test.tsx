// @vitest-environment jsdom

import '@testing-library/jest-dom/vitest'
import { cleanup, render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { afterEach, describe, expect, it, vi } from 'vitest'
import type {
  AspectWindow,
  ChakraFixedPhasorInterval,
  ChakraLabSnapshot,
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

  it('keeps Fields as a dedicated workspace hand-off instead of embedding field lanes', async () => {
    const user = userEvent.setup()
    const onOpenFields = vi.fn()
    render(
      <ProductFirstSbcWorkspace
        chart={chart}
        snapshot={snapshot}
        selectedCell="1:1"
        onSelectCell={() => undefined}
        onSelectMoment={() => undefined}
        visualizationPolicy={visualizationModePolicy('SOURCE_ONLY_BASELINE')}
        phasorBusy={false}
        phasorError=""
        onLoadFixedPhasor={() => undefined}
        onOpenFields={onOpenFields}
      />,
    )

    expect(screen.queryByRole('region', { name: 'Independent synchronized field stack' })).not.toBeInTheDocument()
    expect(screen.getByText(/USD, JPY, pair-relative, and independent SBC fields are available/i)).toBeInTheDocument()
    await user.click(screen.getAllByRole('button', { name: 'Open in Fields' })[0])
    expect(onOpenFields).toHaveBeenCalledTimes(1)
  })

  it('keeps every Chakra toolbar control reachable while Fields remains external', () => {
    render(
      <ProductFirstSbcWorkspace
        chart={chart}
        snapshot={snapshot}
        selectedCell="1:1"
        onSelectCell={() => undefined}
        onSelectMoment={() => undefined}
        visualizationPolicy={visualizationModePolicy('SOURCE_ONLY_BASELINE')}
        phasorBusy={false}
        phasorError=""
        onLoadFixedPhasor={() => undefined}
      />,
    )

    const toolbar = screen.getByRole('group', { name: 'Workspace view controls' })
    expect(toolbar).toBeInTheDocument()
    for (const label of ['Previous loaded candle', 'Time', 'Profile', 'Wheel', 'Phase lab', 'Compare', 'Next loaded candle']) {
      const buttons = screen.getAllByRole('button', { name: label })
      expect(buttons.length).toBeGreaterThan(0)
    }
    expect(toolbar.className).toContain('product-first-view-controls')
  })
})
