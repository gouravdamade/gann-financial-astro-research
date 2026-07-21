import { describe, expect, it } from 'vitest'
import {
  defaultPlanetaryLineOverlaySettings,
  normalizePlanetaryLineSettings,
  parsePlanetaryLineValues,
  planetaryLineCount,
  sampledVisibleCandleTimes,
} from './planetaryLines'
import type { Candle } from './types'

describe('planetary line laboratory settings', () => {
  it('seeds every planet independently and keeps the overlay research-off by default', () => {
    const settings = defaultPlanetaryLineOverlaySettings({
      nValues: [30, 60],
      harmonics: [1.6, 1.8],
      degrees: [360, 180],
    })
    expect(settings.visible).toBe(false)
    expect(settings.groups).toHaveLength(13)
    expect(settings.groups.find((group) => group.planet === 'AVG(ALL)')?.enabled).toBe(true)
    expect(settings.groups.find((group) => group.planet === 'MARS')?.nValues).toEqual([30, 60])
    expect(planetaryLineCount(settings)).toBe(8)
  })

  it('counts direct and mirror combinations before sending them to the backend', () => {
    const settings = defaultPlanetaryLineOverlaySettings()
    const avg = settings.groups.find((group) => group.planet === 'AVG(ALL)')!
    avg.mode = 'both'
    avg.nValues = [1, 2, 3]
    avg.fValues = [0.5, 1]
    avg.degrees = [180, 360]
    expect(planetaryLineCount(settings)).toBe(24)
  })

  it('parses comma, semicolon, and space separated values without duplicates', () => {
    expect(parsePlanetaryLineValues('30, 60; 90 60', 'nValues', 1, 150)).toEqual([30, 60, 90])
    expect(() => parsePlanetaryLineValues('0, 10', 'nValues', 1, 150)).toThrow('between 1 and 150')
  })

  it('normalizes imported settings and restores missing planet rows', () => {
    const defaults = defaultPlanetaryLineOverlaySettings()
    const normalized = normalizePlanetaryLineSettings({
      ...defaults,
      groups: [{
        ...defaults.groups[0],
        planet: 'SUN',
        enabled: true,
        mode: 'mirror',
      }],
    })
    expect(normalized.groups).toHaveLength(13)
    expect(normalized.groups[0].mode).toBe('mirror')
    expect(normalized.groups.find((group) => group.planet === 'AVG(ALL)')?.enabled).toBe(true)
  })
})

describe('visible timestamp sampling', () => {
  const candles: Candle[] = Array.from({ length: 1_500 }, (_, index) => ({
    time: 1_700_000_000 + index * 3_600,
    open: 100,
    high: 101,
    low: 99,
    close: 100,
    volume: 1,
  }))

  it('caps samples while preserving first and last visible times', () => {
    const values = sampledVisibleCandleTimes(candles, undefined, undefined, 300)
    expect(values).toHaveLength(300)
    expect(values[0]).toBe(candles[0].time)
    expect(values.at(-1)).toBe(candles.at(-1)?.time)
  })

  it('calculates only around the visible chart range', () => {
    const start = new Date(candles[500].time * 1_000).toISOString()
    const end = new Date(candles[600].time * 1_000).toISOString()
    const values = sampledVisibleCandleTimes(candles, start, end, 300)
    expect(values.length).toBeGreaterThan(100)
    expect(values[0]).toBeLessThan(candles[500].time)
    expect(values.at(-1)).toBeGreaterThan(candles[600].time)
  })
})
