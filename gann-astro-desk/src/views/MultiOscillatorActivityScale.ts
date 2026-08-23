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
