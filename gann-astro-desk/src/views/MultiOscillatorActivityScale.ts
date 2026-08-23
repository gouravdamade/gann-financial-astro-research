import type { MultiOscillatorActivityInterval } from '../types'

export function deriveSharedRawActivityAxisMax(
  intervalsBySide: Record<'USD' | 'JPY', MultiOscillatorActivityInterval[]>,
): number {
  return Math.max(
    0,
    ...(['USD', 'JPY'] as const).flatMap((side) =>
      intervalsBySide[side].map((interval) => interval.rawActiveEventCount),
    ),
  )
}

export function rawActivityHeightPercent(rawCount: number, sharedAxisMax: number): number {
  if (!Number.isFinite(rawCount) || rawCount <= 0) return 0
  if (!Number.isFinite(sharedAxisMax) || sharedAxisMax <= 0) return 0
  return Math.min(100, Math.max(0, (rawCount / sharedAxisMax) * 100))
}
