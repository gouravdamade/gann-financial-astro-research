import { useCallback, useEffect, useMemo, useState } from 'react'
import { BookOpen, CircleAlert, LockKeyhole, MapPinned, ShieldCheck } from 'lucide-react'
import { fetchTrailokyaNativeProfile, resolveTrailokyaTargets } from '../api'
import type { SbcSourceProfileId, TrailokyaNativeBoardCell, TrailokyaNativeProfile, TrailokyaResolvedTarget, TrailokyaTargetResolution } from '../types'

type Props = {
  profileId: SbcSourceProfileId
  onProfileChange: (profileId: SbcSourceProfileId) => void
}

const profileOptions: Array<{ id: SbcSourceProfileId; label: string }> = [
  { id: 'phaladeepika_editor_vedha_guidance_v1', label: 'Phaladeepika editor profile' },
  { id: 'SBC_TRAILOKYA_1972_V1', label: 'Trailokya 1972 Research' },
  { id: 'AGARWAL_2000_GEOMETRY_STRENGTH_INSPECTOR_V1', label: 'Agarwal 2000 Research' },
]

const nakshatras = [
  'KRITTIKA', 'ROHINI', 'MRIGASHIRSHA', 'ARDRA', 'PUNARVASU', 'PUSHYA', 'ASHLESHA',
  'MAGHA', 'PURVA_PHALGUNI', 'UTTARA_PHALGUNI', 'HASTA', 'CHITRA', 'SWATI', 'VISHAKHA',
  'ANURADHA', 'JYESHTHA', 'MULA', 'PURVA_ASHADHA', 'UTTARA_ASHADHA', 'ABHIJIT', 'SHRAVANA',
  'DHANISHTHA', 'SHATABHISHA', 'PURVA_BHADRAPADA', 'UTTARA_BHADRAPADA', 'REVATI', 'ASHVINI', 'BHARANI',
]

function display(value: string): string {
  return value.replaceAll('_', ' ').toLowerCase().replace(/\b\w/g, (letter) => letter.toUpperCase())
}

function cellLabel(cell: TrailokyaNativeBoardCell): string {
  return `${cell.sourceLiteral}, ${display(cell.canonicalToken)}, ${display(cell.layer)}, coordinate ${cell.coordinate.label}`
}

function TargetList({ title, targets, kind, onSelect }: { title: string; targets: TrailokyaResolvedTarget[]; kind: 'direct' | 'derived'; onSelect: (target: TrailokyaResolvedTarget) => void }) {
  return <section className={`trailokya-target-list trailokya-target-${kind}`} aria-label={title}>
    <div className="trailokya-list-heading"><strong>{title}</strong><span>{targets.length}</span></div>
    {targets.length === 0 ? <p className="trailokya-empty-list">No {kind} targets in the selected source row.</p> : (
      <ol>
        {targets.map((target) => <li key={target.targetId}>
          <button type="button" onClick={() => onSelect(target)}>
            <span>{display(target.targetType)} · {display(target.canonicalToken)}</span>
            <small>{target.mappingState === 'AVAILABLE' ? target.physicalCell?.label : target.mappingState}</small>
          </button>
        </li>)}
      </ol>
    )}
  </section>
}

export function TrailokyaNativeInspectorWorkspace({ profileId, onProfileChange }: Props) {
  const [profile, setProfile] = useState<TrailokyaNativeProfile | null>(null)
  const [sourceNakshatra, setSourceNakshatra] = useState('KRITTIKA')
  const [direction, setDirection] = useState<'LEFT' | 'FRONT' | 'RIGHT'>('LEFT')
  const [resolution, setResolution] = useState<TrailokyaTargetResolution | null>(null)
  const [selectedTarget, setSelectedTarget] = useState<TrailokyaResolvedTarget | null>(null)
  const [selectedCellId, setSelectedCellId] = useState('5:5')
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    let active = true
    setLoading(true)
    setError('')
    void fetchTrailokyaNativeProfile()
      .then((next) => { if (active) setProfile(next) })
      .catch((caught) => { if (active) setError(caught instanceof Error ? caught.message : String(caught)) })
      .finally(() => { if (active) setLoading(false) })
    return () => { active = false }
  }, [])

  const resolve = useCallback(async () => {
    setError('')
    try {
      const next = await resolveTrailokyaTargets({ sourceNakshatra, direction })
      setResolution(next)
      setSelectedTarget(next.directTargets[0] ?? null)
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : String(caught))
    }
  }, [direction, sourceNakshatra])

  useEffect(() => { void resolve() }, [resolve]) // Source selection is the manual audit action.

  const selectedCell = useMemo(() => profile?.board.cells.find((cell) => cell.coordinate.label === selectedCellId) ?? null, [profile, selectedCellId])
  const highlightedCoordinates = useMemo(() => new Set(resolution?.allTargets.flatMap((target) => target.physicalCell ? [target.physicalCell.label] : []) ?? []), [resolution])
  const directCoordinates = useMemo(() => new Set(resolution?.directTargets.flatMap((target) => target.physicalCell ? [target.physicalCell.label] : []) ?? []), [resolution])

  if (error && !profile) {
    return <section className="trailokya-inspector"><div className="error-state"><CircleAlert size={16} /><strong>Trailokya source inspector unavailable</strong><span>{error}</span></div></section>
  }
  if (loading || !profile) {
    return <section className="trailokya-inspector loading-state"><strong>Loading Trailokya source contract</strong><span>Reading the native board and enumerated target fixtures.</span></section>
  }
  return <section className="trailokya-inspector" aria-label="Trailokya Dipika 1972 native board and enumerated Vedha inspector">
    <header className="trailokya-inspector-header">
      <div>
        <div className="agarwal-section-kicker"><BookOpen size={14} /> SBC source profile</div>
        <h1>Trailokya Dipika 1972 Research</h1>
        <p>Native source board and enumerated target audit. This is a read-only research inspector, not a market model.</p>
      </div>
      <div className="agarwal-profile-controls">
        <label htmlFor="trailokya-source-profile">Vedha source profile</label>
        <select id="trailokya-source-profile" aria-label="Trailokya source profile" value={profileId} onChange={(event) => onProfileChange(event.target.value as SbcSourceProfileId)}>
          {profileOptions.map((option) => <option key={option.id} value={option.id}>{option.label}</option>)}
        </select>
      </div>
    </header>

    <div className="trailokya-badges" aria-label="Trailokya scope status">
      <span className="status-badge status-badge-positive">SOURCE-CLOSED BOARD</span>
      <span className="status-badge status-badge-source">ENUMERATED VEDHA TARGETS</span>
      <span className="status-badge"><LockKeyhole size={12} /> READ ONLY</span>
      <span className="status-badge status-badge-warning">MARKET MAPPING LOCKED</span>
    </div>

    {error && <div className="error-state trailokya-inline-error"><CircleAlert size={16} /><span>{error}</span></div>}

    <div className="trailokya-manual-controls">
      <div><MapPinned size={15} /><strong>Manual Source Audit</strong><span>Source row selection only. No ephemeris or market data is used.</span></div>
      <label>Source nakshatra<select aria-label="Trailokya source nakshatra" value={sourceNakshatra} onChange={(event) => setSourceNakshatra(event.target.value)}>{nakshatras.map((item) => <option key={item} value={item}>{display(item)}</option>)}</select></label>
      <fieldset aria-label="Trailokya direction"><legend>Direction</legend>{(['LEFT', 'FRONT', 'RIGHT'] as const).map((item) => <label key={item}><input type="radio" checked={direction === item} onChange={() => setDirection(item)} /> {display(item)}</label>)}</fieldset>
      <button className="secondary-command" type="button" onClick={() => void resolve()}>Resolve source row</button>
    </div>

    <div className="trailokya-layout">
      <section className="trailokya-board-panel" aria-label="Trailokya native 9 by 9 board">
        <div className="agarwal-panel-heading"><div><strong>Native Akhanda 81 board</strong><span>{profile.board.contract}</span></div><span className="source-status-chip">81 / 81 source cells</span></div>
        <div className="trailokya-board-stage">
          <span className="trailokya-orientation top">EAST</span><span className="trailokya-orientation left">NORTH</span><span className="trailokya-orientation right">SOUTH</span><span className="trailokya-orientation bottom">WEST</span>
          <div className="trailokya-board" role="grid" aria-label="Trailokya 9 by 9 source board">
            {profile.board.cells.map((cell) => {
              const isDirect = directCoordinates.has(cell.coordinate.label)
              const isHighlighted = highlightedCoordinates.has(cell.coordinate.label)
              return <button key={cell.coordinate.label} type="button" role="gridcell" aria-label={cellLabel(cell)} aria-selected={selectedCellId === cell.coordinate.label} className={`trailokya-cell trailokya-layer-${cell.layer} ${isHighlighted ? 'is-highlighted' : ''} ${isDirect ? 'is-direct' : ''} ${selectedCellId === cell.coordinate.label ? 'is-selected' : ''}`} onClick={() => setSelectedCellId(cell.coordinate.label)}>
                <span>{cell.sourceLiteral}</span><small>{cell.normalizedDisplay}</small><em>{cell.coordinate.label}</em>
              </button>
            })}
          </div>
        </div>
        <div className="trailokya-board-note">The enumerated source row controls target identity. Board highlights are a visual projection only.</div>
      </section>

      <aside className="trailokya-audit-column">
        <section className="trailokya-source-card">
          <div className="agarwal-section-kicker"><ShieldCheck size={14} /> Source row</div>
          <h3>{display(sourceNakshatra)} · {display(direction)}</h3>
          <dl className="agarwal-detail-list">
            <div><dt>Authority</dt><dd>{resolution?.targetAuthority ?? 'ENUMERATED_SOURCE_ROWS'}</dd></div>
            <div><dt>Verse</dt><dd>{resolution?.sourceRow.verse ?? '—'}</dd></div>
            <div><dt>Locator</dt><dd>Scan {resolution?.sourceRow.scanPage ?? '—'} · printed p.{resolution?.sourceRow.printedPage ?? '—'}</dd></div>
            <div><dt>Causal event</dt><dd>{resolution?.causalVedhaEventId.slice(0, 12) ?? '—'}</dd></div>
          </dl>
        </section>
        <section className="trailokya-source-card">
          <div className="agarwal-section-kicker">Selected board cell</div>
          {selectedCell ? <dl className="agarwal-detail-list"><div><dt>Coordinate</dt><dd>{selectedCell.coordinate.label}</dd></div><div><dt>Literal</dt><dd>{selectedCell.sourceLiteral}</dd></div><div><dt>Canonical</dt><dd>{selectedCell.canonicalToken}</dd></div><div><dt>Layer</dt><dd>{selectedCell.layer}</dd></div><div><dt>Evidence</dt><dd>Scan {selectedCell.scanPage} · p.{selectedCell.printedPage} · {selectedCell.sourceStatus}</dd></div></dl> : <p>Select a board cell.</p>}
        </section>
        {selectedTarget && <section className="trailokya-source-card"><div className="agarwal-section-kicker">Target audit</div><h3>{display(selectedTarget.targetType)} · {display(selectedTarget.canonicalToken)}</h3><dl className="agarwal-detail-list"><div><dt>Kind</dt><dd>{selectedTarget.isDerived ? `Derived · ${selectedTarget.derivationRuleId}` : 'Direct source target'}</dd></div><div><dt>Physical map</dt><dd>{selectedTarget.physicalCell?.label ?? selectedTarget.mappingState}</dd></div><div><dt>Reach</dt><dd>{selectedTarget.reachState}</dd></div><div><dt>Causal event</dt><dd>{selectedTarget.causalVedhaEventId.slice(0, 12)}</dd></div></dl></section>}
      </aside>
    </div>

    <div className="trailokya-target-grid">
      <TargetList title="Direct targets - source order" targets={resolution?.directTargets ?? []} kind="direct" onSelect={setSelectedTarget} />
      <TargetList title="Derived semantic targets - same causal event" targets={resolution?.derivedTargets ?? []} kind="derived" onSelect={setSelectedTarget} />
      <section className="trailokya-unknown-panel"><div className="agarwal-section-kicker"><CircleAlert size={14} /> Unknown and blocked</div><strong>Context-free reach state is UNKNOWN</strong><p>Manual source audit resolves source identity only. Target reach requires an explicit context and is never converted into a negative result.</p><p>Generic grid traversal is diagnostic only and cannot replace the enumerated row.</p></section>
    </div>
    <footer className="trailokya-inspector-footer"><span>{profile.sourceId}</span><span>{profile.targetAuthority.contract}</span><span>executionAllowed = {String(profile.guardrails.executionAllowed)}</span></footer>
  </section>
}
