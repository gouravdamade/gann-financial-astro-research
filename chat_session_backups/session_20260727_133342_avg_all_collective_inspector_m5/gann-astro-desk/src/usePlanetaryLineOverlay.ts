import { useCallback, useEffect, useMemo, useRef, useState } from 'react'
import { fetchPlanetaryLines } from './api'
import {
  enabledPlanetaryLineGroups,
  planetaryLineCount,
  sampledVisibleCandleTimes,
} from './planetaryLines'
import type {
  ChartPayload,
  PlanetaryLineGroup,
  PlanetaryLineOverlay,
  PlanetaryLineOverlaySettings,
} from './types'

export type PlanetaryLineOverlayStatus = 'idle' | 'calculating' | 'ready' | 'error'

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
    || collective.eventSummary.guardrails.executionAllowed
    || !collective.eventSummary.guardrails.sampledTimingOnly
    || collective.events.some((event) => (
      event.contract !== 'GANN_PLANETARY_COLLECTIVE_EVENT_V1'
      || event.timing.exact
      || event.guardrails.exactEventTime
      || event.guardrails.directionalContribution !== 0
      || event.guardrails.castsSbcVedha
      || event.guardrails.consumedByLiveInference
      || event.guardrails.consumedByAutoSuggest
      || event.guardrails.consumedByShadowLedger
      || event.guardrails.consumedByOfficialMlNotes
      || event.guardrails.executionAllowed
    ))
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
