import { Activity, Clock3, Fingerprint, LockKeyhole, RefreshCw, ShieldAlert, ShieldCheck } from 'lucide-react'
import type { CandlestickShadowRecord, CandlestickShadowSnapshot } from '../types'

type CandlestickShadowPanelProps = {
  snapshot: CandlestickShadowSnapshot | null
  busy: boolean
  error: string
  onScan: () => void
}

function probability(value?: number): string {
  return value == null ? '-' : `${(value * 100).toFixed(2)}%`
}

function signed(value?: number | null): string {
  if (value == null) return '-'
  return `${value > 0 ? '+' : ''}${value.toFixed(1)}`
}

function recordValues(record: CandlestickShadowRecord): {
  primary: string
  diagnostic: string
  evidence: string
  result: string
} {
  const payload = record.payload
  if (record.entryType === 'decision') {
    const diagnostic = payload.diagnostics[0]
    return {
      primary: `${payload.primary.action} | up ${probability(payload.primary.probabilityUp)}`,
      diagnostic: diagnostic ? `${diagnostic.action} | up ${probability(diagnostic.probabilityUp)}` : '-',
      evidence: payload.patterns?.map((item) => item.name.replaceAll('_', ' ')).join(', ') || 'no named pattern',
      result: 'awaiting six bars',
    }
  }
  const diagnostic = payload.diagnostics[0]
  return {
    primary: `${payload.primary.action} | ${signed(payload.primary.netPips)} net`,
    diagnostic: diagnostic ? `${diagnostic.action} | ${signed(diagnostic.netPips)} net` : '-',
    evidence: `${payload.entryPrice?.toFixed(3)} to ${payload.exitPrice?.toFixed(3)}`,
    result: `${signed(payload.grossLongPips)} long pips | ${payload.targetUp ? 'up' : 'down'}`,
  }
}

export function CandlestickShadowPanel({ snapshot, busy, error, onScan }: CandlestickShadowPanelProps) {
  const chainValid = snapshot?.integrity.ok ?? true
  return (
    <section className="candle-shadow-panel">
      <div className="shadow-ledger-summary">
        <span className={chainValid ? 'is-valid' : 'is-invalid'}>
          {chainValid ? <ShieldCheck size={15} /> : <ShieldAlert size={15} />}
          <strong>{chainValid ? 'Chain verified' : 'Chain failed'}</strong>
          <small>{snapshot?.integrity.entries ?? 0} immutable entries</small>
        </span>
        <span><strong>{snapshot?.summary.decisions ?? 0}</strong><small>timely H1 decisions</small></span>
        <span><strong>{snapshot?.summary.pending ?? 0}</strong><small>awaiting six bars</small></span>
        <span><strong>{snapshot?.summary.outcomes ?? 0}</strong><small>settled observations</small></span>
        <span className="candle-gate-failed"><Activity size={13} /><strong>Primary failed</strong><small>retrospective gate</small></span>
        <span className="shadow-execution-lock"><LockKeyhole size={14} /><strong>Execution locked</strong></span>
        <button type="button" onClick={onScan} disabled={busy} title="Scan the read-only H1 candle shadow ledger now">
          <RefreshCw size={14} className={busy ? 'is-spinning' : ''} /> Scan now
        </button>
      </div>
      <div className="candle-shadow-status">
        <Clock3 size={13} />
        <strong>{snapshot?.lastScan.state.replaceAll('_', ' ') ?? 'starting'}</strong>
        <span>{snapshot?.lastScan.message ?? 'Waiting for the first read-only MT5 scan.'}</span>
        {snapshot?.lastScan.observedAtUtc && <span>{new Date(snapshot.lastScan.observedAtUtc).toLocaleString()}</span>}
        {snapshot?.lastScan.marketClock && (
          <span className={snapshot.lastScan.marketClock.valid ? '' : 'negative'}>
            MT5 clock {snapshot.lastScan.marketClock.skewSeconds > 0 ? '+' : ''}{snapshot.lastScan.marketClock.skewSeconds.toFixed(0)}s
          </span>
        )}
        {error && <span className="negative">{error}</span>}
      </div>
      <div className="candle-shadow-status">
        <Fingerprint size={13} />
        <strong>Frozen transparent model</strong>
        <span title={snapshot?.trial.trialId}>trial {snapshot?.trial.trialId.slice(0, 12) ?? '-'}</span>
        <span title={snapshot?.model.primaryModelId}>primary {snapshot?.model.primaryModelId.slice(0, 12) ?? '-'}</span>
        <span>15-minute grace; missed bars are never backfilled; MT5 clock skew must be within 5 minutes</span>
        <span className="shadow-policy-lock"><LockKeyhole size={12} /> research only</span>
      </div>
      <div className="shadow-ledger-table-wrap">
        <table className="shadow-ledger-table candle-shadow-table">
          <thead>
            <tr>
              <th>Effective</th>
              <th>Entry</th>
              <th>Primary candidate</th>
              <th>Raw diagnostic</th>
              <th>Evidence</th>
              <th>Observed result</th>
              <th>Hash</th>
            </tr>
          </thead>
          <tbody>
            {(snapshot?.records ?? []).map((record) => {
              const values = recordValues(record)
              return (
                <tr key={record.entryId}>
                  <td>{new Date(record.effectiveAtUtc).toLocaleString()}</td>
                  <td>{record.entryType}</td>
                  <td>{values.primary}</td>
                  <td>{values.diagnostic}</td>
                  <td title={values.evidence}>{values.evidence}</td>
                  <td>{values.result}</td>
                  <td title={record.entryHash}>{record.entryHash.slice(0, 12)}</td>
                </tr>
              )
            })}
            {!snapshot?.records.length && (
              <tr><td colSpan={7} className="shadow-empty">No timely prospective candle decisions recorded</td></tr>
            )}
          </tbody>
        </table>
      </div>
    </section>
  )
}
