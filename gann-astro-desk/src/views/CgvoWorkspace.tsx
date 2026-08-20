import { useCallback, useEffect, useState } from 'react'
import { CircleAlert, Globe2, LockKeyhole, MapPinned, RefreshCw, ShieldCheck } from 'lucide-react'
import { fetchCgvoEventSearch, fetchCgvoStatus, fetchCgvoWorkbench } from '../api'
import type { CgvoEvent, CgvoSearch, CgvoStatus, CgvoWorkbench } from '../cgvoTypes'

type EventType = 'SOLAR' | 'LUNAR'
type Locality = { localityId: string; label: string; latitude: number; longitude: number; elevationM: number; timezone: string }

const LOCALITIES: Locality[] = [
  { localityId: 'UJJAIN', label: 'Ujjain, India', latitude: 23.1765, longitude: 75.7885, elevationM: 0, timezone: 'Asia/Kolkata' },
  { localityId: 'NEW_YORK', label: 'New York, USA', latitude: 40.7128, longitude: -74.006, elevationM: 10, timezone: 'America/New_York' },
  { localityId: 'LONDON', label: 'London, UK', latitude: 51.5072, longitude: -0.1276, elevationM: 10, timezone: 'Europe/London' },
]

const UNKNOWN_LABELS: Record<string, string> = {
  rasi: 'Rasi: UNKNOWN - source zodiac frame not authorized',
  nakshatra: 'Nakshatra: UNKNOWN - source frame/ayanamsha adapter not authorized',
  lunarMonth: 'Lunar month: UNKNOWN - convention not closed',
  ayana: 'Ayana: UNKNOWN - adapter not configured',
  firmament: 'Firmament interpretation: SOURCE_INTERPRETATION_UNRESOLVED',
  commencementQuarter: 'Commencement quarter: MAPPING_UNRESOLVED',
  liberationClass: 'Liberation class: MAPPING_UNRESOLVED',
  morphology: 'Morphology: MAPPING_UNRESOLVED',
  colour: 'Colour: OBSERVATION_REQUIRED',
  sevenDayOmens: 'Seven-day omens: UNKNOWN - historical evidence not loaded',
}

function dateLabel(value: string | null | undefined): string {
  if (!value) return 'Unknown'
  return new Date(value).toLocaleString([], { dateStyle: 'medium', timeStyle: 'short', timeZone: 'UTC' }) + ' UTC'
}

function numberLabel(value: number | null | undefined, suffix = ''): string {
  return value == null || !Number.isFinite(value) ? 'Unknown' : `${value.toFixed(4)}${suffix}`
}

function EventOption({ event }: { event: CgvoEvent }) {
  return <option value={event.causalEventId}>{dateLabel(event.astronomyEventIdentity.globalMaxUtc)} · {event.astronomyEventIdentity.globalType}</option>
}

function StatusChip({ children, className = '' }: { children: React.ReactNode; className?: string }) {
  return <span className={`cgvo-status-chip ${className}`}>{children}</span>
}

function ModernFacts({ event }: { event: CgvoEvent }) {
  const modern = event.modernAstronomy
  const identity = event.astronomyEventIdentity
  return <>
    <section className="cgvo-panel" aria-label="Modern astronomy facts">
      <div className="cgvo-panel-heading"><div><span>Modern astronomy</span><strong>Topocentric local circumstances</strong></div><StatusChip>FACTUAL ENGINE OUTPUT</StatusChip></div>
      <div className="cgvo-fact-grid">
        <div><span>Global identity</span><strong>{identity.eventType} · {identity.globalType}</strong></div>
        <div><span>Global maximum</span><strong>{dateLabel(identity.globalMaxUtc)}</strong></div>
        <div><span>Local type</span><strong>{modern?.localEclipseType ?? 'Not calculated'}</strong></div>
        <div><span>Local visibility</span><strong>{modern?.visibility ?? 'Not calculated'}</strong></div>
        <div><span>Magnitude</span><strong>{numberLabel(modern?.magnitude)}</strong><small>Solar diameter coverage; not area obscuration</small></div>
        <div><span>Area obscuration</span><strong>{numberLabel(modern?.obscuration)}</strong><small>Fraction of solar disc covered</small></div>
        <div><span>Sun altitude / azimuth</span><strong>{numberLabel(modern?.sunAltitudeAzimuth?.altitudeApparentDeg, ' deg')} / {numberLabel(modern?.sunAltitudeAzimuth?.azimuthDeg, ' deg')}</strong></div>
        <div><span>Moon altitude / azimuth</span><strong>{numberLabel(modern?.moonAltitudeAzimuth?.altitudeApparentDeg, ' deg')} / {numberLabel(modern?.moonAltitudeAzimuth?.azimuthDeg, ' deg')}</strong></div>
      </div>
      <div className="cgvo-location-line"><MapPinned size={13} /> {event.locality ? `${event.locality.label} · ${event.locality.latitude}, ${event.locality.longitude} · ${event.locality.timezone}` : 'Select a locality to calculate local circumstances.'}</div>
    </section>
    <section className="cgvo-panel" aria-label="Eclipse phase timeline">
      <div className="cgvo-panel-heading"><div><span>Phase timeline</span><strong>{identity.eventType === 'SOLAR' ? 'C1 / C2 / MAX / C3 / C4' : 'P1 / U1 / U2 / MAX / U3 / U4 / P4'}</strong></div><small>Null means the phase is not present or not locally visible.</small></div>
      <div className="cgvo-phase-timeline">{Object.entries(modern?.contacts ?? identity.globalContacts).map(([key, value]) => <div key={key}><span>{key}</span><strong>{dateLabel(value)}</strong></div>)}</div>
    </section>
  </>
}

function VarahamihiraCard({ profile }: { profile: Record<string, unknown> }) {
  const statuses = (profile.displayStatuses ?? {}) as Record<string, string>
  const claims = (profile.claims ?? []) as Array<Record<string, unknown>>
  return <section className="cgvo-panel" aria-label="Varahamihira source inspector">
    <div className="cgvo-panel-heading"><div><span>Varahamihira source inspector</span><strong>Brihat Samhita typed claims</strong></div><StatusChip>SOURCE-SEPARATED</StatusChip></div>
    <p className="cgvo-source-note">{String(profile.edition)}. {String(profile.sourceStatus)}. Modern eligibility and classical interpretation are displayed as separate fields.</p>
    <div className="cgvo-source-statuses">{Object.entries(statuses).map(([key, value]) => <div key={key}><span>{key.replaceAll(/([A-Z])/g, ' $1')}</span><strong>{value}</strong></div>)}</div>
    <div className="cgvo-claims">{claims.map((claim) => <article key={String(claim.id)}><strong>{String(claim.topic)}</strong><span>{String(claim.locator)} · {String(claim.status)}</span></article>)}</div>
  </section>
}

function GeographyCards({ workbench }: { workbench: CgvoWorkbench }) {
  const kurma = workbench.kurma
  return <section className="cgvo-panel" aria-label="Geography claims">
    <div className="cgvo-panel-heading"><div><span>Geography claims</span><strong>Parallel source dimensions</strong></div><StatusChip>NO AGGREGATION</StatusChip></div>
    <div className="cgvo-geography-grid">
      <article><span>Rasi region</span><strong>UNKNOWN</strong><small>Source zodiac frame and modern region mapping are not authorized.</small></article>
      <article><span>Kurma nakshatra region</span><strong>RAW GROUPS ONLY</strong><small>Modern geography mapping is not built.</small></article>
      <article><span>Lunar month region</span><strong>UNKNOWN</strong><small>Lunar-month convention remains open.</small></article>
    </div>
    <div className="cgvo-kurma-grid">{kurma.groups.map((group) => <div key={group.direction}><span>{group.direction}</span><strong>{group.nakshatras.join(' / ')}</strong><small>{group.mappingStatus}</small></div>)}</div>
  </section>
}

function TrailokyaCard({ profile }: { profile: Record<string, unknown> }) {
  return <section className="cgvo-panel cgvo-trailokya" aria-label="Trailokya geography and argha context">
    <div className="cgvo-panel-heading"><div><span>Trailokya 1972</span><strong>Geography / Argha context</strong></div><StatusChip>PROFILE ISOLATED</StatusChip></div>
    <div className="cgvo-banner-list">{((profile.banner ?? []) as string[]).map((item) => <span key={item}>{item}</span>)}</div>
    <p className="cgvo-source-note">The held witness is source-silent for an eclipse-visibility doctrine. No Varahamihira claim is inherited and no Trailokya claim is applied to the modern eclipse facts.</p>
  </section>
}

function AuditPanel({ event, status }: { event: CgvoEvent; status: CgvoStatus | null }) {
  return <section className="cgvo-panel" aria-label="CGVO provenance and guardrails">
    <div className="cgvo-panel-heading"><div><span>Audit and guardrails</span><strong>Unknowns remain inspectable</strong></div><ShieldCheck size={15} /></div>
    <div className="cgvo-audit-grid">
      <div><span>Causal event</span><code>{event.causalEventId}</code></div>
      <div><span>Astronomy contract</span><code>{event.astronomyEventIdentity.astronomyContract}</code></div>
      <div><span>Ephemeris</span><code>{event.astronomyEventIdentity.ephemeris} {event.astronomyEventIdentity.ephemerisVersion}</code></div>
      <div><span>Time policy</span><code>{event.astronomyEventIdentity.timeScale} · timezone display only</code></div>
      <div><span>Milestone</span><code>{status?.milestone ?? 'PFR-V2B-CGVO-P1'}</code></div>
      <div><span>Execution</span><code>false · read-only research</code></div>
    </div>
    <div className="cgvo-unknown-list">{Object.entries(UNKNOWN_LABELS).map(([key, value]) => <span key={key}>{value}</span>)}{event.sourceUnknowns.map((reason) => <span key={reason}>{reason}</span>)}</div>
  </section>
}

export function CgvoWorkspace() {
  const [status, setStatus] = useState<CgvoStatus | null>(null)
  const [eventType, setEventType] = useState<EventType>('SOLAR')
  const [search, setSearch] = useState<CgvoSearch | null>(null)
  const [event, setEvent] = useState<CgvoEvent | null>(null)
  const [workbench, setWorkbench] = useState<CgvoWorkbench | null>(null)
  const [locality, setLocality] = useState(LOCALITIES[0])
  const [startUtc, setStartUtc] = useState('2027-01-01T00:00:00Z')
  const [endUtc, setEndUtc] = useState('2028-01-01T00:00:00Z')
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')

  const loadSearch = useCallback(async (nextType = eventType) => {
    setBusy(true); setError('')
    try {
      const nextSearch = await fetchCgvoEventSearch({ eventType: nextType, startUtc, endUtc, limit: 24 })
      setSearch(nextSearch)
      const nextEvent = nextSearch.events[0] ?? null
      setEvent(nextEvent)
      if (nextEvent) {
        setWorkbench(await fetchCgvoWorkbench({ eventType: nextType, globalMaxUtc: nextEvent.astronomyEventIdentity.globalMaxUtc, ...locality }))
      } else setWorkbench(null)
    } catch (caught) { setError(caught instanceof Error ? caught.message : String(caught)) } finally { setBusy(false) }
  }, [endUtc, eventType, locality, startUtc])

  const loadLocality = useCallback(async (nextEvent: CgvoEvent | null, nextLocality = locality) => {
    if (!nextEvent) return
    setBusy(true); setError('')
    try {
      setWorkbench(await fetchCgvoWorkbench({ eventType, globalMaxUtc: nextEvent.astronomyEventIdentity.globalMaxUtc, ...nextLocality }))
    } catch (caught) { setError(caught instanceof Error ? caught.message : String(caught)) } finally { setBusy(false) }
  }, [eventType, locality])

  useEffect(() => { void fetchCgvoStatus().then(setStatus).catch((caught) => setError(caught instanceof Error ? caught.message : String(caught))); void loadSearch() }, [loadSearch])
  const selectedEventId = event?.causalEventId ?? ''
  const sourceProfiles = workbench?.sourceProfiles ?? []
  const varahamihira = sourceProfiles.find((profile) => profile.profileId === 'VARAHAMIHIRA_BS_ECLIPSE_V1')
  const trailokya = sourceProfiles.find((profile) => profile.profileId === 'TRAILOKYA_1972_GEOGRAPHY_ARGHA_V1')

  return <section className="cgvo-workspace" aria-label="Classical Geography and Visibility Observatory">
    <div className="cgvo-safety-banner"><Globe2 size={16} /><strong>CGVO-P1 · READ-ONLY RESEARCH INSPECTOR</strong><span>Modern eclipse facts, source-separated classical ledgers, explicit unknowns. No forecast, score, market direction, Fields, SBC, Auto Suggest, ML, MT5, or execution.</span><LockKeyhole size={14} /></div>
    <header className="cgvo-header"><div><div className="experimental-kicker"><MapPinned size={14} /> Classical geography and visibility</div><h1>Classical Geography &amp; Visibility</h1><p>One physical eclipse remains one causal event. Locality changes local circumstances, not global identity.</p></div><div className="cgvo-controls"><label>Event type<select aria-label="CGVO event type" value={eventType} onChange={(e) => { const next = e.target.value as EventType; setEventType(next); void loadSearch(next) }} disabled={busy}><option value="SOLAR">Solar eclipse</option><option value="LUNAR">Lunar eclipse</option></select></label><label>Locality<select aria-label="CGVO locality" value={locality.localityId} onChange={(e) => { const next = LOCALITIES.find((item) => item.localityId === e.target.value) ?? LOCALITIES[0]; setLocality(next); void loadLocality(event, next) }} disabled={busy}>{LOCALITIES.map((item) => <option key={item.localityId} value={item.localityId}>{item.label}</option>)}</select></label><button type="button" className="secondary-command" onClick={() => void loadSearch()} disabled={busy}><RefreshCw size={14} className={busy ? 'xe1-spin' : ''} /> Refresh</button></div></header>
    <section className="cgvo-event-selector" aria-label="CGVO event selector"><label>Search start UTC<input value={startUtc} onChange={(e) => setStartUtc(e.target.value)} /></label><label>Search end UTC<input value={endUtc} onChange={(e) => setEndUtc(e.target.value)} /></label><button type="button" className="secondary-command" onClick={() => void loadSearch()} disabled={busy}>Search events</button><label className="cgvo-event-select">Selected event<select aria-label="CGVO event" value={selectedEventId} onChange={(e) => { const next = search?.events.find((item) => item.causalEventId === e.target.value) ?? null; setEvent(next); void loadLocality(next) }} disabled={busy || !search?.events.length}>{search?.events.map((item) => <EventOption key={item.causalEventId} event={item} />)}</select></label></section>
    {error && <div className="cgvo-error"><CircleAlert size={16} /><strong>CGVO unavailable</strong><span>{error}</span></div>}
    {!workbench?.event && !error && <div className="cgvo-empty">{busy ? 'Calculating deterministic eclipse facts...' : 'No eclipse exists in the selected UTC range.'}</div>}
    {workbench?.event && <><section className="cgvo-context-strip" aria-label="Selected CGVO event"><span><strong>{workbench.event.astronomyEventIdentity.eventType}</strong> · {workbench.event.astronomyEventIdentity.globalType}</span><span>Global max {dateLabel(workbench.event.astronomyEventIdentity.globalMaxUtc)}</span><span>{workbench.event.causalEventId}</span><StatusChip>EXECUTION LOCKED</StatusChip></section><ModernFacts event={workbench.event} /><div className="cgvo-source-grid">{varahamihira && <VarahamihiraCard profile={varahamihira} />}{trailokya && <TrailokyaCard profile={trailokya} />}</div><GeographyCards workbench={workbench} /><AuditPanel event={workbench.event} status={status} /></>}
    <footer className="cgvo-footer"><span>MODERN ASTRONOMY: factual only</span><span>VARAHAMIHIRA: source-separated</span><span>TRAILOKYA: source silent for eclipse visibility</span><span>executionAllowed = false</span></footer>
  </section>
}
