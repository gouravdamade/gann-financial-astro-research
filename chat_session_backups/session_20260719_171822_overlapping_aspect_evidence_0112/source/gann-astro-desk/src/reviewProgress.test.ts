import { describe, expect, it } from 'vitest'
import { canToggleReview, nextReviewStatus, reviewButtonLabel } from './reviewProgress'
import type { AspectWindow } from './types'

function occurrence(overrides: Partial<AspectWindow> = {}): AspectWindow {
  return {
    eventId: 'event-1',
    caseId: 1,
    familyKey: 'TN::MOON->MERCURY::square',
    pairKey: 'MOON|MERCURY',
    aspect: 'square',
    aspectLabel: 'Square',
    transitBody: 'MOON',
    natalBody: 'MERCURY',
    start: 1,
    end: 2,
    peak: 1,
    startIso: '2025-01-01T00:00:00+05:30',
    endIso: '2025-01-01T01:00:00+05:30',
    peakIso: '2025-01-01T00:30:00+05:30',
    durationMinutes: 60,
    peakOrbDeg: 0.1,
    orbLimitDeg: 1,
    color: '#ffffff',
    occurrenceIndex: 1,
    occurrenceCount: 1,
    knownPriorCount: 0,
    knownOccurrenceCount: 1,
    outcome: null,
    returnPct: null,
    reviewed: false,
    reviewStatus: 'pending',
    reviewSource: 'none',
    signedPips: null,
    astronomyContract: 'test',
    sourceGenerator: 'test',
    ...overrides,
  }
}

describe('review progress policy', () => {
  it('marks an untouched occurrence reviewed next', () => {
    const item = occurrence()
    expect(canToggleReview(item)).toBe(true)
    expect(nextReviewStatus(item)).toBe('reviewed')
    expect(reviewButtonLabel(item, false)).toBe('Mark reviewed')
  })

  it('reopens app progress without rewriting legacy completion', () => {
    expect(nextReviewStatus(occurrence({ reviewed: true, reviewSource: 'app_progress' }))).toBe('pending')
    const legacy = occurrence({ reviewed: true, reviewSource: 'legacy_completed_review' })
    expect(canToggleReview(legacy)).toBe(false)
    expect(reviewButtonLabel(legacy, false)).toBe('Legacy review complete')
  })
})
