import type {
  MultiOscillatorActivityInterval,
  MultiOscillatorActivityEvent,
  MultiOscillatorActivityRange,
  MultiOscillatorActivityRangeRequest,
  MultiOscillatorActivitySide,
} from './types'

export const ACTIVITY_CHUNK_SECONDS = 14 * 24 * 60 * 60
export const ACTIVITY_CACHE_CAPACITY = 12

export type ActivityChunk = {
  startSeconds: number
  endSeconds: number
  rangeStartUtc: string
  rangeEndUtc: string
  key: string
}

export type ActivityVisibleRange = { from: number; to: number }

export type ActivityStepPoint = { time: number; value: number }
export type ActivityMarkerGroup = {
  markerId: string
  side: 'USD' | 'JPY'
  time: number
  events: MultiOscillatorActivityEvent[]
}

export function activityChunkAt(seconds: number): ActivityChunk {
  if (!Number.isFinite(seconds)) throw new Error('Activity chunk time must be finite')
  const startSeconds = Math.floor(seconds / ACTIVITY_CHUNK_SECONDS) * ACTIVITY_CHUNK_SECONDS
  const endSeconds = startSeconds + ACTIVITY_CHUNK_SECONDS
  const rangeStartUtc = new Date(startSeconds * 1000).toISOString()
  const rangeEndUtc = new Date(endSeconds * 1000).toISOString()
  return {
    startSeconds,
    endSeconds,
    rangeStartUtc,
    rangeEndUtc,
    key: `USDJPY|USD+JPY|ASPECT_STRENGTH_V0|${rangeStartUtc}`,
  }
}

export function activityChunkForVisibleRange(range: ActivityVisibleRange): ActivityChunk {
  if (!Number.isFinite(range.from) || !Number.isFinite(range.to) || range.to <= range.from) {
    throw new Error('Activity visible range must be a non-empty UTC interval')
  }
  return activityChunkAt(range.from + (range.to - range.from) / 2)
}

export function activityChunksForVisibleRange(range: ActivityVisibleRange): ActivityChunk[] {
  if (!Number.isFinite(range.from) || !Number.isFinite(range.to) || range.to <= range.from) {
    throw new Error('Activity visible range must be a non-empty UTC interval')
  }
  const first = activityChunkAt(range.from)
  const last = activityChunkAt(range.to - 0.001)
  const chunkCount = Math.floor((last.startSeconds - first.startSeconds) / ACTIVITY_CHUNK_SECONDS) + 1
  const boundedCount = Math.min(chunkCount, ACTIVITY_CACHE_CAPACITY)
  const center = activityChunkForVisibleRange(range)
  const centeredStart = center.startSeconds - Math.floor((boundedCount - 1) / 2) * ACTIVITY_CHUNK_SECONDS
  const minStart = first.startSeconds
  const maxStart = last.startSeconds - (boundedCount - 1) * ACTIVITY_CHUNK_SECONDS
  const start = Math.max(minStart, Math.min(centeredStart, maxStart))
  return Array.from({ length: boundedCount }, (_, index) => activityChunkAt(start + index * ACTIVITY_CHUNK_SECONDS))
}

export function adjacentActivityChunk(chunk: ActivityChunk, direction: -1 | 1): ActivityChunk {
  return activityChunkAt(chunk.startSeconds + direction * ACTIVITY_CHUNK_SECONDS)
}

export function activityIntervalAt(
  intervals: readonly MultiOscillatorActivityInterval[],
  seconds: number,
): MultiOscillatorActivityInterval | null {
  let low = 0
  let high = intervals.length - 1
  while (low <= high) {
    const middle = Math.floor((low + high) / 2)
    const interval = intervals[middle]
    const start = Date.parse(interval.startUtc) / 1000
    const end = Date.parse(interval.endUtc) / 1000
    if (seconds < start) high = middle - 1
    else if (seconds >= end) low = middle + 1
    else return interval
  }
  return null
}

export function activityCoverageLabel(
  interval: MultiOscillatorActivityInterval | null,
): string {
  if (!interval) return 'No loaded activity interval'
  if (interval.coverage === 'KNOWN') {
    return interval.rawActiveEventCount === 0
      ? '0 observed | coverage known'
      : `${interval.rawActiveEventCount} observed | coverage known`
  }
  return interval.rawActiveEventCount === 0
    ? 'Coverage incomplete | no confirmed events'
    : `${interval.rawActiveEventCount} observed | coverage incomplete`
}

export function activityStepPoints(
  intervals: readonly MultiOscillatorActivityInterval[],
  visibleRange: ActivityVisibleRange,
): ActivityStepPoint[] {
  const start = visibleRange.from
  const end = visibleRange.to
  const ordered = [...intervals].sort((left, right) => left.startUtc.localeCompare(right.startUtc))
  const points: ActivityStepPoint[] = []
  const first = activityIntervalAt(ordered, start)
  if (first) points.push({ time: start, value: first.rawActiveEventCount })
  for (const interval of ordered) {
    const intervalStart = Date.parse(interval.startUtc) / 1000
    if (intervalStart <= start || intervalStart >= end) continue
    points.push({ time: intervalStart, value: interval.rawActiveEventCount })
  }
  return points
}

export function unknownActivityCoverageRanges(
  range: MultiOscillatorActivityRange | null,
): ActivityVisibleRange[] {
  if (!range) return []
  const intervals = [
    ...range.fields.USD.activityIntervals,
    ...range.fields.JPY.activityIntervals,
  ].filter((interval) => interval.coverage === 'UNKNOWN')
    .map((interval) => ({
      from: Date.parse(interval.startUtc) / 1000,
      to: Date.parse(interval.endUtc) / 1000,
    }))
    .filter((interval) => Number.isFinite(interval.from) && Number.isFinite(interval.to) && interval.to > interval.from)
    .sort((left, right) => left.from - right.from)
  const merged: ActivityVisibleRange[] = []
  for (const interval of intervals) {
    const previous = merged[merged.length - 1]
    if (previous && interval.from <= previous.to) previous.to = Math.max(previous.to, interval.to)
    else merged.push({ ...interval })
  }
  return merged
}

export function groupActivityEventsForMarkers(
  fields: Record<'USD' | 'JPY', MultiOscillatorActivitySide>,
  dataRange: ActivityVisibleRange,
  visibleRange: ActivityVisibleRange,
  limit = 500,
): ActivityMarkerGroup[] {
  const groups = new Map<string, ActivityMarkerGroup>()
  for (const side of ['USD', 'JPY'] as const) {
    for (const event of fields[side].events) {
      const exact = Date.parse(event.exactUtc) / 1000
      if (!Number.isFinite(exact) || exact < dataRange.from || exact >= dataRange.to) continue
      const time = Math.floor(exact)
      const markerId = `activity-${side}-${time}`
      const group = groups.get(markerId) ?? { markerId, side, time, events: [] }
      group.events.push(event)
      groups.set(markerId, group)
    }
  }
  const visible = [...groups.values()]
    .filter((group) => group.time >= visibleRange.from && group.time <= visibleRange.to)
    .sort((left, right) => left.time - right.time)
  if (visible.length <= limit) return visible
  const center = visibleRange.from + (visibleRange.to - visibleRange.from) / 2
  return visible
    .sort((left, right) => Math.abs(left.time - center) - Math.abs(right.time - center))
    .slice(0, Math.max(0, limit))
    .sort((left, right) => left.time - right.time)
}

export function mergeActivityRanges(
  ranges: readonly MultiOscillatorActivityRange[],
): MultiOscillatorActivityRange | null {
  if (!ranges.length) return null
  const ordered = [...ranges].sort((left, right) => left.rangeStartUtc.localeCompare(right.rangeStartUtc))
  const latest = ordered[ordered.length - 1]
  const mergeSide = (side: 'USD' | 'JPY'): MultiOscillatorActivityRange['fields'][typeof side] => {
    const sideRanges = ordered.map((range) => range.fields[side])
    const eventMap = new Map<string, (typeof sideRanges)[number]['events'][number]>()
    const intervalMap = new Map<string, MultiOscillatorActivityInterval>()
    for (const field of sideRanges) {
      for (const event of field.events) eventMap.set(event.eventId, event)
      for (const interval of field.activityIntervals) {
        intervalMap.set(`${interval.intervalId}|${interval.startUtc}|${interval.endUtc}`, interval)
      }
    }
    const events = [...eventMap.values()].sort((left, right) => left.exactUtc.localeCompare(right.exactUtc))
    const activityIntervals = [...intervalMap.values()].sort((left, right) => left.startUtc.localeCompare(right.startUtc))
    const coverage = sideRanges.some((field) => field.coverage === 'UNKNOWN')
      || activityIntervals.some((interval) => interval.coverage === 'UNKNOWN')
      ? 'UNKNOWN' as const
      : 'KNOWN' as const
    const reasons = [...new Set(sideRanges.map((field) => field.unknownReason).filter((value): value is string => Boolean(value)))]
    return {
      ...sideRanges[sideRanges.length - 1],
      rangeStartUtc: ordered[0].rangeStartUtc,
      rangeEndUtc: ordered[ordered.length - 1].rangeEndUtc,
      events,
      activityIntervals,
      sourceEventCount: events.length,
      eligibleEventCount: events.length,
      coverage,
      unknownReason: reasons.length ? reasons.join('; ') : null,
    }
  }
  return {
    ...latest,
    rangeStartUtc: ordered[0].rangeStartUtc,
    rangeEndUtc: ordered[ordered.length - 1].rangeEndUtc,
    fields: { USD: mergeSide('USD'), JPY: mergeSide('JPY') },
  }
}

export class ActivityChunkCache {
  private readonly cache = new Map<string, MultiOscillatorActivityRange>()
  private readonly inFlight = new Map<string, Promise<MultiOscillatorActivityRange>>()
  private readonly fetchRange: (request: MultiOscillatorActivityRangeRequest) => Promise<MultiOscillatorActivityRange>
  private readonly capacity: number

  constructor(
    fetchRange: (request: MultiOscillatorActivityRangeRequest) => Promise<MultiOscillatorActivityRange>,
    capacity = ACTIVITY_CACHE_CAPACITY,
  ) {
    this.fetchRange = fetchRange
    this.capacity = capacity
  }

  has(chunk: ActivityChunk): boolean {
    return this.cache.has(chunk.key)
  }

  get(chunk: ActivityChunk): MultiOscillatorActivityRange | null {
    const value = this.cache.get(chunk.key)
    if (!value) return null
    this.cache.delete(chunk.key)
    this.cache.set(chunk.key, value)
    return value
  }

  getMerged(): MultiOscillatorActivityRange | null {
    return mergeActivityRanges([...this.cache.values()])
  }

  request(chunk: ActivityChunk): Promise<MultiOscillatorActivityRange> {
    const cached = this.get(chunk)
    if (cached) return Promise.resolve(cached)
    const pending = this.inFlight.get(chunk.key)
    if (pending) return pending
    const request: MultiOscillatorActivityRangeRequest = {
      rangeStartUtc: chunk.rangeStartUtc,
      rangeEndUtc: chunk.rangeEndUtc,
      sideIdentities: ['USD', 'JPY'],
      aspectProfileId: 'ASPECT_STRENGTH_V0',
    }
    const next = this.fetchRange(request).then((range) => {
      this.cache.delete(chunk.key)
      this.cache.set(chunk.key, range)
      while (this.cache.size > this.capacity) {
        const oldest = this.cache.keys().next().value
        if (oldest == null) break
        this.cache.delete(oldest)
      }
      return range
    }).finally(() => {
      this.inFlight.delete(chunk.key)
    })
    this.inFlight.set(chunk.key, next)
    return next
  }
}
