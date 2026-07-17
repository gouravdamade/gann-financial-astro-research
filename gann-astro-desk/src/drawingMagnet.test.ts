import { describe, expect, it } from 'vitest'
import { chooseMagnetCandidate, type MagnetCandidate } from './drawingMagnet'

const candidates: MagnetCandidate[] = [
  { time: 10, price: 147.1, field: 'open', distancePx: 12 },
  { time: 10, price: 147.2, field: 'high', distancePx: 6 },
]

describe('drawing OHLC magnet', () => {
  it('leaves the point alone when magnet mode is off', () => {
    expect(chooseMagnetCandidate(candidates, 'off')).toBeNull()
  })

  it('snaps weak mode only inside the screen-space threshold', () => {
    expect(chooseMagnetCandidate(candidates, 'weak')?.field).toBe('high')
    expect(chooseMagnetCandidate(candidates, 'weak', 5)).toBeNull()
  })

  it('always picks the nearest OHLC value in strong mode', () => {
    expect(chooseMagnetCandidate(candidates, 'strong', 1)?.price).toBe(147.2)
  })
})
