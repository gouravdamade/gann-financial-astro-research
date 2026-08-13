import { BookOpenText, CalendarDays, RefreshCw } from 'lucide-react'
import { useEffect, useMemo, useRef, useState } from 'react'
import { fetchBphsClassicalCalendarRange } from '../api'
import type { BphsClassicalCalendarInterval, BphsClassicalCalendarRange } from '../types'

const PROFILE_ID = 'BPHS_1899_CLASSICAL_CALENDAR_RESEARCH_V1' as const
const LABELS = {
  muhurta: 'Muhurta',
  tithi: 'Tithi',
  nakshatra: 'Nakshatra',
  yoga: 'Yoga',
  karana: 'Karana',
  weekday: 'Civil weekday (engineering)',
  tara: 'Tara',
} as const

type Props = {
  rangeStartUtc: string
  rangeEndUtc: string
  timezone: string
  latitude: number
  longitude: number
  crosshairTimestampUtc: string | null
}

type DisplaySegment = {
  intervalId: string
  startUtc: string
  endUtc: string
  value: string
  availability: string
  detail: string
  sourceLocator: string
  calculationProfile: string
  dependency: string | null
}

function intervalContains(interval: BphsClassicalCalendarInterval, at: string): boolean {
  const time = Date.parse(at)
  return time >= Date.parse(interval.startUtc) && time < Date.parse(interval.endUtc)
}

function localTime(value: string, timezone: string): string {
  return new Intl.DateTimeFormat('en-GB', {
    timeZone: timezone,
    day: '2-digit', month: 'short', hour: '2-digit', minute: '2-digit', hour12: false,
  }).format(new Date(value))
}

function displaySegments(range: BphsClassicalCalendarRange, category: keyof typeof LABELS): DisplaySegment[] {
  const segments: DisplaySegment[] = []
  for (const interval of range.intervals) {
    const state = interval.categories[category]
    const prior = segments.at(-1)
    if (prior && prior.value === state.value && prior.availability === state.availability && prior.endUtc === interval.startUtc) {
      prior.endUtc = interval.endUtc
      continue
    }
    segments.push({
      intervalId: interval.intervalId,
      startUtc: interval.startUtc,
      endUtc: interval.endUtc,
      value: state.value,
      availability: state.availability,
      detail: state.detail,
      sourceLocator: state.sourceLocator,
      calculationProfile: state.calculationProfile,
      dependency: state.dependency,
    })
  }
  return segments
}

export function BphsClassicalTimingPane(props: Props) {
  const [calendar, setCalendar] = useState<BphsClassicalCalendarRange | null>(null)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')
  const [selected, setSelected] = useState<DisplaySegment | null>(null)
  const sequence = useRef(0)
  const cache = useRef(new Map<string, BphsClassicalCalendarRange>())
  const signature = `${props.rangeStartUtc}:${props.rangeEndUtc}:${props.timezone}:${props.latitude}:${props.longitude}`

  useEffect(() => {
    const request = sequence.current + 1
    sequence.current = request
    setBusy(true)
    setError('')
    const cached = cache.current.get(signature)
    if (cached) {
      setCalendar(cached)
      setBusy(false)
      return
    }
    void fetchBphsClassicalCalendarRange({
      rangeStartUtc: props.rangeStartUtc,
      rangeEndUtc: props.rangeEndUtc,
      timezone: props.timezone,
      latitude: props.latitude,
      longitude: props.longitude,
      profileId: PROFILE_ID,
    }).then((result) => {
      if (request === sequence.current) {
        cache.current.set(signature, result)
        setCalendar(result)
      }
    }).catch((caught: unknown) => {
      if (request === sequence.current) {
        setCalendar(null)
        setError(caught instanceof Error ? caught.message : String(caught))
      }
    }).finally(() => {
      if (request === sequence.current) setBusy(false)
    })
  }, [signature, props.latitude, props.longitude, props.rangeEndUtc, props.rangeStartUtc, props.timezone])

  const activeInterval = useMemo(() => {
    const crosshair = props.crosshairTimestampUtc
    if (!calendar || !crosshair) return null
    return calendar.intervals.find((interval) => intervalContains(interval, crosshair)) ?? null
  }, [calendar, props.crosshairTimestampUtc])

  return <section className="bphs-calendar-pane" aria-label="BPHS Classical Calendar">
    <header>
      <div><CalendarDays size={15} /><div><strong>BPHS Classical Calendar</strong><span>Neutral time-aligned categories only. No polarity, score, market meaning, or execution path.</span></div></div>
      <span className="bphs-calendar-status">{busy ? 'Refreshing calendar' : calendar?.sourceProfile.evidenceStatus ?? 'Awaiting calendar'}</span>
    </header>
    {error ? <p className="bphs-calendar-error">Calendar unavailable: {error}</p> : null}
    {!calendar && !error ? <p className="bphs-calendar-empty">{busy ? 'Calculating source-labelled calendar boundaries...' : 'No calendar range is available.'}</p> : null}
    {calendar ? <>
      <div className="bphs-calendar-context">
        <span><b>Profile</b>{calendar.sourceProfile.profileId}</span>
        <span><b>Location</b>{calendar.timezone} | {calendar.location.latitude.toFixed(4)}, {calendar.location.longitude.toFixed(4)}</span>
        <span><b>Engineering</b>{calendar.engineeringCalculationProfile}</span>
      </div>
      <div className="bphs-calendar-lanes" aria-label="Classical calendar categorical lanes">
        {calendar.categoryOrder.map((category) => {
          const segments = displaySegments(calendar, category)
          return <div className="bphs-calendar-lane" key={category}>
            <div><strong>{LABELS[category]}</strong><span>{category === 'tara' ? 'source mapping/reference required' : category === 'weekday' ? 'boundary not closed by Packet 1W' : 'calendar category'}</span></div>
            <div className="bphs-calendar-track">
              {segments.map((segment) => <button
                key={`${category}:${segment.intervalId}:${segment.startUtc}`}
                type="button"
                className={`bphs-calendar-block is-${segment.availability.toLowerCase().replaceAll('_', '-')}${selected?.intervalId === segment.intervalId && selected.value === segment.value ? ' is-selected' : ''}`}
                style={{ flexGrow: Math.max(1, Date.parse(segment.endUtc) - Date.parse(segment.startUtc)), flexBasis: 0 }}
                title={`${LABELS[category]}: ${segment.value}\n${localTime(segment.startUtc, calendar.timezone)} to ${localTime(segment.endUtc, calendar.timezone)}\n${segment.detail}`}
                aria-label={`Select ${LABELS[category]} ${segment.value} from ${segment.startUtc} to ${segment.endUtc}`}
                onClick={() => setSelected(segment)}
              >{segment.value}</button>)}
            </div>
          </div>
        })}
      </div>
      <section className="bphs-calendar-current" aria-label="Calendar state at shared crosshair">
        <header><RefreshCw size={13} /><div><strong>Shared crosshair state</strong><span>{props.crosshairTimestampUtc ? `${props.crosshairTimestampUtc} | ${localTime(props.crosshairTimestampUtc, calendar.timezone)} ${calendar.timezone}` : 'Move over the price chart to inspect a calendar moment.'}</span></div></header>
        {activeInterval ? <div className="bphs-calendar-current-grid">{calendar.categoryOrder.map((category) => <div key={category}><b>{LABELS[category]}</b><span>{activeInterval.categories[category].value}</span><small>{activeInterval.categories[category].availability}</small></div>)}</div> : <p>No active calendar interval in the shared range.</p>}
      </section>
      <section className="bphs-calendar-source-detail" aria-label="BPHS source and provenance">
        <BookOpenText size={14} />
        <div><strong>Source and provenance</strong><span>{calendar.sourceProfile.sourceId} | {calendar.sourceProfile.edition} | {calendar.sourceProfile.scope} | SHA-256 {calendar.sourceProfile.fileSha256}</span><small>{calendar.sourceProfile.interpretation}</small><small>Source gaps: {calendar.sourceProfile.sourceGaps.join(' | ')}</small></div>
      </section>
      {selected ? <section className="bphs-calendar-selection" aria-label="Selected calendar interval"><strong>Selected category</strong><span>{selected.value} | {selected.availability} | {selected.startUtc} to {selected.endUtc}</span><small>{selected.detail} {selected.dependency ? `Dependency: ${selected.dependency}` : ''}</small></section> : null}
    </> : null}
  </section>
}
