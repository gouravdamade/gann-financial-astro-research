import { describe, expect, it } from 'vitest'
import type { MultiOscillatorActivityInterval } from '../types'
import {
  deriveUnsignedActivityStepSegments,
  MO_UNSIGNED_ACTIVITY_STEP_WAVE_CONTRACT,
  unsignedActivityStepWavePath,
  unsignedActivityWaveY,
  WAVE_PLOT_BASELINE,
} from './MultiOscillatorActivityWave'

const rangeStartUtc = '2026-08-01T00:00:00.000Z'
const hourUtc = '2026-08-01T01:00:00.000Z'
const threeHourUtc = '2026-08-01T03:00:00.000Z'
const fourHourUtc = '2026-08-01T04:00:00.000Z'

function interval(
  startUtc: string,
  endUtc: string,
  rawActiveEventCount: number,
  coverage: MultiOscillatorActivityInterval['coverage'] = 'KNOWN',
): MultiOscillatorActivityInterval {
  return {
    intervalId: `${startUtc}-${endUtc}`,
    startUtc,
    endUtc,
    rawActiveEventCount,
    contributingEventIds: Array.from({ length: rawActiveEventCount }, (_, index) => `event-${index}`),
    coverage,
    unknownReason: coverage === 'UNKNOWN' ? 'coverage is incomplete' : null,
  }
}

describe('MO unsigned activity step wave', () => {
  it('declares the exploratory unsigned step-wave contract', () => {
    expect(MO_UNSIGNED_ACTIVITY_STEP_WAVE_CONTRACT).toBe('MO_UNSIGNED_ACTIVITY_STEP_WAVE_V1')
  })

  it('derives exact interval segments without changing raw counts or provenance IDs', () => {
    const source = [interval(rangeStartUtc, hourUtc, 2), interval(hourUtc, threeHourUtc, 5), interval(threeHourUtc, fourHourUtc, 0)]
    const segments = deriveUnsignedActivityStepSegments(source)

    expect(segments).toHaveLength(3)
    expect(segments.map((segment) => [segment.startUtc, segment.endUtc, segment.rawActiveEventCount])).toEqual([
      [rangeStartUtc, hourUtc, 2],
      [hourUtc, threeHourUtc, 5],
      [threeHourUtc, fourHourUtc, 0],
    ])
    expect(segments[0].contributingEventIds).toEqual(['event-0', 'event-1'])
    expect(segments[0].semanticUnit).toBe('ACTIVE_EVENT_COUNT')
  })

  it('renders 2, 5 and 0 as a zero-order-hold path at exact boundaries', () => {
    const segments = deriveUnsignedActivityStepSegments([
      interval(rangeStartUtc, hourUtc, 2),
      interval(hourUtc, threeHourUtc, 5),
      interval(threeHourUtc, fourHourUtc, 0),
    ])

    expect(unsignedActivityStepWavePath(segments, rangeStartUtc, fourHourUtc, 5)).toBe('M 0 58.4 H 25 V 8 H 75 V 92 H 100')
    expect(unsignedActivityWaveY(0, 5)).toBe(WAVE_PLOT_BASELINE)
    expect(unsignedActivityWaveY(5, 5)).toBe(8)
  })

  it('preserves an observed count while marking incomplete coverage', () => {
    const segments = deriveUnsignedActivityStepSegments([interval(rangeStartUtc, hourUtc, 5, 'UNKNOWN')])

    expect(segments[0].rawActiveEventCount).toBe(5)
    expect(segments[0].coverage).toBe('UNKNOWN')
    expect(segments[0].unknownReason).toBe('coverage is incomplete')
  })

  it('starts a new path across a non-contiguous interval gap instead of interpolating it', () => {
    const gapStartUtc = '2026-08-01T05:00:00.000Z'
    const rangeEndUtc = '2026-08-01T06:00:00.000Z'
    const sixHourUtc = '2026-08-01T06:00:00.000Z'
    const segments = deriveUnsignedActivityStepSegments([
      interval(rangeStartUtc, hourUtc, 2),
      interval(gapStartUtc, sixHourUtc, 5),
    ])

    expect(unsignedActivityStepWavePath(segments, rangeStartUtc, rangeEndUtc, 5)).toBe('M 0 58.4 H 16.6667 M 83.3333 8 H 100')
  })
})
