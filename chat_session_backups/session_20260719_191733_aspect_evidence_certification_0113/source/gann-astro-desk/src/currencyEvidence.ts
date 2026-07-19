import type { CurrencyPairEvidence } from './types'

export type CurrencyDivergenceBar = {
  label: string
  score: number | null
  leftPct: number
  widthPct: number
  tone: 'supportive' | 'stressful' | 'neutral'
}

export type CurrencyDivergenceModel = {
  bars: [CurrencyDivergenceBar, CurrencyDivergenceBar]
  pairScore: number | null
  pairDirection: string
  conflictPct: number | null
}

function finiteScore(value: number | null | undefined): number | null {
  return typeof value === 'number' && Number.isFinite(value) ? value : null
}

export function currencyDivergenceModel(
  evidence: CurrencyPairEvidence,
): CurrencyDivergenceModel {
  const baseScore = finiteScore(evidence.base.doctrineNetScore ?? evidence.base.netScore)
  const quoteScore = finiteScore(evidence.quote.doctrineNetScore ?? evidence.quote.netScore)
  const scale = Math.max(1, Math.abs(baseScore ?? 0), Math.abs(quoteScore ?? 0))
  const bar = (label: string, score: number | null): CurrencyDivergenceBar => {
    const magnitude = score == null ? 0 : Math.min(50, (Math.abs(score) / scale) * 50)
    return {
      label,
      score,
      leftPct: score != null && score < 0 ? 50 - magnitude : 50,
      widthPct: magnitude,
      tone: score == null || Math.abs(score) < 1e-9
        ? 'neutral'
        : score > 0
          ? 'supportive'
          : 'stressful',
    }
  }
  return {
    bars: [
      bar(evidence.base.label, baseScore),
      bar(evidence.quote.label, quoteScore),
    ],
    pairScore: finiteScore(evidence.pair.doctrineNetScore ?? evidence.pair.netScore),
    pairDirection: evidence.pair.doctrineDirection ?? evidence.pair.direction ?? 'UNKNOWN',
    conflictPct: evidence.pair.doctrineConflictRatio == null
      ? evidence.pair.conflictRatio == null
        ? null
        : evidence.pair.conflictRatio * 100
      : evidence.pair.doctrineConflictRatio * 100,
  }
}
