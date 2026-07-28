import {
  Clock3,
  GitBranch,
  ListChecks,
  Plus,
  Radar,
  RefreshCw,
  ShieldAlert,
  Table2,
  Trash2,
} from 'lucide-react'
import { useMemo, useState } from 'react'
import { fetchChakraLabAudit } from '../api'
import type {
  ChakraAuditInterval,
  ChakraAuditLedgerCell,
  ChakraAuditRay,
  ChakraLabAuditBoundaryInput,
  ChakraLabRequest,
  ChakraLinkedAuditView,
} from '../types'


type AuditTab =
  | 'TIMELINE'
  | 'LEDGER'
  | 'RAY_AUDIT'
  | 'SOURCE_LINEAGE'
  | 'RECONCILIATION'
  | 'VALIDATION'

const TAB_ICONS = {
  TIMELINE: Clock3,
  LEDGER: Table2,
  RAY_AUDIT: Radar,
  SOURCE_LINEAGE: GitBranch,
  RECONCILIATION: ListChecks,
  VALIDATION: ShieldAlert,
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

type Props = {
  currentRequest: ChakraLabRequest
}

export function SbcLinkedAuditWorkspace({ currentRequest }: Props) {
  const [instrumentIdentity, setInstrumentIdentity] = useState('FX:USDJPY')
  const [boundaryReason, setBoundaryReason] = useState('manual review boundary')
  const [terminalLocal, setTerminalLocal] = useState(() => plusHour(currentRequest.at))
  const [boundaries, setBoundaries] = useState<ChakraLabAuditBoundaryInput[]>([])
  const [audit, setAudit] = useState<ChakraLinkedAuditView | null>(null)
  const [activeTab, setActiveTab] = useState<AuditTab>('TIMELINE')
  const [selectedIntervalId, setSelectedIntervalId] = useState('')
  const [selectedClusterId, setSelectedClusterId] = useState('')
  const [selectedCellId, setSelectedCellId] = useState('')
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')

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

  const sortedBoundaries = useMemo(
    () => [...boundaries].sort(
      (left, right) => left.request.at.localeCompare(right.request.at),
    ),
    [boundaries],
  )

  const captureBoundary = () => {
    const captured: ChakraLabAuditBoundaryInput = {
      reason: boundaryReason.trim() || 'manual review boundary',
      request: structuredClone(currentRequest),
    }
    setBoundaries((current) => {
      const next = [...current, captured]
      return next.sort((left, right) => left.request.at.localeCompare(right.request.at))
    })
    const candidate = plusHour(currentRequest.at)
    if (new Date(offsetIst(terminalLocal)) <= new Date(currentRequest.at)) {
      setTerminalLocal(candidate)
    }
    setAudit(null)
    setError('')
  }

  const removeBoundary = (index: number) => {
    setBoundaries((current) => current.filter((_, itemIndex) => itemIndex !== index))
    setAudit(null)
  }

  const buildAudit = async () => {
    setBusy(true)
    setError('')
    try {
      const result = await fetchChakraLabAudit({
        instrumentIdentity: instrumentIdentity.trim(),
        terminalEnd: offsetIst(terminalLocal),
        boundaries: sortedBoundaries,
      })
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
            Boundary reason
            <input
              value={boundaryReason}
              onChange={(event) => setBoundaryReason(event.target.value)}
            />
          </label>
          <button
            className="secondary-command chakra-audit-action"
            onClick={captureBoundary}
            title="Capture the current Chakra Lab moment as an explicit audit boundary"
          >
            <Plus size={13} />
            Capture current moment
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
      </aside>

      <section className="chakra-audit-main">
        <div className="chakra-audit-tabs" role="tablist" aria-label="SBC audit views">
          {(audit?.views ?? [
            { view_id: 'TIMELINE', label: 'Timeline', purpose: 'Intervals' },
            { view_id: 'LEDGER', label: 'Ledger', purpose: 'Dimensions' },
            { view_id: 'RAY_AUDIT', label: 'Ray audit', purpose: 'Vedha directions' },
            { view_id: 'SOURCE_LINEAGE', label: 'Lineage', purpose: 'Sources' },
            { view_id: 'RECONCILIATION', label: 'Reconciliation', purpose: 'Checks' },
            { view_id: 'VALIDATION', label: 'Validation', purpose: 'Safety gates' },
          ]).map((view) => {
            const viewId = view.view_id as AuditTab
            const Icon = TAB_ICONS[viewId]
            return (
              <button
                key={viewId}
                role="tab"
                aria-selected={activeTab === viewId}
                className={activeTab === viewId ? 'is-active' : ''}
                onClick={() => setActiveTab(viewId)}
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

        <section className="chakra-audit-locks">
          <span>Read only</span>
          <span>No phase</span>
          <span>No direction</span>
          <span>No execution</span>
        </section>
      </aside>
    </div>
  )
}
