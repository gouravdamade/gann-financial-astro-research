// @vitest-environment jsdom

import '@testing-library/jest-dom/vitest'
import { cleanup, render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { afterEach, describe, expect, it, vi } from 'vitest'
import { CgvoWorkspace } from './views/CgvoWorkspace'
import type { CgvoEvent, CgvoStatus, CgvoWorkbench } from './cgvoTypes'

const api = vi.hoisted(() => ({
  fetchCgvoEventSearch: vi.fn(),
  fetchCgvoStatus: vi.fn(),
  fetchCgvoWorkbench: vi.fn(),
}))

vi.mock('./api', () => api)

const guardrails = {
  readOnly: true, experimental: true, priceDataRead: false, priceOutcomeRead: false,
  fieldsPath: false, sbcPath: false, autoSuggestPath: false, mlPath: false, mt5Path: false,
  executionAllowed: false, automaticOrderPlacement: false, marketDirectionInferred: false,
  scoreAggregationUsed: false, crossSourceComposition: false,
} as const

const event: CgvoEvent = {
  causalEventId: 'CGVO-SOLAR-DEMO',
  eventIdentity: { eventType: 'SOLAR', globalMaxUtc: '2027-08-02T10:06:41Z', globalMaxSwissUt: '2027-08-02T10:06:41Z', globalMaxUtcDisplay: '2027-08-02T10:06:41Z', globalType: 'TOTAL', identityTimeScale: 'SWISSEPH_UT', displayTimeScale: 'UTC', displayTimezone: 'UTC' },
  astronomyEventIdentity: {
    eventType: 'SOLAR', globalType: 'TOTAL', globalMaxUtc: '2027-08-02T10:06:41Z',
    globalMaxSwissUt: '2027-08-02T10:06:41Z', globalMaxUtcDisplay: '2027-08-02T10:06:41Z',
    globalContacts: { C1: '2027-08-02T07:30:17Z', C2: '2027-08-02T08:23:29Z', MAX: '2027-08-02T10:06:41Z', C3: '2027-08-02T11:49:56Z', C4: '2027-08-02T12:43:08Z' },
    astronomyContract: 'MODERN_ASTRONOMY_VISIBILITY_V1', ephemeris: 'Swiss Ephemeris', ephemerisVersion: '2.10.03', timeScale: 'SWISSEPH_UT', displayTimeScale: 'UTC', displayTimezone: 'UTC', deltaTModel: 'SWISS_EPHEMERIS_INTERNAL',
  },
  locality: { localityId: 'UJJAIN', label: 'Ujjain, India', latitude: 23.1765, longitude: 75.7885, elevationM: 0, timezone: 'Asia/Kolkata' },
  modernAstronomy: {
    globalType: 'TOTAL', localEclipseType: 'PARTIAL', visibility: 'VISIBLE', localMaxUtc: '2027-08-02T11:07:16Z', contacts: { C1: '2027-08-02T10:21:13Z', C2: null, MAX: '2027-08-02T11:07:16Z', C3: null, C4: '2027-08-02T11:49:57Z' },
    magnitude: 0.29, obscuration: 0.18, visibilityDetails: { status: 'VISIBLE', maximumVisibility: 'VISIBLE', visibleWindowStartUtc: '2027-08-02T10:21:13Z', visibleWindowEndUtc: '2027-08-02T11:49:57Z', clipBoundaries: [], horizonEvents: { riseUtc: null, setUtc: null }, swissVisibilityFlags: 5008 }, sunAltitudeAzimuth: { altitudeApparentDeg: 33, azimuthDeg: 96, sourceAzimuthDeg: 276, azimuthConvention: 'NORTH_CLOCKWISE_0N_90E_180S_270W', sourceAzimuthConvention: 'SWISSEPH_SOUTH_CLOCKWISE_TO_WEST', topocentric: true }, moonAltitudeAzimuth: { altitudeApparentDeg: 33, azimuthDeg: 96, sourceAzimuthDeg: 276, azimuthConvention: 'NORTH_CLOCKWISE_0N_90E_180S_270W', sourceAzimuthConvention: 'SWISSEPH_SOUTH_CLOCKWISE_TO_WEST', topocentric: true },
  },
  observationalContext: {}, varahamihiraClaims: [], trailokyaClaims: [], historicalRegionCandidates: [], sourceUnknowns: [], provenance: [], guardrails,
  sourceAdapters: {
    varahamihiraFrame: { partitionStatus: 'CLOSED_ROOT_SOURCE', absoluteFrameStatus: 'NULL', selectedProfileId: null, luminary: { availability: 'ABSOLUTE_FRAME_NOT_SELECTED', rasi: null, nakshatra: null, pada: null } },
    varahamihiraLunarMonth: { baseSystem: 'PURNIMANTA', evidenceStatus: 'HIGH_CONFIDENCE_SOURCE_INTERNAL_INFERENCE', result: 'UNKNOWN_INTERCALATION_PROFILE_NOT_CLOSED', intercalationGuard: { status: 'AMBIGUOUS_OR_INTERCALARY', reason: 'ADHIKA_OR_KSHAYA_GUARD_TRIGGERED', synodicIntervals: [] } },
    varahamihiraAspect: { geometryStatus: 'CLOSED_SAME_AUTHOR_DELEGATED_SOURCE', auditGeometryAtMaximum: { timeSwissUt: '2027-08-02T10:06:41Z', role: 'GEOMETRY_SNAPSHOT_ONLY', records: [] }, sourcePhaseActivation: { status: 'UNKNOWN_SOURCE_PHASE_MAPPING_NOT_CLOSED', effectActivated: null, jupiterMitigationActivated: null }, effectMagnitudeMultiplier: null, jupiterMitigationCoefficient: null },
    varahamihiraFirmament: { status: 'COMMENTARY_CONFLICT_NOT_SOURCE_CLOSED', classicalSection: 'UNKNOWN', sourceCertifiedClassifier: false, rawGeometry: {} },
  },
}

const status: CgvoStatus = { contract: 'CLASSICAL_GEOGRAPHY_VISIBILITY_OBSERVATORY_V1', schemaVersion: 1, milestone: 'PFR-V2B-CGVO-P1', status: 'READY', availableProfiles: ['MODERN_ASTRONOMY_VISIBILITY_V1'], availableEventTypes: ['SOLAR', 'LUNAR'], guardrails, sourceProfiles: { varahamihira: 'WORKING_WITNESS_METADATA_PENDING', trailokya: 'SOURCE_SILENT_FOR_ECLIPSE_VISIBILITY_IN_HELD_WITNESS' } }
const workbench: CgvoWorkbench = {
  contract: 'CLASSICAL_GEOGRAPHY_VISIBILITY_OBSERVATORY_V1', schemaVersion: 1, event, guardrails,
  sourceProfiles: [
    { profileId: 'VARAHAMIHIRA_BS_ECLIPSE_V1', contract: 'SOURCE', sourceId: 'BS', edition: '1946 working witness', authority: 'SOURCE', sourceStatus: 'WORKING_WITNESS_METADATA_PENDING', displayStatuses: { rasi: 'UNKNOWN_ZODIAC_FRAME_NOT_AUTHORIZED', colour: 'OBSERVATION_REQUIRED' }, claims: [], guardrails: {} },
    { profileId: 'TRAILOKYA_1972_GEOGRAPHY_ARGHA_V1', contract: 'SOURCE', sourceId: 'TRAILOKYA', edition: '1972', authority: 'SOURCE', sourceStatus: 'SOURCE_SILENT_FOR_ECLIPSE_VISIBILITY_IN_HELD_WITNESS', banner: ['ECLIPSE VISIBILITY DOCTRINE: SOURCE SILENT IN HELD WITNESS'], guardrails: {} },
  ],
  kurma: { contract: 'KURMA', status: 'RAW_CHAPTER_XIV_NAMES_MODERN_MAPPING_NOT_BUILT', historicalSource: { chapter: 'XIV / Kūrma Vibhāga', modernGeographicInference: false }, groups: [{ direction: 'CENTER', nakshatras: ['Krittika'], sourceVerses: '14.2-14.4', historicalNames: ['Bhadrā', 'Arimeda'], mappingStatus: 'UNKNOWN' }], guardrails: {} },
}

const lunarEvent: CgvoEvent = {
  ...event,
  causalEventId: 'CGVO-LUNAR-DEMO',
  eventIdentity: { ...event.eventIdentity, eventType: 'LUNAR', globalType: 'TOTAL' },
  astronomyEventIdentity: { ...event.astronomyEventIdentity, eventType: 'LUNAR', globalType: 'TOTAL' },
  modernAstronomy: {
    ...event.modernAstronomy!,
    globalType: 'TOTAL',
    localEclipseType: 'TOTAL',
    visibility: 'RISE_SET_CLIPPED',
    umbralMagnitude: 1.2,
    penumbralMagnitude: 2.3,
    magnitudeReference: 'SWISSEPH_LUNAR_ECLIPSE_HOW_AT_EVENT_MAX_SWISSEPH_UT',
    visibilityDetails: { status: 'RISE_SET_CLIPPED', maximumVisibility: 'NOT_VISIBLE_AT_MAXIMUM', visibleWindowStartUtc: '2027-08-02T10:21:13Z', visibleWindowEndUtc: '2027-08-02T11:49:57Z', clipBoundaries: ['MOONRISE'], horizonEvents: { riseUtc: '2027-08-02T10:21:13Z', setUtc: null }, swissVisibilityFlags: 16576 },
  },
}

afterEach(() => { cleanup(); vi.clearAllMocks() })

describe('CgvoWorkspace', () => {
  it('shows modern local facts, source gaps, and isolated Trailokya context', async () => {
    api.fetchCgvoStatus.mockResolvedValue(status)
    api.fetchCgvoEventSearch.mockResolvedValue({ contract: 'SEARCH', range: { startUtc: '', endUtc: '' }, eventType: 'SOLAR', events: [event], count: 1, selection: 'chronological', guardrails })
    api.fetchCgvoWorkbench.mockResolvedValue(workbench)
    render(<CgvoWorkspace />)
    expect(await screen.findByText('Classical Geography & Visibility')).toBeInTheDocument()
    expect(await screen.findByText('PARTIAL', { selector: 'strong' })).toBeInTheDocument()
    expect(screen.getByText(/ECLIPSE VISIBILITY DOCTRINE: SOURCE SILENT/)).toBeInTheDocument()
    expect(screen.getByText(/Rasi partition: ROOT SOURCE CLOSED/)).toBeInTheDocument()
    expect(screen.getByLabelText('Varahamihira absolute frame')).toBeInTheDocument()
    expect(screen.getByText('Purnimanta source profile')).toBeInTheDocument()
    expect(screen.getByText('AMBIGUOUS_OR_INTERCALARY')).toBeInTheDocument()
    expect(screen.getByText('GEOMETRY_SNAPSHOT_ONLY')).toBeInTheDocument()
    expect(screen.getByText(/UNKNOWN_SOURCE_PHASE_MAPPING_NOT_CLOSED/)).toBeInTheDocument()
    expect(screen.getByText(/Effect magnitude multiplier: null/)).toBeInTheDocument()
    expect(screen.getByText('COMMENTARY_CONFLICT_NOT_SOURCE_CLOSED')).toBeInTheDocument()
    expect(screen.queryByText(/BULLISH|BEARISH/)).not.toBeInTheDocument()
  })

  it('passes an explicitly selected source reconstruction candidate without selecting a default', async () => {
    api.fetchCgvoStatus.mockResolvedValue(status)
    api.fetchCgvoEventSearch.mockResolvedValue({ contract: 'SEARCH', range: { startUtc: '', endUtc: '' }, eventType: 'SOLAR', events: [event], count: 1, selection: 'chronological', guardrails })
    api.fetchCgvoWorkbench.mockResolvedValue(workbench)
    const user = userEvent.setup()
    render(<CgvoWorkspace />)
    await screen.findByText('Classical Geography & Visibility')
    const selector = screen.getByLabelText('Varahamihira absolute frame')
    expect(selector).toHaveValue('')
    await user.selectOptions(selector, 'VARAHAMIHIRA_CHITRA_180_RECONSTRUCTION_V1')
    await waitFor(() => expect(api.fetchCgvoWorkbench).toHaveBeenLastCalledWith(expect.objectContaining({
      absoluteFrameProfileId: 'VARAHAMIHIRA_CHITRA_180_RECONSTRUCTION_V1',
    })))
  })

  it('recomputes only local circumstances when locality changes', async () => {
    api.fetchCgvoStatus.mockResolvedValue(status)
    api.fetchCgvoEventSearch.mockResolvedValue({ contract: 'SEARCH', range: { startUtc: '', endUtc: '' }, eventType: 'SOLAR', events: [event], count: 1, selection: 'chronological', guardrails })
    api.fetchCgvoWorkbench.mockResolvedValue(workbench)
    const user = userEvent.setup()
    render(<CgvoWorkspace />)
    await screen.findByText('PARTIAL', { selector: 'strong' })
    await user.selectOptions(screen.getByLabelText('CGVO locality'), 'NEW_YORK')
    await waitFor(() => expect(api.fetchCgvoWorkbench).toHaveBeenLastCalledWith(expect.objectContaining({ localityId: 'NEW_YORK', globalMaxSwissUt: event.astronomyEventIdentity.globalMaxSwissUt, causalEventId: event.causalEventId })))
  })

  it('renders lunar magnitudes, clipped visibility, and explicit Swiss UT/display labels', async () => {
    api.fetchCgvoStatus.mockResolvedValue(status)
    api.fetchCgvoEventSearch.mockResolvedValue({ contract: 'SEARCH', range: { startUtc: '', endUtc: '' }, eventType: 'LUNAR', events: [lunarEvent], count: 1, selection: 'chronological', guardrails })
    api.fetchCgvoWorkbench.mockResolvedValue({ ...workbench, event: lunarEvent })
    render(<CgvoWorkspace />)
    expect(await screen.findByText('Umbral magnitude')).toBeInTheDocument()
    expect(screen.getByText('1.2000')).toBeInTheDocument()
    expect(screen.getByText('Penumbral magnitude')).toBeInTheDocument()
    expect(screen.getByText('2.3000')).toBeInTheDocument()
    expect(screen.getByText('RISE_SET_CLIPPED')).toBeInTheDocument()
    expect(screen.getByText(/Identity time scale: SWISSEPH_UT/)).toBeInTheDocument()
    expect(screen.getByText(/Rise\/set clip: MOONRISE/)).toBeInTheDocument()
  })
})
