import { Layers3, ShieldCheck } from 'lucide-react'
import type { FxSidePilotStatus, ResearchFieldIntervalSelection, SynchronizedIndependentRange } from '../types'
import { compileFxPairRelativeCategoricalField } from '../pairRelativeField'
import type { VisualizationEngineMode } from '../visualizationModes'

type Props = {
  range: SynchronizedIndependentRange | null
  rangeSource?: string | null
  busy: boolean
  error: string
  onLoad: () => void
  pilotStatus: FxSidePilotStatus | null
  pilotBusy: boolean
  pilotError: string
  onLoadPilot: () => void
  selectedInterval?: ResearchFieldIntervalSelection | null
  onSelectInterval?: (selection: ResearchFieldIntervalSelection) => void
  crosshairTimestampUtc?: string | null
  visualizationMode?: VisualizationEngineMode
  isFxPair?: boolean
}

type LaneBlock = {
  id: string
  startUtc: string
  endUtc: string
  state: string
  detail: string
  supportiveActive?: boolean
  adverseActive?: boolean
  displayValue?: number | null
}

function compactUtc(value: string): string {
  const date = new Date(value)
  return Number.isNaN(date.valueOf())
    ? value
    : new Intl.DateTimeFormat('en-IN', {
      day: '2-digit', month: 'short', hour: '2-digit', minute: '2-digit', timeZone: 'UTC',
    }).format(date)
}

function durationSeconds(block: LaneBlock): number {
  return Math.max(1, (Date.parse(block.endUtc) - Date.parse(block.startUtc)) / 1000)
}

function valueForBlock(block: LaneBlock): number | null {
  if (block.displayValue != null) return block.displayValue
  switch (block.state) {
    case 'SUPPORTIVE': return 1
    case 'ADVERSE': return -1
    case 'NEUTRAL': return 0
    // MIXED is known activity with both components present. Keep it at the
    // neutral baseline while rendering its supportive/adverse components.
    case 'MIXED': return 0
    default: return null
  }
}

function compactNumber(value: number | null): string {
  return value == null ? 'unknown' : value.toFixed(3)
}

function activitySummary(supportive: boolean, adverse: boolean, gross: number): string {
  const components = [supportive ? 'supportive' : null, adverse ? 'adverse' : null].filter(Boolean)
  return `${components.join(' + ') || 'neutral'} | gross ${gross}`
}

function xFor(value: string, rangeStart: number, rangeEnd: number): number {
  const instant = Date.parse(value)
  return Math.max(0, Math.min(1000, ((instant - rangeStart) / Math.max(1, rangeEnd - rangeStart)) * 1000))
}

function yFor(value: number): number {
  return 50 - value * 32
}

function steppedPath(blocks: LaneBlock[], rangeStart: number, rangeEnd: number, component: 'balance' | 'supportive' | 'adverse'): string {
  let path = ''
  let previousValue: number | null = null
  let previousEnd = 0
  for (const block of blocks) {
    const start = xFor(block.startUtc, rangeStart, rangeEnd)
    const end = xFor(block.endUtc, rangeStart, rangeEnd)
    const value = component === 'balance'
      ? valueForBlock(block)
      : component === 'supportive'
        ? (block.supportiveActive ? 0.62 : null)
        : (block.adverseActive ? -0.62 : null)
    if (value == null) {
      previousValue = null
      continue
    }
    if (previousValue == null || start !== previousEnd) {
      path += `M ${start} ${yFor(value)} `
    } else if (previousValue !== value) {
      path += `L ${start} ${yFor(previousValue)} L ${start} ${yFor(value)} `
    }
    path += `L ${end} ${yFor(value)} `
    previousValue = value
    previousEnd = end
  }
  return path.trim()
}

function StateLane({ label, note, blocks, selectedInterval, onSelectInterval }: {
  label: string
  note: string
  blocks: LaneBlock[]
  selectedInterval: ResearchFieldIntervalSelection | null
  onSelectInterval?: (selection: ResearchFieldIntervalSelection) => void
}) {
  return <div className="independent-field-lane">
    <div className="independent-field-lane-label"><strong>{label}</strong><span>{note}</span></div>
    <div className="independent-field-lane-track" role="list" aria-label={`${label} intervals`}>
      {blocks.map((block) => <button
        key={block.id}
        type="button"
        role="listitem"
        className={`independent-field-block is-${block.state.toLowerCase()}${selectedInterval?.field === 'SBC' && selectedInterval.intervalId === block.id ? ' is-selected' : ''}`}
        aria-label={`Select SBC interval ${block.state}: ${compactUtc(block.startUtc)} to ${compactUtc(block.endUtc)}`}
        style={{ flexGrow: durationSeconds(block) }}
        title={`${block.state}: ${compactUtc(block.startUtc)} to ${compactUtc(block.endUtc)}. ${block.detail}`}
        onClick={() => onSelectInterval?.({ field: 'SBC', intervalId: block.id, startUtc: block.startUtc, endUtc: block.endUtc })}
      >
        <span>{block.state.replaceAll('_', ' ')}</span>
      </button>)}
    </div>
  </div>
}

export function CategoricalStepPane({ label, field, blocks, rangeStartUtc, rangeEndUtc, selectedInterval, onSelectInterval, crosshairTimestampUtc, suppressed = false, note = 'MAGNITUDE NOT CONFIGURED' }: {
  label: string
  field: 'USD' | 'JPY' | 'PAIR'
  blocks: LaneBlock[]
  rangeStartUtc: string
  rangeEndUtc: string
  selectedInterval: ResearchFieldIntervalSelection | null
  onSelectInterval?: (selection: ResearchFieldIntervalSelection) => void
  crosshairTimestampUtc: string | null
  suppressed?: boolean
  note?: string
}) {
  const start = Date.parse(rangeStartUtc)
  const end = Date.parse(rangeEndUtc)
  const balance = steppedPath(blocks, start, end, 'balance')
  const supportive = steppedPath(blocks, start, end, 'supportive')
  const adverse = steppedPath(blocks, start, end, 'adverse')
  const unknown = blocks.filter((block) => valueForBlock(block) == null)
  const unknownReasons = [...new Set(unknown.map((block) => block.detail).filter(Boolean))]
  const knownCount = blocks.length - unknown.length
  const gapPatternId = `categorical-gap-${field.toLowerCase()}`
  const crosshairX = crosshairTimestampUtc ? xFor(crosshairTimestampUtc, start, end) : null
  return <section className={`categorical-step-pane${suppressed ? ' is-suppressed' : ''}`} aria-label={`${label} categorical stepped field`}>
    <header>
      <strong>{label}</strong>
      <span>{note} | {knownCount}/{blocks.length} known</span>
    </header>
    {suppressed && <p className="categorical-step-suppressed">DIRECTIONAL FIELD SUPPRESSED BY VISUAL-ONLY MODE</p>}
    <svg viewBox="0 0 1000 100" preserveAspectRatio="none" role="img" aria-label={`${field} categorical state over the shared range`}>
      <defs>
        <pattern id={gapPatternId} width="12" height="12" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">
          <rect width="12" height="12" fill="#26313a" />
          <line x1="0" x2="0" y1="0" y2="12" stroke="#64717a" strokeWidth="3" opacity=".5" />
        </pattern>
      </defs>
      <line className="categorical-step-axis" x1="0" x2="1000" y1="50" y2="50" />
      <line className="categorical-step-guide" x1="0" x2="1000" y1="18" y2="18" />
      <line className="categorical-step-guide" x1="0" x2="1000" y1="82" y2="82" />
      {unknown.map((block) => <rect
        key={block.id}
        fill={`url(#${gapPatternId})`}
        x={xFor(block.startUtc, start, end)}
        width={Math.max(1, xFor(block.endUtc, start, end) - xFor(block.startUtc, start, end))}
        y="0"
        height="100"
        className={`categorical-step-gap${selectedInterval?.field === field && selectedInterval.intervalId === block.id ? ' is-selected' : ''}`}
        role="button"
        aria-label={`Select ${field} interval ${block.state}: ${compactUtc(block.startUtc)} to ${compactUtc(block.endUtc)}`}
        tabIndex={0}
        onClick={() => onSelectInterval?.({ field, intervalId: block.id, startUtc: block.startUtc, endUtc: block.endUtc })}
        onKeyDown={(event) => {
          if (event.key === 'Enter' || event.key === ' ') {
            event.preventDefault()
            onSelectInterval?.({ field, intervalId: block.id, startUtc: block.startUtc, endUtc: block.endUtc })
          }
        }}
      ><title>{`UNKNOWN: ${block.detail}`}</title></rect>)}
      {blocks.filter((block) => valueForBlock(block) != null).map((block) => <rect
        key={`${block.id}-selection`}
        className={`categorical-step-hitbox${selectedInterval?.field === field && selectedInterval.intervalId === block.id ? ' is-selected' : ''}`}
        x={xFor(block.startUtc, start, end)}
        width={Math.max(1, xFor(block.endUtc, start, end) - xFor(block.startUtc, start, end))}
        y="0"
        height="100"
        role="button"
        aria-label={`Select ${field} interval ${block.state}: ${compactUtc(block.startUtc)} to ${compactUtc(block.endUtc)}`}
        tabIndex={0}
        onClick={() => onSelectInterval?.({ field, intervalId: block.id, startUtc: block.startUtc, endUtc: block.endUtc })}
        onKeyDown={(event) => {
          if (event.key === 'Enter' || event.key === ' ') {
            event.preventDefault()
            onSelectInterval?.({ field, intervalId: block.id, startUtc: block.startUtc, endUtc: block.endUtc })
          }
        }}
      ><title>{`${block.state}: ${compactUtc(block.startUtc)} to ${compactUtc(block.endUtc)}. ${block.detail}`}</title></rect>)}
      {!suppressed && supportive && <path className="categorical-step-supportive-component" d={supportive} />}
      {!suppressed && adverse && <path className="categorical-step-adverse-component" d={adverse} />}
      {!suppressed && balance && <path className="categorical-step-balance" d={balance} />}
      {crosshairX != null && <line className="categorical-step-crosshair" x1={crosshairX} x2={crosshairX} y1="0" y2="100" />}
    </svg>
    <div className="categorical-step-legend"><span className="supportive">Supportive</span><span className="neutral">Neutral</span><span className="adverse">Adverse</span><span className="gap">Unknown gap</span></div>
    {unknownReasons.length > 0 && <p className="categorical-step-gap-reason">Unknown evidence: {unknownReasons.join(' | ')}</p>}
  </section>
}

export function IndependentFieldStack({
  range, rangeSource = null, busy, error, onLoad, pilotStatus, pilotBusy, pilotError, onLoadPilot,
  selectedInterval = null, onSelectInterval, crosshairTimestampUtc = null,
  visualizationMode = 'SOURCE_ONLY_BASELINE', isFxPair = true,
}: Props) {
  const usdBlocks: LaneBlock[] = range?.aspectFields.USD.intervals.map((interval) => ({
    id: interval.intervalId,
    startUtc: interval.startUtc,
    endUtc: interval.endUtc,
    state: interval.polarityState,
    detail: interval.reason,
    supportiveActive: interval.supportiveActive,
    adverseActive: interval.adverseActive,
  })) ?? []
  const jpyBlocks: LaneBlock[] = range?.aspectFields.JPY.intervals.map((interval) => ({
    id: interval.intervalId,
    startUtc: interval.startUtc,
    endUtc: interval.endUtc,
    state: interval.polarityState,
    detail: interval.reason,
    supportiveActive: interval.supportiveActive,
    adverseActive: interval.adverseActive,
  })) ?? []
  const pairField = range && isFxPair ? compileFxPairRelativeCategoricalField(range) : null
  const pairBlocks: LaneBlock[] = pairField?.intervals.map((interval) => ({
    id: interval.intervalId,
    startUtc: interval.startUtc,
    endUtc: interval.endUtc,
    state: interval.state,
    detail: interval.unknownReason ?? `base ${interval.baseBalance ?? 'unknown'}; quote ${interval.quoteBalance ?? 'unknown'}; pair ${interval.pairDisplay ?? 'unknown'}`,
    supportiveActive: interval.baseSupportiveActive || interval.quoteSupportiveActive,
    adverseActive: interval.baseAdverseActive || interval.quoteAdverseActive,
    displayValue: interval.pairDisplay,
  })) ?? []
  const selectedPairInterval = pairField?.intervals.find((interval) => (
    selectedInterval?.field === 'PAIR' && selectedInterval.intervalId === interval.intervalId
  )) ?? pairField?.intervals[0] ?? null
  const suppressDirectionalPaths = visualizationMode === 'VISUAL_ONLY_NO_SCORE'
  const sbcGeometryOnlyRange = range && 'state' in range.sbcField
    ? range.sbcField
    : null
  const sbcGeometryOnlyState = sbcGeometryOnlyRange
    ? sbcGeometryOnlyRange.state
    : null
  const sbcLaneNote = sbcGeometryOnlyRange
    ? `${sbcGeometryOnlyRange.state}. ${sbcGeometryOnlyRange.reason}`
    : 'Independent availability only; not a polarity scale'
  const sbcBlocks: LaneBlock[] = range?.sbcField.intervals.map((interval) => ({
    id: interval.interval_id,
    startUtc: interval.start_utc,
    endUtc: interval.end_utc,
    state: interval.guidance_availability,
    detail: interval.missing_evidence_ids.length
      ? `Missing evidence: ${interval.missing_evidence_ids.join(', ')}`
      : 'Existing SBC atomic interval availability only.',
  })) ?? []

  return <section className="independent-field-stack" aria-label="Independent synchronized field stack">
    <header>
      <div><Layers3 size={15} /><div><strong>Independent field stack</strong><span>One chart range. USD, JPY, pair-relative, and SBC remain separate.</span></div></div>
      <button onClick={onLoad} disabled={busy}>{busy ? 'Updating range' : 'Refresh now'}</button>
    </header>
    {rangeSource && <p className="independent-field-stack-source">Auto-synced from {rangeSource}; stale responses are discarded.</p>}
    {error && <p className="independent-field-stack-error">{error}</p>}
    {!range && !busy && !error && <p className="independent-field-stack-empty">Open this workspace from a chart. Its current visible range will load automatically.</p>}
    {range && <>
      <div className="independent-field-stack-range"><span>{compactUtc(range.rangeStartUtc)}</span><b>Shared UTC range</b><span>{compactUtc(range.rangeEndUtc)}</span></div>
      <CategoricalStepPane label="USD categorical field" field="USD" blocks={usdBlocks} rangeStartUtc={range.rangeStartUtc} rangeEndUtc={range.rangeEndUtc} selectedInterval={selectedInterval} onSelectInterval={onSelectInterval} crosshairTimestampUtc={crosshairTimestampUtc} suppressed={suppressDirectionalPaths} />
      <CategoricalStepPane label="JPY categorical field" field="JPY" blocks={jpyBlocks} rangeStartUtc={range.rangeStartUtc} rangeEndUtc={range.rangeEndUtc} selectedInterval={selectedInterval} onSelectInterval={onSelectInterval} crosshairTimestampUtc={crosshairTimestampUtc} suppressed={suppressDirectionalPaths} />
      {pairField && <>
        <CategoricalStepPane label="USDJPY pair-relative field" field="PAIR" blocks={pairBlocks} rangeStartUtc={range.rangeStartUtc} rangeEndUtc={range.rangeEndUtc} selectedInterval={selectedInterval} onSelectInterval={onSelectInterval} crosshairTimestampUtc={crosshairTimestampUtc} suppressed={suppressDirectionalPaths} note="MODERN RESEARCH TRANSFORM | MAGNITUDE NOT CONFIGURED" />
        <p className="independent-field-stack-source">FX_PAIR_RELATIVE_CATEGORICAL_FIELD_V1: base balance minus quote balance, divided by two and clamped. It uses only stored side boundaries; it is not classical doctrine, an SBC confirmation, or a market forecast.</p>
        {selectedPairInterval && <section className="pair-relative-audit" aria-label="Selected pair-relative interval audit">
          <header>
            <strong>Selected pair interval</strong>
            <span>{compactUtc(selectedPairInterval.startUtc)} to {compactUtc(selectedPairInterval.endUtc)}</span>
          </header>
          <dl>
            <div><dt>USD balance</dt><dd>{compactNumber(selectedPairInterval.baseBalance)}</dd></div>
            <div><dt>JPY balance</dt><dd>{compactNumber(selectedPairInterval.quoteBalance)}</dd></div>
            <div><dt>Pair display</dt><dd>{compactNumber(selectedPairInterval.pairDisplay)}</dd></div>
            <div><dt>USD activity</dt><dd>{activitySummary(selectedPairInterval.baseSupportiveActive, selectedPairInterval.baseAdverseActive, selectedPairInterval.baseGrossActivity ?? 0)}</dd></div>
            <div><dt>JPY activity</dt><dd>{activitySummary(selectedPairInterval.quoteSupportiveActive, selectedPairInterval.quoteAdverseActive, selectedPairInterval.quoteGrossActivity ?? 0)}</dd></div>
            <div><dt>Common activity</dt><dd>{selectedPairInterval.commonActivity == null ? 'unknown' : `${selectedPairInterval.commonActivity} shared active component(s)`}</dd></div>
            <div><dt>Conflict</dt><dd>{selectedPairInterval.conflict ? 'present' : 'none'}</dd></div>
            <div><dt>Coverage</dt><dd>{selectedPairInterval.coverage}</dd></div>
            <div><dt>Input intervals</dt><dd>{selectedPairInterval.sourceIntervalIds.base ?? 'none'} | {selectedPairInterval.sourceIntervalIds.quote ?? 'none'}</dd></div>
            {selectedPairInterval.unknownReason && <div><dt>Unknown reason</dt><dd>{selectedPairInterval.unknownReason}</dd></div>}
          </dl>
        </section>}
      </>}
      {!isFxPair && <p className="independent-field-stack-empty">Single-stock contract: no automatic base-minus-quote field is created. A chart-conditioned stock field requires an explicit stock evidence profile.</p>}
      <StateLane label="SBC atomic field" note={sbcLaneNote} blocks={sbcBlocks} selectedInterval={selectedInterval} onSelectInterval={onSelectInterval} />
      {sbcGeometryOnlyState && <p className="independent-field-stack-error">SBC source-only geometry has no compiled range or score. USD and JPY remain independent descriptive fields.</p>}
      <p className="independent-field-stack-lock"><ShieldCheck size={12} /> Categorical polarity state only. No magnitude, fusion, automatic confirmation, or execution.</p>
    </>}
    <section className="fx-side-pilot-status" aria-label="FX side pilot status">
      <header><strong>FX side pilot status</strong><button onClick={onLoadPilot} disabled={pilotBusy}>{pilotBusy ? 'Checking pilot' : 'Refresh pilot'}</button></header>
      {pilotError && <p className="independent-field-stack-error">{pilotError}</p>}
      {!pilotStatus && !pilotBusy && !pilotError && <p>Load the current immutable registry status. This cannot create a reviewed record.</p>}
      {pilotStatus && <>
        <p><b>{pilotStatus.status.replaceAll('_', ' ')}</b> - {pilotStatus.summary}</p>
        {(['USD', 'JPY'] as const).map((side) => {
          const summary = pilotStatus.sides[side]
          return <div key={side} className="fx-side-pilot-row">
            <strong>{side}</strong>
            <span>{summary.catalogueEntryCount} categorical record{summary.catalogueEntryCount === 1 ? '' : 's'}</span>
            <span>{summary.missingRequiredStates.length ? `Needs ${summary.missingRequiredStates.join(' + ')}` : 'Supportive + adverse present'}</span>
          </div>
        })}
        <small>Unknown gaps stay visible for unreviewed side events. This panel neither admits evidence nor derives USDJPY direction.</small>
      </>}
    </section>
  </section>
}
