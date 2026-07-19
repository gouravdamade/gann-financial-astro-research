import { readFileSync } from 'node:fs'
import { fileURLToPath } from 'node:url'
import { describe, expect, it } from 'vitest'

const css = readFileSync(
  fileURLToPath(new URL('./App.css', import.meta.url)),
  'utf8',
)

function cssRule(selector) {
  const escaped = selector.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')
  const match = css.match(
    new RegExp(`(?:^|})\\s*${escaped}\\s*\\{([^}]*)\\}`),
  )
  if (!match) throw new Error(`Missing CSS rule: ${selector}`)
  return match[1]
}

describe('chart overlay stacking contract', () => {
  it('keeps all aspect bands above the chart canvas and below drawings', () => {
    expect(cssRule('.market-chart')).toMatch(/isolation:\s*isolate/)
    expect(cssRule('.market-chart-host')).toMatch(/z-index:\s*0/)
    expect(cssRule('.aspect-window-layer')).toMatch(/z-index:\s*1/)
    expect(cssRule('.aspect-band-layer')).toMatch(/z-index:\s*3/)
    expect(cssRule('.drawing-layer')).toMatch(/z-index:\s*5/)
    expect(cssRule('.annotation-layer')).toMatch(/z-index:\s*7/)
    expect(cssRule('.aspect-hover-card')).toMatch(/z-index:\s*16/)
  })
})
