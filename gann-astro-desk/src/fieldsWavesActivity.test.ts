import { describe, expect, it, vi } from 'vitest'
import type { MultiOscillatorActivityRange } from './types'
import {
  ACTIVITY_CHUNK_SECONDS,
  ACTIVITY_CACHE_CAPACITY,
  ActivityChunkCache,
  activityChunkAt,
  activityChunksForVisibleRange,
  activityChunkForVisibleRange,
  activityCoverageLabel,
  activityIntervalAt,
  activityStepPoints,
  activityVisibleRangeIsBounded,
  adjacentActivityChunk,
  groupActivityEventsForMarkers,
  mergeActivityRanges,
  unknownActivityCoverageRanges,
} from './fieldsWavesActivity'

const iso = (seconds: number) => new Date(seconds * 1000).toISOString()

function activityRange(start: number, end: number, suffix: string, count = 0, coverage: 'KNOWN' | 'UNKNOWN' = 'KNOWN') {
  const interval = {
    intervalId: `interval-${suffix}`,
    startUtc: iso(start),
    endUtc: iso(end),
    rawActiveEventCount: count,
    contributingEventIds: count ? [`event-${suffix}`] : [],
    coverage,
    unknownReason: coverage === 'UNKNOWN' ? 'fixture gap' : null,
  }
  const event = {
    eventId: `event-${suffix}`,
    eventHash: `hash-${suffix}`,
    sideIdentity: 'USD' as const,
    instrumentIdentity: 'FX_CURRENCY:USD',
    chartId: 'chart-usd',
    chartHypothesisId: 'hypothesis-usd',
    transitBody: 'SUN',
    natalTarget: 'MOON',
    aspectType: 'conjunction',
    applyingStartUtc: iso(start),
    exactUtc: iso(start + 1),
    separatingEndUtc: iso(end),
    polarity: null,
    magnitude: null,
  }
  const side = (sideIdentity: 'USD' | 'JPY') => ({
    contract: 'MO_UNSIGNED_EVENT_ACTIVITY_SIDE_V1_1',
    schemaVersion: 2,
    evidenceMode: 'EXPLORATORY_UNSIGNED',
    sideIdentity,
    instrumentIdentity: `FX_CURRENCY:${sideIdentity}`,
    chartId: `chart-${sideIdentity.toLowerCase()}`,
    chartHypothesisId: `hypothesis-${sideIdentity.toLowerCase()}`,
    rangeStartUtc: iso(start),
    rangeEndUtc: iso(end),
    eventUniverseProfileId: 'ASPECT_STRENGTH_V0',
    eventUniverseHash: 'universe-hash',
    bodyUniverse: ['SUN', 'MOON'],
    aspectProfile: {
      profileId: 'ASPECT_STRENGTH_V0',
      aspectTypes: ['conjunction'],
      maxOrbDeg: 3,
      directionPolicy: 'GEOMETRY_ONLY',
      doctrineStatus: 'EXPERIMENTAL_GEOMETRY_PROFILE',
    },
    astronomy: {},
    events: sideIdentity === 'USD' && count ? [event] : [],
    activityIntervals: [interval],
    sourceEventCount: count,
    eligibleEventCount: count,
    rejectedEventCount: 0,
    relevantRejectedEventCount: 0,
    irrelevantRejectedEventCount: 0,
    groupedCounts: { byTransitBody: {}, byAspectType: {} },
    coverage,
    unknownReason: interval.unknownReason,
    guardrails: {},
  })
  return {
    contract: 'MO_UNSIGNED_EVENT_ACTIVITY_RANGE_V1_1',
    schemaVersion: 2,
    evidenceMode: 'EXPLORATORY_UNSIGNED',
    contributionContract: 'MO_ACTIVITY_CONTRIBUTION_V1',
    rangeStartUtc: iso(start),
    rangeEndUtc: iso(end),
    sideIdentities: ['USD', 'JPY'],
    eventUniverse: {},
    fields: { USD: side('USD'), JPY: side('JPY') },
    guardrails: {},
  } as unknown as MultiOscillatorActivityRange
}

describe('chart-native Fields & Waves activity data', () => {
  it('uses fixed half-open 14-day UTC chunks and stable source context keys', () => {
    const chunk = activityChunkAt(ACTIVITY_CHUNK_SECONDS - 1)
    expect(chunk.startSeconds).toBe(0)
    expect(chunk.endSeconds).toBe(ACTIVITY_CHUNK_SECONDS)
    expect(activityChunkAt(ACTIVITY_CHUNK_SECONDS).startSeconds).toBe(ACTIVITY_CHUNK_SECONDS)
    expect(activityChunkForVisibleRange({ from: 1, to: 3 }).key).toBe(chunk.key)
    expect(activityChunksForVisibleRange({ from: 1, to: ACTIVITY_CHUNK_SECONDS }))
      .toHaveLength(1)
    expect(activityChunksForVisibleRange({ from: ACTIVITY_CHUNK_SECONDS - 10, to: ACTIVITY_CHUNK_SECONDS + 10 }))
      .toHaveLength(2)
    expect(activityChunksForVisibleRange({ from: 0, to: ACTIVITY_CHUNK_SECONDS * 20 }))
      .toHaveLength(12)
    expect(activityVisibleRangeIsBounded({ from: 0, to: ACTIVITY_CHUNK_SECONDS * 20 })).toBe(true)
    expect(activityVisibleRangeIsBounded({ from: 0, to: ACTIVITY_CHUNK_SECONDS * ACTIVITY_CACHE_CAPACITY })).toBe(false)
    expect(adjacentActivityChunk(chunk, 1).startSeconds).toBe(ACTIVITY_CHUNK_SECONDS)
    expect(chunk.key).toContain('USDJPY|USD+JPY|ASPECT_STRENGTH_V0')
  })

  it('distinguishes known zero, known count, and incomplete observed counts', () => {
    expect(activityCoverageLabel(null)).toBe('DATA NOT LOADED')
    expect(activityCoverageLabel({ rawActiveEventCount: 0, coverage: 'KNOWN' } as never))
      .toBe('0 observed | coverage known')
    expect(activityCoverageLabel({ rawActiveEventCount: 3, coverage: 'KNOWN' } as never))
      .toBe('3 observed | coverage known')
    expect(activityCoverageLabel({ rawActiveEventCount: 3, coverage: 'UNKNOWN' } as never))
      .toBe('3 observed | coverage incomplete')
    expect(activityCoverageLabel({ rawActiveEventCount: 0, coverage: 'UNKNOWN' } as never))
      .toBe('Coverage incomplete | no confirmed events')
  })

  it('uses half-open lookup and creates raw step points without interpolation', () => {
    const intervals = [
      activityRange(90, 105, 'a', 0).fields.USD.activityIntervals[0],
      activityRange(105, 120, 'b', 3).fields.USD.activityIntervals[0],
      activityRange(120, 130, 'c', 1).fields.USD.activityIntervals[0],
    ]
    expect(activityIntervalAt(intervals, 105)?.intervalId).toBe('interval-b')
    expect(activityIntervalAt(intervals, 130)).toBeNull()
    expect(activityStepPoints(intervals, { from: 100, to: 130 })).toEqual([
      { time: 100, value: 0 },
      { time: 105, value: 3 },
      { time: 120, value: 1 },
    ])
  })

  it('breaks the native line across unloaded intervals but not at epoch-adjacent edges', () => {
    const first = activityRange(90, 105, 'gap-a', 0).fields.USD.activityIntervals[0]
    const adjacent = activityRange(105, 120, 'gap-b', 3).fields.USD.activityIntervals[0]
    const disjoint = activityRange(115, 125, 'gap-c', 2).fields.USD.activityIntervals[0]
    const epochEquivalentEnd = { ...first, endUtc: '1970-01-01T00:01:45+00:00' }

    expect(Date.parse(epochEquivalentEnd.endUtc)).toBe(Date.parse(adjacent.startUtc))
    expect(activityStepPoints([epochEquivalentEnd, adjacent], { from: 100, to: 120 })).toEqual([
      { time: 100, value: 0 },
      { time: 105, value: 3 },
    ])
    expect(activityStepPoints([first, disjoint], { from: 100, to: 130 })).toEqual([
      { time: 100, value: 0 },
      { time: 105 },
      { time: 115, value: 2 },
    ])
    expect(activityStepPoints([first, { ...first, intervalId: 'duplicate-edge' }], { from: 90, to: 105 }))
      .toEqual([{ time: 90, value: 0 }])
  })

  it('unions incomplete coverage spans across USD and JPY without changing observations', () => {
    const usd = activityRange(0, 10, 'usd-gap', 3, 'UNKNOWN')
    const jpy = activityRange(5, 15, 'jpy-gap', 1, 'UNKNOWN')
    const known = activityRange(15, 20, 'known', 0, 'KNOWN')
    const range = {
      ...usd,
      fields: {
        ...usd.fields,
        JPY: {
          ...jpy.fields.JPY,
          activityIntervals: [jpy.fields.JPY.activityIntervals[0], known.fields.JPY.activityIntervals[0]],
        },
      },
    } as unknown as MultiOscillatorActivityRange
    expect(unknownActivityCoverageRanges(range)).toEqual([{ from: 0, to: 15 }])
    expect(range.fields.USD.activityIntervals[0].rawActiveEventCount).toBe(3)
  })

  it('keeps unknown-coverage hatching separate from an unloaded hole', () => {
    const left = activityRange(0, 5, 'unknown-left', 0, 'UNKNOWN')
    const right = activityRange(10, 15, 'unknown-right', 2, 'UNKNOWN')
    const range = {
      ...left,
      fields: {
        ...left.fields,
        USD: {
          ...left.fields.USD,
          activityIntervals: [
            left.fields.USD.activityIntervals[0],
            right.fields.USD.activityIntervals[0],
          ],
        },
        JPY: { ...left.fields.JPY, activityIntervals: [] },
      },
    } as unknown as MultiOscillatorActivityRange

    expect(unknownActivityCoverageRanges(range)).toEqual([
      { from: 0, to: 5 },
      { from: 10, to: 15 },
    ])
    expect(activityCoverageLabel(activityIntervalAt(range.fields.USD.activityIntervals, 7)))
      .toBe('DATA NOT LOADED')
    expect(activityCoverageLabel(activityIntervalAt(range.fields.USD.activityIntervals, 12)))
      .toBe('2 observed | coverage incomplete')
  })

  it('groups exact markers by side and UTC second, bounds them to the visible half-open data range', () => {
    const usd = activityRange(0, 10, 'usd', 1)
    const jpy = activityRange(0, 10, 'jpy', 1)
    const usdEvent = { ...usd.fields.USD.events[0], exactUtc: iso(4) }
    const jpyEvent = { ...jpy.fields.USD.events[0], sideIdentity: 'JPY' as const, exactUtc: iso(4) }
    const endEvent = { ...usdEvent, eventId: 'event-at-end', exactUtc: iso(10) }
    const fields = {
      USD: { ...usd.fields.USD, events: [usdEvent, endEvent] },
      JPY: { ...jpy.fields.JPY, events: [jpyEvent] },
    } as unknown as MultiOscillatorActivityRange['fields']
    const groups = groupActivityEventsForMarkers(fields, { from: 0, to: 10 }, { from: 3, to: 6 })
    expect(groups.map((group) => [group.markerId, group.side, group.time, group.events.length])).toEqual([
      ['activity-USD-4', 'USD', 4, 1],
      ['activity-JPY-4', 'JPY', 4, 1],
    ])
  })

  it('does not place exact-event markers in an unloaded interval gap', () => {
    const loaded = activityRange(0, 5, 'marker-loaded', 1)
    const inGap = { ...loaded.fields.USD.events[0], eventId: 'event-in-gap', exactUtc: iso(7) }
    const laterLoaded = { ...loaded.fields.USD.events[0], eventId: 'event-later', exactUtc: iso(12) }
    const fields = {
      USD: {
        ...loaded.fields.USD,
        events: [loaded.fields.USD.events[0], inGap, laterLoaded],
        activityIntervals: [
          loaded.fields.USD.activityIntervals[0],
          activityRange(10, 15, 'marker-later', 1).fields.USD.activityIntervals[0],
        ],
      },
      JPY: { ...loaded.fields.JPY, activityIntervals: [] },
    } as unknown as MultiOscillatorActivityRange['fields']

    expect(groupActivityEventsForMarkers(fields, { from: 0, to: 15 }, { from: 0, to: 15 })
      .flatMap((group) => group.events.map((event) => event.eventId)))
      .toEqual(['event-marker-loaded', 'event-later'])
    expect(activityCoverageLabel(activityIntervalAt(fields.USD.activityIntervals, 7))).toBe('DATA NOT LOADED')
    expect(activityCoverageLabel(activityIntervalAt(fields.USD.activityIntervals, 2))).toBe('1 observed | coverage known')
  })

  it('merges chunk records by immutable event and interval identity without averaging', () => {
    const first = activityRange(0, 10, 'shared', 3, 'UNKNOWN')
    const second = activityRange(10, 20, 'next', 1, 'KNOWN')
    const epochEquivalentDuplicate = {
      ...first.fields.USD.activityIntervals[0],
      startUtc: '1970-01-01T01:00:00+01:00',
      endUtc: '1970-01-01T01:00:10+01:00',
    }
    const duplicated = {
      ...second,
      fields: {
        ...second.fields,
        USD: {
          ...second.fields.USD,
          events: [...second.fields.USD.events, first.fields.USD.events[0]],
          activityIntervals: [...second.fields.USD.activityIntervals, epochEquivalentDuplicate],
        },
      },
    }
    const merged = mergeActivityRanges([first, duplicated])
    expect(merged?.fields.USD.events.map((event) => event.eventId)).toEqual(['event-shared', 'event-next'])
    expect(merged?.fields.USD.activityIntervals).toHaveLength(2)
    expect(merged?.fields.USD.coverage).toBe('UNKNOWN')
    expect(merged?.fields.USD.activityIntervals.map((interval) => interval.rawActiveEventCount)).toEqual([3, 1])
    expect(activityIntervalAt(merged!.fields.USD.activityIntervals, 10)?.intervalId).toBe('interval-next')
    expect(activityIntervalAt(merged!.fields.USD.activityIntervals, 20)).toBeNull()
  })

  it('deduplicates simultaneous in-flight requests and evicts least-recently-used chunks', async () => {
    const fetchRange = vi.fn(async (request) => activityRange(
      Date.parse(request.rangeStartUtc) / 1000,
      Date.parse(request.rangeEndUtc) / 1000,
      request.rangeStartUtc,
    ))
    const cache = new ActivityChunkCache(fetchRange, 2)
    const firstChunk = activityChunkAt(1)
    const firstA = cache.request(firstChunk)
    const firstB = cache.request(firstChunk)
    expect(fetchRange).toHaveBeenCalledTimes(1)
    await Promise.all([firstA, firstB])
    const secondChunk = activityChunkAt(ACTIVITY_CHUNK_SECONDS + 1)
    await cache.request(secondChunk)
    expect(cache.get(firstChunk)).not.toBeNull()
    const thirdChunk = activityChunkAt(2 * ACTIVITY_CHUNK_SECONDS + 1)
    await cache.request(thirdChunk)
    expect(cache.has(secondChunk)).toBe(false)
    expect(cache.has(firstChunk)).toBe(true)
    expect(cache.has(thirdChunk)).toBe(true)
  })
})
