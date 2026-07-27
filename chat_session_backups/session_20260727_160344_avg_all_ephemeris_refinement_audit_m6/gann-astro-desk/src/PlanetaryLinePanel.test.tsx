// @vitest-environment jsdom

import '@testing-library/jest-dom/vitest'
import { cleanup, render, screen } from '@testing-library/react'
import { afterEach, describe, expect, it, vi } from 'vitest'
import { PlanetaryLinePanel } from './components/PlanetaryLinePanel'
import { defaultPlanetaryLineOverlaySettings } from './planetaryLines'
import type { PlanetaryCollectiveField } from './types'

afterEach(cleanup)

const collectiveField: PlanetaryCollectiveField = {
  contract: 'GANN_PLANETARY_COLLECTIVE_FIELD_V1',
  calculationVersion: 'AVG_ALL_CIRCULAR_GEOMETRY_V1',
  profile: {
    profileId: 'AVG_ALL_TEN_BODY_EQUAL_WEIGHT_V1',
    members: ['SUN', 'MOON'],
    weights: [0.5, 0.5],
    nodePolicy: 'RAHU_KETU_EXCLUDED',
    memberSetHash: 'sha256:test',
    thresholdProfile: {
      profileId: 'AVG_ALL_DISPLAY_RELIABILITY_V1',
      classification: 'UI_HEURISTIC_RESEARCH_ONLY',
      unstableResultantFloor: 1e-8,
      lowCoherenceFloor: 0.2,
      concentratedFloor: 0.65,
      bipolarR2Floor: 0.55,
    },
  },
  samples: [],
  latest: {
    time: 1_700_000_000,
    meanLongitudeDeg: 147.82,
    coherenceR1: 0.712,
    circularVariance: 0.288,
    circularStdDeg: 47.15,
    polarisationR2: 0.341,
    polarisationAxisDeg: 62.4,
    state: 'CONCENTRATED',
    reliability: 'RELIABLE',
    longitudeReliable: true,
    segmentId: 1,
    unwrappedLongitudeDeg: 147.82,
    velocityDegPerDay: 0.72,
    accelerationDegPerDay2: null,
    memberAudit: [
      {
        body: 'SUN',
        longitudeDeg: 140,
        weight: 0.5,
        angularDistanceFromMeanDeg: 7.82,
        longitudeLeverageDeg: 7.82,
        coherenceLeverage: -0.1,
        tempoClass: 'FAST_MOVING_CLASS',
        role: 'DISPERSING_FAST_DRIVER',
        influenceRank: 1,
      },
      {
        body: 'MOON',
        longitudeDeg: 155.64,
        weight: 0.5,
        angularDistanceFromMeanDeg: 7.82,
        longitudeLeverageDeg: 7.82,
        coherenceLeverage: -0.1,
        tempoClass: 'FAST_MOVING_CLASS',
        role: 'DISPERSING_FAST_DRIVER',
        influenceRank: 2,
      },
    ],
  },
  motion: {
    contract: 'GANN_PLANETARY_COLLECTIVE_MOTION_V1',
    calculationVersion: 'RELIABILITY_SAFE_CIRCULAR_MOTION_V1',
    segmentCount: 1,
    reliableSampleCount: 300,
    velocitySampleCount: 300,
    accelerationSampleCount: 298,
    velocityDegPerDay: { minimum: -0.4, maximum: 1.2 },
    accelerationDegPerDay2: { minimum: -0.08, maximum: 0.09 },
    guardrails: {
      reliabilityGapsBreakSegments: true,
      usesExactTimestampDifferences: true,
      bridgesUnreliableSamples: false,
      displaySmoothingApplied: false,
      researchOnly: true,
      executionAllowed: false,
    },
  },
  influence: {
    contract: 'GANN_PLANETARY_COLLECTIVE_INFLUENCE_V1',
    calculationVersion: 'AVG_ALL_LEAVE_ONE_OUT_AUDIT_V1',
    latestTopLongitudeLeverage: null,
    rolePolicy: {
      classification: 'DETERMINISTIC_UI_AUDIT_ONLY',
      fastMovingClass: ['SUN', 'MOON'],
      topFastDriverRankLimit: 3,
      slowAnchorRule: 'test',
    },
    guardrails: {
      researchOnly: true,
      countsAsIndependentVote: false,
      directionalContribution: 0,
      consumedByLiveInference: false,
      consumedByAutoSuggest: false,
      consumedByShadowLedger: false,
      consumedByOfficialMlNotes: false,
      executionAllowed: false,
    },
  },
  events: [],
  eventSummary: {
    contract: 'GANN_PLANETARY_COLLECTIVE_EVENT_SUMMARY_V1',
    eventPolicy: {
      profileId: 'AVG_ALL_SAMPLED_EVENTS_V1',
      timingClassification: 'MIXED_SAMPLED_AND_EPHEMERIS_REFINED',
      lowCoherenceFloor: 0.2,
      concentratedFloor: 0.65,
      detects: [
        'MEAN_RASHI_INGRESS',
        'COHERENCE_THRESHOLD_CROSSING',
        'CLUSTER_STATE_TRANSITION',
      ],
      doesNotDetectYet: [],
    },
    eventCount: 0,
    eventTypeCounts: {},
    refinement: {
      contract: 'GANN_PLANETARY_COLLECTIVE_EVENT_REFINEMENT_V1',
      policyId: 'AVG_ALL_EPHEMERIS_ROOT_REFINEMENT_V1',
      refinableEventTypes: ['MEAN_RASHI_INGRESS'],
      candidateCount: 0,
      candidateBudget: 64,
      attemptedCount: 0,
      skippedBudgetCount: 0,
      refinedCount: 0,
      fallbackCount: 0,
      evaluatedTimestampCount: 0,
      rootToleranceSeconds: 1,
      residualToleranceDeg: 0.001,
      guardrails: {
        researchOnly: true,
        heuristicThresholdEventsRemainSampled: true,
        countsAsIndependentVote: false,
        directionalContribution: 0,
        consumedByLiveInference: false,
        consumedByAutoSuggest: false,
        consumedByShadowLedger: false,
        consumedByOfficialMlNotes: false,
        executionAllowed: false,
      },
    },
    guardrails: {
      sampledTimingOnly: false,
      exactRootsLimitedTo: ['MEAN_RASHI_INGRESS'],
      prospectiveFreezePerformed: false,
      researchOnly: true,
      executionAllowed: false,
    },
  },
  summary: {
    sampleCount: 300,
    reliabilityCounts: { RELIABLE: 284, LOW_COHERENCE: 16 },
    stateCounts: { CONCENTRATED: 284, DISPERSED: 16 },
    coherenceR1: { minimum: 0.14, median: 0.63, maximum: 0.91 },
    polarisationR2: { minimum: 0.08, median: 0.34, maximum: 0.81 },
  },
  evidence: {
    contract: 'GANN_RESEARCH_EVIDENCE_PACKET_V1',
    sourceFamily: 'PLANETARY_COLLECTIVE_GEOMETRY',
    sourceProfileId: 'AVG_ALL_TEN_BODY_EQUAL_WEIGHT_V1',
    calculationVersion: 'AVG_ALL_CIRCULAR_GEOMETRY_V1',
    observedAtUnix: 1_700_000_000,
    role: 'CONTEXT_ONLY',
    channels: {
      direction: { status: 'NOT_APPLICABLE', value: null, unit: null, label: 'Direction', reason: 'No market mapping.' },
      activation: { status: 'NOT_APPLICABLE', value: null, unit: null, label: 'Activation', reason: 'No market mapping.' },
      conflict: { status: 'NOT_APPLICABLE', value: null, unit: null, label: 'Conflict', reason: 'No market mapping.' },
      confidence: { status: 'NOT_APPLICABLE', value: null, unit: null, label: 'Confidence', reason: 'No market mapping.' },
    },
    descriptors: [],
    unknownReasons: [],
    provenance: {},
    empiricalCoefficient: 0,
    guardrails: {
      timestampSafe: true,
      researchOnly: true,
      consumedByLiveInference: false,
      consumedByAutoSuggest: false,
      consumedByShadowLedger: false,
      consumedByOfficialMlNotes: false,
      executionAllowed: false,
    },
  },
  causalClusterPolicy: {
    profileId: 'PLANETARY_GEOMETRY_CAUSAL_CLUSTER_V1',
    description: 'One planetary-geometry source.',
    countsAsIndependentVote: false,
    directionalContribution: 0,
  },
  legacyCompatibility: {
    legacyLineFormulaUnchanged: true,
    legacyLineValuesPreserved: true,
    reliabilityChangesLineVisibility: false,
  },
  guardrails: {
    researchOnly: true,
    contextOnly: true,
    empiricalCoefficient: 0,
    traditionalAuthority: false,
    castsSbcVedha: false,
    directionalContribution: 0,
    consumedByLiveInference: false,
    consumedByAutoSuggest: false,
    consumedByShadowLedger: false,
    consumedByOfficialMlNotes: false,
    executionAllowed: false,
  },
}

describe('PlanetaryLinePanel collective geometry', () => {
  it('shows auditable R1/R2 reliability while preserving the legacy line notice', () => {
    render(
      <PlanetaryLinePanel
        settings={defaultPlanetaryLineOverlaySettings()}
        status="ready"
        error=""
        plottedLineCount={8}
        sampledTimestampCount={300}
        generatedAtUtc="2026-07-27T10:00:00Z"
        collectiveField={collectiveField}
        collectiveInspectorOpen={false}
        onOpenCollectiveInspector={vi.fn()}
        onChange={vi.fn()}
        onRecalculate={vi.fn()}
        onReset={vi.fn()}
        onClose={vi.fn()}
      />,
    )

    expect(screen.getByText('AVG collective geometry')).toBeInTheDocument()
    expect(screen.getByText('CONCENTRATED')).toBeInTheDocument()
    expect(screen.getByText('0.712')).toBeInTheDocument()
    expect(screen.getByText('0.341')).toBeInTheDocument()
    expect(screen.getByText(/284 reliable of 300 samples/)).toBeInTheDocument()
    expect(screen.getByText(/legacy lines unchanged/)).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Open planetary collective field inspector' })).toBeInTheDocument()
  })
})
