import { describe, expect, it } from 'vitest'
import {
  automaticAspectMinDurationMinutes,
  effectiveAspectMinDurationMinutes,
  formatAspectDuration,
} from './aspectTimeframePolicy'

describe('timeframe-aware aspect visibility', () => {
  it('requires at least one selected-timeframe candle in auto mode', () => {
    expect(automaticAspectMinDurationMinutes('M30')).toBe(30)
    expect(automaticAspectMinDurationMinutes('H1')).toBe(60)
    expect(automaticAspectMinDurationMinutes('H4')).toBe(240)
    expect(automaticAspectMinDurationMinutes('D1')).toBe(1_440)
    expect(automaticAspectMinDurationMinutes('W1')).toBe(10_080)
  })

  it('keeps a deliberate manual threshold across timeframe switches', () => {
    expect(effectiveAspectMinDurationMinutes({
      timeframe: 'W1',
      aspectDurationMode: 'manual',
      minDurationMinutes: 30_240,
    })).toBe(30_240)
  })

  it('formats the applied policy compactly', () => {
    expect(formatAspectDuration(30)).toBe('30m')
    expect(formatAspectDuration(240)).toBe('4h')
    expect(formatAspectDuration(1_440)).toBe('1d')
    expect(formatAspectDuration(30_240)).toBe('3w')
  })
})
