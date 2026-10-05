import { Eye, ShieldCheck } from 'lucide-react'
import type { VisualizationModePolicy } from '../visualizationModes'
import type { FieldsResearchSelection } from './fieldsResearchSelection'
import { buildFieldsResearchExplanation } from './fieldsResearchExplanation'

type Props = {
  selection: FieldsResearchSelection | null
  crosshairTimestampUtc: string | null
  visualizationPolicy: VisualizationModePolicy
  sourceProfileId: string
}

function value(value: unknown): string {
  if (value == null) return 'UNKNOWN'
  if (typeof value === 'number') return value.toFixed(3)
  return String(value)
}

function Metadata({ selection, sourceProfileId }: { selection: FieldsResearchSelection; sourceProfileId: string }) {
  return <div className="fields-inspector-metadata">
    <span>Source profile: {sourceProfileId}</span>
    <span>Profile reference: {selection.profileId}</span>
    <span>Classification: {selection.classification}</span>
    <span>Read only</span>
    <span>executionAllowed=false</span>
    {selection.sourceGapIds.length > 0 ? <span>Source gaps: {selection.sourceGapIds.join(' | ')}</span> : null}
  </div>
}

function FieldDetails({ selection, directionalFieldsVisible }: { selection: Extract<FieldsResearchSelection, { kind: 'FIELD_INTERVAL' }>; directionalFieldsVisible: boolean }) {
  if (!directionalFieldsVisible) return <p className="fields-inspector-withheld">WITHHELD BY CURRENT MODE. Directional field values are not exposed by the resolved policy.</p>
  const interval = selection.interval
  return <dl>
    <div><dt>Side</dt><dd>{selection.selection.field}</dd></div>
    <div><dt>State</dt><dd>{interval.polarityState}</dd></div>
    <div><dt>Start / end</dt><dd>{interval.startUtc} to {interval.endUtc}</dd></div>
    <div><dt>Coverage</dt><dd>{interval.unknownEventIds.length ? 'UNKNOWN' : 'KNOWN'}</dd></div>
    <div><dt>Supportive active</dt><dd>{interval.supportiveActive ? 'yes' : 'no'}</dd></div>
    <div><dt>Adverse active</dt><dd>{interval.adverseActive ? 'yes' : 'no'}</dd></div>
    <div><dt>Source interval ID</dt><dd>{interval.intervalId}</dd></div>
    <div><dt>Reason</dt><dd>{interval.reason}</dd></div>
  </dl>
}

function PairDetails({ selection, directionalFieldsVisible }: { selection: Extract<FieldsResearchSelection, { kind: 'PAIR_INTERVAL' }>; directionalFieldsVisible: boolean }) {
  if (!directionalFieldsVisible) return <p className="fields-inspector-withheld">WITHHELD BY CURRENT MODE. Pair-relative directional values are not exposed by the resolved policy.</p>
  const interval = selection.interval
  return <>
    <p className="fields-inspector-classification">MODERN ENGINEERING RESEARCH TRANSFORM</p>
    <dl>
      <div><dt>USD balance</dt><dd>{value(interval.baseBalance)}</dd></div>
      <div><dt>JPY balance</dt><dd>{value(interval.quoteBalance)}</dd></div>
      <div><dt>Pair raw</dt><dd>{value(interval.pairRaw)}</dd></div>
      <div><dt>Pair display</dt><dd>{value(interval.pairDisplay)}</dd></div>
      <div><dt>State</dt><dd>{interval.state}</dd></div>
      <div><dt>Conflict</dt><dd>{interval.conflict ? 'present' : 'none'}</dd></div>
      <div><dt>Coverage</dt><dd>{interval.coverage}</dd></div>
      <div><dt>Source interval IDs</dt><dd>{interval.sourceIntervalIds.base ?? 'none'} | {interval.sourceIntervalIds.quote ?? 'none'}</dd></div>
      <div><dt>Unknown reason</dt><dd>{interval.unknownReason ?? 'none'}</dd></div>
    </dl>
  </>
}

function EventDetails({ selection }: { selection: Extract<FieldsResearchSelection, { kind: 'ACTIVITY_EVENT' }> }) {
  const event = selection.event
  return <dl>
    <div><dt>Side</dt><dd>{event.sideIdentity}</dd></div>
    <div><dt>Event ID</dt><dd>{event.eventId}</dd></div>
    <div><dt>Event hash</dt><dd>{event.eventHash}</dd></div>
    <div><dt>Transit body</dt><dd>{event.transitBody}</dd></div>
    <div><dt>Natal target</dt><dd>{event.natalTarget}</dd></div>
    <div><dt>Aspect</dt><dd>{event.aspectType}</dd></div>
    <div><dt>Applying start</dt><dd>{event.applyingStartUtc}</dd></div>
    <div><dt>Exact UTC</dt><dd>{event.exactUtc}</dd></div>
    <div><dt>Separating end</dt><dd>{event.separatingEndUtc}</dd></div>
    <div><dt>Coverage</dt><dd>{selection.coverage}</dd></div>
    <div><dt>Unknown reason</dt><dd>{selection.unknownReason ?? 'none'}</dd></div>
    <div><dt>Astronomy contract</dt><dd>{event.astronomyContract ?? 'Canonical compiler contract'}</dd></div>
    <div><dt>Event contract</dt><dd>{event.eventContract ?? 'CHART_CONDITIONED_TRANSIT_EVENT_RANGE_V1'}</dd></div>
    <div><dt>Polarity</dt><dd>NOT ASSIGNED</dd></div>
    <div><dt>Magnitude</dt><dd>NOT CONFIGURED</dd></div>
  </dl>
}

function SbcDetails({ selection }: { selection: Extract<FieldsResearchSelection, { kind: 'SBC_INTERVAL' }> }) {
  const interval = selection.interval
  return <dl>
    <div><dt>Availability</dt><dd>{interval.guidance_availability}</dd></div>
    <div><dt>Interval</dt><dd>{interval.start_utc} to {interval.end_utc}</dd></div>
    <div><dt>Interval ledger ID</dt><dd>{interval.interval_ledger_id}</dd></div>
    <div><dt>Missing evidence IDs</dt><dd>{interval.missing_evidence_ids.join(' | ') || 'none'}</dd></div>
    <div><dt>Evidence cutoff</dt><dd>{interval.evidence_cutoff_utc}</dd></div>
  </dl>
}

function BphsDetails({ selection }: { selection: Extract<FieldsResearchSelection, { kind: 'BPHS_INTERVAL' }> }) {
  const item = selection.selection
  return <dl>
    <div><dt>Category</dt><dd>{item.category}</dd></div>
    <div><dt>Value</dt><dd>{item.value}</dd></div>
    <div><dt>Availability</dt><dd>{item.availability}</dd></div>
    <div><dt>Start / end</dt><dd>{item.startUtc} to {item.endUtc}</dd></div>
    <div><dt>Source locator</dt><dd>{item.sourceLocator}</dd></div>
    <div><dt>Calculation profile</dt><dd>{item.calculationProfile}</dd></div>
    <div><dt>Dependency</dt><dd>{item.dependency ?? 'none'}</dd></div>
    <div><dt>Role</dt><dd>NO MARKET ROLE</dd></div>
  </dl>
}

function ExplanationAndProvenance({ model }: { model: NonNullable<ReturnType<typeof buildFieldsResearchExplanation>> }) {
  const entries = [
    ['What is happening?', model.headline],
    ['Why is it visible?', model.whyThisIsVisible],
    ['Astronomy fact', model.astronomyFact],
    ['Source doctrine', model.sourceDoctrine],
    ['Astrology interpretation', model.astrologyInterpretation],
    ['Engineering transform', model.engineeringTransform],
    ['Market bridge', model.marketBridge],
    ['Financial validation', model.financialValidation],
    ['Magnitude', model.magnitude],
    ['Unknowns and withheld', model.unknownsAndWithheld],
    ['Execution', model.execution],
  ] as const

  return <section className="fields-inspector-explanation" aria-label="Explanation and provenance">
    <h3>Explanation and provenance</h3>
    <dl className="fields-inspector-explanation-grid">
      {entries.map(([label, detail]) => <div key={label}><dt>{label}</dt><dd>{detail}</dd></div>)}
    </dl>
  </section>
}

export function FieldsResearchInspector({ selection, crosshairTimestampUtc, visualizationPolicy, sourceProfileId }: Props) {
  const directionalFieldsVisible = visualizationPolicy.scoringVisible
  const explanation = buildFieldsResearchExplanation(selection, visualizationPolicy)
  return <section className="fields-research-inspector" aria-label="Unified Fields research inspector">
    <header>
      <div><Eye size={15} /><div><strong>Unified Research Inspector</strong><span>Read-only selected source and engineering detail</span></div></div>
      <span className="fields-inspector-lock"><ShieldCheck size={12} /> executionAllowed=false</span>
    </header>
    {!selection ? <div className="fields-inspector-empty">
      <strong>NO RESEARCH ITEM SELECTED</strong>
      <span>{crosshairTimestampUtc ? `Crosshair UTC: ${crosshairTimestampUtc}` : 'Crosshair UTC: not selected'}</span>
      <small>Select a field interval, activity event, SBC interval, or BPHS interval to inspect immutable detail.</small>
    </div> : <>
      <div className="fields-inspector-selection-heading"><strong>{selection.kind === 'ACTIVITY_EVENT' ? 'Selected event provenance' : `Selected: ${selection.kind.replaceAll('_', ' ')}`}</strong><span>{selection.kind === 'ACTIVITY_EVENT' ? `${selection.event.sideIdentity} | CANONICAL_COMPILER_EVENT | ${selection.event.exactUtc}` : selection.kind === 'BPHS_INTERVAL' ? selection.selection.startUtc : selection.kind === 'SBC_INTERVAL' ? selection.interval.start_utc : selection.kind === 'PAIR_INTERVAL' ? selection.interval.startUtc : selection.interval.startUtc}</span></div>
      {selection.kind === 'FIELD_INTERVAL' ? <FieldDetails selection={selection} directionalFieldsVisible={directionalFieldsVisible} /> : null}
      {selection.kind === 'PAIR_INTERVAL' ? <PairDetails selection={selection} directionalFieldsVisible={directionalFieldsVisible} /> : null}
      {selection.kind === 'ACTIVITY_EVENT' ? <EventDetails selection={selection} /> : null}
      {selection.kind === 'SBC_INTERVAL' ? <SbcDetails selection={selection} /> : null}
      {selection.kind === 'BPHS_INTERVAL' ? <BphsDetails selection={selection} /> : null}
      {explanation ? <ExplanationAndProvenance model={explanation} /> : null}
      <Metadata selection={selection} sourceProfileId={sourceProfileId} />
    </>}
  </section>
}
