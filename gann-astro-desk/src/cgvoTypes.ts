export type CgvoGuardrails = {
  readOnly: boolean
  experimental: boolean
  priceDataRead: boolean
  priceOutcomeRead: boolean
  fieldsPath: boolean
  sbcPath: boolean
  autoSuggestPath: boolean
  mlPath: boolean
  mt5Path: boolean
  executionAllowed: boolean
  automaticOrderPlacement: boolean
  marketDirectionInferred: boolean
  scoreAggregationUsed: boolean
  crossSourceComposition: boolean
}

export type CgvoSourceProfile = {
  profileId: string
  contract: string
  sourceId: string
  edition: string
  authority: string
  sourceStatus: string
  interpretationPolicy?: string
  claims?: Array<Record<string, unknown>>
  displayStatuses?: Record<string, string>
  lexicalLocks?: Array<Record<string, unknown>>
  banner?: string[]
  dimensions?: Array<Record<string, unknown>>
  guardrails: Record<string, unknown>
}

export type CgvoKurmaSeed = {
  contract: string
  status: string
  historicalSource?: {
    work?: string
    chapter?: string
    locatorPolicy?: string
    sourceStatus?: string
    historicalNamesStatus?: string
    modernGeographicInference?: boolean
    mappingStatus?: string
  }
  groups: Array<{
    direction: string
    nakshatras: string[]
    sourceVerses?: string
    historicalNames?: string[]
    historicalNameStatus?: string
    mappingStatus: string
  }>
  guardrails: Record<string, unknown>
}

export type CgvoHorizontalCoordinates = {
  altitudeTrueDeg?: number | null
  altitudeApparentDeg?: number | null
  azimuthDeg?: number | null
  sourceAzimuthDeg?: number | null
  azimuthConvention?: string
  sourceAzimuthConvention?: string
  rightAscensionDeg?: number | null
  localHourAngleDeg?: number | null
  meridianRelation?: string
  topocentric?: boolean
}

export type CgvoVisibilityDetails = {
  status: 'VISIBLE' | 'NOT_VISIBLE' | 'RISE_SET_CLIPPED'
  maximumVisibility: 'VISIBLE' | 'NOT_VISIBLE_AT_MAXIMUM'
  visibleWindowStartUtc: string | null
  visibleWindowEndUtc: string | null
  clipBoundaries: string[]
  horizonEvents: { riseUtc: string | null; setUtc: string | null }
  swissVisibilityFlags: number
}

export type CgvoModernAstronomy = {
  globalType: string
  localEclipseType: string
  visibility: 'VISIBLE' | 'NOT_VISIBLE' | 'RISE_SET_CLIPPED'
  visibilityDetails?: CgvoVisibilityDetails
  contacts: Record<string, string | null>
  localMaxUtc: string | null
  sunriseDuring?: string | null
  sunsetDuring?: string | null
  moonriseDuring?: string | null
  moonsetDuring?: string | null
  magnitude?: number | null
  obscuration?: number | null
  apparentDiameterRatio?: number | null
  apparentMoonSunDiameterRatio?: number | null
  coreShadowDiameterKm?: number | null
  umbralMagnitude?: number | null
  penumbralMagnitude?: number | null
  distanceFromOppositionDeg?: number | null
  sunAltitudeAzimuth?: CgvoHorizontalCoordinates
  moonAltitudeAzimuth?: CgvoHorizontalCoordinates
  magnitudeReference?: string
  saros?: Record<string, number | null> | null
  rawAttributes?: Array<number | null>
}

export type CgvoEvent = {
  causalEventId: string
  eventIdentity: {
    eventType: string
    globalMaxUtc: string
    globalMaxSwissUt?: string
    globalMaxUtcDisplay?: string
    globalType: string
    identityTimeScale?: string
    displayTimeScale?: string
    displayTimezone?: string
  }
  astronomyEventIdentity: {
    eventType: string
    globalType: string
    globalMaxUtc: string
    globalMaxSwissUt?: string
    globalMaxUtcDisplay?: string
    globalContacts: Record<string, string | null>
    globalContactsSwissUt?: Record<string, string | null>
    globalContactsUtcDisplay?: Record<string, string | null>
    astronomyContract: string
    ephemeris: string
    ephemerisVersion: string
    timeScale: string
    displayTimeScale?: string
    displayTimezone?: string
    deltaTModel: string
  }
  locality: Record<string, unknown> | null
  modernAstronomy: CgvoModernAstronomy | null
  observationalContext: Record<string, unknown>
  varahamihiraClaims: Array<Record<string, unknown>>
  trailokyaClaims: Array<Record<string, unknown>>
  historicalRegionCandidates: Array<Record<string, unknown>>
  sourceUnknowns: string[]
  provenance: Array<Record<string, unknown>>
  sourceAdapters?: Record<string, unknown>
  guardrails: CgvoGuardrails
}

export type CgvoStatus = {
  contract: string
  schemaVersion: number
  milestone: string
  status: string
  availableProfiles: string[]
  availableEventTypes: string[]
  guardrails: CgvoGuardrails
  sourceProfiles: Record<string, string>
  sourceAdapters?: Record<string, unknown>
}

export type CgvoSearch = {
  contract: string
  range: { startUtc: string; endUtc: string }
  eventType: 'SOLAR' | 'LUNAR'
  events: CgvoEvent[]
  count: number
  selection: string
  guardrails: CgvoGuardrails
}

export type CgvoWorkbench = {
  contract: string
  schemaVersion: number
  event: CgvoEvent | null
  sourceProfiles: CgvoSourceProfile[]
  sourceAdapters?: Record<string, unknown>
  kurma: CgvoKurmaSeed
  guardrails: CgvoGuardrails
}
