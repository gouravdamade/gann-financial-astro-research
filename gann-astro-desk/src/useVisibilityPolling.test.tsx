// @vitest-environment jsdom

import { act, renderHook } from '@testing-library/react'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { useVisibilityPolling } from './useVisibilityPolling'

describe('useVisibilityPolling', () => {
  let visibilityState: DocumentVisibilityState

  beforeEach(() => {
    vi.useFakeTimers()
    visibilityState = 'visible'
    Object.defineProperty(document, 'visibilityState', {
      configurable: true,
      get: () => visibilityState,
    })
  })

  afterEach(() => {
    vi.useRealTimers()
  })

  it('does not overlap requests and uses the slower hidden cadence', async () => {
    let finishFirst: (() => void) | undefined
    const firstRequest = new Promise<void>((resolve) => {
      finishFirst = resolve
    })
    const task = vi.fn()
      .mockImplementationOnce(() => firstRequest)
      .mockResolvedValue(undefined)

    const { unmount } = renderHook(() => useVisibilityPolling(task, {
      intervalMs: 1000,
      hiddenIntervalMs: 30000,
    }))

    await act(async () => {
      await vi.advanceTimersByTimeAsync(0)
    })
    expect(task).toHaveBeenCalledTimes(1)

    await act(async () => {
      await vi.advanceTimersByTimeAsync(5000)
    })
    expect(task).toHaveBeenCalledTimes(1)

    visibilityState = 'hidden'
    await act(async () => {
      finishFirst?.()
      await firstRequest
    })

    await act(async () => {
      await vi.advanceTimersByTimeAsync(29999)
    })
    expect(task).toHaveBeenCalledTimes(1)

    await act(async () => {
      await vi.advanceTimersByTimeAsync(1)
    })
    expect(task).toHaveBeenCalledTimes(2)
    unmount()
  })
})
