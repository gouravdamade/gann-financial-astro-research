// @vitest-environment jsdom

import '@testing-library/jest-dom/vitest'
import { cleanup, fireEvent, render, screen } from '@testing-library/react'
import { afterEach, describe, expect, it, vi } from 'vitest'
import type {
  PlanetaryCollectiveField,
  PlanetaryCollectiveSample,
} from '../types'
import { CollectiveFieldInspector } from './CollectiveFieldInspector'

afterEach(cleanup)

const firstTime = 1_700_000_000
const secondTime = firstTime + 3_600

function memberAudit(body: string, rank: number) {
  return {
    body,
    longitudeDeg: body === 'MOON' ? 150 : 140,
    weight: 0.5,
    angularDistanceFromMeanDeg: 5,
    longitudeLeverageDeg: body === 'MOON' ? 8 : 2,
    coherenceLeverage: body === 'MOON' ? -0.12 : 0.04,
    tempoClass: 'FAST_MOVING_CLASS' as const,
    role: body === 'MOON'
      ? 'DISPERSING_FAST_DRIVER'
      : 'CONCENTRATING_FAST_MEMBER',
    influenceRank: rank,
  }
}

function sample(
  time: number,
  overrides: Partial<PlanetaryCollectiveSample> = {},
): PlanetaryCollectiveSample {
  return {
    time,
    meanLongitudeDeg: 145,
    coherenceR1: 0.72,
    circularVariance: 0.28,
    circularStdDeg: 46,
    polarisationR2: 0.31,
    polarisationAxisDeg: 60,
    state: 'CONCENTRATED',
    reliability: 'RELIABLE',
    longitudeReliable: true,
    segmentId: 1,
    unwrappedLongitudeDeg: 145,
    velocityDegPerDay: 0.8,
    accelerationDegPerDay2: null,
    memberAudit: [memberAudit('MOON', 1), memberAudit('SUN', 2)],
    ...overrides,
  }
}

function field(
  samples: PlanetaryCollectiveSample[] = [
    sample(firstTime, { meanLongitudeDeg: 140 }),
    sample(secondTime, { meanLongitudeDeg: 145 }),
  ],
): PlanetaryCollectiveField {
  return {
    profile: {
      profileId: 'AVG_ALL_TEST',
      members: ['SUN', 'MOON'],
      memberSetHash: 'sha256:test',
    },
    samples,
    latest: samples.at(-1),
    events: [
      {
        eventId: 'event-1',
        eventType: 'MEAN_RASHI_INGRESS',
        estimatedTimeUnix: secondTime,
        details: { fromRashi: 'ARIES', toRashi: 'TAURUS' },
      },
    ],
  } as unknown as PlanetaryCollectiveField
}

describe('CollectiveFieldInspector', () => {
  it('shows deterministic lanes, member influence, and research guardrails', () => {
    render(
      <CollectiveFieldInspector
        field={field()}
        cursorTime={null}
        pinnedTime={null}
        onHoverTime={vi.fn()}
        onPinTime={vi.fn()}
        onClose={vi.fn()}
      />,
    )

    expect(screen.getByText('Planetary Collective Field')).toBeInTheDocument()
    expect(screen.getByText('AVG 2 | synthetic research geometry')).toBeInTheDocument()
    expect(screen.getByText('dispersing fast driver')).toBeInTheDocument()
    expect(screen.getByText('2 bar-time samples')).toBeInTheDocument()
    expect(screen.getByText(/Coefficient 0.0/)).toHaveTextContent('no inference')
  })

  it('synchronizes the accessible time control and pin command', () => {
    const onHoverTime = vi.fn()
    const onPinTime = vi.fn()
    const { rerender } = render(
      <CollectiveFieldInspector
        field={field()}
        cursorTime={firstTime}
        pinnedTime={null}
        onHoverTime={onHoverTime}
        onPinTime={onPinTime}
        onClose={vi.fn()}
      />,
    )

    fireEvent.change(screen.getByRole('slider', { name: 'Collective field timestamp' }), {
      target: { value: '1' },
    })
    expect(onHoverTime).toHaveBeenLastCalledWith(secondTime)

    fireEvent.click(screen.getByRole('button', { name: 'Pin selected collective timestamp' }))
    expect(onPinTime).toHaveBeenLastCalledWith(firstTime)

    rerender(
      <CollectiveFieldInspector
        field={field()}
        cursorTime={null}
        pinnedTime={secondTime}
        onHoverTime={onHoverTime}
        onPinTime={onPinTime}
        onClose={vi.fn()}
      />,
    )
    fireEvent.click(screen.getByRole('button', { name: 'Clear pinned collective timestamp' }))
    expect(onPinTime).toHaveBeenLastCalledWith(null)
  })

  it('does not invent a mean marker when longitude is unreliable', () => {
    const unstable = sample(firstTime, {
      meanLongitudeDeg: null,
      coherenceR1: 0,
      circularVariance: 1,
      polarisationR2: 1,
      polarisationAxisDeg: 0,
      state: 'BIPOLAR',
      reliability: 'UNSTABLE',
      longitudeReliable: false,
      segmentId: null,
      unwrappedLongitudeDeg: null,
      velocityDegPerDay: null,
      memberAudit: [
        {
          ...memberAudit('MOON', 1),
          angularDistanceFromMeanDeg: null,
          longitudeLeverageDeg: null,
          coherenceLeverage: null,
          influenceRank: null,
          role: 'UNKNOWN',
        },
        {
          ...memberAudit('SUN', 2),
          angularDistanceFromMeanDeg: null,
          longitudeLeverageDeg: null,
          coherenceLeverage: null,
          influenceRank: null,
          role: 'UNKNOWN',
        },
      ],
    })
    const { container } = render(
      <CollectiveFieldInspector
        field={field([unstable])}
        cursorTime={null}
        pinnedTime={null}
        onHoverTime={vi.fn()}
        onPinTime={vi.fn()}
        onClose={vi.fn()}
      />,
    )

    expect(container.querySelector('.collective-field-selected-marker')).toBeNull()
    expect(screen.getAllByText('n/a').length).toBeGreaterThan(0)
  })
})
