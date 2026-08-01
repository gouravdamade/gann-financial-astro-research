import type { AspectWindow, ChakraLabSnapshot } from './types'

export const PROJECT_CONVENTION_TIMING_PHASE_V1 = {
  contract: 'PROJECT_CONVENTION_TIMING_PHASE_V1',
  classification: 'PROJECT_CONVENTION_EXPERIMENTAL',
  featureFlag: 'VITE_ENABLE_TIMING_PHASE_EXPERIMENT',
  phaseSpanRadians: (3 * Math.PI) / 4,
  safeMarginRadians: Math.PI / 12,
  exactToleranceSeconds: 30,
  symmetricTimingDeclared: false,
  voteWeight: 0,
  directionalContribution: 0,
  fusionCoefficient: 0,
  executionAllowed: false,
  automaticOrderPlacement: false,
} as const

export type TimingLifecycle = 'APPLYING' | 'EXACT' | 'SEPARATING' | 'UNKNOWN'
export type TimingGeometryState = 'UNLINKED_EVENT_GEOMETRY' | 'UNKNOWN_INVALID_EVENT_WINDOW' | 'UNKNOWN'

export type TimingEventPhase = {
  eventId: string
  label: string
  startUtc: string
  exactUtc: string
  endUtc: string
  lifecycle: TimingLifecycle
  applyingWindowSeconds: number | null
  separatingWindowSeconds: number | null
  normalizedLifecycleProgress: number | null
  timingPhaseRadians: number | null
  symmetricTimingDeclared: false
  safeSector: boolean
}

export type TimingPhaseVector = never

export type TimingPhaseExperiment = {
  contract: typeof PROJECT_CONVENTION_TIMING_PHASE_V1.contract
  classification: typeof PROJECT_CONVENTION_TIMING_PHASE_V1.classification
  enabled: boolean
  state: TimingGeometryState
  marketDirection: 'ABSTAIN'
  directionalInterpretation: 'NOT_AVAILABLE'
  calculationId: string | null
  activeEvents: TimingEventPhase[]
  vectors: TimingPhaseVector[]
  unknownVectorCount: number
  unlinkedResolvedContributionCount: number
  aggregateWithheld: boolean
  aggregateWithheldReason: string | null
  sourceGapId: 'EVENT_CONTRIBUTION_LINK_PROFILE_MISSING' | null
  realUnits: null
  imaginaryUnits: null
  resultantUnits: null
  grossUnits: null
  coherence: null
  conflict: null
  collectivePhaseRadians: null
  resultantFloorUnits: null
  safeSector: boolean
  guardrails: {
    voteWeight: 0
    directionalContribution: 0
    fusionCoefficient: 0
    executionAllowed: false
    automaticOrderPlacement: false
    financiallyValidated: false
  }
}

function clamp(value: number, minimum: number, maximum: number): number {
  return Math.max(minimum, Math.min(maximum, value))
}

function lifecycleFor(asOfSeconds: number, exactSeconds: number): TimingLifecycle {
  if (Math.abs(asOfSeconds - exactSeconds) <= PROJECT_CONVENTION_TIMING_PHASE_V1.exactToleranceSeconds) return 'EXACT'
  return asOfSeconds < exactSeconds ? 'APPLYING' : 'SEPARATING'
}

function stableCalculationId(asOfSeconds: number, events: TimingEventPhase[]): string {
  const input = JSON.stringify({
    contract: PROJECT_CONVENTION_TIMING_PHASE_V1.contract,
    asOfSeconds,
    linkProfile: 'MISSING',
    events,
  })
  let hash = 2166136261
  for (let index = 0; index < input.length; index += 1) {
    hash ^= input.charCodeAt(index)
    hash = Math.imul(hash, 16777619)
  }
  return `PFTPV1-${(hash >>> 0).toString(16).padStart(8, '0').toUpperCase()}`
}

function emptyExperiment(enabled: boolean, unknownVectorCount = 0): TimingPhaseExperiment {
  return {
    contract: PROJECT_CONVENTION_TIMING_PHASE_V1.contract,
    classification: PROJECT_CONVENTION_TIMING_PHASE_V1.classification,
    enabled,
    state: 'UNKNOWN',
    marketDirection: 'ABSTAIN',
    directionalInterpretation: 'NOT_AVAILABLE',
    calculationId: null,
    activeEvents: [],
    vectors: [],
    unknownVectorCount,
    unlinkedResolvedContributionCount: 0,
    aggregateWithheld: true,
    aggregateWithheldReason: null,
    sourceGapId: null,
    realUnits: null,
    imaginaryUnits: null,
    resultantUnits: null,
    grossUnits: null,
    coherence: null,
    conflict: null,
    collectivePhaseRadians: null,
    resultantFloorUnits: null,
    safeSector: false,
    guardrails: {
      voteWeight: 0,
      directionalContribution: 0,
      fusionCoefficient: 0,
      executionAllowed: false,
      automaticOrderPlacement: false,
      financiallyValidated: false,
    },
  }
}

export function calculateProductFirstTimingPhase({
  enabled,
  snapshot,
  aspects,
}: {
  enabled: boolean
  snapshot: ChakraLabSnapshot | null
  aspects: AspectWindow[]
}): TimingPhaseExperiment {
  if (!enabled || !snapshot) return emptyExperiment(enabled)

  const asOfSeconds = Date.parse(snapshot.as_of_utc) / 1000
  const activeEvents = aspects
    .filter((aspect) => asOfSeconds >= aspect.start && asOfSeconds <= aspect.end)
    .sort((left, right) => left.start - right.start || left.eventId.localeCompare(right.eventId))
    .map((aspect): TimingEventPhase => {
      const applyingWindowSeconds = aspect.peak - aspect.start
      const separatingWindowSeconds = aspect.end - aspect.peak
      if (applyingWindowSeconds <= 0 || separatingWindowSeconds <= 0) {
        return {
          eventId: aspect.eventId,
          label: aspect.aspectLabel,
          startUtc: aspect.startIso,
          exactUtc: aspect.peakIso,
          endUtc: aspect.endIso,
          lifecycle: 'UNKNOWN',
          applyingWindowSeconds: applyingWindowSeconds > 0 ? applyingWindowSeconds : null,
          separatingWindowSeconds: separatingWindowSeconds > 0 ? separatingWindowSeconds : null,
          normalizedLifecycleProgress: null,
          timingPhaseRadians: null,
          symmetricTimingDeclared: false,
          safeSector: false,
        }
      }
      const lifecycle = lifecycleFor(asOfSeconds, aspect.peak)
      const normalizedLifecycleProgress = lifecycle === 'EXACT'
        ? 0
        : lifecycle === 'APPLYING'
          ? clamp((asOfSeconds - aspect.peak) / applyingWindowSeconds, -1, 0)
          : clamp((asOfSeconds - aspect.peak) / separatingWindowSeconds, 0, 1)
      const timingPhaseRadians = PROJECT_CONVENTION_TIMING_PHASE_V1.phaseSpanRadians * normalizedLifecycleProgress
      return {
        eventId: aspect.eventId,
        label: aspect.aspectLabel,
        startUtc: aspect.startIso,
        exactUtc: aspect.peakIso,
        endUtc: aspect.endIso,
        lifecycle,
        applyingWindowSeconds,
        separatingWindowSeconds,
        normalizedLifecycleProgress,
        timingPhaseRadians,
        symmetricTimingDeclared: false,
        safeSector: Math.abs(timingPhaseRadians) < Math.PI / 2 - PROJECT_CONVENTION_TIMING_PHASE_V1.safeMarginRadians,
      }
    })

  const unknownContributionCount = snapshot.guidance?.contributions.filter((contribution) => contribution.signed_guidance_units == null).length ?? 0
  if (!activeEvents.length) return emptyExperiment(true, unknownContributionCount)

  const calculationId = stableCalculationId(asOfSeconds, activeEvents)
  if (activeEvents.some((event) => event.lifecycle === 'UNKNOWN')) {
    return {
      ...emptyExperiment(true, unknownContributionCount),
      state: 'UNKNOWN_INVALID_EVENT_WINDOW',
      calculationId,
      activeEvents,
      aggregateWithheldReason: 'One or more active events has an undeclared zero-length applying or separating span. Its lifecycle geometry fails closed as unknown.',
    }
  }

  const resolvedContributionCount = snapshot.guidance?.contributions.filter((contribution) => contribution.signed_guidance_units != null).length ?? 0
  return {
    ...emptyExperiment(true, unknownContributionCount),
    state: 'UNLINKED_EVENT_GEOMETRY',
    calculationId,
    activeEvents,
    unlinkedResolvedContributionCount: resolvedContributionCount,
    aggregateWithheldReason: 'EVENT_CONTRIBUTION_LINK_PROFILE_MISSING: active event lifecycle geometry is visible, but aggregate interference is withheld because no causal contribution-event mapping has been declared.',
    sourceGapId: 'EVENT_CONTRIBUTION_LINK_PROFILE_MISSING',
    safeSector: activeEvents.every((event) => event.safeSector),
  }
}
