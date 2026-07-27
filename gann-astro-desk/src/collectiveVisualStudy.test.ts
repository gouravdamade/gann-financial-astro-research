import { describe, expect, it } from 'vitest'
import {
  collectiveVisualStudyFileName,
  createCollectiveStudySbcRequest,
  createCollectiveVisualStudyDossier,
} from './collectiveVisualStudy'
import type {
  ChakraLabSnapshot,
  ChartDrawing,
  PlanetaryCollectiveAuditSnapshot,
} from './types'

const selectedTimeUnix = Date.parse('2026-07-27T06:30:00Z') / 1000

function audit(): PlanetaryCollectiveAuditSnapshot {
  return {
    contract: 'GANN_PLANETARY_COLLECTIVE_AUDIT_SNAPSHOT_V1',
    schemaVersion: 1,
    snapshotId: 'audit-m7',
    createdAtUtc: '2026-07-27T06:30:01Z',
    symbol: 'USDJPY',
    timeframe: 'H1',
    chartRange: {
      startUtc: '2026-07-26T00:00:00Z',
      endUtc: '2026-07-28T00:00:00Z',
    },
    selectedTimeUnix,
    fieldCalculationVersion: 'AVG_ALL_CIRCULAR_GEOMETRY_V1',
    profile: {
      profileId: 'AVG_ALL_EQUAL_WEIGHT_TEN_BODY_V1',
      members: ['SUN'],
      weights: [1],
      nodePolicy: 'EXCLUDED',
      memberSetHash: 'sha256:m7',
      thresholdProfile: {
        profileId: 'AVG_ALL_GEOMETRY_THRESHOLDS_V1',
        classification: 'UI_HEURISTIC_RESEARCH_ONLY',
        unstableResultantFloor: 0.05,
        lowCoherenceFloor: 0.2,
        concentratedFloor: 0.65,
        bipolarR2Floor: 0.65,
      },
    },
    sample: {
      time: selectedTimeUnix,
      meanLongitudeDeg: 120,
      coherenceR1: 0.7,
      circularVariance: 0.3,
      circularStdDeg: 40,
      polarisationR2: 0.2,
      polarisationAxisDeg: 30,
      state: 'CONCENTRATED',
      reliability: 'RELIABLE',
      longitudeReliable: true,
      segmentId: 1,
      unwrappedLongitudeDeg: 120,
      velocityDegPerDay: 0.4,
      accelerationDegPerDay2: null,
      memberAudit: [{
        body: 'SUN',
        longitudeDeg: 120,
        weight: 1,
        angularDistanceFromMeanDeg: 0,
        longitudeLeverageDeg: 0,
        coherenceLeverage: 0,
        tempoClass: 'SLOW_MOVING_CLASS',
        role: 'SLOW_ANCHOR',
        influenceRank: 1,
      }],
    },
    nearbyEvents: [],
    guardrails: {
      researchOnly: true,
      immutableEvidenceCopy: true,
      countsAsIndependentVote: false,
      directionalContribution: 0,
      consumedByLiveInference: false,
      consumedByAutoSuggest: false,
      consumedByShadowLedger: false,
      consumedByOfficialMlNotes: false,
      executionAllowed: false,
    },
  }
}

function gannFan(visible = true): ChartDrawing {
  return {
    contract: 'GANN_RESEARCH_CHART_DRAWING_V1',
    schemaVersion: 1,
    drawingId: 'fan-1',
    type: 'gann_fan',
    name: 'Review fan',
    visible,
    locked: false,
    groupId: null,
    groupName: '',
    syncScope: 'layout',
    pane: 'price',
    zIndex: 1,
    anchors: [{
      timeUtc: '2026-07-27T06:00:00Z',
      price: 147.25,
    }],
    style: {
      color: '#D7A63E',
      lineWidth: 1,
      lineStyle: 'dashed',
      opacity: 0.82,
    },
    settings: { ratios: [0.5, 1, 2] },
    guardrails: {
      researchOnly: true,
      consumedByLiveInference: false,
      consumedByShadowLedger: false,
      executionAllowed: false,
    },
  }
}

function sbcSnapshot(): ChakraLabSnapshot {
  return {
    contract: 'SBC_CHAKRA_LAB_SNAPSHOT_V1',
    schema_version: 1,
    snapshot_id: 'sbc-m7',
    requested_at_local: '2026-07-27T12:00:00+05:30',
    as_of_utc: '2026-07-27T06:30:00Z',
    evidence_cutoff_utc: '2026-07-27T06:30:00Z',
    timezone: 'Asia/Kolkata',
    location: {
      latitude: 28.6139,
      longitude: 77.209,
      timezone: 'Asia/Kolkata',
      altitude_m: 0,
    },
    foundation_snapshot: {
      snapshot_id: 'foundation-m7',
      profile_id: 'sbc_foundation_v1',
      profile_hash: 'sha256:foundation',
      astronomy_contract: 'SWISSEPH_SIDEREAL_RAMAN_V1',
      panchanga: {
        tithi_name: 'Trayodashi',
        tithi_group: 'Jaya',
        paksha: 'Shukla',
        moon_phase: 'waxing',
        yoga_name: 'Siddha',
        karana_name: 'Taitila',
        vara: {
          weekday: 'Monday',
          weekday_lord: 'MOON',
        },
      },
    },
    grid: {
      grid_profile_id: 'sbc_81_rotation_normalized_partial_v1',
      profile_hash: 'sha256:grid',
      rows: 9,
      columns: 9,
      cells: [],
      certified_layers: [],
      complete: false,
      blocked_capabilities: [],
    },
    context_contract: 'SBC_CURRENT_MOMENT_CONTEXT_V1',
    target_context: [{
      layer: 'NAKSHATRA',
      values: ['Punarvasu'],
    }],
    position_context: [{
      body: 'SUN',
      longitude_deg: 100,
      longitude_speed_deg_per_day: 0.96,
      rashi: 'CANCER',
      nakshatras: ['Pushya'],
    }],
    actor_readiness: [{
      body: 'SUN',
      requested: true,
      status: 'READY',
      source_nakshatra: 'Pushya',
      motion_class: 'MEAN',
      reason: 'Fixed-body actor available for the visual study.',
    }],
    guidance: null,
    source_ids: ['fixture-m7'],
    guardrails: {
      read_only: true,
      timestamp_safe: true,
      no_lookahead: true,
      execution_allowed: false,
      market_data_included: false,
      financially_validated: false,
      guidance_only: true,
    },
  }
}

describe('M7 collective visual study', () => {
  it('builds a fixed-body SBC request at the selected IST moment', () => {
    const request = createCollectiveStudySbcRequest({
      selectedTimeUnix,
      latitude: 28.6139,
      longitude: 77.209,
    })

    expect(request.at).toBe('2026-07-27T12:00:00+05:30')
    expect(request.actors.map((actor) => actor.body)).toEqual([
      'SUN',
      'MOON',
      'RAHU',
      'KETU',
    ])
    expect(request.bodies).toHaveLength(9)
  })

  it('freezes an export-only non-voting dossier without outcome labels', async () => {
    const dossier = await createCollectiveVisualStudyDossier({
      audit: audit(),
      drawings: [gannFan(), gannFan(false)],
      sbcSnapshot: sbcSnapshot(),
      createdAtUtc: '2026-07-27T06:31:00Z',
    })

    expect(dossier.gannStudy.fanCount).toBe(1)
    expect(dossier.sbcStudy.actorScope).toBe('SUN_MOON_RAHU_KETU_ONLY')
    expect(dossier.prospectiveFreeze.packetFrozen).toBe(true)
    expect(dossier.prospectiveFreeze.trialRegistered).toBe(false)
    expect(dossier.prospectiveFreeze.existingShadowTrialModified).toBe(false)
    expect(dossier.guardrails.directionalContribution).toBe(0)
    expect(dossier.guardrails.consumedByLiveInference).toBe(false)
    expect(dossier.studyFingerprintSha256).toMatch(/^[A-F0-9]{64}$/)
    expect(collectiveVisualStudyFileName(dossier)).toContain(
      'USDJPY_H1_avg_all_m7_visual_study_',
    )
  })

  it('rejects lookahead or execution-enabled SBC evidence', async () => {
    const unsafe = sbcSnapshot()
    unsafe.guardrails.execution_allowed = true as false

    await expect(createCollectiveVisualStudyDossier({
      audit: audit(),
      drawings: [gannFan()],
      sbcSnapshot: unsafe,
    })).rejects.toThrow('violated timestamp or research guardrails')
  })
})
