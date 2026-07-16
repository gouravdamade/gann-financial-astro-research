import type { ChartParameters, PriceSource } from './types'

export type ResearchSourceTimeframe = 'M30' | 'H1'

export type BoundedResearchRange = {
  start: string
  end: string
  startCovered: boolean
  endCovered: boolean
}

export function mt5SourceTimeframeForChart(
  timeframe: ChartParameters['timeframe'],
): ResearchSourceTimeframe {
  return timeframe === 'M30' ? 'M30' : 'H1'
}

export function chartTimeframeForSource(
  preferred: ChartParameters['timeframe'],
  sourceTimeframe: string,
): ChartParameters['timeframe'] {
  if (sourceTimeframe === 'M30') return 'M30'
  if (sourceTimeframe === 'H1' && preferred !== 'M30') return preferred
  return 'H1'
}

function parsedTime(value: string, label: string): number {
  const parsed = Date.parse(value)
  if (!Number.isFinite(parsed)) throw new Error(`${label} is not a valid timestamp`)
  return parsed
}

export function boundRequestedRangeToSource(
  requestedStart: string,
  requestedEnd: string,
  source: Pick<PriceSource, 'dateStart' | 'dateEnd'>,
): BoundedResearchRange {
  const requestedStartMs = parsedTime(requestedStart, 'Requested start')
  const requestedEndMs = parsedTime(requestedEnd, 'Requested end')
  const sourceStartMs = parsedTime(source.dateStart, 'MT5 source start')
  const sourceEndMs = parsedTime(source.dateEnd, 'MT5 source end')
  if (requestedEndMs <= requestedStartMs) throw new Error('End must be later than start')

  const boundedStart = Math.max(requestedStartMs, sourceStartMs)
  const boundedEnd = Math.min(requestedEndMs, sourceEndMs)
  if (boundedEnd <= boundedStart) {
    throw new Error('MT5 returned no usable closed-bar overlap for the requested range')
  }
  const marketClosureToleranceMs = 72 * 60 * 60 * 1000
  return {
    start: new Date(boundedStart).toISOString(),
    end: new Date(boundedEnd).toISOString(),
    startCovered: sourceStartMs <= requestedStartMs + marketClosureToleranceMs,
    endCovered: sourceEndMs >= requestedEndMs - marketClosureToleranceMs,
  }
}
