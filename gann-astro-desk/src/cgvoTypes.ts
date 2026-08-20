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
  groups: Array<{ direction: string; nakshatras: string[]; mappingStatus: string }>
  guardrails: Record<string, unknown>
}

export type CgvoModernAstronomy = {
  globalType: string
  localEclipseType: string
  visibility: 'VISIBLE' | 'NOT_VISIBLE' | 'RISE_SET_CLIPPED'
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
  sunAltitudeAzimuth?: Record<string, number | null>
  moonAltitudeAzimuth?: Record<string, number | null>
  saros?: Record<string, number | null> | null
  rawAttributes?: Array<number | null>
}

export type CgvoEvent = {
  causalEventId: string
  eventIdentity: { eventType: string; globalMaxUtc: string; globalType: string }
  astronomyEventIdentity: {
    eventType: string
    globalType: string
    globalMaxUtc: string
    globalContacts: Record<string, string | null>
    astronomyContract: string
    ephemeris: string
    ephemerisVersion: string
    timeScale: string
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
  kurma: CgvoKurmaSeed
  guardrails: CgvoGuardrails
}
