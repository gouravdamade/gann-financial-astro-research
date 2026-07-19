import type { AspectWindow } from './types'

function upperBound(values: number[], target: number): number {
  let low = 0
  let high = values.length
  while (low < high) {
    const middle = Math.floor((low + high) / 2)
    if (values[middle] <= target) low = middle + 1
    else high = middle
  }
  return low
}

function lowerBound(values: number[], target: number): number {
  let low = 0
  let high = values.length
  while (low < high) {
    const middle = Math.floor((low + high) / 2)
    if (values[middle] < target) low = middle + 1
    else high = middle
  }
  return low
}

export function activeAspectCountsAtPeak(events: AspectWindow[]): Map<string, number> {
  const starts = events.map((event) => event.start).sort((a, b) => a - b)
  const ends = events.map((event) => event.end).sort((a, b) => a - b)
  return new Map(events.map((event) => {
    const started = upperBound(starts, event.peak)
    const endedBeforePeak = lowerBound(ends, event.peak)
    return [event.eventId, Math.max(1, started - endedBeforePeak)]
  }))
}

export function aspectsAtTime(events: AspectWindow[], time: number): AspectWindow[] {
  return events
    .filter((event) => event.start <= time && event.end >= time)
    .sort((left, right) => (
      (left.lane ?? 0) - (right.lane ?? 0)
      || left.start - right.start
      || left.end - right.end
      || left.eventId.localeCompare(right.eventId)
    ))
}

export function nextAspectAtTime(
  events: AspectWindow[],
  time: number,
  selectedEventId?: string | null,
  preferredEventId?: string | null,
): AspectWindow | null {
  const candidates = aspectsAtTime(events, time)
  if (!candidates.length) return null
  const selectedIndex = candidates.findIndex((event) => event.eventId === selectedEventId)
  if (selectedIndex >= 0) return candidates[(selectedIndex + 1) % candidates.length]
  return candidates.find((event) => event.eventId === preferredEventId) ?? candidates[0]
}

export function formatAspectRange(event: AspectWindow): string {
  const format = (value: number) => new Date(value * 1000).toLocaleString([], {
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
  return `${format(event.start)} - ${format(event.end)}`
}
