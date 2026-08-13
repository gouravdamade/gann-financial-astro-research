import { describe, expect, it } from 'vitest'
import type { ChartPayload } from './types'
import {
  FIELDS_RESEARCH_WINDOW_MS,
  fieldsResearchWindowFor,
  isTimestampInsideResearchWindow,
  researchWindowPageForTimestamp,
} from './fieldsResearchWindow'

const start = Date.parse('2026-08-01T00:00:00Z')
const end = start + (31 * 24 * 60 * 60 * 1000)
const chart = {
  symbol: 'USDJPY',
  timeframe: 'D1',
  candles: [
    { time: start / 1000 },
    { time: end / 1000 },
  ],
} as ChartPayload

describe('Fields research window', () => {
  it('anchors deterministic half-open 14-day pages to the loaded chart start', () => {
    const first = fieldsResearchWindowFor(chart, 0)
    const second = fieldsResearchWindowFor(chart, 1)
    const final = fieldsResearchWindowFor(chart, 2)

    expect(first).toMatchObject({ pageIndex: 0, pageCount: 3, rangeStartUtc: new Date(start).toISOString(), rangeEndUtc: new Date(start + FIELDS_RESEARCH_WINDOW_MS).toISOString() })
    expect(second).toMatchObject({ pageIndex: 1, rangeStartUtc: first?.rangeEndUtc, rangeEndUtc: new Date(start + (2 * FIELDS_RESEARCH_WINDOW_MS)).toISOString() })
    expect(final).toMatchObject({ pageIndex: 2, isFinalPage: true, rangeStartUtc: second?.rangeEndUtc, rangeEndUtc: new Date(end).toISOString() })
  })

  it('maps a crosshair to its stable page without moving the page itself', () => {
    const first = fieldsResearchWindowFor(chart, 0)
    const outside = new Date(start + FIELDS_RESEARCH_WINDOW_MS + 1).toISOString()

    expect(researchWindowPageForTimestamp(chart, outside)).toBe(1)
    expect(isTimestampInsideResearchWindow(first, outside)).toBe(false)
    expect(researchWindowPageForTimestamp(chart, new Date(end).toISOString())).toBeNull()
  })
})
