import { Layers3, ShieldCheck } from 'lucide-react'
import type { SynchronizedIndependentRange } from '../types'

type Props = {
  range: SynchronizedIndependentRange | null
  busy: boolean
  error: string
  onLoad: () => void
}

type LaneBlock = {
  id: string
  startUtc: string
  endUtc: string
  state: string
  detail: string
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

export function IndependentFieldStack({ range, busy, error, onLoad }: Props) {
  const usdBlocks: LaneBlock[] = range?.aspectFields.USD.intervals.map((interval) => ({
    id: interval.intervalId,
    startUtc: interval.startUtc,
    endUtc: interval.endUtc,
    state: interval.polarityState,
    detail: interval.reason,
  })) ?? []
  const jpyBlocks: LaneBlock[] = range?.aspectFields.JPY.intervals.map((interval) => ({
    id: interval.intervalId,
    startUtc: interval.startUtc,
    endUtc: interval.endUtc,
    state: interval.polarityState,
    detail: interval.reason,
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
      <button onClick={onLoad} disabled={busy}>{busy ? 'Loading range' : 'Load chart range'}</button>
    </header>
    {error && <p className="independent-field-stack-error">{error}</p>}
    {!range && !busy && !error && <p className="independent-field-stack-empty">Load the rendered chart range. Unreviewed side-chart evidence remains visible as an unknown gap.</p>}
    {range && <>
      <div className="independent-field-stack-range"><span>{compactUtc(range.rangeStartUtc)}</span><b>Shared UTC range</b><span>{compactUtc(range.rangeEndUtc)}</span></div>
      <StateLane label="USD aspect field" note="Categorical side context" blocks={usdBlocks} />
      <StateLane label="JPY aspect field" note="Categorical side context" blocks={jpyBlocks} />
      <StateLane label="SBC atomic field" note="Guidance availability only" blocks={sbcBlocks} />
      <p className="independent-field-stack-lock"><ShieldCheck size={12} /> No fusion, no automatic confirmation, no magnitude, and no execution.</p>
    </>}
  </section>
}
