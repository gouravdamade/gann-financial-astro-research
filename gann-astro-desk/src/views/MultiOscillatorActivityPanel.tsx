import { Activity, Eye, Filter, ShieldCheck } from 'lucide-react'
import { useEffect, useMemo, useState, type CSSProperties } from 'react'
import type {
  MultiOscillatorActivityEvent,
  MultiOscillatorActivityInterval,
  MultiOscillatorActivityRange,
  MultiOscillatorActivitySide,
} from '../types'
import { eventMatchesActivityFilters } from './MultiOscillatorActivityFilter'
import { deriveSharedRawActivityAxisMax, rawActivityHeightPercent } from './MultiOscillatorActivityScale'
import {
  deriveUnsignedActivityStepSegments,
  MO_UNSIGNED_ACTIVITY_STEP_WAVE_CONTRACT,
  unsignedActivityStepSegmentPath,
  unsignedActivityStepWavePath,
  unsignedActivityWaveIntervalStyle,
  unsignedActivityWaveMarkerStyle,
  WAVE_PLOT_BASELINE,
  WAVE_PLOT_TOP,
  type UnsignedActivityStepSegment,
  type UnsignedActivityWaveSide,
} from './MultiOscillatorActivityWave'

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

function formatAxisUtc(value: string): string {
  const parsed = new Date(value)
  if (!Number.isFinite(parsed.valueOf())) return 'invalid time'
  return `${parsed.toISOString().slice(5, 16).replace('T', ' ')}Z`
}

function eventRasterRowCount(eventCount: number): number {
  return Math.max(4, Math.min(8, Math.ceil(Math.max(1, eventCount) / 8)))
}

function ActivityCountLane({
  side,
  intervals,
  sharedAxisMax,
  onSelectTimestamp,
}: {
  side: MultiOscillatorActivitySide
  intervals: MultiOscillatorActivityInterval[]
  sharedAxisMax: number
  onSelectTimestamp: (timestampUtc: string) => void
}) {
  return <div className="mo-count-lane" aria-label={`${side.sideIdentity} raw active event count`}>
    {intervals.map((interval) => {
      const visibleHeight = rawActivityHeightPercent(interval.rawActiveEventCount, sharedAxisMax)
      return <button
        key={interval.intervalId}
        type="button"
        className={`mo-count-segment ${interval.coverage === 'UNKNOWN' ? 'is-unknown' : ''}`}
        style={{ ...intervalStyle(interval, side), '--mo-activity-height': `${visibleHeight}%` } as CSSProperties}
        title={`${side.sideIdentity} raw active event count ${interval.rawActiveEventCount} | ${formatUtc(interval.startUtc)} to ${formatUtc(interval.endUtc)}`}
        aria-label={`${side.sideIdentity} activity interval ${interval.rawActiveEventCount} active events`}
        onClick={() => onSelectTimestamp(interval.startUtc)}
      ><span className="mo-count-segment-label">{interval.rawActiveEventCount > 0 ? interval.rawActiveEventCount : ''}</span></button>
    })}
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
  const rowCount = eventRasterRowCount(events.length)
  return <div className="mo-event-raster" style={{ height: `${rowCount * 22 + 8}px` }} aria-label={`${side.sideIdentity} applying to separating event spans`}>
    {events.map((event, index) => <button
      key={event.eventId}
      type="button"
      className={`mo-event-span ${selectedEventId === event.eventId ? 'is-selected' : ''}`}
      style={{ ...eventStyle(event, side), top: `${(index % rowCount) * 22 + 3}px` }}
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

function WaveLane({
  side,
  events,
  segments,
  rangeStartUtc,
  rangeEndUtc,
  sharedAxisMax,
  selectedEventId,
  crosshairTimestampUtc,
  onSelectEvent,
  onSelectTimestamp,
}: {
  side: UnsignedActivityWaveSide
  events: MultiOscillatorActivityEvent[]
  segments: UnsignedActivityStepSegment[]
  rangeStartUtc: string
  rangeEndUtc: string
  sharedAxisMax: number
  selectedEventId: string | null
  crosshairTimestampUtc: string | null
  onSelectEvent: (event: MultiOscillatorActivityEvent) => void
  onSelectTimestamp: (timestampUtc: string) => void
}) {
  const unknownSegments = segments.filter((segment) => segment.coverage === 'UNKNOWN')
  const crosshairX = crosshairTimestampUtc
    ? unsignedActivityWaveMarkerStyle({ exactUtc: crosshairTimestampUtc }, rangeStartUtc, rangeEndUtc).left
    : null

  return <article className="mo-wave-lane" aria-label={`${side} unsigned activity step wave`}>
    <header>
      <strong>{side} step wave</strong>
      <span>active-event count | shared axis 0-{sharedAxisMax}</span>
    </header>
    <div className="mo-wave-plot">
      <div className="mo-wave-y-axis" aria-hidden="true"><span>{sharedAxisMax}</span><span>0</span></div>
      <div className="mo-wave-canvas">
        <svg viewBox="0 0 100 100" preserveAspectRatio="none" role="img" aria-label={`${side} exact unsigned activity step trace`}>
          <line className="mo-wave-grid-line" x1="0" x2="100" y1={WAVE_PLOT_TOP} y2={WAVE_PLOT_TOP} />
          <line className="mo-wave-grid-line" x1="0" x2="100" y1={WAVE_PLOT_BASELINE} y2={WAVE_PLOT_BASELINE} />
          <path className="mo-wave-trace" d={unsignedActivityStepWavePath(segments, rangeStartUtc, rangeEndUtc, sharedAxisMax)} />
          {unknownSegments.map((segment) => <g key={`${segment.startUtc}-${segment.endUtc}`}>
            <path className="mo-wave-unknown-trace" d={unsignedActivityStepSegmentPath(segment, rangeStartUtc, rangeEndUtc, sharedAxisMax)} />
            <rect
              className="mo-wave-unknown-band"
              x={Number.parseFloat(unsignedActivityWaveIntervalStyle(segment, rangeStartUtc, rangeEndUtc).left)}
              y="3"
              width={Number.parseFloat(unsignedActivityWaveIntervalStyle(segment, rangeStartUtc, rangeEndUtc).width)}
              height="4"
            />
          </g>)}
          {events.map((event) => <line
            key={`${event.eventId}-wave-marker`}
            className={`mo-wave-event-marker ${selectedEventId === event.eventId ? 'is-selected' : ''}`}
            x1={Number.parseFloat(unsignedActivityWaveMarkerStyle(event, rangeStartUtc, rangeEndUtc).left)}
            x2={Number.parseFloat(unsignedActivityWaveMarkerStyle(event, rangeStartUtc, rangeEndUtc).left)}
            y1="4"
            y2="96"
          />)}
          {crosshairX ? <line className="mo-wave-crosshair" x1={Number.parseFloat(crosshairX)} x2={Number.parseFloat(crosshairX)} y1="0" y2="100" /> : null}
        </svg>
        <div className="mo-wave-interval-hitboxes">
          {segments.map((segment) => {
            const style = unsignedActivityWaveIntervalStyle(segment, rangeStartUtc, rangeEndUtc)
            return <button
              key={`${segment.startUtc}-${segment.endUtc}`}
              type="button"
              className={`mo-wave-interval ${segment.coverage === 'UNKNOWN' ? 'is-unknown' : ''}`}
              style={style}
              title={`${side} raw active event count ${segment.rawActiveEventCount} | ${formatUtc(segment.startUtc)} to ${formatUtc(segment.endUtc)}${segment.coverage === 'UNKNOWN' ? ` | UNKNOWN: ${segment.unknownReason || 'incomplete coverage'}` : ''}`}
              aria-label={`${side} step-wave interval ${segment.rawActiveEventCount} active events${segment.coverage === 'UNKNOWN' ? ' UNKNOWN coverage' : ''}`}
              onClick={() => onSelectTimestamp(segment.startUtc)}
            />
          })}
          {events.map((event) => {
            const style = unsignedActivityWaveMarkerStyle(event, rangeStartUtc, rangeEndUtc)
            return <button
              key={`${event.eventId}-wave-hitbox`}
              type="button"
              className={`mo-wave-marker-hitbox ${selectedEventId === event.eventId ? 'is-selected' : ''}`}
              style={style}
              title={`Exact ${formatUtc(event.exactUtc)} | ${event.transitBody} to ${event.natalTarget} ${event.aspectType}`}
              aria-label={`Select ${side} exact timestamp for ${event.transitBody} ${event.aspectType}`}
              onClick={() => onSelectEvent(event)}
            />
          })}
        </div>
      </div>
    </div>
  </article>
}

function WaveTimeAxis({ rangeStartUtc, rangeEndUtc }: { rangeStartUtc: string; rangeEndUtc: string }) {
  const ticks = [0, 0.25, 0.5, 0.75, 1]
  const startMs = Date.parse(rangeStartUtc)
  const endMs = Date.parse(rangeEndUtc)
  return <div className="mo-wave-time-axis" aria-label="Shared unsigned activity wave time axis">
    <span className="mo-wave-time-axis-title">Shared UTC time axis</span>
    <div className="mo-wave-time-axis-ticks">
      {ticks.map((fraction) => <span key={fraction} style={{ left: `${fraction * 100}%` }}>{formatAxisUtc(new Date(startMs + (endMs - startMs) * fraction).toISOString())}</span>)}
    </div>
  </div>
}

function UnsignedActivityWaveSurface({
  intervalsBySide,
  eventsBySide,
  rangeStartUtc,
  rangeEndUtc,
  sharedAxisMax,
  selectedEventId,
  crosshairTimestampUtc,
  onSelectEvent,
  onSelectTimestamp,
}: {
  intervalsBySide: Record<UnsignedActivityWaveSide, MultiOscillatorActivityInterval[]>
  eventsBySide: Record<UnsignedActivityWaveSide, MultiOscillatorActivityEvent[]>
  rangeStartUtc: string
  rangeEndUtc: string
  sharedAxisMax: number
  selectedEventId: string | null
  crosshairTimestampUtc: string | null
  onSelectEvent: (event: MultiOscillatorActivityEvent) => void
  onSelectTimestamp: (timestampUtc: string) => void
}) {
  const segmentsBySide = {
    USD: deriveUnsignedActivityStepSegments(intervalsBySide.USD),
    JPY: deriveUnsignedActivityStepSegments(intervalsBySide.JPY),
  }

  return <section className="mo-wave-surface" aria-label="Unsigned activity waves">
    <header className="mo-wave-surface-header">
      <div><strong>Unsigned Activity Waves</strong><span>{MO_UNSIGNED_ACTIVITY_STEP_WAVE_CONTRACT} | exact zero-order-hold view of filtered interval counts</span></div>
      <span className="mo-wave-semantic-badge">EXPLORATORY_UNSIGNED</span>
    </header>
    <div className="mo-wave-surface-note" role="note" title="The wave is derived from accepted half-open activity intervals. It assigns no sign or magnitude.">
      <span>Raw activity: 0-{sharedAxisMax} events</span>
      <span>Fill/trace = observed count</span>
      <span>Hatch = incomplete coverage</span>
      <span>Baseline = 0</span>
    </div>
    <WaveLane side="USD" events={eventsBySide.USD} segments={segmentsBySide.USD} rangeStartUtc={rangeStartUtc} rangeEndUtc={rangeEndUtc} sharedAxisMax={sharedAxisMax} selectedEventId={selectedEventId} crosshairTimestampUtc={crosshairTimestampUtc} onSelectEvent={onSelectEvent} onSelectTimestamp={onSelectTimestamp} />
    <WaveLane side="JPY" events={eventsBySide.JPY} segments={segmentsBySide.JPY} rangeStartUtc={rangeStartUtc} rangeEndUtc={rangeEndUtc} sharedAxisMax={sharedAxisMax} selectedEventId={selectedEventId} crosshairTimestampUtc={crosshairTimestampUtc} onSelectEvent={onSelectEvent} onSelectTimestamp={onSelectTimestamp} />
    <WaveTimeAxis rangeStartUtc={rangeStartUtc} rangeEndUtc={rangeEndUtc} />
  </section>
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
  sharedAxisMax,
  selectedEventId,
  onSelectEvent,
  onSelectTimestamp,
}: {
  side: MultiOscillatorActivitySide
  events: MultiOscillatorActivityEvent[]
  intervals: MultiOscillatorActivityInterval[]
  sharedAxisMax: number
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
    <ActivityCountLane side={side} intervals={intervals} sharedAxisMax={sharedAxisMax} onSelectTimestamp={onSelectTimestamp} />
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
  }, [activity?.rangeStartUtc, activity?.rangeEndUtc, activity?.eventUniverse.eventUniverseHash, activity?.eventUniverse.bodyUniverse, activity?.eventUniverse.aspectTypes])

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
      result[side] = activity.fields[side].events.filter((event) => eventMatchesActivityFilters(event, activeBodies, activeAspects))
    }
    return result
  }, [activeAspects, activeBodies, activity])

  const filteredIntervals = useMemo(() => {
    const result: Record<'USD' | 'JPY', MultiOscillatorActivityInterval[]> = { USD: [], JPY: [] }
    if (!activity) return result
    for (const side of activity.sideIdentities) {
      const visibleIds = new Set(selectedEventsBySide[side].map((event) => event.eventId))
      result[side] = activity.fields[side].activityIntervals.map((interval) => {
        const ids = interval.contributingEventIds.filter((eventId) => visibleIds.has(eventId))
        return { ...interval, contributingEventIds: ids, rawActiveEventCount: ids.length }
      })
    }
    return result
  }, [activity, selectedEventsBySide])

  const sharedRawAxisMax = useMemo(
    () => deriveSharedRawActivityAxisMax(filteredIntervals),
    [filteredIntervals],
  )

  const selectedEvent = activity
    ? activity.fields.USD.events.find((event) => event.eventId === selectedEventId)
      || activity.fields.JPY.events.find((event) => event.eventId === selectedEventId)
      || null
    : null

  if (!isFxPair) return <section className="multi-oscillator-panel" aria-label="Unsigned multi-oscillator activity"><header><Activity size={16} /><div><strong>Multi Oscillator</strong><span>Unsigned event activity</span></div></header><p className="mo-unavailable">This activity inspector is bounded to the accepted USDJPY FX side identities. Stock instruments keep their existing independent field contract.</p></section>

  const selectActivityEvent = (event: MultiOscillatorActivityEvent) => {
    setSelectedEventId(event.eventId)
    onSelectEventTimestamp(event.exactUtc)
  }

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
      <UnsignedActivityWaveSurface intervalsBySide={filteredIntervals} eventsBySide={selectedEventsBySide} rangeStartUtc={activity.rangeStartUtc} rangeEndUtc={activity.rangeEndUtc} sharedAxisMax={sharedRawAxisMax} selectedEventId={selectedEventId} crosshairTimestampUtc={crosshairTimestampUtc} onSelectEvent={selectActivityEvent} onSelectTimestamp={onSelectEventTimestamp} />
      <div className="mo-scale-note" role="note" title="Activity fill and trace are observed raw counts. Coverage is independent and does not represent magnitude."><span>Filtered interval detail</span><span>Count bars = raw active events</span><span>Coverage hatch = incomplete coverage</span></div>
      <SideActivity side={activity.fields.USD} events={selectedEventsBySide.USD} intervals={filteredIntervals.USD} sharedAxisMax={sharedRawAxisMax} selectedEventId={selectedEventId} onSelectEvent={selectActivityEvent} onSelectTimestamp={onSelectEventTimestamp} />
      <SideActivity side={activity.fields.JPY} events={selectedEventsBySide.JPY} intervals={filteredIntervals.JPY} sharedAxisMax={sharedRawAxisMax} selectedEventId={selectedEventId} onSelectEvent={selectActivityEvent} onSelectTimestamp={onSelectEventTimestamp} />
      <EventInspector event={selectedEvent} />
      <div className="mo-footer-locks"><span>Event IDs and hashes remain immutable.</span><span>Selected crosshair updates the shared research controller.</span><span>No pair-relative unsigned field is created.</span></div>
    </> : null}
  </section>
}
