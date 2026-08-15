import { afterEach, describe, expect, it } from 'vitest'
import {
  clearCompanionSession,
  formatCompanionError,
  getCompanionSession,
  normalizeCompanionBaseUrl,
  setCompanionSession,
  type CompanionSession,
} from './companion'

const session: CompanionSession = {
  contract: 'GANN_ASTRO_COMPANION_SESSION_V2',
  sessionId: '83f13567-13b0-4b74-88bb-e5fdf7a7a3cf',
  baseUrl: 'https://gann-laptop.local:9443',
  expiresAtUtc: '2030-07-20T18:00:00Z',
  certificateSha256: 'A'.repeat(64),
  transport: 'native_pinned_https_wss',
  executionAllowed: false,
  capabilities: {
    contract: 'GANN_ASTRO_COMPANION_CAPABILITIES_V2',
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

  it('rejects a server response that omits either execution lock', () => {
    const missingTopLevel = { ...session } as Partial<CompanionSession>
    delete missingTopLevel.executionAllowed
    expect(() => setCompanionSession(missingTopLevel as CompanionSession)).toThrow('execution lock')

    const missingCapability = {
      ...session,
      capabilities: { ...session.capabilities },
    } as { capabilities: Partial<CompanionSession['capabilities']> }
    delete missingCapability.capabilities.executionAllowed
    expect(() => setCompanionSession(missingCapability as CompanionSession)).toThrow('execution lock')
  })

  it('preserves native Rust invocation errors for remote diagnosis', () => {
    expect(formatCompanionError('Unable to reach the laptop pairing gateway: timeout')).toContain(
      'timeout',
    )
    expect(formatCompanionError({ message: 'Pinned certificate check failed' })).toBe(
      'Pinned certificate check failed',
    )
    expect(formatCompanionError(null)).toBe('Unable to pair with the laptop')
  })
})
