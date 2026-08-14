import { BookOpenText, CalendarDays, RefreshCw } from 'lucide-react'
import { useEffect, useMemo, useRef, useState } from 'react'
import { fetchBphsClassicalCalendarRange } from '../api'
import type { BphsClassicalCalendarInterval, BphsClassicalCalendarRange } from '../types'

const PROFILE_ID = 'BPHS_1899_CLASSICAL_CALENDAR_RESEARCH_V1' as const
const BPHS_VISIBLE_WINDOW_DAYS = 3
const DAY_MS = 24 * 60 * 60 * 1000
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
  researchPageLabel?: string
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

function localDate(value: string, timezone: string): string {
  const parts = new Intl.DateTimeFormat('en-US', {
    timeZone: timezone,
    year: 'numeric', month: '2-digit', day: '2-digit',
  }).formatToParts(new Date(value))
  const part = (type: 'year' | 'month' | 'day') => parts.find((entry) => entry.type === type)?.value ?? ''
  return `${part('year')}-${part('month')}-${part('day')}`
}

function intervalPercent(startUtc: string, endUtc: string, rangeStartUtc: string, rangeEndUtc: string): number {
  const total = Date.parse(rangeEndUtc) - Date.parse(rangeStartUtc)
  if (total <= 0) return 0
  return ((Date.parse(endUtc) - Date.parse(startUtc)) / total) * 100
}

function visibleWindowForScroll(
  rangeStartUtc: string,
  rangeEndUtc: string,
  scrollLeft: number,
  scrollWidth: number,
  clientWidth: number,
  visibleDays = BPHS_VISIBLE_WINDOW_DAYS,
): { startUtc: string; endUtc: string; loadedDays: number; visibleDays: number } {
  const rangeStart = Date.parse(rangeStartUtc)
  const rangeEnd = Date.parse(rangeEndUtc)
  const totalMs = Math.max(0, rangeEnd - rangeStart)
  const loadedDays = Math.max(1, Math.ceil(totalMs / DAY_MS))
  const visibleMs = Math.min(totalMs || DAY_MS, visibleDays * DAY_MS)
  const maxStartMs = Math.max(0, totalMs - visibleMs)
  const maxScroll = Math.max(0, scrollWidth - clientWidth)
  const ratio = maxScroll > 0 ? Math.min(1, Math.max(0, scrollLeft / maxScroll)) : 0
  const startMs = Math.round(maxStartMs * ratio)
  return {
    startUtc: new Date(rangeStart + startMs).toISOString(),
    endUtc: new Date(rangeStart + startMs + visibleMs).toISOString(),
    loadedDays,
    visibleDays: Math.max(1, Math.ceil(visibleMs / DAY_MS)),
  }
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
  const [scrollLeft, setScrollLeft] = useState(0)
  const scrollRef = useRef<HTMLDivElement | null>(null)
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

  const viewport = useMemo(() => {
    if (!calendar) return null
    const totalMs = Date.parse(calendar.rangeEndUtc) - Date.parse(calendar.rangeStartUtc)
    const loadedDays = Math.max(1, Math.ceil(totalMs / DAY_MS))
    const visibleDays = Math.min(BPHS_VISIBLE_WINDOW_DAYS, loadedDays)
    const scrollWidth = scrollRef.current?.scrollWidth ?? 0
    const clientWidth = scrollRef.current?.clientWidth ?? 0
    return visibleWindowForScroll(
      calendar.rangeStartUtc,
      calendar.rangeEndUtc,
      scrollLeft,
      scrollWidth,
      clientWidth,
      visibleDays,
    )
  }, [calendar, scrollLeft])

  const timelineWidth = useMemo(() => {
    if (!calendar) return '100%'
    const totalMs = Date.parse(calendar.rangeEndUtc) - Date.parse(calendar.rangeStartUtc)
    const visibleMs = Math.min(totalMs || DAY_MS, BPHS_VISIBLE_WINDOW_DAYS * DAY_MS)
    return `${Math.max(100, (totalMs / visibleMs) * 100)}%`
  }, [calendar])

  const axisDays = useMemo(() => {
    if (!calendar) return []
    const rangeStart = Date.parse(calendar.rangeStartUtc)
    const rangeEnd = Date.parse(calendar.rangeEndUtc)
    const days = []
    for (let timestamp = rangeStart; timestamp < rangeEnd; timestamp += DAY_MS) {
      days.push({
        timestamp,
        left: ((timestamp - rangeStart) / Math.max(1, rangeEnd - rangeStart)) * 100,
        label: localDate(new Date(timestamp).toISOString(), calendar.timezone),
      })
    }
    return days
  }, [calendar])

  useEffect(() => {
    setScrollLeft(0)
    if (scrollRef.current) scrollRef.current.scrollLeft = 0
  }, [calendar?.rangeStartUtc, calendar?.rangeEndUtc])

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
      <div className="bphs-calendar-window-summary" aria-live="polite">
        <span><b>Research page</b>{localDate(calendar.rangeStartUtc, calendar.timezone)} -&gt; {localDate(calendar.rangeEndUtc, calendar.timezone)}{props.researchPageLabel ? ` | ${props.researchPageLabel}` : ''} | max 14 days</span>
        {viewport ? <span><b>BPHS visible window</b>Viewing {localDate(viewport.startUtc, calendar.timezone)} -&gt; {localDate(viewport.endUtc, calendar.timezone)} | {viewport.visibleDays} of {viewport.loadedDays} loaded days</span> : null}
      </div>
      <div className="bphs-calendar-viewport" aria-label="BPHS shared 3-day viewport">
        <div className="bphs-calendar-viewport-labels" aria-hidden="true">
          <div className="bphs-calendar-axis-label">Calendar day</div>
          {calendar.categoryOrder.map((category) => <div className="bphs-calendar-row-label" key={category}>
            <strong>{LABELS[category]}</strong><span>{category === 'tara' ? 'source mapping/reference required' : category === 'weekday' ? 'boundary not closed by Packet 1W' : 'calendar category'}</span>
          </div>)}
        </div>
        <div
          className="bphs-calendar-scroll"
          ref={scrollRef}
          onScroll={(event) => setScrollLeft(event.currentTarget.scrollLeft)}
          aria-label="Scroll the loaded 14-day BPHS calendar"
        >
          <div className="bphs-calendar-timeline" style={{ width: timelineWidth }}>
            <div className="bphs-calendar-axis" aria-hidden="true">
              {axisDays.map((day) => <span key={day.timestamp} style={{ left: `${day.left}%` }}>{day.label}</span>)}
            </div>
            {calendar.categoryOrder.map((category) => {
              const segments = displaySegments(calendar, category)
              return <div className="bphs-calendar-row" key={category}>
                <div className="bphs-calendar-track">
                  {segments.map((segment) => <button
                    key={`${category}:${segment.intervalId}:${segment.startUtc}`}
                    type="button"
                    className={`bphs-calendar-block is-${segment.availability.toLowerCase().replaceAll('_', '-')}${selected?.intervalId === segment.intervalId && selected.value === segment.value ? ' is-selected' : ''}`}
                    style={{ width: `${intervalPercent(segment.startUtc, segment.endUtc, calendar.rangeStartUtc, calendar.rangeEndUtc)}%` }}
                    title={`${LABELS[category]}: ${segment.value}\n${localTime(segment.startUtc, calendar.timezone)} to ${localTime(segment.endUtc, calendar.timezone)}\n${segment.detail}`}
                    aria-label={`Select ${LABELS[category]} ${segment.value} from ${segment.startUtc} to ${segment.endUtc}`}
                    onClick={() => setSelected(segment)}
                  >{segment.value}</button>)}
                </div>
              </div>
            })}
          </div>
        </div>
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
