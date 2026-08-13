import type { ChartPayload } from './types'

export const FIELDS_RESEARCH_WINDOW_DAYS = 14
export const FIELDS_RESEARCH_WINDOW_MS = FIELDS_RESEARCH_WINDOW_DAYS * 24 * 60 * 60 * 1000

export type FieldsResearchWindow = {
  datasetStartUtc: string
  datasetEndUtc: string
  pageIndex: number
  pageCount: number
  rangeStartUtc: string
  rangeEndUtc: string
  isFinalPage: boolean
}

export function chartDatasetExtent(chart: ChartPayload): { startMs: number; endMs: number } | null {
  if (chart.candles.length < 2) return null
  const startMs = chart.candles[0].time * 1000
  const endMs = chart.candles.at(-1)!.time * 1000
  if (!Number.isFinite(startMs) || !Number.isFinite(endMs) || endMs <= startMs) return null
  return { startMs, endMs }
}

export function fieldsResearchWindowFor(chart: ChartPayload, requestedPageIndex: number): FieldsResearchWindow | null {
  const extent = chartDatasetExtent(chart)
  if (!extent) return null
  const pageCount = Math.ceil((extent.endMs - extent.startMs) / FIELDS_RESEARCH_WINDOW_MS)
  const pageIndex = Math.min(Math.max(0, requestedPageIndex), Math.max(0, pageCount - 1))
  const pageStartMs = extent.startMs + (pageIndex * FIELDS_RESEARCH_WINDOW_MS)
  const pageEndMs = Math.min(pageStartMs + FIELDS_RESEARCH_WINDOW_MS, extent.endMs)
  return {
    datasetStartUtc: new Date(extent.startMs).toISOString(),
    datasetEndUtc: new Date(extent.endMs).toISOString(),
    pageIndex,
    pageCount,
    rangeStartUtc: new Date(pageStartMs).toISOString(),
    rangeEndUtc: new Date(pageEndMs).toISOString(),
    isFinalPage: pageIndex === pageCount - 1,
  }
}

export function researchWindowPageForTimestamp(chart: ChartPayload, timestampUtc: string | null): number | null {
  const extent = chartDatasetExtent(chart)
  const atMs = timestampUtc ? Date.parse(timestampUtc) : Number.NaN
  if (!extent || !Number.isFinite(atMs) || atMs < extent.startMs || atMs >= extent.endMs) return null
  return Math.floor((atMs - extent.startMs) / FIELDS_RESEARCH_WINDOW_MS)
}

export function isTimestampInsideResearchWindow(window: FieldsResearchWindow | null, timestampUtc: string | null): boolean {
  if (!window || !timestampUtc) return false
  const atMs = Date.parse(timestampUtc)
  return Number.isFinite(atMs)
    && atMs >= Date.parse(window.rangeStartUtc)
    && atMs < Date.parse(window.rangeEndUtc)
}
