import { Clock3, Database, LockKeyhole, RefreshCw, ShieldAlert, ShieldCheck } from 'lucide-react'
import type { ShadowLedgerSnapshot } from '../types'

type ShadowLedgerPanelProps = {
  snapshot: ShadowLedgerSnapshot | null
  busy: boolean
  refreshBusy: boolean
  error: string
  onScan: () => void
  onRefresh: () => void
}

function percent(value: number | null, digits = 1): string {
  return value == null ? 'pending' : `${(value * 100).toFixed(digits)}%`
}

function readinessLabel(code: string): string {
  const labels: Record<string, string> = {
    not_scanned: 'Awaiting first scan',
    retrospective_baseline_blocked: 'Baseline excluded from prospective trial',
    artifact_provenance_incomplete: 'Artifact provenance incomplete',
    artifact_timestamp_in_future: 'Artifact timestamp rejected',
    artifact_price_snapshot_stale: 'Price snapshot is stale',
    fresh_corrected_artifact: 'Fresh corrected artifact is monitored',
    waiting_for_just_closed_touch: 'Waiting for a just-closed SR touch',
    unsupported_timeframe: 'Timeframe is not eligible',
    scan_failed: 'Scanner unavailable',
  }
  return labels[code] ?? code.replaceAll('_', ' ')
}

function gateLabel(status: string): string {
  if (status.startsWith('passed')) return 'Passed'
  if (status.startsWith('failed')) return 'Failed'
  return 'Collecting'
}

export function ShadowLedgerPanel({ snapshot, busy, refreshBusy, error, onScan, onRefresh }: ShadowLedgerPanelProps) {
  const summary = snapshot?.summary
  const supervisor = snapshot?.supervisor
  const refresh = snapshot?.refresh
  const chainValid = summary?.chain.valid ?? true
  return (
    <section className="shadow-ledger-panel">
      <div className="shadow-ledger-summary">
        <span className={chainValid ? 'is-valid' : 'is-invalid'}>
          {chainValid ? <ShieldCheck size={15} /> : <ShieldAlert size={15} />}
          <strong>{chainValid ? 'Chain verified' : 'Chain failed'}</strong>
          <small>{summary?.chain.entryCount ?? 0} immutable entries</small>
        </span>
        <span><strong>{summary?.decisionCount ?? 0}</strong><small>captured decisions</small></span>
        <span><strong>{summary?.pendingOutcomeCount ?? 0}</strong><small>awaiting 72h</small></span>
        <span><strong>{summary?.watchClusterCount ?? 0}</strong><small>settled watches</small></span>
        <span><strong>{percent(summary?.hitRate ?? null)}</strong><small>directional hit rate</small></span>
        <span><strong>{gateLabel(summary?.gateStatus ?? '')}</strong><small>prospective gate</small></span>
        <span className="shadow-execution-lock"><LockKeyhole size={14} /><strong>Execution locked</strong></span>
        <button type="button" onClick={onRefresh} disabled={refreshBusy} title="Request a fresh closed-bar MT5 artifact">
          <Database size={14} /> {refreshBusy ? 'Requested' : 'Refresh source'}
        </button>
        <button type="button" onClick={onScan} disabled={busy} title="Scan prospective ledger now">
          <RefreshCw size={14} className={busy ? 'is-spinning' : ''} /> Scan now
        </button>
      </div>
      <div className="shadow-refresh-line">
        <Database size={13} />
        <strong>{refresh?.state.replaceAll('_', ' ') ?? 'refresh starting'}</strong>
        <span>{refresh?.message ?? 'Checking for the latest fully closed MT5 bar.'}</span>
        {refresh?.latestClosedBarUtc && <span>latest close {new Date(refresh.latestClosedBarUtc).toLocaleString()}</span>}
        {refresh?.activeRun?.artifactId && <span>artifact {refresh.activeRun.artifactId.slice(0, 14)}</span>}
        {refresh?.lastError && <span className="negative">{refresh.lastError}</span>}
      </div>
      <div className="shadow-readiness-line">
        <Clock3 size={13} />
        <strong>{readinessLabel(supervisor?.readiness.code ?? 'not_scanned')}</strong>
        {supervisor?.lastScanAtUtc && <span>last scan {new Date(supervisor.lastScanAtUtc).toLocaleString()}</span>}
        {summary?.wilson95Lower != null && summary.wilson95Upper != null && (
          <span>95% interval {percent(summary.wilson95Lower)} to {percent(summary.wilson95Upper)}</span>
        )}
        {(error || supervisor?.lastError) && <span className="negative">{error || supervisor?.lastError}</span>}
      </div>
      <div className="shadow-ledger-table-wrap">
        <table className="shadow-ledger-table">
          <thead>
            <tr>
              <th>Captured</th>
              <th>Family</th>
              <th>Decision</th>
              <th>Anchor</th>
              <th>72h due</th>
              <th>Status</th>
              <th>Observed</th>
              <th>Result</th>
            </tr>
          </thead>
          <tbody>
            {(snapshot?.records ?? []).map((record) => (
              <tr key={record.shadowId}>
                <td>{new Date(record.capturedAtUtc).toLocaleString()}</td>
                <td title={record.familyKey}>{record.familyKey.replace('TN::', '')}</td>
                <td className={record.direction === 'bullish' ? 'positive' : record.direction === 'bearish' ? 'negative' : ''}>{record.action.replace('WATCH_', '')}</td>
                <td>{record.anchorClose.toFixed(3)}</td>
                <td>{new Date(record.labelDueTimeUtc).toLocaleString()}</td>
                <td>{record.status === 'settled' ? 'settled' : 'pending'}</td>
                <td>{record.observedDirection ?? '-'}</td>
                <td className={record.hit === true ? 'positive' : record.hit === false ? 'negative' : ''}>
                  {record.hit == null ? '-' : record.hit ? 'hit' : 'miss'}
                  {record.signedReturnPct == null ? '' : ` | ${record.signedReturnPct > 0 ? '+' : ''}${record.signedReturnPct.toFixed(3)}%`}
                </td>
              </tr>
            ))}
            {!snapshot?.records.length && (
              <tr><td colSpan={8} className="shadow-empty">No prospective decisions recorded</td></tr>
            )}
          </tbody>
        </table>
      </div>
    </section>
  )
}
