import { useCallback, useEffect, useRef, useState } from 'react'
import { BookOpenCheck, CircleAlert, LockKeyhole, RefreshCw, ShieldCheck } from 'lucide-react'
import {
  compareXe2ScopedEvidenceTransforms,
  fetchXe2ScopedEvidenceProfile,
  fetchXe2ScopedEvidenceSnapshot,
  fetchXe2ScopedEvidenceTrialLedger,
} from '../api'
import type {
  Xe2ComparisonResponse,
  Xe2ProfileResponse,
  Xe2Snapshot,
  Xe2TrialLedger,
} from '../xe2EvidenceTypes'

const XE2_TRANSFORM_LABELS: Record<string, string> = {
  XE2_M0_BASE_SYNTHETIC_SIGN_TEST_V1: 'M0 base test sign',
  XE2_M1_SCOPED_POSITIVE_SPEED_MULTIPLIER_V1: 'M1 scoped speed multiplier',
  XE2_M2_SPEED_SEPARATE_CHANNEL_V1: 'M2 separate speed channel',
  XE2_M3_SPEED_INTERACTION_V1: 'M3 speed interaction',
  XE2_M4_MOTION_CONTEXT_GATE_V1: 'M4 direct-motion gate',
}

function formatNumber(value: number | null | undefined, digits = 4): string {
  return value == null ? 'Unknown' : value.toFixed(digits)
}

function Xe2RawEvidence({ snapshot }: { snapshot: Xe2Snapshot }) {
  return (
    <section className="xe1-panel" aria-label="XE2 real astronomical raw evidence">
      <div className="xe1-panel-heading">
        <div><span>Evidence admission</span><strong>Real astronomy, unsigned modifier, synthetic sign test</strong></div>
        <span className="xe1-lock-chip"><LockKeyhole size={12} /> Raw fixture sealed</span>
      </div>
      <p className="xe1-governance">Every event identity and raw speed is hash-linked to the verified April packet. The signed values below are deliberately synthetic test inputs, not market evidence.</p>
      <div className="xe1-table-wrap">
        <table className="xe1-table xe2-table">
          <thead><tr><th>Exact event</th><th>Raw astronomy</th><th>Modifier scope</th><th>Signed channel</th><th>Identity</th></tr></thead>
          <tbody>{snapshot.causalContributions.map((item) => (
            <tr key={item.causalEventId}>
              <td><strong>{item.eventId}</strong><small>{item.causalEventId}</small></td>
              <td>{formatNumber(item.rawSpeedDegPerDay, 8)} deg/day<small>{item.speedNormalizationContract}; z {formatNumber(item.zSpeed)}</small></td>
              <td>{item.scope.scopeType}<small>{item.scope.scopeStatus}; global default: no</small></td>
              <td>SYNTHETIC {formatNumber(item.rawSyntheticSignTestValue, 2)}<small>not market evidence</small></td>
              <td><code>{item.eventHash.slice(0, 18)}...</code><small>single pass verified</small></td>
            </tr>
          ))}</tbody>
        </table>
      </div>
    </section>
  )
}

function Xe2Contributions({ snapshot }: { snapshot: Xe2Snapshot }) {
  return (
    <section className="xe1-panel" aria-label="XE2 causal scope audit">
      <div className="xe1-panel-heading"><div><span>Causal scope audit</span><strong>Each modifier is bound to one event only</strong></div><span className="xe1-note-chip">NO GLOBAL SCOPE</span></div>
      <div className="xe1-contribution-list">
        {snapshot.causalContributions.map((item) => (
          <article key={item.causalEventId} className={item.value == null ? 'is-unknown' : ''}>
            <div><strong>{item.causalEventId}</strong><span>{item.motionPhaseAtExact} motion context</span></div>
            <span className="xe1-contribution-value">test {formatNumber(item.value, 3)}</span>
            <p>Base synthetic sign {formatNumber(item.rawSyntheticSignTestValue, 3)}; speed z {formatNumber(item.zSpeed)}; modifier/interaction {formatNumber(item.multiplierOrInteraction)}; gate {formatNumber(item.contextGate)}.</p>
            <small>{item.signEvidenceStatus}{item.reason ? `; ${item.reason}` : ''}</small>
          </article>
        ))}
      </div>
    </section>
  )
}

function Xe2Tournament({ comparison }: { comparison: Xe2ComparisonResponse | null }) {
  return (
    <section className="xe1-panel" aria-label="XE2 modifier tournament">
      <div className="xe1-panel-heading"><div><span>Modifier tournament</span><strong>M0-M4 side-by-side; no selection, fit, or optimization</strong></div></div>
      {!comparison && <p className="xe1-empty">Loading causal-scoped tournament.</p>}
      {comparison && <div className="xe1-transform-grid xe2-transform-grid">{comparison.comparisons.map((item) => (
        <article key={item.transformId}>
          <span>{XE2_TRANSFORM_LABELS[item.transformId] ?? item.transform.label}</span>
          <strong className="is-unknown">SYNTHETIC SIGN TEST ONLY</strong>
          <small>Test D norm {formatNumber(item.syntheticStateVector.syntheticNormalized)}</small>
          <small>{item.marketDirectionStatus.replaceAll('_', ' ')}</small>
        </article>
      ))}</div>}
    </section>
  )
}

function Xe2TrialLedgerPanel({ ledger }: { ledger: Xe2TrialLedger | null }) {
  return (
    <section className="xe1-panel xe1-trial-panel" aria-label="XE2 immutable trial ledger">
      <div className="xe1-panel-heading"><div><span>Trial / profile</span><strong>Immutable causal-scoped research ledger</strong></div><span className="xe1-lock-chip">APRIL 2025: TOUCHED DEV</span></div>
      {!ledger && <p className="xe1-empty">Loading trial ledger.</p>}
      {ledger && <>
        <p className="xe1-governance">{String(ledger.datasetGovernance.outcomeEvaluationStatus).replaceAll('_', ' ')}. No price outcome, live MT5 feed, or validation result is part of XE2.</p>
        <div className="xe1-trial-list">{ledger.entries.map((item) => <article key={item.trialId}><div><strong>{item.trialId}</strong><span>{item.datasetStatus} · {item.result}</span></div><p>{item.notes}</p><small>Immutable hash {item.entryHash.slice(0, 16)}...</small></article>)}</div>
      </>}
    </section>
  )
}

export function Xe2ScopedEvidencePanel() {
  const [profile, setProfile] = useState<Xe2ProfileResponse | null>(null)
  const [snapshot, setSnapshot] = useState<Xe2Snapshot | null>(null)
  const [comparison, setComparison] = useState<Xe2ComparisonResponse | null>(null)
  const [ledger, setLedger] = useState<Xe2TrialLedger | null>(null)
  const [transformId, setTransformId] = useState('XE2_M1_SCOPED_POSITIVE_SPEED_MULTIPLIER_V1')
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')
  const requestId = useRef(0)

  const load = useCallback(async (nextTransformId = transformId) => {
    const currentRequest = requestId.current + 1
    requestId.current = currentRequest
    setBusy(true)
    setError('')
    try {
      const [nextProfile, nextSnapshot, nextComparison, nextLedger] = await Promise.all([
        profile ? Promise.resolve(profile) : fetchXe2ScopedEvidenceProfile(),
        fetchXe2ScopedEvidenceSnapshot({ transformId: nextTransformId }),
        compareXe2ScopedEvidenceTransforms(),
        ledger ? Promise.resolve(ledger) : fetchXe2ScopedEvidenceTrialLedger(),
      ])
      if (currentRequest !== requestId.current) return
      setProfile(nextProfile)
      setSnapshot(nextSnapshot)
      setComparison(nextComparison)
      setLedger(nextLedger)
    } catch (caught) {
      if (currentRequest === requestId.current) setError(caught instanceof Error ? caught.message : String(caught))
    } finally {
      if (currentRequest === requestId.current) setBusy(false)
    }
  }, [ledger, profile, transformId])

  useEffect(() => { void load() }, [load])

  return (
    <>
      <section className="xe1-context-strip xe2-context-strip" aria-label="XE2 research profile context">
        <span><BookOpenCheck size={13} /> {profile?.profile.profileId ?? 'Loading XE2 profile'}</span>
        <span>Profile hash {snapshot?.profile.profileHash.slice(0, 16) ?? '...'}...</span>
        <span>REAL ASTRONOMY: HASH-LINKED</span><span className="xe1-market-input">SIGNED MARKET EVIDENCE: NONE</span><span><ShieldCheck size={13} /> execution locked</span>
      </section>
      <header className="xe2-panel-controls">
        <div><span>XE2 scope</span><strong>Real astronomical input with a synthetic sign test channel</strong><p>No market sign is inferred from event geometry, speed, target, or motion.</p></div>
        <div className="experimental-controls">
          <label>Transform<select aria-label="XE2 modifier transform" value={transformId} onChange={(event) => { const value = event.target.value; setTransformId(value); void load(value) }} disabled={busy}>{Object.entries(XE2_TRANSFORM_LABELS).map(([id, label]) => <option key={id} value={id}>{label}</option>)}</select></label>
          <button type="button" className="secondary-command" onClick={() => void load()} disabled={busy} title="Refresh immutable XE2 evidence"><RefreshCw size={14} className={busy ? 'xe1-spin' : ''} /> Refresh</button>
        </div>
      </header>
      {error && <div className="xe1-error"><CircleAlert size={16} /><strong>XE2 research lab unavailable</strong><span>{error}</span></div>}
      {snapshot && <>
        <section className="xe2-status-grid" aria-label="XE2 evidence and outcome status">
          <div><span>Dataset</span><strong>{snapshot.datasetStatus}</strong></div>
          <div><span>Real inputs</span><strong>EVENT IDENTITY + SPEED</strong></div>
          <div><span>Signed channel</span><strong>SYNTHETIC TEST ONLY</strong></div>
          <div><span>Outcome evaluation</span><strong>BLOCKED</strong></div>
        </section>
        <section className="xe1-panel xe1-oscillator-panel" aria-label="XE2 synthetic test vector">
          <div className="xe1-panel-heading"><div><span>Test-only aggregate</span><strong>Not a market oscillator or forecast</strong></div><span className="xe1-state-chip is-unknown">{snapshot.syntheticStateVector.state.replaceAll('_', ' ')}</span></div>
          <div className="xe1-vector-summary"><div><span>Test P</span><strong>{formatNumber(snapshot.syntheticStateVector.positive)}</strong></div><div><span>Test N</span><strong>{formatNumber(snapshot.syntheticStateVector.negative)}</strong></div><div><span>Test D raw</span><strong>{formatNumber(snapshot.syntheticStateVector.syntheticRaw)}</strong></div><div><span>Test D norm</span><strong>{formatNumber(snapshot.syntheticStateVector.syntheticNormalized)}</strong></div><div><span>Activity</span><strong>{formatNumber(snapshot.syntheticStateVector.activity)}</strong></div><div><span>Conflict</span><strong>{formatNumber(snapshot.syntheticStateVector.conflict)}</strong></div></div>
        </section>
        <div className="xe1-content-grid"><Xe2RawEvidence snapshot={snapshot} /><Xe2Contributions snapshot={snapshot} /></div>
        <Xe2Tournament comparison={comparison} />
        <div className="xe1-bottom-grid">
          <section className="xe1-panel" aria-label="XE2 normalization and source audit"><div className="xe1-panel-heading"><div><span>Source / normalization</span><strong>Raw units and provenance remain inspectable</strong></div></div><dl className="xe1-detail-list"><div><dt>Speed contract</dt><dd>{snapshot.normalization.contract}</dd></div><div><dt>Raw unit</dt><dd>{snapshot.normalization.rawUnit}</dd></div><div><dt>Reference</dt><dd>{snapshot.normalization.referenceSpeedDegPerDay} deg/day</dd></div><div><dt>Formula</dt><dd>{snapshot.normalization.formula}</dd></div><div><dt>Event source</dt><dd>{snapshot.astronomySource.reviewedPacketFile}</dd></div><div><dt>Market direction</dt><dd>{snapshot.marketDirectionStatus}</dd></div></dl></section>
          <Xe2TrialLedgerPanel ledger={ledger} />
        </div>
      </>}
    </>
  )
}
