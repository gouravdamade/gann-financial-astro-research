import { useEffect, useMemo, useState } from 'react'
import { BookOpen, CircleAlert, LockKeyhole, ShieldCheck } from 'lucide-react'
import { fetchAgarwalSourceProfile } from '../api'
import type { AgarwalSourceCell, AgarwalSourceProfile, SbcSourceProfileId } from '../types'

type Props = {
  profileId: SbcSourceProfileId
  onProfileChange: (profileId: SbcSourceProfileId) => void
}

const profileOptions: Array<{ id: SbcSourceProfileId; label: string }> = [
  { id: 'phaladeepika_editor_vedha_guidance_v1', label: 'Phaladeepika editor profile' },
  { id: 'SBC_TRAILOKYA_1972_V1', label: 'Trailokya Dipika 1972 - source-only geometry' },
  { id: 'AGARWAL_2000_GEOMETRY_STRENGTH_INSPECTOR_V1', label: 'Agarwal 2000 Research' },
]

function cellAriaLabel(cell: AgarwalSourceCell): string {
  return `${cell.literal}, varga ${cell.vargaNumber}, ${cell.layer}, coordinate ${cell.coordinate.label}`
}

function sourceValue(value: unknown): string {
  if (value == null) return 'Not normalized in the source record'
  return typeof value === 'string' ? value : JSON.stringify(value)
}

function OrientationFrame() {
  return (
    <div className="agarwal-orientation-frame" aria-label="Agarwal author orientation">
      <span className="agarwal-orientation-top">EAST</span>
      <span className="agarwal-orientation-left">NORTH</span>
      <span className="agarwal-orientation-right">SOUTH</span>
      <span className="agarwal-orientation-bottom">WEST</span>
    </div>
  )
}

function CellAudit({ cell, profile }: { cell: AgarwalSourceCell | null; profile: AgarwalSourceProfile }) {
  if (!cell) {
    return (
      <div className="agarwal-cell-audit empty-state">
        <strong>Select a board cell</strong>
        <span>Cell details remain source-only and read-only.</span>
      </div>
    )
  }
  return (
    <div className="agarwal-cell-audit">
      <div className="agarwal-section-kicker">Selected cell</div>
      <h3>{cell.literal}</h3>
      <dl className="agarwal-detail-list">
        <div><dt>Coordinate</dt><dd>{cell.coordinate.label}</dd></div>
        <div><dt>Varga number</dt><dd>{cell.vargaNumber}</dd></div>
        <div><dt>Layer</dt><dd>{cell.layer}</dd></div>
        <div><dt>Normalized label</dt><dd>{cell.normalizedLabel ?? 'Source literal retained'}</dd></div>
        <div><dt>Source profile</dt><dd>{profile.sourceId}</dd></div>
        <div><dt>Printed page</dt><dd>p.{cell.printedPage}</dd></div>
        <div><dt>Evidence packet</dt><dd>{cell.evidencePacketId}</dd></div>
        <div><dt>Source status</dt><dd>{cell.sourceStatus}</dd></div>
      </dl>
    </div>
  )
}

export function AgarwalSourceInspectorWorkspace({ profileId, onProfileChange }: Props) {
  const [profile, setProfile] = useState<AgarwalSourceProfile | null>(null)
  const [selectedCellId, setSelectedCellId] = useState('5:5')
  const [error, setError] = useState('')

  useEffect(() => {
    let active = true
    setError('')
    void fetchAgarwalSourceProfile()
      .then((nextProfile) => {
        if (active) setProfile(nextProfile)
      })
      .catch((caught) => {
        if (active) setError(caught instanceof Error ? caught.message : String(caught))
      })
    return () => { active = false }
  }, [])

  const selectedCell = useMemo(
    () => profile?.geometry.cells.find((cell) => cell.coordinate.label === selectedCellId) ?? null,
    [profile, selectedCellId],
  )

  if (error) {
    return (
      <section className="agarwal-inspector">
        <div className="error-state"><CircleAlert size={16} /><strong>Agarwal source profile unavailable</strong><span>{error}</span></div>
      </section>
    )
  }

  if (!profile) {
    return <section className="agarwal-inspector loading-state"><strong>Loading Agarwal source records</strong><span>Reading the committed geometry and strength fixtures.</span></section>
  }

  return (
    <section className="agarwal-inspector" aria-label="Agarwal 2000 geometry and strength inspector">
      <header className="agarwal-inspector-header">
        <div>
          <div className="agarwal-section-kicker"><BookOpen size={14} /> SBC source profile</div>
          <h1>Sarvatobhadra Chakra - Agarwal 2000 Research</h1>
          <p>Read-only geometry and source-strength inspection. This is not a complete Vedha or market engine.</p>
        </div>
        <div className="agarwal-profile-controls">
          <label htmlFor="agarwal-source-profile">Source profile</label>
          <select
            id="agarwal-source-profile"
            aria-label="Agarwal source profile"
            value={profileId}
            onChange={(event) => onProfileChange(event.target.value as SbcSourceProfileId)}
          >
            {profileOptions.map((option) => <option key={option.id} value={option.id}>{option.label}</option>)}
          </select>
        </div>
      </header>

      <div className="agarwal-badges" aria-label="Agarwal scope status">
        <span className="status-badge status-badge-source">MODERN PRACTITIONER SOURCE</span>
        <span className="status-badge status-badge-positive">GEOMETRY + STRENGTH SOURCE CLOSED</span>
        <span className="status-badge status-badge-warning">VEDHA NOT READY</span>
        <span className="status-badge"><LockKeyhole size={12} /> READ ONLY</span>
      </div>

      <div className="agarwal-inspector-grid">
        <section className="agarwal-board-panel" aria-label="Agarwal p.145 board">
          <div className="agarwal-panel-heading">
            <div><strong>Author board</strong><span>Printed p.145 - AGARWAL_PAGE145_CORE_9X9_V1</span></div>
            <span className="source-status-chip">81 / 81 cells source closed</span>
          </div>
          <div className="agarwal-board-stage">
            <OrientationFrame />
            <div className="agarwal-board" role="grid" aria-label="Agarwal 9 by 9 core board">
              {profile.geometry.cells.map((cell) => (
                <button
                  key={cell.coordinate.label}
                  type="button"
                  role="gridcell"
                  aria-label={cellAriaLabel(cell)}
                  aria-selected={selectedCellId === cell.coordinate.label}
                  className={`agarwal-cell agarwal-layer-${cell.layer} ${selectedCellId === cell.coordinate.label ? 'is-selected' : ''}`}
                  onClick={() => setSelectedCellId(cell.coordinate.label)}
                >
                  <span className="agarwal-cell-literal">{cell.literal}</span>
                  <span className="agarwal-cell-number">{cell.vargaNumber}</span>
                  <span className="agarwal-cell-layer">{cell.layer.replaceAll('_', ' ')}</span>
                </button>
              ))}
            </div>
          </div>
          <div className="agarwal-board-note">Literal source labels are preserved. Normalized names, if later supplied, remain separate presentation data.</div>
        </section>

        <aside className="agarwal-audit-column">
          <CellAudit cell={selectedCell} profile={profile} />
          <section className="agarwal-source-card">
            <div className="agarwal-section-kicker"><ShieldCheck size={14} /> Provenance</div>
            <h3>Authenticated source record</h3>
            <dl className="agarwal-detail-list">
              <div><dt>Book</dt><dd>{profile.edition}</dd></div>
              <div><dt>Geometry evidence</dt><dd>{profile.provenance.geometryEvidence}</dd></div>
              <div><dt>Allocation context</dt><dd>Printed p.{profile.provenance.allocationContextPrintedPage}</dd></div>
              <div><dt>Reconciliation</dt><dd>{profile.geometry.p144Reconciliation.status} / AGREED</dd></div>
              <div><dt>Historical fold state</dt><dd>{profile.geometry.historicalUnknownCenterFold}</dd></div>
            </dl>
            <div className="agarwal-allocation-title">p.144 allocation groups</div>
            <ul className="agarwal-allocation-list">
              {Object.entries(profile.geometry.p144Reconciliation.expected).map(([layer, values]) => (
                <li key={layer}><strong>{layer.replaceAll('_', ' ')}</strong><span>{sourceValue(values)}</span></li>
              ))}
            </ul>
          </section>
        </aside>
      </div>

      <section className="agarwal-source-section">
        <div className="agarwal-panel-heading">
          <div><strong>Agarwal Source Strength</strong><span>Read-only records from pp.54-55 and 60-63</span></div>
          <span className="source-status-chip">{profile.strengthEvidence.rows.length} source rows</span>
        </div>
        <div className="agarwal-strength-table" role="table" aria-label="Agarwal source strength rows">
          <div className="agarwal-strength-row agarwal-strength-head" role="row"><span>Source category</span><span>Literal value</span><span>Page</span><span>Status</span></div>
          {profile.strengthEvidence.rows.map((row) => (
            <div className="agarwal-strength-row" role="row" key={row.variableId}>
              <span><strong>{row.categoryLiteral}</strong><small>{row.variableId}</small></span>
              <span>{row.literalValue}<small>Normalized: {sourceValue(row.normalizedValue)}</small></span>
              <span>p.{row.printedPage}</span>
              <span>{row.sourceStatus}<small>{row.diffStatus}</small></span>
            </div>
          ))}
        </div>
        <div className="agarwal-lock-note"><LockKeyhole size={13} /> Source records only. No master score, market comparison, polarity, Fields input or execution path is created.</div>
      </section>

      <div className="agarwal-two-column-cards">
        <section className="agarwal-source-card vedha-card">
          <div className="agarwal-section-kicker"><CircleAlert size={14} /> Vedha operator</div>
          <h3>DEPENDENCY_NOT_READY</h3>
          <p>Partial source evidence is visible for audit only. No live rays or simulated Vedha paths are rendered.</p>
          <ul>{profile.vedhaDependencies.map((dependency) => <li key={dependency}>{dependency}</li>)}</ul>
          <div className="partial-evidence">Partial source evidence: {profile.partialSourceEvidence.join('; ')}.</div>
        </section>
        <section className="agarwal-source-card">
          <div className="agarwal-section-kicker"><LockKeyhole size={14} /> Financial material</div>
          <h3>Chapter 20 - FINANCIAL_HYPOTHESIS_LEDGER_ONLY</h3>
          <p>Research/audit material is isolated from product calculations.</p>
          <div className="agarwal-financial-locks">{profile.financialStatus.labels.map((label) => <span key={label}>{label}</span>)}</div>
          <div className="agarwal-financial-classification">{profile.financialStatus.classification}</div>
          <div className="agarwal-financial-claims">{profile.financialStatus.claims.map((claim) => <span key={claim.hypothesisId}>{claim.hypothesisId} · p.{claim.printedPage}</span>)}</div>
        </section>
      </div>

      <footer className="agarwal-inspector-footer">
        <span>{profile.sourceId}</span>
        <span>Phaladeepika and Trailokya remain separate profiles</span>
        <span>executionAllowed = {String(profile.executionAllowed)}</span>
      </footer>
    </section>
  )
}
