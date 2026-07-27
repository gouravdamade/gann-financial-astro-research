import { describe, expect, it } from 'vitest'
import type { PlanetaryLineOverlay } from './types'
import { assertPlanetaryLineOverlayResearchContract } from './usePlanetaryLineOverlay'

function validOverlay(): PlanetaryLineOverlay {
  return {
    contract: 'GANN_EXPLORATORY_PLANETARY_LINE_OVERLAY_V1',
    guardrails: {
      researchOnly: true,
      curveFitExploration: true,
      exactBarTimestamps: true,
      consumedByLiveInference: false,
      consumedByAutoSuggest: false,
      consumedByShadowLedger: false,
      executionAllowed: false,
    },
    collectiveField: {
      contract: 'GANN_PLANETARY_COLLECTIVE_FIELD_V1',
      profile: {
        members: ['SUN'],
      },
      samples: [
        {
          memberAudit: [
            {
              body: 'SUN',
              longitudeDeg: 120,
              weight: 1,
              angularDistanceFromMeanDeg: 0,
              longitudeLeverageDeg: 0,
              coherenceLeverage: 0,
              influenceRank: 1,
            },
          ],
        },
      ],
      latest: {
        memberAudit: [
          {
            body: 'SUN',
            longitudeLeverageDeg: 0,
            coherenceLeverage: 0,
          },
        ],
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
      motion: {
        contract: 'GANN_PLANETARY_COLLECTIVE_MOTION_V1',
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
        guardrails: {
          countsAsIndependentVote: false,
          directionalContribution: 0,
          consumedByLiveInference: false,
          consumedByAutoSuggest: false,
          consumedByShadowLedger: false,
          consumedByOfficialMlNotes: false,
          executionAllowed: false,
        },
      },
      eventSummary: {
        contract: 'GANN_PLANETARY_COLLECTIVE_EVENT_SUMMARY_V1',
        eventCount: 1,
        refinement: {
          contract: 'GANN_PLANETARY_COLLECTIVE_EVENT_REFINEMENT_V1',
          candidateCount: 0,
          candidateBudget: 64,
          attemptedCount: 0,
          skippedBudgetCount: 0,
          refinedCount: 0,
          fallbackCount: 0,
          guardrails: {
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
          prospectiveFreezePerformed: false,
          researchOnly: true,
          executionAllowed: false,
        },
      },
      events: [
        {
          contract: 'GANN_PLANETARY_COLLECTIVE_EVENT_V1',
          eventType: 'CLUSTER_STATE_TRANSITION',
          estimatedTimeUnix: 1_700_000_000,
          refinedTimeUnix: null,
          sourceBracket: {
            startUnix: 1_700_000_000,
            endUnix: 1_700_003_600,
          },
          timing: {
            exact: false,
            method: 'RIGHT_SAMPLE_STATE_OBSERVATION',
            precision: 'BETWEEN_EXACT_BAR_SAMPLES',
          },
          refinement: null,
          guardrails: {
            exactEventTime: false,
            directionalContribution: 0,
            castsSbcVedha: false,
            consumedByLiveInference: false,
            consumedByAutoSuggest: false,
            consumedByShadowLedger: false,
            consumedByOfficialMlNotes: false,
            executionAllowed: false,
          },
        },
      ],
      evidence: {
        contract: 'GANN_RESEARCH_EVIDENCE_PACKET_V1',
        empiricalCoefficient: 0,
        guardrails: {
          consumedByLiveInference: false,
          consumedByAutoSuggest: false,
          consumedByShadowLedger: false,
          consumedByOfficialMlNotes: false,
          executionAllowed: false,
        },
      },
    },
  } as unknown as PlanetaryLineOverlay
}

describe('planetary collective response guardrails', () => {
  it('accepts mixed sampled context-only collective events', () => {
    expect(() => {
      assertPlanetaryLineOverlayResearchContract(validOverlay())
    }).not.toThrow()
  })

  it('accepts a bracketed ephemeris ingress root without promoting it', () => {
    const overlay = validOverlay()
    const event = overlay.collectiveField?.events[0]
    if (!event) throw new Error('missing fixture event')
    Object.assign(event, {
      eventType: 'MEAN_RASHI_INGRESS',
      refinedTimeUnix: 1_700_001_800,
      timing: {
        exact: true,
        method: 'BRACKETED_BISECTION_OF_EPHEMERIS_MEAN',
        precision: 'WITHIN_DECLARED_TIME_AND_ANGULAR_TOLERANCE',
        sampledEstimateUnix: 1_700_001_700,
        rootToleranceSeconds: 1,
        residualToleranceDeg: 0.001,
      },
      refinement: {
        contract: 'GANN_PLANETARY_COLLECTIVE_EVENT_REFINEMENT_V1',
        policyId: 'AVG_ALL_EPHEMERIS_ROOT_REFINEMENT_V1',
        status: 'REFINED_BRACKETED_ROOT',
        sampledEstimateUnix: 1_700_001_700,
        refinedTimeUnix: 1_700_001_800,
        rootToleranceSeconds: 1,
        residualToleranceDeg: 0.001,
        residualDeg: 0.0001,
        coherenceR1AtRoot: 0.5,
        iterations: 12,
        evaluatedTimestampCount: 14,
        reason: 'fixture',
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
      guardrails: {
        ...event.guardrails,
        exactEventTime: true,
      },
    })
    Object.assign(overlay.collectiveField?.eventSummary.refinement ?? {}, {
      candidateCount: 1,
      attemptedCount: 1,
      refinedCount: 1,
      fallbackCount: 0,
    })

    expect(() => {
      assertPlanetaryLineOverlayResearchContract(overlay)
    }).not.toThrow()
  })

  it('rejects an event that merely claims an exact timestamp', () => {
    const overlay = validOverlay()
    Object.assign(overlay.collectiveField?.events[0].timing ?? {}, { exact: true })

    expect(() => {
      assertPlanetaryLineOverlayResearchContract(overlay)
    }).toThrow('AVG collective geometry violated its context-only contract')
  })

  it('rejects shadow-ledger consumption at either contract layer', () => {
    const overlay = validOverlay()
    Object.assign(overlay.collectiveField?.evidence.guardrails ?? {}, {
      consumedByShadowLedger: true,
    })

    expect(() => {
      assertPlanetaryLineOverlayResearchContract(overlay)
    }).toThrow('AVG collective geometry violated its context-only contract')
  })

  it('rejects unsafe influence consumption', () => {
    const overlay = validOverlay()
    Object.assign(overlay.collectiveField?.influence.guardrails ?? {}, {
      consumedByAutoSuggest: true,
    })

    expect(() => {
      assertPlanetaryLineOverlayResearchContract(overlay)
    }).toThrow('AVG collective geometry violated its context-only contract')
  })

  it('rejects a malformed historical member audit', () => {
    const overlay = validOverlay()
    const sample = overlay.collectiveField?.samples[0]
    if (sample) sample.memberAudit[0].longitudeLeverageDeg = Number.NaN

    expect(() => {
      assertPlanetaryLineOverlayResearchContract(overlay)
    }).toThrow('AVG collective geometry violated its context-only contract')
  })
})
