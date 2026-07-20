import { describe, expect, it } from 'vitest'
import { validateRuntimeProfile } from './runtimeProfile'
import type { RuntimeProfile } from './types'

describe('runtime profile', () => {
  it('accepts a locked Android companion profile', () => {
    expect(validateRuntimeProfile({
      contract: 'GANN_ASTRO_RUNTIME_PROFILE_V1',
      platform: 'android',
      backendMode: 'remote_companion',
      configured: false,
      executionAllowed: false,
    }).platform).toBe('android')
  })

  it('rejects a sidecar profile outside desktop', () => {
    expect(() => validateRuntimeProfile({
      contract: 'GANN_ASTRO_RUNTIME_PROFILE_V1',
      platform: 'android',
      backendMode: 'managed_sidecar',
      configured: true,
      executionAllowed: false,
    })).toThrow('desktop-only')
  })

  it('rejects execution-enabled profiles', () => {
    expect(() => validateRuntimeProfile({
      contract: 'GANN_ASTRO_RUNTIME_PROFILE_V1',
      platform: 'desktop',
      backendMode: 'managed_sidecar',
      configured: true,
      executionAllowed: true,
    } as unknown as RuntimeProfile)).toThrow('read-only execution lock')
  })
})
