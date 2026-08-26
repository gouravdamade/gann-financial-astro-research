import type { MultiOscillatorActivityEvent, MultiOscillatorActivityInterval } from '../types'

export const MO_UNSIGNED_ACTIVITY_STEP_WAVE_CONTRACT = 'MO_UNSIGNED_ACTIVITY_STEP_WAVE_V1' as const

export type UnsignedActivityStepSegment = {
  startUtc: string
  endUtc: string
  rawActiveEventCount: number
  coverage: MultiOscillatorActivityInterval['coverage']
  unknownReason: string | null
  contributingEventIds: string[]
  semanticUnit: 'ACTIVE_EVENT_COUNT'
}

export type UnsignedActivityWaveSide = 'USD' | 'JPY'

export const WAVE_PLOT_TOP = 8
export const WAVE_PLOT_BASELINE = 92

function timestampMs(value: string): number {
  const parsed = Date.parse(value)
  return Number.isFinite(parsed) ? parsed : 0
}

function percentBetween(value: string, startUtc: string, endUtc: string): number {
  const start = timestampMs(startUtc)
  const end = timestampMs(endUtc)
  if (end <= start) return 0
  return Math.max(0, Math.min(100, ((timestampMs(value) - start) / (end - start)) * 100))
}

function coordinate(value: number): string {
  return Number(value.toFixed(4)).toString()
}

export function deriveUnsignedActivityStepSegments(
  intervals: MultiOscillatorActivityInterval[],
): UnsignedActivityStepSegment[] {
  return intervals.map((interval) => ({
    startUtc: interval.startUtc,
    endUtc: interval.endUtc,
    rawActiveEventCount: interval.rawActiveEventCount,
    coverage: interval.coverage,
    unknownReason: interval.unknownReason,
    contributingEventIds: [...interval.contributingEventIds],
    semanticUnit: 'ACTIVE_EVENT_COUNT',
  }))
}

export function unsignedActivityWaveY(rawCount: number, sharedAxisMax: number): number {
  if (!Number.isFinite(rawCount) || rawCount <= 0) return WAVE_PLOT_BASELINE
  if (!Number.isFinite(sharedAxisMax) || sharedAxisMax <= 0) return WAVE_PLOT_BASELINE
  const height = Math.min(1, Math.max(0, rawCount / sharedAxisMax)) * (WAVE_PLOT_BASELINE - WAVE_PLOT_TOP)
  return WAVE_PLOT_BASELINE - height
}

export function unsignedActivityStepSegmentPath(
  segment: UnsignedActivityStepSegment,
  rangeStartUtc: string,
  rangeEndUtc: string,
  sharedAxisMax: number,
): string {
  const startX = coordinate(percentBetween(segment.startUtc, rangeStartUtc, rangeEndUtc))
  const endX = coordinate(percentBetween(segment.endUtc, rangeStartUtc, rangeEndUtc))
  const y = coordinate(unsignedActivityWaveY(segment.rawActiveEventCount, sharedAxisMax))
  return `M ${startX} ${y} H ${endX}`
}

export function unsignedActivityStepWavePath(
  segments: UnsignedActivityStepSegment[],
  rangeStartUtc: string,
  rangeEndUtc: string,
  sharedAxisMax: number,
): string {
  if (!segments.length) return ''

  const commands: string[] = []
  segments.forEach((segment, index) => {
    const startX = coordinate(percentBetween(segment.startUtc, rangeStartUtc, rangeEndUtc))
    const endX = coordinate(percentBetween(segment.endUtc, rangeStartUtc, rangeEndUtc))
    const y = coordinate(unsignedActivityWaveY(segment.rawActiveEventCount, sharedAxisMax))
    const previous = segments[index - 1]

    if (index === 0 || !previous || timestampMs(previous.endUtc) !== timestampMs(segment.startUtc)) {
      commands.push(`M ${startX} ${y}`)
    } else {
      commands.push(`V ${y}`)
    }
    commands.push(`H ${endX}`)
  })
  return commands.join(' ')
}

export function unsignedActivityWaveIntervalStyle(
  segment: UnsignedActivityStepSegment,
  rangeStartUtc: string,
  rangeEndUtc: string,
): { left: string; width: string } {
  const left = percentBetween(segment.startUtc, rangeStartUtc, rangeEndUtc)
  const right = percentBetween(segment.endUtc, rangeStartUtc, rangeEndUtc)
  return {
    left: `${left}%`,
    width: `${Math.max(0.2, right - left)}%`,
  }
}

export function unsignedActivityWaveMarkerStyle(
  event: Pick<MultiOscillatorActivityEvent, 'exactUtc'>,
  rangeStartUtc: string,
  rangeEndUtc: string,
): { left: string } {
  return { left: `${percentBetween(event.exactUtc, rangeStartUtc, rangeEndUtc)}%` }
}
