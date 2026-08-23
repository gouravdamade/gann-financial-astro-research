import { Activity, Eye, Filter, ShieldCheck } from 'lucide-react'
import { useEffect, useMemo, useState, type CSSProperties } from 'react'
import type {
  MultiOscillatorActivityEvent,
  MultiOscillatorActivityInterval,
  MultiOscillatorActivityRange,
  MultiOscillatorActivitySide,
} from '../types'

type Props = {
  activity: MultiOscillatorActivityRange | null
  busy: boolean
  error: string
  isFxPair: boolean
  crosshairTimestampUtc: string | null
  onLoad: () => void
  onSelectEventTimestamp: (timestampUtc: string) => void
}

const BODY_COLORS: Record<string, string> = {
  SUN: '#e9b66d',
  MOON: '#aec7da',
  MARS: '#ef8b7d',
  MERCURY: '#b6a0e3',
  JUPITER: '#d6c082',
  VENUS: '#e18eb6',
  SATURN: '#8ea4b6',
  RAHU: '#9d90cc',
  KETU: '#8cb9ae',
}

function timestampMs(value: string): number {
  const parsed = Date.parse(value)
  return Number.isFinite(parsed) ? parsed : 0
}

function percentBetween(value: string, startUtc: string, endUtc: string): number {
  const start = timestampMs(startUtc)
  const end = timestampMs(endUtc)
  if (end <= start) return 0
  return Math.max(0, Math.min(100, ((timestampMs(value) - start) / (end - start)) * 100))
}

function intervalStyle(interval: MultiOscillatorActivityInterval, side: MultiOscillatorActivitySide): CSSProperties {
  const left = percentBetween(interval.startUtc, side.rangeStartUtc, side.rangeEndUtc)
  const right = percentBetween(interval.endUtc, side.rangeStartUtc, side.rangeEndUtc)
  return { left: `${left}%`, width: `${Math.max(0.25, right - left)}%` }
}

function eventStyle(event: MultiOscillatorActivityEvent, side: MultiOscillatorActivitySide): CSSProperties {
  const left = percentBetween(event.applyingStartUtc, side.rangeStartUtc, side.rangeEndUtc)
  const right = percentBetween(event.separatingEndUtc, side.rangeStartUtc, side.rangeEndUtc)
  return {
    left: `${left}%`,
    width: `${Math.max(0.35, right - left)}%`,
    borderColor: BODY_COLORS[event.transitBody] || '#78b8c8',
    backgroundColor: `${BODY_COLORS[event.transitBody] || '#78b8c8'}22`,
  }
}

function eventMarkerStyle(event: MultiOscillatorActivityEvent, side: MultiOscillatorActivitySide): CSSProperties {
  return { left: `${percentBetween(event.exactUtc, side.rangeStartUtc, side.rangeEndUtc)}%` }
}

function formatUtc(value: string): string {
  return value.replace('T', ' ').replace('.000Z', 'Z')
}

function ActivityCountLane({
  side,
  intervals,
  onSelectTimestamp,
}: {
  side: MultiOscillatorActivitySide
  intervals: MultiOscillatorActivityInterval[]
  onSelectTimestamp: (timestampUtc: string) => void
}) {
  const maximum = Math.max(1, ...intervals.map((interval) => interval.rawActiveEventCount))
  return <div className="mo-count-lane" aria-label={`${side.sideIdentity} raw active event count`}>
    {intervals.map((interval) => <button
      key={interval.intervalId}
      type="button"
      className={`mo-count-segment ${interval.coverage === 'UNKNOWN' ? 'is-unknown' : ''}`}
      style={{ ...intervalStyle(interval, side), height: `${Math.max(5, (interval.rawActiveEventCount / maximum) * 100)}%` }}
      title={`${side.sideIdentity} raw active event count ${interval.rawActiveEventCount} | ${formatUtc(interval.startUtc)} to ${formatUtc(interval.endUtc)}`}
      aria-label={`${side.sideIdentity} activity interval ${interval.rawActiveEventCount} active events`}
      onClick={() => onSelectTimestamp(interval.startUtc)}
    >{interval.rawActiveEventCount > 0 ? interval.rawActiveEventCount : ''}</button>)}
  </div>
}

function EventRaster({
  side,
  events,
  selectedEventId,
  onSelectEvent,
}: {
  side: MultiOscillatorActivitySide
  events: MultiOscillatorActivityEvent[]
  selectedEventId: string | null
  onSelectEvent: (event: MultiOscillatorActivityEvent) => void
}) {
  return <div className="mo-event-raster" aria-label={`${side.sideIdentity} applying to separating event spans`}>
    {events.map((event, index) => <button
      key={event.eventId}
      type="button"
      className={`mo-event-span ${selectedEventId === event.eventId ? 'is-selected' : ''}`}
      style={{ ...eventStyle(event, side), top: `${(index % 4) * 22 + 3}px` }}
      title={`${event.transitBody} to ${event.natalTarget} ${event.aspectType} | ${formatUtc(event.applyingStartUtc)} to ${formatUtc(event.separatingEndUtc)}`}
      aria-label={`Inspect ${side.sideIdentity} ${event.transitBody} ${event.aspectType} event`}
      onClick={() => onSelectEvent(event)}
    >{event.transitBody} / {event.aspectType}</button>)}
    {events.map((event) => <button
      key={`${event.eventId}-exact`}
      type="button"
      className={`mo-event-marker ${selectedEventId === event.eventId ? 'is-selected' : ''}`}
      style={eventMarkerStyle(event, side)}
      title={`Exact ${formatUtc(event.exactUtc)}`}
      aria-label={`Select exact timestamp for ${side.sideIdentity} ${event.transitBody} ${event.aspectType}`}
      onClick={() => onSelectEvent(event)}
    />)}
  </div>
}

function EventInspector({ event }: { event: MultiOscillatorActivityEvent | null }) {
  if (!event) return <div className="mo-event-inspector is-empty"><Eye size={14} /><span>Select an event span or exact marker to inspect immutable provenance.</span></div>
  return <div className="mo-event-inspector" aria-label="Selected multi-oscillator event provenance">
    <header><strong>Selected event provenance</strong><span>{event.sideIdentity} | CANONICAL_COMPILER_EVENT</span></header>
    <dl>
      <div><dt>Event ID</dt><dd>{event.eventId}</dd></div>
      <div><dt>Event hash</dt><dd>{event.eventHash}</dd></div>
      <div><dt>Exact UTC</dt><dd>{formatUtc(event.exactUtc)}</dd></div>
      <div><dt>Applying start</dt><dd>{formatUtc(event.applyingStartUtc)}</dd></div>
      <div><dt>Separating end</dt><dd>{formatUtc(event.separatingEndUtc)}</dd></div>
      <div><dt>Transit body</dt><dd>{event.transitBody}</dd></div>
      <div><dt>Natal target</dt><dd>{event.natalTarget}</dd></div>
      <div><dt>Aspect</dt><dd>{event.aspectType}</dd></div>
      <div><dt>Event contract</dt><dd>{event.eventContract || 'CHART_CONDITIONED_TRANSIT_EVENT_RANGE_V1'}</dd></div>
      <div><dt>Astronomy</dt><dd>{event.astronomyContract || 'Canonical compiler contract'}</dd></div>
      <div><dt>Generator</dt><dd>{event.generatorVersion || 'Canonical event compiler'}</dd></div>
      <div><dt>Chart</dt><dd>{event.chartId}</dd></div>
      <div><dt>Hypothesis</dt><dd>{event.chartHypothesisId}</dd></div>
      <div><dt>Polarity</dt><dd>NOT ASSIGNED</dd></div>
      <div><dt>Magnitude</dt><dd>NOT CONFIGURED</dd></div>
    </dl>
  </div>
}

function SideActivity({
  side,
  events,
  intervals,
  selectedEventId,
  onSelectEvent,
  onSelectTimestamp,
}: {
  side: MultiOscillatorActivitySide
  events: MultiOscillatorActivityEvent[]
  intervals: MultiOscillatorActivityInterval[]
  selectedEventId: string | null
  onSelectEvent: (event: MultiOscillatorActivityEvent) => void
  onSelectTimestamp: (timestampUtc: string) => void
}) {
  return <section className="mo-side-activity" aria-label={`${side.sideIdentity} unsigned activity lane`}>
    <header>
      <div><strong>{side.sideIdentity} unsigned activity</strong><span>{side.instrumentIdentity} | {side.eligibleEventCount} events in range</span></div>
      <span className={side.coverage === 'KNOWN' ? 'mo-known' : 'mo-unknown'}>{side.coverage === 'KNOWN' ? 'KNOWN COVERAGE' : 'UNKNOWN COVERAGE'}</span>
    </header>
    <div className="mo-lane-label">Applying-to-separating spans and exact markers</div>
    <EventRaster side={side} events={events} selectedEventId={selectedEventId} onSelectEvent={onSelectEvent} />
    <div className="mo-lane-label">Raw active-event count (integer activity, not score)</div>
    <ActivityCountLane side={side} intervals={intervals} onSelectTimestamp={onSelectTimestamp} />
    <div className="mo-side-summary">
      <span>Range {formatUtc(side.rangeStartUtc)} to {formatUtc(side.rangeEndUtc)}</span>
      <span>{side.coverage === 'KNOWN' ? 'No active event is a known zero.' : side.unknownReason || 'Coverage unavailable.'}</span>
    </div>
  </section>
}

export function MultiOscillatorActivityPanel({
  activity,
  busy,
  error,
  isFxPair,
  crosshairTimestampUtc,
  onLoad,
  onSelectEventTimestamp,
}: Props) {
  const [selectedBodies, setSelectedBodies] = useState<string[] | null>(null)
  const [selectedAspects, setSelectedAspects] = useState<string[] | null>(null)
  const [selectedEventId, setSelectedEventId] = useState<string | null>(null)

  useEffect(() => {
    setSelectedBodies(activity?.eventUniverse.bodyUniverse ?? null)
    setSelectedAspects(activity?.eventUniverse.aspectTypes ?? null)
    setSelectedEventId(null)
  }, [activity?.rangeStartUtc, activity?.rangeEndUtc, activity?.eventUniverse.profileHash, activity?.eventUniverse.bodyUniverse, activity?.eventUniverse.aspectTypes])

  const activeBodies = useMemo(
    () => selectedBodies ?? activity?.eventUniverse.bodyUniverse ?? [],
    [activity?.eventUniverse.bodyUniverse, selectedBodies],
  )
  const activeAspects = useMemo(
    () => selectedAspects ?? activity?.eventUniverse.aspectTypes ?? [],
    [activity?.eventUniverse.aspectTypes, selectedAspects],
  )

  const selectedEventsBySide = useMemo(() => {
    const result: Record<'USD' | 'JPY', MultiOscillatorActivityEvent[]> = { USD: [], JPY: [] }
    if (!activity) return result
    for (const side of activity.sideIdentities) {
      result[side] = activity.fields[side].events.filter((event) => activeBodies.includes(event.transitBody) && activeAspects.includes(event.aspectType))
    }
    return result
  }, [activeAspects, activeBodies, activity])

  const filteredIntervals = useMemo(() => {
    const result: Record<'USD' | 'JPY', MultiOscillatorActivityInterval[]> = { USD: [], JPY: [] }
    if (!activity) return result
    const visibleIds = new Set([...selectedEventsBySide.USD, ...selectedEventsBySide.JPY].map((event) => event.eventId))
    for (const side of activity.sideIdentities) {
      result[side] = activity.fields[side].activityIntervals.map((interval) => {
        const ids = interval.contributingEventIds.filter((eventId) => visibleIds.has(eventId))
        return { ...interval, contributingEventIds: ids, rawActiveEventCount: ids.length }
      })
    }
    return result
  }, [activity, selectedEventsBySide])

  const selectedEvent = activity
    ? activity.fields.USD.events.find((event) => event.eventId === selectedEventId)
      || activity.fields.JPY.events.find((event) => event.eventId === selectedEventId)
      || null
    : null

  if (!isFxPair) return <section className="multi-oscillator-panel" aria-label="Unsigned multi-oscillator activity"><header><Activity size={16} /><div><strong>Multi Oscillator</strong><span>Unsigned event activity</span></div></header><p className="mo-unavailable">This activity inspector is bounded to the accepted USDJPY FX side identities. Stock instruments keep their existing independent field contract.</p></section>

  return <section className="multi-oscillator-panel" aria-label="Unsigned multi-oscillator activity">
    <header className="mo-panel-header">
      <div><Activity size={16} /><div><strong>Multi Oscillator / Event Activity</strong><span>Backend-owned event presence for the shared Fields research window</span></div></div>
      <div className="mo-badges"><span>EXPLORATORY_UNSIGNED</span><span>UNSIGNED</span><span>NON-PREDICTIVE</span><span>MAGNITUDE NOT CONFIGURED</span></div>
    </header>
    <div className="mo-contract-note"><ShieldCheck size={14} /><span>Experimental geometry profile {activity?.eventUniverse.profileId || 'ASPECT_STRENGTH_V0'} supplies event activity only. It does not supply direction, score, magnitude, smoothing, or a USD-JPY difference.</span></div>
    {busy ? <div className="mo-loading">Compiling immutable USD/JPY astronomy events for this research window...</div> : null}
    {error ? <div className="mo-error" role="alert"><strong>Activity unavailable</strong><span>{error}</span><button type="button" onClick={onLoad}>Retry activity range</button></div> : null}
    {!busy && !error && !activity ? <div className="mo-empty"><span>No activity range loaded.</span><button type="button" onClick={onLoad}>Load unsigned activity</button></div> : null}
    {activity ? <>
      <div className="mo-range-row"><span>UTC range: {formatUtc(activity.rangeStartUtc)} to {formatUtc(activity.rangeEndUtc)}</span><span>Shared crosshair: {crosshairTimestampUtc ? formatUtc(crosshairTimestampUtc) : 'not selected'}</span></div>
      <div className="mo-filter-panel" aria-label="Event activity filters"><div className="mo-filter-title"><Filter size={13} /> Local event filters</div><div className="mo-filter-group"><span>Transit bodies</span>{activity.eventUniverse.bodyUniverse.map((body) => <label key={body}><input type="checkbox" checked={activeBodies.includes(body)} onChange={(event) => setSelectedBodies((current) => { const base = current ?? activity.eventUniverse.bodyUniverse; return event.target.checked ? [...base, body] : base.filter((item) => item !== body) })} />{body}</label>)}</div><div className="mo-filter-group"><span>Aspects</span>{activity.eventUniverse.aspectTypes.map((aspect) => <label key={aspect}><input type="checkbox" checked={activeAspects.includes(aspect)} onChange={(event) => setSelectedAspects((current) => { const base = current ?? activity.eventUniverse.aspectTypes; return event.target.checked ? [...base, aspect] : base.filter((item) => item !== aspect) })} />{aspect}</label>)}</div></div>
      <SideActivity side={activity.fields.USD} events={selectedEventsBySide.USD} intervals={filteredIntervals.USD} selectedEventId={selectedEventId} onSelectEvent={(event) => { setSelectedEventId(event.eventId); onSelectEventTimestamp(event.exactUtc) }} onSelectTimestamp={onSelectEventTimestamp} />
      <SideActivity side={activity.fields.JPY} events={selectedEventsBySide.JPY} intervals={filteredIntervals.JPY} selectedEventId={selectedEventId} onSelectEvent={(event) => { setSelectedEventId(event.eventId); onSelectEventTimestamp(event.exactUtc) }} onSelectTimestamp={onSelectEventTimestamp} />
      <EventInspector event={selectedEvent} />
      <div className="mo-footer-locks"><span>Event IDs and hashes remain immutable.</span><span>Selected crosshair updates the shared research controller.</span><span>No pair-relative unsigned field is created.</span></div>
    </> : null}
  </section>
}
