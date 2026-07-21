import { describe, expect, it } from 'vitest'
import {
  createChartDrawing,
  defaultDrawingPreferences,
  defaultFibonacciSettings,
  defaultRsiPaneSettings,
  defaultSquareOfNineSettings,
  squareOfNineLevels,
  squareOfNineValue,
  validateImportedLayout,
} from './chartLayouts'
import { defaultPlanetaryLineOverlaySettings } from './planetaryLines'

describe('Fibonacci retracement research drawing', () => {
  it('creates standard persisted levels with research-only guardrails', () => {
    const drawing = createChartDrawing(
      'fibonacci_retracement',
      [
        { timeUtc: '2026-07-13T10:00:00Z', price: 148.25 },
        { timeUtc: '2026-07-13T14:00:00Z', price: 147.5 },
      ],
      2,
    )
    expect(drawing.settings).toEqual(defaultFibonacciSettings())
    expect(drawing.guardrails.executionAllowed).toBe(false)
    expect(drawing.guardrails.consumedByLiveInference).toBe(false)
    expect(drawing.style.color).toBe('#57b8a6')
    expect(drawing.groupId).toBeNull()
    expect(drawing.syncScope).toBe('layout')
  })
})

describe('Square of Nine research math', () => {
  it('matches the documented square-root rotation steps', () => {
    expect(squareOfNineValue(5041, 1, 45)).toBeCloseTo(5076.5625, 8)
    expect(Math.ceil(squareOfNineValue(5041, 1, 45))).toBe(5077)
    expect(Math.round(squareOfNineValue(34, 1, 360, 'inward'))).toBe(15)
  })

  it('generates persisted highlighted levels ring by ring', () => {
    const settings = defaultSquareOfNineSettings(100)
    settings.increment = 1
    settings.rings = 2
    settings.highlightedAngles = [0, 90, 180, 360]
    const levels = squareOfNineLevels(settings)
    expect(levels).toHaveLength(6)
    expect(levels.find((item) => item.ring === 1 && item.angleDeg === 180)?.value).toBe(121)
    expect(levels.find((item) => item.ring === 2 && item.angleDeg === 0)?.value).toBe(144)
  })
})

describe('layout import guardrails', () => {
  it('forces imported drawings back into research-only mode', () => {
    const imported = validateImportedLayout({
      contract: 'GANN_CHART_LAYOUT_V1',
      schemaVersion: 1,
      layoutId: 'foreign',
      name: 'Imported',
      workspaceKind: 'main',
      symbol: 'USDJPY',
      timeframe: 'H1',
      familyKey: '',
      revision: 9,
      isDefault: true,
      autosave: true,
      chartState: { showAspects: true, showSrLines: true },
      drawings: [{
        drawingId: 'line-1',
        type: 'horizontal_line',
        anchors: [{ timeUtc: '2026-07-13T10:00:00Z', price: 147 }],
        guardrails: { executionAllowed: true },
      }],
    })
    expect(imported.isDefault).toBe(false)
    expect(imported.drawings[0].guardrails.executionAllowed).toBe(false)
    expect(imported.drawings[0].guardrails.consumedByLiveInference).toBe(false)
    expect(imported.drawings[0].syncScope).toBe('layout')
    expect(imported.drawings[0].pane).toBe('price')
    expect(imported.chartState.drawingPreferences).toEqual(defaultDrawingPreferences())
    expect(imported.chartState.rsi).toEqual(defaultRsiPaneSettings())
    expect(imported.chartState.planetaryLines).toEqual(defaultPlanetaryLineOverlaySettings())
  })

  it('preserves explicit RSI drawings and normalized indicator settings', () => {
    const imported = validateImportedLayout({
      contract: 'GANN_CHART_LAYOUT_V1',
      schemaVersion: 1,
      layoutId: 'rsi-layout',
      name: 'RSI research',
      workspaceKind: 'main',
      symbol: 'USDJPY',
      timeframe: 'H4',
      familyKey: '',
      revision: 1,
      isDefault: false,
      autosave: true,
      chartState: {
        showAspects: true,
        showSrLines: true,
        rsi: { visible: true, period: 21, levels: [20, 50, 80] },
      },
      drawings: [{
        drawingId: 'rsi-level-1',
        type: 'horizontal_line',
        pane: 'rsi',
        anchors: [{ timeUtc: '2026-07-13T10:00:00Z', price: 63.5 }],
      }],
    })
    expect(imported.chartState.rsi).toMatchObject({ visible: true, period: 21, levels: [20, 50, 80] })
    expect(imported.drawings[0].pane).toBe('rsi')
    expect(imported.drawings[0].anchors[0].price).toBe(63.5)
  })
})
