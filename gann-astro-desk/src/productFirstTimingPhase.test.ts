import { describe, expect, it } from 'vitest'
import type { AspectWindow, ChakraLabSnapshot } from './types'
import { calculateProductFirstTimingPhase, PROJECT_CONVENTION_TIMING_PHASE_V0 } from './productFirstTimingPhase'

const aspect: AspectWindow = {
  eventId: 'event-1',
  caseId: 1,
  familyKey: 'TEST',
  pairKey: 'MOON|MARS',
  aspect: 'Square',
  aspectLabel: 'MOON to MARS Square',
  transitBody: 'MOON',
  natalBody: 'MARS',
  start: 1_000,
  end: 2_000,
  peak: 1_500,
  startIso: '1970-01-01T00:16:40.000Z',
  peakIso: '1970-01-01T00:25:00.000Z',
  endIso: '1970-01-01T00:33:20.000Z',
  durationMinutes: 16,
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

describe('PROJECT_CONVENTION_TIMING_PHASE_V0', () => {
  it('fails closed when the feature flag is disabled', () => {
    const result = calculateProductFirstTimingPhase({
      enabled: false,
      snapshot: snapshotAt(1_500, [{ body: 'MOON', signed: 2 }]),
      aspects: [aspect],
    })

    expect(result.enabled).toBe(false)
    expect(result.state).toBe('UNKNOWN')
    expect(result.vectors).toEqual([])
    expect(result.marketDirection).toBe('ABSTAIN')
  })

  it('builds inspectable internal geometry but retains a permanent zero vote and ABSTAIN market result', () => {
    const result = calculateProductFirstTimingPhase({
      enabled: true,
      snapshot: snapshotAt(1_500, [{ body: 'MOON', signed: 2 }, { body: 'MARS', signed: -1 }, { body: 'VENUS', signed: null }]),
      aspects: [aspect],
    })

    expect(result.contract).toBe(PROJECT_CONVENTION_TIMING_PHASE_V0.contract)
    expect(result.activeEvents).toHaveLength(1)
    expect(result.activeEvents[0]?.lifecycle).toBe('EXACT')
    expect(result.realUnits).toBeCloseTo(1)
    expect(result.imaginaryUnits).toBeCloseTo(0)
    expect(result.marketDirection).toBe('ABSTAIN')
    expect(result.directionalInterpretation).toBe('SUPPRESSED')
    expect(result.guardrails).toMatchObject({ voteWeight: 0, directionalContribution: 0, fusionCoefficient: 0, executionAllowed: false })
    expect(result.unknownVectorCount).toBe(1)
  })

  it('suppresses interpretation outside the declared safe sector without altering vectors', () => {
    const result = calculateProductFirstTimingPhase({
      enabled: true,
      snapshot: snapshotAt(1_000, [{ body: 'MOON', signed: 2 }]),
      aspects: [aspect],
    })

    expect(result.vectors).toHaveLength(1)
    expect(result.safeSector).toBe(false)
    expect(result.state).toBe('NON_DIRECTIONAL_TIMING_GEOMETRY')
    expect(result.directionalInterpretation).toBe('NOT_AVAILABLE')
    expect(result.marketDirection).toBe('ABSTAIN')
  })

  it('keeps overlapping windows independently phased instead of rotating all contributions by one nearest event', () => {
    const earlierEvent: AspectWindow = {
      ...aspect,
      eventId: 'event-2',
      aspectLabel: 'VENUS to SATURN Trine',
      peak: 1_250,
      peakIso: '1970-01-01T00:20:50.000Z',
    }
    const result = calculateProductFirstTimingPhase({
      enabled: true,
      snapshot: snapshotAt(1_500, [{ body: 'MOON', signed: 2 }]),
      aspects: [aspect, earlierEvent],
    })

    expect(result.activeEvents).toHaveLength(2)
    expect(result.activeEvents.map((event) => event.lifecycle)).toEqual(['EXACT', 'SEPARATING'])
    expect(result.vectors).toHaveLength(2)
    expect(new Set(result.vectors.map((vector) => vector.eventId))).toEqual(new Set(['event-1', 'event-2']))
    expect(result.vectors[0]?.timingPhaseRadians).not.toBe(result.vectors[1]?.timingPhaseRadians)
    expect(result.marketDirection).toBe('ABSTAIN')
    expect(result.guardrails).toMatchObject({ voteWeight: 0, directionalContribution: 0, fusionCoefficient: 0, executionAllowed: false })
  })

  it('uses near-zero abstention when opposing vectors cancel despite gross activity', () => {
    const result = calculateProductFirstTimingPhase({
      enabled: true,
      snapshot: snapshotAt(1_500, [{ body: 'MOON', signed: 1 }, { body: 'MARS', signed: -1 }]),
      aspects: [aspect],
    })

    expect(result.grossUnits).toBe(2)
    expect(result.resultantUnits).toBeCloseTo(0)
    expect(result.collectivePhaseRadians).toBeNull()
    expect(result.state).toBe('RESULTANT_NEAR_ZERO')
    expect(result.marketDirection).toBe('ABSTAIN')
  })
})
