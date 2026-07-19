import {
  ArrowUpRight,
  BrainCircuit,
  CalendarRange,
  CheckCircle2,
  ChevronDown,
  ChevronUp,
  CircleDot,
  Gauge,
  Microscope,
  Scale,
} from 'lucide-react'
import { useEffect, useState } from 'react'
import type { AspectWindow, ChartAnnotation, EventDetail } from '../types'

type InspectorPanelProps = {
  selected: AspectWindow | null
  detail: EventDetail | null
  annotation: ChartAnnotation | null
  detailsRequestNonce: number
  onAnalyze: () => void
  onAnnotationNoteChange: (value: string) => void
  onSaveAnnotation: () => void
}

function evidenceValue(value: string | number, unit: string): string {
  const formatted = typeof value === 'number' ? value.toFixed(3) : value
  return unit === 'text' ? String(formatted) : `${formatted} ${unit}`
}

function scoreTone(value: number | null): string {
  if (value == null || Math.abs(value) < 1e-9) return 'mixed / unavailable'
  return value > 0 ? 'supportive' : 'stressful'
}

export function InspectorPanel({
  selected,
  detail,
  annotation,
  detailsRequestNonce,
  onAnalyze,
  onAnnotationNoteChange,
  onSaveAnnotation,
}: InspectorPanelProps) {
  const [detailsOpen, setDetailsOpen] = useState(false)

  useEffect(() => {
    setDetailsOpen(false)
  }, [selected?.eventId])

  useEffect(() => {
    if (detailsRequestNonce > 0) setDetailsOpen(true)
  }, [detailsRequestNonce])

  if (!selected) {
    return (
      <aside className="inspector-panel empty-panel">
        <CircleDot size={22} />
        <strong>No aspect selected</strong>
        <span>No corrected aspect overlaps this chart range.</span>
      </aside>
    )
  }
  return (
    <aside className="inspector-panel">
      <header className="inspector-header">
        <div>
          <span className="eyebrow">Selected aspect</span>
          <h2>{selected.transitBody} to {selected.natalBody}</h2>
          <p>{selected.aspectLabel}</p>
        </div>
        <span className="aspect-status" style={{ borderColor: selected.color }}>
          {selected.knownPriorCount} prior
        </span>
      </header>
      <div className="inspector-actions">
        <button className="primary-command" onClick={onAnalyze}>
          <Microscope size={17} />
          Review Aspect
          <ArrowUpRight size={15} />
        </button>
        <button
          className="secondary-command"
          onClick={() => setDetailsOpen((current) => !current)}
          aria-expanded={detailsOpen}
        >
          <Gauge size={15} />
          Details
          {detailsOpen ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
        </button>
      </div>
      <section className="inspector-section">
        <div className="section-title"><CalendarRange size={15} /> Window</div>
        <dl className="property-grid">
          <dt>Starts</dt><dd>{new Date(selected.start * 1000).toLocaleString()}</dd>
          <dt>Ends</dt><dd>{new Date(selected.end * 1000).toLocaleString()}</dd>
          <dt>Duration</dt><dd>{Math.round(selected.durationMinutes)} minutes</dd>
          <dt>Peak orb</dt><dd>{selected.peakOrbDeg.toFixed(4)} / {selected.orbLimitDeg.toFixed(4)} deg</dd>
          <dt>Loaded range</dt><dd>{selected.occurrenceIndex ?? '-'} of {selected.occurrenceCount}</dd>
          <dt>Known history</dt><dd>{selected.knownPriorCount} prior / {selected.knownOccurrenceCount} total</dd>
          <dt>Source case</dt><dd>{selected.caseId ?? 'not touched'}</dd>
          <dt>Review</dt><dd>{selected.reviewed ? 'complete' : 'pending'}</dd>
        </dl>
      </section>
      {!detailsOpen && (
        <section className="inspector-section">
          <div className="section-title"><CheckCircle2 size={15} /> Evidence preview</div>
          {detail?.astroEvidence.slice(0, 6).map((item) => (
            <div className="evidence-row" key={item.key}>
              <span>{item.label}</span>
              <strong>{evidenceValue(item.value, item.unit)}</strong>
            </div>
          ))}
          {!detail && <span className="muted">Loading deterministic context...</span>}
        </section>
      )}
      {detailsOpen && (
        <>
          <section className="inspector-section">
            <div className="section-title"><Scale size={15} /> Family recurrence</div>
            {detail ? (
              <dl className="property-grid">
                <dt>Total</dt><dd>{detail.familySummary.total}</dd>
                <dt>Reviewed</dt><dd>{detail.familySummary.reviewed} of {detail.familySummary.total}</dd>
                <dt>Observed</dt><dd>{detail.familySummary.bullish} up / {detail.familySummary.bearish} down / {detail.familySummary.unknown} unknown</dd>
                <dt>Avg 72h</dt><dd>{detail.familySummary.averageReturnPct == null ? 'not available' : `${detail.familySummary.averageReturnPct > 0 ? '+' : ''}${detail.familySummary.averageReturnPct.toFixed(3)}%`}</dd>
              </dl>
            ) : <span className="muted">Loading recurrence evidence...</span>}
            <p className="inspector-boundary">Observed outcomes are retrospective labels, not live inputs.</p>
          </section>
          <section className="inspector-section">
            <div className="section-title"><Gauge size={15} /> Astrology evidence</div>
            {detail?.astroEvidence.map((item) => (
              <div className="evidence-row" key={item.key}>
                <span>{item.label}<small>{item.certification}</small></span>
                <strong>{evidenceValue(item.value, item.unit)}</strong>
              </div>
            ))}
            {!detail && <span className="muted">Loading deterministic context...</span>}
          </section>
          {detail?.currencyPairEvidence && (
            <section className="inspector-section">
              <div className="section-title"><Scale size={15} /> Forex pair evidence</div>
              <div className="currency-evidence-heading">
                <strong>{detail.currencyPairEvidence.base.label}</strong>
                <span>base minus quote</span>
                <strong>{detail.currencyPairEvidence.quote.label}</strong>
              </div>
              <div className="currency-side-evidence">
                <div>
                  <strong>{detail.currencyPairEvidence.base.label}</strong>
                  <small>{detail.currencyPairEvidence.base.referenceLabel}</small>
                  <span>{scoreTone(detail.currencyPairEvidence.base.doctrineNetScore)}</span>
                  <dl>
                    <dt>Raw score</dt><dd>{detail.currencyPairEvidence.base.netScore?.toFixed(3) ?? '-'}</dd>
                    <dt>Doctrine</dt><dd>{detail.currencyPairEvidence.base.doctrineNetScore?.toFixed(3) ?? '-'}</dd>
                    <dt>Hits</dt><dd>{detail.currencyPairEvidence.base.scoredHitCount ?? 0}</dd>
                    <dt>Dominant</dt><dd>{detail.currencyPairEvidence.base.doctrineDominantHit || detail.currencyPairEvidence.base.dominantHit || '-'}</dd>
                    <dt>Dignity</dt><dd>{detail.currencyPairEvidence.base.doctrineDominantDignity || '-'}</dd>
                  </dl>
                </div>
                <div>
                  <strong>{detail.currencyPairEvidence.quote.label}</strong>
                  <small>{detail.currencyPairEvidence.quote.referenceLabel}</small>
                  <span>{scoreTone(detail.currencyPairEvidence.quote.doctrineNetScore)}</span>
                  <dl>
                    <dt>Raw score</dt><dd>{detail.currencyPairEvidence.quote.netScore?.toFixed(3) ?? '-'}</dd>
                    <dt>Doctrine</dt><dd>{detail.currencyPairEvidence.quote.doctrineNetScore?.toFixed(3) ?? '-'}</dd>
                    <dt>Hits</dt><dd>{detail.currencyPairEvidence.quote.scoredHitCount ?? 0}</dd>
                    <dt>Dominant</dt><dd>{detail.currencyPairEvidence.quote.doctrineDominantHit || detail.currencyPairEvidence.quote.dominantHit || '-'}</dd>
                    <dt>Dignity</dt><dd>{detail.currencyPairEvidence.quote.doctrineDominantDignity || '-'}</dd>
                  </dl>
                </div>
              </div>
              <dl className="property-grid pair-balance">
                <dt>Direction</dt><dd>{detail.currencyPairEvidence.pair.doctrineDirection ?? 'UNKNOWN'}</dd>
                <dt>Pair score</dt><dd>{detail.currencyPairEvidence.pair.doctrineNetScore?.toFixed(3) ?? '-'}</dd>
                <dt>Conflict</dt><dd>{detail.currencyPairEvidence.pair.doctrineConflictRatio == null ? '-' : `${(detail.currencyPairEvidence.pair.doctrineConflictRatio * 100).toFixed(1)}%`}</dd>
              </dl>
              <p className="inspector-boundary">Provisional research scoring. Both currencies are shown; no trade is authorized here.</p>
            </section>
          )}
          <section className="inspector-section inspector-llm-boundary">
            <div className="section-title"><BrainCircuit size={15} /> Interpretation</div>
            <p>Open Review for local Jyotish guidance, citations, verifier checks, annotations, and the complete recurrence family. LLM prose remains draft evidence until reviewed.</p>
          </section>
        </>
      )}
      {annotation && (
        <section className="inspector-section annotation-editor">
          <div className="section-title">Selected annotation</div>
          <div className="annotation-coordinate">
            {new Date(annotation.anchorTimeUtc).toLocaleString()} @ {annotation.anchorPrice?.toFixed(3)}
          </div>
          <textarea
            value={annotation.note}
            onChange={(event) => onAnnotationNoteChange(event.target.value)}
            aria-label="Annotation note"
          />
          <button className="secondary-command" onClick={onSaveAnnotation}>Save annotation</button>
        </section>
      )}
      <footer className="contract-footer" title={selected.astronomyContract}>
        <span className="status-dot" /> Raman TN v2
      </footer>
    </aside>
  )
}
