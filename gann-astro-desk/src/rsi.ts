import type { Candle, RsiPoint } from './types'

export const DEFAULT_RSI_PERIOD = 14
export const DEFAULT_RSI_LEVELS = [30, 50, 70] as const
export const DEFAULT_RSI_WARMUP_BARS = 100

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

export function rsiWarmupBars(requestedPeriod = DEFAULT_RSI_PERIOD): number {
  const period = normalizeRsiPeriod(requestedPeriod)
  return Math.max(DEFAULT_RSI_WARMUP_BARS, period * 5)
}

function validCandle(candle: Candle): boolean {
  return Number.isFinite(candle.time)
    && Number.isFinite(candle.open)
    && Number.isFinite(candle.high)
    && Number.isFinite(candle.low)
    && Number.isFinite(candle.close)
}

export function mergeIndicatorCandles(history: Candle[], visibleCandles: Candle[]): Candle[] {
  const byTime = new Map<number, Candle>()
  for (const candle of [...history, ...visibleCandles]) {
    if (!validCandle(candle)) continue
    byTime.set(candle.time, candle)
  }
  return [...byTime.values()].sort((left, right) => left.time - right.time)
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

export function rsiCandlesForVisibleRange(
  visibleCandles: Candle[],
  history: Candle[],
  timeframe: string,
  cutoffUtc: string,
  requestedPeriod = DEFAULT_RSI_PERIOD,
): Candle[] {
  const merged = mergeIndicatorCandles(history, visibleCandles)
  const visibleStart = visibleCandles[0]?.time
  if (!Number.isFinite(visibleStart)) return []
  const closed = closedCandlesAt(merged, timeframe, cutoffUtc)
  const warmup = closed
    .filter((candle) => candle.time < visibleStart)
    .slice(-rsiWarmupBars(requestedPeriod))
  const visible = closed.filter((candle) => candle.time >= visibleStart)
  return [...warmup, ...visible]
}

export function visibleRsiPoints(
  visibleCandles: Candle[],
  history: Candle[],
  timeframe: string,
  cutoffUtc: string,
  requestedPeriod = DEFAULT_RSI_PERIOD,
): RsiPoint[] {
  const input = rsiCandlesForVisibleRange(
    visibleCandles,
    history,
    timeframe,
    cutoffUtc,
    requestedPeriod,
  )
  const points = wilderRsiPoints(input, requestedPeriod)
  const visibleStart = visibleCandles[0]?.time
  const visibleEnd = visibleCandles.at(-1)?.time
  if (
    typeof visibleStart !== 'number'
    || !Number.isFinite(visibleStart)
    || typeof visibleEnd !== 'number'
    || !Number.isFinite(visibleEnd)
  ) return []
  return points.filter((point) => point.time >= visibleStart && point.time <= visibleEnd)
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
