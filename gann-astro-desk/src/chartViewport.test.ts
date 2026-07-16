import { describe, expect, it } from 'vitest'
import {
  isChartNavigationProximity,
  maximumVisibleBars,
  MIN_CHART_BAR_SPACING,
  navigateChartLogicalRange,
} from './chartViewport'

describe('market chart viewport', () => {
  it('allows a two-year daily range to fit in the main chart', () => {
    expect(MIN_CHART_BAR_SPACING).toBe(0.5)
    expect(maximumVisibleBars(1_100)).toBeGreaterThanOrEqual(627)
  })

  it('rejects invalid chart widths', () => {
    expect(maximumVisibleBars(0)).toBe(0)
    expect(maximumVisibleBars(Number.NaN)).toBe(0)
  })

  it('zooms around the visible center and stays inside available candles', () => {
    const zoomedIn = navigateChartLogicalRange({ from: 100, to: 200 }, 'zoom_in', 500)
    expect(zoomedIn).not.toBeNull()
    expect(zoomedIn!.to - zoomedIn!.from).toBeCloseTo(75)
    expect((zoomedIn!.from + zoomedIn!.to) / 2).toBeCloseTo(150)

    const zoomedOut = navigateChartLogicalRange({ from: -2, to: 504 }, 'zoom_out', 500)
    expect(zoomedOut).toEqual({ from: -2, to: 504 })
  })

  it('moves one quarter viewport backward or forward and clamps at data edges', () => {
    expect(navigateChartLogicalRange({ from: 100, to: 200 }, 'backward', 500))
      .toEqual({ from: 75, to: 175 })
    expect(navigateChartLogicalRange({ from: 100, to: 200 }, 'forward', 500))
      .toEqual({ from: 125, to: 225 })
    expect(navigateChartLogicalRange({ from: -2, to: 98 }, 'backward', 500))
      .toEqual({ from: -2, to: 98 })
    expect(navigateChartLogicalRange({ from: 404, to: 504 }, 'forward', 500))
      .toEqual({ from: 404, to: 504 })
  })

  it('reveals navigation only near the bottom-center chart area', () => {
    expect(isChartNavigationProximity(550, 640, 1_100, 700)).toBe(true)
    expect(isChartNavigationProximity(550, 400, 1_100, 700)).toBe(false)
    expect(isChartNavigationProximity(80, 660, 1_100, 700)).toBe(false)
    expect(isChartNavigationProximity(Number.NaN, 660, 1_100, 700)).toBe(false)
  })
})
