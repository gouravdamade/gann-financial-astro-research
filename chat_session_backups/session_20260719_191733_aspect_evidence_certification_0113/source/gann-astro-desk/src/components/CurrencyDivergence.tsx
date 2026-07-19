import { currencyDivergenceModel } from '../currencyEvidence'
import type { CurrencyPairEvidence } from '../types'

type CurrencyDivergenceProps = {
  evidence: CurrencyPairEvidence
}

export function CurrencyDivergence({ evidence }: CurrencyDivergenceProps) {
  const model = currencyDivergenceModel(evidence)
  return (
    <div className="currency-divergence" aria-label={`${evidence.base.label} versus ${evidence.quote.label} divergence`}>
      <header>
        <strong>Currency divergence</strong>
        <span>stressful <i /> supportive</span>
      </header>
      <div className="currency-divergence-bars">
        {model.bars.map((bar) => (
          <div className="currency-divergence-row" key={bar.label}>
            <strong>{bar.label}</strong>
            <div className="currency-divergence-track">
              <i className="currency-divergence-zero" />
              <span
                className={bar.tone}
                style={{ left: `${bar.leftPct}%`, width: `${bar.widthPct}%` }}
              />
            </div>
            <em>{bar.score == null ? '-' : `${bar.score > 0 ? '+' : ''}${bar.score.toFixed(3)}`}</em>
          </div>
        ))}
      </div>
      <footer>
        <span>{model.pairDirection}</span>
        <strong>{model.pairScore == null ? 'no pair score' : `${model.pairScore > 0 ? '+' : ''}${model.pairScore.toFixed(3)} base-minus-quote`}</strong>
        <small>{model.conflictPct == null ? 'conflict unavailable' : `${model.conflictPct.toFixed(1)}% conflict`}</small>
      </footer>
    </div>
  )
}
