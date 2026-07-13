import { CloudDownload, RefreshCw } from 'lucide-react'
import type { ProspectiveRefreshStatus } from '../types'

type RefreshStatusChipProps = {
  status: ProspectiveRefreshStatus | null | undefined
  busy: boolean
  onRefresh: () => void
}

function stateLabel(state: string | undefined): string {
  const labels: Record<string, string> = {
    starting: 'Starting',
    waiting: 'Waiting',
    waiting_for_close: 'Finalizing bar',
    waiting_for_generator: 'Generator busy',
    generating: 'Building artifact',
    up_to_date: 'Up to date',
    market_stale: 'Market closed',
    error: 'Needs attention',
  }
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
  const latest = status?.latestClosedBarUtc
    ? new Date(status.latestClosedBarUtc).toLocaleString([], { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' })
    : 'closed-bar watcher'
  const working = busy || state === 'generating' || state === 'waiting_for_close'

  return (
    <button
      type="button"
      className={`auto-refresh-chip is-${tone(state)}`}
      onClick={onRefresh}
      disabled={busy}
      title={`${status?.message ?? 'Automatic closed-bar refresh is checking MT5.'}\nLatest: ${latest}\nClick to request a safe check now.`}
      aria-label="Request automatic source refresh check"
    >
      {working ? <RefreshCw size={14} className="is-spinning" /> : <CloudDownload size={14} />}
      <span><strong>Auto refresh</strong><small>{stateLabel(state)}</small></span>
      <i aria-hidden="true" />
    </button>
  )
}
