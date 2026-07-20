import type { RuntimeProfile } from './types'

function isTauriRuntime(): boolean {
  return typeof window !== 'undefined' && '__TAURI_INTERNALS__' in window
}

export function validateRuntimeProfile(profile: RuntimeProfile): RuntimeProfile {
  if (profile.contract !== 'GANN_ASTRO_RUNTIME_PROFILE_V1') {
    throw new Error(`Unsupported runtime profile contract: ${String(profile.contract)}`)
  }
  if (profile.executionAllowed) {
    throw new Error('Runtime profile violated the read-only execution lock')
  }
  if (profile.backendMode === 'managed_sidecar' && profile.platform !== 'desktop') {
    throw new Error('Managed sidecar mode is desktop-only')
  }
  if (profile.backendMode === 'remote_companion' && !['android', 'mobile'].includes(profile.platform)) {
    throw new Error('Remote companion mode requires a mobile runtime')
  }
  return profile
}

export async function fetchRuntimeProfile(): Promise<RuntimeProfile> {
  if (!isTauriRuntime()) {
    return {
      contract: 'GANN_ASTRO_RUNTIME_PROFILE_V1',
      platform: 'browser',
      backendMode: 'browser_development',
      configured: true,
      executionAllowed: false,
    }
  }
  const { invoke } = await import('@tauri-apps/api/core')
  return validateRuntimeProfile(await invoke<RuntimeProfile>('runtime_profile'))
}
