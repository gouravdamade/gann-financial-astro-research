import { describe, expect, it } from 'vitest'
import {
  aspectLabel,
  datetimeInputValue,
  datetimeParameterValue,
  parseNumberList,
  toggleValue,
} from './parameterUtils'

describe('parameter utilities', () => {
  it('round-trips IST datetime-local values without browser timezone drift', () => {
    expect(datetimeInputValue('2025-05-25T00:00:00+05:30')).toBe('2025-05-25T00:00')
    expect(datetimeParameterValue('2025-05-25T00:00')).toBe('2025-05-25T00:00:00+05:30')
  })

  it('parses numeric SR lists and ignores invalid fragments', () => {
    expect(parseNumberList('0.12, 0.18 bad 1.6')).toEqual([0.12, 0.18, 1.6])
    expect(parseNumberList('')).toEqual([])
  })

  it('toggles filters and presents aspect labels', () => {
    expect(toggleValue(['MOON'], 'MERCURY')).toEqual(['MOON', 'MERCURY'])
    expect(toggleValue(['MOON'], 'MOON')).toEqual([])
    expect(aspectLabel('opposition_orb')).toBe('opposition')
  })
})
