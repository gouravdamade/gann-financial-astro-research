import {
  BookmarkPlus,
  Clock3,
  Columns3,
  Download,
  FileCheck2,
  GitBranch,
  ListChecks,
  PackageCheck,
  Plus,
  Radar,
  RefreshCw,
  ShieldAlert,
  Table2,
  Trash2,
  Upload,
} from 'lucide-react'
import { useMemo, useRef, useState } from 'react'
import {
  buildChakraLabAuditPackage,
  fetchChakraLabAudit,
  verifyChakraLabAuditPackage,
} from '../api'
import type {
  ChakraAuditBookmarkInput,
  ChakraAuditBookmarkTarget,
  ChakraAuditInterval,
  ChakraAuditLedgerCell,
  ChakraAuditPackageBuild,
  ChakraAuditPackageVerification,
  ChakraAuditRay,
  ChakraLabAuditBoundaryInput,
  ChakraLabAuditRequest,
  ChakraLabRequest,
  ChakraLinkedAuditView,
  ChakraReproducibleAuditPackage,
} from '../types'


type AuditTab =
  | 'TIMELINE'
  | 'LEDGER'
  | 'RAY_AUDIT'
  | 'SOURCE_LINEAGE'
  | 'RECONCILIATION'
  | 'VALIDATION'
  | 'COMPARE'
  | 'PACKAGE'

const TAB_ICONS = {
  TIMELINE: Clock3,
  LEDGER: Table2,
  RAY_AUDIT: Radar,
  SOURCE_LINEAGE: GitBranch,
  RECONCILIATION: ListChecks,
  VALIDATION: ShieldAlert,
  COMPARE: Columns3,
  PACKAGE: PackageCheck,
} as const

function offsetIst(value: string): string {
  return `${value}${value.length === 16 ? ':00' : ''}+05:30`
}

function istInput(value: string): string {
  const date = new Date(value)
  return new Date(date.getTime() + 330 * 60 * 1000).toISOString().slice(0, 16)
}

function plusHour(value: string): string {
  const date = new Date(value)
  return istInput(new Date(date.getTime() + 60 * 60 * 1000).toISOString())
}

function shortId(value: string | null | undefined): string {
  return value ? value.slice(0, 10) : '-'
}

function displayToken(value: string | null | undefined): string {
  if (!value) return 'Unavailable'
  return value
    .replaceAll('_', ' ')
    .toLowerCase()
    .replace(/\b\w/g, (letter) => letter.toUpperCase())
}

function formatMoment(value: string): string {
  return new Intl.DateTimeFormat('en-IN', {
    dateStyle: 'medium',
    timeStyle: 'short',
    timeZone: 'Asia/Kolkata',
  }).format(new Date(value))
}

function formatDuration(seconds: number): string {
  const hours = Math.floor(seconds / 3600)
  const minutes = Math.floor((seconds % 3600) / 60)
  return hours ? `${hours}h ${minutes}m` : `${minutes}m`
}

function units(value: number): string {
  return value.toFixed(2)
}

function signedUnits(value: number): string {
  return `${value >= 0 ? '+' : ''}${value.toFixed(2)}`
}

function downloadText(content: string, type: string, filename: string) {
  const url = URL.createObjectURL(new Blob([content], { type }))
  const link = document.createElement('a')
  link.href = url
  link.download = filename
  link.click()
  URL.revokeObjectURL(url)
}

type Props = {
  currentRequest: ChakraLabRequest
}

export function SbcLinkedAuditWorkspace({ currentRequest }: Props) {
  const [instrumentIdentity, setInstrumentIdentity] = useState('FX:USDJPY')
  const [boundaryLocal, setBoundaryLocal] = useState(() => istInput(currentRequest.at))
  const [boundaryReason, setBoundaryReason] = useState('manual review boundary')
  const [terminalLocal, setTerminalLocal] = useState(() => plusHour(currentRequest.at))
  const [boundaries, setBoundaries] = useState<ChakraLabAuditBoundaryInput[]>([])
  const [audit, setAudit] = useState<ChakraLinkedAuditView | null>(null)
  const [activeTab, setActiveTab] = useState<AuditTab>('TIMELINE')
  const [selectedIntervalId, setSelectedIntervalId] = useState('')
  const [selectedClusterId, setSelectedClusterId] = useState('')
  const [selectedCellId, setSelectedCellId] = useState('')
  const [baselineIntervalId, setBaselineIntervalId] = useState('')
  const [comparisonIntervalIds, setComparisonIntervalIds] = useState<string[]>([])
  const [bookmarks, setBookmarks] = useState<ChakraAuditBookmarkInput[]>([])
  const [bookmarkTargetType, setBookmarkTargetType] = useState<ChakraAuditBookmarkTarget>('INTERVAL')
  const [bookmarkLabel, setBookmarkLabel] = useState('')
  const [bookmarkNote, setBookmarkNote] = useState('')
  const [packageBuild, setPackageBuild] = useState<ChakraAuditPackageBuild | null>(null)
  const [verification, setVerification] = useState<ChakraAuditPackageVerification | null>(null)
  const [busy, setBusy] = useState(false)
  const [packageBusy, setPackageBusy] = useState(false)
  const [error, setError] = useState('')
  const importInputRef = useRef<HTMLInputElement>(null)

  const selectedInterval = audit?.intervals.find(
    (item) => item.interval_id === selectedIntervalId,
  ) ?? audit?.intervals[0] ?? null
  const intervalId = selectedInterval?.interval_id ?? ''
  const ledgerRows = audit?.ledger_cells.filter(
    (item) => item.interval_id === intervalId,
  ) ?? []
  const rayRows = audit?.ray_rows.filter(
    (item) => item.interval_id === intervalId,
  ) ?? []
  const lineageRows = audit?.lineage_rows.filter(
    (item) => item.interval_id === intervalId,
  ) ?? []
  const reconciliationRows = audit?.reconciliations.filter(
    (item) => item.interval_id === intervalId,
  ) ?? []
  const selectedCluster = audit?.ray_rows.find(
    (item) => item.cluster_id === selectedClusterId,
  ) ?? null
  const selectedLineage = audit?.lineage_rows.find(
    (item) => item.cluster_id === selectedClusterId,
  ) ?? null
  const selectedCell = audit?.ledger_cells.find(
    (item) => item.cell_id === selectedCellId,
  ) ?? null
  const bookmarkTargetId = bookmarkTargetType === 'AUDIT'
    ? audit?.audit_view_id ?? ''
    : bookmarkTargetType === 'INTERVAL'
      ? selectedInterval?.interval_id ?? ''
      : bookmarkTargetType === 'CELL'
        ? selectedCell?.cell_id ?? ''
        : selectedCluster?.cluster_id ?? ''
  const packageComparisons = packageBuild?.package.comparisons ?? []

  const sortedBoundaries = useMemo(
    () => [...boundaries].sort(
      (left, right) => left.request.at.localeCompare(right.request.at),
    ),
    [boundaries],
  )

  const auditRequest = (): ChakraLabAuditRequest => ({
    instrumentIdentity: instrumentIdentity.trim(),
    terminalEnd: offsetIst(terminalLocal),
    boundaries: sortedBoundaries,
  })

  const resetPackage = () => {
    setPackageBuild(null)
    setVerification(null)
  }

  const captureBoundary = () => {
    const capturedAt = offsetIst(boundaryLocal)
    if (boundaries.some((item) => item.request.at === capturedAt)) {
      setError('That boundary moment is already captured.')
      return
    }
    const captured: ChakraLabAuditBoundaryInput = {
      reason: boundaryReason.trim() || 'manual review boundary',
      request: {
        ...structuredClone(currentRequest),
        at: capturedAt,
      },
    }
    setBoundaries((current) => {
      const next = [...current, captured]
      return next.sort((left, right) => left.request.at.localeCompare(right.request.at))
    })
    const candidate = plusHour(capturedAt)
    setBoundaryLocal(candidate)
    if (new Date(offsetIst(terminalLocal)) <= new Date(capturedAt)) {
      setTerminalLocal(candidate)
    }
    setAudit(null)
    setBookmarks([])
    resetPackage()
    setError('')
  }

  const removeBoundary = (index: number) => {
    setBoundaries((current) => current.filter((_, itemIndex) => itemIndex !== index))
    setAudit(null)
    setBookmarks([])
    resetPackage()
  }

  const buildAudit = async () => {
    setBusy(true)
    setError('')
    try {
      const result = await fetchChakraLabAudit(auditRequest())
      setAudit(result)
      const firstInterval = result.intervals[0]
      setSelectedIntervalId(firstInterval?.interval_id ?? '')
      const firstRay = result.ray_rows.find(
        (item) => item.interval_id === firstInterval?.interval_id,
      )
      setSelectedClusterId(firstRay?.cluster_id ?? '')
      const firstCell = result.ledger_cells.find(
        (item) => item.interval_id === firstInterval?.interval_id,
      )
      setSelectedCellId(firstCell?.cell_id ?? '')
      setBaselineIntervalId(firstInterval?.interval_id ?? '')
      setComparisonIntervalIds(
        result.intervals.slice(1).map((item) => item.interval_id),
      )
      setBookmarks([])
      resetPackage()
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : String(caught))
    } finally {
      setBusy(false)
    }
  }

  const selectInterval = (item: ChakraAuditInterval) => {
    setSelectedIntervalId(item.interval_id)
    const nextRay = audit?.ray_rows.find(
      (row) => row.interval_id === item.interval_id,
    )
    const nextCell = audit?.ledger_cells.find(
      (row) => row.interval_id === item.interval_id,
    )
    setSelectedClusterId(nextRay?.cluster_id ?? '')
    setSelectedCellId(nextCell?.cell_id ?? '')
  }

  const selectCell = (item: ChakraAuditLedgerCell) => {
    setSelectedCellId(item.cell_id)
    setSelectedClusterId(item.cluster_ids[0] ?? '')
  }

  const selectRay = (item: ChakraAuditRay) => {
    setSelectedClusterId(item.cluster_id)
    setSelectedCellId(item.cell_ids[0] ?? '')
  }

  const openLedgerCell = (cellId: string) => {
    const nextCell = audit?.ledger_cells.find((item) => item.cell_id === cellId)
    if (!nextCell) return
    const nextInterval = audit?.intervals.find(
      (item) => item.interval_id === nextCell.interval_id,
    )
    if (nextInterval) {
      setSelectedIntervalId(nextInterval.interval_id)
    }
    setSelectedCellId(nextCell.cell_id)
    setSelectedClusterId(nextCell.cluster_ids[0] ?? '')
    setActiveTab('LEDGER')
  }

  const toggleComparison = (intervalIdToToggle: string) => {
    setComparisonIntervalIds((current) => (
      current.includes(intervalIdToToggle)
        ? current.filter((item) => item !== intervalIdToToggle)
        : [...current, intervalIdToToggle]
    ))
    resetPackage()
  }

  const addBookmark = () => {
    if (!bookmarkTargetId || !bookmarkLabel.trim() || !bookmarkNote.trim()) return
    setBookmarks((current) => [
      ...current,
      {
        targetType: bookmarkTargetType,
        targetId: bookmarkTargetId,
        label: bookmarkLabel.trim(),
        note: bookmarkNote.trim(),
        createdAt: new Date().toISOString(),
      },
    ])
    setBookmarkLabel('')
    setBookmarkNote('')
    resetPackage()
  }

  const removeBookmark = (index: number) => {
    setBookmarks((current) => current.filter((_, itemIndex) => itemIndex !== index))
    resetPackage()
  }

  const buildPackage = async () => {
    if (!audit || !baselineIntervalId || comparisonIntervalIds.length === 0) return
    setPackageBusy(true)
    setError('')
    setVerification(null)
    try {
      const result = await buildChakraLabAuditPackage({
        auditRequest: auditRequest(),
        baselineIntervalId,
        comparisonIntervalIds,
        bookmarks,
        sealedAt: new Date().toISOString(),
      })
      setPackageBuild(result)
      setActiveTab('COMPARE')
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : String(caught))
    } finally {
      setPackageBusy(false)
    }
  }

  const verifyPackage = async (value = packageBuild?.package) => {
    if (!value) return
    setPackageBusy(true)
    setError('')
    try {
      const result = await verifyChakraLabAuditPackage(value)
      setVerification(result)
      setActiveTab('PACKAGE')
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : String(caught))
    } finally {
      setPackageBusy(false)
    }
  }

  const importPackage = async (file: File | undefined) => {
    if (!file) return
    try {
      const parsed = JSON.parse(await file.text()) as ChakraReproducibleAuditPackage
      setPackageBuild({ package: parsed, htmlReport: '' })
      await verifyPackage(parsed)
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : String(caught))
    } finally {
      if (importInputRef.current) importInputRef.current.value = ''
    }
  }

  return (
    <div className="chakra-audit-shell">
      <aside className="chakra-audit-capture">
        <section>
          <div className="chakra-section-heading">
            <strong>Audit range</strong>
            <span>Explicit boundaries</span>
          </div>
          <label>
            Instrument identity
            <input
              value={instrumentIdentity}
              onChange={(event) => setInstrumentIdentity(event.target.value)}
            />
          </label>
          <label>
            Boundary moment (IST)
            <input
              type="datetime-local"
              value={boundaryLocal}
              onChange={(event) => setBoundaryLocal(event.target.value)}
            />
          </label>
          <label>
            Boundary reason
            <input
              value={boundaryReason}
              onChange={(event) => setBoundaryReason(event.target.value)}
            />
          </label>
          <button
            className="secondary-command chakra-audit-action"
            onClick={captureBoundary}
            title="Capture this explicit audit boundary"
          >
            <Plus size={13} />
            Capture boundary
          </button>
          <label>
            Terminal end (IST)
            <input
              type="datetime-local"
              value={terminalLocal}
              onChange={(event) => setTerminalLocal(event.target.value)}
            />
          </label>
          <button
            className="primary-command chakra-audit-action"
            onClick={() => void buildAudit()}
            disabled={busy || boundaries.length === 0}
          >
            <RefreshCw size={13} className={busy ? 'is-spinning' : ''} />
            {busy ? 'Compiling audit' : 'Compile linked audit'}
          </button>
        </section>

        <section>
          <div className="chakra-section-heading">
            <strong>Captured boundaries</strong>
            <span>{boundaries.length}</span>
          </div>
          <div className="chakra-boundary-list">
            {sortedBoundaries.map((item, index) => (
              <div key={`${item.request.at}-${index}`} className="chakra-boundary-row">
                <button
                  className="chakra-boundary-moment"
                  onClick={() => setTerminalLocal(plusHour(item.request.at))}
                  title={item.request.at}
                >
                  <strong>{formatMoment(item.request.at)}</strong>
                  <span>{item.reason}</span>
                </button>
                <button
                  className="icon-button"
                  onClick={() => removeBoundary(index)}
                  aria-label={`Remove boundary ${index + 1}`}
                  title="Remove boundary"
                >
                  <Trash2 size={12} />
                </button>
              </div>
            ))}
            {!boundaries.length && (
              <span className="chakra-muted-row">No boundary captured</span>
            )}
          </div>
        </section>

        <section>
          <div className="chakra-section-heading">
            <strong>P4 comparison package</strong>
            <span>{comparisonIntervalIds.length} selected</span>
          </div>
          <label>
            Baseline interval
            <select
              value={baselineIntervalId}
              onChange={(event) => {
                setBaselineIntervalId(event.target.value)
                setComparisonIntervalIds((current) => (
                  current.filter((item) => item !== event.target.value)
                ))
                resetPackage()
              }}
              disabled={!audit}
            >
              {(audit?.intervals ?? []).map((item, index) => (
                <option key={item.interval_id} value={item.interval_id}>
                  {index + 1} - {formatMoment(item.start_utc)}
                </option>
              ))}
            </select>
          </label>
          <div className="chakra-comparison-picks">
            {(audit?.intervals ?? [])
              .filter((item) => item.interval_id !== baselineIntervalId)
              .map((item, index) => (
                <button
                  key={item.interval_id}
                  className={comparisonIntervalIds.includes(item.interval_id) ? 'is-selected' : ''}
                  aria-pressed={comparisonIntervalIds.includes(item.interval_id)}
                  onClick={() => toggleComparison(item.interval_id)}
                >
                  <span>{index + 1}</span>
                  {formatMoment(item.start_utc)}
                </button>
              ))}
            {audit && audit.intervals.length < 2 && (
              <span className="chakra-muted-row">Capture at least two intervals</span>
            )}
          </div>
          <button
            className="primary-command chakra-audit-action"
            onClick={() => void buildPackage()}
            disabled={
              packageBusy
              || !audit
              || !baselineIntervalId
              || comparisonIntervalIds.length === 0
            }
          >
            <PackageCheck size={13} />
            {packageBusy ? 'Recomputing package' : 'Build sealed package'}
          </button>
          <input
            ref={importInputRef}
            className="chakra-package-file"
            type="file"
            accept="application/json,.json"
            onChange={(event) => void importPackage(event.target.files?.[0])}
          />
          <button
            className="secondary-command chakra-audit-action"
            onClick={() => importInputRef.current?.click()}
          >
            <Upload size={13} />
            Import and replay
          </button>
        </section>
      </aside>

      <section className="chakra-audit-main">
        <div className="chakra-audit-tabs" role="tablist" aria-label="SBC audit views">
          {[
            ...(audit?.views ?? [
              { view_id: 'TIMELINE', label: 'Timeline', purpose: 'Intervals' },
              { view_id: 'LEDGER', label: 'Ledger', purpose: 'Dimensions' },
              { view_id: 'RAY_AUDIT', label: 'Ray audit', purpose: 'Vedha directions' },
              { view_id: 'SOURCE_LINEAGE', label: 'Lineage', purpose: 'Sources' },
              { view_id: 'RECONCILIATION', label: 'Reconciliation', purpose: 'Checks' },
              { view_id: 'VALIDATION', label: 'Validation', purpose: 'Safety gates' },
            ]),
            {
              view_id: 'COMPARE',
              label: 'Compare',
              purpose: 'Descriptive interval differences only',
            },
            {
              view_id: 'PACKAGE',
              label: 'Package',
              purpose: 'Export, import, and full replay verification',
            },
          ].map((view) => {
            const viewId = view.view_id as AuditTab
            const Icon = TAB_ICONS[viewId]
            return (
              <button
                key={viewId}
                role="tab"
                aria-selected={activeTab === viewId}
                className={activeTab === viewId ? 'is-active' : ''}
                onClick={() => setActiveTab(viewId)}
                disabled={!audit && (viewId === 'COMPARE' || viewId === 'PACKAGE')}
                title={view.purpose}
              >
                <Icon size={12} />
                {view.label}
              </button>
            )
          })}
        </div>

        {error && (
          <div className="chakra-audit-error">
            <ShieldAlert size={14} />
            {error}
          </div>
        )}

        {!audit ? (
          <div className="chakra-audit-empty">
            <Clock3 size={23} />
            <strong>Linked audit not compiled</strong>
            <span>SBC_LINKED_AUDIT_VIEW_V1</span>
          </div>
        ) : (
          <div className="chakra-audit-view">
            {activeTab === 'TIMELINE' && (
              <div className="chakra-audit-table is-timeline">
                <div className="chakra-audit-table-head">
                  <span>Interval</span><span>Start</span><span>End</span>
                  <span>Duration</span><span>Net</span><span>Gross</span>
                  <span>Coverage</span>
                </div>
                {audit.intervals.map((item, index) => (
                  <button
                    key={item.interval_id}
                    className={intervalId === item.interval_id ? 'is-selected' : ''}
                    onClick={() => selectInterval(item)}
                  >
                    <strong>{index + 1}</strong>
                    <span>{formatMoment(item.start_utc)}</span>
                    <span>{formatMoment(item.end_utc)}</span>
                    <span>{formatDuration(item.duration_seconds)}</span>
                    <span>{units(item.total_summary.net_guidance_units)}</span>
                    <span>{units(item.total_summary.gross_activation_units)}</span>
                    <span>{(item.total_summary.scoring_coverage_ratio * 100).toFixed(0)}%</span>
                  </button>
                ))}
              </div>
            )}

            {activeTab === 'LEDGER' && (
              <div className="chakra-audit-table is-ledger">
                <div className="chakra-audit-table-head">
                  <span>Axis</span><span>Key</span><span>Favorable</span>
                  <span>Adverse</span><span>Net</span><span>Gross</span>
                  <span>Unknown</span>
                </div>
                {ledgerRows.map((item) => (
                  <button
                    key={item.cell_id}
                    className={selectedCellId === item.cell_id ? 'is-selected' : ''}
                    onClick={() => selectCell(item)}
                  >
                    <strong>{displayToken(item.axis)}</strong>
                    <span>{displayToken(item.key)}</span>
                    <span>{units(item.summary.favorable_guidance_units)}</span>
                    <span>{units(item.summary.adverse_guidance_units)}</span>
                    <span>{units(item.summary.net_guidance_units)}</span>
                    <span>{units(item.summary.gross_activation_units)}</span>
                    <span>{item.summary.unknown_contribution_count}</span>
                  </button>
                ))}
              </div>
            )}

            {activeTab === 'RAY_AUDIT' && (
              <div className="chakra-audit-table is-rays">
                <div className="chakra-audit-table-head">
                  <span>Actor</span><span>Source</span><span>Direction</span>
                  <span>Target</span><span>Nature</span><span>Units</span>
                  <span>Status</span>
                </div>
                {rayRows.map((item) => (
                  <button
                    key={item.cluster_id}
                    className={selectedClusterId === item.cluster_id ? 'is-selected' : ''}
                    onClick={() => selectRay(item)}
                  >
                    <strong>{item.actor_identity ?? 'Missing'}</strong>
                    <span>{displayToken(item.source_nakshatra)}</span>
                    <span>{displayToken(item.vedha_direction)}</span>
                    <span>{displayToken(item.target_value)}</span>
                    <span>{displayToken(item.nature)}</span>
                    <span>{item.signed_guidance_units == null ? 'Unknown' : units(item.signed_guidance_units)}</span>
                    <span>{displayToken(item.status)}</span>
                  </button>
                ))}
              </div>
            )}

            {activeTab === 'SOURCE_LINEAGE' && (
              <div className="chakra-audit-table is-lineage">
                <div className="chakra-audit-table-head">
                  <span>Cluster</span><span>Snapshot</span><span>Foundation</span>
                  <span>Grid</span><span>Vedha</span><span>Witness</span>
                  <span>Status</span>
                </div>
                {lineageRows.map((item) => (
                  <button
                    key={item.cluster_id}
                    className={selectedClusterId === item.cluster_id ? 'is-selected' : ''}
                    onClick={() => setSelectedClusterId(item.cluster_id)}
                  >
                    <strong>{shortId(item.cluster_id)}</strong>
                    <span>{shortId(item.snapshot_id)}</span>
                    <span>{item.foundation_profile_id}</span>
                    <span>{item.grid_profile_id}</span>
                    <span>{item.vedha_profile_id}</span>
                    <span>{item.target_witness_set_id ?? 'Missing'}</span>
                    <span>{displayToken(item.status)}</span>
                  </button>
                ))}
              </div>
            )}

            {activeTab === 'RECONCILIATION' && (
              <div className="chakra-reconciliation-grid">
                {reconciliationRows.map((item) => (
                  <div key={`${item.interval_id}-${item.axis}`}>
                    <strong>{displayToken(item.axis)}</strong>
                    <span>{item.cell_count} cells</span>
                    <span>{item.cluster_count} clusters</span>
                    <em>{item.reconciled ? 'PASS' : 'FAIL'}</em>
                  </div>
                ))}
              </div>
            )}

            {activeTab === 'VALIDATION' && (
              <div className="chakra-validation-list">
                {audit.validation_gates.map((item) => (
                  <div key={item.gate_id} className={`is-${item.state.toLowerCase()}`}>
                    <span>{item.state}</span>
                    <strong>{item.label}</strong>
                    <p>{item.detail}</p>
                  </div>
                ))}
                <div className="chakra-blocked-capabilities">
                  <strong>Blocked capabilities</strong>
                  <div>
                    {audit.guardrails.blocked_capabilities.map((item) => (
                      <span key={item}>{displayToken(item)}</span>
                    ))}
                  </div>
                </div>
              </div>
            )}

            {activeTab === 'COMPARE' && (
              !packageBuild ? (
                <div className="chakra-audit-empty is-inline">
                  <Columns3 size={21} />
                  <strong>Comparison package not built</strong>
                  <span>Select a baseline and at least one comparison interval.</span>
                </div>
              ) : (
                <div className="chakra-comparison-list">
                  <p className="chakra-comparison-warning">
                    Candidate minus baseline. These are descriptive ledger differences,
                    not market direction, confidence, performance, or trade signals.
                  </p>
                  {packageComparisons.map((comparison) => (
                    <section key={comparison.comparison_id} className="chakra-comparison-section">
                      <header>
                        <div>
                          <strong>{shortId(comparison.comparison_id)}</strong>
                          <span>
                            {shortId(comparison.baseline_interval_id)}
                            {' to '}
                            {shortId(comparison.comparison_interval_id)}
                          </span>
                        </div>
                        <div className="chakra-comparison-metrics">
                          <span>Net {signedUnits(comparison.total_delta.net_guidance_units)}</span>
                          <span>Gross {signedUnits(comparison.total_delta.gross_activation_units)}</span>
                          <span>Coverage {signedUnits(comparison.total_delta.scoring_coverage_ratio * 100)}%</span>
                          <span>Unknown {comparison.total_delta.unknown_contribution_count >= 0 ? '+' : ''}{comparison.total_delta.unknown_contribution_count}</span>
                        </div>
                      </header>
                      <div className="chakra-audit-table is-comparison">
                        <div className="chakra-audit-table-head">
                          <span>Axis</span><span>Key</span><span>Baseline</span>
                          <span>Comparison</span><span>Net delta</span>
                          <span>Gross delta</span><span>Unknown delta</span>
                        </div>
                        {comparison.cell_comparisons.map((item) => (
                          <button
                            key={`${comparison.comparison_id}-${item.axis}-${item.key}`}
                            onClick={() => {
                              openLedgerCell(
                                item.comparison_cell_id ?? item.baseline_cell_id ?? '',
                              )
                            }}
                          >
                            <strong>{displayToken(item.axis)}</strong>
                            <span>{displayToken(item.key)}</span>
                            <span>{item.baseline_cell_id ? units(item.baseline_summary?.net_guidance_units ?? 0) : 'Absent'}</span>
                            <span>{item.comparison_cell_id ? units(item.comparison_summary?.net_guidance_units ?? 0) : 'Absent'}</span>
                            <span>{signedUnits(item.delta.net_guidance_units)}</span>
                            <span>{signedUnits(item.delta.gross_activation_units)}</span>
                            <span>{item.delta.unknown_contribution_count >= 0 ? '+' : ''}{item.delta.unknown_contribution_count}</span>
                          </button>
                        ))}
                      </div>
                    </section>
                  ))}
                </div>
              )
            )}

            {activeTab === 'PACKAGE' && (
              !packageBuild ? (
                <div className="chakra-audit-empty is-inline">
                  <PackageCheck size={21} />
                  <strong>No sealed package</strong>
                  <span>Build or import a P4 package to inspect and verify it.</span>
                </div>
              ) : (
                <div className="chakra-package-view">
                  <header className="chakra-package-toolbar">
                    <div>
                      <strong>Sealed audit package</strong>
                      <span>{shortId(packageBuild.package.package_id)}</span>
                    </div>
                    <div>
                      <button
                        className="icon-button"
                        title="Download sealed JSON"
                        aria-label="Download sealed JSON"
                        onClick={() => downloadText(
                          JSON.stringify(packageBuild.package, null, 2),
                          'application/json',
                          `sbc-audit-${packageBuild.package.package_id.slice(0, 12)}.json`,
                        )}
                      >
                        <Download size={13} />
                      </button>
                      <button
                        className="icon-button"
                        title="Download readable HTML report"
                        aria-label="Download readable HTML report"
                        disabled={!packageBuild.htmlReport}
                        onClick={() => downloadText(
                          packageBuild.htmlReport,
                          'text/html',
                          `sbc-audit-${packageBuild.package.package_id.slice(0, 12)}.html`,
                        )}
                      >
                        <FileCheck2 size={13} />
                      </button>
                      <button
                        className="secondary-command"
                        disabled={packageBusy}
                        onClick={() => void verifyPackage()}
                      >
                        <RefreshCw size={12} />
                        Replay verify
                      </button>
                    </div>
                  </header>

                  <dl className="chakra-package-meta">
                    <div><dt>Package</dt><dd>{packageBuild.package.package_id}</dd></div>
                    <div><dt>Source audit</dt><dd>{packageBuild.package.source_audit_id}</dd></div>
                    <div><dt>Projection</dt><dd>{packageBuild.package.source_projection_hash}</dd></div>
                    <div><dt>Replay recipe</dt><dd>{packageBuild.package.replay_recipe_hash}</dd></div>
                    <div><dt>Sealed UTC</dt><dd>{packageBuild.package.sealed_at_utc}</dd></div>
                  </dl>

                  {verification && (
                    <div className={`chakra-package-verification is-${verification.state.toLowerCase()}`}>
                      <span>{verification.state}</span>
                      <strong>
                        {verification.state === 'PASS'
                          ? 'Full Chakra to P1 to P2 to P3 to P4 replay matched'
                          : 'Replay verification failed'}
                      </strong>
                      {verification.errors.map((item) => <p key={item}>{item}</p>)}
                    </div>
                  )}

                  <div className="chakra-validation-list">
                    {packageBuild.package.validation_gates.map((item) => (
                      <div key={item.gate_id} className={`is-${item.state.toLowerCase()}`}>
                        <span>{item.state}</span>
                        <strong>{item.label}</strong>
                        <p>{item.detail}</p>
                      </div>
                    ))}
                  </div>

                  <section>
                    <div className="chakra-section-heading">
                      <strong>Manual research bookmarks</strong>
                      <span>{packageBuild.package.bookmarks.length}</span>
                    </div>
                    <div className="chakra-package-bookmarks">
                      {packageBuild.package.bookmarks.map((item) => (
                        <div key={item.bookmark_id}>
                          <span>{displayToken(item.target_type)}</span>
                          <strong>{item.label}</strong>
                          <p>{item.note}</p>
                          <code>{shortId(item.target_id)}</code>
                        </div>
                      ))}
                      {!packageBuild.package.bookmarks.length && (
                        <span className="chakra-muted-row">No manual bookmarks</span>
                      )}
                    </div>
                  </section>
                </div>
              )
            )}
          </div>
        )}
      </section>

      <aside className="chakra-audit-inspector">
        <section>
          <div className="chakra-section-heading">
            <strong>Linked selection</strong>
            <span>{audit ? shortId(audit.audit_view_id) : '-'}</span>
          </div>
          <dl>
            <div><dt>Interval</dt><dd>{shortId(selectedInterval?.interval_id)}</dd></div>
            <div><dt>Cell</dt><dd>{shortId(selectedCell?.cell_id)}</dd></div>
            <div><dt>Cluster</dt><dd>{shortId(selectedCluster?.cluster_id)}</dd></div>
            <div><dt>Cutoff</dt><dd>{selectedInterval ? formatMoment(selectedInterval.evidence_cutoff_utc) : '-'}</dd></div>
          </dl>
        </section>

        <section>
          <div className="chakra-section-heading">
            <strong>Primary evidence</strong>
            <span>{selectedCluster?.evidence_kind ?? '-'}</span>
          </div>
          <dl>
            <div><dt>Actor</dt><dd>{selectedCluster?.actor_identity ?? 'Unavailable'}</dd></div>
            <div><dt>Ray</dt><dd>{displayToken(selectedCluster?.vedha_direction)}</dd></div>
            <div><dt>Target</dt><dd>{displayToken(selectedCluster?.target_value)}</dd></div>
            <div><dt>Nature</dt><dd>{displayToken(selectedCluster?.nature)}</dd></div>
            <div><dt>Units</dt><dd>{selectedCluster?.signed_guidance_units == null ? 'Unknown' : units(selectedCluster.signed_guidance_units)}</dd></div>
          </dl>
          {selectedCluster?.unknown_reason && (
            <p className="chakra-audit-unknown">{selectedCluster.unknown_reason}</p>
          )}
        </section>

        <section>
          <div className="chakra-section-heading">
            <strong>Source lineage</strong>
            <span>{selectedLineage?.status ?? '-'}</span>
          </div>
          <dl>
            <div><dt>Lineage</dt><dd>{shortId(selectedLineage?.source_lineage_id)}</dd></div>
            <div><dt>Foundation</dt><dd>{selectedLineage?.foundation_profile_id ?? '-'}</dd></div>
            <div><dt>Grid</dt><dd>{selectedLineage?.grid_profile_id ?? '-'}</dd></div>
            <div><dt>Vedha</dt><dd>{selectedLineage?.vedha_profile_id ?? '-'}</dd></div>
          </dl>
          <div className="chakra-source-tags">
            {selectedLineage?.source_ids.map((item) => <span key={item}>{item}</span>)}
          </div>
        </section>

        <section>
          <div className="chakra-section-heading">
            <strong>Research bookmark</strong>
            <span>Not ML evidence</span>
          </div>
          <div className="chakra-bookmark-editor">
            <select
              value={bookmarkTargetType}
              onChange={(event) => setBookmarkTargetType(
                event.target.value as ChakraAuditBookmarkTarget,
              )}
              disabled={!audit}
            >
              <option value="AUDIT">Whole audit</option>
              <option value="INTERVAL">Selected interval</option>
              <option value="CELL">Selected ledger cell</option>
              <option value="CLUSTER">Selected evidence cluster</option>
            </select>
            <input
              value={bookmarkLabel}
              onChange={(event) => setBookmarkLabel(event.target.value)}
              placeholder="Bookmark label"
              disabled={!bookmarkTargetId}
            />
            <textarea
              value={bookmarkNote}
              onChange={(event) => setBookmarkNote(event.target.value)}
              placeholder="Manual observation only"
              disabled={!bookmarkTargetId}
            />
            <button
              className="secondary-command"
              onClick={addBookmark}
              disabled={
                !bookmarkTargetId
                || !bookmarkLabel.trim()
                || !bookmarkNote.trim()
              }
            >
              <BookmarkPlus size={12} />
              Add bookmark
            </button>
          </div>
          <div className="chakra-bookmark-drafts">
            {bookmarks.map((item, index) => (
              <div key={`${item.createdAt}-${index}`}>
                <button
                  className="icon-button"
                  aria-label={`Remove bookmark ${index + 1}`}
                  title="Remove bookmark"
                  onClick={() => removeBookmark(index)}
                >
                  <Trash2 size={11} />
                </button>
                <strong>{item.label}</strong>
                <span>{displayToken(item.targetType)} · {shortId(item.targetId)}</span>
              </div>
            ))}
          </div>
        </section>

        <section className="chakra-audit-locks">
          <span>Read only</span>
          <span>No phase</span>
          <span>No direction</span>
          <span>Bookmarks not ML</span>
          <span>No execution</span>
        </section>
      </aside>
    </div>
  )
}
