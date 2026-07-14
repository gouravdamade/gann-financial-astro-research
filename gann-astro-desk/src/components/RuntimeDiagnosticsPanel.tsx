import { Activity, Gauge, RotateCcw, ShieldCheck } from 'lucide-react'
import type { RuntimeDiagnosticsBundle } from '../types'

type RuntimeDiagnosticsPanelProps = {
  bundle: RuntimeDiagnosticsBundle | null
  error: string
}

function formatDuration(milliseconds: number): string {
  if (milliseconds >= 60_000) return `${(milliseconds / 60_000).toFixed(1)}m`
  if (milliseconds >= 1_000) return `${(milliseconds / 1_000).toFixed(2)}s`
  return `${milliseconds.toFixed(milliseconds >= 100 ? 0 : 1)}ms`
}

function shortOperationName(name: string): string {
  return name
    .replace(/^http:/, '')
    .replace(/^frontend:/, 'UI ')
    .replaceAll('/api/', '/')
}

export function RuntimeDiagnosticsPanel({ bundle, error }: RuntimeDiagnosticsPanelProps) {
  if (!bundle) {
    return <div className="dock-empty">{error || 'Collecting native runtime diagnostics...'}</div>
  }
  const { diagnostics, runtime } = bundle
  const operations = [...diagnostics.operations]
    .filter((metric) => metric.count > 0)
    .sort((left, right) => right.p95Ms - left.p95Ms)
    .slice(0, 14)
  const startupPhases = Object.entries(diagnostics.startup.phasesMs)
    .sort((left, right) => left[1] - right[1])
  const recoveryClass = runtime?.recoveryState === 'recovered' ? 'is-recovered' : ''

  return (
    <div className="runtime-diagnostics-panel">
      <div className="runtime-summary-strip">
        <span className={runtime?.status === 'ready' ? 'is-ready' : 'is-waiting'}>
          <Activity size={14} />
          <strong>{runtime?.status ?? 'browser'}</strong>
          <small>{runtime ? `sidecar PID ${runtime.pid}` : 'development transport'}</small>
        </span>
        <span className={recoveryClass}>
          <RotateCcw size={14} />
          <strong>{runtime?.restartCount ?? 0} restarts</strong>
          <small>{runtime?.recoveryState ?? 'steady'}</small>
        </span>
        <span>
          <Gauge size={14} />
          <strong>{formatDuration(diagnostics.startup.totalMs)}</strong>
          <small>sidecar startup</small>
        </span>
        <span>
          <ShieldCheck size={14} />
          <strong>observability only</strong>
          <small>execution locked</small>
        </span>
        <span className="runtime-phases" title={startupPhases.map(([name, value]) => `${name}: ${formatDuration(value)}`).join('\n')}>
          {startupPhases.map(([name, value]) => (
            <i key={name}>{name.replaceAll('_', ' ')} {formatDuration(value)}</i>
          ))}
        </span>
      </div>
      {error && <div className="runtime-diagnostic-error">{error}</div>}
      <div className="runtime-metric-table-wrap">
        <table className="runtime-metric-table">
          <thead>
            <tr>
              <th>Operation</th>
              <th>Count</th>
              <th>Last</th>
              <th>Average</th>
              <th>P50</th>
              <th>P95</th>
              <th>Max</th>
              <th>Failures</th>
            </tr>
          </thead>
          <tbody>
            {operations.map((metric) => (
              <tr key={metric.name}>
                <td title={metric.name}>{shortOperationName(metric.name)}</td>
                <td>{metric.count}</td>
                <td>{formatDuration(metric.lastMs)}</td>
                <td>{formatDuration(metric.averageMs)}</td>
                <td>{formatDuration(metric.p50Ms)}</td>
                <td>{formatDuration(metric.p95Ms)}</td>
                <td>{formatDuration(metric.maxMs)}</td>
                <td className={metric.failureCount ? 'negative' : ''}>{metric.failureCount}</td>
              </tr>
            ))}
            {!operations.length && (
              <tr><td colSpan={8} className="runtime-empty">Waiting for measured operations.</td></tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  )
}
