import { describe, expect, it } from 'vitest'
import {
  buildSquareOfNineCells,
  defaultSquareOfNineWorkspaceState,
  normalizeSquareOfNineWorkspaceState,
  squareOfNineDisplayValue,
} from './squareOfNineWorkspace'

describe('standalone Square of Nine workspace', () => {
  it('treats size as the center plus surrounding levels', () => {
    const state = { ...defaultSquareOfNineWorkspaceState(100), size: 3 }
    const cells = buildSquareOfNineCells(state)
    expect(cells).toHaveLength(25)
    expect(new Set(cells.map((cell) => `${cell.row}:${cell.column}`)).size).toBe(25)
    expect(cells.find((cell) => cell.ordinal === 1)).toMatchObject({ row: 3, column: 3, ring: 0 })
    expect(cells.find((cell) => cell.ordinal === 25)?.ring).toBe(2)
  })

  it('mirrors number placement when rotation changes', () => {
    const base = { ...defaultSquareOfNineWorkspaceState(1), size: 2 }
    const clockwise = buildSquareOfNineCells(base)
    const counterclockwise = buildSquareOfNineCells({ ...base, numberRotation: 'counterclockwise' })
    const clockwiseThree = clockwise.find((cell) => cell.ordinal === 3)
    const counterclockwiseThree = counterclockwise.find((cell) => cell.ordinal === 3)
    expect(clockwiseThree?.x).toBe(counterclockwiseThree?.x)
    expect(clockwiseThree?.y).toBe(-(counterclockwiseThree?.y ?? 0))
  })

  it('supports signed price increments', () => {
    const state = { ...defaultSquareOfNineWorkspaceState(100), increment: -2.5 }
    expect(squareOfNineDisplayValue(state, 4)).toMatchObject({ numericValue: 92.5 })
  })

  it('skips weekends for trading-day date increments', () => {
    const state = {
      ...defaultSquareOfNineWorkspaceState(1),
      dataType: 'date' as const,
      firstDate: '2026-07-10',
      increment: 1,
      incrementUnit: 'trading_day' as const,
    }
    expect(squareOfNineDisplayValue(state, 2).displayValue).toBe('2026-07-13')
  })

  it('normalizes unsafe imported dimensions and selection', () => {
    const normalized = normalizeSquareOfNineWorkspaceState({ size: 999, zoomPercent: 1, selectedCellOrdinal: 99999 })
    expect(normalized.size).toBe(15)
    expect(normalized.zoomPercent).toBe(50)
    expect(normalized.selectedCellOrdinal).toBe(841)
  })
})
