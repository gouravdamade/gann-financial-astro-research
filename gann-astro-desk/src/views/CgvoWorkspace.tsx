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
  rasi: 'Rasi partition: ROOT SOURCE CLOSED; absolute frame requires explicit selection',
  nakshatra: 'Nakshatra partition: ROOT SOURCE CLOSED; absolute frame requires explicit selection',
  lunarMonth: 'Lunar month base: PURNIMANTA - high-confidence source-internal inference; intercalation may remain UNKNOWN',
  ayana: 'Ayana: UNKNOWN - adapter not configured',
  firmament: 'Firmament: COMMENTARY CONFLICT - raw geometry available; classical section UNKNOWN',
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
  return <option value={event.causalEventId}>{dateLabel(event.astronomyEventIdentity.globalMaxUtcDisplay ?? event.astronomyEventIdentity.globalMaxUtc)} · {event.astronomyEventIdentity.globalType}</option>
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
        <div><span>Global maximum (UTC display)</span><strong>{dateLabel(identity.globalMaxUtcDisplay ?? identity.globalMaxUtc)}</strong></div>
        <div><span>Swiss UT identity</span><strong>{dateLabel(identity.globalMaxSwissUt ?? identity.globalMaxUtc)}</strong><small>Identity time scale: {event.eventIdentity.identityTimeScale ?? 'SWISSEPH_UT'} · display timezone is not used for hashing</small></div>
        <div><span>Local type</span><strong>{modern?.localEclipseType ?? 'Not calculated'}</strong></div>
        <div><span>Local visibility</span><strong>{modern?.visibility ?? 'Not calculated'}</strong></div>
        {identity.eventType === 'LUNAR' ? <>
          <div><span>Umbral magnitude</span><strong>{numberLabel(modern?.umbralMagnitude)}</strong><small>Swiss Ephemeris lunar umbral magnitude</small></div>
          <div><span>Penumbral magnitude</span><strong>{numberLabel(modern?.penumbralMagnitude)}</strong><small>Swiss Ephemeris lunar penumbral magnitude</small></div>
        </> : <>
          <div><span>Magnitude</span><strong>{numberLabel(modern?.magnitude)}</strong><small>Solar diameter coverage; not area obscuration</small></div>
          <div><span>Area obscuration</span><strong>{numberLabel(modern?.obscuration)}</strong><small>Fraction of solar disc covered</small></div>
        </>}
        <div><span>Sun altitude / azimuth</span><strong>{numberLabel(modern?.sunAltitudeAzimuth?.altitudeApparentDeg, ' deg')} / {numberLabel(modern?.sunAltitudeAzimuth?.azimuthDeg, ' deg')}</strong></div>
        <div><span>Moon altitude / azimuth</span><strong>{numberLabel(modern?.moonAltitudeAzimuth?.altitudeApparentDeg, ' deg')} / {numberLabel(modern?.moonAltitudeAzimuth?.azimuthDeg, ' deg')}</strong></div>
        <div><span>Azimuth convention</span><strong>0° North · clockwise</strong><small>Normalized from Swiss Ephemeris South-to-West; horizontal coordinates are topocentric.</small></div>
        <div><span>Visibility window</span><strong>{modern?.visibilityDetails?.visibleWindowStartUtc ? `${dateLabel(modern.visibilityDetails.visibleWindowStartUtc)} → ${dateLabel(modern.visibilityDetails.visibleWindowEndUtc)}` : 'No local visible window'}</strong><small>{modern?.visibilityDetails?.clipBoundaries.length ? `Rise/set clip: ${modern.visibilityDetails.clipBoundaries.join(', ')}` : 'Maximum and horizon status are reported separately.'}</small></div>
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

function SourceArchitecturePanel({ event }: { event: CgvoEvent }) {
  const adapters = (event.sourceAdapters ?? {}) as Record<string, Record<string, unknown>>
  const frame = adapters.varahamihiraFrame ?? {}
  const lunarMonth = adapters.varahamihiraLunarMonth ?? {}
  const aspect = adapters.varahamihiraAspect ?? {}
  const firmament = adapters.varahamihiraFirmament ?? {}
  const luminary = (frame.luminary ?? {}) as Record<string, unknown>
  const auditGeometry = (aspect.auditGeometryAtMaximum ?? {}) as Record<string, unknown>
  const records = (auditGeometry.records ?? []) as Array<Record<string, unknown>>
  const sourcePhase = (aspect.sourcePhaseActivation ?? {}) as Record<string, unknown>
  const intercalationGuard = (lunarMonth.intercalationGuard ?? {}) as Record<string, unknown>
  const rawGeometry = (firmament.rawGeometry ?? {}) as Record<string, unknown>
  return <>
    <section className="cgvo-panel" aria-label="Varahamihira astronomical frame">
      <div className="cgvo-panel-heading"><div><span>Varahamihira astronomical frame</span><strong>Rasi / nakshatra partition</strong><small>Root source partition; absolute frame stays an explicit candidate selection.</small></div><StatusChip>{String(frame.partitionStatus ?? 'UNKNOWN')}</StatusChip></div>
      <div className="cgvo-fact-grid">
        <div><span>Absolute frame</span><strong>{String(frame.absoluteFrameStatus ?? 'NULL')}</strong><small>{String(frame.selectedProfileId ?? 'No reconstruction selected')}</small></div>
        <div><span>Eclipsed luminary rasi</span><strong>{String(luminary.rasi ?? 'UNKNOWN')}</strong><small>{String(luminary.availability ?? 'UNKNOWN')}</small></div>
        <div><span>Nakshatra / pada</span><strong>{luminary.nakshatra ? `${String(luminary.nakshatra)} / ${String(luminary.pada)}` : 'UNKNOWN'}</strong><small>Candidate offset {numberLabel(luminary.candidateOffsetDeg as number | null | undefined, ' deg')}</small></div>
        <div><span>Precessional distinction</span><strong>{String(((frame.precessionalDistinction ?? {}) as Record<string, unknown>).sourceStatus ?? 'UNKNOWN')}</strong><small>No numeric precession constant is claimed.</small></div>
      </div>
      <div className="cgvo-source-note">Chitra/Spica at 180 degrees is a source reconstruction candidate, never a default ayanamsha and never an alias for Lahiri, Raman, or tropical coordinates.</div>
    </section>
    <section className="cgvo-panel" aria-label="Varahamihira lunar month">
      <div className="cgvo-panel-heading"><div><span>Lunar month</span><strong>Purnimanta source profile</strong><small>Only ordinary, unambiguous cases are labelled.</small></div><StatusChip>{String(lunarMonth.evidenceStatus ?? 'UNKNOWN')}</StatusChip></div>
      <div className="cgvo-fact-grid">
        <div><span>Base convention</span><strong>{String(lunarMonth.baseSystem ?? 'UNKNOWN')}</strong><small>High-confidence source-internal inference</small></div>
        <div><span>Result</span><strong>{String(lunarMonth.result ?? 'UNKNOWN_INTERCALATION_PROFILE_NOT_CLOSED')}</strong></div>
        <div><span>Intercalation guard</span><strong>{String(intercalationGuard.status ?? 'NOT_EVALUATED')}</strong><small>{String(intercalationGuard.reason ?? '')}</small></div>
        <div><span>Local source day</span><strong>{String(lunarMonth.sourceDayLocal ?? 'UNKNOWN')}</strong><small>{String(lunarMonth.timezone ?? lunarMonth.unknownReason ?? '')}</small></div>
        <div><span>Full-moon anchor</span><strong>{String(lunarMonth.monthAnchorNakshatra ?? 'UNKNOWN')}</strong><small>{dateLabel(lunarMonth.nextFullMoonUtc as string | null | undefined)}</small></div>
      </div>
    </section>
    <section className="cgvo-panel" aria-label="Varahamihira eclipse aspects">
      <div className="cgvo-panel-heading"><div><span>Eclipse aspects</span><strong>Maximum-time audit geometry</strong><small>Fractions are categorical geometry only; source-phase activation remains unclosed.</small></div><StatusChip>{String(auditGeometry.role ?? 'UNKNOWN')}</StatusChip></div>
      <div className="cgvo-aspect-list">
        {records.length ? records.map((record) => <article key={String(record.planet)}><strong>{String(record.planet)} → {String(record.eclipsedLuminary)}</strong><span>{String(record.aspectingRasi)} to {String(record.eclipsedRasi)} · sign {String(record.signDistance)} · fraction {String(record.fraction)} · {record.aspectExists ? 'ASPECT EXISTS' : 'NO ASPECT'}</span><small>Source claim: {String(record.sourceEffectToken ?? 'None for this maximum-time geometry')}</small></article>) : <div className="cgvo-source-note">ABSOLUTE_FRAME_NOT_SELECTED. Aspect records remain unavailable until an explicit source reconstruction candidate is selected.</div>}
      </div>
      <div className="cgvo-source-note">Source phase activation: {String(sourcePhase.status ?? 'UNKNOWN_SOURCE_PHASE_MAPPING_NOT_CLOSED')}. Effect activation: {String(sourcePhase.effectActivated ?? 'null')}. Jupiter mitigation activation: {String(sourcePhase.jupiterMitigationActivated ?? 'null')}. Effect magnitude multiplier: null. Jupiter mitigation coefficient: null.</div>
    </section>
    <section className="cgvo-panel" aria-label="Varahamihira firmament geometry">
      <div className="cgvo-panel-heading"><div><span>Firmament geometry</span><strong>Raw modern geometry with unresolved classical section</strong><small>Commentary candidates remain non-voting comparisons.</small></div><StatusChip>{String(firmament.status ?? 'UNKNOWN')}</StatusChip></div>
      <div className="cgvo-fact-grid">
        <div><span>Apparent altitude</span><strong>{numberLabel(rawGeometry.apparentAltitudeDeg as number | null | undefined, ' deg')}</strong></div>
        <div><span>Normalized / raw azimuth</span><strong>{numberLabel(rawGeometry.normalizedAzimuthDeg as number | null | undefined, ' deg')} / {numberLabel(rawGeometry.rawSwissAzimuthDeg as number | null | undefined, ' deg')}</strong></div>
        <div><span>Local hour angle</span><strong>{numberLabel(rawGeometry.localHourAngleDeg as number | null | undefined, ' deg')}</strong><small>{String(rawGeometry.meridianRelation ?? 'UNKNOWN')}</small></div>
        <div><span>Classical section</span><strong>{String(firmament.classicalSection ?? 'UNKNOWN')}</strong><small>source-certified classifier: {String(firmament.sourceCertifiedClassifier ?? false)}</small></div>
      </div>
    </section>
  </>
}

function GeographyCards({ workbench }: { workbench: CgvoWorkbench }) {
  const kurma = workbench.kurma
  return <section className="cgvo-panel" aria-label="Geography claims">
    <div className="cgvo-panel-heading"><div><span>Geography claims</span><strong>Parallel source dimensions</strong></div><StatusChip>NO AGGREGATION</StatusChip></div>
    <div className="cgvo-geography-grid">
      <article><span>Rasi region</span><strong>UNKNOWN</strong><small>Partition is source-closed; modern historical-region mapping is not authorized. The absolute frame remains an explicit candidate.</small></article>
      <article><span>Kurma nakshatra region</span><strong>RAW GROUPS ONLY</strong><small>Modern geography mapping is not built.</small></article>
      <article><span>Lunar month region</span><strong>UNKNOWN</strong><small>Base convention is purnimanta; intercalation and month-to-region application remain unresolved.</small></article>
    </div>
    <div className="cgvo-kurma-grid">{kurma.groups.map((group) => <div key={group.direction}><span>{group.direction}</span><strong>{group.nakshatras.join(' / ')}</strong><small>{group.sourceVerses ?? 'Chapter XIV'} · {group.mappingStatus}</small>{group.historicalNames?.length ? <details><summary>{group.historicalNames.length} raw Chapter XIV names</summary><small>{group.historicalNames.join(' · ')}</small></details> : null}</div>)}</div>
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
      <div><span>Time policy</span><code>{event.astronomyEventIdentity.timeScale} identity · {event.astronomyEventIdentity.displayTimeScale ?? 'UTC'} display only</code></div>
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
  const [absoluteFrameProfileId, setAbsoluteFrameProfileId] = useState('')
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
        setWorkbench(await fetchCgvoWorkbench({ eventType: nextType, globalMaxSwissUt: nextEvent.astronomyEventIdentity.globalMaxSwissUt ?? nextEvent.astronomyEventIdentity.globalMaxUtc, causalEventId: nextEvent.causalEventId, ...locality, absoluteFrameProfileId: absoluteFrameProfileId || undefined }))
      } else setWorkbench(null)
    } catch (caught) { setError(caught instanceof Error ? caught.message : String(caught)) } finally { setBusy(false) }
  }, [absoluteFrameProfileId, endUtc, eventType, locality, startUtc])

  const loadLocality = useCallback(async (nextEvent: CgvoEvent | null, nextLocality = locality, nextFrameProfileId = absoluteFrameProfileId) => {
    if (!nextEvent) return
    setBusy(true); setError('')
    try {
      setWorkbench(await fetchCgvoWorkbench({ eventType, globalMaxSwissUt: nextEvent.astronomyEventIdentity.globalMaxSwissUt ?? nextEvent.astronomyEventIdentity.globalMaxUtc, causalEventId: nextEvent.causalEventId, ...nextLocality, absoluteFrameProfileId: nextFrameProfileId || undefined }))
    } catch (caught) { setError(caught instanceof Error ? caught.message : String(caught)) } finally { setBusy(false) }
  }, [absoluteFrameProfileId, eventType, locality])

  useEffect(() => { void fetchCgvoStatus().then(setStatus).catch((caught) => setError(caught instanceof Error ? caught.message : String(caught))); void loadSearch() }, [loadSearch])
  const selectedEventId = event?.causalEventId ?? ''
  const sourceProfiles = workbench?.sourceProfiles ?? []
  const varahamihira = sourceProfiles.find((profile) => profile.profileId === 'VARAHAMIHIRA_BS_ECLIPSE_V1')
  const trailokya = sourceProfiles.find((profile) => profile.profileId === 'TRAILOKYA_1972_GEOGRAPHY_ARGHA_V1')

  return <section className="cgvo-workspace" aria-label="Classical Geography and Visibility Observatory">
    <div className="cgvo-safety-banner"><Globe2 size={16} /><strong>CGVO-S1A-R1 · READ-ONLY RESEARCH INSPECTOR</strong><span>Modern eclipse facts, source-separated Varahamihira adapters, and explicit unknowns. No market-linked, automated, or execution behavior.</span><LockKeyhole size={14} /></div>
    <header className="cgvo-header"><div><div className="experimental-kicker"><MapPinned size={14} /> Classical geography and visibility</div><h1>Classical Geography &amp; Visibility</h1><p>One physical eclipse remains one causal event. Locality changes local circumstances, not global identity.</p></div><div className="cgvo-controls"><label>Event type<select aria-label="CGVO event type" value={eventType} onChange={(e) => { const next = e.target.value as EventType; setEventType(next); void loadSearch(next) }} disabled={busy}><option value="SOLAR">Solar eclipse</option><option value="LUNAR">Lunar eclipse</option></select></label><label>Locality<select aria-label="CGVO locality" value={locality.localityId} onChange={(e) => { const next = LOCALITIES.find((item) => item.localityId === e.target.value) ?? LOCALITIES[0]; setLocality(next); void loadLocality(event, next) }} disabled={busy}>{LOCALITIES.map((item) => <option key={item.localityId} value={item.localityId}>{item.label}</option>)}</select></label><label>Varahamihira absolute frame<select aria-label="Varahamihira absolute frame" value={absoluteFrameProfileId} onChange={(e) => { const next = e.target.value; setAbsoluteFrameProfileId(next); void loadLocality(event, locality, next) }} disabled={busy}><option value="">No absolute frame selected</option><option value="VARAHAMIHIRA_CHITRA_180_RECONSTRUCTION_V1">Chitra / Spica 180 reconstruction (candidate)</option></select></label><button type="button" className="secondary-command" onClick={() => void loadSearch()} disabled={busy}><RefreshCw size={14} className={busy ? 'xe1-spin' : ''} /> Refresh</button></div></header>
    <section className="cgvo-event-selector" aria-label="CGVO event selector"><label>Search start UTC<input value={startUtc} onChange={(e) => setStartUtc(e.target.value)} /></label><label>Search end UTC<input value={endUtc} onChange={(e) => setEndUtc(e.target.value)} /></label><button type="button" className="secondary-command" onClick={() => void loadSearch()} disabled={busy}>Search events</button><label className="cgvo-event-select">Selected event<select aria-label="CGVO event" value={selectedEventId} onChange={(e) => { const next = search?.events.find((item) => item.causalEventId === e.target.value) ?? null; setEvent(next); void loadLocality(next) }} disabled={busy || !search?.events.length}>{search?.events.map((item) => <EventOption key={item.causalEventId} event={item} />)}</select></label></section>
    {error && <div className="cgvo-error"><CircleAlert size={16} /><strong>CGVO unavailable</strong><span>{error}</span></div>}
    {!workbench?.event && !error && <div className="cgvo-empty">{busy ? 'Calculating deterministic eclipse facts...' : 'No eclipse exists in the selected UTC range.'}</div>}
    {workbench?.event && <><section className="cgvo-context-strip" aria-label="Selected CGVO event"><span><strong>{workbench.event.astronomyEventIdentity.eventType}</strong> · {workbench.event.astronomyEventIdentity.globalType}</span><span>Global max {dateLabel(workbench.event.astronomyEventIdentity.globalMaxUtcDisplay ?? workbench.event.astronomyEventIdentity.globalMaxUtc)}</span><span>{workbench.event.causalEventId}</span><StatusChip>EXECUTION LOCKED</StatusChip></section><ModernFacts event={workbench.event} /><SourceArchitecturePanel event={workbench.event} /><div className="cgvo-source-grid">{varahamihira && <VarahamihiraCard profile={varahamihira} />}{trailokya && <TrailokyaCard profile={trailokya} />}</div><GeographyCards workbench={workbench} /><AuditPanel event={workbench.event} status={status} /></>}
    <footer className="cgvo-footer"><span>MODERN ASTRONOMY: factual only</span><span>VARAHAMIHIRA: source-separated</span><span>TRAILOKYA: source silent for eclipse visibility</span><span>executionAllowed = false</span></footer>
  </section>
}
