import { describe, expect, it } from 'vitest'
import type { AspectWindow, ChakraLabSnapshot } from './types'
import { calculateProductFirstTimingPhase, PROJECT_CONVENTION_TIMING_PHASE_V1 } from './productFirstTimingPhase'

function aspect(overrides: Partial<AspectWindow> = {}): AspectWindow {
  return {
    eventId: 'event-1',
    caseId: 1,
    familyKey: 'TEST',
    pairKey: 'MOON|MARS',
    aspect: 'Square',
    aspectLabel: 'MOON to MARS Square',
    transitBody: 'MOON',
    natalBody: 'MARS',
    start: 1_000,
    end: 1_180,
    peak: 1_100,
    startIso: '1970-01-01T00:16:40.000Z',
    peakIso: '1970-01-01T00:18:20.000Z',
    endIso: '1970-01-01T00:19:40.000Z',
    durationMinutes: 2,
    peakOrbDeg: 0,
    orbLimitDeg: 1,
    color: '#000000',
    occurrenceIndex: 1,
    occurrenceCount: 1,
    knownPriorCount: 0,
    knownOccurrenceCount: 1,
    outcome: null,
    returnPct: null,
    reviewed: false,
    reviewStatus: 'none',
    reviewSource: 'none',
    signedPips: null,
    astronomyContract: 'TEST',
    sourceGenerator: 'TEST',
    ...overrides,
  }
}

function snapshotAt(epochSeconds: number, contributions: Array<{ body: string; signed: number | null }>): ChakraLabSnapshot {
  return {
    as_of_utc: new Date(epochSeconds * 1000).toISOString(),
    guidance: {
      contributions: contributions.map((item, index) => ({
        body: item.body,
        source_nakshatra: 'Ashwini',
        direction: 'LEFT',
        target: { row: 1, column: index + 1, layer: 'NAKSHATRA', value: `Target ${index + 1}`, semantic_role: null, witness_set_id: 'test', evidence_status: 'TEST' },
        nature: 'BENEFIC',
        effective_multiplier: 1,
        signed_guidance_units: item.signed,
        status: item.signed == null ? 'UNKNOWN' : 'READY',
        explanation: 'test',
      })),
    },
  } as ChakraLabSnapshot
}

describe('PROJECT_CONVENTION_TIMING_PHASE_V1', () => {
  it('fails closed while disabled', () => {
    const result = calculateProductFirstTimingPhase({ enabled: false, snapshot: snapshotAt(1_050, [{ body: 'MOON', signed: 2 }]), aspects: [aspect()] })
    expect(result.enabled).toBe(false)
    expect(result.state).toBe('UNKNOWN')
    expect(result.vectors).toEqual([])
    expect(result.marketDirection).toBe('ABSTAIN')
    expect(result.guardrails).toMatchObject({ voteWeight: 0, executionAllowed: false, automaticOrderPlacement: false })
  })

  it('uses independent applying and separating denominators around exact', () => {
    const applying = calculateProductFirstTimingPhase({ enabled: true, snapshot: snapshotAt(1_050, [{ body: 'MOON', signed: 2 }]), aspects: [aspect()] })
    const separating = calculateProductFirstTimingPhase({ enabled: true, snapshot: snapshotAt(1_140, [{ body: 'MOON', signed: 2 }]), aspects: [aspect()] })

    expect(applying.contract).toBe(PROJECT_CONVENTION_TIMING_PHASE_V1.contract)
    expect(applying.activeEvents[0]).toMatchObject({ lifecycle: 'APPLYING', applyingWindowSeconds: 100, separatingWindowSeconds: 80, normalizedLifecycleProgress: -0.5, symmetricTimingDeclared: false })
    expect(separating.activeEvents[0]).toMatchObject({ lifecycle: 'SEPARATING', normalizedLifecycleProgress: 0.5, symmetricTimingDeclared: false })
    expect(applying.state).toBe('UNLINKED_EVENT_GEOMETRY')
    expect(applying.aggregateWithheld).toBe(true)
    expect(applying.sourceGapId).toBe('EVENT_CONTRIBUTION_LINK_PROFILE_MISSING')
    expect(applying.realUnits).toBeNull()
    expect(applying.vectors).toEqual([])
  })

  it('keeps overlapping event lifecycles but withholds the unlinked aggregate', () => {
    const result = calculateProductFirstTimingPhase({
      enabled: true,
      snapshot: snapshotAt(1_100, [{ body: 'MOON', signed: 2 }, { body: 'VENUS', signed: null }]),
      aspects: [aspect(), aspect({ eventId: 'event-2', aspectLabel: 'VENUS to SATURN Trine', start: 1_010, peak: 1_060, end: 1_160 })],
    })
    expect(result.activeEvents).toHaveLength(2)
    expect(result.vectors).toEqual([])
    expect(result.unlinkedResolvedContributionCount).toBe(1)
    expect(result.unknownVectorCount).toBe(1)
    expect(result.aggregateWithheldReason).toContain('EVENT_CONTRIBUTION_LINK_PROFILE_MISSING')
    expect(result.marketDirection).toBe('ABSTAIN')
  })

  it('fails closed for an invalid zero-length event span', () => {
    const result = calculateProductFirstTimingPhase({
      enabled: true,
      snapshot: snapshotAt(1_100, [{ body: 'MOON', signed: 2 }]),
      aspects: [aspect({ peak: 1_000, peakIso: '1970-01-01T00:16:40.000Z' })],
    })
    expect(result.state).toBe('UNKNOWN_INVALID_EVENT_WINDOW')
    expect(result.activeEvents[0]?.lifecycle).toBe('UNKNOWN')
    expect(result.calculationId).toMatch(/^PFTPV1-/)
    expect(result.marketDirection).toBe('ABSTAIN')
  })

  it('returns unknown when no event is active', () => {
    const result = calculateProductFirstTimingPhase({ enabled: true, snapshot: snapshotAt(900, [{ body: 'MOON', signed: 2 }]), aspects: [aspect()] })
    expect(result.state).toBe('UNKNOWN')
    expect(result.activeEvents).toEqual([])
    expect(result.calculationId).toBeNull()
    expect(result.marketDirection).toBe('ABSTAIN')
  })
})
