import { describe, expect, it } from 'vitest'
import { canAddActivityToChart, isActivityChartSupported } from './activityChartEligibility'

describe('activity chart eligibility', () => {
  it('supports only the exact USDJPY chart contract', () => {
    expect(isActivityChartSupported('USDJPY')).toBe(true)
    expect(isActivityChartSupported('AAPL')).toBe(false)
    expect(isActivityChartSupported('EURJPY')).toBe(false)
  })

  it('keeps the parent operation closed for unsupported symbols and dirty Fields review', () => {
    expect(canAddActivityToChart('AAPL', false, 'fields')).toBe(false)
    expect(canAddActivityToChart('USDJPY', true, 'fields')).toBe(false)
    expect(canAddActivityToChart('USDJPY', true, 'chart')).toBe(true)
    expect(canAddActivityToChart('USDJPY', false, 'fields')).toBe(true)
  })
})
