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
        if (
          result.contract !== 'GANN_EXPLORATORY_PLANETARY_LINE_OVERLAY_V1'
          || result.guardrails.executionAllowed
          || result.guardrails.consumedByLiveInference
        ) {
          throw new Error('Planetary line response violated its research-only contract')
        }
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
