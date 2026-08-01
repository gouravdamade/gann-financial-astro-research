import {
  BookOpen,
  CandlestickChart,
  CornerDownLeft,
  LoaderCircle,
  ShieldAlert,
} from 'lucide-react'
import { useEffect, useState } from 'react'
import {
  analyzeWithLocalCandlestick,
  fetchCandlestickEvidence,
  fetchLocalCandlestickHealth,
} from '../api'
import type {
  CandlestickEvidence,
  ChartAnnotation,
  LocalCandlestickDraft,
  LocalCandlestickHealth,
} from '../types'

type CandlestickPanelProps = {
  eventId: string
  selectedAnnotation: ChartAnnotation | null
}

const DEFAULT_QUESTION = 'Explain the focus-bar geometry and event-window candle behavior. Separate observation, prior-trend context, hindsight, empirical limitations, and uncertainty.'

function percentage(value: number): string {
  return `${(value * 100).toFixed(0)}%`
}

function signed(value: number | null | undefined, suffix = ''): string {
  if (value == null) return 'not available'
  return `${value > 0 ? '+' : ''}${value.toFixed(1)}${suffix}`
}

export function CandlestickPanel({ eventId, selectedAnnotation }: CandlestickPanelProps) {
  const [health, setHealth] = useState<LocalCandlestickHealth | null>(null)
  const [evidence, setEvidence] = useState<CandlestickEvidence | null>(null)
  const [question, setQuestion] = useState(DEFAULT_QUESTION)
  const [draft, setDraft] = useState<LocalCandlestickDraft | null>(null)
  const [busy, setBusy] = useState(false)
  const [loadingEvidence, setLoadingEvidence] = useState(true)
  const [error, setError] = useState('')
  const annotationId = selectedAnnotation?.annotationId ?? null

  useEffect(() => {
    let active = true
    setDraft(null)
    setError('')
    setLoadingEvidence(true)
    Promise.all([
      fetchLocalCandlestickHealth(),
      fetchCandlestickEvidence({ eventId, annotationId }),
    ])
      .then(([nextHealth, nextEvidence]) => {
        if (!active) return
        setHealth(nextHealth)
        setEvidence(nextEvidence)
      })
      .catch((reason) => {
        if (active) setError(reason instanceof Error ? reason.message : String(reason))
      })
      .finally(() => {
        if (active) setLoadingEvidence(false)
      })
    return () => { active = false }
  }, [annotationId, eventId])

  const submit = async () => {
    if (!question.trim() || busy || !health?.ready) return
    setBusy(true)
    setError('')
    try {
      const nextDraft = await analyzeWithLocalCandlestick({
        eventId,
        annotationId,
        question: question.trim(),
      })
      setDraft(nextDraft)
      setEvidence(nextDraft.evidence)
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : String(reason))
    } finally {
      setBusy(false)
    }
  }

  const focus = evidence?.focusBar ?? null
  return (
    <section className="local-jyotish-panel candlestick-panel">
      <header className="local-jyotish-header">
        <div><CandlestickChart size={17} /><strong>Candle specialist</strong></div>
        <span className={health?.ready ? 'bridge-ready' : 'bridge-offline'}>
          {health == null ? 'checking' : health.ready ? `${health.model} | isolated corpus` : 'deterministic only'}
        </span>
      </header>
      <div className="local-jyotish-boundary">
        <ShieldAlert size={14} /> Formula evidence is authoritative. Named shapes are hypotheses, not trade signals.
      </div>

      {loadingEvidence && (
        <div className="local-jyotish-thinking"><LoaderCircle className="is-spinning" size={15} /> Measuring closed OHLC bars...</div>
      )}
      {evidence && (
        <div className="candle-evidence">
          <div className="candle-cutoff">
            <span>Evidence cutoff</span>
            <strong>{new Date(evidence.analysisCutoff).toLocaleString()}</strong>
            <small>{evidence.closedBarCountAtCutoff} closed {evidence.timeframe} bars | {evidence.methodologyVersion.replaceAll('_', ' ')}</small>
          </div>
          {focus ? (
            <>
              <div className="candle-focus-header">
                <div><strong>Focus bar</strong><span>{new Date(focus.startTime).toLocaleString()}</span></div>
                <span className={focus.direction === 'bullish' ? 'positive' : focus.direction === 'bearish' ? 'negative' : ''}>{focus.direction}</span>
              </div>
              <dl className="candle-ohlc-grid">
                <div><dt>Open</dt><dd>{focus.open.toFixed(3)}</dd></div>
                <div><dt>High</dt><dd>{focus.high.toFixed(3)}</dd></div>
                <div><dt>Low</dt><dd>{focus.low.toFixed(3)}</dd></div>
                <div><dt>Close</dt><dd>{focus.close.toFixed(3)}</dd></div>
                <div><dt>Body</dt><dd>{focus.bodyPips.toFixed(1)} pips | {percentage(focus.bodyFraction)}</dd></div>
                <div><dt>Wicks</dt><dd>{percentage(focus.upperWickFraction)} upper | {percentage(focus.lowerWickFraction)} lower</dd></div>
                <div><dt>Prior trend</dt><dd>{focus.preTrend} | {signed(focus.preTrendStrengthAtr, ' ATR')}</dd></div>
                <div><dt>ATR14</dt><dd>{focus.atr14Pips.toFixed(1)} pips</dd></div>
              </dl>
              <div className="candle-pattern-list">
                {focus.patterns.map((pattern) => (
                  <div key={`${pattern.name}-${pattern.context}`} className={`candle-pattern is-${pattern.hypothesisBias}`}>
                    <strong>{pattern.name.replaceAll('_', ' ')}</strong>
                    <span>{pattern.context}</span>
                    <small>{pattern.basis}</small>
                  </div>
                ))}
                {!focus.patterns.length && <div className="empty-inline">No named v1 geometry on the focus bar. Raw ratios remain available above.</div>}
              </div>
            </>
          ) : <div className="empty-inline">No bar had closed by the selected cutoff.</div>}
          <div className="candle-window-summary">
            <div><span>Event window</span><strong>{evidence.eventWindow.barCount} bars</strong></div>
            <div><span>Open-to-close</span><strong>{signed(evidence.eventWindow.movePips, ' pips')}</strong></div>
            <div><span>Named geometries</span><strong>{evidence.eventWindow.patterns.length}</strong></div>
          </div>
          <details className="candle-hindsight">
            <summary>Retrospective bars after cutoff</summary>
            <p>{evidence.hindsight.label}</p>
            <div>
              <span>{evidence.hindsight.barCount} bars</span>
              <span>close {signed(evidence.hindsight.closeMoveFromCutoffPips, ' pips')}</span>
              <span>max up {signed(evidence.hindsight.maxUpFromCutoffPips, ' pips')}</span>
              <span>max down {signed(evidence.hindsight.maxDownFromCutoffPips, ' pips')}</span>
            </div>
          </details>
        </div>
      )}

      {!health?.ready && health && (
        <div className="local-jyotish-unavailable">
          <strong>{health.corpusReady ? 'Commentary model offline' : 'Candlestick specialist unavailable - optional corpus not installed'}</strong>
          <span>Deterministic candle evidence above remains available. {health.error}</span>
        </div>
      )}
      <div className="local-jyotish-composer">
        <textarea
          value={question}
          onChange={(event) => setQuestion(event.target.value)}
          disabled={busy}
          aria-label="Candlestick specialist question"
        />
        <button type="button" onClick={submit} disabled={!health?.ready || !question.trim() || busy} title="Draft with isolated candlestick specialist">
          {busy ? <LoaderCircle className="is-spinning" size={16} /> : <CornerDownLeft size={16} />}
        </button>
      </div>
      {error && <div className="local-jyotish-error">{error}</div>}
      {busy && <div className="local-jyotish-thinking"><LoaderCircle className="is-spinning" size={15} /> Retrieving method and empirical evidence...</div>}
      {draft && (
        <div className="local-jyotish-draft">
          <header>
            <strong>Untrusted candle draft</strong>
            <span className={draft.verifier.status === 'pass' ? 'positive' : 'negative'}>
              {draft.verifier.status.replaceAll('_', ' ')} | {draft.model}
            </span>
          </header>
          {draft.verifier.issues.length > 0 && (
            <div className="local-jyotish-verifier">
              {draft.verifier.issues.map((issue) => <span key={issue}>{issue}</span>)}
            </div>
          )}
          {draft.verifier.repairs.length > 0 && (
            <div className="candle-verifier-repair">
              {draft.verifier.repairs.map((repair) => <span key={repair}>{repair}</span>)}
            </div>
          )}
          <p>{draft.text}</p>
          <div className="local-jyotish-citations">
            <strong><BookOpen size={13} /> Retrieved citations</strong>
            {draft.citations.map((citation) => (
              <span key={citation.chunkId} title={`retrieval score ${citation.score}`}>
                [{citation.chunkId}] {citation.title} | {citation.layer.replaceAll('_', ' ')}
              </span>
            ))}
          </div>
          <small>{draft.disclaimer}</small>
        </div>
      )}
    </section>
  )
}
