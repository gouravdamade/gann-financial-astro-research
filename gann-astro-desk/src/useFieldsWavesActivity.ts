import { useCallback, useEffect, useRef, useState } from 'react'
import { fetchMultiOscillatorActivityRange } from './api'
import {
  ActivityChunkCache,
  activityChunksForVisibleRange,
  activityVisibleRangeIsBounded,
  type ActivityVisibleRange,
} from './fieldsWavesActivity'
import type { MultiOscillatorActivityRange } from './types'

export type FieldsWavesActivityStatus = 'disabled' | 'idle' | 'loading' | 'ready' | 'bounded_partial' | 'data_unavailable'

export function useFieldsWavesActivity(enabled: boolean, chartSymbol: string) {
  const cacheRef = useRef<ActivityChunkCache | null>(null)
  if (!cacheRef.current) cacheRef.current = new ActivityChunkCache(fetchMultiOscillatorActivityRange)
  const timerRef = useRef<number | null>(null)
  const enabledRef = useRef(enabled)
  const symbolRef = useRef(chartSymbol)
  const currentRangeKeyRef = useRef<string | null>(null)
  const [activity, setActivity] = useState<MultiOscillatorActivityRange | null>(null)
  const [requestStatus, setRequestStatus] = useState<FieldsWavesActivityStatus>('disabled')
  const [activityRangeBounded, setActivityRangeBounded] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    enabledRef.current = enabled
    symbolRef.current = chartSymbol
    if (!enabled && timerRef.current != null) {
      window.clearTimeout(timerRef.current)
      timerRef.current = null
    }
    if (!enabled || chartSymbol !== 'USDJPY') setActivityRangeBounded(false)
    setRequestStatus(enabled && chartSymbol === 'USDJPY' ? 'idle' : 'disabled')
  }, [enabled, chartSymbol])

  useEffect(() => () => {
    if (timerRef.current != null) window.clearTimeout(timerRef.current)
  }, [])

  const requestVisibleRange = useCallback((range: ActivityVisibleRange) => {
    if (!enabledRef.current || symbolRef.current !== 'USDJPY') return
    if (timerRef.current != null) window.clearTimeout(timerRef.current)
    timerRef.current = window.setTimeout(() => {
      timerRef.current = null
      if (!enabledRef.current || symbolRef.current !== 'USDJPY') return
      const cache = cacheRef.current
      if (!cache) return
      let chunks
      let isRangeBounded: boolean
      try {
        chunks = activityChunksForVisibleRange(range)
        isRangeBounded = activityVisibleRangeIsBounded(range)
      } catch {
        return
      }
      const requestKey = chunks.map((chunk) => chunk.key).join('||')
      currentRangeKeyRef.current = requestKey
      setActivityRangeBounded(isRangeBounded)
      setError('')
      const allCached = chunks.every((chunk) => cache.has(chunk))
      setActivity(cache.getMerged())
      setRequestStatus(allCached ? (isRangeBounded ? 'bounded_partial' : 'ready') : 'loading')
      void Promise.all(chunks.map((chunk) => cache.request(chunk))).then(() => {
        setActivity(cache.getMerged())
        if (currentRangeKeyRef.current === requestKey && enabledRef.current) {
          setRequestStatus(isRangeBounded ? 'bounded_partial' : 'ready')
        }
      }).catch((requestError: unknown) => {
        if (currentRangeKeyRef.current !== requestKey || !enabledRef.current) return
        setActivity(cache.getMerged())
        setError(requestError instanceof Error ? requestError.message : String(requestError))
        setRequestStatus('data_unavailable')
      })
    }, 180)
  }, [])

  return { activity, requestStatus, activityRangeBounded, error, requestVisibleRange }
}
