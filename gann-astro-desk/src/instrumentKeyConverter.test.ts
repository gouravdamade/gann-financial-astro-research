import { describe, expect, it } from 'vitest'
import { suggestInstrumentInitialKey } from './instrumentKeyConverter'

describe('suggestInstrumentInitialKey', () => {
  it('maps the spoken USD ticker initial to YA and shows Hindi pronunciation', () => {
    const result = suggestInstrumentInitialKey('USD', 'ticker')

    expect(result.spokenHindi).toBe('यू-एस-डी')
    expect(result.status).toBe('ready')
    expect(result.candidates).toEqual([
      expect.objectContaining({
        layer: 'NAME_INITIAL',
        key: 'YA',
        glyph: 'य',
        hindiInitial: 'य',
      }),
    ])
  })

  it('keeps ticker spelling distinct from the company-name reading', () => {
    const ticker = suggestInstrumentInitialKey('AAPL', 'ticker')
    const company = suggestInstrumentInitialKey('Apple', 'company')

    expect(ticker.spokenHindi).toBe('ए-ए-पी-एल')
    expect(ticker.candidates[0]).toEqual(expect.objectContaining({
      layer: 'VOWEL',
      key: 'E',
    }))
    expect(company.status).toBe('review')
    expect(company.candidates.map((item) => item.key)).toEqual(['A', 'AI'])
  })

  it('provides an unambiguous spelling candidate but still requires company-name review', () => {
    const result = suggestInstrumentInitialKey('Reliance', 'company')

    expect(result.status).toBe('review')
    expect(result.spokenHindi).toBe('र')
    expect(result.candidates[0]).toEqual(expect.objectContaining({
      layer: 'NAME_INITIAL',
      key: 'RA',
      glyph: 'र',
    }))
  })

  it('recognizes exact leading digraphs', () => {
    const result = suggestInstrumentInitialKey('Bharti Airtel', 'company')

    expect(result.candidates).toEqual([
      expect.objectContaining({
        layer: 'NAME_INITIAL',
        key: 'BHA',
        glyph: 'भ',
      }),
    ])
  })

  it('does not force a ticker sound that has no exact certified cell', () => {
    const result = suggestInstrumentInitialKey('BRK.B', 'ticker')

    expect(result.spokenHindi).toBe('बी-आर-के-बी')
    expect(result.status).toBe('unsupported')
    expect(result.candidates).toEqual([])
  })
})
