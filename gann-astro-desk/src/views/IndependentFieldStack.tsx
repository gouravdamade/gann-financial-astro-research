import { Layers3, ShieldCheck } from 'lucide-react'
import type { FxSidePilotStatus, SynchronizedIndependentRange } from '../types'

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
}

type LaneBlock = {
  id: string
  startUtc: string
  endUtc: string
  state: string
  detail: string
  supportiveActive?: boolean
  adverseActive?: boolean
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

function valueForState(state: string): number | null {
  switch (state) {
    case 'SUPPORTIVE': return 1
    case 'ADVERSE': return -1
    case 'NEUTRAL': return 0
    default: return null
  }
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
      ? valueForState(block.state)
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

function StateLane({ label, note, blocks }: {
  label: string
  note: string
  blocks: LaneBlock[]
}) {
  return <div className="independent-field-lane">
    <div className="independent-field-lane-label"><strong>{label}</strong><span>{note}</span></div>
    <div className="independent-field-lane-track" role="list" aria-label={`${label} intervals`}>
      {blocks.map((block) => <div
        key={block.id}
        role="listitem"
        className={`independent-field-block is-${block.state.toLowerCase()}`}
        style={{ flexGrow: durationSeconds(block) }}
        title={`${block.state}: ${compactUtc(block.startUtc)} to ${compactUtc(block.endUtc)}. ${block.detail}`}
      >
        <span>{block.state.replaceAll('_', ' ')}</span>
      </div>)}
    </div>
  </div>
}

function CategoricalStepPane({ label, side, blocks, rangeStartUtc, rangeEndUtc }: {
  label: string
  side: 'USD' | 'JPY'
  blocks: LaneBlock[]
  rangeStartUtc: string
  rangeEndUtc: string
}) {
  const start = Date.parse(rangeStartUtc)
  const end = Date.parse(rangeEndUtc)
  const balance = steppedPath(blocks, start, end, 'balance')
  const supportive = steppedPath(blocks, start, end, 'supportive')
  const adverse = steppedPath(blocks, start, end, 'adverse')
  const unknown = blocks.filter((block) => block.state === 'UNKNOWN')
  const gapPatternId = `categorical-gap-${side.toLowerCase()}`
  return <section className="categorical-step-pane" aria-label={`${label} categorical stepped field`}>
    <header>
      <strong>{label}</strong>
      <span>MAGNITUDE NOT CONFIGURED</span>
    </header>
    <svg viewBox="0 0 1000 100" preserveAspectRatio="none" role="img" aria-label={`${side} categorical state over the shared range`}>
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
        className="categorical-step-gap"
        fill={`url(#${gapPatternId})`}
        x={xFor(block.startUtc, start, end)}
        width={Math.max(1, xFor(block.endUtc, start, end) - xFor(block.startUtc, start, end))}
        y="0"
        height="100"
      ><title>{`UNKNOWN: ${block.detail}`}</title></rect>)}
      {supportive && <path className="categorical-step-supportive-component" d={supportive} />}
      {adverse && <path className="categorical-step-adverse-component" d={adverse} />}
      {balance && <path className="categorical-step-balance" d={balance} />}
    </svg>
    <div className="categorical-step-legend"><span className="supportive">Supportive</span><span className="neutral">Neutral</span><span className="adverse">Adverse</span><span className="gap">Unknown gap</span></div>
  </section>
}

export function IndependentFieldStack({
  range, rangeSource = null, busy, error, onLoad, pilotStatus, pilotBusy, pilotError, onLoadPilot,
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
      <div><Layers3 size={15} /><div><strong>Independent field stack</strong><span>One chart range. Three separate descriptive fields.</span></div></div>
      <button onClick={onLoad} disabled={busy}>{busy ? 'Updating range' : 'Refresh now'}</button>
    </header>
    {rangeSource && <p className="independent-field-stack-source">Auto-synced from {rangeSource}; stale responses are discarded.</p>}
    {error && <p className="independent-field-stack-error">{error}</p>}
    {!range && !busy && !error && <p className="independent-field-stack-empty">Open this workspace from a chart. Its current visible range will load automatically.</p>}
    {range && <>
      <div className="independent-field-stack-range"><span>{compactUtc(range.rangeStartUtc)}</span><b>Shared UTC range</b><span>{compactUtc(range.rangeEndUtc)}</span></div>
      <CategoricalStepPane label="USD categorical field" side="USD" blocks={usdBlocks} rangeStartUtc={range.rangeStartUtc} rangeEndUtc={range.rangeEndUtc} />
      <CategoricalStepPane label="JPY categorical field" side="JPY" blocks={jpyBlocks} rangeStartUtc={range.rangeStartUtc} rangeEndUtc={range.rangeEndUtc} />
      <StateLane label="SBC atomic field" note="Independent availability only; not a polarity scale" blocks={sbcBlocks} />
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
