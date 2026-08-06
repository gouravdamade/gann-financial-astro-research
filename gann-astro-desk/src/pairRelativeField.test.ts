import { describe, expect, it } from 'vitest'
import type { ChartConditionedPolarityRangeInterval, SynchronizedIndependentRange } from './types'
import { compileFxPairRelativeCategoricalField } from './pairRelativeField'

function sideInterval(
  intervalId: string,
  startUtc: string,
  endUtc: string,
  polarityState: ChartConditionedPolarityRangeInterval['polarityState'],
  supportiveActive = false,
  adverseActive = false,
): ChartConditionedPolarityRangeInterval {
  return {
    intervalId,
    startUtc,
    endUtc,
    polarityState,
    supportiveActive,
    adverseActive,
    activeEventIds: [],
    unknownEventIds: [],
    reason: polarityState === 'UNKNOWN' ? 'POLARITY_CATALOGUE_MISSING' : 'fixture',
  }
}

function range(usd: ChartConditionedPolarityRangeInterval[], jpy: ChartConditionedPolarityRangeInterval[]): SynchronizedIndependentRange {
  return {
    contract: 'SYNCHRONIZED_INDEPENDENT_RANGE_V1',
    schemaVersion: 1,
    rangeStartUtc: '2025-04-01T00:00:00.000Z',
    rangeEndUtc: '2025-04-01T03:00:00.000Z',
    synchronizationStatus: 'SYNCHRONIZED',
    aspectFields: {
      USD: { intervals: usd },
      JPY: { intervals: jpy },
    },
    sbcField: { intervals: [] },
    guardrails: {
      readOnly: true,
      fieldsRemainIndependent: true,
      fieldsFused: false,
      marketDirectionInferred: false,
      executionAllowed: false,
    },
  } as unknown as SynchronizedIndependentRange
}

describe('FX_PAIR_RELATIVE_CATEGORICAL_FIELD_V1', () => {
  it('uses the union of source boundaries without sampling or smoothing', () => {
    const result = compileFxPairRelativeCategoricalField(range(
      [sideInterval('usd-a', '2025-04-01T00:00:00.000Z', '2025-04-01T02:00:00.000Z', 'SUPPORTIVE', true)],
      [
        sideInterval('jpy-a', '2025-04-01T00:00:00.000Z', '2025-04-01T01:00:00.000Z', 'NEUTRAL'),
        sideInterval('jpy-b', '2025-04-01T01:00:00.000Z', '2025-04-01T03:00:00.000Z', 'ADVERSE', false, true),
      ],
    ))

    expect(result.intervals.map((item) => [item.startUtc, item.endUtc])).toEqual([
      ['2025-04-01T00:00:00.000Z', '2025-04-01T01:00:00.000Z'],
      ['2025-04-01T01:00:00.000Z', '2025-04-01T02:00:00.000Z'],
      ['2025-04-01T02:00:00.000Z', '2025-04-01T03:00:00.000Z'],
    ])
    expect(result.intervals[0]).toMatchObject({ baseBalance: 1, quoteBalance: 0, pairDisplay: 0.5, state: 'SUPPORTIVE' })
    expect(result.intervals[1]).toMatchObject({ baseBalance: 1, quoteBalance: -1, pairDisplay: 1, state: 'SUPPORTIVE' })
    expect(result.intervals[2]).toMatchObject({ state: 'UNKNOWN_SIDE_EVIDENCE', pairDisplay: null, coverage: 'UNKNOWN' })
  })

  it('preserves mixed activity and conflict even when its balance is zero', () => {
    const result = compileFxPairRelativeCategoricalField(range(
      [sideInterval('usd-mixed', '2025-04-01T00:00:00.000Z', '2025-04-01T03:00:00.000Z', 'MIXED', true, true)],
      [sideInterval('jpy-neutral', '2025-04-01T00:00:00.000Z', '2025-04-01T03:00:00.000Z', 'NEUTRAL')],
    ))
    expect(result.intervals[0]).toMatchObject({
      state: 'MIXED',
      baseBalance: 0,
      pairDisplay: 0,
      baseGrossActivity: 2,
      conflict: true,
    })
  })

  it('keeps an unknown side as an explicit pair gap rather than zero', () => {
    const result = compileFxPairRelativeCategoricalField(range(
      [sideInterval('usd-unknown', '2025-04-01T00:00:00.000Z', '2025-04-01T03:00:00.000Z', 'UNKNOWN')],
      [sideInterval('jpy-supportive', '2025-04-01T00:00:00.000Z', '2025-04-01T03:00:00.000Z', 'SUPPORTIVE', true)],
    ))
    expect(result.intervals[0]).toMatchObject({
      state: 'UNKNOWN_SIDE_EVIDENCE',
      pairDisplay: null,
      coverage: 'UNKNOWN',
      unknownReason: 'POLARITY_CATALOGUE_MISSING',
    })
  })

  it('declares the result non-classical, score-free, and execution-locked', () => {
    const result = compileFxPairRelativeCategoricalField(range([], []))
    expect(result.contract).toBe('FX_PAIR_RELATIVE_CATEGORICAL_FIELD_V1')
    expect(result.magnitudeState).toBe('MAGNITUDE_NOT_CONFIGURED')
    expect(result.guardrails).toMatchObject({
      classicalDoctrine: false,
      sbcConfirmation: false,
      curveFitting: false,
      smoothing: false,
      executionAllowed: false,
    })
  })
})
