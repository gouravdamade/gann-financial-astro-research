import type { AspectWindow, ChakraLabSnapshot } from './types'

export const PROJECT_CONVENTION_TIMING_PHASE_V0 = {
  contract: 'PROJECT_CONVENTION_TIMING_PHASE_V0',
  classification: 'PROJECT_CONVENTION_EXPERIMENTAL',
  featureFlag: 'VITE_ENABLE_TIMING_PHASE_EXPERIMENT',
  phaseSpanRadians: (3 * Math.PI) / 4,
  safeMarginRadians: Math.PI / 12,
  resultantFloorUnits: 0.25,
  relativeResultantFloor: 0.15,
  voteWeight: 0,
  directionalContribution: 0,
  fusionCoefficient: 0,
  executionAllowed: false,
  automaticOrderPlacement: false,
} as const

export type TimingLifecycle = 'APPLYING' | 'EXACT' | 'SEPARATING' | 'UNKNOWN'
export type TimingGeometryState = 'PROJECT_CONVENTION_GEOMETRY' | 'NON_DIRECTIONAL_TIMING_GEOMETRY' | 'RESULTANT_NEAR_ZERO' | 'UNKNOWN'

export type TimingEventPhase = {
  eventId: string
  label: string
  startUtc: string
  exactUtc: string
  endUtc: string
  lifecycle: TimingLifecycle
  halfWindowSeconds: number
  timingPhaseRadians: number
  safeSector: boolean
}

export type TimingPhaseVector = {
  vectorId: string
  eventId: string
  eventLabel: string
  body: string
  target: string
  sourcePolarity: 'SUPPORTIVE' | 'ADVERSE'
  sourcePhaseRadians: number
  timingPhaseRadians: number
  totalPhaseRadians: number
  magnitudeUnits: number
  realUnits: number
  imaginaryUnits: number
  lifecycle: TimingLifecycle
  safeSector: boolean
}

export type TimingPhaseExperiment = {
  contract: typeof PROJECT_CONVENTION_TIMING_PHASE_V0.contract
  classification: typeof PROJECT_CONVENTION_TIMING_PHASE_V0.classification
  enabled: boolean
  state: TimingGeometryState
  marketDirection: 'ABSTAIN'
  directionalInterpretation: 'SUPPRESSED' | 'NOT_AVAILABLE'
  activeEvents: TimingEventPhase[]
  vectors: TimingPhaseVector[]
  unknownVectorCount: number
  realUnits: number | null
  imaginaryUnits: number | null
  resultantUnits: number | null
  grossUnits: number | null
  coherence: number | null
  conflict: number | null
  collectivePhaseRadians: number | null
  resultantFloorUnits: number | null
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
  if (Math.abs(asOfSeconds - exactSeconds) <= 30) return 'EXACT'
  return asOfSeconds < exactSeconds ? 'APPLYING' : 'SEPARATING'
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
  const guardrails = {
    voteWeight: 0 as const,
    directionalContribution: 0 as const,
    fusionCoefficient: 0 as const,
    executionAllowed: false as const,
    automaticOrderPlacement: false as const,
    financiallyValidated: false as const,
  }
  if (!enabled || !snapshot) {
    return {
      contract: PROJECT_CONVENTION_TIMING_PHASE_V0.contract,
      classification: PROJECT_CONVENTION_TIMING_PHASE_V0.classification,
      enabled,
      state: 'UNKNOWN',
      marketDirection: 'ABSTAIN',
      directionalInterpretation: 'NOT_AVAILABLE',
      activeEvents: [],
      vectors: [],
      unknownVectorCount: 0,
      realUnits: null,
      imaginaryUnits: null,
      resultantUnits: null,
      grossUnits: null,
      coherence: null,
      conflict: null,
      collectivePhaseRadians: null,
      resultantFloorUnits: null,
      safeSector: false,
      guardrails,
    }
  }

  const asOfSeconds = Date.parse(snapshot.as_of_utc) / 1000
  const activeEvents = aspects
    .filter((aspect) => asOfSeconds >= aspect.start && asOfSeconds <= aspect.end)
    .sort((left, right) => left.start - right.start || left.eventId.localeCompare(right.eventId))
    .map((aspect): TimingEventPhase => {
      const halfWindowSeconds = Math.max(1, (aspect.end - aspect.start) / 2)
      const timingPhaseRadians = PROJECT_CONVENTION_TIMING_PHASE_V0.phaseSpanRadians * clamp(
        (asOfSeconds - aspect.peak) / halfWindowSeconds,
        -1,
        1,
      )
      return {
        eventId: aspect.eventId,
        label: aspect.aspectLabel,
        startUtc: aspect.startIso,
        exactUtc: aspect.peakIso,
        endUtc: aspect.endIso,
        lifecycle: lifecycleFor(asOfSeconds, aspect.peak),
        halfWindowSeconds,
        timingPhaseRadians,
        safeSector: Math.abs(timingPhaseRadians) < Math.PI / 2 - PROJECT_CONVENTION_TIMING_PHASE_V0.safeMarginRadians,
      }
    })
  if (!activeEvents.length) {
    return {
      contract: PROJECT_CONVENTION_TIMING_PHASE_V0.contract,
      classification: PROJECT_CONVENTION_TIMING_PHASE_V0.classification,
      enabled,
      state: 'UNKNOWN',
      marketDirection: 'ABSTAIN',
      directionalInterpretation: 'NOT_AVAILABLE',
      activeEvents: [],
      vectors: [],
      unknownVectorCount: snapshot.guidance?.contributions.length ?? 0,
      realUnits: null,
      imaginaryUnits: null,
      resultantUnits: null,
      grossUnits: null,
      coherence: null,
      conflict: null,
      collectivePhaseRadians: null,
      resultantFloorUnits: null,
      safeSector: false,
      guardrails,
    }
  }

  const resolved = snapshot.guidance?.contributions.filter((contribution) => contribution.signed_guidance_units != null) ?? []
  const vectors = resolved.flatMap((contribution, contributionIndex) => activeEvents.map((event): TimingPhaseVector => {
    const sourcePolarity = (contribution.signed_guidance_units ?? 0) >= 0 ? 'SUPPORTIVE' : 'ADVERSE'
    const sourcePhaseRadians = sourcePolarity === 'SUPPORTIVE' ? 0 : Math.PI
    const magnitudeUnits = Math.abs(contribution.signed_guidance_units ?? 0)
    const totalPhaseRadians = sourcePhaseRadians + event.timingPhaseRadians
    return {
      vectorId: `${event.eventId}:${contribution.body}:${contribution.target.row}:${contribution.target.column}:${contributionIndex}`,
      eventId: event.eventId,
      eventLabel: event.label,
      body: contribution.body,
      target: contribution.target.value,
      sourcePolarity,
      sourcePhaseRadians,
      timingPhaseRadians: event.timingPhaseRadians,
      totalPhaseRadians,
      magnitudeUnits,
      realUnits: magnitudeUnits * Math.cos(totalPhaseRadians),
      imaginaryUnits: magnitudeUnits * Math.sin(totalPhaseRadians),
      lifecycle: event.lifecycle,
      safeSector: event.safeSector,
    }
  }))
  const realUnits = vectors.reduce((sum, vector) => sum + vector.realUnits, 0)
  const imaginaryUnits = vectors.reduce((sum, vector) => sum + vector.imaginaryUnits, 0)
  const resultantUnits = Math.hypot(realUnits, imaginaryUnits)
  const grossUnits = vectors.reduce((sum, vector) => sum + vector.magnitudeUnits, 0)
  const resultantFloorUnits = Math.max(
    PROJECT_CONVENTION_TIMING_PHASE_V0.resultantFloorUnits,
    grossUnits * PROJECT_CONVENTION_TIMING_PHASE_V0.relativeResultantFloor,
  )
  const nearZero = vectors.length === 0 || resultantUnits < resultantFloorUnits
  const safeSector = activeEvents.every((event) => event.safeSector)
  const state: TimingGeometryState = nearZero
    ? 'RESULTANT_NEAR_ZERO'
    : safeSector
      ? 'PROJECT_CONVENTION_GEOMETRY'
      : 'NON_DIRECTIONAL_TIMING_GEOMETRY'
  return {
    contract: PROJECT_CONVENTION_TIMING_PHASE_V0.contract,
    classification: PROJECT_CONVENTION_TIMING_PHASE_V0.classification,
    enabled,
    state,
    marketDirection: 'ABSTAIN',
    directionalInterpretation: safeSector && !nearZero ? 'SUPPRESSED' : 'NOT_AVAILABLE',
    activeEvents,
    vectors,
    unknownVectorCount: ((snapshot.guidance?.contributions.length ?? 0) - resolved.length) * activeEvents.length,
    realUnits,
    imaginaryUnits,
    resultantUnits,
    grossUnits,
    coherence: grossUnits > 0 ? resultantUnits / grossUnits : null,
    conflict: grossUnits > 0 ? 1 - resultantUnits / grossUnits : null,
    collectivePhaseRadians: nearZero ? null : Math.atan2(imaginaryUnits, realUnits),
    resultantFloorUnits,
    safeSector,
    guardrails,
  }
}
