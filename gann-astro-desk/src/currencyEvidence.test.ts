import { describe, expect, it } from 'vitest'
import { currencyDivergenceModel } from './currencyEvidence'
import type { CurrencyPairEvidence } from './types'

function evidence(base: number | null, quote: number | null): CurrencyPairEvidence {
  return {
    contract: 'GANN_FX_PAIR_EVIDENCE_V2',
    status: 'provisional_research_only',
    profileId: 'fx_doctrine_consensus_watch_only_v1',
    asOfUtc: '2026-08-01T00:00:00+00:00',
    evidenceCutoffUtc: '2026-08-01T00:00:00+00:00',
    mappingIdentity: 'USD:USD|JPY:JPY',
    base: {
      label: 'USD', referenceLabel: 'USD', netScore: base, doctrineNetScore: base,
      state: 'KNOWN', supportiveUnits: 2, adverseUnits: 0, netUnits: base, grossActivationUnits: 2,
      conflictRatio: 0, eligibleCount: 2, scoredHitCount: 2, unresolvedCount: 0, unknownCoverage: 0,
      dominantHit: null, doctrineDominantHit: null,
      doctrineDominantDignity: null, doctrineDignityVirupaAvg: null,
    },
    quote: {
      label: 'JPY', referenceLabel: 'JPY', netScore: quote, doctrineNetScore: quote,
      state: 'KNOWN', supportiveUnits: 0, adverseUnits: 2, netUnits: quote, grossActivationUnits: 2,
      conflictRatio: 0, eligibleCount: 2, scoredHitCount: 2, unresolvedCount: 0, unknownCoverage: 0,
      dominantHit: null, doctrineDominantHit: null,
      doctrineDominantDignity: null, doctrineDignityVirupaAvg: null,
    },
    pair: {
      state: 'KNOWN', netDifferenceUnits: 3, jointNetStrengthUnits: 1.5, commonActivationUnits: 2, grossActivationUnits: 4,
      netScore: 3, conflictRatio: 0.25, conflictRatioLegacy: 0.25, direction: 'BULLISH',
      doctrineNetScore: 3, doctrineConflictRatio: 0.25, doctrineDirection: 'BULLISH',
    },
    notes: null,
  }
}

describe('currencyDivergenceModel', () => {
  it('places supportive and stressful scores on opposite sides of zero', () => {
    const model = currencyDivergenceModel(evidence(2, -1))
    expect(model.bars[0]).toMatchObject({ tone: 'supportive', leftPct: 50, widthPct: 50 })
    expect(model.bars[1]).toMatchObject({ tone: 'stressful', leftPct: 25, widthPct: 25 })
    expect(model.pairDirection).toBe('BULLISH')
    expect(model.conflictPct).toBe(25)
  })

  it('keeps missing evidence neutral without inventing a score', () => {
    const model = currencyDivergenceModel(evidence(null, null))
    expect(model.bars.every((bar) => bar.tone === 'neutral' && bar.widthPct === 0)).toBe(true)
  })
})
