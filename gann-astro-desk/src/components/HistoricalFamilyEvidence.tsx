import type { HistoricalFamilySummary } from '../types'

type HistoricalFamilyEvidenceProps = {
  summary: HistoricalFamilySummary
}

function percent(value: number | null, signed = false): string {
  if (value == null) return '-'
  return `${signed && value > 0 ? '+' : ''}${value.toFixed(3)}%`
}

export function HistoricalFamilyEvidence({ summary }: HistoricalFamilyEvidenceProps) {
  const bullishWidth = summary.bullishRatePct ?? 0
  return (
    <div className="historical-family-evidence">
      <header>
        <div>
          <strong>Prior family behavior</strong>
          <span>{summary.priorOccurrenceCount} prior; {summary.labeledCount} matured labels</span>
        </div>
        <em className={summary.directionalBias}>{summary.directionalBias}</em>
      </header>
      {summary.labeledCount > 0 ? (
        <>
          <div className="family-rate-bar" aria-label={`${summary.bullishRatePct}% bullish and ${summary.bearishRatePct}% bearish`}>
            <span className="bullish" style={{ width: `${bullishWidth}%` }} />
            <span className="bearish" style={{ width: `${100 - bullishWidth}%` }} />
          </div>
          <div className="family-rate-labels">
            <span>{summary.bullishRatePct?.toFixed(1)}% bullish ({summary.bullish})</span>
            <span>{summary.bearishRatePct?.toFixed(1)}% bearish ({summary.bearish})</span>
          </div>
        </>
      ) : (
        <p>No fully matured prior touch outcomes existed at this event cutoff.</p>
      )}
      <dl>
        <div><dt>Median 72h return</dt><dd>{percent(summary.medianReturnPct, true)}</dd></div>
        <div><dt>Median upside excursion</dt><dd>{percent(summary.medianUpsideExcursionPct, true)}</dd></div>
        <div><dt>Median downside excursion</dt><dd>{percent(summary.medianDownsideExcursionPct, true)}</dd></div>
        <div><dt>Bias-conditioned MFE</dt><dd>{percent(summary.medianFavorableExcursionPct)}</dd></div>
        <div><dt>Bias-conditioned MAE</dt><dd>{percent(summary.medianAdverseExcursionPct)}</dd></div>
      </dl>
      <footer>
        {summary.excursionSampleCount} touch-close anchored 72h samples. As of {new Date(summary.asOf).toLocaleString()}.
        Retrospective only; never consumed by live inference.
      </footer>
    </div>
  )
}
