import type { ChartParameters, ChartTimeframe } from './types'

const TIMEFRAME_BAR_MINUTES: Record<ChartTimeframe, number> = {
  M30: 30,
  H1: 60,
  H4: 240,
  D1: 1_440,
  W1: 10_080,
}

export function automaticAspectMinDurationMinutes(timeframe: ChartTimeframe): number {
  return TIMEFRAME_BAR_MINUTES[timeframe]
}

export function effectiveAspectMinDurationMinutes(
  parameters: Pick<ChartParameters, 'timeframe' | 'aspectDurationMode' | 'minDurationMinutes'>,
): number {
  return parameters.aspectDurationMode === 'manual'
    ? Math.max(0, parameters.minDurationMinutes)
    : automaticAspectMinDurationMinutes(parameters.timeframe)
}

export function formatAspectDuration(minutes: number): string {
  if (!Number.isFinite(minutes) || minutes < 0) return '0m'
  if (minutes >= 10_080 && minutes % 10_080 === 0) return `${minutes / 10_080}w`
  if (minutes >= 1_440 && minutes % 1_440 === 0) return `${minutes / 1_440}d`
  if (minutes >= 60 && minutes % 60 === 0) return `${minutes / 60}h`
  return `${minutes}m`
}
