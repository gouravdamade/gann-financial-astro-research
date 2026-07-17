import type { ChartTimeframe } from './types'

const TIMEFRAME_SECONDS: Record<ChartTimeframe, number> = {
  M30: 30 * 60,
  H1: 60 * 60,
  H4: 4 * 60 * 60,
  D1: 24 * 60 * 60,
  W1: 7 * 24 * 60 * 60,
}

export function replayCutoffForCandle(
  candleOpenTime: number,
  timeframe: string,
): string {
  const duration = TIMEFRAME_SECONDS[timeframe.toUpperCase() as ChartTimeframe]
  if (!duration) throw new Error(`Unsupported Bar Replay timeframe: ${timeframe}`)
  return new Date((candleOpenTime + duration) * 1000).toISOString()
}

export function replayClockLabel(cutoffUtc: string): string {
  return new Date(cutoffUtc).toLocaleString([], {
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}
