import { useCallback, useEffect, useMemo, useRef, useState } from 'react'
import { Activity, Beaker, BookOpenCheck, CircleAlert, LockKeyhole, RefreshCw, ShieldCheck } from 'lucide-react'
import {
  compareExperimentalEvidenceTransforms,
  fetchExperimentalEvidenceProfile,
  fetchExperimentalEvidenceSnapshot,
  fetchExperimentalEvidenceTrialLedger,
} from '../api'
import type {
  ExperimentalComparisonResponse,
  ExperimentalDatasetStatus,
  ExperimentalProfileResponse,
  ExperimentalSnapshot,
  ExperimentalTrialLedger,
} from '../experimentalEvidenceTypes'
import { Xe2ScopedEvidencePanel } from './Xe2ScopedEvidencePanel'
import { Xe3OutcomeBlindReviewPanel } from './Xe3OutcomeBlindReviewPanel'

const DATA_MODE_LABELS: Record<ExperimentalDatasetStatus, string> = {
  SYNTHETIC: 'Synthetic fixture',
  TOUCHED_DEV: 'Touched development',
  MANUAL: 'Manual input placeholder',
}

const TRANSFORM_LABELS: Record<string, string> = {
  XE1_BASE_DIRECTIONAL_V1: 'Base directional evidence',
  XE1_BOUNDED_EXP_MULTIPLIER_V1: 'Bounded positive multiplier',
  XE1_SEPARATE_CHANNEL_V1: 'Separate modifier channel',
  XE1_INTERACTION_V1: 'Interaction comparison',
}

function asNumber(value: number | null | undefined, digits = 3): string {
  return value == null ? 'Unknown' : value.toFixed(digits)
}

function stateTone(value: string): string {
  if (value === 'SUPPORTIVE') return 'is-supportive'
  if (value === 'ADVERSE') return 'is-adverse'
  if (value === 'MIXED') return 'is-mixed'
  return 'is-unknown'
}

function stateLabel(value: string): string {
  if (value === 'SUPPORTIVE') return 'POSITIVE EVIDENCE'
  if (value === 'ADVERSE') return 'NEGATIVE EVIDENCE'
  if (value === 'MIXED') return 'MIXED EVIDENCE'
  if (value === 'NEUTRAL') return 'UNKNOWN / BALANCED'
  return 'UNKNOWN / NO ACTIVE EVIDENCE'
}

function roleTone(role: string): string {
  if (role === 'SIGN') return 'is-sign'
  if (role === 'MODIFIER') return 'is-modifier'
  if (role === 'GATE') return 'is-gate'
  return 'is-context'
}

function ExperimentalStateLane({ snapshot }: { snapshot: ExperimentalSnapshot }) {
  const value = snapshot.experimentalOscillator.displayValue
  const position = value == null ? 50 : Math.max(0, Math.min(100, (value + 1) * 50))
  return (
    <section className="xe1-panel xe1-oscillator-panel" aria-label="Experimental categorical oscillator">
      <div className="xe1-panel-heading">
        <div>
          <span>Experimental oscillator</span>
          <strong>Categorical state vector, not a market forecast</strong>
        </div>
        <span className={`xe1-state-chip ${stateTone(snapshot.stateVector.state)}`}>{stateLabel(snapshot.stateVector.state)}</span>
      </div>
      <div className="xe1-oscillator-lane" aria-label="Experimental directional state lane">
        <span className="xe1-lane-negative">negative evidence</span>
        <span className="xe1-lane-neutral">unknown / balanced</span>
        <span className="xe1-lane-positive">positive evidence</span>
        {value == null
          ? <span className="xe1-lane-gap">No active evidence</span>
          : <span className="xe1-lane-marker" style={{ left: `${position}%` }} title={`Experimental normalized state ${value.toFixed(3)}`} />}
      </div>
      <div className="xe1-vector-summary">
        <div><span>P</span><strong>{asNumber(snapshot.stateVector.positive)}</strong></div>
        <div><span>N</span><strong>{asNumber(snapshot.stateVector.negative)}</strong></div>
        <div><span>D raw</span><strong>{asNumber(snapshot.stateVector.directionalRaw)}</strong></div>
        <div><span>D norm</span><strong>{asNumber(snapshot.stateVector.directionalNormalized)}</strong></div>
        <div><span>Activity</span><strong>{asNumber(snapshot.stateVector.activity)}</strong></div>
        <div><span>Conflict</span><strong>{asNumber(snapshot.stateVector.conflictLinear)}</strong></div>
      </div>
    </section>
  )
}

function RawEvidenceTable({ snapshot }: { snapshot: ExperimentalSnapshot }) {
  const roleByFeature = useMemo(
    () => new Map(snapshot.profile.bindings.map((binding) => [binding.featureKey, binding])),
    [snapshot.profile.bindings],
  )
  return (
    <section className="xe1-panel" aria-label="Immutable raw evidence">
      <div className="xe1-panel-heading">
        <div><span>Evidence input</span><strong>Immutable raw observations</strong></div>
        <span className="xe1-lock-chip"><LockKeyhole size={12} /> {snapshot.dataMode === 'SYNTHETIC' && snapshot.rawObservations.length > 0 ? 'Raw fixture sealed' : 'No observations admitted'}</span>
      </div>
      {!snapshot.rawObservations.length && <p className="xe1-empty">{snapshot.manualInputStatus.replaceAll('_', ' ')}. This version deliberately accepts no frontend-invented evidence.</p>}
      {!!snapshot.rawObservations.length && <div className="xe1-table-wrap">
        <table className="xe1-table">
          <thead><tr><th>Observation</th><th>Type</th><th>Raw value</th><th>Role</th><th>Causal identity</th><th>Source state</th></tr></thead>
          <tbody>{snapshot.rawObservations.map((observation) => {
            const binding = roleByFeature.get(observation.featureKey)
            return <tr key={observation.observationId}>
              <td><strong>{observation.featureKey}</strong><small>{observation.observationId}</small></td>
              <td>{observation.valueType}</td>
              <td>{observation.rawValue == null ? 'Unknown' : String(observation.rawValue)} <small>{observation.rawUnit}</small></td>
              <td><span className={`xe1-role-chip ${roleTone(binding?.role ?? 'CONTEXT')}`}>{binding?.role ?? 'UNBOUND'}</span></td>
              <td>{observation.causalClassification}<small>{observation.causalEventId ?? 'No causal ID'}</small></td>
              <td>{observation.sourceStatus}{observation.unknownReasons.length > 0 && <small>{observation.unknownReasons.join(', ')}</small>}</td>
            </tr>
          })}</tbody>
        </table>
      </div>}
    </section>
  )
}

function Contributions({ snapshot }: { snapshot: ExperimentalSnapshot }) {
  return (
    <section className="xe1-panel" aria-label="Causal contribution audit">
      <div className="xe1-panel-heading">
        <div><span>Causal grouping</span><strong>One directional vote per causal group</strong></div>
        <span className="xe1-note-chip">AMBIGUOUS fails closed</span>
      </div>
      <div className="xe1-contribution-list">
        {snapshot.causalContributions.map((contribution) => (
          <article key={contribution.causalEventId} className={contribution.value == null ? 'is-unknown' : ''}>
            <div><strong>{contribution.causalEventId}</strong><span>{contribution.causalClassification}</span></div>
            <span className="xe1-contribution-value">{asNumber(contribution.value)}</span>
            <p>{contribution.reason ?? `Primary raw ${asNumber(contribution.rawDirectionalValue)}; derived children remain audit-only.`}</p>
            {contribution.derivedChildIds.length > 0 && <small>Derived child: {contribution.derivedChildIds.join(', ')}</small>}
          </article>
        ))}
      </div>
    </section>
  )
}

function ModifierComparison({ comparison }: { comparison: ExperimentalComparisonResponse | null }) {
  return (
    <section className="xe1-panel" aria-label="Modifier transform comparison">
      <div className="xe1-panel-heading"><div><span>Modifier comparison</span><strong>Side-by-side transforms, no tuning or optimization</strong></div></div>
      {!comparison && <p className="xe1-empty">Loading transform comparison.</p>}
      {comparison && <div className="xe1-transform-grid">
        {comparison.comparisons.map((item) => <article key={item.transformId}>
          <span>{TRANSFORM_LABELS[item.transformId] ?? item.transformId}</span>
          <strong className={stateTone(item.stateVector.state)}>{stateLabel(item.stateVector.state)}</strong>
          <small>D norm {asNumber(item.stateVector.directionalNormalized)}</small>
          <small>M {asNumber(item.modifier.value)}</small>
        </article>)}
      </div>}
    </section>
  )
}

function TrialLedgerPanel({ ledger }: { ledger: ExperimentalTrialLedger | null }) {
  return (
    <section className="xe1-panel xe1-trial-panel" aria-label="Experimental trial ledger">
      <div className="xe1-panel-heading"><div><span>Trial / profile</span><strong>Immutable research ledger</strong></div><span className="xe1-lock-chip">APRIL 2025: TOUCHED DEV</span></div>
      {!ledger && <p className="xe1-empty">Loading trial ledger.</p>}
      {ledger && <>
        <p className="xe1-governance">{ledger.datasetGovernance.exploratoryControlsLabel}. April 2025 is not a pristine holdout, and this lab has no validation result.</p>
        <div className="xe1-trial-list">{ledger.entries.map((entry) => <article key={entry.trialId}>
          <div><strong>{entry.trialId}</strong><span>{entry.datasetStatus} · {entry.result}</span></div>
          <p>{entry.notes}</p><small>Immutable hash {entry.entryHash.slice(0, 16)}...</small>
        </article>)}</div>
      </>}
    </section>
  )
}

export function ExperimentalLabWorkspace({ onOutcomeBlindReviewChange }: { onOutcomeBlindReviewChange?: (active: boolean) => void }) {
  const [researchProfile, setResearchProfile] = useState<'XE1' | 'XE2' | 'XE3'>('XE1')
  const [profile, setProfile] = useState<ExperimentalProfileResponse | null>(null)
  const [snapshot, setSnapshot] = useState<ExperimentalSnapshot | null>(null)
  const [comparison, setComparison] = useState<ExperimentalComparisonResponse | null>(null)
  const [ledger, setLedger] = useState<ExperimentalTrialLedger | null>(null)
  const [dataMode, setDataMode] = useState<ExperimentalDatasetStatus>('SYNTHETIC')
  const [transformId, setTransformId] = useState('XE1_BOUNDED_EXP_MULTIPLIER_V1')
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')
  const requestId = useRef(0)

  const load = useCallback(async (nextDataMode = dataMode, nextTransformId = transformId) => {
    const currentRequest = requestId.current + 1
    requestId.current = currentRequest
    setBusy(true)
    setError('')
    try {
      const [nextProfile, nextSnapshot, nextComparison, nextLedger] = await Promise.all([
        profile ? Promise.resolve(profile) : fetchExperimentalEvidenceProfile(),
        fetchExperimentalEvidenceSnapshot({ dataMode: nextDataMode, transformId: nextTransformId }),
        compareExperimentalEvidenceTransforms({ dataMode: nextDataMode }),
        ledger ? Promise.resolve(ledger) : fetchExperimentalEvidenceTrialLedger(),
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
  }, [dataMode, ledger, profile, transformId])

  useEffect(() => {
    if (researchProfile === 'XE1') void load()
  }, [load, researchProfile])

  useEffect(() => {
    onOutcomeBlindReviewChange?.(researchProfile === 'XE3')
    return () => onOutcomeBlindReviewChange?.(false)
  }, [onOutcomeBlindReviewChange, researchProfile])

  return (
    <section className="experimental-lab" aria-label="Experimental Evidence and Modifier Lab">
      <div className="experimental-safety-banner"><Beaker size={16} /><strong>EXPERIMENTAL - NOT CLASSICAL - NOT VALIDATED - NO EXECUTION</strong><span>Read-only evidence-role and modifier ablation. No price, Fields, SBC, Auto Suggest, ML, MT5, or execution path is connected.</span></div>
      <header className="experimental-lab-header">
        <div><div className="experimental-kicker"><Activity size={14} /> Evidence research workspace</div><h1>Experimental Lab</h1><p>Raw observations are immutable. Roles, causal grouping, and bounded transforms are versioned research objects.</p></div>
        <div className="experimental-controls">
          <label>Research profile<select aria-label="Experimental research profile" value={researchProfile} onChange={(event) => setResearchProfile(event.target.value as 'XE1' | 'XE2' | 'XE3')}><option value="XE1">XE1 synthetic baseline</option><option value="XE2">XE2 scoped evidence</option><option value="XE3">XE3 outcome-blind sign admission</option></select></label>
          {researchProfile === 'XE1' && <><label>Dataset<select aria-label="Experimental dataset mode" value={dataMode} onChange={(event) => { const value = event.target.value as ExperimentalDatasetStatus; setDataMode(value); void load(value, transformId) }} disabled={busy}>{(['SYNTHETIC', 'TOUCHED_DEV', 'MANUAL'] as const).map((mode) => <option key={mode} value={mode}>{DATA_MODE_LABELS[mode]}</option>)}</select></label>
          <label>Transform<select aria-label="Experimental transform" value={transformId} onChange={(event) => { const value = event.target.value; setTransformId(value); void load(dataMode, value) }} disabled={busy}>{Object.entries(TRANSFORM_LABELS).map(([id, label]) => <option key={id} value={id}>{label}</option>)}</select></label>
          <button type="button" className="secondary-command" onClick={() => void load()} disabled={busy} title="Refresh the immutable experimental snapshot"><RefreshCw size={14} className={busy ? 'xe1-spin' : ''} /> Refresh</button></>}
        </div>
      </header>
      {researchProfile === 'XE2' && <Xe2ScopedEvidencePanel />}
      {researchProfile === 'XE3' && <Xe3OutcomeBlindReviewPanel />}
      {researchProfile === 'XE1' && error && <div className="xe1-error"><CircleAlert size={16} /><strong>Experimental lab unavailable</strong><span>{error}</span></div>}
      {researchProfile === 'XE1' && snapshot && <>
        <section className="xe1-context-strip" aria-label="Experimental profile context"><span><BookOpenCheck size={13} /> {profile?.profile.profileId}</span><span>Profile hash {snapshot.profile.profileHash.slice(0, 16)}...</span><span>Code {snapshot.codeCommit.slice(0, 12)}</span><span>{snapshot.datasetLabel}</span><span className="xe1-market-input">MARKET INPUT: NONE</span><span><ShieldCheck size={13} /> execution locked</span></section>
        <ExperimentalStateLane snapshot={snapshot} />
        <div className="xe1-content-grid"><RawEvidenceTable snapshot={snapshot} /><Contributions snapshot={snapshot} /></div>
        <ModifierComparison comparison={comparison} />
        <div className="xe1-bottom-grid">
          <section className="xe1-panel" aria-label="Safety and uncertainty detail"><div className="xe1-panel-heading"><div><span>Safety / uncertainty</span><strong>Confidence is a separate display field</strong></div></div><dl className="xe1-detail-list"><div><dt>Confidence</dt><dd>{asNumber(snapshot.quality.confidence)}</dd></div><div><dt>Use</dt><dd>{snapshot.quality.confidenceUse}</dd></div><div><dt>Unknown groups</dt><dd>{snapshot.stateVector.unknownGroupCount}</dd></div><div><dt>Modifier bounds</dt><dd>{snapshot.modifier.parameters.mMin} to {snapshot.modifier.parameters.mMax}; beta {snapshot.modifier.parameters.beta}</dd></div><div><dt>Sign flip</dt><dd>{snapshot.modifier.nonSignFlipGuaranteed ? 'Impossible for this positive multiplier' : 'Not guaranteed by selected comparison'}</dd></div><div><dt>Execution</dt><dd>Disabled</dd></div></dl></section>
          <TrialLedgerPanel ledger={ledger} />
        </div>
      </>}
    </section>
  )
}
