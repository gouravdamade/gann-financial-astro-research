import { describe, expect, it } from 'vitest'
import type { Candle } from './types'
import {
  chartBarSeconds,
  closedCandlesAt,
  normalizeRsiLevels,
  normalizeRsiPeriod,
  wilderRsiPoints,
} from './rsi'

function candles(closes: number[], stepSeconds = 3600): Candle[] {
  return closes.map((close, index) => ({
    time: 1_700_000_000 + index * stepSeconds,
    open: close,
    high: close,
    low: close,
    close,
    volume: 1,
  }))
}

describe('Wilder RSI', () => {
  it('returns the expected boundaries for rising, falling, and flat closes', () => {
    expect(wilderRsiPoints(candles(Array.from({ length: 20 }, (_, index) => index)), 14).at(-1)?.value).toBe(100)
    expect(wilderRsiPoints(candles(Array.from({ length: 20 }, (_, index) => 20 - index)), 14).at(-1)?.value).toBe(0)
    expect(wilderRsiPoints(candles(Array.from({ length: 20 }, () => 10)), 14).at(-1)?.value).toBe(50)
  })

  it('requires period plus one closes', () => {
    expect(wilderRsiPoints(candles(Array.from({ length: 14 }, (_, index) => index)), 14)).toEqual([])
    expect(wilderRsiPoints(candles(Array.from({ length: 15 }, (_, index) => index)), 14)).toHaveLength(1)
  })

  it('clamps settings and validates levels', () => {
    expect(normalizeRsiPeriod(1)).toBe(2)
    expect(normalizeRsiPeriod(999)).toBe(200)
    expect(normalizeRsiLevels([70, 50, -1, 30, 70, 101])).toEqual([30, 50, 70])
  })

  it('excludes the unclosed candle at a timestamp cutoff', () => {
    const source = candles([1, 2, 3, 4])
    const cutoff = new Date((source[2].time + 1800) * 1000).toISOString()
    expect(chartBarSeconds(source, 'H1')).toBe(3600)
    expect(closedCandlesAt(source, 'H1', cutoff)).toHaveLength(2)
  })
})
