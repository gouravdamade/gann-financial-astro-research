import { describe, expect, it } from 'vitest'
import { ChartPaneRegistry, drawingAllowedInPane, type PaneLike, type PaneSeriesLike } from './chartPaneRegistry'

function series(name: string, pane: { current: PaneLike }): PaneSeriesLike & { name: string } {
  return { name, getPane: () => pane.current }
}

function pane(index: number, values: unknown[] = []) {
  const value: PaneLike = {
    paneIndex: () => index,
    getSeries: () => values,
  }
  return value
}

describe('chart pane ownership', () => {
  it('supports price-only, RSI-only, activity-only, and combined indicator layouts', () => {
    const pricePane = { current: pane(0) }
    const price = series('price', pricePane)
    const rsiPane = { current: pane(1) }
    const rsi = series('rsi', rsiPane)
    const activityPane = { current: pane(1) }
    const activity = series('activity', activityPane)
    let panes = [pricePane.current]
    const registry = new ChartPaneRegistry({ panes: () => panes }, price)
    pricePane.current = pane(0, [price])
    panes = [pricePane.current]
    expect(registry.ownerAtRuntimeIndex(0)).toBe('PRICE')
    expect(registry.ownerAtRuntimeIndex(1)).toBeNull()

    registry.registerIndicator({ id: 'RSI', series: rsi, preferredHeight: 120, classification: 'oscillator', modeEligible: true })
    rsiPane.current = pane(1, [rsi])
    panes = [pricePane.current, rsiPane.current]
    expect(registry.ownerAtRuntimeIndex(1)).toBe('RSI')
    registry.unregisterIndicator('RSI')

    registry.registerIndicator({ id: 'FIELDS_ACTIVITY', series: activity, preferredHeight: 136, classification: 'unsigned_activity', modeEligible: true })
    activityPane.current = pane(1, [activity])
    panes = [pricePane.current, activityPane.current]
    expect(registry.ownerAtRuntimeIndex(1)).toBe('FIELDS_ACTIVITY')

    registry.registerIndicator({ id: 'RSI', series: rsi, preferredHeight: 120, classification: 'oscillator', modeEligible: true })
    activityPane.current = pane(1, [activity])
    rsiPane.current = pane(2, [rsi])
    panes = [pricePane.current, activityPane.current, rsiPane.current]
    expect(registry.ownerAtRuntimeIndex(1)).toBe('FIELDS_ACTIVITY')
    expect(registry.ownerAtRuntimeIndex(2)).toBe('RSI')
    rsiPane.current = pane(1, [rsi])
    activityPane.current = pane(2, [activity])
    panes = [pricePane.current, rsiPane.current, activityPane.current]
    expect(registry.ownerAtRuntimeIndex(1)).toBe('RSI')
    expect(registry.ownerAtRuntimeIndex(2)).toBe('FIELDS_ACTIVITY')
  })

  it('resolves price, RSI, and activity by series identity at runtime indices', () => {
    const pricePane = { current: pane(0) }
    const price = series('price', pricePane)
    const rsiPane = { current: pane(1) }
    const rsi = series('rsi', rsiPane)
    const activityPane = { current: pane(2) }
    const activity = series('activity', activityPane)
    pricePane.current = pane(0, [price])
    rsiPane.current = pane(1, [rsi])
    activityPane.current = pane(2, [activity])
    let panes = [pricePane.current, rsiPane.current, activityPane.current]
    const registry = new ChartPaneRegistry({ panes: () => panes }, price)
    registry.registerIndicator({ id: 'RSI', series: rsi, preferredHeight: 120, classification: 'oscillator', modeEligible: true })
    registry.registerIndicator({ id: 'FIELDS_ACTIVITY', series: activity, preferredHeight: 136, classification: 'unsigned_activity', modeEligible: true })
    expect(registry.ownerAtRuntimeIndex(0)).toBe('PRICE')
    expect(registry.ownerAtRuntimeIndex(1)).toBe('RSI')
    expect(registry.ownerAtRuntimeIndex(2)).toBe('FIELDS_ACTIVITY')
    expect(registry.paneIndex('FIELDS_ACTIVITY')).toBe(2)

    pricePane.current = pane(0, [price])
    activityPane.current = pane(1, [activity])
    rsiPane.current = pane(2, [rsi])
    panes = [pricePane.current, activityPane.current, rsiPane.current]
    expect(registry.ownerAtRuntimeIndex(1)).toBe('FIELDS_ACTIVITY')
    expect(registry.ownerAtRuntimeIndex(2)).toBe('RSI')
  })

  it('never routes drawing tools into the activity pane', () => {
    for (const tool of ['select', 'horizontal', 'vertical', 'gann', 'fibonacci', 'annotation', 'replay'] as const) {
      expect(drawingAllowedInPane('FIELDS_ACTIVITY', tool)).toBe(false)
      expect(drawingAllowedInPane('PRICE', tool)).toBe(true)
    }
    expect(drawingAllowedInPane('RSI', 'horizontal')).toBe(true)
    expect(drawingAllowedInPane('RSI', 'gann')).toBe(false)
    expect(drawingAllowedInPane(null, 'horizontal')).toBe(false)
  })
})
