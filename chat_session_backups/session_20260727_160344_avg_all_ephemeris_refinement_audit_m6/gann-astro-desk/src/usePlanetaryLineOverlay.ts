import { useCallback, useEffect, useMemo, useRef, useState } from 'react'
import { fetchPlanetaryLines } from './api'
import {
  enabledPlanetaryLineGroups,
  planetaryLineCount,
  sampledVisibleCandleTimes,
} from './planetaryLines'
import type {
  ChartPayload,
  PlanetaryCollectiveEvent,
  PlanetaryLineGroup,
  PlanetaryLineOverlay,
  PlanetaryLineOverlaySettings,
} from './types'

export type PlanetaryLineOverlayStatus = 'idle' | 'calculating' | 'ready' | 'error'

function collectiveEventViolatesContract(
  event: PlanetaryCollectiveEvent,
): boolean {
  const refinement = event.refinement
  const commonViolation = (
    event.contract !== 'GANN_PLANETARY_COLLECTIVE_EVENT_V1'
    || !Number.isFinite(event.estimatedTimeUnix)
    || event.guardrails.directionalContribution !== 0
    || event.guardrails.castsSbcVedha
    || event.guardrails.consumedByLiveInference
    || event.guardrails.consumedByAutoSuggest
    || event.guardrails.consumedByShadowLedger
    || event.guardrails.consumedByOfficialMlNotes
    || event.guardrails.executionAllowed
  )
  if (commonViolation) return true
  if (!event.timing.exact) {
    return (
      event.refinedTimeUnix != null
      || event.guardrails.exactEventTime
      || (
        event.eventType === 'MEAN_RASHI_INGRESS'
        && (
          refinement == null
          || refinement.status !== 'SAMPLED_FALLBACK'
          || refinement.refinedTimeUnix != null
        )
      )
      || (
        event.eventType !== 'MEAN_RASHI_INGRESS'
        && refinement != null
      )
    )
  }
  return (
    event.eventType !== 'MEAN_RASHI_INGRESS'
    || !event.guardrails.exactEventTime
    || event.timing.method !== 'BRACKETED_BISECTION_OF_EPHEMERIS_MEAN'
    || event.refinedTimeUnix == null
    || !Number.isFinite(event.refinedTimeUnix)
    || event.refinedTimeUnix < event.sourceBracket.startUnix
    || event.refinedTimeUnix > event.sourceBracket.endUnix
    || refinement == null
    || refinement.contract !== 'GANN_PLANETARY_COLLECTIVE_EVENT_REFINEMENT_V1'
    || refinement.status !== 'REFINED_BRACKETED_ROOT'
    || refinement.refinedTimeUnix !== event.refinedTimeUnix
    || refinement.residualDeg == null
    || !Number.isFinite(refinement.residualDeg)
    || Math.abs(refinement.residualDeg) > refinement.residualToleranceDeg
    || refinement.guardrails.countsAsIndependentVote
    || refinement.guardrails.directionalContribution !== 0
    || refinement.guardrails.consumedByLiveInference
    || refinement.guardrails.consumedByAutoSuggest
    || refinement.guardrails.consumedByShadowLedger
    || refinement.guardrails.consumedByOfficialMlNotes
    || refinement.guardrails.executionAllowed
  )
}

export function assertPlanetaryLineOverlayResearchContract(
  result: PlanetaryLineOverlay,
): void {
  if (
    result.contract !== 'GANN_EXPLORATORY_PLANETARY_LINE_OVERLAY_V1'
    || result.guardrails.executionAllowed
    || result.guardrails.consumedByLiveInference
    || result.guardrails.consumedByAutoSuggest
    || result.guardrails.consumedByShadowLedger
  ) {
    throw new Error('Planetary line response violated its research-only contract')
  }
  const collective = result.collectiveField
  if (!collective) return
  const memberAuditViolatesContract = collective.samples.some((sample) => (
    sample.memberAudit.length !== collective.profile.members.length
    || new Set(sample.memberAudit.map((member) => member.body)).size
      !== collective.profile.members.length
    || sample.memberAudit.some((member) => (
      !collective.profile.members.includes(member.body)
      || !Number.isFinite(member.weight)
      || (
        member.longitudeDeg != null
        && !Number.isFinite(member.longitudeDeg)
      )
      || (
        member.angularDistanceFromMeanDeg != null
        && !Number.isFinite(member.angularDistanceFromMeanDeg)
      )
      || (
        member.longitudeLeverageDeg != null
        && !Number.isFinite(member.longitudeLeverageDeg)
      )
      || (
        member.coherenceLeverage != null
        && !Number.isFinite(member.coherenceLeverage)
      )
      || (
        member.influenceRank != null
        && (!Number.isInteger(member.influenceRank) || member.influenceRank < 1)
      )
    ))
  ))
  const ingressEvents = collective.events.filter(
    (event) => event.eventType === 'MEAN_RASHI_INGRESS',
  )
  const refinedIngressCount = ingressEvents.filter(
    (event) => event.timing.exact,
  ).length
  const fallbackIngressCount = ingressEvents.length - refinedIngressCount
  if (
    collective.contract !== 'GANN_PLANETARY_COLLECTIVE_FIELD_V1'
    || collective.guardrails.executionAllowed
    || collective.guardrails.consumedByLiveInference
    || collective.guardrails.consumedByAutoSuggest
    || collective.guardrails.consumedByShadowLedger
    || collective.guardrails.consumedByOfficialMlNotes
    || collective.guardrails.directionalContribution !== 0
    || collective.guardrails.castsSbcVedha
    || collective.motion.contract !== 'GANN_PLANETARY_COLLECTIVE_MOTION_V1'
    || collective.motion.guardrails.executionAllowed
    || collective.motion.guardrails.bridgesUnreliableSamples
    || collective.influence.contract !== 'GANN_PLANETARY_COLLECTIVE_INFLUENCE_V1'
    || collective.influence.guardrails.countsAsIndependentVote
    || collective.influence.guardrails.directionalContribution !== 0
    || collective.influence.guardrails.consumedByLiveInference
    || collective.influence.guardrails.consumedByAutoSuggest
    || collective.influence.guardrails.consumedByShadowLedger
    || collective.influence.guardrails.consumedByOfficialMlNotes
    || collective.influence.guardrails.executionAllowed
    || collective.samples.length === 0
    || memberAuditViolatesContract
    || collective.eventSummary.contract !== 'GANN_PLANETARY_COLLECTIVE_EVENT_SUMMARY_V1'
    || collective.eventSummary.eventCount !== collective.events.length
    || collective.eventSummary.guardrails.executionAllowed
    || collective.eventSummary.guardrails.sampledTimingOnly
    || collective.eventSummary.refinement.contract
      !== 'GANN_PLANETARY_COLLECTIVE_EVENT_REFINEMENT_V1'
    || collective.eventSummary.refinement.candidateBudget !== 64
    || collective.eventSummary.refinement.candidateCount
      !== ingressEvents.length
    || collective.eventSummary.refinement.candidateCount
      !== (
        collective.eventSummary.refinement.attemptedCount
        + collective.eventSummary.refinement.skippedBudgetCount
      )
    || collective.eventSummary.refinement.attemptedCount
      > collective.eventSummary.refinement.candidateBudget
    || collective.eventSummary.refinement.fallbackCount
      !== (
        collective.eventSummary.refinement.candidateCount
        - collective.eventSummary.refinement.refinedCount
      )
    || collective.eventSummary.refinement.refinedCount !== refinedIngressCount
    || collective.eventSummary.refinement.fallbackCount !== fallbackIngressCount
    || !collective.eventSummary.refinement.guardrails.heuristicThresholdEventsRemainSampled
    || collective.eventSummary.refinement.guardrails.countsAsIndependentVote
    || collective.eventSummary.refinement.guardrails.directionalContribution !== 0
    || collective.eventSummary.refinement.guardrails.consumedByLiveInference
    || collective.eventSummary.refinement.guardrails.consumedByAutoSuggest
    || collective.eventSummary.refinement.guardrails.consumedByShadowLedger
    || collective.eventSummary.refinement.guardrails.consumedByOfficialMlNotes
    || collective.eventSummary.refinement.guardrails.executionAllowed
    || collective.events.some(collectiveEventViolatesContract)
    || collective.evidence.contract !== 'GANN_RESEARCH_EVIDENCE_PACKET_V1'
    || collective.evidence.empiricalCoefficient !== 0
    || collective.evidence.guardrails.consumedByLiveInference
    || collective.evidence.guardrails.consumedByAutoSuggest
    || collective.evidence.guardrails.consumedByShadowLedger
    || collective.evidence.guardrails.consumedByOfficialMlNotes
    || collective.evidence.guardrails.executionAllowed
  ) {
    throw new Error('AVG collective geometry violated its context-only contract')
  }
}

export function usePlanetaryLineOverlay(
  chart: ChartPayload | null,
  settings: PlanetaryLineOverlaySettings,
  visibleStartUtc?: string,
  visibleEndUtc?: string,
) {
  const [overlay, setOverlay] = useState<PlanetaryLineOverlay | null>(null)
  const [status, setStatus] = useState<PlanetaryLineOverlayStatus>('idle')
  const [error, setError] = useState('')
  const [refreshNonce, setRefreshNonce] = useState(0)
  const requestSequence = useRef(0)
  const lineCount = planetaryLineCount(settings)
  const timestamps = useMemo(
    () => sampledVisibleCandleTimes(
      chart?.candles ?? [],
      visibleStartUtc,
      visibleEndUtc,
      settings.sampleLimit,
    ),
    [chart?.candles, settings.sampleLimit, visibleEndUtc, visibleStartUtc],
  )
  const groups = useMemo(
    () => enabledPlanetaryLineGroups(settings),
    [settings],
  )
  const requestKey = useMemo(() => JSON.stringify({
    symbol: chart?.symbol ?? '',
    timeframe: chart?.timeframe ?? '',
    timestamps,
    groups,
  }), [chart?.symbol, chart?.timeframe, groups, timestamps])
  const requestInput = useMemo(() => JSON.parse(requestKey) as {
    symbol: string
    timeframe: string
    timestamps: number[]
    groups: PlanetaryLineGroup[]
  }, [requestKey])

  useEffect(() => {
    const sequence = ++requestSequence.current
    if (!requestInput.symbol || !settings.visible || !lineCount || !requestInput.timestamps.length) {
      setOverlay(null)
      setError('')
      setStatus('idle')
      return
    }
    if (lineCount > 96) {
      setOverlay(null)
      setError(`This setup creates ${lineCount} lines; the live limit is 96.`)
      setStatus('error')
      return
    }
    setStatus('calculating')
    setError('')
    const timer = window.setTimeout(() => {
      void fetchPlanetaryLines({
        ...requestInput,
      }).then((result) => {
        if (sequence !== requestSequence.current) return
        assertPlanetaryLineOverlayResearchContract(result)
        setOverlay(result)
        setStatus('ready')
      }).catch((reason) => {
        if (sequence !== requestSequence.current) return
        setOverlay(null)
        setStatus('error')
        setError(reason instanceof Error ? reason.message : String(reason))
      })
    }, 260)
    return () => window.clearTimeout(timer)
  }, [lineCount, refreshNonce, requestInput, settings.visible])

  const recalculate = useCallback(() => {
    setRefreshNonce((current) => current + 1)
  }, [])

  return {
    overlay,
    status,
    error,
    requestedLineCount: lineCount,
    sampledTimestampCount: timestamps.length,
    generatedAtUtc: overlay?.generatedAtUtc ?? '',
    recalculate,
  }
}
