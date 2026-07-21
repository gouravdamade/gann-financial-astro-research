import {
  Activity,
  ChevronDown,
  CircleDot,
  RefreshCw,
  ShieldCheck,
} from 'lucide-react'
import { useCallback, useEffect, useState } from 'react'
import { fetchAspectEvidenceTrace } from '../api'
import type { AspectEvidenceTrace, AspectEvidenceTraceRecord } from '../types'

type Props = {
  eventId: string
}

function formatNumber(value: number | null | undefined, digits = 2): string {
  return typeof value === 'number' && Number.isFinite(value) ? value.toFixed(digits) : '-'
}

function localTime(value: string | null | undefined): string {
  if (!value) return '-'
  const date = new Date(value)
  return Number.isNaN(date.getTime()) ? value : date.toLocaleString('en-IN', {
    timeZone: 'Asia/Kolkata',
    day: '2-digit',
    month: 'short',
    hour: '2-digit',
    minute: '2-digit',
  })
}

function readinessSummary(record: AspectEvidenceTraceRecord): string {
  const ready = record.sbc.actorReadiness.filter((item) => item.status === 'READY').length
  const motion = record.sbc.actorReadiness.filter((item) => item.status === 'MOTION_REQUIRED').length
  return motion ? `${ready} ready, ${motion} motion required` : `${ready} ready`
}

function TracePoint({
  record,
  label,
  open = false,
}: {
  record: AspectEvidenceTraceRecord
  label: string
  open?: boolean
}) {
  const guidance = record.sbc.guidance
  const market = record.market
  const strength = record.strength
  const patterns = market.candle?.patterns?.map((item) => item.name.replaceAll('_', ' ')) ?? []
  return (
    <details className={`evidence-trace-point is-${record.kind}`} open={open}>
      <summary>
        <div>
          <span>{label}</span>
          <strong>{localTime(record.asOfIst)}</strong>
        </div>
        <div className="evidence-trace-summary-values">
          <span>{market.available ? `RSI ${formatNumber(market.rsi14?.value, 1)}` : 'No closed bar'}</span>
          <span className={guidance && (guidance.netUnits ?? 0) > 0 ? 'is-positive' : guidance && (guidance.netUnits ?? 0) < 0 ? 'is-negative' : ''}>
            SBC {formatNumber(guidance?.netUnits, 1)}
          </span>
          <ChevronDown size={13} />
        </div>
      </summary>
      <div className="evidence-trace-point-body">
        <div className="evidence-trace-grid">
          <div><span>Close</span><strong>{formatNumber(market.close, 3)}</strong></div>
          <div><span>RSI 14</span><strong>{formatNumber(market.rsi14?.value, 1)} {market.rsi14?.zone?.replaceAll('_', ' ')}</strong></div>
          <div><span>Candle</span><strong>{market.candle?.direction ?? 'unavailable'}</strong></div>
          <div><span>Overlaps</span><strong>{record.overlaps.otherActiveCount} other</strong></div>
          <div><span>SBC net</span><strong>{formatNumber(guidance?.netUnits, 2)} {guidance?.band ?? 'unavailable'}</strong></div>
          <div><span>Vedha readiness</span><strong>{readinessSummary(record)}</strong></div>
          <div><span>Planet strength</span><strong>{formatNumber(strength.implementedTotalVirupa, 1)} virupa</strong></div>
          <div><span>Drik pressure</span><strong>{formatNumber(strength.drikVirupa, 1)} virupa</strong></div>
          <div><span>Chesta</span><strong>{formatNumber(strength.chestaVirupa, 1)} virupa</strong></div>
          <div><span>SR state</span><strong>{market.sr?.status?.replaceAll('_', ' ') ?? 'unavailable'}</strong></div>
        </div>
        <div className="evidence-trace-panchanga">
          <span>{record.sbc.panchanga.tithi}</span>
          <span>{record.sbc.panchanga.paksha}</span>
          <span>{record.sbc.panchanga.yoga}</span>
          <span>{record.sbc.panchanga.weekday}</span>
        </div>
        {patterns.length > 0 && <p className="evidence-trace-patterns">Candle geometry: {patterns.join(', ')}</p>}
        {market.sr?.lines?.length ? (
          <div className="evidence-trace-sr-lines">
            {market.sr.lines.map((line) => (
              <span key={`${line.planet}:${line.price}`}>{line.planet} {line.price.toFixed(3)} ({formatNumber(line.distancePipsFromClose, 1)} pips)</span>
            ))}
          </div>
        ) : market.sr?.status === 'not_observed_yet' ? (
          <p className="evidence-trace-muted">SR touch is intentionally absent until its candle closes.</p>
        ) : null}
        <div className="evidence-trace-certification">
          <span className={strength.certification?.certified ? 'is-certified' : 'is-provisional'}>
            Strength {strength.certification?.status?.replaceAll('_', ' ') ?? strength.status}
          </span>
          <span>SBC guidance only</span>
          <span>outcome excluded</span>
        </div>
        {strength.missingComponents?.length ? (
          <p className="evidence-trace-muted">Pending strength witnesses: {strength.missingComponents.join(', ').replaceAll('_', ' ')}</p>
        ) : null}
      </div>
    </details>
  )
}

export function AspectEvidenceTracePanel({ eventId }: Props) {
  const [trace, setTrace] = useState<AspectEvidenceTrace | null>(null)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')

  const load = useCallback(async () => {
    setBusy(true)
    setError('')
    try {
      setTrace(await fetchAspectEvidenceTrace(eventId))
    } catch (caught) {
      setTrace(null)
      setError(caught instanceof Error ? caught.message : String(caught))
    } finally {
      setBusy(false)
    }
  }, [eventId])

  useEffect(() => {
    void load()
  }, [load])

  if (!trace && busy) {
    return <div className="analysis-tab-body evidence-trace-loading"><Activity size={15} /> Calculating timestamp-safe evidence trace...</div>
  }
  if (!trace) {
    return (
      <div className="analysis-tab-body evidence-trace-error">
        <strong>Evidence trace unavailable</strong>
        <span>{error || 'No trace was returned.'}</span>
        <button className="secondary-command" onClick={() => void load()}><RefreshCw size={14} /> Retry</button>
      </div>
    )
  }

  return (
    <div className="analysis-tab-body evidence-trace-tab">
      <section className="evidence-trace-header">
        <div>
          <span className="eyebrow">Aspect evidence trace</span>
          <strong>{trace.symbol} {trace.timeframe}</strong>
          <small>{trace.profile.referenceLabel} | IST display</small>
        </div>
        <button className="icon-button" onClick={() => void load()} disabled={busy} title="Refresh deterministic trace">
          <RefreshCw size={15} className={busy ? 'is-spinning' : ''} />
        </button>
      </section>
      <div className="evidence-trace-guards">
        <span><ShieldCheck size={11} /> timestamp safe</span>
        <span>no lookahead</span>
        <span>research only</span>
      </div>
      <TracePoint record={trace.start} label="Start" open />
      <section className="evidence-trace-window">
        <header>
          <div>
            <CircleDot size={14} />
            <strong>Window trace</strong>
          </div>
          <span>{trace.window.includedBarCount}/{trace.window.totalCompletedBars} closed bars</span>
        </header>
        {trace.window.sampled && <p className="evidence-trace-muted">Evenly sampled closed bars; source window has more records than the review cap.</p>}
        <div className="evidence-trace-record-list">
          {trace.window.records.map((record, index) => (
            <TracePoint
              key={`${record.kind}:${record.asOfUtc}`}
              record={record}
              label={`Bar ${index + 1}`}
              open={trace.window.records.length <= 3 && index === trace.window.records.length - 1}
            />
          ))}
          {!trace.window.records.length && <p className="evidence-trace-muted">No candle closed fully inside this aspect window.</p>}
        </div>
      </section>
      <TracePoint record={trace.end} label="Window end" />
      <section className="evidence-trace-outcome">
        <header><strong>Observed outcome</strong><span>retrospective only</span></header>
        {trace.outcome.available ? (
          <div>
            <strong className={trace.outcome.direction === 'UP' ? 'positive' : trace.outcome.direction === 'DOWN' ? 'negative' : ''}>
              {trace.outcome.direction} {typeof trace.outcome.returnPct === 'number' ? `${trace.outcome.returnPct > 0 ? '+' : ''}${trace.outcome.returnPct.toFixed(3)}%` : ''}
            </strong>
            <small>Label available {localTime(trace.outcome.labelAvailableAtUtc)}</small>
          </div>
        ) : <p>{trace.outcome.reason}</p>}
      </section>
      <section className="evidence-trace-status">
        <strong>Pre-calculations</strong>
        {Object.entries(trace.precalculationStatus).map(([key, status]) => (
          <div key={key}><span>{key.replace(/([A-Z])/g, ' $1').trim()}</span><small>{status.replaceAll('_', ' ')}</small></div>
        ))}
      </section>
    </div>
  )
}
