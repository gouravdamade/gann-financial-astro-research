import { describe, expect, it } from 'vitest'
import { maximumVisibleBars, MIN_CHART_BAR_SPACING } from './chartViewport'

describe('market chart viewport', () => {
  it('allows a two-year daily range to fit in the main chart', () => {
    expect(MIN_CHART_BAR_SPACING).toBe(0.5)
    expect(maximumVisibleBars(1_100)).toBeGreaterThanOrEqual(627)
  })

  it('rejects invalid chart widths', () => {
    expect(maximumVisibleBars(0)).toBe(0)
    expect(maximumVisibleBars(Number.NaN)).toBe(0)
  })
})
