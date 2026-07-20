import { afterEach, describe, expect, it } from 'vitest'
import {
  clearCompanionSession,
  getCompanionSession,
  normalizeCompanionBaseUrl,
  setCompanionSession,
  type CompanionSession,
} from './companion'

const session: CompanionSession = {
  contract: 'GANN_ASTRO_COMPANION_SESSION_V1',
  baseUrl: 'https://gann-laptop.local:9443',
  accessToken: 'a'.repeat(48),
  expiresAtUtc: '2026-07-20T18:00:00Z',
  executionAllowed: false,
  capabilities: {
    contract: 'GANN_ASTRO_COMPANION_CAPABILITIES_V1',
    chartRead: true,
    reviewWrite: true,
    aiDrafts: true,
    codexBridge: true,
    executionAllowed: false,
  },
}

describe('mobile companion session', () => {
  afterEach(clearCompanionSession)

  it('normalizes an HTTPS host and rejects embedded credentials or paths', () => {
    expect(normalizeCompanionBaseUrl('https://gann-laptop.local:9443/')).toBe(
      'https://gann-laptop.local:9443',
    )
    expect(() => normalizeCompanionBaseUrl('http://gann-laptop.local:9443')).toThrow('HTTPS')
    expect(() => normalizeCompanionBaseUrl('https://user:pass@gann-laptop.local')).toThrow(
      'credentials',
    )
    expect(() => normalizeCompanionBaseUrl('https://gann-laptop.local/api')).toThrow('path')
  })

  it('keeps a validated session in memory without enabling execution', () => {
    setCompanionSession(session)
    expect(getCompanionSession()).toEqual(session)
    expect(getCompanionSession()?.executionAllowed).toBe(false)
  })

  it('rejects an execution-enabled server response', () => {
    expect(() => setCompanionSession({
      ...session,
      executionAllowed: true,
    } as unknown as CompanionSession)).toThrow('execution lock')
  })
})
