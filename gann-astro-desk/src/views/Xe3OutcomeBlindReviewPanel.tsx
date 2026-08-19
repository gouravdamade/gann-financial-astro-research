import { ChevronLeft, ChevronRight, CircleAlert, EyeOff, FileCheck2, LockKeyhole, RefreshCw, ShieldCheck } from 'lucide-react'
import { useCallback, useEffect, useMemo, useState } from 'react'
import {
  fetchXe3OutcomeBlindWorkbench,
  fetchXe3Preregistration,
  fetchXe3SignedLedger,
  fetchXe3TransformPreview,
  freezeXe3Preregistration,
  saveXe3OutcomeBlindReviewRevision,
} from '../api'
import { packagedSourceCommit } from '../buildInfo'
import type {
  Xe3Decision,
  Xe3EvidenceClassification,
  Xe3Ledger,
  Xe3Preregistration,
  Xe3Review,
  Xe3ReviewRow,
  Xe3SideWorkbench,
  Xe3TransformComparison,
  Xe3Workbench,
} from '../xe3EvidenceTypes'

const DECISIONS: Xe3Decision[] = [
  'SUPPORTIVE',
  'ADVERSE',
  'MIXED',
  'NEUTRAL',
  'UNKNOWN_MORE_EVIDENCE_REQUIRED',
  'REJECT_EVENT_IDENTITY',
]

const CLASSIFICATIONS: Xe3EvidenceClassification[] = [
  'FOUNDER_RESEARCH_HYPOTHESIS',
  'SOURCE_BACKED_CLASSICAL_CANDIDATE',
]

function ist(value: string): string {
  const date = new Date(value)
  if (Number.isNaN(date.valueOf())) return 'invalid time'
  return new Intl.DateTimeFormat('en-IN', {
    timeZone: 'Asia/Kolkata', year: 'numeric', month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit', hour12: false,
  }).format(date) + ' IST'
}

function shortHash(value: string | null | undefined): string {
  return value ? `${value.slice(0, 18)}...` : 'None yet'
}

function updateRow(side: Xe3SideWorkbench, index: number, updater: (row: Xe3ReviewRow) => Xe3ReviewRow): Xe3SideWorkbench {
  return { ...side, rows: side.rows.map((row, rowIndex) => rowIndex === index ? updater(row) : row) }
}

function panelGuardrails(workbench: Xe3Workbench | null): string {
  if (!workbench) return 'Checking immutable packet and integrity-manifest hashes.'
  return 'This screen contains no price path, live quote, market result, Fields, SBC, Auto Suggest, ML, or execution control.'
}

export function Xe3OutcomeBlindReviewPanel() {
  const [workbench, setWorkbench] = useState<Xe3Workbench | null>(null)
  const [ledger, setLedger] = useState<Xe3Ledger | null>(null)
  const [comparison, setComparison] = useState<Xe3TransformComparison | null>(null)
  const [preregistration, setPreregistration] = useState<Xe3Preregistration | null>(null)
  const [sideIdentity, setSideIdentity] = useState<'USD' | 'JPY'>('USD')
  const [rowIndex, setRowIndex] = useState(0)
  const [reviewer, setReviewer] = useState('')
  const [attested, setAttested] = useState(false)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')
  const [notice, setNotice] = useState('')

  const load = useCallback(async () => {
    setBusy(true)
    setError('')
    try {
      const [nextWorkbench, nextLedger, nextComparison, nextPreregistration] = await Promise.all([
        fetchXe3OutcomeBlindWorkbench(),
        fetchXe3SignedLedger(),
        fetchXe3TransformPreview(),
        fetchXe3Preregistration(),
      ])
      setWorkbench(nextWorkbench)
      setLedger(nextLedger)
      setComparison(nextComparison)
      setPreregistration(nextPreregistration)
      setRowIndex((current) => Math.min(current, Math.max(0, (nextWorkbench.sides.find((side) => side.sideIdentity === sideIdentity)?.rows.length ?? 1) - 1)))
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : String(caught))
    } finally {
      setBusy(false)
    }
  }, [sideIdentity])

  useEffect(() => { void load() }, [load])

  const side = useMemo(() => workbench?.sides.find((candidate) => candidate.sideIdentity === sideIdentity) ?? null, [workbench, sideIdentity])
  const row = side?.rows[rowIndex] ?? null

  const replaceCurrentReview = (updater: (review: Xe3Review) => Xe3Review) => {
    if (!side || !row) return
    setWorkbench((current) => current ? {
      ...current,
      sides: current.sides.map((candidate) => candidate.sideIdentity === sideIdentity
        ? updateRow(candidate, rowIndex, (selected) => ({ ...selected, review: updater(selected.review) }))
        : candidate),
    } : current)
  }

  const changeDecision = (value: string) => {
    const decision = (value || null) as Xe3Decision | null
    replaceCurrentReview((current) => ({
      ...current,
      decision,
      evidenceClassification: decision === null || decision === 'REJECT_EVENT_IDENTITY' ? null : current.evidenceClassification,
      sourceReferences: decision === null || decision === 'REJECT_EVENT_IDENTITY' ? [] : current.sourceReferences,
      rejectionReason: decision === 'REJECT_EVENT_IDENTITY' ? current.rejectionReason : '',
      reasoning: decision === null ? '' : current.reasoning,
    }))
  }

  const saveRevision = async () => {
    if (!side || !attested) return
    setBusy(true)
    setError('')
    setNotice('')
    try {
      const result = await saveXe3OutcomeBlindReviewRevision({
        side: side.sideIdentity,
        baseRevisionHash: side.latestReviewRevisionHash,
        reviewer,
        outcomeBlindAttestation: true,
        rows: side.rows,
      })
      setNotice(`Immutable ${result.sideIdentity} review revision saved: ${shortHash(result.reviewRevisionHash)}. Earlier revisions remain preserved.`)
      await load()
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : String(caught))
    } finally {
      setBusy(false)
    }
  }

  const freeze = async () => {
    if (!preregistration?.freezeReady || !attested || !packagedSourceCommit) return
    setBusy(true)
    setError('')
    setNotice('')
    try {
      const next = await freezeXe3Preregistration(preregistration.ledgerHash, packagedSourceCommit)
      setPreregistration(next)
      setNotice(`Preregistration frozen: ${shortHash(next.frozenRecord?.preregistrationHash)}. Outcome evaluation remains blocked.`)
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : String(caught))
    } finally {
      setBusy(false)
    }
  }

  const projection = ledger?.entries.find((entry) => entry.eventId === row?.eventIdentity.eventId)?.scalarProjection
  const classicalReference = row?.review.sourceReferences[0] ?? { sourceId: '', edition: '', locator: '', connection: '' }
  const transformSummary = comparison?.comparisons.map((item) => ({
    transformId: item.transformId,
    label: item.transform.label,
    state: item.signedStateVector.state,
    active: item.signedStateVector.activity,
  })) ?? []

  return <section className="xe3-workbench" aria-label="XE3 outcome-blind sign admission">
    <header className="xe3-header">
      <div>
        <span className="experimental-kicker"><EyeOff size={14} /> Outcome-blind founder review</span>
        <h2>XE3 Signed Evidence Admission</h2>
        <p>Chart-conditioned research signs are founder-entered and hash-linked. They are not inferred from astronomy and have not been compared with outcomes.</p>
      </div>
      <div className="xe3-header-actions">
        <button type="button" onClick={() => void load()} disabled={busy}><RefreshCw size={13} className={busy ? 'xe1-spin' : ''} /> Refresh integrity</button>
      </div>
    </header>

    <section className="xe3-status-strip" aria-label="XE3 safety status">
      <strong>EXPERIMENTAL - NOT CLASSICAL - NOT VALIDATED - NO EXECUTION</strong>
      <span><EyeOff size={12} /> OUTCOME-BLIND REVIEW - PRICE HIDDEN</span>
      <span>REAL ASTRONOMY: HASH-LINKED</span>
      <span>SIGNED EVIDENCE: {workbench?.signedEvidenceStatus ?? 'CHECKING'}</span>
      <span>OUTCOME EVALUATION: BLOCKED</span>
      <span>DATASET: TOUCHED DEV</span>
    </section>

    <section className="xe3-guardrail" aria-label="Outcome blindness guardrails"><ShieldCheck size={15} /><span>{panelGuardrails(workbench)}</span></section>
    {busy && <p className="xe1-empty">Checking immutable review, ledger, and preregistration records...</p>}
    {error && <p className="xe1-error"><CircleAlert size={15} /> {error}</p>}
    {notice && <p className="xe3-notice">{notice}</p>}

    {workbench && side && row && <>
      <section className="xe3-summary-grid" aria-label="XE3 packet summary">
        {workbench.sides.map((candidate) => <article key={candidate.sideIdentity}>
          <span>{candidate.sideIdentity} packet</span>
          <strong>{candidate.completion.counts.decidedRows}/{candidate.completion.counts.eligibleRows} decided</strong>
          <small>{candidate.completion.status.replaceAll('_', ' ')}</small>
          <code>{shortHash(candidate.blankPacketSha256)}</code>
        </article>)}
        <article><span>Ledger</span><strong>{workbench.signedEvidenceStatus}</strong><small>Immutable hash-linked admissions only</small><code>{shortHash(workbench.ledgerHash)}</code></article>
        <article><span>Preregistration</span><strong>{preregistration?.status ?? 'CHECKING'}</strong><small>{preregistration?.freezeReady ? 'Terminal review packets can freeze.' : 'Waiting for terminal USD and JPY review.'}</small><code>{shortHash(preregistration?.frozenRecord?.preregistrationHash)}</code></article>
      </section>

      <section className="xe3-controls" aria-label="XE3 packet controls">
        <label>Currency-side packet<select value={sideIdentity} onChange={(event) => { setSideIdentity(event.target.value as 'USD' | 'JPY'); setRowIndex(0) }} disabled={busy}><option value="USD">USD</option><option value="JPY">JPY</option></select></label>
        <span>{side.chartId}</span><span>{side.chartHypothesisId}</span>
        <code>Packet {shortHash(side.blankPacketSha256)}</code><code>Integrity {shortHash(side.identityIntegrityManifestSha256)}</code>
      </section>

      <section className="xe3-review-shell" aria-label={`${sideIdentity} verified event review`}>
        <nav className="xe3-event-navigator" aria-label="Verified event navigator">
          <button type="button" onClick={() => setRowIndex((current) => Math.max(0, current - 1))} disabled={busy || rowIndex === 0} aria-label="Previous verified event"><ChevronLeft size={16} /></button>
          <div><span>{sideIdentity} verified event {rowIndex + 1} of {side.rows.length}</span><strong>{row.eventIdentity.transitBody} to {row.eventIdentity.natalTarget} | {row.eventIdentity.aspectType}</strong><small>{row.identityStatus.replaceAll('_', ' ')}</small></div>
          <button type="button" onClick={() => setRowIndex((current) => Math.min(side.rows.length - 1, current + 1))} disabled={busy || rowIndex === side.rows.length - 1} aria-label="Next verified event"><ChevronRight size={16} /></button>
        </nav>

        <div className="xe3-review-grid">
          <section className="xe3-event-provenance">
            <div className="xe1-panel-heading"><div><span>Immutable event provenance</span><strong>Packet-verified astronomy facts only</strong></div><span className="xe1-lock-chip"><LockKeyhole size={12} /> SINGLE PASS VERIFIED</span></div>
            <dl>
              <div><dt>Event ID</dt><dd><code>{row.eventIdentity.eventId}</code></dd></div>
              <div><dt>Event hash</dt><dd><code>{row.eventIdentity.eventHash}</code></dd></div>
              <div><dt>Exact UTC / IST</dt><dd>{row.eventIdentity.exactUtc} | {ist(row.eventIdentity.exactUtc)}</dd></div>
              <div><dt>Applying / separating</dt><dd>{row.eventIdentity.applyingStartUtc} / {row.eventIdentity.separatingEndUtc}</dd></div>
              <div><dt>Chart identity</dt><dd>{row.eventIdentity.chartId}</dd></div>
              <div><dt>Chart hypothesis</dt><dd>{row.eventIdentity.chartHypothesisId}</dd></div>
              <div><dt>Astronomy</dt><dd>{row.eventIdentity.astronomyContract} | {row.eventIdentity.ayanamsha} | {row.eventIdentity.nodePolicy}</dd></div>
              <div><dt>Orb profile</dt><dd>{row.eventIdentity.orbContract.profileId} | exact {row.eventIdentity.orbContract.exactAngleDeg} deg | max {row.eventIdentity.orbContract.maxOrbDeg} deg</dd></div>
              <div><dt>Motion at exactness</dt><dd>{row.motionPhaseAtExact ? `${row.motionPhaseAtExact.phase} | ${row.motionPhaseAtExact.speedDegPerDay} deg/day` : 'Recorded identity context unavailable'}</dd></div>
            </dl>
          </section>

          <section className="xe3-decision-editor">
            <div className="xe1-panel-heading"><div><span>Founder research decision</span><strong>No automatic sign suggestion</strong></div><span className="xe1-note-chip">PRICE HIDDEN</span></div>
            <label>Decision<select aria-label="XE3 decision" value={row.review.decision ?? ''} onChange={(event) => changeDecision(event.target.value)} disabled={busy}><option value="">Leave undecided</option>{DECISIONS.map((decision) => <option key={decision} value={decision}>{decision.replaceAll('_', ' ')}</option>)}</select></label>
            {row.review.decision && row.review.decision !== 'REJECT_EVENT_IDENTITY' && <label>Evidence classification<select aria-label="XE3 evidence classification" value={row.review.evidenceClassification ?? ''} onChange={(event) => replaceCurrentReview((current) => ({ ...current, evidenceClassification: (event.target.value || null) as Xe3EvidenceClassification | null, sourceReferences: event.target.value === 'SOURCE_BACKED_CLASSICAL_CANDIDATE' ? (current.sourceReferences.length ? current.sourceReferences : [{ sourceId: '', edition: '', locator: '', connection: '' }]) : [] }))} disabled={busy}><option value="">Choose classification</option>{CLASSIFICATIONS.map((classification) => <option key={classification} value={classification}>{classification.replaceAll('_', ' ')}</option>)}</select></label>}
            {row.review.decision && row.review.decision !== 'REJECT_EVENT_IDENTITY' && <label>Reasoning{row.review.decision === 'UNKNOWN_MORE_EVIDENCE_REQUIRED' ? ' (optional reason code)' : ' (required)'}<textarea value={row.review.reasoning} onChange={(event) => replaceCurrentReview((current) => ({ ...current, reasoning: event.target.value }))} disabled={busy} placeholder="Founder-entered research rationale only" /></label>}
            {row.review.decision === 'REJECT_EVENT_IDENTITY' && <label>Rejection reason (required)<textarea value={row.review.rejectionReason} onChange={(event) => replaceCurrentReview((current) => ({ ...current, rejectionReason: event.target.value }))} disabled={busy} placeholder="Why this verified identity must be excluded" /></label>}
            {row.review.evidenceClassification === 'SOURCE_BACKED_CLASSICAL_CANDIDATE' && <fieldset className="xe3-source-reference"><legend>Exact source reference</legend><label>Source ID<input value={classicalReference.sourceId} onChange={(event) => replaceCurrentReview((current) => ({ ...current, sourceReferences: [{ ...classicalReference, sourceId: event.target.value }] }))} disabled={busy} /></label><label>Edition<input value={classicalReference.edition} onChange={(event) => replaceCurrentReview((current) => ({ ...current, sourceReferences: [{ ...classicalReference, edition: event.target.value }] }))} disabled={busy} /></label><label>Printed page / locator<input value={classicalReference.locator} onChange={(event) => replaceCurrentReview((current) => ({ ...current, sourceReferences: [{ ...classicalReference, locator: event.target.value }] }))} disabled={busy} /></label><label>Connection to event<textarea value={classicalReference.connection} onChange={(event) => replaceCurrentReview((current) => ({ ...current, sourceReferences: [{ ...classicalReference, connection: event.target.value }] }))} disabled={busy} /></label></fieldset>}
            <section className="xe3-projection"><span>Scalar projection</span><strong>{projection ? `${projection.status}${projection.value == null ? '' : ` | ${projection.value.toFixed(1)}`}` : 'NO REVIEW DECISION'}</strong><small>Only explicit NEUTRAL is numeric zero. MIXED and UNKNOWN remain non-projectable.</small></section>
          </section>
        </div>

        <footer className="xe3-save-bar">
          <label>Reviewer<input aria-label="XE3 reviewer" value={reviewer} onChange={(event) => setReviewer(event.target.value)} placeholder="Required for any decided row" disabled={busy} /></label>
          <label className="xe3-attestation"><input aria-label="Outcome-blind attestation" type="checkbox" checked={attested} onChange={(event) => setAttested(event.target.checked)} disabled={busy} /> I attest this decision was made without viewing price or outcome data.</label>
          <button type="button" onClick={() => void saveRevision()} disabled={busy || !attested || !reviewer.trim()}><FileCheck2 size={14} /> Save immutable {sideIdentity} revision</button>
        </footer>
      </section>

      <section className="xe3-transform-panel" aria-label="XE3 M0-M4 outcome-free preview">
        <div className="xe1-panel-heading"><div><span>Frozen XE2 M0-M4 preview</span><strong>REAL SIGNED EVIDENCE - OUTCOME NOT EVALUATED</strong></div><span className="xe1-lock-chip">NO WINNER</span></div>
        <p>Only projectable reviewed signs in the frozen XE2 causal cohort can appear here. Moon speed stays bound to its own causal event; there is no global modifier or stacking.</p>
        <div>{transformSummary.map((item) => <article key={item.transformId}><span>{item.transformId}</span><strong>{item.label}</strong><small>{item.state} | activity {item.active.toFixed(3)}</small></article>)}</div>
      </section>

      <section className="xe3-freeze-panel" aria-label="XE3 preregistration freeze">
        <div><span>Preregistered causal modifier trial</span><strong>{preregistration?.status ?? 'CHECKING'}</strong><p>Freezing captures the reviewed packet hashes, causal identities, scalar mapping, unchanged M0-M4 parameters, and exact packaged source commit. It does not authorize an outcome read.</p>{!packagedSourceCommit && <small>Freeze is unavailable in an unbound development build. A founder candidate binds the exact source commit.</small>}</div>
        <button type="button" onClick={() => void freeze()} disabled={busy || !attested || !preregistration?.freezeReady || preregistration.status === 'FROZEN' || !packagedSourceCommit}>Freeze signed-evidence trial</button>
      </section>
    </>}
  </section>
}
