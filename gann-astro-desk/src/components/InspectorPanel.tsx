import { ArrowUpRight, CalendarRange, CheckCircle2, CircleDot, Microscope } from 'lucide-react'
import type { AspectWindow, ChartAnnotation, EventDetail } from '../types'

type InspectorPanelProps = {
  selected: AspectWindow | null
  detail: EventDetail | null
  annotation: ChartAnnotation | null
  onAnalyze: () => void
  onAnnotationNoteChange: (value: string) => void
  onSaveAnnotation: () => void
}

export function InspectorPanel({
  selected,
  detail,
  annotation,
  onAnalyze,
  onAnnotationNoteChange,
  onSaveAnnotation,
}: InspectorPanelProps) {
  if (!selected) {
    return (
      <aside className="inspector-panel empty-panel">
        <CircleDot size={22} />
        <strong>Select an aspect</strong>
        <span>Click a colored aspect ribbon or an event row.</span>
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
        <span className="aspect-status" style={{ borderColor: selected.color }}>{selected.occurrenceCount}x</span>
      </header>
      <button className="primary-command" onClick={onAnalyze}>
        <Microscope size={17} />
        Analyze Aspect
        <ArrowUpRight size={15} />
      </button>
      <section className="inspector-section">
        <div className="section-title"><CalendarRange size={15} /> Window</div>
        <dl className="property-grid">
          <dt>Starts</dt><dd>{new Date(selected.start * 1000).toLocaleString()}</dd>
          <dt>Ends</dt><dd>{new Date(selected.end * 1000).toLocaleString()}</dd>
          <dt>Peak orb</dt><dd>{selected.peakOrbDeg.toFixed(4)} deg</dd>
          <dt>Source case</dt><dd>{selected.caseId ?? 'not touched'}</dd>
          <dt>Review</dt><dd>{selected.reviewed ? 'complete' : 'pending'}</dd>
        </dl>
      </section>
      <section className="inspector-section">
        <div className="section-title"><CheckCircle2 size={15} /> Evidence preview</div>
        {detail?.astroEvidence.slice(0, 6).map((item) => (
          <div className="evidence-row" key={item.key}>
            <span>{item.label}</span>
            <strong>{typeof item.value === 'number' ? item.value.toFixed(2) : item.value}</strong>
          </div>
        ))}
        {!detail && <span className="muted">Loading deterministic context...</span>}
      </section>
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
