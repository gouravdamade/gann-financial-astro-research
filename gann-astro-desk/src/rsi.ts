import type { Candle, RsiPoint } from './types'

export const DEFAULT_RSI_PERIOD = 14
export const DEFAULT_RSI_LEVELS = [30, 50, 70] as const

export function normalizeRsiPeriod(value: number): number {
  if (!Number.isFinite(value)) return DEFAULT_RSI_PERIOD
  return Math.max(2, Math.min(200, Math.round(value)))
}

export function normalizeRsiLevels(values: number[]): number[] {
  const normalized = [...new Set(values
    .filter((value) => Number.isFinite(value) && value >= 0 && value <= 100)
    .map((value) => Number(value.toFixed(3))))]
    .sort((left, right) => left - right)
  return normalized.length ? normalized : [...DEFAULT_RSI_LEVELS]
}

export function chartBarSeconds(candles: Candle[], timeframe: string): number {
  const differences = candles
    .slice(1)
    .map((candle, index) => candle.time - candles[index].time)
    .filter((value) => Number.isFinite(value) && value > 0)
    .sort((left, right) => left - right)
  if (differences.length) return Math.max(60, differences[Math.floor(differences.length / 2)])
  return ({ M30: 1800, H1: 3600, H4: 14400, D1: 86400, W1: 604800 } as Record<string, number>)[timeframe.toUpperCase()] ?? 3600
}

export function closedCandlesAt(
  candles: Candle[],
  timeframe: string,
  cutoffUtc: string,
): Candle[] {
  const cutoffSeconds = new Date(cutoffUtc).getTime() / 1000
  if (!Number.isFinite(cutoffSeconds)) return candles
  const barSeconds = chartBarSeconds(candles, timeframe)
  return candles.filter((candle) => candle.time + barSeconds <= cutoffSeconds)
}

export function wilderRsiPoints(candles: Candle[], requestedPeriod = DEFAULT_RSI_PERIOD): RsiPoint[] {
  const period = normalizeRsiPeriod(requestedPeriod)
  if (candles.length <= period) return []
  const deltas = candles.slice(1).map((candle, index) => candle.close - candles[index].close)
  let averageGain = deltas.slice(0, period).reduce((sum, delta) => sum + Math.max(delta, 0), 0) / period
  let averageLoss = deltas.slice(0, period).reduce((sum, delta) => sum + Math.max(-delta, 0), 0) / period
  const score = (gain: number, loss: number) => {
    if (gain === 0 && loss === 0) return 50
    if (loss === 0) return 100
    if (gain === 0) return 0
    return 100 - (100 / (1 + gain / loss))
  }
  const points: RsiPoint[] = [{
    time: candles[period].time,
    value: score(averageGain, averageLoss),
  }]
  for (let index = period + 1; index < candles.length; index += 1) {
    const delta = deltas[index - 1]
    averageGain = ((averageGain * (period - 1)) + Math.max(delta, 0)) / period
    averageLoss = ((averageLoss * (period - 1)) + Math.max(-delta, 0)) / period
    points.push({ time: candles[index].time, value: score(averageGain, averageLoss) })
  }
  return points
}
