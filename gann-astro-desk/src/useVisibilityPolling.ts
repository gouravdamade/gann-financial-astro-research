import { useEffect, useRef } from 'react'

type VisibilityPollingOptions = {
  enabled?: boolean
  intervalMs: number
  hiddenIntervalMs?: number
}

export function useVisibilityPolling(
  task: () => Promise<void>,
  {
    enabled = true,
    intervalMs,
    hiddenIntervalMs = Math.max(intervalMs, 30000),
  }: VisibilityPollingOptions,
): void {
  const taskRef = useRef(task)

  useEffect(() => {
    taskRef.current = task
  }, [task])

  useEffect(() => {
    if (!enabled) return
    let disposed = false
    let running = false
    let timer: number | null = null

    const schedule = (delayMs: number) => {
      if (disposed) return
      if (timer != null) window.clearTimeout(timer)
      timer = window.setTimeout(run, delayMs)
    }
    const run = async () => {
      timer = null
      if (disposed) return
      if (running) return
      running = true
      try {
        await taskRef.current()
      } catch {
        // Polling tasks surface their own user-facing error state.
      } finally {
        running = false
        schedule(document.visibilityState === 'hidden' ? hiddenIntervalMs : intervalMs)
      }
    }
    const handleVisibilityChange = () => {
      if (document.visibilityState === 'visible') schedule(0)
    }

    document.addEventListener('visibilitychange', handleVisibilityChange)
    schedule(0)
    return () => {
      disposed = true
      document.removeEventListener('visibilitychange', handleVisibilityChange)
      if (timer != null) window.clearTimeout(timer)
    }
  }, [enabled, hiddenIntervalMs, intervalMs])
}
