export type AspectViewportInterval = {
  from: number
  to: number
}

// An active aspect must remain visible when a zoomed viewport sits inside it.
export function clipAspectWindowToViewport(
  aspectStart: number,
  aspectEnd: number,
  viewportStart: number,
  viewportEnd: number,
): AspectViewportInterval | null {
  if (![aspectStart, aspectEnd, viewportStart, viewportEnd].every(Number.isFinite)) return null
  const start = Math.min(aspectStart, aspectEnd)
  const end = Math.max(aspectStart, aspectEnd)
  const viewportFrom = Math.min(viewportStart, viewportEnd)
  const viewportTo = Math.max(viewportStart, viewportEnd)
  if (end < viewportFrom || start > viewportTo) return null
  return {
    from: Math.max(start, viewportFrom),
    to: Math.min(end, viewportTo),
  }
}
