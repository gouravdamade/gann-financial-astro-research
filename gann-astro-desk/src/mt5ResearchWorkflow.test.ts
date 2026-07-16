import { describe, expect, it } from 'vitest'
import {
  boundRequestedRangeToSource,
  chartTimeframeForSource,
  mt5SourceTimeframeForChart,
} from './mt5ResearchWorkflow'

describe('MT5 research workflow', () => {
  it('uses H1 source bars for overview chart timeframes', () => {
    expect(mt5SourceTimeframeForChart('H1')).toBe('H1')
    expect(mt5SourceTimeframeForChart('H4')).toBe('H1')
    expect(mt5SourceTimeframeForChart('D1')).toBe('H1')
    expect(mt5SourceTimeframeForChart('M30')).toBe('M30')
  })

  it('preserves H4 and D1 views backed by H1 archives', () => {
    expect(chartTimeframeForSource('D1', 'H1')).toBe('D1')
    expect(chartTimeframeForSource('H4', 'H1')).toBe('H4')
    expect(chartTimeframeForSource('D1', 'M30')).toBe('M30')
  })

  it('reports and bounds partial broker history instead of silently claiming full coverage', () => {
    const range = boundRequestedRangeToSource(
      '2022-01-01T00:00:00+05:30',
      '2026-01-10T00:00:00+05:30',
      {
        dateStart: '2023-01-01T00:00:00Z',
        dateEnd: '2025-12-31T23:00:00Z',
      },
    )
    expect(range.start).toBe('2023-01-01T00:00:00.000Z')
    expect(range.end).toBe('2025-12-31T23:00:00.000Z')
    expect(range.startCovered).toBe(false)
    expect(range.endCovered).toBe(false)
  })

  it('does not call an ordinary weekend edge a missing-history failure', () => {
    const range = boundRequestedRangeToSource(
      '2026-01-03T00:00:00Z',
      '2026-01-06T00:00:00Z',
      {
        dateStart: '2026-01-05T00:00:00Z',
        dateEnd: '2026-01-05T23:00:00Z',
      },
    )
    expect(range.startCovered).toBe(true)
    expect(range.endCovered).toBe(true)
  })
})
