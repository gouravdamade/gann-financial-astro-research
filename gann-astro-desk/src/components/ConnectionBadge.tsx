import { CircleAlert, Radio, RefreshCw } from 'lucide-react'
import type { Mt5Status } from '../types'

export function ConnectionBadge({ status }: { status: Mt5Status | null }) {
  const state = status?.state ?? 'starting'
  const connected = Boolean(status?.connected)
  const Icon = connected ? Radio : state === 'reconnecting' ? RefreshCw : CircleAlert
  const label = connected ? 'MT5 connected' : state === 'reconnecting' ? 'MT5 reconnecting' : 'MT5 starting'
  return (
    <div className={`connection-badge ${connected ? 'is-connected' : 'is-offline'}`} title={status?.lastError || label}>
      <Icon size={15} className={state === 'reconnecting' ? 'is-spinning' : ''} />
      <span>{label}</span>
      {connected && status?.bid != null && <strong>{status.bid.toFixed(3)}</strong>}
    </div>
  )
}
