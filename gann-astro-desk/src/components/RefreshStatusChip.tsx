import { CircleAlert, CloudDownload, FileSearch, RefreshCw } from 'lucide-react'
import type { ProspectiveRefreshStatus } from '../types'

type RefreshStatusChipProps = {
  status: ProspectiveRefreshStatus | null | undefined
  busy: boolean
  onRefresh: () => void
}

function stateLabel(state: string | undefined, historicalFailure: boolean): string {
  const labels: Record<string, string> = {
    starting: 'Starting',
    waiting: 'Waiting',
    waiting_for_close: 'Finalizing bar',
    waiting_for_generator: 'Generator busy',
    generating: 'Building artifact',
    up_to_date: 'Up to date',
    market_stale: 'Market closed',
    error: 'Refresh blocked',
  }
  if (historicalFailure) return 'Historical failure'
  return labels[state ?? ''] ?? (state ? state.replaceAll('_', ' ') : 'Checking')
}

function tone(state: string | undefined): string {
  if (state === 'up_to_date') return 'ready'
  if (state === 'error') return 'error'
  if (state === 'market_stale') return 'idle'
  return 'working'
}

export function RefreshStatusChip({ status, busy, onRefresh }: RefreshStatusChipProps) {
  const state = status?.state
  const failedRun = status?.activeRun?.status === 'failed' ? status.activeRun : null
  const historicalFailure = Boolean(
    failedRun && status?.latestClosedBarUtc && failedRun.sourceBarCloseUtc === status.latestClosedBarUtc,
  )
  const latest = status?.latestClosedBarUtc
    ? new Date(status.latestClosedBarUtc).toLocaleString([], { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' })
    : 'closed-bar watcher'
  const working = busy || state === 'generating' || state === 'waiting_for_close'
  const title = historicalFailure
    ? 'The latest closed bar already has a preserved failed run. This check does not retry that bar; it checks whether a later eligible closed bar can proceed. Open Inspect failed run for details.'
    : `${status?.message ?? 'Automatic closed-bar refresh is checking MT5.'}\nLatest: ${latest}\nClick to request a safe check now.`

  return (
    <>
      <button
        type="button"
        className={`auto-refresh-chip is-${tone(state)}`}
        onClick={onRefresh}
        disabled={busy}
        title={title}
        aria-label={historicalFailure ? 'Check for a later eligible closed bar' : 'Request automatic source refresh check'}
      >
        {working ? <RefreshCw size={14} className="is-spinning" /> : historicalFailure ? <CircleAlert size={14} /> : <CloudDownload size={14} />}
        <span><strong>Auto refresh</strong><small>{stateLabel(state, historicalFailure)}</small></span>
        <i aria-hidden="true" />
      </button>
      {failedRun && (
        <details className="auto-refresh-failure-details">
          <summary><FileSearch size={13} /> Inspect failed run</summary>
          <div className="auto-refresh-failure-body">
            <div><span>Failed bar</span><strong>{new Date(failedRun.sourceBarCloseUtc).toLocaleString()}</strong></div>
            <div><span>Run ID</span><code>{failedRun.runId}</code></div>
            <div><span>Stage</span><code>{failedRun.stage}</code></div>
            <div><span>Source snapshot</span><code>{failedRun.sourceSnapshotId ?? 'none'}</code></div>
            <div><span>Price source</span><code>{failedRun.priceSourceId ?? 'none'}</code></div>
            <div><span>Generation job</span><code>{failedRun.generationJobId ?? 'none'}</code></div>
            <div><span>Artifact</span><code>{failedRun.artifactId ?? 'none'}</code></div>
            <p><strong>Error</strong>{failedRun.error || failedRun.message || 'No persisted error detail.'}</p>
            <small>This historical row is preserved. A later eligible closed bar is processed under its own run ID.</small>
          </div>
        </details>
      )}
    </>
  )
}
