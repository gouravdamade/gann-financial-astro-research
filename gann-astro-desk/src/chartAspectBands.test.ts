import { describe, expect, it } from 'vitest'
import { clipAspectWindowToViewport } from './chartAspectBands'

describe('aspect band viewport clipping', () => {
  it('keeps an aspect visible when the viewport is entirely inside its window', () => {
    expect(clipAspectWindowToViewport(100, 900, 400, 500)).toEqual({ from: 400, to: 500 })
  })

  it('clips only the boundary that is outside the viewport', () => {
    expect(clipAspectWindowToViewport(300, 450, 400, 600)).toEqual({ from: 400, to: 450 })
  })

  it('drops a fully off-screen aspect', () => {
    expect(clipAspectWindowToViewport(100, 200, 400, 500)).toBeNull()
  })
})
