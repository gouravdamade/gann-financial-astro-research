import { CircleAlert, Radio, RefreshCw } from 'lucide-react'
import type { Mt5Status } from '../types'

export function ConnectionBadge({ status }: { status: Mt5Status | null }) {
  const state = status?.state ?? 'starting'
  const connected = Boolean(status?.connected)
  const Icon = connected ? Radio : state === 'reconnecting' ? RefreshCw : CircleAlert
  const label = connected ? 'MT5 data only' : state === 'reconnecting' ? 'MT5 reconnecting' : 'MT5 starting'
  const detail = connected
    ? `${status?.server ?? 'MT5'} · terminal algo ${status?.terminalAllowsTrading ? 'enabled' : 'disabled'} · app execution locked`
    : status?.lastError || label
  return (
    <div className={`connection-badge ${connected ? 'is-connected' : 'is-offline'}`} title={detail}>
      <Icon size={15} className={state === 'reconnecting' ? 'is-spinning' : ''} />
      <span>{label}</span>
      {connected && status?.bid != null && <strong>{status.bid.toFixed(3)}</strong>}
    </div>
  )
}
