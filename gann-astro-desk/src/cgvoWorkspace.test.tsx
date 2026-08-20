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
  eventIdentity: { eventType: 'SOLAR', globalMaxUtc: '2027-08-02T10:06:41Z', globalType: 'TOTAL' },
  astronomyEventIdentity: {
    eventType: 'SOLAR', globalType: 'TOTAL', globalMaxUtc: '2027-08-02T10:06:41Z',
    globalContacts: { C1: '2027-08-02T07:30:17Z', C2: '2027-08-02T08:23:29Z', MAX: '2027-08-02T10:06:41Z', C3: '2027-08-02T11:49:56Z', C4: '2027-08-02T12:43:08Z' },
    astronomyContract: 'MODERN_ASTRONOMY_VISIBILITY_V1', ephemeris: 'Swiss Ephemeris', ephemerisVersion: '2.10.03', timeScale: 'UT1_PRIMARY_SWISSEPH_UT', deltaTModel: 'SWISS_EPHEMERIS_INTERNAL',
  },
  locality: { localityId: 'UJJAIN', label: 'Ujjain, India', latitude: 23.1765, longitude: 75.7885, elevationM: 0, timezone: 'Asia/Kolkata' },
  modernAstronomy: {
    globalType: 'TOTAL', localEclipseType: 'PARTIAL', visibility: 'VISIBLE', localMaxUtc: '2027-08-02T11:07:16Z', contacts: { C1: '2027-08-02T10:21:13Z', C2: null, MAX: '2027-08-02T11:07:16Z', C3: null, C4: '2027-08-02T11:49:57Z' },
    magnitude: 0.29, obscuration: 0.18, sunAltitudeAzimuth: { altitudeApparentDeg: 33, azimuthDeg: 96 }, moonAltitudeAzimuth: { altitudeApparentDeg: 33, azimuthDeg: 96 },
  },
  observationalContext: {}, varahamihiraClaims: [], trailokyaClaims: [], historicalRegionCandidates: [], sourceUnknowns: [], provenance: [], guardrails,
}

const status: CgvoStatus = { contract: 'CLASSICAL_GEOGRAPHY_VISIBILITY_OBSERVATORY_V1', schemaVersion: 1, milestone: 'PFR-V2B-CGVO-P1', status: 'READY', availableProfiles: ['MODERN_ASTRONOMY_VISIBILITY_V1'], availableEventTypes: ['SOLAR', 'LUNAR'], guardrails, sourceProfiles: { varahamihira: 'WORKING_WITNESS_METADATA_PENDING', trailokya: 'SOURCE_SILENT_FOR_ECLIPSE_VISIBILITY_IN_HELD_WITNESS' } }
const workbench: CgvoWorkbench = {
  contract: 'CLASSICAL_GEOGRAPHY_VISIBILITY_OBSERVATORY_V1', schemaVersion: 1, event, guardrails,
  sourceProfiles: [
    { profileId: 'VARAHAMIHIRA_BS_ECLIPSE_V1', contract: 'SOURCE', sourceId: 'BS', edition: '1946 working witness', authority: 'SOURCE', sourceStatus: 'WORKING_WITNESS_METADATA_PENDING', displayStatuses: { rasi: 'UNKNOWN_ZODIAC_FRAME_NOT_AUTHORIZED', colour: 'OBSERVATION_REQUIRED' }, claims: [], guardrails: {} },
    { profileId: 'TRAILOKYA_1972_GEOGRAPHY_ARGHA_V1', contract: 'SOURCE', sourceId: 'TRAILOKYA', edition: '1972', authority: 'SOURCE', sourceStatus: 'SOURCE_SILENT_FOR_ECLIPSE_VISIBILITY_IN_HELD_WITNESS', banner: ['ECLIPSE VISIBILITY DOCTRINE: SOURCE SILENT IN HELD WITNESS'], guardrails: {} },
  ],
  kurma: { contract: 'KURMA', status: 'UNKNOWN', groups: [{ direction: 'CENTER', nakshatras: ['Krittika'], mappingStatus: 'UNKNOWN' }], guardrails: {} },
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
    expect(screen.getByText(/Rasi: UNKNOWN/)).toBeInTheDocument()
    expect(screen.queryByText(/BULLISH|BEARISH/)).not.toBeInTheDocument()
  })

  it('recomputes only local circumstances when locality changes', async () => {
    api.fetchCgvoStatus.mockResolvedValue(status)
    api.fetchCgvoEventSearch.mockResolvedValue({ contract: 'SEARCH', range: { startUtc: '', endUtc: '' }, eventType: 'SOLAR', events: [event], count: 1, selection: 'chronological', guardrails })
    api.fetchCgvoWorkbench.mockResolvedValue(workbench)
    const user = userEvent.setup()
    render(<CgvoWorkspace />)
    await screen.findByText('PARTIAL', { selector: 'strong' })
    await user.selectOptions(screen.getByLabelText('CGVO locality'), 'NEW_YORK')
    await waitFor(() => expect(api.fetchCgvoWorkbench).toHaveBeenLastCalledWith(expect.objectContaining({ localityId: 'NEW_YORK', globalMaxUtc: event.astronomyEventIdentity.globalMaxUtc })))
  })
})
