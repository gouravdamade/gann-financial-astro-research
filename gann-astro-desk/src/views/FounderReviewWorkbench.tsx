import { ClipboardCheck, RefreshCw, ShieldCheck } from 'lucide-react'
import { useCallback, useEffect, useState } from 'react'
import {
  exportFounderReviewPacket,
  fetchFounderReviewWorkbench,
} from '../api'
import type {
  FounderReviewDecision,
  FounderReviewEvidenceClassification,
  FounderReviewExportRequest,
  FounderReviewFields,
  FounderReviewSide,
  FounderReviewSourceReference,
  FounderReviewWorkbench,
  FounderReviewWorkbenchRow,
} from '../types'

type Props = {
  onClose: () => void
  onDirtyChange?: (dirty: boolean) => void
}

type ExportOutcome = {
  side: FounderReviewSide['sideIdentity']
  status: 'committed' | 'failed'
  revisionId?: string
  revisionHash?: string
  error?: string
}

const EMPTY_SOURCE_REFERENCE: FounderReviewSourceReference = {
  sourceId: '',
  edition: '',
  locator: '',
  connection: '',
}

const DECISIONS: FounderReviewDecision[] = [
  'SUPPORTIVE',
  'ADVERSE',
  'MIXED',
  'NEUTRAL',
  'UNKNOWN_MORE_EVIDENCE_REQUIRED',
  'REJECT_EVENT_IDENTITY',
]

const CLASSIFICATIONS: FounderReviewEvidenceClassification[] = [
  'FOUNDER_RESEARCH_HYPOTHESIS',
  'SOURCE_BACKED_CLASSICAL_CANDIDATE',
]

function istLabel(value: string): string {
  const date = new Date(value)
  if (Number.isNaN(date.valueOf())) return 'invalid time'
  return new Intl.DateTimeFormat('en-IN', {
    timeZone: 'Asia/Kolkata',
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
    hour12: false,
  }).format(date) + ' IST'
}

function timePair(value: string): string {
  return `${value} | ${istLabel(value)}`
}

function updateSide(
  current: FounderReviewWorkbench,
  sideIdentity: 'USD' | 'JPY',
  update: (side: FounderReviewSide) => FounderReviewSide,
): FounderReviewWorkbench {
  return {
    ...current,
    sides: current.sides.map((side) => side.sideIdentity === sideIdentity ? update(side) : side),
  }
}

function updateRow(
  current: FounderReviewWorkbench,
  sideIdentity: 'USD' | 'JPY',
  eventId: string,
  update: (row: FounderReviewWorkbenchRow) => FounderReviewWorkbenchRow,
): FounderReviewWorkbench {
  return updateSide(current, sideIdentity, (side) => ({
    ...side,
    rows: side.rows.map((row) => row.eventIdentity.eventId === eventId ? update(row) : row),
  }))
}

function updateReview(
  current: FounderReviewWorkbench,
  sideIdentity: 'USD' | 'JPY',
  row: FounderReviewWorkbenchRow,
  update: (review: FounderReviewFields) => FounderReviewFields,
): FounderReviewWorkbench {
  return updateRow(current, sideIdentity, row.eventIdentity.eventId, (currentRow) => ({
    ...currentRow,
    founderReview: update(currentRow.founderReview),
  }))
}

function updateExportedSide(
  current: FounderReviewWorkbench,
  sideIdentity: FounderReviewSide['sideIdentity'],
  result: {
    founderCompletionStatus: FounderReviewSide['founderCompletionStatus']
    counts: FounderReviewSide['completeness']
    reviewedPacketHash: string
    revisionId: string
    revisionHash: string
    previousRevisionHash: string | null
    reviewStoreContract: string
  },
): FounderReviewWorkbench {
  return updateSide(current, sideIdentity, (side) => ({
    ...side,
    founderCompletionStatus: result.founderCompletionStatus,
    completeness: result.counts,
    reviewedPacketHash: result.reviewedPacketHash,
    currentRevisionId: result.revisionId,
    currentRevisionHash: result.revisionHash,
    previousRevisionHash: result.previousRevisionHash,
    reviewStoreContract: result.reviewStoreContract,
  }))
}

function formatExportError(caught: unknown): string {
  const message = caught instanceof Error ? caught.message : String(caught)
  if (typeof caught !== 'object' || caught === null) return message
  const candidate = caught as {
    status?: unknown
    errorCode?: unknown
    conflict?: {
      currentRevisionId?: unknown
      currentRevisionHash?: unknown
    }
    details?: {
      errorCode?: unknown
      conflict?: {
        currentRevisionId?: unknown
        currentRevisionHash?: unknown
      }
    }
  }
  const details = candidate.details ?? candidate
  const errorCode = typeof candidate.errorCode === 'string'
    ? candidate.errorCode
    : typeof details.errorCode === 'string' ? details.errorCode : null
  const status = typeof candidate.status === 'number' ? candidate.status : null
  const prefix = errorCode && !message.includes(errorCode)
    ? `${errorCode}: `
    : !errorCode && status !== null && !message.includes(`HTTP ${status}`)
      ? `HTTP ${status}: `
      : ''
  const conflict = details.conflict
  const currentRevision = conflict
    && (typeof conflict.currentRevisionId === 'string' || typeof conflict.currentRevisionHash === 'string')
    ? ` Current revision ${typeof conflict.currentRevisionId === 'string' ? conflict.currentRevisionId : 'unknown'} (${typeof conflict.currentRevisionHash === 'string' ? conflict.currentRevisionHash : 'no hash'}) remains authoritative.`
    : ''
  return `${prefix}${message}${currentRevision}`
}

function Fact({ label, value }: { label: string; value: string }) {
  return <div className="founder-review-fact"><dt>{label}</dt><dd>{value}</dd></div>
}

function sourceReferenceFor(row: FounderReviewWorkbenchRow): FounderReviewSourceReference {
  return row.founderReview.sourceReferences[0] ?? EMPTY_SOURCE_REFERENCE
}

function ReviewRow({
  side,
  row,
  setWorkbench,
}: {
  side: FounderReviewSide
  row: FounderReviewWorkbenchRow
  setWorkbench: React.Dispatch<React.SetStateAction<FounderReviewWorkbench | null>>
}) {
  const event = row.eventIdentity
  const review = row.founderReview
  const decision = review.reviewedPolarity
  const reasoningRequired = decision === 'SUPPORTIVE' || decision === 'ADVERSE'
  const sourceReference = sourceReferenceFor(row)
  const changeReview = (update: (value: FounderReviewFields) => FounderReviewFields) => {
    setWorkbench((current) => current ? updateReview(current, side.sideIdentity, row, update) : current)
  }
  const changeDecision = (value: string) => {
    const nextDecision = (value || null) as FounderReviewDecision | null
    changeReview((current) => ({
      ...current,
      reviewedPolarity: nextDecision,
      evidenceClassification: nextDecision === 'REJECT_EVENT_IDENTITY' || nextDecision === null
        ? null
        : current.evidenceClassification,
      sourceReferences: nextDecision === 'REJECT_EVENT_IDENTITY' || nextDecision === null
        ? []
        : current.sourceReferences,
      rejectionReason: nextDecision === 'REJECT_EVENT_IDENTITY' ? current.rejectionReason : '',
    }))
  }
  const changeClassification = (value: string) => {
    const classification = (value || null) as FounderReviewEvidenceClassification | null
    changeReview((current) => ({
      ...current,
      evidenceClassification: classification,
      sourceReferences: classification === 'SOURCE_BACKED_CLASSICAL_CANDIDATE'
        ? (current.sourceReferences.length ? current.sourceReferences : [{ ...EMPTY_SOURCE_REFERENCE }])
        : [],
    }))
  }
  const changeSourceReference = (key: keyof FounderReviewSourceReference, value: string) => {
    changeReview((current) => {
      const sourceReferences = current.sourceReferences.length
        ? [...current.sourceReferences]
        : [{ ...EMPTY_SOURCE_REFERENCE }]
      sourceReferences[0] = { ...sourceReferences[0], [key]: value }
      return { ...current, sourceReferences }
    })
  }
  return <article className={`founder-review-row${row.eligible ? '' : ' is-locked'}`}>
    <header>
      <div><span className="founder-review-row-number">{event.eventId}</span><strong>{event.transitBody} to {event.natalTarget} | {event.aspectType}</strong></div>
      <span className={row.eligible ? 'founder-review-eligible' : 'founder-review-ineligible'}>{row.identityStatus.replaceAll('_', ' ')}</span>
    </header>
    <dl className="founder-review-facts">
      <Fact label="Side" value={event.sideIdentity} />
      <Fact label="Chart" value={event.chartId} />
      <Fact label="Hypothesis" value={event.chartHypothesisId} />
      <Fact label="Applying / exact / separating" value={`${timePair(event.applyingStartUtc)} | ${timePair(event.exactUtc)} | ${timePair(event.separatingEndUtc)}`} />
      <Fact label="Event hash" value={event.eventHash} />
      <Fact label="Astronomy" value={`${event.astronomyContract} | ${event.ayanamsha} | ${event.nodePolicy}`} />
      <Fact label="Orb profile" value={`${event.orbContract.profileId} | exact ${event.orbContract.exactAngleDeg} deg | max ${event.orbContract.maxOrbDeg} deg`} />
      <Fact label="Motion at exactness" value={row.motionPhaseAtExact ? `${row.motionPhaseAtExact.phase} | ${row.motionPhaseAtExact.speedDegPerDay} deg/day` : 'Not recorded in identity audit'} />
    </dl>
    {row.eligible ? <fieldset className="founder-review-decision-fields">
      <legend>Founder decision</legend>
      <label>Decision
        <select value={decision ?? ''} onChange={(eventChange) => changeDecision(eventChange.target.value)}>
          <option value="">Choose founder decision</option>
          {DECISIONS.map((option) => <option key={option} value={option}>{option.replaceAll('_', ' ')}</option>)}
        </select>
      </label>
      {decision && decision !== 'REJECT_EVENT_IDENTITY' && <label>Evidence classification
        <select value={review.evidenceClassification ?? ''} onChange={(eventChange) => changeClassification(eventChange.target.value)}>
          <option value="">Choose evidence classification</option>
          {CLASSIFICATIONS.map((option) => <option key={option} value={option}>{option.replaceAll('_', ' ')}</option>)}
        </select>
      </label>}
      {decision === 'REJECT_EVENT_IDENTITY' && <label>Founder rejection reason
        <textarea value={review.rejectionReason} onChange={(eventChange) => changeReview((current) => ({ ...current, rejectionReason: eventChange.target.value }))} placeholder="Why is this event identity rejected?" />
      </label>}
      {decision && decision !== 'REJECT_EVENT_IDENTITY' && <label>Founder reasoning {reasoningRequired ? '(required)' : '(optional)'}
        <textarea value={review.founderReasoning} onChange={(eventChange) => changeReview((current) => ({ ...current, founderReasoning: eventChange.target.value }))} placeholder={reasoningRequired ? 'Enter founder reasoning before exporting' : 'Optional founder reasoning'} required={reasoningRequired} aria-required={reasoningRequired} />
        {reasoningRequired && !review.founderReasoning.trim() && <small>Required for SUPPORTIVE and ADVERSE decisions.</small>}
      </label>}
      {review.evidenceClassification === 'SOURCE_BACKED_CLASSICAL_CANDIDATE' && <div className="founder-review-source-fields">
        <strong>Exact source reference required</strong>
        <label>Source ID<input value={sourceReference.sourceId} onChange={(eventChange) => changeSourceReference('sourceId', eventChange.target.value)} /></label>
        <label>Edition<input value={sourceReference.edition} onChange={(eventChange) => changeSourceReference('edition', eventChange.target.value)} /></label>
        <label>Printed page / locator<input value={sourceReference.locator} onChange={(eventChange) => changeSourceReference('locator', eventChange.target.value)} /></label>
        <label>Connection to this event<textarea value={sourceReference.connection} onChange={(eventChange) => changeSourceReference('connection', eventChange.target.value)} /></label>
      </div>}
    </fieldset> : <p className="founder-review-fail-closed">This row is not reviewable because its immutable identity checks did not pass.</p>}
  </article>
}

export function FounderReviewWorkbench({ onClose, onDirtyChange }: Props) {
  const [workbench, setWorkbench] = useState<FounderReviewWorkbench | null>(null)
  const [reviewer, setReviewer] = useState('')
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')
  const [notice, setNotice] = useState('')
  const [exportOutcomes, setExportOutcomes] = useState<ExportOutcome[]>([])
  const [dirty, setDirty] = useState(false)
  const [pendingAction, setPendingAction] = useState<'reload' | 'close' | null>(null)

  const load = useCallback(async () => {
    setBusy(true)
    setError('')
    setExportOutcomes([])
    try {
      setWorkbench(await fetchFounderReviewWorkbench())
      setDirty(false)
      setPendingAction(null)
    } catch (caught) {
      setWorkbench(null)
      setError(caught instanceof Error ? caught.message : String(caught))
    } finally {
      setBusy(false)
    }
  }, [])

  useEffect(() => { void load() }, [load])

  useEffect(() => {
    onDirtyChange?.(dirty)
  }, [dirty, onDirtyChange])

  useEffect(() => {
    const preventLoss = (event: BeforeUnloadEvent) => {
      if (!dirty) return
      event.preventDefault()
      event.returnValue = ''
    }
    window.addEventListener('beforeunload', preventLoss)
    return () => window.removeEventListener('beforeunload', preventLoss)
  }, [dirty])

  const updateWorkbench = (update: React.SetStateAction<FounderReviewWorkbench | null>) => {
    setDirty(true)
    setWorkbench(update)
  }

  const persistPackets = async (): Promise<boolean> => {
    if (!workbench) return false
    setBusy(true)
    setError('')
    setNotice('')
    setExportOutcomes([])
    try {
      for (const side of workbench.sides) {
        for (const row of side.rows) {
          const decision = row.founderReview.reviewedPolarity
          if ((decision === 'SUPPORTIVE' || decision === 'ADVERSE') && !row.founderReview.founderReasoning.trim()) {
            throw new Error(`${side.sideIdentity} ${row.eventIdentity.eventId}: ${decision} requires non-empty founder reasoning`)
          }
        }
      }
      const outcomes: ExportOutcome[] = []
      let updatedWorkbench = workbench
      for (const side of workbench.sides) {
        const rows = side.rows.map((row) => row.founderReview.reviewedPolarity && !row.founderReview.reviewer
          ? { ...row, founderReview: { ...row.founderReview, reviewer } }
          : row)
        const request: FounderReviewExportRequest = {
          side: side.sideIdentity,
          baseRevisionHash: side.currentRevisionHash,
          rows,
        }
        try {
          const result = await exportFounderReviewPacket(request)
          outcomes.push({
            side: side.sideIdentity,
            status: 'committed',
            revisionId: result.revisionId,
            revisionHash: result.revisionHash,
          })
          updatedWorkbench = updateExportedSide(updatedWorkbench, side.sideIdentity, result)
          setWorkbench(updatedWorkbench)
        } catch (caught) {
          outcomes.push({
            side: side.sideIdentity,
            status: 'failed',
            error: formatExportError(caught),
          })
        }
      }
      setExportOutcomes(outcomes)
      const failures = outcomes.filter((outcome) => outcome.status === 'failed')
      if (failures.length > 0) {
        setDirty(true)
        setNotice('Founder-review export incomplete. Only the sides marked committed were saved; failed-side edits remain unsaved and dirty.')
        return false
      }
      setDirty(false)
      setNotice('Founder-review export committed independently for every side.')
      await load()
      setExportOutcomes(outcomes)
      return true
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : String(caught))
      return false
    } finally {
      setBusy(false)
    }
  }

  const exportPackets = () => { void persistPackets() }
  const requestReload = () => {
    if (dirty) setPendingAction('reload')
    else void load()
  }
  const requestClose = () => {
    if (dirty) setPendingAction('close')
    else onClose()
  }
  const discardPending = () => {
    const action = pendingAction
    setPendingAction(null)
    setDirty(false)
    if (action === 'close') onClose()
    if (action === 'reload') void load()
  }
  const savePending = async () => {
    const action = pendingAction
    if (!action) return
    const saved = await persistPackets()
    if (saved && action === 'close') {
      setPendingAction(null)
      onClose()
    }
  }

  return <section className="founder-review-workbench" aria-label="Founder review workbench">
    <header className="founder-review-header">
      <div><ClipboardCheck size={18} /><div><strong>Founder Review</strong><span>Neutral astronomy packet review; every decision remains founder-entered.</span></div></div>
      <div className="founder-review-actions"><button type="button" onClick={requestReload} disabled={busy}><RefreshCw size={13} /> Refresh integrity</button><button type="button" onClick={requestClose} disabled={busy}>Back to Fields</button></div>
    </header>
    <section className="founder-review-guardrails" aria-label="Founder review guardrails">
      <ShieldCheck size={15} /><span>Blank packets are read-only. No price, SBC, LLM, catalogue admission, wave, market interpretation, Auto Suggest, or execution path is used here.</span>
    </section>
    {busy && <p className="founder-review-message">Checking packet and identity-manifest hashes...</p>}
    {error && <p className="founder-review-error">{error}</p>}
    {notice && <p className="founder-review-notice">{notice}</p>}
    {exportOutcomes.length > 0 && <section className="founder-review-export-results" aria-label="Founder review export result">
      <strong>{exportOutcomes.some((outcome) => outcome.status === 'failed') ? 'Partial founder-review export' : 'Founder-review export committed'}</strong>
      <ul>
        {exportOutcomes.map((outcome) => <li key={outcome.side} className={outcome.status === 'committed' ? 'is-committed' : 'is-failed'}>
          {outcome.status === 'committed'
            ? <><strong>{outcome.side} committed</strong><span>Revision {outcome.revisionId} | hash {outcome.revisionHash}</span></>
            : <><strong>{outcome.side} failed</strong><span>{outcome.error}</span></>}
        </li>)}
      </ul>
      {exportOutcomes.some((outcome) => outcome.status === 'failed') && <p>The failed side remains dirty for retry or discard. This is not an all-sides save.</p>}
    </section>}
    {workbench && <>
      <section className="founder-review-summary" aria-label="Founder review summary">
        {workbench.sides.map((side) => <div key={side.sideIdentity}><strong>{side.sideIdentity}</strong><span>{side.completeness.decidedRows}/{side.completeness.eligibleRows} decided</span><span>{side.founderCompletionStatus.replaceAll('_', ' ')}</span><small>{side.blankPacketSha256}</small></div>)}
      </section>
      <label className="founder-review-reviewer">Reviewer for new decisions
        <input value={reviewer} onChange={(event) => { setDirty(true); setReviewer(event.target.value) }} placeholder="Enter your name before exporting decided rows" />
      </label>
      {dirty && <p className="founder-review-dirty" role="status">Unsaved founder-review edits are present.</p>}
      <p className="founder-review-instruction">Choose a decision only when you are ready. A blank decision remains blank; UNKNOWN_MORE_EVIDENCE_REQUIRED remains an unknown gap and is never converted to NEUTRAL.</p>
      {workbench.sides.map((side) => <section key={side.sideIdentity} className="founder-review-side" aria-label={`${side.sideIdentity} founder review`}>
        <header><div><strong>{side.sideIdentity}</strong><span>{side.chartId} | {side.chartHypothesisId}</span><small>{side.eventCompiler.ephemerisProvider} {side.ephemerisVersion} | {side.ephemerisVersionProvenance.replaceAll('_', ' ')}</small></div><span>{side.identityIntegrityManifestFile} {side.currentRevisionId ? `| ${side.currentRevisionId}` : '| no saved revision'}</span></header>
        {side.rows.map((row) => <ReviewRow key={row.eventIdentity.eventId} side={side} row={row} setWorkbench={updateWorkbench} />)}
      </section>)}
      <footer className="founder-review-footer"><button type="button" onClick={() => void exportPackets()} disabled={busy}>Export founder-review packets</button><span>Exports remain disconnected from the polarity catalogue and all execution paths.</span></footer>
    </>}
    {pendingAction && <section className="founder-review-unsaved-dialog" role="alertdialog" aria-label="Unsaved founder review edits">
      <strong>Unsaved founder-review edits</strong>
      <span>{pendingAction === 'reload' ? 'Refresh integrity would discard the current edits.' : 'Back to Fields would discard the current edits.'}</span>
      <div><button type="button" onClick={() => void savePending()} disabled={busy}>Save changes</button><button type="button" onClick={discardPending} disabled={busy}>Discard changes</button><button type="button" onClick={() => setPendingAction(null)} disabled={busy}>Cancel</button></div>
    </section>}
  </section>
}
