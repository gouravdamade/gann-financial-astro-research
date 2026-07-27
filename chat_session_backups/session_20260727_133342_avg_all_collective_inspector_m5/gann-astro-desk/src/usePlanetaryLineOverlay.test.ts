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
        guardrails: {
          sampledTimingOnly: true,
          prospectiveFreezePerformed: false,
          researchOnly: true,
          executionAllowed: false,
        },
      },
      events: [
        {
          contract: 'GANN_PLANETARY_COLLECTIVE_EVENT_V1',
          timing: { exact: false },
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
  it('accepts sampled context-only collective events', () => {
    expect(() => {
      assertPlanetaryLineOverlayResearchContract(validOverlay())
    }).not.toThrow()
  })

  it('rejects an event that claims an exact timestamp', () => {
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
