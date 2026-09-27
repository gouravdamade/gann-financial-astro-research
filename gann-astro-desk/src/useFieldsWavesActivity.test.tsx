// @vitest-environment jsdom

import { act, renderHook } from '@testing-library/react'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import type { MultiOscillatorActivityRange, MultiOscillatorActivityRangeRequest } from './types'

const { fetchMock } = vi.hoisted(() => ({ fetchMock: vi.fn() }))
vi.mock('./api', () => ({ fetchMultiOscillatorActivityRange: (request: MultiOscillatorActivityRangeRequest) => fetchMock(request) }))

import { useFieldsWavesActivity } from './useFieldsWavesActivity'

function emptyRange(request: MultiOscillatorActivityRangeRequest): MultiOscillatorActivityRange {
  const side = (sideIdentity: 'USD' | 'JPY') => ({
    sideIdentity,
    rangeStartUtc: request.rangeStartUtc,
    rangeEndUtc: request.rangeEndUtc,
    events: [],
    activityIntervals: [],
    coverage: 'KNOWN' as const,
    unknownReason: null,
  })
  return {
    contract: 'MO_UNSIGNED_EVENT_ACTIVITY_RANGE_V1_1',
    schemaVersion: 2,
    evidenceMode: 'EXPLORATORY_UNSIGNED',
    contributionContract: 'MO_ACTIVITY_CONTRIBUTION_V1',
    rangeStartUtc: request.rangeStartUtc,
    rangeEndUtc: request.rangeEndUtc,
    sideIdentities: ['USD', 'JPY'],
    eventUniverse: {} as MultiOscillatorActivityRange['eventUniverse'],
    fields: { USD: side('USD'), JPY: side('JPY') } as unknown as MultiOscillatorActivityRange['fields'],
    guardrails: {} as MultiOscillatorActivityRange['guardrails'],
  }
}

describe('visible-range activity controller', () => {
  beforeEach(() => {
    vi.useFakeTimers()
    fetchMock.mockReset()
    fetchMock.mockImplementation(async (request) => emptyRange(request))
  })

  afterEach(() => vi.useRealTimers())

  it('waits for the debounced visible range and makes one fixed-chunk request', async () => {
    const { result } = renderHook(() => useFieldsWavesActivity(true, 'USDJPY'))
    expect(fetchMock).not.toHaveBeenCalled()
    await act(async () => {
      result.current.requestVisibleRange({ from: 1_800_000_000, to: 1_800_100_000 })
      await vi.advanceTimersByTimeAsync(180)
    })
    expect(fetchMock).toHaveBeenCalledTimes(1)
    const request = fetchMock.mock.calls[0][0]
    expect(request.sideIdentities).toEqual(['USD', 'JPY'])
    expect(Date.parse(request.rangeEndUtc) - Date.parse(request.rangeStartUtc)).toBe(14 * 24 * 60 * 60 * 1000)
    expect(result.current.requestStatus).toBe('ready')
  })

  it('does not refetch on crosshair-only render, mode change, marker toggle, or pan inside a cached chunk', async () => {
    const { result, rerender } = renderHook(
      ({ mode, markersVisible }: { mode: string; markersVisible: boolean }) => {
        void mode
        void markersVisible
        return useFieldsWavesActivity(true, 'USDJPY')
      },
      { initialProps: { mode: 'MODE_1', markersVisible: true } },
    )
    await act(async () => {
      result.current.requestVisibleRange({ from: 1_800_000_000, to: 1_800_100_000 })
      await vi.advanceTimersByTimeAsync(180)
    })
    expect(fetchMock).toHaveBeenCalledTimes(1)
    rerender({ mode: 'MODE_2', markersVisible: false })
    rerender({ mode: 'MODE_3', markersVisible: true })
    await act(async () => {
      result.current.requestVisibleRange({ from: 1_800_010_000, to: 1_800_090_000 })
      await vi.advanceTimersByTimeAsync(180)
    })
    expect(fetchMock).toHaveBeenCalledTimes(1)
  })

  it('requests one bounded chunk when the visible range enters an uncached interval', async () => {
    const { result } = renderHook(() => useFieldsWavesActivity(true, 'USDJPY'))
    await act(async () => {
      result.current.requestVisibleRange({ from: 1_800_000_000, to: 1_800_100_000 })
      await vi.advanceTimersByTimeAsync(180)
    })
    expect(fetchMock).toHaveBeenCalledTimes(1)
    await act(async () => {
      result.current.requestVisibleRange({
        from: 1_800_000_000 + 14 * 24 * 60 * 60,
        to: 1_800_100_000 + 14 * 24 * 60 * 60,
      })
      await vi.advanceTimersByTimeAsync(180)
    })
    expect(fetchMock).toHaveBeenCalledTimes(2)
    expect(fetchMock.mock.calls[1][0].rangeStartUtc).not.toBe(fetchMock.mock.calls[0][0].rangeStartUtc)
    expect(Date.parse(fetchMock.mock.calls[1][0].rangeEndUtc) - Date.parse(fetchMock.mock.calls[1][0].rangeStartUtc))
      .toBe(14 * 24 * 60 * 60 * 1000)
  })

  it('loads every bounded fixed chunk intersecting a zoomed-out visible range', async () => {
    const { result } = renderHook(() => useFieldsWavesActivity(true, 'USDJPY'))
    await act(async () => {
      result.current.requestVisibleRange({
        from: 1_800_000_000,
        to: 1_800_000_000 + 14 * 24 * 60 * 60 + 1,
      })
      await vi.advanceTimersByTimeAsync(180)
    })
    expect(fetchMock).toHaveBeenCalledTimes(2)
    expect(new Set(fetchMock.mock.calls.map(([request]) => request.rangeStartUtc)).size).toBe(2)
    expect(result.current.requestStatus).toBe('ready')
  })

  it('does not request activity while disabled or for a non-USDJPY chart', async () => {
    const { result, rerender } = renderHook(
      ({ enabled, symbol }: { enabled: boolean; symbol: string }) => useFieldsWavesActivity(enabled, symbol),
      { initialProps: { enabled: false, symbol: 'USDJPY' } },
    )
    act(() => result.current.requestVisibleRange({ from: 1_800_000_000, to: 1_800_100_000 }))
    await act(async () => vi.advanceTimersByTimeAsync(200))
    rerender({ enabled: true, symbol: 'EURUSD' })
    act(() => result.current.requestVisibleRange({ from: 1_800_000_000, to: 1_800_100_000 }))
    await act(async () => vi.advanceTimersByTimeAsync(200))
    expect(fetchMock).not.toHaveBeenCalled()
  })
})
