import { useState, type FormEvent } from 'react'
import { CircleAlert, Laptop, Link2, LoaderCircle, ShieldCheck, WifiOff } from 'lucide-react'
import { formatCompanionError, pairCompanion, type CompanionSession } from '../companion'

type MobileCompanionSetupProps = {
  onPaired: (session: CompanionSession) => void
}

export function MobileCompanionSetup({ onPaired }: MobileCompanionSetupProps) {
  const [baseUrl, setBaseUrl] = useState('')
  const [pairingCode, setPairingCode] = useState('')
  const [deviceName, setDeviceName] = useState('Android phone')
  const [error, setError] = useState('')
  const [pairing, setPairing] = useState(false)

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setError('')
    setPairing(true)
    try {
      onPaired(await pairCompanion({ baseUrl, pairingCode, deviceName }))
    } catch (reason) {
      setError(formatCompanionError(reason))
    } finally {
      setPairing(false)
    }
  }

  return (
    <main className="mobile-pairing-shell">
      <header className="mobile-pairing-header">
        <div className="mobile-pairing-brand">
          <span className="mobile-pairing-brand-mark"><Laptop size={21} /></span>
          <span>
            <strong>Gann Astro Mobile</strong>
            <small>Private companion</small>
          </span>
        </div>
        <span className="mobile-execution-lock"><ShieldCheck size={15} /> Execution locked</span>
      </header>

      <section className="mobile-pairing-workspace">
        <div className="mobile-pairing-status">
          <WifiOff size={22} />
          <span>
            <strong>Laptop not paired</strong>
            <small>Open Companion on Gann Astro Desk to obtain the HTTPS address and one-time code.</small>
          </span>
        </div>

        <form className="mobile-pairing-form" onSubmit={submit}>
          <label>
            <span>Laptop address</span>
            <input
              type="url"
              inputMode="url"
              autoCapitalize="none"
              autoCorrect="off"
              placeholder="https://192.168.1.20:9443"
              value={baseUrl}
              onChange={(event) => setBaseUrl(event.target.value)}
              required
            />
          </label>
          <label>
            <span>One-time pairing code</span>
            <input
              type="text"
              inputMode="text"
              autoCapitalize="characters"
              autoCorrect="off"
              placeholder="ABCD-EFGH-JK23"
              value={pairingCode}
              onChange={(event) => setPairingCode(event.target.value)}
              required
            />
          </label>
          <label>
            <span>Device name</span>
            <input
              type="text"
              value={deviceName}
              onChange={(event) => setDeviceName(event.target.value)}
              minLength={2}
              maxLength={64}
              required
            />
          </label>

          {error ? <p className="mobile-pairing-error"><CircleAlert size={16} /> {error}</p> : null}

          <button className="mobile-pairing-submit" type="submit" disabled={pairing}>
            {pairing ? <LoaderCircle className="mobile-spin" size={17} /> : <Link2 size={17} />}
            {pairing ? 'Pairing' : 'Pair laptop'}
          </button>
          <p className="mobile-pairing-security-note">
            The code authenticates an encrypted handshake. The laptop certificate and session token remain inside the native Rust layer.
          </p>
        </form>
      </section>
    </main>
  )
}
