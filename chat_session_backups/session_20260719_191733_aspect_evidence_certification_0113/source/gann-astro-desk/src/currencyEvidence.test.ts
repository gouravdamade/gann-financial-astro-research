import { describe, expect, it } from 'vitest'
import { currencyDivergenceModel } from './currencyEvidence'
import type { CurrencyPairEvidence } from './types'

function evidence(base: number | null, quote: number | null): CurrencyPairEvidence {
  return {
    contract: 'GANN_FX_PAIR_EVIDENCE_V1',
    status: 'provisional_research_only',
    base: {
      label: 'USD', referenceLabel: 'USD', netScore: base, doctrineNetScore: base,
      scoredHitCount: 2, dominantHit: null, doctrineDominantHit: null,
      doctrineDominantDignity: null, doctrineDignityVirupaAvg: null,
    },
    quote: {
      label: 'JPY', referenceLabel: 'JPY', netScore: quote, doctrineNetScore: quote,
      scoredHitCount: 2, dominantHit: null, doctrineDominantHit: null,
      doctrineDominantDignity: null, doctrineDignityVirupaAvg: null,
    },
    pair: {
      netScore: 3, conflictRatio: 0.25, direction: 'BULLISH',
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
