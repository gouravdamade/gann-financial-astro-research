import { describe, expect, it } from 'vitest'
import { replayCutoffForCandle } from './barReplay'

describe('timestamp-safe Bar Replay clock', () => {
  it('reveals an H1 candle only at its close', () => {
    const open = Date.parse('2026-07-13T10:00:00Z') / 1000
    expect(replayCutoffForCandle(open, 'H1')).toBe('2026-07-13T11:00:00.000Z')
  })

  it('uses the full weekly close interval', () => {
    const open = Date.parse('2026-07-13T00:00:00Z') / 1000
    expect(replayCutoffForCandle(open, 'W1')).toBe('2026-07-20T00:00:00.000Z')
  })
})
