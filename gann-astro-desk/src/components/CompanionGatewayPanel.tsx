import { useCallback, useEffect, useMemo, useState } from 'react'
import { Copy, Link2, LoaderCircle, RefreshCw, ShieldCheck, Smartphone, Trash2, X } from 'lucide-react'
import {
  fetchCompanionGateway,
  fetchCompanionSessions,
  openCompanionPairing,
  revokeCompanionSession,
  type CompanionGatewayInfo,
  type CompanionGatewaySession,
  type CompanionPairingWindow,
} from '../desktopCompanion'

type CompanionGatewayPanelProps = {
  onClose: () => void
}

function shortFingerprint(value: string): string {
  return value.match(/.{1,4}/g)?.slice(0, 8).join(' ') ?? value
}

export function CompanionGatewayPanel({ onClose }: CompanionGatewayPanelProps) {
  const [gateway, setGateway] = useState<CompanionGatewayInfo | null>(null)
  const [pairing, setPairing] = useState<CompanionPairingWindow | null>(null)
  const [sessions, setSessions] = useState<CompanionGatewaySession[]>([])
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')
  const [copied, setCopied] = useState('')
  const [selectedUrl, setSelectedUrl] = useState('')

  const refresh = useCallback(async () => {
    setError('')
    try {
      const [nextGateway, nextSessions] = await Promise.all([
        fetchCompanionGateway(),
        fetchCompanionSessions(),
      ])
      setGateway(nextGateway)
      setSessions(nextSessions)
      if (!nextGateway.pairingActive) setPairing(null)
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : 'Unable to inspect companion gateway')
    }
  }, [])

  useEffect(() => {
    void refresh()
    const timer = window.setInterval(() => void refresh(), 5000)
    return () => window.clearInterval(timer)
  }, [refresh])

  const availableUrls = useMemo(
    () => pairing?.urls ?? gateway?.urls ?? [],
    [gateway?.urls, pairing?.urls],
  )
  useEffect(() => {
    if (!availableUrls.length) {
      setSelectedUrl('')
    } else if (!availableUrls.includes(selectedUrl)) {
      setSelectedUrl(availableUrls[0])
    }
  }, [availableUrls, selectedUrl])

  async function beginPairing() {
    setBusy(true)
    setError('')
    try {
      const next = await openCompanionPairing()
      setPairing(next)
      await refresh()
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : 'Unable to open pairing')
    } finally {
      setBusy(false)
    }
  }

  async function copy(label: string, value: string) {
    await navigator.clipboard.writeText(value)
    setCopied(label)
    window.setTimeout(() => setCopied(''), 1500)
  }

  async function revoke(sessionId: string) {
    setBusy(true)
    try {
      await revokeCompanionSession(sessionId)
      await refresh()
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : 'Unable to revoke device')
    } finally {
      setBusy(false)
    }
  }

  const primaryUrl = selectedUrl || availableUrls[0] || ''
  const expires = pairing?.expiresAtUtc ?? gateway?.pairingExpiresAtUtc

  return (
    <aside className="companion-gateway-panel" aria-label="Android companion gateway">
      <header>
        <span><Smartphone size={18} /><span><strong>Android companion</strong><small>Rust HTTPS/WSS gateway</small></span></span>
        <button className="icon-button" onClick={onClose} title="Close companion panel"><X size={16} /></button>
      </header>

      <div className="companion-gateway-status">
        <span className={gateway?.status === 'ready' ? 'is-ready' : 'is-waiting'}><i /> {gateway?.status ?? 'checking'}</span>
        <span><ShieldCheck size={13} /> Execution locked</span>
        <button className="icon-button" onClick={() => void refresh()} title="Refresh companion status"><RefreshCw size={14} /></button>
      </div>

      {pairing ? (
        <section className="companion-pairing-card">
          <div><strong>One-time code</strong><time>{expires ? new Date(expires).toLocaleTimeString() : ''}</time></div>
          <button className="companion-code" onClick={() => void copy('code', pairing.pairingCode)} title="Copy pairing code">
            {pairing.pairingCode}<Copy size={14} />
          </button>
          <button className="companion-url" onClick={() => void copy('address', primaryUrl)} title="Copy laptop address">
            <span>{primaryUrl}</span><Copy size={14} />
          </button>
          {availableUrls.length > 1 && (
            <label className="companion-address-choice">
              <span>Network address</span>
              <select value={primaryUrl} onChange={(event) => setSelectedUrl(event.target.value)}>
                {availableUrls.map((url) => <option key={url} value={url}>{url}</option>)}
              </select>
            </label>
          )}
          <small>{copied ? `${copied} copied` : 'Enter both values in Gann Astro Mobile while the phone is on this network.'}</small>
        </section>
      ) : (
        <button className="companion-open-pairing" onClick={() => void beginPairing()} disabled={busy || !gateway}>
          {busy ? <LoaderCircle className="mobile-spin" size={16} /> : <Link2 size={16} />} Pair a phone
        </button>
      )}

      <section className="companion-certificate">
        <strong>Certificate pin</strong>
        <code>{gateway ? shortFingerprint(gateway.certificateSha256) : 'waiting'}</code>
        <small>The one-time-code handshake encrypts this certificate and the session token before Android trusts it.</small>
      </section>

      <section className="companion-session-list">
        <div><strong>Paired this run</strong><span>{sessions.length}</span></div>
        {sessions.map((session) => (
          <article key={session.sessionId}>
            <span><strong>{session.deviceName}</strong><small>{session.remoteAddress} | seen {new Date(session.lastSeenAtUtc).toLocaleTimeString()}</small></span>
            <button className="icon-button" onClick={() => void revoke(session.sessionId)} disabled={busy} title="Revoke phone"><Trash2 size={14} /></button>
          </article>
        ))}
        {!sessions.length && <p>No active phone session. Sessions expire after 12 hours and are revoked when the Windows app closes.</p>}
      </section>

      {error && <p className="companion-gateway-error">{error}</p>}
    </aside>
  )
}
