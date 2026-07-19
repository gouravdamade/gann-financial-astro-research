import { describe, expect, it } from 'vitest'
import {
  activeAspectCountsAtPeak,
  aspectsAtTime,
  nextAspectAtTime,
} from './aspectPresentation'
import type { AspectWindow } from './types'

function event(
  eventId: string,
  start: number,
  end: number,
  peak: number,
  lane = 0,
): AspectWindow {
  return {
    eventId,
    caseId: null,
    familyKey: `family-${eventId}`,
    pairKey: 'MOON|MERCURY',
    aspect: 'square',
    aspectLabel: 'Square',
    transitBody: 'MOON',
    natalBody: 'MERCURY',
    start,
    end,
    peak,
    startIso: new Date(start * 1000).toISOString(),
    endIso: new Date(end * 1000).toISOString(),
    peakIso: new Date(peak * 1000).toISOString(),
    durationMinutes: (end - start) / 60,
    peakOrbDeg: 0.2,
    orbLimitDeg: 1,
    color: '#e0ad45',
    lane,
    occurrenceIndex: 1,
    occurrenceCount: 3,
    knownPriorCount: 2,
    knownOccurrenceCount: 3,
    outcome: null,
    returnPct: null,
    reviewed: false,
    reviewStatus: 'pending',
    reviewSource: 'none',
    signedPips: null,
    astronomyContract: 'test',
    sourceGenerator: 'test',
  }
}

describe('aspect chart presentation', () => {
  const events = [
    event('one', 10, 30, 20, 0),
    event('two', 15, 25, 20, 1),
    event('three', 20, 40, 30, 2),
  ]

  it('counts every aspect active at each event peak', () => {
    expect(Object.fromEntries(activeAspectCountsAtPeak(events))).toEqual({
      one: 3,
      two: 3,
      three: 2,
    })
  })

  it('returns all overlapping aspects in deterministic lane order', () => {
    expect(aspectsAtTime(events, 20).map((item) => item.eventId)).toEqual([
      'one',
      'two',
      'three',
    ])
  })

  it('cycles through overlapping aspects without hiding lower layers', () => {
    expect(nextAspectAtTime(events, 20, null, 'two')?.eventId).toBe('two')
    expect(nextAspectAtTime(events, 20, 'two')?.eventId).toBe('three')
    expect(nextAspectAtTime(events, 20, 'three')?.eventId).toBe('one')
  })
})
