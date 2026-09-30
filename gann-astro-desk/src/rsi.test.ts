import { describe, expect, it } from 'vitest'
import type { Candle } from './types'
import {
  chartBarSeconds,
  closedCandlesAt,
  mergeIndicatorCandles,
  normalizeRsiLevels,
  normalizeRsiPeriod,
  rsiCandlesForVisibleRange,
  rsiWarmupBars,
  visibleRsiPoints,
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

  it('uses bounded hidden history while preserving the visible candle series', () => {
    const history = candles(Array.from({ length: 100 }, (_, index) => index), 86400)
    const visible = candles(Array.from({ length: 12 }, (_, index) => 200 + index), 86400)
      .map((candle) => ({ ...candle, time: candle.time + 100 * 86400 }))
    const cutoff = new Date((visible.at(-1)!.time + 86400) * 1000).toISOString()
    const input = rsiCandlesForVisibleRange(visible, history, 'D1', cutoff, 14)
    const points = visibleRsiPoints(visible, history, 'D1', cutoff, 14)
    expect(input).toHaveLength(112)
    expect(points.length).toBeGreaterThan(0)
    expect(points.every((point) => point.time >= visible[0].time && point.time <= visible.at(-1)!.time)).toBe(true)
    expect(visible).toHaveLength(12)
  })

  it('deduplicates the visible boundary and ignores invalid OHLC history', () => {
    const visible = candles([200, 201, 202], 86400)
    const history = [
      ...candles([100, 101, 102], 86400),
      { ...visible[0], close: Number.NaN },
      { ...visible[0], close: visible[0].close + 10 },
      { ...visible[1], high: Number.POSITIVE_INFINITY },
    ]
    const merged = mergeIndicatorCandles(history, visible)
    expect(merged).toHaveLength(3)
    expect(merged.find((candle) => candle.time === visible[0].time)?.close).toBe(200)
  })

  it('keeps the warm-up policy based on closed-bar count, not calendar days', () => {
    expect(rsiWarmupBars(14)).toBe(100)
    expect(rsiWarmupBars(200)).toBe(1000)
  })

  it.each([
    ['H1', 3600],
    ['H4', 14400],
    ['D1', 86400],
    ['W1', 604800],
  ])('warms up visible RSI points across %s history', (timeframe, stepSeconds) => {
    const history = candles(Array.from({ length: 100 }, (_, index) => 100 + index), stepSeconds)
    const visible = candles(Array.from({ length: 12 }, (_, index) => 220 + index), stepSeconds)
      .map((candle) => ({ ...candle, time: candle.time + 100 * stepSeconds }))
    const cutoff = new Date((visible.at(-1)!.time + stepSeconds) * 1000).toISOString()

    expect(visibleRsiPoints(visible, history, timeframe, cutoff, 14)).not.toHaveLength(0)
  })

  it('keeps weekend and session gaps from changing the visible range contract', () => {
    const base = 1_700_000_000
    const withWeekendGaps = (offset: number, count: number): Candle[] => Array.from({ length: count }, (_, index) => {
      const businessDays = index + Math.floor(index / 5) * 2
      const close = offset + index
      return {
        time: base + businessDays * 86400,
        open: close,
        high: close,
        low: close,
        close,
        volume: 1,
      }
    })
    const history = withWeekendGaps(100, 100)
    const visible = withWeekendGaps(220, 12).map((candle) => ({
      ...candle,
      time: candle.time + 100 * 86400,
    }))
    const cutoff = new Date((visible.at(-1)!.time + 86400) * 1000).toISOString()
    const points = visibleRsiPoints(visible, history, 'D1', cutoff, 14)

    expect(points).not.toHaveLength(0)
    expect(points.every((point) => point.time >= visible[0].time)).toBe(true)
    expect(visible).toHaveLength(12)
  })

  it('does not use candles after a replay cutoff', () => {
    const history = candles(Array.from({ length: 100 }, (_, index) => index), 86400)
    const visible = candles(Array.from({ length: 12 }, (_, index) => 200 + index), 86400)
      .map((candle) => ({ ...candle, time: candle.time + 100 * 86400 }))
    const cutoff = new Date((visible[5].time + 86400) * 1000).toISOString()
    const futureChanged = visible.map((candle, index) => index > 5 ? { ...candle, close: 10000 + index } : candle)
    expect(visibleRsiPoints(visible, history, 'D1', cutoff, 14)).toEqual(
      visibleRsiPoints(futureChanged, history, 'D1', cutoff, 14),
    )
  })

  it('ignores a changing open candle', () => {
    const history = candles(Array.from({ length: 100 }, (_, index) => index), 3600)
    const visible = candles(Array.from({ length: 12 }, (_, index) => 200 + index), 3600)
      .map((candle) => ({ ...candle, time: candle.time + 100 * 3600 }))
    const cutoff = new Date((visible.at(-1)!.time + 1800) * 1000).toISOString()
    const openChanged = { ...visible.at(-1)!, close: 10000 }
    expect(visibleRsiPoints(visible, history, 'H1', cutoff, 14)).toEqual(
      visibleRsiPoints([...visible.slice(0, -1), openChanged], history, 'H1', cutoff, 14),
    )
  })
})
