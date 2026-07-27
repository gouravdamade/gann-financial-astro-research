import { describe, expect, it } from 'vitest'
import {
  MAX_COLLECTIVE_AUDIT_SNAPSHOTS,
  MAX_COLLECTIVE_AUDIT_STORAGE_BYTES,
  collectiveAuditFileName,
  createCollectiveAuditSnapshot,
  normalizeCollectiveAuditSnapshots,
  upsertCollectiveAuditSnapshot,
} from './collectiveAudit'
import type {
  PlanetaryCollectiveAuditSnapshot,
  PlanetaryCollectiveField,
  PlanetaryCollectiveSample,
} from './types'

const firstTime = 1_700_000_000
const secondTime = firstTime + 3_600

function sample(time: number): PlanetaryCollectiveSample {
  return {
    time,
    meanLongitudeDeg: 145,
    coherenceR1: 0.72,
    circularVariance: 0.28,
    circularStdDeg: 46,
    polarisationR2: 0.31,
    polarisationAxisDeg: 60,
    state: 'CONCENTRATED',
    reliability: 'RELIABLE',
    longitudeReliable: true,
    segmentId: 1,
    unwrappedLongitudeDeg: 145,
    velocityDegPerDay: 0.8,
    accelerationDegPerDay2: null,
    memberAudit: [{
      body: 'SUN',
      longitudeDeg: 140,
      weight: 1,
      angularDistanceFromMeanDeg: 5,
      longitudeLeverageDeg: 2,
      coherenceLeverage: 0.04,
      tempoClass: 'FAST_MOVING_CLASS',
      role: 'CONCENTRATING_FAST_MEMBER',
      influenceRank: 1,
    }],
  }
}

function field(): PlanetaryCollectiveField {
  const samples = [sample(firstTime), sample(secondTime)]
  return {
    calculationVersion: 'AVG_ALL_CIRCULAR_GEOMETRY_V1',
    profile: {
      profileId: 'AVG_ALL_TEST',
      members: ['SUN'],
      weights: [1],
      nodePolicy: 'TRUE_NODES',
      memberSetHash: 'sha256:test',
      thresholdProfile: {
        profileId: 'AVG_ALL_TEST_THRESHOLDS',
        classification: 'UI_HEURISTIC_RESEARCH_ONLY',
        unstableResultantFloor: 0.05,
        lowCoherenceFloor: 0.35,
        concentratedFloor: 0.65,
        bipolarR2Floor: 0.65,
      },
    },
    samples,
    latest: samples[1],
    events: [{
      contract: 'GANN_PLANETARY_COLLECTIVE_EVENT_V1',
      eventId: 'refined-ingress',
      profileId: 'AVG_ALL_TEST',
      eventPolicyId: 'AVG_ALL_SAMPLED_EVENTS_V1',
      eventType: 'MEAN_RASHI_INGRESS',
      estimatedTimeUnix: firstTime + 1_000,
      refinedTimeUnix: firstTime + 1_500,
      sourceBracket: {
        startUnix: firstTime,
        endUnix: secondTime,
      },
      timing: {
        exact: true,
        method: 'BRACKETED_BISECTION_OF_EPHEMERIS_MEAN',
        precision: 'WITHIN_DECLARED_TIME_AND_ANGULAR_TOLERANCE',
        sampledEstimateUnix: firstTime + 1_000,
        rootToleranceSeconds: 1,
        residualToleranceDeg: 0.001,
      },
      refinement: {
        contract: 'GANN_PLANETARY_COLLECTIVE_EVENT_REFINEMENT_V1',
        policyId: 'AVG_ALL_EPHEMERIS_ROOT_REFINEMENT_V1',
        status: 'REFINED_BRACKETED_ROOT',
        sampledEstimateUnix: firstTime + 1_000,
        refinedTimeUnix: firstTime + 1_500,
        rootToleranceSeconds: 1,
        residualToleranceDeg: 0.001,
        residualDeg: 0.0001,
        coherenceR1AtRoot: 0.72,
        iterations: 12,
        evaluatedTimestampCount: 14,
        reason: 'fixture root',
        astronomyContract: 'RAMAN_SIDEREAL_SWISSEPH_EPHEMERIS_ROOT_V1',
        guardrails: {
          researchOnly: true,
          preservesSampledEstimate: true,
          countsAsIndependentVote: false,
          directionalContribution: 0,
          consumedByLiveInference: false,
          consumedByAutoSuggest: false,
          consumedByShadowLedger: false,
          consumedByOfficialMlNotes: false,
          executionAllowed: false,
        },
      },
      causalClusterId: 'cluster-1',
      details: {
        fromRashi: 'ARIES',
        toRashi: 'TAURUS',
      },
      guardrails: {
        researchOnly: true,
        visualMarkerOnly: true,
        timestampSafe: true,
        exactEventTime: true,
        directionalContribution: 0,
        castsSbcVedha: false,
        consumedByLiveInference: false,
        consumedByAutoSuggest: false,
        consumedByShadowLedger: false,
        consumedByOfficialMlNotes: false,
        executionAllowed: false,
      },
    }],
  } as unknown as PlanetaryCollectiveField
}

function makeSnapshot(overrides: {
  snapshotId?: string
  createdAtUtc?: string
  selectedTimeUnix?: number
} = {}): PlanetaryCollectiveAuditSnapshot {
  return createCollectiveAuditSnapshot({
    field: field(),
    selectedTimeUnix: overrides.selectedTimeUnix ?? firstTime,
    symbol: 'usdjpy',
    timeframe: 'h1',
    chartStartUtc: '2023-11-14T00:00:00Z',
    chartEndUtc: '2023-11-15T00:00:00Z',
    snapshotId: overrides.snapshotId ?? 'audit-1',
    createdAtUtc: overrides.createdAtUtc ?? '2026-07-27T10:00:00Z',
  })
}

describe('collective audit snapshots', () => {
  it('copies the nearest bar and preserves refined event evidence', () => {
    const snapshot = makeSnapshot()
    expect(snapshot.symbol).toBe('USDJPY')
    expect(snapshot.timeframe).toBe('H1')
    expect(snapshot.selectedTimeUnix).toBe(firstTime)
    expect(snapshot.nearbyEvents[0].refinedTimeUnix).toBe(firstTime + 1_500)
    expect(snapshot.guardrails).toMatchObject({
      immutableEvidenceCopy: true,
      consumedByLiveInference: false,
      consumedByAutoSuggest: false,
      executionAllowed: false,
    })
  })

  it('replaces the same timestamp/profile audit instead of duplicating it', () => {
    const original = makeSnapshot()
    const replacement = makeSnapshot({
      snapshotId: 'audit-2',
      createdAtUtc: '2026-07-27T11:00:00Z',
    })
    const output = upsertCollectiveAuditSnapshot([original], replacement)
    expect(output).toHaveLength(1)
    expect(output[0].snapshotId).toBe('audit-2')
  })

  it('rejects unsafe imports, deduplicates ids, and caps retained history', () => {
    const snapshots = Array.from(
      { length: MAX_COLLECTIVE_AUDIT_SNAPSHOTS + 3 },
      (_, index) => makeSnapshot({
        snapshotId: `audit-${index}`,
        createdAtUtc: new Date(Date.UTC(2026, 6, 27, 10, index)).toISOString(),
        selectedTimeUnix: index % 2 ? firstTime : secondTime,
      }),
    )
    const unsafe = JSON.parse(JSON.stringify(makeSnapshot({
      snapshotId: 'unsafe',
    }))) as PlanetaryCollectiveAuditSnapshot
    ;(unsafe.guardrails as unknown as { executionAllowed: boolean })
      .executionAllowed = true
    const output = normalizeCollectiveAuditSnapshots([
      ...snapshots,
      snapshots[0],
      unsafe,
    ])
    expect(output).toHaveLength(MAX_COLLECTIVE_AUDIT_SNAPSHOTS)
    expect(output.some((item) => item.snapshotId === 'unsafe')).toBe(false)
    expect(new Set(output.map((item) => item.snapshotId)).size).toBe(output.length)
  })

  it('rejects unsafe nested events and enforces the layout storage budget', () => {
    const unsafeEvent = JSON.parse(JSON.stringify(makeSnapshot({
      snapshotId: 'unsafe-event',
    }))) as PlanetaryCollectiveAuditSnapshot
    ;(
      unsafeEvent.nearbyEvents[0].guardrails as unknown as {
        executionAllowed: boolean
      }
    ).executionAllowed = true
    expect(normalizeCollectiveAuditSnapshots([unsafeEvent])).toEqual([])

    const oversized = makeSnapshot({ snapshotId: 'oversized' })
    oversized.nearbyEvents[0].details = {
      padding: 'x'.repeat(MAX_COLLECTIVE_AUDIT_STORAGE_BYTES),
    }
    expect(normalizeCollectiveAuditSnapshots([oversized])).toEqual([])
  })

  it('uses a deterministic filesystem-safe export name', () => {
    expect(collectiveAuditFileName(makeSnapshot())).toBe(
      'USDJPY_H1_avg_all_audit_2023-11-14T221320Z.json',
    )
  })
})
