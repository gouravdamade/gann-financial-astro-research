import {
  BookmarkPlus,
  Crosshair,
  Download,
  FlaskConical,
  Pin,
  PinOff,
  ShieldCheck,
  Trash2,
  X,
} from 'lucide-react'
import { useMemo } from 'react'
import type { MouseEvent } from 'react'
import { collectiveEventTime } from '../collectiveAudit'
import type {
  PlanetaryCollectiveAuditSnapshot,
  PlanetaryCollectiveEvent,
  PlanetaryCollectiveField,
  PlanetaryCollectiveSample,
  PlanetaryCollectiveVisualStudyDossier,
} from '../types'

type CollectiveFieldInspectorProps = {
  field: PlanetaryCollectiveField
  cursorTime: number | null
  pinnedTime: number | null
  onHoverTime: (time: number | null) => void
  onPinTime: (time: number | null) => void
  snapshots: PlanetaryCollectiveAuditSnapshot[]
  onSaveAudit: (time: number) => void
  onExportAudit: (time: number) => void
  onExportSavedAudit: (snapshot: PlanetaryCollectiveAuditSnapshot) => void
  onDeleteSavedAudit: (snapshotId: string) => void
  visualStudy: PlanetaryCollectiveVisualStudyDossier | null
  visualStudyBusy: boolean
  visualStudyError: string
  onBuildVisualStudy: (time: number) => void
  onExportVisualStudy: (dossier: PlanetaryCollectiveVisualStudyDossier) => void
  onClose: () => void
}

const VIEWBOX_WIDTH = 1000
const VIEWBOX_HEIGHT = 350
const PLOT_LEFT = 52
const PLOT_RIGHT = 984
const LANE_HEIGHT = 52

function nearestSample(
  samples: PlanetaryCollectiveSample[],
  target: number,
): PlanetaryCollectiveSample {
  let low = 0
  let high = samples.length - 1
  while (low < high) {
    const middle = Math.floor((low + high) / 2)
    if (samples[middle].time < target) low = middle + 1
    else high = middle
  }
  if (low === 0) return samples[0]
  const before = samples[low - 1]
  const after = samples[low]
  return Math.abs(target - before.time) <= Math.abs(after.time - target)
    ? before
    : after
}

function numberText(
  value: number | null,
  digits = 3,
  suffix = '',
): string {
  return value == null ? 'n/a' : `${value.toFixed(digits)}${suffix}`
}

function eventLabel(event: PlanetaryCollectiveEvent): string {
  if (event.eventType === 'MEAN_RASHI_INGRESS') {
    return `${String(event.details.fromRashi)} to ${String(event.details.toRashi)}`
  }
  if (event.eventType === 'COHERENCE_THRESHOLD_CROSSING') {
    return `${String(event.details.thresholdName).replaceAll('_', ' ')} ${String(event.details.direction).toLowerCase()}`
  }
  return `${String(event.details.fromState).replaceAll('_', ' ')} to ${String(event.details.toState).replaceAll('_', ' ')}`
}

function reliabilityFill(reliability: PlanetaryCollectiveSample['reliability']): string {
  if (reliability === 'RELIABLE') return '#315c6952'
  if (reliability === 'LOW_COHERENCE') return '#80642f52'
  if (reliability === 'UNSTABLE') return '#75534e52'
  return '#6d374052'
}

export function CollectiveFieldInspector({
  field,
  cursorTime,
  pinnedTime,
  onHoverTime,
  onPinTime,
  snapshots,
  onSaveAudit,
  onExportAudit,
  onExportSavedAudit,
  onDeleteSavedAudit,
  visualStudy,
  visualStudyBusy,
  visualStudyError,
  onBuildVisualStudy,
  onExportVisualStudy,
  onClose,
}: CollectiveFieldInspectorProps) {
  const samples = field.samples.length ? field.samples : [field.latest]
  const startTime = samples[0].time
  const endTime = samples.at(-1)?.time ?? field.latest.time
  const timeSpan = Math.max(1, endTime - startTime)
  const xFor = (time: number) => (
    PLOT_LEFT + ((time - startTime) / timeSpan) * (PLOT_RIGHT - PLOT_LEFT)
  )
  const activeTime = cursorTime ?? pinnedTime ?? field.latest.time
  const selected = nearestSample(samples.length ? samples : [field.latest], activeTime)
  const selectedIndex = Math.max(0, samples.findIndex((sample) => sample.time === selected.time))
  const selectedX = xFor(selected.time)
  const velocityLimit = Math.max(
    0.001,
    ...samples.flatMap((sample) => (
      sample.velocityDegPerDay == null ? [] : [Math.abs(sample.velocityDegPerDay)]
    )),
  )

  const pathFor = (
    valueFor: (sample: PlanetaryCollectiveSample) => number | null,
    laneTop: number,
    minimum: number,
    maximum: number,
    breakBySegment = false,
  ) => {
    let path = ''
    let drawing = false
    let previousSegment: number | null = null
    for (const sample of samples) {
      const value = valueFor(sample)
      const segmentChanged = breakBySegment && sample.segmentId !== previousSegment
      if (value == null || (breakBySegment && sample.segmentId == null)) {
        drawing = false
        previousSegment = sample.segmentId
        continue
      }
      const ratio = (value - minimum) / Math.max(1e-12, maximum - minimum)
      const y = laneTop + LANE_HEIGHT - Math.max(0, Math.min(1, ratio)) * LANE_HEIGHT
      path += `${drawing && !segmentChanged ? ' L' : ' M'} ${xFor(sample.time).toFixed(2)} ${y.toFixed(2)}`
      drawing = true
      previousSegment = sample.segmentId
    }
    return path.trim()
  }

  const meanPath = pathFor(
    (sample) => sample.meanLongitudeDeg,
    20,
    0,
    360,
    true,
  )
  const r1Path = pathFor((sample) => sample.coherenceR1, 92, 0, 1)
  const r2Path = pathFor((sample) => sample.polarisationR2, 164, 0, 1)
  const variancePath = pathFor((sample) => sample.circularVariance, 164, 0, 1)
  const velocityPath = pathFor(
    (sample) => sample.velocityDegPerDay,
    236,
    -velocityLimit,
    velocityLimit,
    true,
  )
  const memberRows = useMemo(
    () => [...selected.memberAudit].sort((left, right) => (
      (left.influenceRank ?? 999) - (right.influenceRank ?? 999)
      || left.body.localeCompare(right.body)
    )),
    [selected],
  )
  const nearbyEvents = useMemo(
    () => [...field.events]
      .sort((left, right) => (
        Math.abs(collectiveEventTime(left) - selected.time)
        - Math.abs(collectiveEventTime(right) - selected.time)
      ))
      .slice(0, 4),
    [field.events, selected.time],
  )

  const pointerSample = (event: MouseEvent<SVGSVGElement>) => {
    const bounds = event.currentTarget.getBoundingClientRect()
    const plotRatio = Math.max(
      0,
      Math.min(
        1,
        ((event.clientX - bounds.left) / Math.max(1, bounds.width) * VIEWBOX_WIDTH - PLOT_LEFT)
          / (PLOT_RIGHT - PLOT_LEFT),
      ),
    )
    return nearestSample(samples, startTime + plotRatio * timeSpan)
  }

  return (
    <section className="collective-field-inspector" aria-label="Planetary collective field inspector">
      <header>
        <span className={`collective-field-glyph is-${selected.reliability.toLowerCase()}`} aria-hidden="true" />
        <div>
          <strong>Planetary Collective Field</strong>
          <span>AVG {field.profile.members.length} | synthetic research geometry</span>
        </div>
        <output aria-live="polite">
          {new Date(selected.time * 1000).toLocaleString()} | {selected.state.replaceAll('_', ' ')}
        </output>
        <button
          className={pinnedTime != null ? 'icon-button is-active' : 'icon-button'}
          onClick={() => onPinTime(pinnedTime == null ? selected.time : null)}
          title={pinnedTime == null ? 'Pin selected collective timestamp' : 'Clear pinned collective timestamp'}
          aria-label={pinnedTime == null ? 'Pin selected collective timestamp' : 'Clear pinned collective timestamp'}
        >
          {pinnedTime == null ? <Pin size={14} /> : <PinOff size={14} />}
        </button>
        <button
          className="icon-button"
          onClick={() => onSaveAudit(selected.time)}
          title="Save selected collective audit in this chart layout"
          aria-label="Save selected collective audit"
        >
          <BookmarkPlus size={15} />
        </button>
        <button
          className="icon-button"
          onClick={() => onExportAudit(selected.time)}
          title="Export selected collective audit as JSON"
          aria-label="Export selected collective audit"
        >
          <Download size={15} />
        </button>
        <button
          className="icon-button"
          onClick={() => onBuildVisualStudy(selected.time)}
          disabled={visualStudyBusy}
          title="Build timestamp-matched M7 Gann and SBC visual study"
          aria-label="Build M7 visual study"
        >
          <FlaskConical size={15} />
        </button>
        <button className="icon-button" onClick={onClose} title="Close collective field inspector" aria-label="Close collective field inspector">
          <X size={15} />
        </button>
      </header>

      <div className="collective-field-inspector-body">
        <div className="collective-field-plot-pane">
          <svg
            className="collective-field-chart"
            viewBox={`0 0 ${VIEWBOX_WIDTH} ${VIEWBOX_HEIGHT}`}
            preserveAspectRatio="none"
            role="img"
            aria-labelledby="collective-field-chart-title collective-field-chart-description"
            onMouseMove={(event) => onHoverTime(pointerSample(event).time)}
            onMouseLeave={() => onHoverTime(null)}
            onClick={(event) => onPinTime(pointerSample(event).time)}
          >
            <title id="collective-field-chart-title">AVG collective geometry diagnostic lanes</title>
            <desc id="collective-field-chart-description">
              Wrapped mean longitude, coherence R1, polarisation R2, variance, velocity, reliability, sampled heuristic events, and eligible ephemeris-refined ingress roots.
            </desc>
            {samples.slice(0, -1).map((sample, index) => {
              const next = samples[index + 1]
              return (
                <rect
                  key={`${sample.time}:reliability`}
                  x={xFor(sample.time)}
                  y={10}
                  width={Math.max(1, xFor(next.time) - xFor(sample.time))}
                  height={298}
                  fill={reliabilityFill(sample.reliability)}
                />
              )
            })}
            {[20, 92, 164, 236, 308].map((y) => (
              <line key={y} x1={PLOT_LEFT} x2={PLOT_RIGHT} y1={y + LANE_HEIGHT} y2={y + LANE_HEIGHT} className="collective-field-grid-line" />
            ))}
            <text x={8} y={48}>Mean</text>
            <text x={8} y={120}>R1</text>
            <text x={8} y={192}>R2/V</text>
            <text x={8} y={264}>Speed</text>
            <line x1={PLOT_LEFT} x2={PLOT_RIGHT} y1={92 + LANE_HEIGHT * 0.8} y2={92 + LANE_HEIGHT * 0.8} className="collective-field-threshold is-low" />
            <line x1={PLOT_LEFT} x2={PLOT_RIGHT} y1={92 + LANE_HEIGHT * 0.35} y2={92 + LANE_HEIGHT * 0.35} className="collective-field-threshold is-high" />
            <line x1={PLOT_LEFT} x2={PLOT_RIGHT} y1={236 + LANE_HEIGHT / 2} y2={236 + LANE_HEIGHT / 2} className="collective-field-zero-line" />
            <path d={meanPath} className="collective-field-path is-mean" />
            <path d={r1Path} className="collective-field-path is-r1" />
            <path d={r2Path} className="collective-field-path is-r2" />
            <path d={variancePath} className="collective-field-path is-variance" />
            <path d={velocityPath} className="collective-field-path is-velocity" />
            {field.events.map((event) => (
              <g key={event.eventId}>
                <line
                  x1={xFor(collectiveEventTime(event))}
                  x2={xFor(collectiveEventTime(event))}
                  y1={314}
                  y2={340}
                  className={`collective-field-event is-${event.eventType.toLowerCase()}`}
                />
                <circle
                  cx={xFor(collectiveEventTime(event))}
                  cy={326}
                  r={4}
                  className={`collective-field-event-dot is-${event.eventType.toLowerCase()}`}
                >
                  <title>
                    {eventLabel(event)} | {event.timing.exact
                      ? 'ephemeris-refined root'
                      : 'approximate sampled time'}
                  </title>
                </circle>
              </g>
            ))}
            <line x1={selectedX} x2={selectedX} y1={10} y2={340} className={pinnedTime != null ? 'collective-field-crosshair is-pinned' : 'collective-field-crosshair'} />
            {selected.longitudeReliable && selected.meanLongitudeDeg != null && (
              <circle
                cx={selectedX}
                cy={20 + LANE_HEIGHT - (selected.meanLongitudeDeg / 360) * LANE_HEIGHT}
                r={6}
                className={`collective-field-selected-marker is-${selected.reliability.toLowerCase()}`}
              />
            )}
          </svg>
          <div className="collective-field-time-control">
            <Crosshair size={13} aria-hidden="true" />
            <input
              type="range"
              min={0}
              max={Math.max(0, samples.length - 1)}
              value={selectedIndex}
              onChange={(event) => onHoverTime(samples[Number(event.target.value)]?.time ?? null)}
              onDoubleClick={() => onPinTime(selected.time)}
              aria-label="Collective field timestamp"
            />
            <span>{samples.length} bar-time samples</span>
            <span>{field.events.length} research events</span>
          </div>
        </div>

        <aside className="collective-field-audit-pane" aria-label="Selected collective timestamp audit">
          <div className="collective-field-audit-metrics">
            <span><small>Mean</small><strong>{numberText(selected.meanLongitudeDeg, 2, ' deg')}</strong></span>
            <span><small>R1</small><strong>{numberText(selected.coherenceR1)}</strong></span>
            <span><small>R2</small><strong>{numberText(selected.polarisationR2)}</strong></span>
            <span><small>Variance</small><strong>{numberText(selected.circularVariance)}</strong></span>
            <span><small>Axis</small><strong>{numberText(selected.polarisationAxisDeg, 2, ' deg')}</strong></span>
            <span><small>Speed</small><strong>{numberText(selected.velocityDegPerDay, 3, ' deg/day')}</strong></span>
          </div>
          <div className="collective-field-audit-identity">
            <strong>{selected.reliability.replaceAll('_', ' ')}</strong>
            <span>Segment {selected.segmentId ?? 'none'}</span>
            <code title={field.profile.memberSetHash}>{field.profile.profileId}</code>
          </div>
          <div className="collective-field-member-table-wrap">
            <table className="collective-field-member-table">
              <caption>Leave-one-out member influence at selected timestamp</caption>
              <thead>
                <tr>
                  <th>Body</th>
                  <th>Longitude</th>
                  <th>Distance</th>
                  <th>Mean leverage</th>
                  <th>R1 effect</th>
                  <th>Role</th>
                </tr>
              </thead>
              <tbody>
                {memberRows.map((member) => (
                  <tr key={member.body} title={member.role.replaceAll('_', ' ').toLowerCase()}>
                    <th>{member.influenceRank ?? '-'} {member.body}</th>
                    <td>{numberText(member.longitudeDeg, 2, ' deg')}</td>
                    <td>{numberText(member.angularDistanceFromMeanDeg, 2, ' deg')}</td>
                    <td>{numberText(member.longitudeLeverageDeg, 2, ' deg')}</td>
                    <td className={(member.coherenceLeverage ?? 0) >= 0 ? 'is-positive' : 'is-negative'}>
                      {numberText(member.coherenceLeverage, 3)}
                    </td>
                    <td className="collective-field-member-role">
                      {member.role.replaceAll('_', ' ').toLowerCase()}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <div className="collective-field-event-list">
            <strong>Nearest research events</strong>
            {nearbyEvents.length ? nearbyEvents.map((event) => (
              <div key={event.eventId}>
                <span>{eventLabel(event)}</span>
                <time dateTime={new Date(collectiveEventTime(event) * 1000).toISOString()}>
                  {new Date(collectiveEventTime(event) * 1000).toLocaleString()}
                </time>
                <small>
                  {event.timing.exact
                    ? `ephemeris root within ${event.timing.rootToleranceSeconds}s`
                    : 'estimated between exact samples'}
                </small>
              </div>
            )) : <span>No research event in this range</span>}
          </div>
          <div className="collective-field-visual-study">
            <div>
              <strong>M7 visual study</strong>
              <span>Gann geometry + timestamp-matched SBC</span>
            </div>
            {visualStudyBusy && <p>Building guarded evidence dossier...</p>}
            {visualStudyError && <p className="is-error">{visualStudyError}</p>}
            {!visualStudyBusy && !visualStudyError && !visualStudy && (
              <p>Build an export-only packet. No direction or outcome label is inferred.</p>
            )}
            {visualStudy && (
              <>
                <div className="collective-field-visual-study-summary">
                  <span>
                    <small>Gann</small>
                    <strong>{visualStudy.gannStudy.fanCount} visible fan{visualStudy.gannStudy.fanCount === 1 ? '' : 's'}</strong>
                  </span>
                  <span>
                    <small>SBC</small>
                    <strong>{visualStudy.sbcStudy.snapshot.guidance?.guidance_band ?? 'context only'}</strong>
                  </span>
                </div>
                <code title={visualStudy.studyFingerprintSha256}>
                  {visualStudy.studyFingerprintSha256.slice(0, 16)}...
                </code>
                <div className="collective-field-visual-study-freeze">
                  Frozen packet | trial not registered | existing cohort unchanged
                </div>
                <button
                  className="secondary-command"
                  onClick={() => onExportVisualStudy(visualStudy)}
                >
                  <Download size={12} />
                  Export M7 dossier
                </button>
              </>
            )}
          </div>
          <div className="collective-field-snapshot-list">
            <strong>Saved audit snapshots</strong>
            {snapshots.length ? snapshots.map((snapshot) => (
              <div key={snapshot.snapshotId}>
                <button
                  className="collective-field-snapshot-time"
                  onClick={() => onPinTime(snapshot.selectedTimeUnix)}
                  title="Pin this saved audit timestamp"
                >
                  <Pin size={11} />
                  <time dateTime={new Date(snapshot.selectedTimeUnix * 1000).toISOString()}>
                    {new Date(snapshot.selectedTimeUnix * 1000).toLocaleString()}
                  </time>
                </button>
                <button
                  className="icon-button"
                  onClick={() => onExportSavedAudit(snapshot)}
                  title="Export saved collective audit"
                  aria-label={`Export saved audit ${snapshot.selectedTimeUnix}`}
                >
                  <Download size={12} />
                </button>
                <button
                  className="icon-button"
                  onClick={() => onDeleteSavedAudit(snapshot.snapshotId)}
                  title="Delete saved collective audit"
                  aria-label={`Delete saved audit ${snapshot.selectedTimeUnix}`}
                >
                  <Trash2 size={12} />
                </button>
              </div>
            )) : <span>No saved audit snapshots</span>}
          </div>
          <footer>
            <ShieldCheck size={13} />
            <span>Coefficient 0.0 | no Vedha | no inference | no execution</span>
          </footer>
        </aside>
      </div>
    </section>
  )
}
