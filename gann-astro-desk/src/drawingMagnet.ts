import type { DrawingMagnetMode } from './types'

export type MagnetCandidate = {
  time: number
  price: number
  field: 'open' | 'high' | 'low' | 'close'
  distancePx: number
}

export function chooseMagnetCandidate(
  candidates: MagnetCandidate[],
  mode: DrawingMagnetMode,
  weakThresholdPx = 10,
): MagnetCandidate | null {
  if (mode === 'off' || candidates.length === 0) return null
  const nearest = candidates.reduce((best, candidate) => (
    candidate.distancePx < best.distancePx ? candidate : best
  ))
  if (mode === 'weak' && nearest.distancePx > weakThresholdPx) return null
  return nearest
}
